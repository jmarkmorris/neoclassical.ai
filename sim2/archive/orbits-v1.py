"""
This version was archived on Nov 30, 2025.
It animates the orbit. That is kinda cool but it takes a lot of computation.
I am thinking about changing it so that it only keeps track of the path and I can fast forward or reverse to jump over frames.
Also, I am having problems with the visualization so I want to build the frame up in layers.
So this is an archive of v1 before I make those major changes.
--------

sim2 prototype (single-file).

Implements core math and a non-graphical, testable pipeline:
• Path sampling for predefined trajectories (unit circle, exponential inward spiral).
• Emission bookkeeping with constant field speed v=1 and 1/r^2 falloff.
• Hit detection via causal condition ||s_r(t) - s_e(t0)|| = v * (t - t0).
• Basic pre-bake loop that can run until domain coverage is achieved.

Usage:
    python orbits.py --self-test
    python orbits.py --duration 4 --fps 30 --path unit_circle
"""

from __future__ import annotations

import argparse
import math
import os
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple
import numpy as np

Vec2 = Tuple[float, float]


def precompute_worker_static(
    args: Tuple[
        int,
        float,
        float,
        float,
        float,
        bool,
        str,
        bool,
        float,
        float,
        int,
        int,
        int,
        float,
    ]
) -> Tuple[int, Dict[str, Vec2], List["Hit"], np.ndarray]:
    (
        idx,
        t,
        path_t,
        emission_retention_local,
        field_v_local,
        allow_self,
        path_name,
        reverse,
        dt,
        domain_half_extent,
        canvas_w,
        height,
        fps,
        speed_mult_local,
    ) = args

    path = PATH_LIBRARY[path_name]
    positrino = Architrino("positrino", +1, PURE_RED, 0.0, path, reverse=reverse)
    electrino = Architrino("electrino", -1, PURE_BLUE, math.pi, path, reverse=reverse)

    pos_posi = positrino.position(path_t)
    pos_elec = electrino.position(path_t)
    positions = {"positrino": pos_posi, "electrino": pos_elec}

    emissions_local: List[Emission] = []
    for j in range(idx + 1):
        tj = j * dt
        emissions_local.append(Emission(time=tj, pos=positrino.position(speed_mult_local * tj), emitter="positrino"))
        emissions_local.append(Emission(time=tj, pos=electrino.position(speed_mult_local * tj), emitter="electrino"))
    emissions_local = [e for e in emissions_local if (t - e.time) <= emission_retention_local]

    hits: List[Hit] = []
    radius_tol = max(field_v_local * dt, 0.005)
    seen_local = set()
    for emission in emissions_local:
        tau = t - emission.time
        if tau <= 0:
            continue
        radius = field_v_local * tau
        for receiver_name, receiver_pos in positions.items():
            dist = l2(receiver_pos, emission.pos)
            if abs(dist - radius) <= radius_tol:
                key = (emission.time, emission.emitter, receiver_name)
                if key in seen_local:
                    continue
                if emission.emitter == receiver_name and not allow_self:
                    continue
                seen_local.add(key)
                strength = 1.0 / (dist * dist) if dist > 0 else float("inf")
                ang = angle_from_x_axis(receiver_pos)
                hits.append(
                    Hit(
                        t_obs=t,
                        t_emit=emission.time,
                        emitter=emission.emitter,
                        receiver=receiver_name,
                        distance=dist,
                        strength=strength,
                        angle=ang,
                        speed_multiplier=speed_mult_local,
                        emit_pos=emission.pos,
                    )
                )

    res = 512
    min_dim = min(canvas_w, height)
    x_extent = domain_half_extent * (canvas_w / min_dim)
    y_extent = domain_half_extent * (height / min_dim)
    xs = np.linspace(-x_extent, x_extent, res)
    ys = np.linspace(-y_extent, y_extent, res)
    xx, yy = np.meshgrid(xs, ys)
    eps = 1e-6
    net = np.zeros_like(xx, dtype=np.float64)
    shell_thickness = max(field_v_local * (1.5 / fps), 0.005)
    for em in emissions_local:
        tau = t - em.time
        if tau < 0:
            continue
        r = field_v_local * tau
        if r > emission_retention_local * field_v_local:
            continue
        ex, ey = em.pos
        dist = np.sqrt((xx - ex) ** 2 + (yy - ey) ** 2) + eps
        mask = np.abs(dist - r) <= shell_thickness
        if not np.any(mask):
            continue
        sign = 1.0 if em.emitter == "positrino" else -1.0
        contrib = np.zeros_like(dist)
        contrib[mask] = sign / (dist[mask] ** 2)
        net += contrib

    log_net = np.sign(net) * np.log1p(np.abs(net))
    max_abs = np.percentile(np.abs(log_net), 99) if np.any(log_net) else 1.0
    if max_abs < 1e-9:
        max_abs = 1.0
    pos_norm = np.clip(np.maximum(log_net, 0.0) / max_abs, 0.0, 1.0)
    neg_norm = np.clip(np.maximum(-log_net, 0.0) / max_abs, 0.0, 1.0)
    red = (255 * (1 - neg_norm)).astype(np.uint8)
    blue = (255 * (1 - pos_norm)).astype(np.uint8)
    green = (255 * (1 - np.maximum(pos_norm, neg_norm))).astype(np.uint8)
    rgb = np.stack([red, green, blue], axis=-1)
    return idx, positions, hits, rgb


