"""
Orbit visualizer prototype (single-file).

Implements core math and a non-graphical, testable pipeline:
• Path sampling for predefined trajectories (unit circle, exponential inward spiral).
• Emission bookkeeping with constant field speed v=1 and 1/r^2 falloff.
• Hit detection via causal condition ||s_r(t) - s_e(t0)|| = v * (t - t0).
• Basic pre-bake loop that can run until domain coverage is achieved.

Usage:
    python orbits.py --run circle.json
    python orbits.py --run spiral.json

Run files expect top-level "directives" and a "groups" array; see orbit-visualizer/circle.json.

Per codex: You can push the field snapshot finer in a few ways; each trades directly against CPU time/memory:

  - Increase the grid resolution: bump base_res above 640 to shrink pixel size; or shrink the
    domain_half_extent if you only care about a tighter view.
  - Make shells thinner: lower shell_thickness toward field_v*dt (or a fixed small value) so the
    annulus band is narrower.
  - Sample more times: raise the sampling rate so more shell positions are accumulated.
  - Use a tighter linear map: if you want more dynamic range resolution, adjust
    the percentile cut or scaling.

  Beyond that, heavier options are GPU rendering (e.g., CUDA/Metal) or adaptive/multi-resolution
  grids, but those require more refactor.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Tuple
import numpy as np

Vec2 = Tuple[float, float]



# Color constants (RGB)
PURE_RED = (255, 0, 0)
PURE_BLUE = (0, 0, 255)
PURE_PURPLE = (255, 0, 255)  # neutral (red + blue)
PURE_WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
LIGHT_RED = (255, 160, 160)
LIGHT_BLUE = (160, 200, 255)


@dataclass
class PathSpec:
    name: str
    sampler: Callable[[float], Vec2]
    description: str
    decay: float | None = None  # optional radial decay parameter


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
class Architrino:
    name: str
    polarity: int  # +1 positrino, -1 electrino
    color: Tuple[int, int, int]
    phase: float  # radians
    path: PathSpec

    def position(self, t: float, speed_mult: float | None = None, field_v: float | None = None) -> Vec2:
        """Position on the assigned path with phase offset."""
        # For spirals, decay is based on the traveled angle; phase only rotates the angle.
        if self.path.name == "exp_inward_spiral" and self.path.decay is not None:
            base_param = t
            decay_scale = 1.0
            if speed_mult is not None and field_v is not None and speed_mult > field_v + 1e-6:
                decay_scale = 2.0
            angle = base_param + self.phase
            radius = math.exp(-self.path.decay * abs(base_param) * decay_scale)
            return radius * math.cos(angle), radius * math.sin(angle)
        param = t + self.phase
        x, y = self.path.sampler(param)
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
    speed_multiplier: float  # path speed multiplier applied during this frame
    emit_pos: Vec2


@dataclass
class SimulationConfig:
    hz: int = 1000
    field_speed: float = 1.0  # v=1
    domain_half_extent: float = 2.0  # domain [-2,2] by default
    speed_multiplier: float = 0.5  # path speed scaling in [0, 100]; 0 => stationary
    position_snap: float | None = None  # optional spatial quantization step
    path_snap: float | None = None  # optional path-parameter snap step
    field_visible: bool = True  # show field texture by default in render mode
    start_paused: bool = True  # render loop starts paused unless overridden
    field_grid_scale_with_canvas: bool = False  # scale field grid resolution by canvas scale
    shell_thickness_scale_with_canvas: bool = False  # scale shell thickness by 1/canvas_scale
    field_color_falloff: str = "inverse_r2"  # "inverse_r2" (log10) or "inverse_r" (sqrt log10)
    shell_weight: str = "raised_cosine"  # "raised_cosine" or "hard"
    field_alg: str = "gpu_instanced"  # "cpu_rebuild", "cpu_incremental", or "gpu_instanced"


@dataclass
class OrbitConfig:
    path: str
    speed_multiplier: float | None = None
    decay: float | None = None


@dataclass
class ArchitrinoGroupSpec:
    name: str
    electrinos: int
    positrinos: int
    orbit: OrbitConfig | None = None
    simulation: Dict[str, object] | None = None


@dataclass
class RunScenario:
    config: SimulationConfig
    groups: List[ArchitrinoGroupSpec]
    paths: Dict[str, PathSpec]
    render: bool = False

    def primary_orbit(self) -> OrbitConfig:
        if not self.groups or self.groups[0].orbit is None:
            raise ValueError("Scenario has no primary orbit configured.")
        return self.groups[0].orbit


def l2(a: Vec2, b: Vec2) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.hypot(dx, dy)


def snap_position(pos: Vec2, snap_distance: float | None) -> Vec2:
    if snap_distance is None or snap_distance <= 0:
        return pos
    return (
        round(pos[0] / snap_distance) * snap_distance,
        round(pos[1] / snap_distance) * snap_distance,
    )


def _expect_dict(value: object, label: str) -> Dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object.")
    return value


def _expect_list(value: object, label: str) -> List[object]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a JSON array.")
    return value


def _coerce_float(value: object, label: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a number.") from exc


def _coerce_int(value: object, label: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be an integer.") from exc


def load_run_file(
    run_path: str,
    paths: Dict[str, PathSpec],
) -> RunScenario:
    run_file = Path(run_path).expanduser()
    if not run_file.is_file():
        script_dir = Path(__file__).resolve().parent
        fallback = script_dir / run_file.name
        if fallback.is_file():
            run_file = fallback
        else:
            raise FileNotFoundError(f"Run file not found: {run_path}")
    with run_file.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    payload = _expect_dict(payload, "run file")

    directives = payload.get("directives", {})
    if directives is None:
        directives = {}
    directives = _expect_dict(directives, "directives")

    groups = _expect_list(payload.get("groups"), "groups")
    if not groups:
        raise ValueError("Run file requires at least one architrino group.")
    if len(groups) != 1:
        raise ValueError("Run file currently supports exactly one group.")
    group = _expect_dict(groups[0], "group")
    group_name = group.get("name", "group-1")

    if "electrinos" not in group or "positrinos" not in group:
        raise ValueError(f"Group '{group_name}' requires 'electrinos' and 'positrinos' counts.")
    electrinos = _coerce_int(group.get("electrinos"), f"group '{group_name}' electrinos")
    positrinos = _coerce_int(group.get("positrinos"), f"group '{group_name}' positrinos")
    if electrinos != 1 or positrinos != 1:
        raise ValueError("Run file currently supports exactly 1 electrino and 1 positrino per group.")

    orbit = group.get("orbit")
    simulation = group.get("simulation")
    if orbit is not None and simulation is not None:
        raise ValueError(f"Group '{group_name}' cannot define both 'orbit' and 'simulation'.")
    if simulation is not None:
        raise NotImplementedError("Simulation groups are not implemented yet.")
    if orbit is None:
        raise ValueError(f"Group '{group_name}' must define an 'orbit' or 'simulation' block.")
    orbit = _expect_dict(orbit, f"group '{group_name}' orbit")

    path_name = orbit.get("path") or orbit.get("name")
    if not isinstance(path_name, str):
        raise ValueError(f"Group '{group_name}' orbit requires a string 'path'.")
    if path_name not in paths:
        raise ValueError(f"Unknown path '{path_name}'. Available: {list(paths.keys())}")

    speed_mult_value = orbit.get("speed_multiplier", directives.get("speed_multiplier", 0.5))
    speed_mult = _coerce_float(speed_mult_value, f"group '{group_name}' speed_multiplier")

    path_snap = directives.get("path_snap", directives.get("path_step"))
    if path_snap is not None:
        path_snap = _coerce_float(path_snap, "directives.path_snap")
        if path_snap <= 0:
            raise ValueError("directives.path_snap must be > 0.")

    position_snap = directives.get("position_snap", directives.get("snap_distance"))
    if position_snap is not None:
        position_snap = _coerce_float(position_snap, "directives.position_snap")
        if position_snap <= 0:
            raise ValueError("directives.position_snap must be > 0.")

    field_visible = bool(directives.get("field_visible", directives.get("field_on", True)))
    start_paused = bool(directives.get("start_paused", True))
    field_grid_scale_with_canvas = bool(directives.get("field_grid_scale_with_canvas", False))
    shell_thickness_scale_with_canvas = bool(directives.get("shell_thickness_scale_with_canvas", False))
    field_color_falloff = directives.get("field_color_falloff", "inverse_r2")
    if not isinstance(field_color_falloff, str):
        raise ValueError("directives.field_color_falloff must be a string.")
    field_color_falloff = field_color_falloff.lower()
    if field_color_falloff not in {"inverse_r2", "inverse_r"}:
        raise ValueError("directives.field_color_falloff must be 'inverse_r2' or 'inverse_r'.")
    shell_weight = directives.get("shell_weight", "raised_cosine")
    if not isinstance(shell_weight, str):
        raise ValueError("directives.shell_weight must be a string.")
    shell_weight = shell_weight.lower()
    if shell_weight not in {"raised_cosine", "hard"}:
        raise ValueError("directives.shell_weight must be 'raised_cosine' or 'hard'.")
    field_alg = directives.get("field_alg", "gpu_instanced")
    if not isinstance(field_alg, str):
        raise ValueError("directives.field_alg must be a string.")
    field_alg = field_alg.lower()
    if field_alg not in {"cpu_rebuild", "cpu_incremental", "gpu_instanced"}:
        raise ValueError(
            "directives.field_alg must be 'cpu_rebuild', 'cpu_incremental', or 'gpu_instanced'."
        )

    cfg = SimulationConfig(
        hz=_coerce_int(directives.get("hz", 1000), "directives.hz"),
        field_speed=_coerce_float(directives.get("field_speed", 1.0), "directives.field_speed"),
        domain_half_extent=_coerce_float(directives.get("domain_half_extent", 2.0), "directives.domain_half_extent"),
        speed_multiplier=speed_mult,
        position_snap=position_snap,
        path_snap=path_snap,
        field_visible=field_visible,
        start_paused=start_paused,
        field_grid_scale_with_canvas=field_grid_scale_with_canvas,
        shell_thickness_scale_with_canvas=shell_thickness_scale_with_canvas,
        field_color_falloff=field_color_falloff,
        shell_weight=shell_weight,
        field_alg=field_alg,
    )

    paths_override = paths
    decay = None
    decay_value = orbit.get("decay")
    if decay_value is not None:
        if path_name != "exp_inward_spiral":
            raise ValueError("orbit.decay is only supported for exp_inward_spiral.")
        decay = _coerce_float(decay_value, f"group '{group_name}' orbit.decay")
        base = paths[path_name]
        paths_override = dict(paths)
        paths_override[path_name] = PathSpec(
            name=base.name,
            sampler=base.sampler,
            description=base.description,
            decay=decay,
        )

    render = bool(directives.get("render", False))
    orbit_spec = OrbitConfig(
        path=path_name,
        speed_multiplier=speed_mult,
        decay=decay,
    )
    group_spec = ArchitrinoGroupSpec(
        name=group_name,
        electrinos=electrinos,
        positrinos=positrinos,
        orbit=orbit_spec,
    )
    return RunScenario(
        config=cfg,
        groups=[group_spec],
        paths=paths_override,
        render=render,
    )


def render_live(cfg: SimulationConfig, paths: Dict[str, PathSpec], path_name: str = "unit_circle") -> None:
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
    panel_w = 160
    canvas_scale = 1.0
    if canvas_scale <= 0:
        raise ValueError("canvas_scale must be > 0.")
    info = pygame.display.Info()
    field_alg = cfg.field_alg
    gpu_display = False
    if field_alg == "gpu_instanced":
        try:
            import moderngl  # noqa: F401
            gpu_display = True
        except ImportError:
            field_alg = "cpu_incremental"
    display_flags = pygame.RESIZABLE
    if gpu_display:
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        display_flags |= pygame.OPENGL | pygame.DOUBLEBUF
    max_side = min(info.current_h, max(1, info.current_w - panel_w))
    canvas_side = max(1, int(max_side * canvas_scale))
    canvas_w = canvas_side
    width = panel_w + canvas_w
    height = canvas_w
    screen = pygame.display.set_mode((width, height), display_flags)
    pygame.display.set_caption("Orbit Visualizer (prototype)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 12)

    current_path_name = path_name
    path = paths[current_path_name]
    positrino = Architrino("positrino", +1, PURE_RED, 0.0, path)
    electrino = Architrino("electrino", -1, PURE_BLUE, math.pi, path)

    running = True
    paused = cfg.start_paused
    frame_idx = 0
    sim_clock_start = time.monotonic()
    sim_clock_elapsed = 0.0

    dt = 1.0 / cfg.hz
    field_v = max(cfg.field_speed, 1e-6)
    shell_thickness = 0.0
    speed_mult = max(0.0, min(cfg.speed_multiplier, 100.0))
    pending_speed_mult = speed_mult
    position_snap = cfg.position_snap
    path_snap = cfg.path_snap
    frame_skip = 0

    def snap_param(param: float) -> float:
        if path_snap is None or path_snap <= 0:
            return param
        return round(param / path_snap) * path_snap

    def snap_pos(pos: Vec2) -> Vec2:
        if path_snap is not None and path_snap > 0:
            return pos
        return snap_position(pos, position_snap)

    def position_at(emitter: Architrino, param: float) -> Vec2:
        return snap_pos(emitter.position(snap_param(param), speed_mult, field_v))

    max_radius = math.sqrt(2) * cfg.domain_half_extent * 1.1
    emission_retention = max_radius / field_v
    emissions: List[Emission] = []
    recent_hits = deque()
    panel_log: List[str] = []
    seen_hits = set()
    seen_hits_queue = deque()
    last_diff = {}
    last_diff_queue = deque()
    emitter_lookup = {"positrino": positrino, "electrino": electrino}
    path_traces: Dict[str, List[Vec2]] = {"positrino": [], "electrino": []}
    BASE_OFFSET = 6.0 * math.pi  # start with 3 full revolutions
    path_time_offset = BASE_OFFSET
    trace_limit = 40000
    hit_overlay_enabled = False
    show_hit_overlays = False
    trace_test_frames_remaining: int | None = None
    last_caption_update = 0

    # Grid for the accumulator at a coarser resolution to reduce work; upscale for display.
    base_res = 640
    if cfg.field_grid_scale_with_canvas:
        base_res = max(64, int(base_res * canvas_scale))
    res_x = res_y = max(64, base_res)
    x_extent = y_extent = cfg.domain_half_extent
    xs = np.linspace(-x_extent, x_extent, res_x)
    ys = np.linspace(-y_extent, y_extent, res_y)
    xx, yy = np.meshgrid(xs, ys)
    eps = 1e-6

    field_grid = np.zeros_like(xx, dtype=np.float32)
    field_surface = None
    field_visible = cfg.field_visible
    shell_weight = cfg.shell_weight
    ui_overlay_visible = True
    gpu_state = None

    grid_dx = (xs[-1] - xs[0]) / max(res_x - 1, 1)
    grid_dy = (ys[-1] - ys[0]) / max(res_y - 1, 1)

    shell_thickness_scale = 1.0
    if cfg.shell_thickness_scale_with_canvas:
        shell_thickness_scale = 1.0 / canvas_scale

    def update_time_params(new_hz: int) -> None:
        nonlocal dt, shell_thickness
        cfg.hz = new_hz
        dt = 1.0 / cfg.hz
        base_shell = max(field_v * dt, 0.003)
        shell_thickness_local = max(base_shell, 0.75 * min(grid_dx, grid_dy))
        shell_thickness_local = max(shell_thickness_local, 0.003)
        shell_thickness = shell_thickness_local * shell_thickness_scale

    update_time_params(cfg.hz)

    def world_to_screen(p: Vec2) -> Vec2:
        scale = canvas_w / (2 * cfg.domain_half_extent)
        sx = panel_w + canvas_w / 2 + p[0] * scale
        sy = canvas_w / 2 + p[1] * scale
        return sx, sy

    def world_to_canvas(p: Vec2) -> Vec2:
        """Like world_to_screen but with the canvas origin at (0, 0)."""
        sx, sy = world_to_screen(p)
        return sx - panel_w, sy

    def clamp_speed(v: float) -> float:
        return max(0.0, min(v, 100.0))

    def apply_speed_change(new_speed: float, auto_pause: bool = True) -> None:
        nonlocal speed_mult, pending_speed_mult, paused, path_time_offset
        current_time = frame_idx * dt
        prev_speed = speed_mult
        speed_mult = clamp_speed(new_speed)
        pending_speed_mult = speed_mult
        # Preserve the current path parameter so paused positions stay fixed.
        path_time_offset += (prev_speed - speed_mult) * current_time
        refresh_hits_for_current_time()
        if auto_pause:
            paused = True

    def make_field_surface() -> "pygame.Surface":
        net = field_grid
        abs_net = np.abs(net)
        max_abs = np.percentile(abs_net, 99) if np.any(abs_net) else 1.0
        if max_abs < 1e-9:
            max_abs = 1.0
        log_max = math.log10(1.0 + max_abs)
        if log_max <= 0:
            log_max = 1.0
        mag = np.log10(1.0 + abs_net) / log_max
        mag = np.clip(mag, 0.0, 1.0)
        pos_norm = np.where(net > 0.0, mag, 0.0)
        neg_norm = np.where(net < 0.0, mag, 0.0)
        if cfg.field_color_falloff == "inverse_r":
            pos_norm = np.sqrt(pos_norm)
            neg_norm = np.sqrt(neg_norm)
        red = (255 * (1 - neg_norm)).astype(np.uint8)
        blue = (255 * (1 - pos_norm)).astype(np.uint8)
        green = (255 * (1 - np.maximum(pos_norm, neg_norm))).astype(np.uint8)
        rgb = np.stack([red, green, blue], axis=-1)
        surf = pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))
        surf = pygame.transform.smoothscale(surf, (canvas_w, height))
        return surf.convert()

    def apply_shell(em: Emission, radius: float, weight_scale: float = 1.0) -> None:
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

        if shell_weight == "hard":
            radial_weight = np.ones_like(delta[mask])
        else:
            # Smooth radial weight (raised cosine) to reduce aliasing.
            radial_weight = 0.5 * (1.0 + np.cos(np.pi * delta[mask] / band_half))
        sign = 1.0 if em.emitter == "positrino" else -1.0
        contrib = (sign * weight_scale) * radial_weight / (dist[mask] ** 2)
        field_grid[y0:y1, x0:x1][mask] += contrib

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
                if em.emitter == receiver_name and not allow_self:
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
                    strength = 1.0 / (dist * dist) if dist > 0 else float("inf")
                    hits.append(
                        Hit(
                            t_obs=current_time,
                            t_emit=em.time,
                            emitter=em.emitter,
                            receiver=receiver_name,
                            distance=dist,
                            strength=strength,
                            speed_multiplier=speed_mult,
                            emit_pos=em.pos,
                        )
                    )

        return hits

    def draw_text(target: "pygame.Surface", text: str, x: int, y: int, color=(0, 0, 0), fnt=None) -> None:
        surf = (fnt or font).render(text, True, color)
        target.blit(surf, (x, y))

    def rebuild_field_surface(current_time: float, update_last_radius: bool = False) -> None:
        nonlocal field_surface
        field_grid[:] = 0.0
        for em in emissions:
            tau = current_time - em.time
            if tau <= 0:
                if update_last_radius:
                    em.last_radius = 0.0
                continue
            radius = field_v * tau
            if radius > max_radius:
                if update_last_radius:
                    em.last_radius = 0.0
                continue
            apply_shell(em, radius)
            if update_last_radius:
                em.last_radius = radius
        field_surface = make_field_surface()

    def update_field_surface(current_time: float) -> None:
        nonlocal field_surface
        radius_quantum = max(0.5 * min(grid_dx, grid_dy), 0.5 * shell_thickness)
        for em in emissions:
            tau = current_time - em.time
            if tau <= 0:
                continue
            radius = field_v * tau
            if radius > max_radius:
                if em.last_radius > 0:
                    apply_shell(em, em.last_radius, weight_scale=-1.0)
                    em.last_radius = 0.0
                continue
            last_radius = em.last_radius
            if last_radius > 0 and abs(radius - last_radius) < radius_quantum:
                continue
            if last_radius > 0:
                apply_shell(em, last_radius, weight_scale=-1.0)
            apply_shell(em, radius)
            em.last_radius = radius
        field_surface = make_field_surface()

    def init_gpu_renderer(display: bool) -> bool:
        nonlocal gpu_state, field_alg
        if gpu_state is not None:
            return True
        try:
            import moderngl
        except ImportError:
            print("Moderngl not available; falling back to cpu_incremental.")
            field_alg = "cpu_incremental"
            return False
        try:
            ctx = moderngl.create_context() if display else moderngl.create_standalone_context()
        except Exception as exc:
            print(f"GPU alg unavailable ({exc}); falling back to cpu_incremental.")
            if not display:
                field_alg = "cpu_incremental"
            return False
        field_tex = ctx.texture((res_x, res_y), components=1, dtype="f4")
        fbo = ctx.framebuffer(color_attachments=[field_tex])
        quad = np.array(
            [
                -1.0,
                -1.0,
                1.0,
                -1.0,
                -1.0,
                1.0,
                1.0,
                1.0,
            ],
            dtype=np.float32,
        )
        vbo = ctx.buffer(quad.tobytes())
        inst_buffer = ctx.buffer(reserve=4 * 4)
        ring_prog = ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_pos;
                in vec2 inst_center;
                in float inst_radius;
                in float inst_sign;
                uniform float domain_half_extent;
                uniform float band_half;
                out vec2 v_world;
                flat out vec2 v_center;
                flat out float v_radius;
                flat out float v_band;
                flat out float v_sign;
                void main() {
                    float extent = inst_radius + band_half;
                    vec2 world = inst_center + in_pos * extent;
                    v_world = world;
                    v_center = inst_center;
                    v_radius = inst_radius;
                    v_band = band_half;
                    v_sign = inst_sign;
                    vec2 ndc = vec2(world.x / domain_half_extent, -world.y / domain_half_extent);
                    gl_Position = vec4(ndc, 0.0, 1.0);
                }
            """,
            fragment_shader="""
                #version 330
                in vec2 v_world;
                flat in vec2 v_center;
                flat in float v_radius;
                flat in float v_band;
                flat in float v_sign;
                out vec4 out_color;
                uniform int use_hard;
                void main() {
                    float dist = length(v_world - v_center);
                    float delta = abs(dist - v_radius);
                    if (delta > v_band) {
                        discard;
                    }
                    float weight = use_hard == 1 ? 1.0 : 0.5 * (1.0 + cos(3.14159265 * delta / v_band));
                    float denom = max(dist * dist, 1e-6);
                    float contrib = v_sign * weight / denom;
                    out_color = vec4(contrib, 0.0, 0.0, 1.0);
                }
            """,
        )
        vao = ctx.vertex_array(
            ring_prog,
            [
                (vbo, "2f", "in_pos"),
                (inst_buffer, "2f 1f 1f/i", "inst_center", "inst_radius", "inst_sign"),
            ],
        )
        screen_prog = None
        screen_vao = None
        overlay_prog = None
        overlay_vbo = None
        overlay_vao = None
        if display:
            screen_prog = ctx.program(
                vertex_shader="""
                    #version 330
                    in vec2 in_pos;
                    in vec2 in_uv;
                    out vec2 v_uv;
                    void main() {
                        v_uv = in_uv;
                        gl_Position = vec4(in_pos, 0.0, 1.0);
                    }
                """,
                fragment_shader="""
                    #version 330
                    uniform sampler2D field_tex;
                    uniform float field_scale;
                    uniform int falloff_mode;
                    in vec2 v_uv;
                    out vec4 out_color;
                    void main() {
                        const float LOG10 = 2.30258509299;
                        float val = texture(field_tex, v_uv).r;
                        float abs_val = abs(val);
                        float log_max = log(1.0 + field_scale) / LOG10;
                        float mag = log(1.0 + abs_val) / max(log_max, 1e-6);
                        mag = clamp(mag, 0.0, 1.0);
                        if (falloff_mode == 1) {
                            mag = sqrt(mag);
                        }
                        float pos = val > 0.0 ? mag : 0.0;
                        float neg = val < 0.0 ? mag : 0.0;
                        float green = 1.0 - max(pos, neg);
                        out_color = vec4(1.0 - neg, green, 1.0 - pos, 1.0);
                    }
                """,
            )
            overlay_prog = ctx.program(
                vertex_shader="""
                    #version 330
                    in vec2 in_pos;
                    in vec2 in_uv;
                    out vec2 v_uv;
                    void main() {
                        v_uv = in_uv;
                        gl_Position = vec4(in_pos, 0.0, 1.0);
                    }
                """,
                fragment_shader="""
                    #version 330
                    uniform sampler2D overlay_tex;
                    in vec2 v_uv;
                    out vec4 out_color;
                    void main() {
                        out_color = texture(overlay_tex, v_uv);
                    }
                """,
            )
            screen_quad = np.array(
                [
                    -1.0,
                    -1.0,
                    0.0,
                    0.0,
                    1.0,
                    -1.0,
                    1.0,
                    0.0,
                    -1.0,
                    1.0,
                    0.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                ],
                dtype=np.float32,
            )
            screen_vbo = ctx.buffer(screen_quad.tobytes())
            screen_vao = ctx.vertex_array(screen_prog, [(screen_vbo, "2f 2f", "in_pos", "in_uv")])
            overlay_vbo = ctx.buffer(reserve=4 * 4 * 4)
            overlay_vao = ctx.vertex_array(overlay_prog, [(overlay_vbo, "2f 2f", "in_pos", "in_uv")])
        gpu_state = {
            "ctx": ctx,
            "moderngl": moderngl,
            "field_tex": field_tex,
            "fbo": fbo,
            "vbo": vbo,
            "inst_buffer": inst_buffer,
            "ring_prog": ring_prog,
            "vao": vao,
            "screen_prog": screen_prog,
            "screen_vao": screen_vao,
            "overlay_prog": overlay_prog,
            "overlay_vbo": overlay_vbo,
            "overlay_vao": overlay_vao,
            "overlay_textures": {},
            "display": display,
            "field_scale": 1.0,
        }
        return True

    if gpu_display and not init_gpu_renderer(display=True):
        gpu_display = False
        display_flags = pygame.RESIZABLE
        screen = pygame.display.set_mode((width, height), display_flags)
        pygame.display.set_caption("Orbit Visualizer (prototype)")

    def gpu_rebuild_field_surface(current_time: float) -> None:
        nonlocal field_surface
        if not init_gpu_renderer(display=False):
            rebuild_field_surface(current_time, update_last_radius=field_alg == "cpu_incremental")
            return
        inst_entries = []
        for em in emissions:
            tau = current_time - em.time
            if tau <= 0:
                continue
            radius = field_v * tau
            if radius > max_radius:
                continue
            sign = 1.0 if em.emitter == "positrino" else -1.0
            inst_entries.append((em.pos[0], em.pos[1], radius, sign))
        if not inst_entries:
            field_grid[:] = 0.0
            field_surface = make_field_surface()
            return
        inst_arr = np.array(inst_entries, dtype=np.float32)
        gpu_state["inst_buffer"].orphan(inst_arr.nbytes)
        gpu_state["inst_buffer"].write(inst_arr.tobytes())
        band_half = max(shell_thickness * 1.5, shell_thickness)
        ring_prog = gpu_state["ring_prog"]
        ring_prog["domain_half_extent"].value = cfg.domain_half_extent
        ring_prog["band_half"].value = band_half
        ring_prog["use_hard"].value = 1 if shell_weight == "hard" else 0
        ctx = gpu_state["ctx"]
        ctx.enable(gpu_state["moderngl"].BLEND)
        ctx.blend_func = (gpu_state["moderngl"].ONE, gpu_state["moderngl"].ONE)
        fbo = gpu_state["fbo"]
        fbo.use()
        fbo.clear(0.0, 0.0, 0.0, 0.0)
        gpu_state["vao"].render(
            mode=gpu_state["moderngl"].TRIANGLE_STRIP,
            instances=inst_arr.shape[0],
        )
        raw = gpu_state["field_tex"].read(alignment=1)
        arr = np.frombuffer(raw, dtype=np.float32).reshape((res_y, res_x))
        field_grid[:] = np.flipud(arr)
        field_surface = make_field_surface()

    def gpu_update_field_texture(current_time: float) -> None:
        if not init_gpu_renderer(display=True):
            return
        inst_entries = []
        r_min = None
        for em in emissions:
            tau = current_time - em.time
            if tau <= 0:
                continue
            radius = field_v * tau
            if radius > max_radius:
                continue
            sign = 1.0 if em.emitter == "positrino" else -1.0
            inst_entries.append((em.pos[0], em.pos[1], radius, sign))
            if r_min is None or radius < r_min:
                r_min = radius
        ctx = gpu_state["ctx"]
        ctx.enable(gpu_state["moderngl"].BLEND)
        ctx.blend_func = (gpu_state["moderngl"].ONE, gpu_state["moderngl"].ONE)
        fbo = gpu_state["fbo"]
        fbo.use()
        fbo.clear(0.0, 0.0, 0.0, 0.0)
        if inst_entries:
            inst_arr = np.array(inst_entries, dtype=np.float32)
            gpu_state["inst_buffer"].orphan(inst_arr.nbytes)
            gpu_state["inst_buffer"].write(inst_arr.tobytes())
            band_half = max(shell_thickness * 1.5, shell_thickness)
            ring_prog = gpu_state["ring_prog"]
            ring_prog["domain_half_extent"].value = cfg.domain_half_extent
            ring_prog["band_half"].value = band_half
            ring_prog["use_hard"].value = 1 if shell_weight == "hard" else 0
            gpu_state["vao"].render(
                mode=gpu_state["moderngl"].TRIANGLE_STRIP,
                instances=inst_arr.shape[0],
            )
        if r_min is None or r_min <= 0:
            gpu_state["field_scale"] = 1.0
        else:
            gpu_state["field_scale"] = max(1.0, 1.0 / (r_min * r_min))

    def gpu_present_field() -> None:
        if not gpu_state or not gpu_state["display"] or gpu_state["screen_prog"] is None:
            return
        ctx = gpu_state["ctx"]
        ctx.screen.use()
        ctx.disable(gpu_state["moderngl"].BLEND)
        screen_prog = gpu_state["screen_prog"]
        screen_prog["field_scale"].value = gpu_state["field_scale"]
        screen_prog["falloff_mode"].value = 1 if cfg.field_color_falloff == "inverse_r" else 0
        gpu_state["field_tex"].use(0)
        screen_prog["field_tex"].value = 0
        gpu_state["screen_vao"].render(mode=gpu_state["moderngl"].TRIANGLE_STRIP)

    def gpu_draw_surface(surface: "pygame.Surface", x: int, y: int, key: str) -> None:
        if not gpu_state or not gpu_state["display"]:
            return
        ctx = gpu_state["ctx"]
        # Use the actual framebuffer size (after DPI / resize) and scale uniformly to preserve aspect.
        # Use the current viewport (which may be smaller than the full framebuffer after scaling).
        view_x, view_y, view_w, view_h = ctx.viewport
        if view_w <= 0 or view_h <= 0:
            return
        scale = min(view_w / width, view_h / height)
        tex = gpu_state["overlay_textures"].get(key)
        size = surface.get_size()
        if tex is None or tex.size != size:
            if tex is not None:
                tex.release()
            tex = ctx.texture(size, components=4)
            tex.filter = (gpu_state["moderngl"].LINEAR, gpu_state["moderngl"].LINEAR)
            gpu_state["overlay_textures"][key] = tex
        data = pygame.image.tostring(surface, "RGBA", True)
        tex.write(data)
        x0 = ((x * scale) / view_w) * 2.0 - 1.0
        x1 = (((x + size[0]) * scale) / view_w) * 2.0 - 1.0
        y0 = 1.0 - ((y * scale) / view_h) * 2.0
        y1 = 1.0 - (((y + size[1]) * scale) / view_h) * 2.0
        verts = np.array(
            [
                x0,
                y1,
                0.0,
                0.0,
                x1,
                y1,
                1.0,
                0.0,
                x0,
                y0,
                0.0,
                1.0,
                x1,
                y0,
                1.0,
                1.0,
            ],
            dtype=np.float32,
        )
        gpu_state["overlay_vbo"].write(verts.tobytes())
        ctx.enable(gpu_state["moderngl"].BLEND)
        ctx.blend_func = (gpu_state["moderngl"].SRC_ALPHA, gpu_state["moderngl"].ONE_MINUS_SRC_ALPHA)
        tex.use(0)
        gpu_state["overlay_prog"]["overlay_tex"].value = 0
        gpu_state["overlay_vao"].render(mode=gpu_state["moderngl"].TRIANGLE_STRIP)

    def add_trace_segment(start_offset: float, end_offset: float, steps: int = 180) -> None:
        nonlocal path_traces
        if end_offset == start_offset:
            return
        for name, emitter in emitter_lookup.items():
            segment = []
            for j in range(steps + 1):
                alpha = j / steps
                s = start_offset + alpha * (end_offset - start_offset)
                segment.append(position_at(emitter, s))
            path_traces[name].extend(segment)
            if len(path_traces[name]) > trace_limit:
                path_traces[name] = path_traces[name][-trace_limit:]

    def rebuild_trace_for_offset(offset: float) -> None:
        nonlocal path_traces
        offset = max(offset, BASE_OFFSET)
        steps = max(2, int(abs(offset) / (2 * math.pi) * 360))
        path_traces = {"positrino": [], "electrino": []}
        for name, emitter in emitter_lookup.items():
            trace: List[Vec2] = []
            for j in range(steps + 1):
                alpha = j / steps
                s = alpha * offset
                trace.append(position_at(emitter, s))
            if len(trace) > trace_limit:
                trace = trace[-trace_limit:]
            path_traces[name] = trace

    def refresh_hits_for_current_time() -> None:
        """Recompute hits for the current frame time using emission history."""
        nonlocal recent_hits, seen_hits, seen_hits_queue, last_diff, last_diff_queue, positions
        current_time = frame_idx * dt
        positions = current_positions(current_time)
        recent_hits.clear()
        seen_hits.clear()
        seen_hits_queue.clear()
        last_diff.clear()
        last_diff_queue.clear()
        recent_hits.extend(detect_hits(current_time, positions, allow_self=speed_mult > field_v))

    def reset_state(
        apply_pending_speed: bool = True,
        keep_trace: bool = False,
        keep_offset: bool = False,
        keep_field_visible: bool = False,
    ) -> None:
        nonlocal emissions, field_grid, frame_idx, speed_mult, field_surface, positions, field_visible, path_traces, pending_speed_mult, path_time_offset, sim_clock_start, sim_clock_elapsed
        if apply_pending_speed:
            speed_mult = clamp_speed(pending_speed_mult)
        else:
            speed_mult = clamp_speed(cfg.speed_multiplier)
            pending_speed_mult = speed_mult
        if not keep_offset:
            path_time_offset = BASE_OFFSET
        emissions = []
        field_grid[:] = 0.0
        field_surface = None
        field_visible = field_visible if keep_field_visible else cfg.field_visible
        frame_idx = 0
        recent_hits.clear()
        seen_hits.clear()
        seen_hits_queue.clear()
        last_diff.clear()
        last_diff_queue.clear()
        positions = current_positions(0.0)
        if not keep_trace:
            rebuild_trace_for_offset(path_time_offset)
        recent_hits.clear()
        sim_clock_start = time.monotonic()
        sim_clock_elapsed = 0.0
        if field_visible:
            if field_alg == "gpu_instanced":
                if gpu_display:
                    gpu_update_field_texture(0.0)
                else:
                    gpu_rebuild_field_surface(0.0)
            else:
                rebuild_field_surface(0.0, update_last_radius=field_alg == "cpu_incremental")

    def render_frame_gl(positions: Dict[str, Vec2], hits: List[Hit], field_surf=None) -> None:
        nonlocal gpu_display
        if not init_gpu_renderer(display=True):
            gpu_display = False
            render_frame(positions, hits, field_surf)
            return
        ctx = gpu_state["ctx"]
        ctx.screen.use()
        view_w, view_h = ctx.screen.viewport[2:]
        if view_w <= 0 or view_h <= 0:
            return
        scale = min(view_w / width, view_h / height)
        content_w = int(width * scale)
        content_h = int(height * scale)
        ctx.viewport = (0, 0, content_w, content_h)
        ctx.clear(1.0, 1.0, 1.0, 1.0)
        if field_visible:
            if field_alg == "gpu_instanced":
                panel_px = int(panel_w * scale)
                canvas_px = max(1, int(canvas_w * scale))
                ctx.viewport = (panel_px, 0, canvas_px, canvas_px)
                gpu_present_field()
                ctx.viewport = (0, 0, content_w, content_h)
            elif field_surface is not None:
                gpu_draw_surface(field_surface, panel_w, 0, "field_rgb")

        overlay_visible = (paused and ui_overlay_visible) or show_hit_overlays
        panel_visible = paused and ui_overlay_visible
        if overlay_visible:
            geometry_layer = pygame.Surface((canvas_w, height), pygame.SRCALPHA).convert_alpha()
            if ui_overlay_visible and current_path_name == "unit_circle":
                center = world_to_canvas((0.0, 0.0))
                scale = min(canvas_w, height) / (2 * cfg.domain_half_extent)
                for r in (int(scale), int(scale) + 1):
                    gfxdraw.aacircle(geometry_layer, int(center[0]), int(center[1]), r, PURE_WHITE)

            if ui_overlay_visible:
                for name, trace in path_traces.items():
                    if len(trace) < 2:
                        continue
                    color = PURE_WHITE
                    prev = world_to_canvas(trace[0])
                    for pt in trace[1:]:
                        cur = world_to_canvas(pt)
                        pygame.draw.aaline(geometry_layer, color, (int(prev[0]), int(prev[1])), (int(cur[0]), int(cur[1])))
                        prev = cur

            def draw_hit_arc(hit: Hit) -> None:
                recv_pos = positions.get(hit.receiver)
                if recv_pos is None:
                    return
                cx, cy = world_to_canvas(hit.emit_pos)
                tx, ty = world_to_canvas(recv_pos)
                dx = tx - cx
                dy = ty - cy
                radius_px = int(math.hypot(dx, dy))
                if radius_px < 2:
                    return
                ang = (math.degrees(math.atan2(dy, dx)) + 360.0) % 360.0
                arc_half = 5.0
                start = (ang - arc_half) % 360
                end = (ang + arc_half) % 360
                color = PURE_RED if hit.emitter == "positrino" else PURE_BLUE

                def draw_arc_span(s: float, e: float) -> None:
                    for r_off in (0, 1):
                        gfxdraw.arc(
                            geometry_layer,
                            int(cx),
                            int(cy),
                            radius_px + r_off,
                            int(s),
                            int(e),
                            color,
                        )

                if start <= end:
                    draw_arc_span(start, end)
                else:
                    draw_arc_span(start, 360)
                    draw_arc_span(0, end)

            if show_hit_overlays:
                for h in hits:
                    draw_hit_arc(h)
                for h in hits:
                    start = world_to_canvas(h.emit_pos)
                    end = world_to_canvas(positions[h.receiver])
                    line_color = PURE_RED if h.emitter == "positrino" else PURE_BLUE
                    gfxdraw.line(geometry_layer, int(start[0]), int(start[1]), int(end[0]), int(end[1]), line_color)
                    gfxdraw.line(geometry_layer, int(start[0]), int(start[1] + 1), int(end[0]), int(end[1] + 1), line_color)

            particle_layer = pygame.Surface((canvas_w, height), pygame.SRCALPHA).convert_alpha()
            if show_hit_overlays:
                for h in hits:
                    start = world_to_canvas(h.emit_pos)
                    marker_color = LIGHT_RED if h.emitter == "positrino" else LIGHT_BLUE
                    gfxdraw.filled_circle(particle_layer, int(start[0]), int(start[1]), 4, marker_color)
                    gfxdraw.aacircle(particle_layer, int(start[0]), int(start[1]), 5, PURE_WHITE)

            if ui_overlay_visible:
                pos_posi_canvas = world_to_canvas(positions["positrino"])
                pos_elec_canvas = world_to_canvas(positions["electrino"])
                gfxdraw.filled_circle(particle_layer, int(pos_posi_canvas[0]), int(pos_posi_canvas[1]), 6, PURE_RED)
                gfxdraw.aacircle(particle_layer, int(pos_posi_canvas[0]), int(pos_posi_canvas[1]), 7, PURE_WHITE)
                gfxdraw.filled_circle(particle_layer, int(pos_elec_canvas[0]), int(pos_elec_canvas[1]), 6, PURE_BLUE)
                gfxdraw.aacircle(particle_layer, int(pos_elec_canvas[0]), int(pos_elec_canvas[1]), 7, PURE_WHITE)

            gpu_draw_surface(geometry_layer, panel_w, 0, "overlay_geom")
            gpu_draw_surface(particle_layer, panel_w, 0, "overlay_particles")

        if panel_visible:
            ui_layer = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
            pygame.draw.rect(ui_layer, (245, 245, 245), (0, 0, panel_w, height))
            def panel_draw(text: str, x: int, y: int, color=(0, 0, 0)) -> None:
                draw_text(ui_layer, text, x, y, color=color)

            panel_draw(f"hz={cfg.hz}", 10, 10)
            panel_draw(f"frame_skip={frame_skip}", 10, 30)
            if paused and pending_speed_mult != speed_mult:
                panel_draw(f"speed_mult={speed_mult:.2f} -> {pending_speed_mult:.2f}", 10, 50)
            else:
                panel_draw(f"speed_mult={speed_mult:.2f}", 10, 50)
            panel_draw(f"path={current_path_name}", 10, 70)
            alg_state = field_alg
            panel_draw(f"alg={alg_state}", 10, 90)
            panel_draw("Controls:", 10, 110)
            panel_draw("ESC reset", 10, 130)
            panel_draw("SPACE pause/resume", 10, 150)
            panel_draw("LEFT/RIGHT skip", 10, 170)
            panel_draw("H: hits (paused)", 10, 190)
            panel_draw("UP/DOWN speed", 10, 210)
            panel_draw("F: hz 250/500/1000", 10, 230)
            panel_draw("V: field on/off", 10, 250)
            panel_draw(f"B: field alg ({alg_state})", 10, 270)
            panel_draw("U: ui/overlays", 10, 290)
            if paused:
                panel_draw("PAUSED", 10, height - 30)
            gpu_draw_surface(ui_layer, 0, 0, "ui_panel")

        pygame.display.flip()

    def render_frame(positions: Dict[str, Vec2], hits: List[Hit], field_surf=None) -> None:
        nonlocal panel_log
        if gpu_display:
            render_frame_gl(positions, hits, field_surf)
            return
        screen.fill(PURE_WHITE)
        fs = field_surf if field_surf is not None else (field_surface if field_visible else None)
        if fs is not None:
            screen.blit(fs, (panel_w, 0))

        overlay_visible = (paused and ui_overlay_visible) or show_hit_overlays
        panel_visible = paused and ui_overlay_visible
        if overlay_visible:
            geometry_layer = pygame.Surface((canvas_w, height), pygame.SRCALPHA).convert_alpha()
            if ui_overlay_visible and current_path_name == "unit_circle":
                center = world_to_canvas((0.0, 0.0))
                scale = min(canvas_w, height) / (2 * cfg.domain_half_extent)
                for r in (int(scale), int(scale) + 1):
                    gfxdraw.aacircle(geometry_layer, int(center[0]), int(center[1]), r, PURE_WHITE)

            # Draw path traces.
            if ui_overlay_visible:
                for name, trace in path_traces.items():
                    if len(trace) < 2:
                        continue
                    color = PURE_WHITE
                    prev = world_to_canvas(trace[0])
                    for pt in trace[1:]:
                        cur = world_to_canvas(pt)
                        pygame.draw.aaline(geometry_layer, color, (int(prev[0]), int(prev[1])), (int(cur[0]), int(cur[1])))
                        prev = cur

            # Draw a small arc on each incoming shell to indicate the arriving wavefront segment.
            def draw_hit_arc(hit: Hit) -> None:
                recv_pos = positions.get(hit.receiver)
                if recv_pos is None:
                    return
                cx, cy = world_to_canvas(hit.emit_pos)
                tx, ty = world_to_canvas(recv_pos)
                dx = tx - cx
                dy = ty - cy
                radius_px = int(math.hypot(dx, dy))
                if radius_px < 2:
                    return
                # Use screen-space angle directly (y down in screen coords).
                ang = (math.degrees(math.atan2(dy, dx)) + 360.0) % 360.0
                arc_half = 5.0
                start = (ang - arc_half) % 360
                end = (ang + arc_half) % 360
                color = PURE_RED if hit.emitter == "positrino" else PURE_BLUE

                def draw_arc_span(s: float, e: float) -> None:
                    # Thicker arc via small radial offsets
                    for r_off in (0, 1):
                        gfxdraw.arc(
                            geometry_layer,
                            int(cx),
                            int(cy),
                            radius_px + r_off,
                            int(s),
                            int(e),
                            color,
                        )

                if start <= end:
                    draw_arc_span(start, end)
                else:
                    # Wrap-around case: split into two arcs.
                    draw_arc_span(start, 360)
                    draw_arc_span(0, end)

            if show_hit_overlays:
                for h in hits:
                    draw_hit_arc(h)

                for h in hits:
                    start = world_to_canvas(h.emit_pos)
                    end = world_to_canvas(positions[h.receiver])
                    line_color = PURE_RED if h.emitter == "positrino" else PURE_BLUE
                    # Thicker line by drawing twice with slight offsets
                    gfxdraw.line(geometry_layer, int(start[0]), int(start[1]), int(end[0]), int(end[1]), line_color)
                    gfxdraw.line(geometry_layer, int(start[0]), int(start[1] + 1), int(end[0]), int(end[1] + 1), line_color)

            particle_layer = pygame.Surface((canvas_w, height), pygame.SRCALPHA).convert_alpha()
            if show_hit_overlays:
                for h in hits:
                    start = world_to_canvas(h.emit_pos)
                    marker_color = LIGHT_RED if h.emitter == "positrino" else LIGHT_BLUE
                    gfxdraw.filled_circle(particle_layer, int(start[0]), int(start[1]), 4, marker_color)
                    gfxdraw.aacircle(particle_layer, int(start[0]), int(start[1]), 5, PURE_WHITE)

            if ui_overlay_visible:
                pos_posi_canvas = world_to_canvas(positions["positrino"])
                pos_elec_canvas = world_to_canvas(positions["electrino"])
                gfxdraw.filled_circle(particle_layer, int(pos_posi_canvas[0]), int(pos_posi_canvas[1]), 6, PURE_RED)
                gfxdraw.aacircle(particle_layer, int(pos_posi_canvas[0]), int(pos_posi_canvas[1]), 7, PURE_WHITE)
                gfxdraw.filled_circle(particle_layer, int(pos_elec_canvas[0]), int(pos_elec_canvas[1]), 6, PURE_BLUE)
                gfxdraw.aacircle(particle_layer, int(pos_elec_canvas[0]), int(pos_elec_canvas[1]), 7, PURE_WHITE)

            screen.blit(geometry_layer, (panel_w, 0))
            screen.blit(particle_layer, (panel_w, 0))

        if panel_visible:
            ui_layer = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
            pygame.draw.rect(ui_layer, (245, 245, 245), (0, 0, panel_w, height))
            def panel_draw(text: str, x: int, y: int, color=(0, 0, 0)) -> None:
                draw_text(ui_layer, text, x, y, color=color)

            panel_draw(f"hz={cfg.hz}", 10, 10)
            panel_draw(f"frame_skip={frame_skip}", 10, 30)
            if paused and pending_speed_mult != speed_mult:
                panel_draw(f"speed_mult={speed_mult:.2f} -> {pending_speed_mult:.2f}", 10, 50)
            else:
                panel_draw(f"speed_mult={speed_mult:.2f}", 10, 50)
            panel_draw(f"path={current_path_name}", 10, 70)
            panel_draw(f"sim={sim_clock_elapsed:.1f}s", 10, 90)
            alg_state = field_alg
            panel_draw(f"alg={alg_state}", 10, 110)
            panel_draw("Controls:", 10, 130)
            panel_draw("ESC reset", 10, 150)
            panel_draw("SPACE pause/resume", 10, 170)
            panel_draw("LEFT/RIGHT skip", 10, 190)
            panel_draw("H: hits (paused)", 10, 210)
            panel_draw("UP/DOWN speed", 10, 230)
            panel_draw("F: hz 250/500/1000", 10, 250)
            panel_draw("V: field on/off", 10, 270)
            panel_draw(f"B: field alg ({alg_state})", 10, 290)
            panel_draw("U: ui/overlays", 10, 310)
            if paused:
                panel_draw("PAUSED", 10, height - 30)

            screen.blit(ui_layer, (0, 0))
        pygame.display.flip()

    def current_positions(time_t: float) -> Dict[str, Vec2]:
        path_t = speed_mult * time_t
        param = path_time_offset + path_t
        return {
            "positrino": position_at(positrino, param),
            "electrino": position_at(electrino, param),
        }

    def prune_emissions(current_time: float) -> None:
        nonlocal emissions
        cutoff = current_time - emission_retention
        if cutoff <= 0:
            return
        if field_alg != "cpu_incremental":
            emissions = [em for em in emissions if em.time >= cutoff]
            return
        kept: List[Emission] = []
        for em in emissions:
            if em.time < cutoff:
                if em.last_radius > 0:
                    apply_shell(em, em.last_radius, weight_scale=-1.0)
                continue
            kept.append(em)
        emissions = kept

    reset_state(apply_pending_speed=False)
    render_frame(positions, list(recent_hits))

    pygame.key.set_repeat(200, 50)

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        hit_overlay_enabled = False
                        show_hit_overlays = False
                        reset_state(apply_pending_speed=True, keep_field_visible=True)
                        paused = True
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                        if not paused:
                            hit_overlay_enabled = False
                            show_hit_overlays = False
                            sim_clock_start = time.monotonic()
                        else:
                            sim_clock_elapsed += time.monotonic() - sim_clock_start
                    elif event.key == pygame.K_h:
                        if paused:
                            hit_overlay_enabled = not hit_overlay_enabled
                    elif event.key == pygame.K_RIGHT:
                        frame_skip += 1
                    elif event.key == pygame.K_LEFT:
                        frame_skip = max(0, frame_skip - 1)
                    elif event.key == pygame.K_UP:
                        apply_speed_change(speed_mult + 0.1, auto_pause=True)
                    elif event.key == pygame.K_DOWN:
                        apply_speed_change(speed_mult - 0.1, auto_pause=True)
                    elif event.key == pygame.K_f:
                        if cfg.hz == 250:
                            new_hz = 500
                        elif cfg.hz == 500:
                            new_hz = 1000
                        else:
                            new_hz = 250
                        update_time_params(new_hz)
                        reset_state(apply_pending_speed=True, keep_field_visible=True)
                        paused = True
                    elif event.key == pygame.K_b:
                        algs = ["cpu_incremental", "cpu_rebuild", "gpu_instanced"]
                        try:
                            idx = algs.index(field_alg)
                        except ValueError:
                            idx = 0
                        field_alg = algs[(idx + 1) % len(algs)]
                        if field_alg == "gpu_instanced":
                            if not init_gpu_renderer(display=gpu_display):
                                field_alg = "cpu_incremental"
                        if field_alg == "gpu_instanced":
                            if gpu_display:
                                gpu_update_field_texture(frame_idx * dt)
                            else:
                                gpu_rebuild_field_surface(frame_idx * dt)
                        else:
                            rebuild_field_surface(
                                frame_idx * dt,
                                update_last_radius=field_alg == "cpu_incremental",
                            )
                    elif event.key == pygame.K_t:
                        trace_test_frames_remaining = 3000
                        paused = False
                        hit_overlay_enabled = False
                        show_hit_overlays = False
                        sim_clock_start = time.monotonic()
                    elif event.key == pygame.K_u:
                        ui_overlay_visible = not ui_overlay_visible
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_v:
                        if field_visible:
                            field_visible = False
                        else:
                            field_visible = True
                            if field_alg == "gpu_instanced":
                                if gpu_display:
                                    gpu_update_field_texture(frame_idx * dt)
                                else:
                                    gpu_rebuild_field_surface(frame_idx * dt)
                            else:
                                rebuild_field_surface(
                                    frame_idx * dt,
                                    update_last_radius=field_alg == "cpu_incremental",
                                )

            show_hit_overlays = paused and hit_overlay_enabled
            if not paused:
                sim_clock_elapsed += time.monotonic() - sim_clock_start
                sim_clock_start = time.monotonic()
            if paused:
                # Refresh hits once when paused with overlay requested.
                if hit_overlay_enabled and not recent_hits:
                    refresh_hits_for_current_time()
                pygame.display.set_caption(f"Orbit Visualizer (frame={frame_idx+1} sim={sim_clock_elapsed:.2f}s)")
                render_frame(positions, list(recent_hits))
                clock.tick(cfg.hz)
                continue
            show_hit_overlays = False

            steps = frame_skip + 1
            display_hits: List[Hit] = []
            sim_idx = frame_idx
            current_time = sim_idx * dt
            for step in range(steps):
                current_time = sim_idx * dt
                positions = current_positions(current_time)
                for name, pos in positions.items():
                    path_traces[name].append(pos)
                    if len(path_traces[name]) > trace_limit:
                        path_traces[name] = path_traces[name][-trace_limit:]

                emissions.append(Emission(time=current_time, pos=positions["positrino"], emitter="positrino"))
                emissions.append(Emission(time=current_time, pos=positions["electrino"], emitter="electrino"))

                prune_emissions(current_time)
                allow_self = speed_mult > field_v + 1e-6
                hits: List[Hit] = []
                # Skip hit detection unless we need to show it (paused hit overlay or overlay enabled).
                if paused or hit_overlay_enabled or show_hit_overlays:
                    hits = detect_hits(current_time, positions, allow_self=allow_self)
                if step == steps - 1:
                    display_hits = hits
                    recent_hits.clear()
                    if display_hits:
                        recent_hits.extend(display_hits)

                sim_idx += 1

            frame_idx = sim_idx - 1
            if field_alg == "cpu_incremental":
                update_field_surface(current_time)
            elif field_alg == "gpu_instanced":
                if field_visible:
                    if gpu_display:
                        gpu_update_field_texture(current_time)
                    else:
                        gpu_rebuild_field_surface(current_time)
            else:
                rebuild_field_surface(current_time)
            render_frame(positions, display_hits)

            # Throttled window title updates during simulation.
            if not paused and (frame_idx - last_caption_update) >= 100:
                pygame.display.set_caption(f"Orbit Visualizer (frame={frame_idx+1} sim={current_time:.2f}s)")
                last_caption_update = frame_idx

            clock.tick(0)

            frame_idx = sim_idx
            if trace_test_frames_remaining is not None:
                trace_test_frames_remaining -= steps
                if trace_test_frames_remaining <= 0:
                    running = False
                    continue
    except KeyboardInterrupt:
        running = False

    pygame.quit()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Orbit visualizer prototype (live).")
    parser.add_argument("--run", type=str, required=True, help="JSON run file with directives and architrino groups.")
    parser.add_argument("--render", action="store_true", help="Open a PyGame window and render the live simulation.")
    return parser.parse_args()


def main() -> None:
    try:
        args = parse_args()
        scenario = load_run_file(args.run, PATH_LIBRARY)
        orbit = scenario.primary_orbit()
        render = scenario.render or args.render
        if not render:
            raise SystemExit("Render disabled. Set directives.render or pass --render.")
        render_live(scenario.config, scenario.paths, path_name=orbit.path)
    except KeyboardInterrupt:
        # Graceful exit on Ctrl-C without traceback.
        try:
            import pygame

            pygame.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
