"""
Orbit visualizer prototype (single-file).

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
    os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
    try:
        import pygame
        from pygame import gfxdraw
    except ImportError as exc:
        raise SystemExit("PyGame is required for rendering. Install with `pip install pygame`.") from exc

    if path_name not in paths:
        raise ValueError(f"Unknown path '{path_name}'. Available: {list(paths.keys())}")

    pygame.init()
    panel_w = 320
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h
    canvas_w = width - panel_w
    display_flags = pygame.RESIZABLE | pygame.SCALED
    screen = pygame.display.set_mode((width, height), display_flags)
    pygame.display.set_caption("Orbit Visualizer (prototype)")
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
    shell_thickness = 0.0
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

    grid_dx = (xs[-1] - xs[0]) / max(res_x - 1, 1)
    grid_dy = (ys[-1] - ys[0]) / max(res_y - 1, 1)

    def update_time_params(new_fps: int) -> None:
        nonlocal dt, shell_thickness
        cfg.fps = new_fps
        dt = 1.0 / cfg.fps
        base_shell = max(field_v * dt, 0.003)
        shell_thickness_local = max(base_shell, 0.75 * min(grid_dx, grid_dy))
        shell_thickness_local = max(shell_thickness_local, 0.003)
        shell_thickness = shell_thickness_local

    update_time_params(cfg.fps)

    def world_to_screen(p: Vec2) -> Vec2:
        scale = min(canvas_w, height) / (2 * cfg.domain_half_extent)
        sx = panel_w + canvas_w / 2 + p[0] * scale
        sy = height / 2 + p[1] * scale
        return sx, sy

    def world_to_canvas(p: Vec2) -> Vec2:
        """Like world_to_screen but with the canvas origin at (0, 0)."""
        sx, sy = world_to_screen(p)
        return sx - panel_w, sy

    def clamp_speed(v: float) -> float:
        return max(0.0, min(v, 100.0))

    def compute_self_delta(speed: float, v_field: float) -> float | None:
        """
        Smallest positive root of 2*sin(s*Δ/2) = v*Δ for a unit circle self-hit.
        Returns None if speed <= v_field (no self hits) or no root found.
        """
        if speed <= v_field + 1e-6:
            return None

        def f(d: float) -> float:
            return 2.0 * math.sin(0.5 * speed * d) - v_field * d

        # Initial bracket around the smallest root
        hi = max(2.0, 2 * math.pi / max(speed, 1e-6))
        for _ in range(120):
            if f(hi) < 0:
                break
            hi *= 1.5
        else:
            return None
        lo = 0.0
        for _ in range(80):
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
        radius_tol_self = max(field_v * dt * 1.5, 0.01)
        cleanup_hits(current_time)

        # Partner hits (emitter != receiver)
        for em in emissions:
            tau = current_time - em.time
            if tau <= 0:
                continue
            radius = field_v * tau
            if radius > max_radius:
                continue
            for receiver_name, receiver_pos in positions.items():
                if em.emitter == receiver_name:
                    continue
                dist = l2(receiver_pos, em.pos)
                diff = dist - radius
                key = (em.time, em.emitter, receiver_name)
                prev = last_diff.get(key)
                crossing = prev is not None and prev * diff <= 0.0
                last_diff[key] = diff
                last_diff_queue.append((em.time, key))
                if abs(diff) <= radius_tol_cross or crossing:
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

        # Self hits (analytic for unit circle using self_delta; fallback to none otherwise)
        if allow_self and self_delta is not None and current_time >= self_delta:
            for name, receiver_pos in positions.items():
                t_emit = current_time - self_delta
                emit_pos = emitter_lookup[name].position(speed_mult * t_emit)
                dist = l2(receiver_pos, emit_pos)
                diff = dist - field_v * self_delta
                key = (t_emit, name, name)
                prev = last_diff.get(key)
                crossing = prev is not None and prev * diff <= 0.0
                last_diff[key] = diff
                last_diff_queue.append((t_emit, key))
                if abs(diff) <= radius_tol_self or crossing:
                    if key in seen_hits:
                        continue
                    seen_hits.add(key)
                    seen_hits_queue.append((t_emit, key))
                    vec = (receiver_pos[0] - emit_pos[0], receiver_pos[1] - emit_pos[1])
                    ang = angle_from_x_axis(vec)
                    strength = 1.0 / (dist * dist) if dist > 0 else float("inf")
                    hits.append(
                        Hit(
                            t_obs=current_time,
                            t_emit=t_emit,
                            emitter=name,
                            receiver=name,
                            distance=dist,
                            strength=strength,
                            angle=ang,
                            speed_multiplier=speed_mult,
                            emit_pos=emit_pos,
                        )
                    )

        return hits

    def analytic_hits(current_time: float, positions: Dict[str, Vec2], allow_self: bool, max_time: float) -> List[Hit]:
        hits: List[Hit] = []
        sample_steps = 360
        step = max_time / sample_steps if sample_steps > 0 else max_time
        tol = 1e-3

        def g(emitter_name: str, receiver_name: str, delta_t: float) -> float:
            t_emit = current_time - delta_t
            emit_pos = emitter_lookup[emitter_name].position(speed_mult * t_emit)
            dist = l2(positions[receiver_name], emit_pos)
            return dist - field_v * delta_t

        for emitter_name in ("positrino", "electrino"):
            for receiver_name in ("positrino", "electrino"):
                is_self = emitter_name == receiver_name
                if is_self:
                    if not allow_self or allow_self and speed_mult <= field_v + 1e-6:
                        continue
                roots_found = 0
                last_root_time = None
                prev_delta = max(step * 0.5, 1e-4)
                prev_val = g(emitter_name, receiver_name, prev_delta)
                for j in range(1, sample_steps + 1):
                    delta = j * step
                    val = g(emitter_name, receiver_name, delta)
                    root = None
                    if abs(val) <= tol:
                        root = delta
                    elif prev_val * val < 0:
                        lo, hi = prev_delta, delta
                        for _ in range(30):
                            mid = 0.5 * (lo + hi)
                            mid_val = g(emitter_name, receiver_name, mid)
                            if abs(mid_val) <= tol:
                                root = mid
                                break
                            if prev_val * mid_val <= 0:
                                hi = mid
                                val = mid_val
                            else:
                                lo = mid
                                prev_val = mid_val
                        if root is None:
                            root = 0.5 * (lo + hi)
                    if root is not None and root > 0:
                        if last_root_time is not None and abs(root - last_root_time) < max(5 * tol, 0.002):
                            prev_delta = delta
                            prev_val = val
                            continue
                        t_emit = current_time - root
                        emit_pos = emitter_lookup[emitter_name].position(speed_mult * t_emit)
                        recv_pos = positions[receiver_name]
                        dist = l2(recv_pos, emit_pos)
                        if dist <= 0:
                            continue
                        strength = 1.0 / (dist * dist)
                        vec = (recv_pos[0] - emit_pos[0], recv_pos[1] - emit_pos[1])
                        ang = angle_from_x_axis(vec)
                        hits.append(
                            Hit(
                                t_obs=current_time,
                                t_emit=t_emit,
                                emitter=emitter_name,
                                receiver=receiver_name,
                                distance=dist,
                                strength=strength,
                                angle=ang,
                                speed_multiplier=speed_mult,
                                emit_pos=emit_pos,
                            )
                        )
                        roots_found += 1
                        last_root_time = root
                        if roots_found >= 2:
                            break
                    prev_delta = delta
                    prev_val = val
        return hits

    def draw_text(target: "pygame.Surface", text: str, x: int, y: int, color=(0, 0, 0)) -> None:
        surf = font.render(text, True, color)
        target.blit(surf, (x, y))

    def reset_state(apply_pending_speed: bool = True) -> None:
        nonlocal emissions, field_grid, frame_idx, stop_reached, target_stop_at_posi_start, hits_at_stop, speed_mult, field_surface, stop_positions, stop_field_surface, self_delta, positions
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
        positions = current_positions(0.0)
        recent_hits.extend(analytic_hits(0.0, positions, speed_mult > field_v, emission_retention))

    def render_frame(positions: Dict[str, Vec2], hits: List[Hit], field_surf=None) -> None:
        screen.fill(PURE_WHITE)
        fs = field_surf if field_surf is not None else field_surface
        screen.blit(fs, (panel_w, 0))

        geometry_layer = pygame.Surface((canvas_w, height), pygame.SRCALPHA).convert_alpha()
        if path_name == "unit_circle":
            center = world_to_canvas((0.0, 0.0))
            scale = min(canvas_w, height) / (2 * cfg.domain_half_extent)
            gfxdraw.aacircle(geometry_layer, int(center[0]), int(center[1]), int(scale), GRAY)

        for h in hits:
            start = world_to_canvas(h.emit_pos)
            end = world_to_canvas(positions[h.receiver])
            gfxdraw.line(geometry_layer, int(start[0]), int(start[1]), int(end[0]), int(end[1]), GRAY)

        particle_layer = pygame.Surface((canvas_w, height), pygame.SRCALPHA).convert_alpha()
        for h in hits:
            start = world_to_canvas(h.emit_pos)
            marker_color = LIGHT_RED if h.emitter == "positrino" else LIGHT_BLUE
            gfxdraw.filled_circle(particle_layer, int(start[0]), int(start[1]), 4, marker_color)
            gfxdraw.aacircle(particle_layer, int(start[0]), int(start[1]), 5, PURE_WHITE)

        pos_posi_canvas = world_to_canvas(positions["positrino"])
        pos_elec_canvas = world_to_canvas(positions["electrino"])
        gfxdraw.filled_circle(particle_layer, int(pos_posi_canvas[0]), int(pos_posi_canvas[1]), 6, PURE_RED)
        gfxdraw.aacircle(particle_layer, int(pos_posi_canvas[0]), int(pos_posi_canvas[1]), 7, PURE_WHITE)
        gfxdraw.filled_circle(particle_layer, int(pos_elec_canvas[0]), int(pos_elec_canvas[1]), 6, PURE_BLUE)
        gfxdraw.aacircle(particle_layer, int(pos_elec_canvas[0]), int(pos_elec_canvas[1]), 7, PURE_WHITE)

        ui_layer = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(ui_layer, (245, 245, 245), (0, 0, panel_w, height))
        draw_text(ui_layer, f"frame={frame_idx+1}", 10, 10)
        draw_text(ui_layer, f"fps={cfg.fps}", 10, 30)
        if paused and pending_speed_mult != speed_mult:
            draw_text(ui_layer, f"speed_mult={speed_mult:.2f} -> {pending_speed_mult:.2f}", 10, 50)
        else:
            draw_text(ui_layer, f"speed_mult={speed_mult:.2f}", 10, 50)
        draw_text(ui_layer, "Controls:", 10, 80)
        draw_text(ui_layer, "ESC quit, SPACE pause", 10, 100)
        draw_text(ui_layer, "UP/DOWN speed (auto-pause)", 10, 120)
        draw_text(ui_layer, "RIGHT: run to positrino start", 10, 140)
        draw_text(ui_layer, "F: toggle fps 30/60", 10, 160)
        draw_text(ui_layer, "Hit table (t = now):", 10, 190)
        y = 210
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
            draw_text(ui_layer, text, 10, y, color=color)
            y += 18

        hits_for_labels = hits_at_stop if stop_reached and hits_at_stop else hits
        circle_center_screen = world_to_screen((0.0, 0.0))
        circle_radius = min(canvas_w, height) / (2 * cfg.domain_half_extent)
        for h in hits_for_labels:
            emit_canvas = world_to_canvas(h.emit_pos)
            vec_to_receiver = positions[h.receiver][0] - h.emit_pos[0], positions[h.receiver][1] - h.emit_pos[1]
            ang_screen_deg = angle_deg_screen(vec_to_receiver)
            label = f"{ang_screen_deg:.1f}°"
            emit_screen = (panel_w + emit_canvas[0], emit_canvas[1])
            dir_vec = (
                emit_screen[0] - circle_center_screen[0],
                emit_screen[1] - circle_center_screen[1],
            )
            dir_len = math.hypot(dir_vec[0], dir_vec[1]) or 1.0
            offset = circle_radius / 6
            label_pos = (
                emit_screen[0] + (dir_vec[0] / dir_len) * offset + 8,
                emit_screen[1] + (dir_vec[1] / dir_len) * offset - 12,
            )
            draw_text(
                ui_layer,
                label,
                int(label_pos[0]),
                int(label_pos[1]),
                color=GRAY,
            )

        if paused:
            draw_text(ui_layer, "PAUSED", 10, height - 30)

        screen.blit(geometry_layer, (panel_w, 0))
        screen.blit(particle_layer, (panel_w, 0))
        screen.blit(ui_layer, (0, 0))
        pygame.display.flip()

    def current_positions(time_t: float) -> Dict[str, Vec2]:
        path_t = speed_mult * time_t
        return {
            "positrino": positrino.position(path_t),
            "electrino": electrino.position(path_t),
        }

    positions = current_positions(0.0)
    field_surface = make_field_surface()

    # Only refresh the field surface every few frames to reduce cost.
    accum_stride = 2

    def prune_emissions(current_time: float) -> None:
        nonlocal emissions
        cutoff = current_time - emission_retention
        if cutoff <= 0:
            return
        emissions = [em for em in emissions if em.time >= cutoff]

    reset_state(apply_pending_speed=False)
    render_frame(positions, list(recent_hits))

    pygame.key.set_repeat(200, 50)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if paused:
                        if pending_speed_mult != speed_mult:
                            reset_state(apply_pending_speed=True)
                        paused = False
                    else:
                        paused = True
                elif event.key == pygame.K_UP:
                    pending_speed_mult = clamp_speed(pending_speed_mult + 0.01)
                    reset_state(apply_pending_speed=True)
                    paused = True
                elif event.key == pygame.K_DOWN:
                    pending_speed_mult = clamp_speed(pending_speed_mult - 0.01)
                    reset_state(apply_pending_speed=True)
                    paused = True
                elif event.key == pygame.K_RIGHT:
                    if pending_speed_mult != speed_mult:
                        reset_state(apply_pending_speed=True)
                    stop_reached = False
                    hits_at_stop = []
                    target_stop_at_posi_start = True
                    paused = False
                elif event.key == pygame.K_f:
                    new_fps = 60 if cfg.fps == 30 else 30
                    update_time_params(new_fps)
                    reset_state(apply_pending_speed=False)
                    paused = True

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
        allow_self = speed_mult > field_v + 1e-6
        hits = detect_hits(current_time, positions, allow_self=allow_self)
        display_hits = hits
        if not display_hits:
            display_hits = analytic_hits(current_time, positions, allow_self, emission_retention)
        recent_hits.clear()
        recent_hits.extend(display_hits)

        if frame_idx % accum_stride == 0:
            field_surface = make_field_surface()
        render_frame(positions, display_hits)

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
    parser = argparse.ArgumentParser(description="Orbit visualizer prototype (pre-bake simulation).")
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
