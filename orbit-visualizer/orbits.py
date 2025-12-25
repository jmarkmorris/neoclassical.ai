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
    max_force: float = 25.0  # clamp for physics impulse magnitude
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
    canvas_shrink: float = 0.9
    seed_static_field: bool = False
    grid_visible: bool = False
    canvas_shrink: float = 0.9


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
    phases: list | None = None


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


def _coerce_positive_float(value: object, label: str, allow_none: bool = True) -> float | None:
    if value is None and allow_none:
        return None
    val = _coerce_float(value, label)
    if val < 0:
        raise ValueError(f"{label} must be >= 0.")
    return val


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

    max_force = directives.get("max_force", 25.0)
    if max_force is not None:
        max_force = _coerce_float(max_force, "directives.max_force")
        if max_force <= 0:
            raise ValueError("directives.max_force must be > 0.")

    world_size = directives.get("world_size", None)
    if world_size is not None:
        world_size = _coerce_float(world_size, "directives.world_size")
        if world_size <= 0:
            raise ValueError("directives.world_size must be > 0.")
    domain_half_extent = directives.get("domain_half_extent", None)
    if domain_half_extent is not None:
        domain_half_extent = _coerce_float(domain_half_extent, "directives.domain_half_extent")
        if domain_half_extent <= 0:
            raise ValueError("directives.domain_half_extent must be > 0.")
    if world_size is not None and domain_half_extent is not None:
        if abs(world_size - 2.0 * domain_half_extent) > 1e-6:
            raise ValueError("directives.world_size conflicts with directives.domain_half_extent.")
    if world_size is not None:
        domain_half_extent = world_size / 2.0
    if domain_half_extent is None:
        domain_half_extent = 2.0

    cfg = SimulationConfig(
        hz=_coerce_int(directives.get("hz", 1000), "directives.hz"),
        field_speed=_coerce_float(directives.get("field_speed", 1.0), "directives.field_speed"),
        max_force=max_force,
        domain_half_extent=domain_half_extent,
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
        canvas_shrink=_coerce_float(directives.get("canvas_shrink", 0.9), "directives.canvas_shrink"),
        seed_static_field=bool(directives.get("seed_static_field", False)),
        grid_visible=bool(directives.get("grid_visible", False)),
    )

    paths_override = dict(paths)
    arch_specs: List[ArchitrinoSpec] = []
    physics_present = False
    physics_present = False
    physics_present = False
    for idx, entry in enumerate(arch_list):
        arch = _expect_dict(entry, f"architrinos[{idx}]")
        name = arch.get("name") or f"arch-{idx+1}"
        if not isinstance(name, str):
            raise ValueError(f"architrinos[{idx}].name must be a string.")
        mover_raw = arch.get("mover")
        mover_type = None
        if mover_raw is not None:
            if not isinstance(mover_raw, str):
                raise ValueError(f"architrinos[{idx}].mover must be a string if provided.")
            mover_type = mover_raw.lower()
            if mover_type not in {"analytic", "physics"}:
                raise ValueError(f"architrinos[{idx}].mover must be 'analytic' or 'physics'.")
        polarity = arch.get("type") or arch.get("polarity")
        if polarity not in {"p", "e"}:
            raise ValueError(f"architrinos[{idx}] polarity/type must be 'p' or 'e'.")
        path_name_raw = arch.get("path")
        if path_name_raw is not None and not isinstance(path_name_raw, str):
            raise ValueError(f"architrinos[{idx}].path must be a string if provided.")
        path_name = path_name_raw if isinstance(path_name_raw, str) else None
        decay_override = arch.get("decay")
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
        phases_raw = arch.get("phases")
        if not phases_raw:
            raise ValueError(f"architrinos[{idx}] requires phases with at least one entry.")
        if not isinstance(phases_raw, list):
            raise ValueError(f"architrinos[{idx}].phases must be an array.")
        if not phases_raw:
            raise ValueError(f"architrinos[{idx}].phases must contain at least one entry.")
        if phases_raw:
            parsed_phases = []
            cumulative = 0.0
            for p_idx, phase_raw in enumerate(phases_raw):
                phase_obj = _expect_dict(phase_raw, f"architrinos[{idx}].phases[{p_idx}]")
                mode = phase_obj.get("mode", "move")
                if not isinstance(mode, str):
                    raise ValueError(f"architrinos[{idx}].phases[{p_idx}].mode must be a string.")
                mode = mode.lower()
                if mode not in {"move", "frozen"}:
                    raise ValueError(f"architrinos[{idx}].phases[{p_idx}].mode must be 'move' or 'frozen'.")
                mover_override = phase_obj.get("mover")
                if mover_override is not None and not isinstance(mover_override, str):
                    raise ValueError(f"architrinos[{idx}].phases[{p_idx}].mover must be a string if provided.")
                if mover_override is not None:
                    mover_override = mover_override.lower()
                    if mover_override not in {"analytic", "physics"}:
                        raise ValueError(f"architrinos[{idx}].phases[{p_idx}].mover must be 'analytic' or 'physics'.")
                path_override = phase_obj.get("path")
                if path_override is not None and not isinstance(path_override, str):
                    raise ValueError(f"architrinos[{idx}].phases[{p_idx}].path must be a string if provided.")
                duration = _coerce_positive_float(phase_obj.get("duration_seconds"), f"architrinos[{idx}].phases[{p_idx}].duration_seconds", allow_none=True)
                velocity_override = phase_obj.get("velocity")
                vel_vec = None
                if velocity_override is not None:
                    vel_dict = _expect_dict(velocity_override, f"architrinos[{idx}].phases[{p_idx}].velocity")
                    v_speed = _coerce_float(vel_dict.get("speed", speed), f"architrinos[{idx}].phases[{p_idx}].velocity.speed")
                    v_heading = _coerce_float(vel_dict.get("heading_deg", heading_deg), f"architrinos[{idx}].phases[{p_idx}].velocity.heading_deg")
                    v_rad = math.radians(v_heading)
                    vel_vec = (v_speed * math.cos(v_rad), -v_speed * math.sin(v_rad))
                phase_speed = phase_obj.get("speed_multiplier")
                if phase_speed is not None:
                    phase_speed = _coerce_float(phase_speed, f"architrinos[{idx}].phases[{p_idx}].speed_multiplier")
                start_t = cumulative
                end_t = None
                if duration is not None:
                    end_t = cumulative + duration
                    cumulative = end_t
                parsed_phases.append(
                    {
                        "mode": mode,
                        "start": start_t,
                        "end": end_t,
                        "mover": mover_override,
                        "path": path_override,
                        "speed_multiplier": phase_speed,
                        "velocity": vel_vec,
                    }
                )
        else:
            parsed_phases = None

        first_phase = parsed_phases[0] if parsed_phases else None
        phase0_mover = first_phase.get("mover") if first_phase else None
        phase0_path = first_phase.get("path") if first_phase else None
        if parsed_phases and phase0_mover is None:
            raise ValueError(f"architrinos[{idx}].phases[0].mover is required when phases are provided.")

        mover_effective = phase0_mover or mover_type or "analytic"
        if mover_effective not in {"analytic", "physics"}:
            raise ValueError(f"architrinos[{idx}].mover must be 'analytic' or 'physics'.")
        if mover_effective == "physics":
            physics_present = True

        path_effective = phase0_path or path_name
        if mover_effective == "physics":
            if path_effective and path_effective.lower() in {"dynamic", "physics"}:
                path_effective = None
            elif path_effective and path_effective not in paths_override:
                raise ValueError(f"Unknown path '{path_effective}' for architrinos[{idx}]. Available: {list(paths_override.keys())}")
        else:
            if not path_effective:
                raise ValueError(f"architrinos[{idx}].path must be set for analytic movers.")
            if path_effective not in paths_override:
                raise ValueError(f"Unknown path '{path_effective}' for architrinos[{idx}]. Available: {list(paths_override.keys())}")

        if decay_override is not None:
            if path_effective != "exp_inward_spiral":
                raise ValueError("decay override is only supported for exp_inward_spiral.")
            decay_val = _coerce_float(decay_override, f"architrinos[{idx}].decay")
            base = paths_override[path_effective]
            paths_override = dict(paths_override)
            paths_override[path_effective] = PathSpec(
                name=base.name,
                sampler=base.sampler,
                description=base.description,
                decay=decay_val,
            )
        arch_specs.append(
            ArchitrinoSpec(
                name=name,
                polarity=polarity,
                path=path_effective or "dynamic",
                start_pos=start_pos,
                velocity_speed=speed,
                velocity_heading_deg=heading_deg,
                decay=decay_override if decay_override is not None else None,
                mover=mover_effective,
                phases=parsed_phases,
            )
        )

    # Default: do not pre-bake static fields; only enable when explicitly requested.
    cfg.seed_static_field = bool(directives.get("seed_static_field", False))

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

    shrink_factor = cfg.canvas_shrink  # reduce requested canvas to avoid OS downscale/resizes
    if not offline:
        max_side = min(info.current_h, max(1, info.current_w - panel_w))
        canvas_side = max(1, int(max_side * shrink_factor * canvas_scale))
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
    movers: Dict[str, Mover] = {
        "analytic": AnalyticMover(),
        "physics": PhysicsMover(),
    }

    def tangent_sign_for_heading(path: PathSpec, param: float, heading_deg: float) -> float:
        """Choose +1/-1 so path tangent best aligns with requested heading.
        Heading uses screen-friendly convention: 0=+x, 90=up (so y is inverted from math).
        """
        def pos_at(p: float) -> Vec2:
            if path.name == "exp_inward_spiral" and path.decay is not None:
                radius = math.exp(-path.decay * abs(p))
                return (radius * math.cos(p), radius * math.sin(p))
            return path.sampler(p)

        heading_rad = math.radians(heading_deg)
        h_vec = (math.cos(heading_rad), -math.sin(heading_rad))  # invert y for screen coords
        eps = 1e-3
        p_fwd = pos_at(param + eps)
        p_back = pos_at(param - eps)
        tan = (p_fwd[0] - p_back[0], p_fwd[1] - p_back[1])
        tan_len = math.hypot(*tan)
        if tan_len < 1e-12:
            return 1.0
        tan_unit = (tan[0] / tan_len, tan[1] / tan_len)
        dot = tan_unit[0] * h_vec[0] + tan_unit[1] * h_vec[1]
        return 1.0 if dot >= 0 else -1.0

    def build_states_from_specs() -> tuple[list[ArchitrinoState], dict[str, list[Vec2]]]:
        new_states: list[ArchitrinoState] = []
        new_traces: dict[str, list[Vec2]] = {}
        nonlocal paths
        for spec in arch_specs:
            # Derive initial mover/path/velocity from first phase if present; otherwise use top-level.
            first_phase = (spec.phases or [])[0] if spec.phases else None
            init_mover = (first_phase.get("mover") if first_phase else None) or spec.mover
            init_path_name = (first_phase.get("path") if first_phase else None) or (spec.path if spec.mover == "analytic" else None)
            base_path = None
            if init_path_name in paths:
                base_path = paths[init_path_name]
            elif init_mover == "analytic":
                raise ValueError(f"Unknown path '{init_path_name}'. Available: {list(paths.keys())}")

            decay = spec.decay if (spec.decay is not None and base_path is not None) else (base_path.decay if base_path else None)
            if base_path is not None and decay is not None and base_path.decay != decay:
                paths = dict(paths)
                paths[spec.path] = PathSpec(
                    name=base_path.name,
                    sampler=base_path.sampler,
                    description=base_path.description,
                    decay=decay,
                )
                base_path = paths[spec.path]

            if init_mover == "physics":
                phase, offset = 0.0, 0.0
                sign = 1.0
                radial_scale = 1.0
            else:
                phase, offset = default_phase_and_offset(init_path_name, spec.start_pos, base_path.decay if base_path else None)
                sign = tangent_sign_for_heading(base_path, offset + phase, spec.velocity_heading_deg) if base_path else 1.0
                start_r = math.hypot(*spec.start_pos)
                if init_path_name == "exp_inward_spiral" and base_path and base_path.decay is not None:
                    sample_r = math.exp(-base_path.decay * abs(offset))
                elif base_path:
                    sample_x, sample_y = base_path.sampler(offset + phase)
                    sample_r = math.hypot(sample_x, sample_y)
                else:
                    sample_r = start_r
                radial_scale = start_r / sample_r if sample_r > 1e-9 else 1.0
            color = PURE_RED if spec.polarity == "p" else PURE_BLUE
            polarity_sign = 1 if spec.polarity == "p" else -1
            heading_rad = math.radians(spec.velocity_heading_deg)
            vx = spec.velocity_speed * math.cos(heading_rad)
            vy = -spec.velocity_speed * math.sin(heading_rad)  # screen-friendly (up is negative y)
            if first_phase and first_phase.get("velocity") is not None:
                v_override = first_phase["velocity"]
                v_speed = _coerce_float(v_override.get("speed", spec.velocity_speed), "phase0.velocity.speed")
                v_heading = _coerce_float(v_override.get("heading_deg", spec.velocity_heading_deg), "phase0.velocity.heading_deg")
                v_rad = math.radians(v_heading)
                vx = v_speed * math.cos(v_rad)
                vy = -v_speed * math.sin(v_rad)
            state = ArchitrinoState(
                name=spec.name,
                polarity=polarity_sign,
                color=color,
                mover_type=init_mover or "analytic",
                path_name=init_path_name,
                phase=phase,
                path_offset=offset,
                base_speed=spec.velocity_speed * sign,
                heading_deg=spec.velocity_heading_deg,
                radial_scale=radial_scale,
                param=offset,
                pos=spec.start_pos,
                initial_vel=(vx, vy),
                vel=(vx, vy),
                trace=[],
                speed_mult_override=None,
                last_emit_time=0.0,
                path_snap=cfg.path_snap,
                position_snap=cfg.position_snap,
                initial_path_offset=offset,
                last_time=0.0,
            )
            new_states.append(state)
            new_traces[state.name] = state.trace if state.trace is not None else []
        return new_states, new_traces

    states, path_traces = build_states_from_specs()

    running = True
    exit_reason: str | None = None
    paused = False if offline else cfg.start_paused
    frame_idx = 0
    phase_plans: Dict[str, list] = {spec.name: (spec.phases or []) for spec in arch_specs}
    phase_indices: Dict[str, int | None] = {spec.name: None for spec in arch_specs}
    frozen_now: set[str] = set()
    sim_clock_start = time.monotonic()
    sim_clock_elapsed = 0.0

    dt = 1.0 / cfg.hz
    field_v = max(cfg.field_speed, 1e-6)
    shell_thickness = 0.0
    speed_mult = max(0.0, min(cfg.speed_multiplier, 100.0))  # global speed scale
    frame_skip = 0

    max_radius = 0.0
    emission_retention = 0.0
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
    display_info = (info.current_w, info.current_h)
    field_visible = ui.field_visible if ui is not None else cfg.field_visible
    architrinos_visible = ui.architrinos_visible if ui is not None else True
    path_trail_visible = ui.path_trail_visible if ui is not None else False
    path_trail_markers_visible = ui.path_trail_markers_visible if ui is not None else False
    legend_visible = False
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

    def format_title(paused_flag: bool, label: str | None = None, fps: float | None = None, max_vel: float | None = None) -> str:
        """Compact title line carrying former panel info."""
        skip_label = f"skip←→ {pad_int(frame_skip, 3)}"
        freq_label = f"🅕 {pad_int(cfg.hz, 4)}Hz"
        fps_val = int(round(fps)) if fps is not None else 0
        fps_label = f"fps {pad_int(fps_val, 5)}"
        vel_label = ""
        if max_vel is not None:
            vel_field = pad_float(max_vel, 6, 2)
            vel_label = f"v {vel_field}"
        field_label = ""
        prefix = f"{label}" if label else "Path Visualizer"
        # Width-stable status markers for macOS title bars.
        status = "⏸︎" if paused_flag else "▶︎"
        parts = [vel_label, skip_label, freq_label, field_label, status, fps_label]
        parts = [p for p in parts if p]
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

    def set_caption(paused_flag: bool, frame_number: int, elapsed_s: float, fps: float | None = None, max_vel: float | None = None) -> None:
        """Single caption updater to keep all title parts in sync and width-stable."""
        pygame.display.set_caption(
            format_title(paused_flag=paused_flag, label=run_label, fps=fps, max_vel=max_vel)
            + " | "
            + format_frame_and_time(frame_number, elapsed_s)
            + " | ?"
        )

    def maybe_update_caption(paused_flag: bool, frame_number: int, elapsed_s: float, fps: float | None = None, force: bool = False, max_vel: float | None = None) -> None:
        nonlocal caption_dirty
        if force or caption_dirty or frame_number % 100 == 0:
            set_caption(paused_flag=paused_flag, frame_number=frame_number, elapsed_s=elapsed_s, fps=fps, max_vel=max_vel)
            caption_dirty = False

    set_caption(paused_flag=paused, frame_number=frame_idx + 1, elapsed_s=sim_clock_elapsed, max_vel=None)

    def compute_state_speed(state: ArchitrinoState, time_t: float) -> float:
        if state.mover_type == "physics":
            vx, vy = state.vel
            if not (math.isfinite(vx) and math.isfinite(vy)):
                return 0.0
            return math.hypot(vx, vy)
        if state.mover_type != "analytic":
            return 0.0
        speed_mult_local = state.speed_mult_override if state.speed_mult_override is not None else speed_mult
        return abs(state.base_speed * speed_mult_local)

    def compute_max_velocity(time_t: float) -> float:
        if not states:
            return 0.0
        max_val = 0.0
        for st in states:
            val = compute_state_speed(st, time_t)
            if val > max_val:
                max_val = val
        return max_val

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

    grid_debug_printed = False

    def draw_grid(target: "pygame.Surface") -> None:
        """Draw a light grid at 0.25 spacing centered on the domain."""
        nonlocal grid_debug_printed
        step = 0.25
        extent = cfg.domain_half_extent
        color = (220, 220, 220)
        axis_color = (180, 180, 180)
        if step <= 0 or extent <= 0:
            return
        intervals = int(round((2 * extent) / step))
        if intervals <= 0:
            return
        # Vertical lines
        for i in range(intervals + 1):
            x_world = -extent + i * step
            p0 = world_to_canvas((x_world, -extent))
            p1 = world_to_canvas((x_world, extent))
            if vec_finite(p0) and vec_finite(p1):
                pygame.draw.line(target, color, p0, p1, 1)
        # Horizontal lines
        for i in range(intervals + 1):
            y_world = -extent + i * step
            p0 = world_to_canvas((-extent, y_world))
            p1 = world_to_canvas((extent, y_world))
            if vec_finite(p0) and vec_finite(p1):
                pygame.draw.line(target, color, p0, p1, 1)
        # Axes
        p0 = world_to_canvas((-extent, 0.0))
        p1 = world_to_canvas((extent, 0.0))
        if vec_finite(p0) and vec_finite(p1):
            pygame.draw.line(target, axis_color, p0, p1, 2)
        p0 = world_to_canvas((0.0, -extent))
        p1 = world_to_canvas((0.0, extent))
        if vec_finite(p0) and vec_finite(p1):
            pygame.draw.line(target, axis_color, p0, p1, 2)

        if not grid_debug_printed:
            left = world_to_canvas((-extent, 0.0))[0]
            right = world_to_canvas((extent, 0.0))[0]
            top = world_to_canvas((0.0, extent))[1]
            bottom = world_to_canvas((0.0, -extent))[1]
            center = world_to_canvas((0.0, 0.0))
            print(
                f"[grid_debug] extent={extent} canvas_w={canvas_w} height={height} "
                f"left_px={left:.2f} right_px={right:.2f} top_px={top:.2f} bottom_px={bottom:.2f} "
                f"center_px=({center[0]:.2f},{center[1]:.2f}) intervals={intervals}",
                flush=True,
            )
            grid_debug_printed = True

    def draw_key_legend(target: "pygame.Surface") -> None:
        lines = [
            "Keys",
            "? help",
            "q quit",
            "i info",
            "esc reset",
            "space pause/resume",
            "",
            "h hits (paused)",
            "p paths",
            "t trail dots",
            "v field on/off",
        ]
        pad = 8
        line_h = font.get_linesize()
        widths = [font.size(text)[0] for text in lines]
        box_w = max(widths) + pad * 2
        box_h = line_h * len(lines) + pad * 2
        legend = pygame.Surface((box_w, box_h), pygame.SRCALPHA).convert_alpha()
        legend.fill((255, 255, 255, 220))
        for idx, text in enumerate(lines):
            draw_text(legend, text, pad, pad + idx * line_h, color=(40, 40, 40))
        target.blit(legend, (12, 12))

    trail_marker_offsets = [
        (-1, -3), (0, -3), (1, -3),
        (-2, -2), (-1, -2), (0, -2), (1, -2), (2, -2),
        (-3, -1), (-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1), (3, -1),
        (-3, 0), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (3, 0),
        (-3, 1), (-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1), (3, 1),
        (-2, 2), (-1, 2), (0, 2), (1, 2), (2, 2),
        (-1, 3), (0, 3), (1, 3),
    ]

    def update_time_params(new_hz: int) -> None:
        nonlocal dt, shell_thickness, max_radius, emission_retention
        cfg.hz = new_hz
        dt = 1.0 / cfg.hz
        base_shell = max(field_v * dt, 0.003)
        shell_thickness_local = max(base_shell, 0.75 * min(grid_dx, grid_dy))
        shell_thickness_local = max(shell_thickness_local, 0.003)
        shell_thickness = shell_thickness_local * shell_thickness_scale
        # Max corner distance from origin (for pruning); per-emission cutoff is computed with its own origin.
        band_half = max(shell_thickness * 1.5, shell_thickness)
        max_radius = math.hypot(cfg.domain_half_extent, cfg.domain_half_extent) + band_half
        emission_retention = max_radius / field_v

    update_time_params(cfg.hz)

    def world_to_screen(p: Vec2) -> Vec2:
        extent = cfg.domain_half_extent
        if extent <= 0:
            return panel_w, 0
        sx = panel_w + ((p[0] + extent) / (2 * extent)) * canvas_w
        sy = ((p[1] + extent) / (2 * extent)) * height
        return sx, sy

    def world_to_canvas(p: Vec2) -> Vec2:
        """Like world_to_screen but with the canvas origin at (0, 0)."""
        sx, sy = world_to_screen(p)
        return sx - panel_w, sy

    def emission_max_radius(em_pos: Vec2) -> float:
        """Return the radius at which a shell centered at em_pos fully clears the domain (including band)."""
        ex, ey = em_pos
        extent = cfg.domain_half_extent
        corners = [
            (extent - ex, extent - ey),
            (extent - ex, -extent - ey),
            (-extent - ex, extent - ey),
            (-extent - ex, -extent - ey),
        ]
        max_corner = max(math.hypot(dx, dy) for dx, dy in corners)
        band_half = max(shell_thickness * 1.5, shell_thickness)
        return max_corner + band_half

    def vec_finite(p: Vec2) -> bool:
        return math.isfinite(p[0]) and math.isfinite(p[1])

    def vec_within_canvas(p: Vec2) -> bool:
        return -0.6 * width <= p[0] <= 1.6 * width and -0.6 * height <= p[1] <= 1.6 * height

    def clamp_speed(v: float) -> float:
        return max(0.0, min(v, 100.0))

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
        if radius <= 0 or radius > emission_max_radius(em.pos):
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

    def apply_static_coulomb(static_positions: Dict[str, Vec2] | None) -> None:
        if not cfg.seed_static_field or not static_positions:
            return
        field_grid[:] = 0.0
        for name, pos in static_positions.items():
            state = state_lookup.get(name)
            if state is None:
                continue
            px, py = pos
            dx = xx - px
            dy = yy - py
            dist2 = dx * dx + dy * dy + 1e-9
            contrib = state.polarity / dist2
            field_grid[:] += contrib

    def rebuild_field_surface(current_time: float, update_last_radius: bool = False, static_positions: Dict[str, Vec2] | None = None) -> None:
        nonlocal field_surface
        field_grid[:] = 0.0
        apply_static_coulomb(static_positions)
        for em in emissions:
            tau = current_time - em.time
            if tau <= 0:
                if update_last_radius:
                    em.last_radius = 0.0
                continue
            radius = field_v * tau
            if radius > emission_max_radius(em.pos):
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
            max_r = emission_max_radius(em.pos)
            if radius > max_r:
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
            if radius > emission_max_radius(em.pos):
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
            if radius > emission_max_radius(em.pos):
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
        recent_hits.extend(detect_hits(current_time, positions, allow_self=True))

    def seed_static_emissions() -> None:
        """Prefill emission history to approximate a long-running static field."""
        if not states:
            return
        steps = 64
        span = emission_retention
        if span <= 0 or steps <= 0:
            return
        for state in states:
            base_pos = state.pos
            for i in range(steps):
                t_emit = -span + (span * i / max(1, steps - 1))
                emissions.append(Emission(time=t_emit, pos=base_pos, emitter=state.name, polarity=state.polarity))

    def reset_state(
        keep_trace: bool = False,
        keep_offset: bool = False,
        keep_field_visible: bool = False,
    ) -> None:
        nonlocal emissions, field_grid, frame_idx, speed_mult, field_surface, positions, field_visible, path_traces, sim_clock_start, sim_clock_elapsed, caption_dirty
        nonlocal states, state_lookup, phase_indices, num_pos_arch, num_neg_arch
        speed_mult = clamp_speed(cfg.speed_multiplier)
        if not keep_offset:
            states, path_traces = build_states_from_specs()
            state_lookup = {s.name: s for s in states}
            phase_indices = {s.name: None for s in states}
            num_pos_arch = sum(1 for s in states if s.polarity > 0)
            num_neg_arch = sum(1 for s in states if s.polarity < 0)
        else:
            for state in states:
                state.path_offset = state.initial_path_offset
                if state.mover_type == "analytic":
                    state.param = state.path_offset
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
        caption_dirty = True
        if cfg.seed_static_field:
            seed_static_emissions()
            # Build a static field snapshot from current positions.
            rebuild_field_surface(0.0, static_positions=positions)
            field_surface = make_field_surface()
            if field_visible and field_alg == "gpu":
                if gpu_display:
                    gpu_update_field_texture(0.0)
                else:
                    gpu_rebuild_field_surface(0.0)
        else:
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
            seeded_static = cfg.seed_static_field and (frame_idx <= 1)
            fs = field_surf if field_surf is not None else field_surface
            if seeded_static and fs is not None:
                gpu_draw_surface(fs, panel_w, 0, "field_rgb")
            elif field_alg == "gpu":
                ctx.viewport = (panel_w, 0, canvas_w, height)
                gpu_present_field()
                ctx.viewport = (0, 0, view_w, view_h)
            elif fs is not None:
                gpu_draw_surface(fs, panel_w, 0, "field_rgb")

        overlay_has_content = (
            (ui_overlay_visible and (path_trail_visible or architrinos_visible))
            or show_hit_overlays
            or cfg.grid_visible
            or legend_visible
        )
        overlay_visible = overlay_has_content
        if overlay_visible:
            geometry_layer = pygame.Surface((canvas_w, height), pygame.SRCALPHA).convert_alpha()
            if cfg.grid_visible:
                draw_grid(geometry_layer)
            if legend_visible:
                draw_key_legend(geometry_layer)
            if ui_overlay_visible and path_trail_visible:
                need_redraw_traces = paused or (frame_idx - trace_layer_last_update >= trace_draw_stride)
                if need_redraw_traces:
                    trace_layer.fill((0, 0, 0, 0))
                    for name, trace in path_traces.items():
                        if len(trace) < 2:
                            continue
                        # Use softened arch-specific color for visibility.
                        arch_obj = state_lookup.get(name)
                        if arch_obj and arch_obj.polarity > 0:
                            base_color = (255, 160, 200)  # light pink for positive
                        elif arch_obj and arch_obj.polarity < 0:
                            base_color = (160, 200, 255)  # light blue for negative
                        else:
                            base_color = PURE_WHITE
                        pts = [(int(world_to_canvas(pt)[0]), int(world_to_canvas(pt)[1])) for pt in trace]
                        n = len(pts)
                        if n < 2:
                            continue
                        max_segments = 24
                        marker_step = max(12, n // max_segments)
                        def inv_cube_weight(idx: int, total: int, strength: float = 2.5) -> float:
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
                                marker_rgb = arch_obj.color if arch_obj is not None else base_color
                                fill_color = (*marker_rgb, alpha)
                                px = pts[i][0]
                                py = pts[i][1]
                                try:
                                    for dx, dy in trail_marker_offsets:
                                        x = px + dx
                                        y = py + dy
                                        if 0 <= x < canvas_w and 0 <= y < height:
                                            trace_layer.set_at((x, y), fill_color)
                                except Exception:
                                    pass
                    trace_layer_last_update = frame_idx
                geometry_layer.blit(trace_layer, (0, 0))

            if show_hit_overlays:
                for h in hits:
                    start = world_to_canvas(h.emit_pos)
                    end = world_to_canvas(positions[h.receiver])
                    emitter_arch = state_lookup.get(h.emitter)
                    line_color = emitter_arch.color if emitter_arch else PURE_WHITE
                    gfxdraw.line(geometry_layer, int(start[0]), int(start[1]), int(end[0]), int(end[1]), line_color)
                    gfxdraw.line(geometry_layer, int(start[0]), int(start[1] + 1), int(end[0]), int(end[1] + 1), line_color)
                    dx = end[0] - start[0]
                    dy = end[1] - start[1]
                    dist = math.hypot(dx, dy)
                    if dist > 1e-6:
                        inv = 1.0 / dist
                        dir_x = dx * inv
                        dir_y = dy * inv
                        nx = -dir_y
                        ny = dir_x
                        tip_offset = -7.0
                        arrow_len = 6.0
                        arrow_half = 2.0
                        tip_x = end[0] + dir_x * tip_offset
                        tip_y = end[1] + dir_y * tip_offset
                        base_x = tip_x - dir_x * arrow_len
                        base_y = tip_y - dir_y * arrow_len
                        left_x = base_x + nx * arrow_half
                        left_y = base_y + ny * arrow_half
                        right_x = base_x - nx * arrow_half
                        right_y = base_y - ny * arrow_half
                        gfxdraw.filled_trigon(
                            geometry_layer,
                            int(tip_x),
                            int(tip_y),
                            int(left_x),
                            int(left_y),
                            int(right_x),
                            int(right_y),
                            line_color,
                        )

            particle_layer = pygame.Surface((canvas_w, height), pygame.SRCALPHA).convert_alpha()
            if show_hit_overlays:
                for h in hits:
                    start = world_to_canvas(h.emit_pos)
                    emitter_arch = state_lookup.get(h.emitter)
                    marker_color = emitter_arch.color if emitter_arch else PURE_WHITE
                    px = int(round(start[0]))
                    py = int(round(start[1]))
                    for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
                        particle_layer.set_at((px + dx, py + dy), marker_color)

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
            (ui_overlay_visible and (path_trail_visible or architrinos_visible))
            or show_hit_overlays
            or cfg.grid_visible
            or legend_visible
        )
        overlay_visible = overlay_has_content
        if overlay_visible:
            geometry_layer = pygame.Surface((canvas_w, height), pygame.SRCALPHA).convert_alpha()
            if cfg.grid_visible:
                draw_grid(geometry_layer)
            if legend_visible:
                draw_key_legend(geometry_layer)
            if ui_overlay_visible and path_trail_visible:
                need_redraw_traces = paused or (frame_idx - trace_layer_last_update >= trace_draw_stride)
                if need_redraw_traces:
                    trace_layer.fill((0, 0, 0, 0))
                    for name, trace in path_traces.items():
                        if len(trace) < 2:
                            continue
                        arch_obj = state_lookup.get(name)
                        if arch_obj and arch_obj.polarity > 0:
                            base_color = (255, 160, 200)  # light pink for positive
                        elif arch_obj and arch_obj.polarity < 0:
                            base_color = (160, 200, 255)  # light blue for negative
                        else:
                            base_color = PURE_WHITE
                        pts = [(int(world_to_canvas(pt)[0]), int(world_to_canvas(pt)[1])) for pt in trace]
                        n = len(pts)
                        if n < 2:
                            continue
                        max_segments = 24
                        marker_step = max(12, n // max_segments)
                        def inv_cube_weight(idx: int, total: int, strength: float = 2.5) -> float:
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
                                marker_rgb = arch_obj.color if arch_obj is not None else base_color
                                fill_color = (*marker_rgb, alpha)
                                px = pts[i][0]
                                py = pts[i][1]
                                try:
                                    for dx, dy in trail_marker_offsets:
                                        x = px + dx
                                        y = py + dy
                                        if 0 <= x < canvas_w and 0 <= y < height:
                                            trace_layer.set_at((x, y), fill_color)
                                except Exception:
                                    pass
                    trace_layer_last_update = frame_idx
                geometry_layer.blit(trace_layer, (0, 0))

            if show_hit_overlays:
                for h in hits:
                    start = world_to_canvas(h.emit_pos)
                    end = world_to_canvas(positions[h.receiver])
                    emitter_arch = state_lookup.get(h.emitter)
                    line_color = emitter_arch.color if emitter_arch else PURE_WHITE
                    # Thicker line by drawing twice with slight offsets
                    gfxdraw.line(geometry_layer, int(start[0]), int(start[1]), int(end[0]), int(end[1]), line_color)
                    gfxdraw.line(geometry_layer, int(start[0]), int(start[1] + 1), int(end[0]), int(end[1] + 1), line_color)
                    dx = end[0] - start[0]
                    dy = end[1] - start[1]
                    dist = math.hypot(dx, dy)
                    if dist > 1e-6:
                        inv = 1.0 / dist
                        dir_x = dx * inv
                        dir_y = dy * inv
                        nx = -dir_y
                        ny = dir_x
                        tip_offset = -7.0
                        arrow_len = 6.0
                        arrow_half = 2.0
                        tip_x = end[0] + dir_x * tip_offset
                        tip_y = end[1] + dir_y * tip_offset
                        base_x = tip_x - dir_x * arrow_len
                        base_y = tip_y - dir_y * arrow_len
                        left_x = base_x + nx * arrow_half
                        left_y = base_y + ny * arrow_half
                        right_x = base_x - nx * arrow_half
                        right_y = base_y - ny * arrow_half
                        gfxdraw.filled_trigon(
                            geometry_layer,
                            int(tip_x),
                            int(tip_y),
                            int(left_x),
                            int(left_y),
                            int(right_x),
                            int(right_y),
                            line_color,
                        )

            particle_layer = pygame.Surface((canvas_w, height), pygame.SRCALPHA).convert_alpha()
            if show_hit_overlays:
                for h in hits:
                    start = world_to_canvas(h.emit_pos)
                    emitter_arch = state_lookup.get(h.emitter)
                    marker_color = emitter_arch.color if emitter_arch else PURE_WHITE
                    px = int(round(start[0]))
                    py = int(round(start[1]))
                    for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
                        particle_layer.set_at((px + dx, py + dy), marker_color)

            if ui_overlay_visible and architrinos_visible:
                for name, pos in positions.items():
                    arch = state_lookup.get(name)
                    if arch is None:
                        continue
                    pos_canvas = world_to_canvas(pos)
                    gfxdraw.filled_circle(particle_layer, int(pos_canvas[0]), int(pos_canvas[1]), 6, arch.color)

            screen.blit(geometry_layer, (panel_w, 0))
            screen.blit(particle_layer, (panel_w, 0))

        if not offline:
            pygame.display.flip()

    def active_phase_for(name: str, time_t: float) -> dict | None:
        plan = phase_plans.get(name)
        if not plan:
            return None
        for idx, ph in enumerate(plan):
            if ph.get("end") is None or time_t < ph["end"]:
                return ph, idx
        return plan[-1], len(plan) - 1

    def analytic_pos_at(state: ArchitrinoState, path_spec: PathSpec, param: float, env: MoverEnv) -> Vec2:
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

    def apply_phase_transition(state: ArchitrinoState, phase_cfg: dict | None, time_t: float, env: MoverEnv) -> None:
        """Apply mover/path/velocity changes when entering a new phase."""
        if phase_cfg is None:
            state.speed_mult_override = None
            return
        prev_mover = state.mover_type
        prev_path = state.path_name
        prev_phase = state.phase
        prev_offset = state.path_offset
        prev_radial = state.radial_scale
        prev_speed_mult = state.speed_mult_override if state.speed_mult_override is not None else env.speed_mult
        mover_override = phase_cfg.get("mover")
        path_override = phase_cfg.get("path")
        vel_override = phase_cfg.get("velocity")
        speed_override = phase_cfg.get("speed_multiplier")

        if speed_override is not None:
            state.speed_mult_override = speed_override
        else:
            state.speed_mult_override = None

        def compute_heading_sign(path: PathSpec, offset_val: float, heading_deg_val: float) -> float:
            try:
                return tangent_sign_for_heading(path, offset_val + state.phase, heading_deg_val)
            except Exception:
                return 1.0

        # Velocity override vector (for physics or tracking)
        if vel_override is not None:
            v_speed = vel_override.get("speed", 0.0)
            v_heading = vel_override.get("heading_deg", 0.0)
            v_speed = _coerce_float(v_speed, "phase.velocity.speed")
            v_heading = _coerce_float(v_heading, "phase.velocity.heading_deg")
            heading_rad = math.radians(v_heading)
            state.vel = (v_speed * math.cos(heading_rad), -v_speed * math.sin(heading_rad))

        if mover_override is not None:
            mover_override = mover_override.lower()
            if mover_override not in {"analytic", "physics"}:
                raise ValueError("phase.mover must be 'analytic' or 'physics'.")

        if path_override is not None and not isinstance(path_override, str):
            raise ValueError("phase.path must be a string if provided.")

        # Handle mover/path transitions.
        if mover_override == "physics" or (mover_override is None and state.mover_type == "physics"):
            # Switch to physics; keep current pos, allow optional velocity override.
            state.mover_type = "physics"
            state.path_name = None
            # Preserve analytic momentum when switching to physics without explicit velocity override.
            if vel_override is None and prev_mover == "analytic" and prev_path in paths:
                path_spec = paths[prev_path]
                param = state.param
                eps = 1e-3
                p_fwd = analytic_pos_at(state, path_spec, param + eps, env)
                p_back = analytic_pos_at(state, path_spec, param - eps, env)
                tan_x = (p_fwd[0] - p_back[0]) / (2 * eps)
                tan_y = (p_fwd[1] - p_back[1]) / (2 * eps)
                tan_x *= prev_radial
                tan_y *= prev_radial
                tan_mag = math.hypot(tan_x, tan_y)
                if tan_mag > 1e-9:
                    tan_x /= tan_mag
                    tan_y /= tan_mag
                    linear_speed = state.base_speed * prev_speed_mult
                    state.vel = (tan_x * linear_speed, tan_y * linear_speed)
                    state.initial_vel = state.vel
        elif mover_override == "analytic" or (mover_override is None and state.mover_type == "analytic" and path_override):
            # Switch or retarget analytic path.
            target_path_name = path_override or state.path_name
            if target_path_name is None or target_path_name not in paths:
                raise ValueError(f"phase.path '{target_path_name}' is not a known path.")
            target_path = paths[target_path_name]
            state.mover_type = "analytic"
            state.path_name = target_path_name
            # Recompute phase/offset to place current position on the target path.
            phase_val, offset_val = default_phase_and_offset(target_path_name, state.pos, target_path.decay)
            state.phase = phase_val
            state.path_offset = offset_val
            state.param = offset_val
            # Adjust radial scale to keep radius consistent.
            sample_x, sample_y = analytic_pos_at(state, target_path, offset_val, env)
            sample_r = math.hypot(sample_x, sample_y)
            current_r = math.hypot(*state.pos)
            state.radial_scale = current_r / sample_r if sample_r > 1e-9 else 1.0
            # Optional heading sign if we have a velocity override.
            if vel_override is not None:
                heading_deg = _coerce_float(vel_override.get("heading_deg", 0.0), "phase.velocity.heading_deg")
                sign = compute_heading_sign(target_path, offset_val, heading_deg)
                state.base_speed = abs(state.base_speed) * sign
        # If mover type remains the same and no path override, nothing else to do.

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
            max_force=cfg.max_force,
        )
        pos: Dict[str, Vec2] = {}
        frozen_now.clear()
        for state in states:
            phase_cfg_idx = active_phase_for(state.name, time_t)
            phase_cfg = phase_cfg_idx[0] if phase_cfg_idx else None
            phase_idx = phase_cfg_idx[1] if phase_cfg_idx else None
            current_idx = phase_indices.get(state.name)
            if phase_idx is not None and phase_idx != current_idx:
                apply_phase_transition(state, phase_cfg, time_t, env)
                phase_indices[state.name] = phase_idx
            if phase_cfg:
                mode = phase_cfg.get("mode", "move")
                if mode == "frozen":
                    state.speed_mult_override = 0.0
                    if state.mover_type == "physics":
                        if phase_cfg.get("velocity") is not None:
                            state.vel = phase_cfg["velocity"]
                        else:
                            state.vel = (0.0, 0.0)
                    frozen_now.add(state.name)
                else:
                    sm = phase_cfg.get("speed_multiplier")
                    state.speed_mult_override = sm
                    if state.mover_type == "physics" and phase_cfg.get("velocity") is not None:
                        state.vel = phase_cfg["velocity"]
                    elif state.mover_type == "physics" and phase_cfg.get("velocity") is None and state.vel == (0.0, 0.0):
                        # Restore base velocity when exiting a frozen phase without an explicit override.
                        state.vel = state.initial_vel
            else:
                state.speed_mult_override = None

        for state in states:
            path_spec = None
            if state.path_name is not None:
                path_spec = paths.get(state.path_name)
            if state.mover_type == "analytic" and path_spec is None:
                continue
            mover = movers.get(state.mover_type, movers["analytic"])
            if state.name in frozen_now:
                pos[state.name] = state.pos
            else:
                pos[state.name] = mover.step(state, env, path_spec if path_spec is not None else paths.get("unit_circle"))
        return pos

    def prune_emissions(current_time: float) -> None:
        """Drop emissions whose rings are entirely off-domain, per-emitter."""
        nonlocal emissions
        if not emissions:
            return
        if field_alg != "cpu_incr":
            emissions = [
                em
                for em in emissions
                if current_time - em.time <= emission_max_radius(em.pos) / field_v
            ]
            return
        kept: List[Emission] = []
        for em in emissions:
            max_age = emission_max_radius(em.pos) / field_v
            if current_time - em.time > max_age:
                if em.last_radius > 0:
                    apply_shell(em, em.last_radius, weight_scale=-1.0)
                continue
            kept.append(em)
        emissions = kept

    reset_state()
    log_state("startup")
    render_frame(positions, list(recent_hits))

    pygame.key.set_repeat(200, 50)

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_reason = exit_reason or "user"
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        hit_overlay_enabled = False
                        show_hit_overlays = False
                        reset_state(keep_field_visible=True)
                        paused = True
                        log_state("key_escape_reset")
                    elif event.key == pygame.K_q:
                        exit_reason = exit_reason or "user"
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
                    elif event.key == pygame.K_i:
                        log_state("key_i_info")
                    elif event.key == pygame.K_t:
                        path_trail_markers_visible = not path_trail_markers_visible
                        caption_dirty = True
                        log_state("key_t_trail_markers_toggle")
                    elif event.key == pygame.K_p:
                        path_trail_visible = not path_trail_visible
                        caption_dirty = True
                        log_state("key_p_path_trail_toggle")
                    elif getattr(event, "unicode", "") == "?":
                        legend_visible = not legend_visible
                        log_state("key_question_legend_toggle")
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
                        max_vel=compute_max_velocity(frame_idx * dt),
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
                # Drop movers that exit the padded canvas bounds; keep sim running.
                removed = set()
                for name, pos in list(positions.items()):
                    if not vec_finite(pos):
                        removed.add(name)
                        continue
                    pos_canvas = world_to_canvas(pos)
                    if not vec_finite(pos_canvas) or not vec_within_canvas(pos_canvas):
                        removed.add(name)
                if removed:
                    for name in removed:
                        positions.pop(name, None)
                        path_traces.pop(name, None)
                        state_lookup.pop(name, None)
                    states[:] = [s for s in states if s.name not in removed]
                    if emissions:
                        emissions = [em for em in emissions if em.emitter not in removed]
                    if not states:
                        exit_reason = exit_reason or "complete"
                        running = False
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
                allow_self = True
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
                    exit_reason = exit_reason or "complete"
                    running = False
                    break

            frame_idx = sim_idx - 1
            if offline and target_frames is not None and captured_frames >= target_frames:
                exit_reason = exit_reason or "complete"
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
                exit_reason = exit_reason or "complete"
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
            max_vel = compute_max_velocity(current_time)
            maybe_update_caption(
                paused_flag=paused,
                frame_number=frame_idx + 1,
                elapsed_s=current_time if not paused else sim_clock_elapsed,
                fps=fps_val,
                max_vel=max_vel,
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
                    exit_reason = exit_reason or "complete"
                    running = False
                    continue
    except KeyboardInterrupt:
        exit_reason = exit_reason or "user"
        running = False
    finally:
        log_state("exit")
        if not offline and exit_reason in {"complete", "fault"}:
            # Keep the final frame on screen until user closes the window.
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_q, pygame.K_ESCAPE, pygame.K_SPACE):
                            waiting = False
                render_frame(positions, list(recent_hits))
                clock.tick(30)
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