# Color constants (RGB)
PURE_RED = (255, 0, 0)
PURE_BLUE = (0, 0, 255)
PURE_PURPLE = (255, 0, 255)  # neutral (red + blue)
PURE_WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
LIGHT_RED = (255, 160, 160)
LIGHT_BLUE = (160, 200, 255)


@dataclass
class PathSpec:
    name: str
    sampler: Callable[[float], Vec2]
    reverse_sampler: Callable[[float], Vec2]
    description: str


def unit_circle_sampler(t: float) -> Vec2:
    """Unit circle at unit angular speed; default phase 0 (counterclockwise in math coords)."""
    return math.cos(t), math.sin(t)


def unit_circle_sampler_reversed(t: float) -> Vec2:
    """Reverse orientation of unit circle."""
    return unit_circle_sampler(-t)


def exp_inward_spiral_sampler(t: float, decay: float = 0.2) -> Vec2:
    """
    Exponential inward spiral toward origin.
    r(t) = exp(-decay * t), angle = t for steady rotation.
    """
    r = math.exp(-decay * t)
    return r * math.cos(t), r * math.sin(t)


def exp_inward_spiral_sampler_reversed(t: float, decay: float = 0.2) -> Vec2:
    return exp_inward_spiral_sampler(-t, decay=decay)


PATH_LIBRARY: Dict[str, PathSpec] = {
    "unit_circle": PathSpec(
        name="unit_circle",
        sampler=unit_circle_sampler,
        reverse_sampler=unit_circle_sampler_reversed,
        description="Unit circle, unit angular speed, phase offset configurable per particle.",
    ),
    "exp_inward_spiral": PathSpec(
        name="exp_inward_spiral",
        sampler=exp_inward_spiral_sampler,
        reverse_sampler=exp_inward_spiral_sampler_reversed,
        description="Exponential inward spiral toward origin; steady angular speed.",
    ),
}


@dataclass
class Architrino:
    name: str
    polarity: int  # +1 positrino, -1 electrino
    color: Tuple[int, int, int]
    phase: float  # radians
    path: PathSpec
    reverse: bool = False

    def position(self, t: float) -> Vec2:
        """Position on the assigned path with phase offset."""
        sampler = self.path.reverse_sampler if self.reverse else self.path.sampler
        x, y = sampler(t + self.phase)
        return x, y


@dataclass
class Emission:
    time: float
    pos: Vec2
    emitter: str
    last_radius: float = 0.0


@dataclass
class Hit:
    t_obs: float
    t_emit: float
    emitter: str
    receiver: str
    distance: float
    strength: float
    angle: float  # radians, from +x
    speed_multiplier: float  # path speed multiplier applied during this frame
    emit_pos: Vec2


@dataclass
class Frame:
    time: float
    positions: Dict[str, Vec2]
    hits: List[Hit] = field(default_factory=list)


@dataclass
class RenderFrame:
    positions: Dict[str, Vec2]
    hits: List[Hit]
    field_surface: "pygame.Surface"


@dataclass
class SimulationConfig:
    fps: int = 60
    duration: float = 4.0
    field_speed: float = 1.0  # v=1
    domain_half_extent: float = 2.0  # domain [-2,2] by default
    coverage_margin: float = 1.1  # scale for coverage duration heuristic
    max_memory_bytes: int = 8 * 1024 * 1024 * 1024  # default budget (~8 GiB) for frames if caching
    speed_multiplier: float = 0.5  # path speed scaling in [0, 100]; 0 => stationary


