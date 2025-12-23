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

Run files expect top-level "directives" and an "architrinos" array; see orbit-visualizer/circle.json.

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
import subprocess
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import numpy as np

from motion import (
    AnalyticMover,
    ArchitrinoState,
    Emission,
    MoverEnv,
    PathSpec,
    PhysicsMover,
    Vec2,
    default_phase_and_offset,
    PATH_LIBRARY,
)


# Color constants (RGB)
PURE_RED = (255, 0, 0)
PURE_BLUE = (0, 0, 255)
PURE_PURPLE = (255, 0, 255)  # neutral (red + blue)
PURE_WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
LIGHT_RED = (255, 160, 160)
LIGHT_BLUE = (160, 200, 255)


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
    field_alg: str = "gpu"  # "cpu_full", "cpu_incr", or "gpu"
    duration_seconds: float | None = None


@dataclass
class UIConfig:
    field_visible: bool = True
    architrinos_visible: bool = True
    path_trail_visible: bool = False
    path_trail_markers_visible: bool = False


@dataclass
class OrbitConfig:
    path: str
    speed_multiplier: float | None = None
    decay: float | None = None


@dataclass
class ArchitrinoSpec:
    name: str
    polarity: str  # "p" or "e"
    path: str
    start_pos: Vec2
    velocity_speed: float
    velocity_heading_deg: float
    decay: float | None = None
    mover: str | None = None


@dataclass
class RunScenario:
    config: SimulationConfig
    architrinos: List[ArchitrinoSpec]
    paths: Dict[str, PathSpec]
    render: bool = False
    ui: UIConfig | None = None

    def primary_path(self) -> str:
        if not self.architrinos:
            raise ValueError("Scenario has no architrinos configured.")
        return self.architrinos[0].path


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

    ui_raw = directives.get("ui", {}) or {}
    ui_raw = _expect_dict(ui_raw, "directives.ui")
    ui_cfg = UIConfig(
        field_visible=bool(ui_raw.get("field_visible", True)),
        architrinos_visible=bool(ui_raw.get("architrinos_visible", True)),
        path_trail_visible=bool(ui_raw.get("path_trail_visible", False)),
        path_trail_markers_visible=bool(ui_raw.get("path_trail_markers_visible", False)),
    )

    arch_list = _expect_list(payload.get("architrinos"), "architrinos")
    if not arch_list:
        raise ValueError("Run file requires an 'architrinos' array with at least one entry.")

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

    field_visible = bool(ui_cfg.field_visible)
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
    field_alg = directives.get("field_alg", "gpu")
    if not isinstance(field_alg, str):
        raise ValueError("directives.field_alg must be a string.")
    field_alg = field_alg.lower()
    legacy_map = {
        "gpu_instanced": "gpu",
        "cpu_incremental": "cpu_incr",
        "cpu_rebuild": "cpu_full",
    }
    field_alg = legacy_map.get(field_alg, field_alg)
    if field_alg not in {"cpu_full", "cpu_incr", "gpu"}:
        raise ValueError("directives.field_alg must be 'cpu_full', 'cpu_incr', or 'gpu'.")

    cfg = SimulationConfig(
        hz=_coerce_int(directives.get("hz", 1000), "directives.hz"),
        field_speed=_coerce_float(directives.get("field_speed", 1.0), "directives.field_speed"),
        domain_half_extent=_coerce_float(directives.get("domain_half_extent", 2.0), "directives.domain_half_extent"),
        speed_multiplier=_coerce_float(directives.get("speed_multiplier", 0.5), "directives.speed_multiplier"),
        position_snap=position_snap,
        path_snap=path_snap,
        field_visible=field_visible,
        start_paused=start_paused,
        field_grid_scale_with_canvas=field_grid_scale_with_canvas,
        shell_thickness_scale_with_canvas=shell_thickness_scale_with_canvas,
        field_color_falloff=field_color_falloff,
        shell_weight=shell_weight,
        field_alg=field_alg,
        duration_seconds=_coerce_float(directives["duration_seconds"], "directives.duration_seconds") if "duration_seconds" in directives else None,
    )

    paths_override = dict(paths)
    arch_specs: List[ArchitrinoSpec] = []
    for idx, entry in enumerate(arch_list):
        arch = _expect_dict(entry, f"architrinos[{idx}]")
        name = arch.get("name") or f"arch-{idx+1}"
        if not isinstance(name, str):
            raise ValueError(f"architrinos[{idx}].name must be a string.")
        polarity = arch.get("type") or arch.get("polarity")
        if polarity not in {"p", "e"}:
            raise ValueError(f"architrinos[{idx}] polarity/type must be 'p' or 'e'.")
        path_name = arch.get("path")
        if not isinstance(path_name, str):
            raise ValueError(f"architrinos[{idx}].path must be a string.")
        if path_name not in paths_override:
            raise ValueError(f"Unknown path '{path_name}' for architrinos[{idx}]. Available: {list(paths_override.keys())}")
        decay_override = arch.get("decay")
        if decay_override is not None:
            if path_name != "exp_inward_spiral":
                raise ValueError("decay override is only supported for exp_inward_spiral.")
            decay_val = _coerce_float(decay_override, f"architrinos[{idx}].decay")
            base = paths_override[path_name]
            paths_override = dict(paths_override)
            paths_override[path_name] = PathSpec(
                name=base.name,
                sampler=base.sampler,
                description=base.description,
                decay=decay_val,
            )
        start_pos_raw = arch.get("start_pos") or arch.get("start")
        if start_pos_raw is None:
            raise ValueError(f"architrinos[{idx}] requires start_pos.")
        start_pos_dict = _expect_dict(start_pos_raw, f"architrinos[{idx}].start_pos")
        if "x" not in start_pos_dict or "y" not in start_pos_dict:
            raise ValueError(f"architrinos[{idx}].start_pos requires x and y.")
        start_pos = (_coerce_float(start_pos_dict["x"], f"architrinos[{idx}].start_pos.x"),
                     _coerce_float(start_pos_dict["y"], f"architrinos[{idx}].start_pos.y"))
        vel_raw = arch.get("velocity") or {}
        vel_raw = _expect_dict(vel_raw, f"architrinos[{idx}].velocity")
        speed = _coerce_float(vel_raw.get("speed", cfg.speed_multiplier), f"architrinos[{idx}].velocity.speed")
        heading_deg = _coerce_float(vel_raw.get("heading_deg", 0.0), f"architrinos[{idx}].velocity.heading_deg")
        mover_type = arch.get("mover", "analytic")
        if mover_type not in {"analytic", "physics"}:
            raise ValueError(f"architrinos[{idx}].mover must be 'analytic' or 'physics'.")
        arch_specs.append(
            ArchitrinoSpec(
                name=name,
                polarity=polarity,
                path=path_name,
                start_pos=start_pos,
                velocity_speed=speed,
                velocity_heading_deg=heading_deg,
                decay=decay_override if decay_override is not None else None,
                mover=mover_type,
            )
        )

    render = bool(directives.get("render", False))
    return RunScenario(
        config=cfg,
        architrinos=arch_specs,
        paths=paths_override,
        render=render,
        ui=ui_cfg,
    )


