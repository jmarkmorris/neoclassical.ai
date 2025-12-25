from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

Vec2 = Tuple[float, float]


def unit_circle_sampler(t: float) -> Vec2:
    """Unit circle at unit angular speed; default phase 0 (counterclockwise in math coords)."""
    return math.cos(t), math.sin(t)


def exp_inward_spiral_sampler(t: float, decay: float = 0.2) -> Vec2:
    """
    Exponential inward spiral toward origin.
    r(t) = exp(-decay * t), angle = t for steady rotation.
    """
    r = math.exp(-decay * t)
    return r * math.cos(t), r * math.sin(t)


@dataclass
class PathSpec:
    name: str
    sampler: Callable[[float], Vec2]
    description: str
    decay: float | None = None  # optional radial decay parameter


PATH_LIBRARY: Dict[str, PathSpec] = {
    "unit_circle": PathSpec(
        name="unit_circle",
        sampler=unit_circle_sampler,
        description="Unit circle, unit angular speed, phase offset configurable per particle.",
    ),
    "exp_inward_spiral": PathSpec(
        name="exp_inward_spiral",
        sampler=exp_inward_spiral_sampler,
        description="Exponential inward spiral toward origin; steady angular speed.",
        decay=0.005,
    ),
}


@dataclass
class ArchitrinoState:
    """
    Unified per-architrino state, covering identity, path params, and runtime
    kinematics. This is forward-compatible with both analytic paths and
    physics-based movers.
    """
    name: str
    polarity: int
    color: Tuple[int, int, int]
    mover_type: str = "analytic"
    path_name: str | None = None
    phase: float = 0.0
    path_offset: float = 0.0
    base_speed: float = 1.0
    heading_deg: float = 0.0
    radial_scale: float = 1.0
    param: float = 0.0  # path parameter (for analytic movers)
    pos: Vec2 = (0.0, 0.0)
    initial_vel: Vec2 = (0.0, 0.0)
    vel: Vec2 = (0.0, 0.0)
    trace: List[Vec2] | None = None
    speed_mult_override: float | None = None
    last_emit_time: float = 0.0
    path_snap: float | None = None
    position_snap: float | None = None
    initial_path_offset: float = 0.0
    trace_limit: int = 40000
    last_time: float = 0.0


@dataclass
class MoverEnv:
    """
    Per-frame context passed into movers.
    """
    time: float
    dt: float
    field_speed: float
    speed_mult: float
    path_snap: float | None
    position_snap: float | None
    emissions: List["Emission"]
    allow_self: bool = True
    hit_tolerance: float | None = None


class Mover:
    """Interface for motion update; concrete movers implement `step`."""

    mover_type: str = "base"

    def step(self, state: ArchitrinoState, env: MoverEnv, path_spec: PathSpec) -> Vec2:
        raise NotImplementedError


class AnalyticMover(Mover):
    """
    Analytic path mover: advances by parametric speed and samples a known path.
    Uses snap settings from state/env to match the existing quantization rules.
    """

    mover_type = "analytic"

    def step(self, state: ArchitrinoState, env: MoverEnv, path_spec: PathSpec) -> Vec2:
        speed_mult = state.speed_mult_override if state.speed_mult_override is not None else env.speed_mult
        snap_step = state.path_snap if state.path_snap is not None else env.path_snap
        path_param = state.param
        dt_step = env.time - state.last_time
        if dt_step < 0:
            dt_step = 0.0

        def pos_at(param: float) -> Vec2:
            if path_spec.name == "exp_inward_spiral" and path_spec.decay is not None:
                base_param = param
                decay_scale = 1.0
                if env.speed_mult is not None and env.field_speed is not None and env.speed_mult > env.field_speed + 1e-6:
                    decay_scale = 2.0
                angle = base_param + state.phase
                radius = math.exp(-path_spec.decay * abs(base_param) * decay_scale)
                return (radius * math.cos(angle), radius * math.sin(angle))
            x, y = path_spec.sampler(param + state.phase)
            return (x, y)

        # Keep linear speed constant by adjusting param rate based on |dpos/dparam|.
        eps = 1e-3
        p_fwd = pos_at(path_param + eps)
        p_back = pos_at(path_param - eps)
        dx = (p_fwd[0] - p_back[0]) / (2 * eps)
        dy = (p_fwd[1] - p_back[1]) / (2 * eps)
        base_speed = math.hypot(dx, dy)
        denom = max(base_speed * state.radial_scale, 1e-9)
        dparam_dt = (state.base_speed * speed_mult) / denom
        path_param = path_param + dparam_dt * dt_step
        snap_param = path_param
        if snap_step is not None and snap_step > 0:
            snap_param = round(path_param / snap_step) * snap_step

        pos = pos_at(snap_param)

        pos = (pos[0] * state.radial_scale, pos[1] * state.radial_scale)
        snap_dist = state.position_snap if state.position_snap is not None else env.position_snap
        if snap_dist is not None and (snap_step is None or snap_step <= 0):
            pos = (
                round(pos[0] / snap_dist) * snap_dist,
                round(pos[1] / snap_dist) * snap_dist,
            )
        state.param = path_param
        state.pos = pos
        state.last_time = env.time
        return pos