def l2(a: Vec2, b: Vec2) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.hypot(dx, dy)


def angle_from_x_axis(p: Vec2) -> float:
    """Angle in [0, 2π) from +x axis."""
    ang = math.atan2(p[1], p[0])
    return ang if ang >= 0 else ang + 2 * math.pi


def angle_deg(p: Vec2) -> float:
    """Angle in degrees [0, 360) from +x axis."""
    ang = angle_from_x_axis(p)
    return math.degrees(ang)


def angle_deg_screen(vec: Vec2) -> float:
    """Angle in degrees [0, 360) from +x axis in screen coords (y down)."""
    ang = math.atan2(-vec[1], vec[0])
    ang = ang if ang >= 0 else ang + 2 * math.pi
    return math.degrees(ang)


def estimate_coverage_duration(cfg: SimulationConfig) -> float:
    """
    Heuristic duration until emissions can cover the domain:
    radius needed ~ diagonal of domain/2 from typical origin positions (~1 unit).
    """
    diag = math.sqrt(2 * (cfg.domain_half_extent ** 2))
    return cfg.coverage_margin * (cfg.domain_half_extent + diag)


def render_live(cfg: SimulationConfig, paths: Dict[str, PathSpec], path_name: str = "unit_circle", reverse: bool = False, parallel_precompute: bool = False) -> None:
    """
    Incremental PyGame renderer that keeps a rolling accumulator grid instead of cached frames.
    """
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "hide")
    try:
        import pygame
    except ImportError as exc:
        raise SystemExit("PyGame is required for rendering. Install with `pip install pygame`.") from exc

    if path_name not in paths:
        raise ValueError(f"Unknown path '{path_name}'. Available: {list(paths.keys())}")

    pygame.init()
    panel_w = 320
    width, height = 1710, 1107
    canvas_w = width - panel_w
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("sim2 (prototype)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)

    path = paths[path_name]
    positrino = Architrino("positrino", +1, PURE_RED, 0.0, path, reverse=reverse)
    electrino = Architrino("electrino", -1, PURE_BLUE, math.pi, path, reverse=reverse)

    running = True
    paused = True
    frame_idx = 0
    target_stop_at_posi_start = False
    stop_reached = False
    hits_at_stop: List[Hit] = []
    stop_positions: Dict[str, Vec2] | None = None
    stop_field_surface = None

    dt = 1.0 / cfg.fps
    field_v = max(cfg.field_speed, 1e-6)
    # Grid spacing used to set a minimum shell thickness to avoid aliasing.
    shell_thickness = max(field_v * dt, 0.003)
    speed_mult = max(0.0, min(cfg.speed_multiplier, 100.0))
    pending_speed_mult = speed_mult

    max_radius = math.sqrt(2) * cfg.domain_half_extent * 1.1
    emission_retention = max_radius / field_v
    emissions: List[Emission] = []
    recent_hits = deque(maxlen=20)
    seen_hits = set()
    seen_hits_queue = deque()
    last_diff = {}
    last_diff_queue = deque()
    self_delta = None
    emitter_lookup = {"positrino": positrino, "electrino": electrino}

    # Grid for the accumulator at a coarser resolution to reduce work; upscale for display.
    base_res = 640  # on the shorter side
    min_dim = min(canvas_w, height)
    res_x = int(base_res * (canvas_w / min_dim))
    res_y = int(base_res * (height / min_dim))
    res_x = max(64, res_x)
    res_y = max(64, res_y)
    min_dim = min(canvas_w, height)
    x_extent = cfg.domain_half_extent * (canvas_w / min_dim)
    y_extent = cfg.domain_half_extent * (height / min_dim)
    xs = np.linspace(-x_extent, x_extent, res_x)
    ys = np.linspace(-y_extent, y_extent, res_y)
    xx, yy = np.meshgrid(xs, ys)
    eps = 1e-6

    field_grid = np.zeros_like(xx, dtype=np.float32)
    field_surface = None

    # Adjust shell thickness to be at least a fraction of a grid cell to reduce aliasing.
    grid_dx = (xs[-1] - xs[0]) / max(res_x - 1, 1)
    grid_dy = (ys[-1] - ys[0]) / max(res_y - 1, 1)
    shell_thickness = max(shell_thickness, 0.75 * min(grid_dx, grid_dy))

    def world_to_screen(p: Vec2) -> Vec2:
        scale = min(canvas_w, height) / (2 * cfg.domain_half_extent)
        sx = panel_w + canvas_w / 2 + p[0] * scale
        sy = height / 2 + p[1] * scale
        return sx, sy

    def clamp_speed(v: float) -> float:
        return max(0.0, min(v, 100.0))

    def compute_self_delta(speed: float, v_field: float) -> float | None:
        """Smallest positive root of 2*sin(w*dt/2) = v*dt for a unit circle self-hit."""
        if speed <= v_field + 1e-6:
            return None

        def f(d: float) -> float:
            return 2.0 * math.sin(0.5 * speed * d) - v_field * d

        hi = max(2.0, 2 * math.pi / max(speed, 1e-6))
        for _ in range(120):
            if f(hi) < 0:
                break
            hi *= 1.5
        else:
            return None
        lo = 0.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if f(mid) > 0:
                lo = mid
            else:
                hi = mid
        return hi

    def smooth5(mat: np.ndarray) -> np.ndarray:
        """Separable 5x5 box blur (edge-padded) to smooth residual banding."""
        # Horizontal blur
        p = np.pad(mat, ((0, 0), (2, 2)), mode="edge")
        h = (p[:, 2:-2] + p[:, 1:-3] + p[:, 3:-1] + p[:, :-4] + p[:, 4:]) / 5.0
        # Vertical blur
        p2 = np.pad(h, ((2, 2), (0, 0)), mode="edge")
        v = (p2[2:-2, :] + p2[1:-3, :] + p2[3:-1, :] + p2[:-4, :] + p2[4:, :]) / 5.0
        return v.astype(np.float32, copy=False)

    def make_field_surface() -> "pygame.Surface":
        log_net = np.sign(field_grid) * np.log1p(np.abs(field_grid))
        log_net = smooth5(log_net)
        max_abs = np.percentile(np.abs(log_net), 99) if np.any(log_net) else 1.0
        if max_abs < 1e-9:
            max_abs = 1.0
        pos_norm = np.clip(np.maximum(log_net, 0.0) / max_abs, 0.0, 1.0)
        neg_norm = np.clip(np.maximum(-log_net, 0.0) / max_abs, 0.0, 1.0)
        red = (255 * (1 - neg_norm)).astype(np.uint8)
        blue = (255 * (1 - pos_norm)).astype(np.uint8)
        green = (255 * (1 - np.maximum(pos_norm, neg_norm))).astype(np.uint8)
        rgb = np.stack([red, green, blue], axis=-1)
        surf = pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))
        surf = pygame.transform.smoothscale(surf, (canvas_w, height))
        return surf.convert()

    def apply_shell(em: Emission, radius: float, remove: bool = False) -> None:
        """Apply a smooth annular band for this emission at the given radius."""
        if radius <= 0 or radius > max_radius:
            return
        ex, ey = em.pos
        band_half = max(shell_thickness * 1.5, shell_thickness)

        # Bounding box in world coords
        x_min = ex - (radius + band_half)
        x_max = ex + (radius + band_half)
        y_min = ey - (radius + band_half)
        y_max = ey + (radius + band_half)
        # Early reject if box is outside domain
        if x_max < xs[0] or x_min > xs[-1] or y_max < ys[0] or y_min > ys[-1]:
            return

        # Convert to index range
        x0 = max(0, np.searchsorted(xs, x_min, side="left"))
        x1 = min(len(xs), np.searchsorted(xs, x_max, side="right"))
        y0 = max(0, np.searchsorted(ys, y_min, side="left"))
        y1 = min(len(ys), np.searchsorted(ys, y_max, side="right"))
        if x0 >= x1 or y0 >= y1:
            return

        sub_xx = xx[y0:y1, x0:x1]
        sub_yy = yy[y0:y1, x0:x1]
        dist = np.sqrt((sub_xx - ex) ** 2 + (sub_yy - ey) ** 2) + eps
        delta = np.abs(dist - radius)
        mask = delta <= band_half
        if not np.any(mask):
            return

        # Smooth radial weight (raised cosine) to reduce aliasing.
        radial_weight = 0.5 * (1.0 + np.cos(np.pi * delta[mask] / band_half))
        sign = 1.0 if em.emitter == "positrino" else -1.0
        contrib = sign * radial_weight / (dist[mask] ** 2)
        if remove:
            field_grid[y0:y1, x0:x1][mask] -= contrib
        else:
            field_grid[y0:y1, x0:x1][mask] += contrib

    def update_emissions(current_time: float) -> None:
        nonlocal emissions
        updated: List[Emission] = []
        for em in emissions:
            r_prev = em.last_radius
            r_new = field_v * (current_time - em.time)
            if r_prev > 0:
                apply_shell(em, r_prev, remove=True)
            if r_new > max_radius:
                continue
            if r_new > 0:
                apply_shell(em, r_new, remove=False)
                em.last_radius = r_new
            updated.append(em)
        emissions = updated

    def cleanup_hits(current_time: float) -> None:
        cutoff = current_time - emission_retention
        while seen_hits_queue and seen_hits_queue[0][0] < cutoff:
            _, key = seen_hits_queue.popleft()
            seen_hits.discard(key)
        while last_diff_queue and last_diff_queue[0][0] < cutoff:
            _, key = last_diff_queue.popleft()
            last_diff.pop(key, None)

    def detect_hits(current_time: float, positions: Dict[str, Vec2], allow_self: bool) -> List[Hit]:
        hits: List[Hit] = []
        radius_tol_cross = max(field_v * dt * 0.6, 0.002)
        radius_tol_self = max(field_v * dt * 0.3, 0.001)
        cleanup_hits(current_time)
        for em in emissions:
            tau = current_time - em.time
            if tau <= 0:
                continue
            radius = field_v * tau
            if radius > max_radius:
                continue
            for receiver_name, receiver_pos in positions.items():
                is_self = em.emitter == receiver_name
                if is_self:
                    if not allow_self or self_delta is None:
                        continue
                    t_emit_target = current_time - self_delta
                    # Find the closest emission from this emitter to the target emission time.
                    best_em = None
                    best_dt = None
                    for candidate in emissions:
                        if candidate.emitter != em.emitter:
                            continue
                        if candidate.time > t_emit_target + dt:
                            continue
                        delta_t = abs(candidate.time - t_emit_target)
                        if best_dt is None or delta_t < best_dt:
                            best_dt = delta_t
                            best_em = candidate
                    if best_em is None:
                        # Fallback: compute position analytically.
                        emit_pos = emitter_lookup[em.emitter].position(speed_mult * t_emit_target)
                        t_emit_used = t_emit_target
                    else:
                        emit_pos = best_em.pos
                        t_emit_used = best_em.time
                    tau_self = current_time - t_emit_used
                    radius_self = field_v * tau_self
                    dist = l2(receiver_pos, emit_pos)
                    diff = dist - radius_self
                    key = (t_emit_used, em.emitter, receiver_name)
                    last_diff[key] = diff
                    last_diff_queue.append((t_emit_used, key))
                    if abs(diff) > radius_tol_self:
                        continue
                    if key in seen_hits:
                        continue
                    seen_hits.add(key)
                    seen_hits_queue.append((t_emit_used, key))
                    vec = (receiver_pos[0] - emit_pos[0], receiver_pos[1] - emit_pos[1])
                    ang = angle_from_x_axis(vec)
                    strength = 1.0 / (dist * dist) if dist > 0 else float("inf")
                    hits.append(
                        Hit(
                            t_obs=current_time,
                            t_emit=t_emit_used,
                            emitter=em.emitter,
                            receiver=receiver_name,
                            distance=dist,
                            strength=strength,
                            angle=ang,
                            speed_multiplier=speed_mult,
                            emit_pos=emit_pos,
                        )
                    )
                else:
                    tol = radius_tol_cross
                    dist = l2(receiver_pos, em.pos)
                    diff = dist - radius
                    key = (em.time, em.emitter, receiver_name)
                    last_diff[key] = diff
                    last_diff_queue.append((em.time, key))
                    if abs(diff) <= tol:
                        prev = last_diff.get(key)
                        if prev is not None and abs(diff) > abs(prev) and diff * prev > 0:
                            continue
                        if key in seen_hits:
                            continue
                        seen_hits.add(key)
                        seen_hits_queue.append((em.time, key))
                        vec = (receiver_pos[0] - em.pos[0], receiver_pos[1] - em.pos[1])
                        ang = angle_from_x_axis(vec)
                        strength = 1.0 / (dist * dist) if dist > 0 else float("inf")
                        hits.append(
                            Hit(
                                t_obs=current_time,
                                t_emit=em.time,
                                emitter=em.emitter,
                                receiver=receiver_name,
                                distance=dist,
                                strength=strength,
                                angle=ang,
                                speed_multiplier=speed_mult,
                                emit_pos=em.pos,
                            )
                        )
        return hits

    def draw_text(text: str, x: int, y: int, color=(0, 0, 0)) -> None:
        surf = font.render(text, True, color)
        screen.blit(surf, (x, y))

    def reset_state(apply_pending_speed: bool = True) -> None:
        nonlocal emissions, field_grid, frame_idx, stop_reached, target_stop_at_posi_start, hits_at_stop, speed_mult, field_surface, stop_positions, stop_field_surface, self_delta
        if apply_pending_speed:
            speed_mult = clamp_speed(pending_speed_mult)
        self_delta = compute_self_delta(speed_mult, field_v)
        emissions = []
        field_grid[:] = 0.0
        field_surface = make_field_surface()
        frame_idx = 0
        stop_reached = False
        target_stop_at_posi_start = False
        hits_at_stop = []
        stop_positions = None
        stop_field_surface = None
        recent_hits.clear()
        seen_hits.clear()
        seen_hits_queue.clear()
        last_diff.clear()
        last_diff_queue.clear()

    def render_frame(positions: Dict[str, Vec2], hits: List[Hit], field_surf=None) -> None:
        screen.fill(PURE_WHITE)
        fs = field_surf if field_surf is not None else field_surface
        screen.blit(fs, (panel_w, 0))
        if path_name == "unit_circle":
            center = world_to_screen((0.0, 0.0))
            scale = min(canvas_w, height) / (2 * cfg.domain_half_extent)
            pygame.draw.circle(screen, GRAY, center, int(scale), 1)

        for h in hits:
            start = world_to_screen(h.emit_pos)
            end = world_to_screen(positions[h.receiver])
            pygame.draw.line(screen, GRAY, start, end, 1)
            if h.emitter == "positrino":
                pygame.draw.circle(screen, LIGHT_RED, start, 4)
            else:
                pygame.draw.circle(screen, LIGHT_BLUE, start, 4)
            pygame.draw.circle(screen, PURE_WHITE, start, 5, 1)

        pos_posi_screen = world_to_screen(positions["positrino"])
        pos_elec_screen = world_to_screen(positions["electrino"])
        pygame.draw.circle(screen, PURE_RED, pos_posi_screen, 6)
        pygame.draw.circle(screen, PURE_WHITE, pos_posi_screen, 7, 1)
        pygame.draw.circle(screen, PURE_BLUE, pos_elec_screen, 6)
        pygame.draw.circle(screen, PURE_WHITE, pos_elec_screen, 7, 1)

        pygame.draw.rect(screen, (245, 245, 245), (0, 0, panel_w, height))
        draw_text(f"frame={frame_idx+1}", 10, 10)
        draw_text(f"fps={cfg.fps}", 10, 30)
        if paused and pending_speed_mult != speed_mult:
            draw_text(f"speed_mult={speed_mult:.1f} -> {pending_speed_mult:.1f}", 10, 50)
        else:
            draw_text(f"speed_mult={speed_mult:.1f}", 10, 50)
        draw_text("Controls:", 10, 80)
        draw_text("ESC quit, SPACE pause", 10, 100)
        draw_text("UP/DOWN speed (auto-pause)", 10, 120)
        draw_text("RIGHT: run to positrino start", 10, 140)
        draw_text("Hit table (t = now):", 10, 170)
        y = 190
        for idx, h in enumerate(list(hits)[:12]):
            recv_now = positions.get(h.receiver, (0.0, 0.0))
            emit_to_recv = (recv_now[0] - h.emit_pos[0], recv_now[1] - h.emit_pos[1])
            hit_angle_deg = angle_deg_screen(emit_to_recv)
            color = PURE_RED if h.receiver == "positrino" else PURE_BLUE
            text = (
                f"{idx+1:02d} recv={h.receiver[0].upper()} "
                f"hit={hit_angle_deg:.1f}° str={h.strength:.3f} "
                f"emit={h.emitter[0].upper()} v={h.speed_multiplier:.2f}"
            )
            draw_text(text, 10, y, color=color)
            y += 18

        if stop_reached and hits_at_stop:
            for h in hits_at_stop:
                recv_now = positions.get(h.receiver, (0.0, 0.0))
                emit_to_recv = (recv_now[0] - h.emit_pos[0], recv_now[1] - h.emit_pos[1])
                ang_deg_disp = angle_deg_screen(emit_to_recv)
                ang_rad_screen = math.radians(ang_deg_disp)
                recv_screen = world_to_screen(recv_now)
                xaxis_proj = world_to_screen((recv_now[0], 0.0))
                pygame.draw.line(screen, GRAY, recv_screen, xaxis_proj, 2)
                radius_px = 30
                rect = pygame.Rect(0, 0, radius_px * 2, radius_px * 2)
                rect.center = recv_screen
                pygame.draw.arc(screen, GRAY, rect, 0, ang_rad_screen, 2)
                label = f"{ang_deg_disp:.1f}°"
                draw_text(label, int(recv_screen[0] + radius_px), int(recv_screen[1] - radius_px))

        if paused:
            draw_text("PAUSED", 10, height - 30)
        pygame.display.flip()

    def current_positions(time_t: float) -> Dict[str, Vec2]:
        path_t = speed_mult * time_t
        return {
            "positrino": positrino.position(path_t),
            "electrino": electrino.position(path_t),
        }

    # Initial frame
    positions = current_positions(0.0)
    field_surface = make_field_surface()
    render_frame(positions, [])

    # Only refresh the field surface every few frames to reduce cost.
    accum_stride = 2

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if paused:
                        # Only reset when a staged speed change exists; otherwise resume where we left off.
                        if pending_speed_mult != speed_mult:
                            reset_state(apply_pending_speed=True)
                        paused = False
                    else:
                        paused = True
                elif event.key == pygame.K_UP:
                    pending_speed_mult = clamp_speed(pending_speed_mult + 0.1)
                    paused = True
                elif event.key == pygame.K_DOWN:
                    pending_speed_mult = clamp_speed(pending_speed_mult - 0.1)
                    paused = True
                elif event.key == pygame.K_RIGHT:
                    # Apply staged speed if any, but do not force a full reset otherwise.
                    if pending_speed_mult != speed_mult:
                        reset_state(apply_pending_speed=True)
                    stop_reached = False
                    hits_at_stop = []
                    target_stop_at_posi_start = True
                    paused = False

        if paused:
            if stop_reached and hits_at_stop:
                render_frame(stop_positions or positions, hits_at_stop, stop_field_surface)
            else:
                render_frame(positions, list(recent_hits))
            clock.tick(cfg.fps)
            continue

        current_time = frame_idx * dt
        positions = current_positions(current_time)

        emissions.append(Emission(time=current_time, pos=positions["positrino"], emitter="positrino"))
        emissions.append(Emission(time=current_time, pos=positions["electrino"], emitter="electrino"))

        update_emissions(current_time)
        allow_self = speed_mult > 1.0
        hits = detect_hits(current_time, positions, allow_self=allow_self)
        recent_hits.clear()
        recent_hits.extend(hits)

        if frame_idx % accum_stride == 0:
            field_surface = make_field_surface()
        render_frame(positions, hits)

        frame_idx += 1
        clock.tick(cfg.fps)

        if target_stop_at_posi_start:
            dx = positions["positrino"][0] - 1.0
            dy = positions["positrino"][1] - 0.0
            if math.hypot(dx, dy) <= 0.02 and frame_idx > 1:
                paused = True
                target_stop_at_posi_start = False
                stop_reached = True
                hits_at_stop = list(recent_hits)
                stop_positions = positions.copy()
                stop_field_surface = field_surface
                # Freeze the field/positions at stop; do not advance frame_idx further.
                frame_idx = frame_idx  # no-op for clarity

    pygame.quit()