def render_live(cfg: SimulationConfig, paths: Dict[str, PathSpec], arch_specs: List[ArchitrinoSpec], ui: UIConfig | None, path_name: str = "unit_circle", run_label: str = "", offline: bool = False, offline_output: str = "output.mp4", offline_fps: int = 60, duration_seconds: float | None = None) -> None:
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

    if not arch_specs:
        raise ValueError("No architrinos defined.")

    if offline:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    panel_w = 0
    canvas_scale = 1.0
    if canvas_scale <= 0:
        raise ValueError("canvas_scale must be > 0.")
    info = pygame.display.Info()
    field_alg = cfg.field_alg
    gpu_display = False
    if offline and field_alg == "gpu":
        field_alg = "cpu_full"
    if field_alg == "gpu" and not offline:
        try:
            import moderngl  # noqa: F401
            gpu_display = True
        except ImportError:
            field_alg = "cpu_incr"
    display_flags = pygame.RESIZABLE
    if gpu_display:
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        display_flags |= pygame.OPENGL | pygame.DOUBLEBUF
    if offline:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        display_flags = 0
    # Frame controls and canvas sizing
    flip_stride = 8  # flip every N frames when running
    trace_draw_stride = 8  # redraw traces every N frames while running
    canvas_w = 0
    width = 0
    height = 0
    screen: "pygame.Surface | None" = None
    trace_layer: "pygame.Surface | None" = None
    trace_layer_last_update = -trace_draw_stride

    def apply_window_size(request_w: int, request_h: int) -> None:
        """Enforce a square canvas based on the min dimension and refresh dependent surfaces."""
        nonlocal screen, width, height, canvas_w, trace_layer, trace_layer_last_update
        request_w = max(request_w, panel_w + 1)
        request_h = max(request_h, 1)
        square_side = max(1, min(request_h, request_w - panel_w))
        target_size = (panel_w + square_side, square_side)
        screen = pygame.display.set_mode(target_size, display_flags)
        actual_w, actual_h = screen.get_size()
        square_side = max(1, min(actual_h, actual_w - panel_w))
        width = panel_w + square_side
        height = square_side
        if (actual_w, actual_h) != (width, height):
            # Force a square client area if the OS adjusted our request.
            screen = pygame.display.set_mode((width, height), display_flags)
        canvas_w = square_side
        trace_layer = pygame.Surface((canvas_w, height), pygame.SRCALPHA).convert_alpha()
        trace_layer.fill((0, 0, 0, 0))
        trace_layer_last_update = -trace_draw_stride

    duration_limit = duration_seconds
    ffmpeg_proc = None
    ffmpeg_log = None
    target_frames = None

    if not offline:
        max_side = min(info.current_h, max(1, info.current_w - panel_w))
        canvas_side = max(1, int(max_side * canvas_scale))
        apply_window_size(panel_w + canvas_side, canvas_side)
    else:
        # Use a fixed offscreen size for offline rendering (square).
        canvas_side = 1080
        apply_window_size(panel_w + canvas_side, canvas_side)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 12)
    if offline:
        capture_stride = 1
        target_frames = int(offline_fps * duration_limit) if (duration_limit is not None and offline_fps is not None) else None
        ffmpeg_log_path = Path(offline_output).with_suffix(Path(offline_output).suffix + ".ffmpeg.log")
        ffmpeg_log = ffmpeg_log_path.open("w", encoding="utf-8")
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgba",
            "-s",
            f"{width}x{height}",
            "-r",
            str(offline_fps),
            "-i",
            "-",
            "-c:v",
            "libx264",
            "-movflags",
            "+faststart",
            "-pix_fmt",
            "yuv420p",
            offline_output,
        ]
        try:
            ffmpeg_proc = subprocess.Popen(
                ffmpeg_cmd,
                stdin=subprocess.PIPE,
                stderr=ffmpeg_log,
                start_new_session=True,
            )
        except FileNotFoundError as exc:
            raise SystemExit("ffmpeg not found; install ffmpeg or disable --offline.") from exc
        print(
            f"[offline] capture start: size={width}x{height}, hz={cfg.hz}, fps={offline_fps}, stride={capture_stride}, duration={duration_limit}s, target_frames={target_frames or 'unbounded'}",
            flush=True,
        )
        print(f"[offline] ffmpeg pid={ffmpeg_proc.pid}", flush=True)
        print(f"[offline] ffmpeg log: {ffmpeg_log_path}", flush=True)

    # Build architrino instances with per-arch offsets and base speeds.
    current_path_name = "multi" if len(arch_specs) > 1 else arch_specs[0].path
    states: List[ArchitrinoState] = []
    movers: Dict[str, Mover] = {
        "analytic": AnalyticMover(),
        "physics": PhysicsMover(),
    }
    path_traces: Dict[str, List[Vec2]] = {}

    def tangent_sign_for_heading(path: PathSpec, param: float, heading_deg: float) -> float:
        """Choose +1/-1 so path tangent best aligns with requested heading.
        Heading uses screen-friendly convention: 0=+x, 90=up (so y is inverted from math).
        """
        heading_rad = math.radians(heading_deg)
        h_vec = (math.cos(heading_rad), -math.sin(heading_rad))  # invert y for screen coords
        eps = 1e-3
        p_fwd = path.sampler(param + eps)
        p_back = path.sampler(param - eps)
        tan = (p_fwd[0] - p_back[0], p_fwd[1] - p_back[1])
        tan_len = math.hypot(*tan)
        if tan_len < 1e-12:
            return 1.0
        tan_unit = (tan[0] / tan_len, tan[1] / tan_len)
        dot = tan_unit[0] * h_vec[0] + tan_unit[1] * h_vec[1]
        return 1.0 if dot >= 0 else -1.0

    for spec in arch_specs:
        if spec.path not in paths:
            raise ValueError(f"Unknown path '{spec.path}'. Available: {list(paths.keys())}")
        base_path = paths[spec.path]
        decay = spec.decay if spec.decay is not None else base_path.decay
        if decay is not None and base_path.decay != decay:
            paths = dict(paths)
            paths[spec.path] = PathSpec(
                name=base_path.name,
                sampler=base_path.sampler,
                description=base_path.description,
                decay=decay,
            )
            base_path = paths[spec.path]
        phase, offset = default_phase_and_offset(spec.path, spec.start_pos, base_path.decay)
        sign = tangent_sign_for_heading(base_path, offset + phase, spec.velocity_heading_deg)
        start_r = math.hypot(*spec.start_pos)
        if spec.path == "exp_inward_spiral" and base_path.decay is not None:
            sample_r = math.exp(-base_path.decay * abs(offset))
        else:
            sample_x, sample_y = base_path.sampler(offset + phase)
            sample_r = math.hypot(sample_x, sample_y)
        radial_scale = start_r / sample_r if sample_r > 1e-9 else 1.0
        color = PURE_RED if spec.polarity == "p" else PURE_BLUE
        polarity_sign = 1 if spec.polarity == "p" else -1
        heading_rad = math.radians(spec.velocity_heading_deg)
        vx = spec.velocity_speed * math.cos(heading_rad)
        vy = -spec.velocity_speed * math.sin(heading_rad)  # screen-friendly (up is negative y)
        state = ArchitrinoState(
            name=spec.name,
            polarity=polarity_sign,
            color=color,
            mover_type=spec.mover or "analytic",
            path_name=spec.path,
            phase=phase,
            path_offset=offset,
            base_speed=spec.velocity_speed * sign,
            heading_deg=spec.velocity_heading_deg,
            radial_scale=radial_scale,
            param=0.0,
            pos=spec.start_pos,
            vel=(vx, vy),
            trace=[],
            speed_mult_override=None,
            last_emit_time=0.0,
            path_snap=cfg.path_snap,
            position_snap=cfg.position_snap,
            initial_path_offset=offset,
        )
        states.append(state)
        path_traces[state.name] = state.trace if state.trace is not None else []

    running = True
    paused = False if offline else cfg.start_paused
    frame_idx = 0
    sim_clock_start = time.monotonic()
    sim_clock_elapsed = 0.0

    dt = 1.0 / cfg.hz
    field_v = max(cfg.field_speed, 1e-6)
    shell_thickness = 0.0
    speed_mult = max(0.0, min(cfg.speed_multiplier, 100.0))  # global speed scale
    pending_speed_mult = speed_mult
    frame_skip = 0

    max_radius = math.sqrt(2) * cfg.domain_half_extent * 1.1
    emission_retention = max_radius / field_v
    emissions: List[Emission] = []
    recent_hits = deque()
    seen_hits = set()
    seen_hits_queue = deque()
    last_diff = {}
    last_diff_queue = deque()
    state_lookup = {s.name: s for s in states}
    num_pos_arch = sum(1 for s in states if s.polarity > 0)
    num_neg_arch = sum(1 for s in states if s.polarity < 0)
    BASE_OFFSET = 0.0  # start at param = 0
    hit_overlay_enabled = False
    show_hit_overlays = False
    trace_test_frames_remaining: int | None = None
    orbit_ring_visible = False
    display_info = (info.current_w, info.current_h)
    field_visible = ui.field_visible if ui is not None else cfg.field_visible
    architrinos_visible = ui.architrinos_visible if ui is not None else True
    path_trail_visible = ui.path_trail_visible if ui is not None else False
    path_trail_markers_visible = ui.path_trail_markers_visible if ui is not None else False
    caption_dirty = True
    positions: Dict[str, Vec2] = {}
    fps_window = 100
    fps_samples = deque(maxlen=fps_window + 1)  # (frame_idx, wall_clock_time)
    progress_stride = 100 if offline else None
    captured_frames = 0
    last_progress_log = time.monotonic()
    ffmpeg_failed = False

    def log_state(reason: str) -> None:
        """Print a fixed-width table snapshot of the current render/sim state."""
        tf = lambda v: "T" if v else "F"
        cols = [
            ("reason", reason, 24),
            ("p", tf(paused), 1),
            ("frm", str(frame_idx), 6),
            ("hz", str(cfg.hz), 4),
            ("skp", str(frame_skip), 3),
            ("flp", str(flip_stride), 3),
            ("trc", str(trace_draw_stride), 3),
            ("spd", f"{speed_mult:.2f}", 6),
            ("pend", f"{pending_speed_mult:.2f}", 6),
            ("path", current_path_name, 24),
            ("field", field_alg, 15),
            ("fv", tf(field_visible), 1),
            ("arch", tf(architrinos_visible), 1),
            ("ui", tf(ui_overlay_visible), 1),
            ("hit", tf(hit_overlay_enabled), 1),
            ("ovr", tf(show_hit_overlays), 1),
            ("size", f"{width}x{height} (panel={panel_w}, canvas={canvas_w})", 36),
            ("disp", f"{display_info[0]}x{display_info[1]}", 12),
        ]
        if not hasattr(log_state, "_widths"):
            widths = []
            for name, val, w in cols:
                base = w if w > 0 else len(name)
                widths.append(max(len(name), base, len(val)))
            log_state._widths = widths
        widths = log_state._widths
        header_line = " | ".join(name.upper().ljust(w) for (name, _, _), w in zip(cols, widths))
        value_line = " | ".join(val.ljust(w) for (_, val, _), w in zip(cols, widths))
        if not hasattr(log_state, "_printed_header"):
            print(header_line)
            log_state._printed_header = True
        print(value_line)

    FIGURE_SPACE = "\u2007"  # tabular-space to stabilize numeral widths in proportional fonts

    def pad_int(value: int, width: int) -> str:
        """Pad integer with figure spaces so digit columns stay aligned."""
        return f"{value:{width}d}".replace(" ", FIGURE_SPACE)

    def pad_float(value: float, width: int, precision: int) -> str:
        """Pad float with figure spaces; assumes width includes decimal and leading spaces."""
        return f"{value:{width}.{precision}f}".replace(" ", FIGURE_SPACE)

    def format_title(paused_flag: bool, label: str | None = None, fps: float | None = None) -> str:
        """Compact title line carrying former panel info."""
        speed_field = pad_float(speed_mult, 6, 2)
        speed_label = f"velo↑↓ {speed_field}"
        if paused_flag and pending_speed_mult != speed_mult:
            pending_field = pad_float(pending_speed_mult, 6, 2)
            speed_label = f"velo↑↓ {speed_field}->{pending_field}"

        skip_label = f"skip←→ {pad_int(frame_skip, 3)}"
        freq_label = f"🅕 {pad_int(cfg.hz, 4)}Hz"
        fps_val = int(round(fps)) if fps is not None else 0
        fps_label = f"fps {pad_int(fps_val, 5)}"
        field_label = f"field 🅥 {'on' if field_visible else 'off'}"
        prefix = f"ORBIT PATH VISUALIZER: {label}" if label else "Orbit Visualizer"
        # Width-stable status markers for macOS title bars.
        status = "⏸︎" if paused_flag else "▶︎"
        parts = [p for p in [speed_label, skip_label, freq_label, field_label, status, fps_label] if p]
        return prefix + " | " + " | ".join(parts)

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

    def format_frame_and_time(frame_number: int, elapsed_s: float) -> str:
        """
        Stabilize the rightmost numeric fields for proportional fonts.
        Fixed widths are chosen to absorb typical run ranges before widening.
        """
        frame_field = pad_int(frame_number, 9)  # up to 999,999,999 frames before width grows
        time_field = pad_float(elapsed_s, 8, 1)  # up to 999,999.9s before width grows
        return f"frame {frame_field} | t {time_field}s"

    def set_caption(paused_flag: bool, frame_number: int, elapsed_s: float, fps: float | None = None) -> None:
        """Single caption updater to keep all title parts in sync and width-stable."""
        pygame.display.set_caption(
            format_title(paused_flag=paused_flag, label=run_label, fps=fps)
            + " | "
            + format_frame_and_time(frame_number, elapsed_s)
        )

    def maybe_update_caption(paused_flag: bool, frame_number: int, elapsed_s: float, fps: float | None = None, force: bool = False) -> None:
        nonlocal caption_dirty
        if force or caption_dirty or frame_number % 100 == 0:
            set_caption(paused_flag=paused_flag, frame_number=frame_number, elapsed_s=elapsed_s, fps=fps)
            caption_dirty = False

    set_caption(paused_flag=paused, frame_number=frame_idx + 1, elapsed_s=sim_clock_elapsed)

    def draw_ring(target: "pygame.Surface", center: Vec2, radius_px: int, thickness_px: int, color: Tuple[int, int, int]) -> None:
        """
        Draw a crisp ring by filling an outer circle then punching out the inner with full transparency.
        Avoids gray borders from alpha blending while keeping the ring centered.
        """
        cx, cy = int(round(center[0])), int(round(center[1]))
        radius_px = max(1, int(round(radius_px)))
        thickness_px = max(1, int(round(thickness_px)))
        outer_r = radius_px + (thickness_px // 2)
        inner_r = max(0, outer_r - thickness_px)
        diam = (outer_r * 2) + 2
        ring_surface = pygame.Surface((diam, diam), pygame.SRCALPHA).convert_alpha()
        center_pt = (diam // 2, diam // 2)
        pygame.draw.circle(ring_surface, (*color, 255), center_pt, outer_r)
        if inner_r > 0:
            pygame.draw.circle(ring_surface, (0, 0, 0, 0), center_pt, inner_r)
        target.blit(ring_surface, (cx - diam // 2, cy - diam // 2))

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

    def vec_finite(p: Vec2) -> bool:
        return math.isfinite(p[0]) and math.isfinite(p[1])

    def vec_within_canvas(p: Vec2) -> bool:
        return -0.6 * width <= p[0] <= 1.6 * width and -0.6 * height <= p[1] <= 1.6 * height

    def clamp_speed(v: float) -> float:
        return max(0.0, min(v, 100.0))

    def apply_speed_change(new_speed: float, auto_pause: bool = True) -> None:
        nonlocal speed_mult, pending_speed_mult, paused
        current_time = frame_idx * dt
        nonlocal caption_dirty
        prev_speed = speed_mult
        speed_mult = clamp_speed(new_speed)
        pending_speed_mult = speed_mult
        # Preserve the current path parameter so paused positions stay fixed for analytic movers.
        for state in states:
            if state.mover_type == "analytic":
                state.path_offset += (prev_speed - speed_mult) * current_time * state.base_speed
        refresh_hits_for_current_time()
        if auto_pause:
            paused = True
        caption_dirty = True

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
        pos_norm_raw = np.where(net > 0.0, mag, 0.0)
        neg_norm_raw = np.where(net < 0.0, mag, 0.0)
        pos_scale = max(1, num_pos_arch)
        neg_scale = max(1, num_neg_arch)
        pos_norm = pos_norm_raw / (pos_scale * max_abs)
        neg_norm = neg_norm_raw / (neg_scale * max_abs)
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
        sign = float(em.polarity)
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
            print("Moderngl not available; falling back to cpu_incr.")
            field_alg = "cpu_incr"
            return False
        try:
            ctx = moderngl.create_context() if display else moderngl.create_standalone_context()
        except Exception as exc:
            print(f"GPU alg unavailable ({exc}); falling back to cpu_incr.")
            if not display:
                field_alg = "cpu_incr"
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
        set_caption(paused_flag=paused, frame_number=frame_idx + 1, elapsed_s=sim_clock_elapsed)

    def gpu_rebuild_field_surface(current_time: float) -> None:
        nonlocal field_surface
        if not init_gpu_renderer(display=False):
            rebuild_field_surface(current_time, update_last_radius=field_alg == "cpu_incr")
            return
        inst_entries = []
        for em in emissions:
            tau = current_time - em.time
            if tau <= 0:
                continue
            radius = field_v * tau
            if radius > max_radius:
                continue
            sign = float(em.polarity)
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
            sign = float(em.polarity)
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
        # Use fixed window dimensions for overlay quads; avoid per-frame scaling.
        view_w, view_h = width, height
        if view_w <= 0 or view_h <= 0:
            return
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
        x0 = (x / view_w) * 2.0 - 1.0
        x1 = ((x + size[0]) / view_w) * 2.0 - 1.0
        y0 = 1.0 - (y / view_h) * 2.0
        y1 = 1.0 - ((y + size[1]) / view_h) * 2.0
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

    def rebuild_trace_for_offsets() -> None:
        nonlocal path_traces
        for state in states:
            state.trace = []
            path_traces[state.name] = state.trace

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
        nonlocal emissions, field_grid, frame_idx, speed_mult, field_surface, positions, field_visible, path_traces, pending_speed_mult, sim_clock_start, sim_clock_elapsed
        if apply_pending_speed:
            speed_mult = clamp_speed(pending_speed_mult)
        else:
            speed_mult = clamp_speed(cfg.speed_multiplier)
            pending_speed_mult = speed_mult
        if not keep_offset:
            for state in states:
                state.path_offset = state.initial_path_offset
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
            rebuild_trace_for_offsets()
        recent_hits.clear()
        sim_clock_start = time.monotonic()
        sim_clock_elapsed = 0.0
        if field_visible:
            if field_alg == "gpu":
                if gpu_display:
                    gpu_update_field_texture(0.0)
                else:
                    gpu_rebuild_field_surface(0.0)
            else:
                rebuild_field_surface(0.0, update_last_radius=field_alg == "cpu_incr")
        log_state("reset")

    def render_frame_gl(positions: Dict[str, Vec2], hits: List[Hit], field_surf=None) -> None:
        nonlocal gpu_display, trace_layer_last_update, trace_layer
        if not init_gpu_renderer(display=True):
            gpu_display = False
            render_frame(positions, hits, field_surf)
            return
        ctx = gpu_state["ctx"]
        ctx.screen.use()
        # Fix viewport to the intended window size; avoid per-frame scaling.
        view_w, view_h = width, height
        ctx.viewport = (0, 0, view_w, view_h)
        ctx.clear(1.0, 1.0, 1.0, 1.0)
        if field_visible:
            if field_alg == "gpu":
                ctx.viewport = (panel_w, 0, canvas_w, height)
                gpu_present_field()
                ctx.viewport = (0, 0, view_w, view_h)
            elif field_surface is not None:
                gpu_draw_surface(field_surface, panel_w, 0, "field_rgb")

        overlay_has_content = (
            orbit_ring_visible
            or (ui_overlay_visible and (path_trail_visible or architrinos_visible))
            or show_hit_overlays
        )
        overlay_visible = overlay_has_content
        if overlay_visible:
            geometry_layer = pygame.Surface((canvas_w, height), pygame.SRCALPHA).convert_alpha()
            if orbit_ring_visible:
                center = (canvas_w // 2, canvas_w // 2)
                ring_radius_px = int((canvas_w / 2) * (1.0 / cfg.domain_half_extent))  # unit radius in world coords
                ring_radius_px = max(1, ring_radius_px)
                draw_ring(geometry_layer, center, ring_radius_px, 6, PURE_WHITE)

            if ui_overlay_visible and path_trail_visible:
                need_redraw_traces = paused or (frame_idx - trace_layer_last_update >= trace_draw_stride)
                if need_redraw_traces:
                    trace_layer.fill((0, 0, 0, 0))
                    for name, trace in path_traces.items():
                        if len(trace) < 2:
                            continue
                        # Use arch-specific color for visibility.
                        arch_obj = state_lookup.get(name)
                        base_color = arch_obj.color if arch_obj else PURE_WHITE
                        pts = [(int(world_to_canvas(pt)[0]), int(world_to_canvas(pt)[1])) for pt in trace]
                        n = len(pts)
                        if n < 2:
                            continue
                        max_segments = 24
                        marker_step = max(12, n // max_segments)
                        def inv_cube_weight(idx: int, total: int, strength: float = 4.0) -> float:
                            """Fade newest strong, oldest quickly via 1/(1 + (age*strength)^3)."""
                            age_frac = (total - 1 - idx) / max(1, total - 1)  # oldest≈1, newest≈0
                            return 1.0 / (1.0 + (age_frac * strength) ** 3)
                        for i in range(n - 1):
                            w = inv_cube_weight(i, n)  # match marker fade profile
                            alpha = int(255 * (0.1 + 0.8 * w))
                            color = (*base_color, alpha)
                            try:
                                pygame.draw.line(trace_layer, color, pts[i], pts[i + 1], 4)
                            except ValueError:
                                pass
                        if path_trail_markers_visible:
                            # Distinct, spaced markers with outline for visibility.
                            for i in range(0, n, marker_step):
                                w = inv_cube_weight(i, n)
                                alpha = int(255 * (0.1 + 0.8 * w))
                                fill_color = (*base_color, alpha)
                                try:
                                    gfxdraw.filled_circle(trace_layer, pts[i][0], pts[i][1], 5, fill_color)
                                    gfxdraw.aacircle(trace_layer, pts[i][0], pts[i][1], 6, PURE_WHITE)
                                except Exception:
                                    pass
                    trace_layer_last_update = frame_idx
                geometry_layer.blit(trace_layer, (0, 0))

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
                emitter_arch = state_lookup.get(hit.emitter)
                color = emitter_arch.color if emitter_arch else PURE_WHITE

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
                    emitter_arch = state_lookup.get(h.emitter)
                    line_color = emitter_arch.color if emitter_arch else PURE_WHITE
                    gfxdraw.line(geometry_layer, int(start[0]), int(start[1]), int(end[0]), int(end[1]), line_color)
                    gfxdraw.line(geometry_layer, int(start[0]), int(start[1] + 1), int(end[0]), int(end[1] + 1), line_color)

            particle_layer = pygame.Surface((canvas_w, height), pygame.SRCALPHA).convert_alpha()
            if show_hit_overlays:
                for h in hits:
                    start = world_to_canvas(h.emit_pos)
                    emitter_arch = state_lookup.get(h.emitter)
                    marker_color = LIGHT_RED if emitter_arch and emitter_arch.polarity > 0 else LIGHT_BLUE
                    gfxdraw.filled_circle(particle_layer, int(start[0]), int(start[1]), 4, marker_color)
                    gfxdraw.aacircle(particle_layer, int(start[0]), int(start[1]), 5, PURE_WHITE)

            if ui_overlay_visible and architrinos_visible:
                for name, pos in positions.items():
                    if not vec_finite(pos):
                        continue
                    arch = state_lookup.get(name)
                    if arch is None:
                        continue
                    pos_canvas = world_to_canvas(pos)
                    if not vec_finite(pos_canvas):
                        continue
                    if abs(pos_canvas[0]) > 32760 or abs(pos_canvas[1]) > 32760:
                        continue
                    gfxdraw.filled_circle(particle_layer, int(pos_canvas[0]), int(pos_canvas[1]), 6, arch.color)
                    gfxdraw.aacircle(particle_layer, int(pos_canvas[0]), int(pos_canvas[1]), 7, PURE_WHITE)

            gpu_draw_surface(geometry_layer, panel_w, 0, "overlay_geom")
            gpu_draw_surface(particle_layer, panel_w, 0, "overlay_particles")
        # Throttled flipping: always flip when paused; otherwise flip every flip_stride frames.
        if not offline:
            if paused or frame_idx % flip_stride == 0:
                pygame.display.flip()

    def render_frame(positions: Dict[str, Vec2], hits: List[Hit], field_surf=None) -> None:
        nonlocal trace_layer_last_update, trace_layer
        if gpu_display:
            render_frame_gl(positions, hits, field_surf)
            return
        screen.fill(PURE_WHITE)
        fs = field_surf if field_surf is not None else (field_surface if field_visible else None)
        if fs is not None:
            screen.blit(fs, (panel_w, 0))

        overlay_has_content = (
            orbit_ring_visible
            or (ui_overlay_visible and (path_trail_visible or architrinos_visible))
            or show_hit_overlays
        )
        overlay_visible = overlay_has_content
        if overlay_visible:
            geometry_layer = pygame.Surface((canvas_w, height), pygame.SRCALPHA).convert_alpha()
            if orbit_ring_visible:
                center = (canvas_w // 2, canvas_w // 2)
                ring_radius_px = int((canvas_w / 2) * (1.0 / cfg.domain_half_extent))  # unit radius in world coords
                ring_radius_px = max(1, ring_radius_px)
                draw_ring(geometry_layer, center, ring_radius_px, 6, PURE_WHITE)

            if ui_overlay_visible and path_trail_visible:
                need_redraw_traces = paused or (frame_idx - trace_layer_last_update >= trace_draw_stride)
                if need_redraw_traces:
                    trace_layer.fill((0, 0, 0, 0))
                    for name, trace in path_traces.items():
                        if len(trace) < 2:
                            continue
                        arch_obj = state_lookup.get(name)
                        base_color = arch_obj.color if arch_obj else PURE_WHITE
                        pts = [(int(world_to_canvas(pt)[0]), int(world_to_canvas(pt)[1])) for pt in trace]
                        n = len(pts)
                        if n < 2:
                            continue
                        max_segments = 24
                        marker_step = max(12, n // max_segments)
                        def inv_cube_weight(idx: int, total: int, strength: float = 4.0) -> float:
                            age_frac = (total - 1 - idx) / max(1, total - 1)
                            return 1.0 / (1.0 + (age_frac * strength) ** 3)
                        for i in range(n - 1):
                            w = inv_cube_weight(i, n)
                            alpha = int(255 * (0.1 + 0.8 * w))
                            color = (*base_color, alpha)
                            try:
                                pygame.draw.line(trace_layer, color, pts[i], pts[i + 1], 4)
                            except ValueError:
                                pass
                        if path_trail_markers_visible:
                            for i in range(0, n, marker_step):
                                w = inv_cube_weight(i, n)
                                alpha = int(255 * (0.1 + 0.8 * w))
                                fill_color = (*base_color, alpha)
                                try:
                                    gfxdraw.filled_circle(trace_layer, pts[i][0], pts[i][1], 5, fill_color)
                                    gfxdraw.aacircle(trace_layer, pts[i][0], pts[i][1], 6, PURE_WHITE)
                                except Exception:
                                    pass
                    trace_layer_last_update = frame_idx
                geometry_layer.blit(trace_layer, (0, 0))

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
                emitter_arch = state_lookup.get(hit.emitter)
                color = emitter_arch.color if emitter_arch else PURE_WHITE

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
                    emitter_arch = state_lookup.get(h.emitter)
                    line_color = emitter_arch.color if emitter_arch else PURE_WHITE
                    # Thicker line by drawing twice with slight offsets
                    gfxdraw.line(geometry_layer, int(start[0]), int(start[1]), int(end[0]), int(end[1]), line_color)
                    gfxdraw.line(geometry_layer, int(start[0]), int(start[1] + 1), int(end[0]), int(end[1] + 1), line_color)

            particle_layer = pygame.Surface((canvas_w, height), pygame.SRCALPHA).convert_alpha()
            if show_hit_overlays:
                for h in hits:
                    start = world_to_canvas(h.emit_pos)
                    emitter_arch = state_lookup.get(h.emitter)
                    marker_color = LIGHT_RED if emitter_arch and emitter_arch.polarity > 0 else LIGHT_BLUE
                    gfxdraw.filled_circle(particle_layer, int(start[0]), int(start[1]), 4, marker_color)
                    gfxdraw.aacircle(particle_layer, int(start[0]), int(start[1]), 5, PURE_WHITE)

            if ui_overlay_visible and architrinos_visible:
                for name, pos in positions.items():
                    arch = state_lookup.get(name)
                    if arch is None:
                        continue
                    pos_canvas = world_to_canvas(pos)
                    gfxdraw.filled_circle(particle_layer, int(pos_canvas[0]), int(pos_canvas[1]), 6, arch.color)
                    gfxdraw.aacircle(particle_layer, int(pos_canvas[0]), int(pos_canvas[1]), 7, PURE_WHITE)

            screen.blit(geometry_layer, (panel_w, 0))
            screen.blit(particle_layer, (panel_w, 0))

        if not offline:
            pygame.display.flip()

    def current_positions(time_t: float) -> Dict[str, Vec2]:
        env = MoverEnv(
            time=time_t,
            dt=dt,
            field_speed=field_v,
            speed_mult=speed_mult,
            path_snap=cfg.path_snap,
            position_snap=cfg.position_snap,
            emissions=emissions,
            allow_self=True,
            hit_tolerance=None,
        )
        pos: Dict[str, Vec2] = {}
        for state in states:
            path_spec = None
            if state.path_name is not None:
                path_spec = paths.get(state.path_name)
            if state.mover_type == "analytic" and path_spec is None:
                continue
            mover = movers.get(state.mover_type, movers["analytic"])
            pos[state.name] = mover.step(state, env, path_spec if path_spec is not None else paths.get("unit_circle"))
        return pos

    def prune_emissions(current_time: float) -> None:
        nonlocal emissions
        cutoff = current_time - emission_retention
        if cutoff <= 0:
            return
        if field_alg != "cpu_incr":
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
    log_state("startup")
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
                        log_state("key_escape_reset")
                    elif event.key == pygame.K_q:
                        running = False
                        log_state("key_q_quit")
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
                            log_state("key_h_toggle_hit_overlay")
                    elif event.key == pygame.K_RIGHT:
                        frame_skip += 1
                        caption_dirty = True
                        log_state("key_right_frame_skip")
                    elif event.key == pygame.K_LEFT:
                        frame_skip = max(0, frame_skip - 1)
                        caption_dirty = True
                        log_state("key_left_frame_skip")
                    elif event.key == pygame.K_UP:
                        apply_speed_change(speed_mult + 0.1, auto_pause=True)
                        log_state("key_up_speed")
                    elif event.key == pygame.K_DOWN:
                        apply_speed_change(speed_mult - 0.1, auto_pause=True)
                        log_state("key_down_speed")
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
                        caption_dirty = True
                        log_state("key_f_hz_toggle")
                    elif event.key == pygame.K_b:
                        algs = ["cpu_incr", "cpu_full", "gpu"]
                        try:
                            idx = algs.index(field_alg)
                        except ValueError:
                            idx = 0
                        field_alg = algs[(idx + 1) % len(algs)]
                        if field_alg == "gpu":
                            if not init_gpu_renderer(display=gpu_display):
                                field_alg = "cpu_incr"
                        if field_alg == "gpu":
                            if gpu_display:
                                gpu_update_field_texture(frame_idx * dt)
                            else:
                                gpu_rebuild_field_surface(frame_idx * dt)
                        else:
                            rebuild_field_surface(
                                frame_idx * dt,
                                update_last_radius=field_alg == "cpu_incr",
                            )
                        log_state("key_b_field_alg")
                    elif event.key == pygame.K_i:
                        log_state("key_i_info")
                    elif event.key == pygame.K_t:
                        trace_test_frames_remaining = 3000
                        paused = False
                        hit_overlay_enabled = False
                        show_hit_overlays = False
                        sim_clock_start = time.monotonic()
                        log_state("key_t_trace_test")
                    elif event.key == pygame.K_u:
                        ui_overlay_visible = not ui_overlay_visible
                        caption_dirty = True
                        log_state("key_u_ui_overlay")
                    elif event.key == pygame.K_o:
                        orbit_ring_visible = not orbit_ring_visible
                        caption_dirty = True
                        log_state("key_o_orbit_ring_toggle")
                elif event.type == pygame.VIDEORESIZE:
                    apply_window_size(event.w, event.h)
                    log_state("resize")
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_v:
                        if field_visible:
                            field_visible = False
                        else:
                            field_visible = True
                            if field_alg == "gpu":
                                if gpu_display:
                                    gpu_update_field_texture(frame_idx * dt)
                                else:
                                    gpu_rebuild_field_surface(frame_idx * dt)
                            else:
                                rebuild_field_surface(
                                    frame_idx * dt,
                                    update_last_radius=field_alg == "cpu_incr",
                                )
                        caption_dirty = True
                        log_state("key_v_field_visible")

            show_hit_overlays = paused and hit_overlay_enabled
            if not paused:
                sim_clock_elapsed += time.monotonic() - sim_clock_start
                sim_clock_start = time.monotonic()
            if paused:
                # Refresh hits once when paused with overlay requested.
                if hit_overlay_enabled and not recent_hits:
                    refresh_hits_for_current_time()
                if frame_idx % 100 == 0 or caption_dirty:
                    fps_val = 0.0
                    if len(fps_samples) >= 2:
                        oldest_frame, oldest_time = fps_samples[0]
                        newest_frame, newest_time = fps_samples[-1]
                        frame_delta = max(1, newest_frame - oldest_frame)
                        time_delta = max(1e-6, newest_time - oldest_time)
                        fps_val = frame_delta / time_delta
                    maybe_update_caption(
                        paused_flag=True,
                        frame_number=frame_idx + 1,
                        elapsed_s=sim_clock_elapsed,
                        fps=fps_val,
                        force=caption_dirty,
                    )
                render_frame(positions, list(recent_hits))
                if offline and ffmpeg_proc and ffmpeg_proc.stdin:
                    frame_bytes = pygame.image.tostring(screen, "RGBA")
                    try:
                        ffmpeg_proc.stdin.write(frame_bytes)
                    except BrokenPipeError:
                        pass
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
                # Abort if any physics mover pushes outside a generous canvas bound.
                for name, pos in positions.items():
                    if not vec_finite(pos):
                        running = False
                        break
                    pos_canvas = world_to_canvas(pos)
                    if not vec_finite(pos_canvas) or not vec_within_canvas(pos_canvas):
                        running = False
                        break
                if not running:
                    break
                for name, pos in positions.items():
                    if not vec_finite(pos):
                        continue
                    trace = path_traces.get(name)
                    if trace is None:
                        trace = []
                        path_traces[name] = trace
                    trace.append(pos)
                    state = state_lookup.get(name)
                    limit = state.trace_limit if state and state.trace_limit else 40000
                    if len(trace) > limit:
                        path_traces[name] = trace[-limit:]

                for state in states:
                    if state.name not in positions:
                        continue
                    emissions.append(
                        Emission(time=current_time, pos=positions[state.name], emitter=state.name, polarity=state.polarity)
                    )

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
                if offline and target_frames is not None and captured_frames >= target_frames:
                    running = False
                    break

            frame_idx = sim_idx - 1
            if offline and target_frames is not None and captured_frames >= target_frames:
                break
            if field_alg == "cpu_incr":
                update_field_surface(current_time)
            elif field_alg == "gpu":
                if field_visible:
                    if gpu_display:
                        gpu_update_field_texture(current_time)
                    else:
                        gpu_rebuild_field_surface(current_time)
            else:
                rebuild_field_surface(current_time)
            render_frame(positions, display_hits)
            if offline and ffmpeg_proc and ffmpeg_proc.stdin and (frame_idx % capture_stride == 0) and not ffmpeg_failed:
                frame_bytes = pygame.image.tostring(screen, "RGBA")
                try:
                    ffmpeg_proc.stdin.write(frame_bytes)
                    captured_frames += 1
                    now = time.monotonic()
                    if progress_stride and (captured_frames % progress_stride == 0 or (now - last_progress_log) >= 5.0):
                        print(
                            f"[offline] captured {captured_frames} frames at sim_t={current_time:.2f}s (frame_idx={frame_idx})",
                            flush=True,
                        )
                        last_progress_log = now
                except BrokenPipeError:
                    ffmpeg_failed = True
                    print("[offline] ffmpeg pipe closed; stopping capture.", flush=True)
            if offline and target_frames is not None and captured_frames >= target_frames:
                running = False

            # Refresh caption at a coarse cadence to reduce overhead; force on state changes.
            fps_samples.append((frame_idx, time.monotonic()))
            fps_val = 0.0
            if len(fps_samples) >= 2:
                oldest_frame, oldest_time = fps_samples[0]
                newest_frame, newest_time = fps_samples[-1]
                frame_delta = max(1, newest_frame - oldest_frame)
                time_delta = max(1e-6, newest_time - oldest_time)
                fps_val = frame_delta / time_delta
            maybe_update_caption(
                paused_flag=paused,
                frame_number=frame_idx + 1,
                elapsed_s=current_time if not paused else sim_clock_elapsed,
                fps=fps_val,
            )

            if offline:
                now = time.monotonic()
                if now - last_progress_log >= 5.0:
                    print(
                        f"[offline] progress: sim_t={current_time:.2f}s frame_idx={frame_idx} captured={captured_frames}",
                        flush=True,
                    )
                    last_progress_log = now

            clock.tick(0)

            frame_idx = sim_idx
            if trace_test_frames_remaining is not None:
                trace_test_frames_remaining -= steps
                if trace_test_frames_remaining <= 0:
                    running = False
                    continue
    except KeyboardInterrupt:
        running = False
    finally:
        log_state("exit")
        if ffmpeg_proc:
            try:
                ffmpeg_proc.stdin.close()
            except Exception:
                pass
            ffmpeg_proc.wait()
            print(f"[offline] wrote video to {offline_output} (captured_frames={captured_frames})", flush=True)
        if ffmpeg_log:
            try:
                ffmpeg_log.close()
            except Exception:
                pass
        pygame.quit()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Orbit visualizer prototype (live).")
    parser.add_argument("--run", type=str, required=True, help="JSON run file with directives and architrino groups.")
    parser.add_argument("--render", action="store_true", help="Open a PyGame window and render the live simulation.")
    parser.add_argument("--offline", action="store_true", help="Render offline to an mp4 (no window, no vsync).")
    parser.add_argument("--output", type=str, default="output.mp4", help="Output video filename for offline render.")
    parser.add_argument("--fps", type=int, default=60, help="Playback FPS for offline encoding.")
    parser.add_argument("--duration-seconds", type=float, default=None, help="Stop the simulation after this many simulation seconds.")
    return parser.parse_args()


def main() -> None:
    try:
        args = parse_args()
        scenario = load_run_file(args.run, PATH_LIBRARY)
        render = scenario.render or args.render or args.offline
        if not render:
            raise SystemExit("Render disabled. Set directives.render or pass --render/--offline.")
        run_label = Path(args.run).name
        render_live(
            scenario.config,
            scenario.paths,
            arch_specs=scenario.architrinos,
            ui=scenario.ui,
            path_name=scenario.primary_path(),
            run_label=run_label,
            offline=args.offline,
            offline_output=args.output,
            offline_fps=args.fps,
            duration_seconds=args.duration_seconds if args.duration_seconds is not None else scenario.config.duration_seconds,
        )
    except KeyboardInterrupt:
        # Graceful exit on Ctrl-C without traceback.
        try:
            import pygame

            pygame.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