class PhysicsMover(Mover):
    """
    Placeholder for Coulomb-style physics movers that operate on retarded hits.
    The integration loop will supply neighbor context via MoverEnv extensions.
    """

    mover_type = "physics"

    def step(self, state: ArchitrinoState, env: MoverEnv, path_spec: PathSpec) -> Vec2:
        # Retarded-force integration using historical emissions.
        dt_step = env.time - state.last_time
        if dt_step <= 0:
            return state.pos
        q = float(state.polarity)
        mass = max(abs(q), 1e-6)
        fx = fy = 0.0
        tol = env.hit_tolerance
        if tol is None:
            tol = max(env.field_speed * dt_step * 0.6, 0.002)
        max_force = 25.0  # simple clamp to avoid blow-ups
        for em in env.emissions:
            if not env.allow_self and em.emitter == state.name:
                continue
            tau = env.time - em.time
            if tau <= 0:
                continue
            radius = env.field_speed * tau
            dx = state.pos[0] - em.pos[0]
            dy = state.pos[1] - em.pos[1]
            dist = math.hypot(dx, dy)
            if dist < 1e-9:
                continue
            diff = abs(dist - radius)
            if diff > tol:
                continue
            force_mag = (q * em.polarity) / (dist * dist)
            force_mag = max(-max_force, min(max_force, force_mag))
            fx += force_mag * (dx / dist)
            fy += force_mag * (dy / dist)
        ax = fx / mass
        ay = fy / mass
        vx = state.vel[0] + ax * dt_step
        vy = state.vel[1] + ay * dt_step
        # Clamp velocity to keep integration stable.
        vmag = math.hypot(vx, vy)
        vcap = 10.0
        if vmag > vcap:
            scale = vcap / vmag
            vx *= scale
            vy *= scale
        px = state.pos[0] + vx * dt_step
        py = state.pos[1] + vy * dt_step
        state.vel = (vx, vy)
        state.pos = (px, py)
        state.param = state.param  # unchanged for physics mover
        state.last_time = env.time
        return state.pos


@dataclass
class Emission:
    time: float
    pos: Vec2
    emitter: str
    polarity: int
    last_radius: float = 0.0


def default_phase_and_offset(path_name: str, start: Vec2, decay: float | None) -> Tuple[float, float]:
    """
    Compute phase and path_offset needed for the analytic path to hit start_pos.
    """
    x, y = start
    if path_name == "unit_circle":
        angle = math.atan2(y, x)
        return angle, 0.0
    if path_name == "exp_inward_spiral" and decay is not None:
        angle = math.atan2(y, x)
        r = math.hypot(x, y)
        base_param = 0.0
        if r > 1e-9:
            base_param = max(0.0, -math.log(r) / max(decay, 1e-9))
        phase = angle - base_param
        return phase, base_param
    return 0.0, 0.0


__all__ = [
    "Vec2",
    "PathSpec",
    "PATH_LIBRARY",
    "ArchitrinoState",
    "MoverEnv",
    "Mover",
    "AnalyticMover",
    "PhysicsMover",
    "Emission",
    "default_phase_and_offset",
    "unit_circle_sampler",
    "exp_inward_spiral_sampler",
]