def simulate(cfg: SimulationConfig, paths: Dict[str, PathSpec], path_name: str = "unit_circle", reverse: bool = False) -> List[Frame]:
    """
    Simulate positions, emissions, and hits for two architrinos on the selected path.
    This is a non-graphical pre-bake; hit detection is discrete per frame.
    """
    if path_name not in paths:
        raise ValueError(f"Unknown path '{path_name}'. Available: {list(paths.keys())}")

    # Clamp speed multiplier to [0, 100]; enforce positive field speed
    speed_mult = max(0.0, min(cfg.speed_multiplier, 100.0))
    field_v = max(cfg.field_speed, 1e-6)

    dt = 1.0 / cfg.fps
    duration = max(cfg.duration, estimate_coverage_duration(cfg))
    n_frames = int(math.ceil(duration / dt))

    path = paths[path_name]
    # Default: positrino at +phase, electrino at phase + pi.
    positrino = Architrino("positrino", +1, PURE_RED, 0.0, path, reverse=reverse)
    electrino = Architrino("electrino", -1, PURE_BLUE, math.pi, path, reverse=reverse)

    emissions: List[Emission] = []
    frames: List[Frame] = []

    seen_hits = set()
    for i in range(n_frames):
        t = i * dt
        path_t = speed_mult * t
        pos_posi = positrino.position(path_t)
        pos_elec = electrino.position(path_t)
        positions = {"positrino": pos_posi, "electrino": pos_elec}

        # Each particle emits once per frame (constant cadence).
        emissions.append(Emission(time=t, pos=pos_posi, emitter="positrino"))
        emissions.append(Emission(time=t, pos=pos_elec, emitter="electrino"))

        hits: List[Hit] = []
        # Check hits against past emissions (naive O(N^2); acceptable for small pre-bakes).
        radius_tol = max(field_v * dt, 0.005)  # relaxed tolerance to avoid missing hits
        for emission in emissions:
            tau = t - emission.time
            if tau <= 0:
                continue
            radius = field_v * tau
            # Check each receiver
            for receiver_name, receiver_pos in positions.items():
                # Skip zero-delay self-interaction (H(0)=0)
                if tau == 0 and emission.emitter == receiver_name:
                    continue
                # Optional self-hit gating: only allow self-hits when speed multiplier > 1
                if emission.emitter == receiver_name and speed_mult <= 1.0:
                    continue
                dist = l2(receiver_pos, emission.pos)
                # Allow small tolerance for discrete stepping
                if abs(dist - radius) <= radius_tol:
                    key = (emission.time, emission.emitter, receiver_name)
                    if key in seen_hits:
                        continue
                    seen_hits.add(key)
                    strength = 1.0 / (dist * dist) if dist > 0 else float("inf")
                    ang = angle_from_x_axis(receiver_pos)
                    hits.append(
                        Hit(
                            t_obs=t,
                            t_emit=emission.time,
                            emitter=emission.emitter,
                            receiver=receiver_name,
                            distance=dist,
                            strength=strength,
                            angle=ang,
                            speed_multiplier=speed_mult,
                            emit_pos=emission.pos,
                        )
                    )

        frames.append(Frame(time=t, positions=positions, hits=hits))

    return frames


