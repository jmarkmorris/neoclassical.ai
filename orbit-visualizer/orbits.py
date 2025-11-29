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
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple

import numpy as np

Vec2 = Tuple[float, float]


# Color constants (RGB)
PURE_RED = (255, 0, 0)
PURE_BLUE = (0, 0, 255)
PURE_PURPLE = (255, 0, 255)  # neutral (red + blue)
PURE_WHITE = (255, 255, 255)
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
class SimulationConfig:
    fps: int = 30
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


def render_live(cfg: SimulationConfig, paths: Dict[str, PathSpec], path_name: str = "unit_circle", reverse: bool = False) -> None:
    """
    Minimal PyGame renderer: draws architrinos and hit connectors.
    """
    try:
        import pygame
    except ImportError as exc:
        raise SystemExit("PyGame is required for rendering. Install with `pip install pygame`.") from exc

    if path_name not in paths:
        raise ValueError(f"Unknown path '{path_name}'. Available: {list(paths.keys())}")

    pygame.init()
    panel_w = 320
    width, height = 1400, 960
    canvas_w = width - panel_w
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Orbit Visualizer (prototype)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)

    path = paths[path_name]
    positrino = Architrino("positrino", +1, PURE_RED, 0.0, path, reverse=reverse)
    electrino = Architrino("electrino", -1, PURE_BLUE, math.pi, path, reverse=reverse)
    emissions: List[Emission] = []

    running = True
    paused = False
    frame_idx = 0
    target_stop_at_posi_start = False
    stop_reached = False
    hits_at_stop: List[Hit] = []
    dt = 1.0 / cfg.fps
    speed_mult = max(0.0, min(cfg.speed_multiplier, 100.0))
    # Enforce positive field speed
    field_v = max(cfg.field_speed, 1e-6)

    # Retain emissions while their shells are on-canvas.
    max_radius = math.sqrt(2) * cfg.domain_half_extent * 1.1
    emission_retention = max_radius / field_v
    recent_hits = deque(maxlen=20)
    seen_hits = set()
    seen_hits_queue = deque()

    def world_to_screen(p: Vec2) -> Vec2:
        scale = min(canvas_w, height) / (2 * cfg.domain_half_extent)
        sx = panel_w + canvas_w / 2 + p[0] * scale
        sy = height / 2 + p[1] * scale  # do not flip y to preserve rotation orientation
        return sx, sy

    def compute_field_surface(current_time: float, emissions: List[Emission], current_positions: Dict[str, Vec2]) -> "pygame.Surface":
        # Downsampled field grid for speed; match aspect ratio to avoid distortion.
        res = 256
        min_dim = min(canvas_w, height)
        x_extent = cfg.domain_half_extent * (canvas_w / min_dim)
        y_extent = cfg.domain_half_extent * (height / min_dim)
        xs = np.linspace(-x_extent, x_extent, res)
        ys = np.linspace(-y_extent, y_extent, res)
        xx, yy = np.meshgrid(xs, ys)

        eps = 1e-6
        net = np.zeros_like(xx, dtype=np.float64)

        shell_thickness = max(field_v * (1.5 / cfg.fps), 0.01)
        for em in emissions:
            tau = current_time - em.time
            if tau < 0:
                continue
            r = field_v * tau
            if r > max_radius:
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

        # Percentile-based normalization to avoid a flat wash; zero regions map to white.
        max_abs = np.percentile(np.abs(net), 99) if np.any(net) else 1.0
        if max_abs < 1e-9:
            max_abs = 1.0
        pos_norm = np.clip(np.maximum(net, 0.0) / max_abs, 0.0, 1.0)
        neg_norm = np.clip(np.maximum(-net, 0.0) / max_abs, 0.0, 1.0)
        # Blend toward red/blue from white; zero stays white.
        red = (255 * (1 - neg_norm)).astype(np.uint8)
        blue = (255 * (1 - pos_norm)).astype(np.uint8)
        green = (255 * (1 - np.maximum(pos_norm, neg_norm))).astype(np.uint8)
        rgb = np.stack([red, green, blue], axis=-1)
        surf = pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))
        # Use an opaque surface; no per-pixel alpha.
        surf = pygame.transform.smoothscale(surf, (canvas_w, height)).convert()
        return surf

    def draw_text(text: str, x: int, y: int, color=(255, 255, 255)) -> None:
        surf = font.render(text, True, color)
        screen.blit(surf, (x, y))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_UP:
                    speed_mult = min(100.0, speed_mult + 0.1)
                elif event.key == pygame.K_DOWN:
                    speed_mult = max(0.0, speed_mult - 0.1)
                elif event.key == pygame.K_RIGHT:
                    target_stop_at_posi_start = True
                    paused = False
                # Reset to initial state on speed change
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    emissions.clear()
                    frame_idx = 0
                    paused = False
                    target_stop_at_posi_start = False
                    stop_reached = False
                    hits_at_stop = []

        if paused:
            clock.tick(cfg.fps)
            continue

        t = frame_idx * dt
        path_t = speed_mult * t

        pos_posi = positrino.position(path_t)
        pos_elec = electrino.position(path_t)
        positions = {"positrino": pos_posi, "electrino": pos_elec}

        emissions.append(Emission(time=t, pos=pos_posi, emitter="positrino"))
        emissions.append(Emission(time=t, pos=pos_elec, emitter="electrino"))

        # Drop emissions whose shells are fully off-canvas; also prune seen_hits
        emissions = [e for e in emissions if (t - e.time) <= emission_retention]
        cutoff_time = t - emission_retention
        seen_hits_queue = deque([k for k in seen_hits_queue if k[0] >= cutoff_time], maxlen=seen_hits_queue.maxlen or 0)
        seen_hits = {(time, emitter, receiver) for (time, emitter, receiver) in seen_hits_queue}

        hits: List[Hit] = []
        radius_tol = max(field_v * dt, 0.02)
        for emission in emissions:
            tau = t - emission.time
            if tau <= 0:
                continue
            radius = field_v * tau
            for receiver_name, receiver_pos in positions.items():
                dist = l2(receiver_pos, emission.pos)
                if abs(dist - radius) <= radius_tol:
                    key = (emission.time, emission.emitter, receiver_name)
                    if key in seen_hits:
                        continue
                    seen_hits.add(key)
                    strength = 1.0 / (dist * dist) if dist > 0 else float("inf")
                    ang = angle_from_x_axis(receiver_pos)
                    if not (emission.emitter == receiver_name and speed_mult <= 1.0):
                        hit = Hit(
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
                        hits.append(hit)
                        seen_hits_queue.append(key)

        # Update recent hit log (current-frame hits only)
        recent_hits.clear()
        if hits:
            recent_hits.extend(hits)

        # Draw
        screen.fill((255, 255, 255))

        # Field overlay
        field_surface = compute_field_surface(t, emissions, positions)
        screen.blit(field_surface, (panel_w, 0))

        # Static orbit guide: unit circle as thin white line on canvas
        if path_name == "unit_circle":
            center = world_to_screen((0.0, 0.0))
            scale = min(canvas_w, height) / (2 * cfg.domain_half_extent)
            pygame.draw.circle(screen, PURE_WHITE, center, int(scale), 1)

        # Hit connectors
        for h in hits:
            start = world_to_screen(h.emit_pos)
            end = world_to_screen(positions[h.receiver])
            pygame.draw.line(screen, PURE_WHITE, start, end, 1)
            # Emitter marker in lighter color
            if h.emitter == "positrino":
                pygame.draw.circle(screen, LIGHT_RED, start, 4)
            else:
                pygame.draw.circle(screen, LIGHT_BLUE, start, 4)

        # Architrinos
        pygame.draw.circle(screen, PURE_RED, world_to_screen(pos_posi), 6)
        pygame.draw.circle(screen, PURE_BLUE, world_to_screen(pos_elec), 6)

        # UI text
        # Panel background
        pygame.draw.rect(screen, (245, 245, 245), (0, 0, panel_w, height))
        draw_text(f"t={t:.2f}s", 10, 10, color=(0, 0, 0))
        draw_text(f"fps={cfg.fps}", 10, 30, color=(0, 0, 0))
        draw_text(f"speed_mult={speed_mult:.1f}", 10, 50, color=(0, 0, 0))
        draw_text("Controls:", 10, 80, color=(0, 0, 0))
        draw_text("ESC quit, SPACE pause", 10, 100, color=(0, 0, 0))
        draw_text("UP/DOWN speed", 10, 120, color=(0, 0, 0))
        draw_text("RIGHT: run until positrino @ (1,0)", 10, 140, color=(0, 0, 0))
        draw_text("Hit table (current frame):", 10, 170, color=(0, 0, 0))
        y = 190
        max_rows = 12
        for idx, h in enumerate(list(recent_hits)[:max_rows]):
            # Angle from historical emission to receiver, measured at emission->receiver vector
            recv_now = positions.get(h.receiver, (0.0, 0.0))
            emit_to_recv = (recv_now[0] - h.emit_pos[0], recv_now[1] - h.emit_pos[1])
            hit_angle_deg = angle_deg_screen(emit_to_recv)
            color = PURE_RED if h.receiver == "positrino" else PURE_BLUE
            text = (
                f"{idx+1:02d} recv={h.receiver[0].upper()} hit_ang={hit_angle_deg:.1f}° "
                f"str={h.strength:.3f} emit={h.emitter[0].upper()}"
            )
            draw_text(text, 10, y, color=color)
            y += 18

        # Visualize angles at stop condition
        if stop_reached and hits_at_stop:
            for h in hits_at_stop:
                recv_now = positions.get(h.receiver, (0.0, 0.0))
                emit_to_recv = (recv_now[0] - h.emit_pos[0], recv_now[1] - h.emit_pos[1])
                ang_deg_disp = angle_deg_screen(emit_to_recv)
                ang_rad_screen = math.radians(ang_deg_disp)
                recv_screen = world_to_screen(recv_now)
                xaxis_proj = world_to_screen((recv_now[0], 0.0))
                pygame.draw.line(screen, (0, 0, 0), recv_screen, xaxis_proj, 2)
                # Arc indicator around receiver (clockwise angles in screen space)
                radius_px = 30
                rect = pygame.Rect(0, 0, radius_px * 2, radius_px * 2)
                rect.center = recv_screen
                arc_color = PURE_RED if h.receiver == "positrino" else PURE_BLUE
                pygame.draw.arc(screen, arc_color, rect, 0, ang_rad_screen, 2)
                # Label angle
                label = f"{ang_deg_disp:.1f}°"
                draw_text(label, int(recv_screen[0] + radius_px), int(recv_screen[1] - radius_px), color=(0, 0, 0))

        pygame.display.flip()
        clock.tick(cfg.fps)
        frame_idx += 1

        # Stop at positrino start when requested
        if target_stop_at_posi_start:
            dx = pos_posi[0] - 1.0
            dy = pos_posi[1] - 0.0
            if math.hypot(dx, dy) <= 0.02 and frame_idx > 1:
                paused = True
                target_stop_at_posi_start = False
                stop_reached = True
                hits_at_stop = list(recent_hits)

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
        radius_tol = max(field_v * dt, 0.02)  # relaxed tolerance for discrete stepping
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
    parser.add_argument("--fps", type=int, default=30, help="Frames per second (default 30).")
    parser.add_argument("--duration", type=float, default=4.0, help="Minimum duration in seconds (coverage heuristic may increase this).")
    parser.add_argument("--path", type=str, default="unit_circle", choices=list(PATH_LIBRARY.keys()), help="Trajectory name.")
    parser.add_argument("--reverse", action="store_true", help="Reverse path orientation.")
    parser.add_argument("--speed-mult", type=float, default=0.5, help="Path speed multiplier in [0, 100]; 0 => stationary.")
    parser.add_argument("--self-test", action="store_true", help="Run a quick simulation and print a summary.")
    parser.add_argument("--render", action="store_true", help="Open a PyGame window and render the live simulation.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = SimulationConfig(fps=args.fps, duration=args.duration, speed_multiplier=args.speed_mult)
    if args.render:
        render_live(cfg, PATH_LIBRARY, path_name=args.path, reverse=args.reverse)
        return

    frames = simulate(cfg, PATH_LIBRARY, path_name=args.path, reverse=args.reverse)
    if args.self_test:
        print(summarize(frames))
    else:
        print("Simulation complete.")
        print(summarize(frames, max_hits=3, max_frames=3))


if __name__ == "__main__":
    main()