def summarize(frames: List[Frame], max_hits: int = 5, max_frames: int = 5) -> str:
    lines: List[str] = []
    lines.append(f"Total frames: {len(frames)}")
    # Prefer frames that actually contain hits; fallback to earliest frames if none.
    hitful_frames = [f for f in frames if f.hits]
    sample_frames = (hitful_frames[:max_frames]) if hitful_frames else frames[:max_frames]

    for frame in sample_frames:
        lines.append(f"t={frame.time:.3f}s pos_elec={frame.positions['electrino']} pos_posi={frame.positions['positrino']}")
        for h in frame.hits[:max_hits]:
            lines.append(
                f"  hit t_emit={h.t_emit:.3f} -> t_obs={h.t_obs:.3f} emitter={h.emitter} receiver={h.receiver} "
                f"r={h.distance:.3f} strength={h.strength:.3f} angle={h.angle:.3f} speed_mult={h.speed_multiplier:.2f}"
            )
    # Aggregate hit counts
    total_hits = sum(len(f.hits) for f in frames)
    lines.append(f"Total hits detected: {total_hits}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="sim2 prototype (pre-bake simulation).")
    parser.add_argument("--fps", type=int, default=60, help="Frames per second (default 60).")
    parser.add_argument("--duration", type=float, default=4.0, help="Minimum duration in seconds (coverage heuristic may increase this).")
    parser.add_argument("--path", type=str, default="unit_circle", choices=list(PATH_LIBRARY.keys()), help="Trajectory name.")
    parser.add_argument("--reverse", action="store_true", help="Reverse path orientation.")
    parser.add_argument("--speed-mult", type=float, default=0.5, help="Path speed multiplier in [0, 100]; 0 => stationary.")
    parser.add_argument("--self-test", action="store_true", help="Run a quick simulation and print a summary.")
    parser.add_argument("--render", action="store_true", help="Open a PyGame window and render the live simulation.")
    parser.add_argument("--parallel-precompute", action="store_true", help="Parallelize precompute using process pool.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = SimulationConfig(fps=args.fps, duration=args.duration, speed_multiplier=args.speed_mult)
    if args.render:
        render_live(cfg, PATH_LIBRARY, path_name=args.path, reverse=args.reverse, parallel_precompute=args.parallel_precompute)
        return

    frames = simulate(cfg, PATH_LIBRARY, path_name=args.path, reverse=args.reverse)
    if args.self_test:
        print(summarize(frames))
    else:
        print("Simulation complete.")
        print(summarize(frames, max_hits=3, max_frames=3))


if __name__ == "__main__":
    main()
