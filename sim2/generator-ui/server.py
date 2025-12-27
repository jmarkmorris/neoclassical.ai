#!/usr/bin/env python3
"""Minimal generator UI backend for sim2 run files."""

from __future__ import annotations

import argparse
import json
import math
import os
import random
from copy import deepcopy
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
JSON_DIR = ROOT.parent / "json"
MAX_ATTEMPTS = 20000


def safe_name(value: str) -> str:
    if not value:
        raise ValueError("Missing file name.")
    name = value.strip()
    if "/" in name or "\\" in name or ".." in name:
        raise ValueError("Invalid file name.")
    if not name.endswith(".json"):
        raise ValueError("File name must end with .json.")
    return name


def list_base_files() -> list[str]:
    if not JSON_DIR.exists():
        return []
    return sorted(p.name for p in JSON_DIR.glob("*.json"))


def load_json_file(name: str) -> dict:
    path = JSON_DIR / safe_name(name)
    if not path.is_file():
        raise FileNotFoundError(f"Base file not found: {name}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def domain_half_extent(directives: dict) -> float:
    world_size = directives.get("world_size")
    domain_half = directives.get("domain_half_extent")
    if domain_half is not None:
        return float(domain_half)
    if world_size is not None:
        return float(world_size) / 2.0
    return 2.0


def heading_from_vector(dx: float, dy: float) -> float:
    return math.degrees(math.atan2(-dy, dx))


def build_position_sampler(position: dict, extent: float, rng: random.Random):
    ptype = (position.get("type") or "uniform_square").lower()
    max_radius = position.get("max_radius")
    max_radius = float(max_radius) if max_radius not in (None, "") else None

    if ptype == "clusters":
        cluster_count = int(position.get("clusters", 3))
        cluster_radius = float(position.get("cluster_radius", extent * 0.8))
        centers = []
        for _ in range(max(1, cluster_count)):
            angle = rng.uniform(0.0, 2 * math.pi)
            r = rng.uniform(0.0, cluster_radius)
            centers.append((r * math.cos(angle), r * math.sin(angle)))
    else:
        centers = None

    def within_radius(x: float, y: float) -> bool:
        if max_radius is None:
            return True
        return math.hypot(x, y) <= max_radius

    def sample_uniform_square() -> tuple[float, float] | None:
        x = rng.uniform(-extent, extent)
        y = rng.uniform(-extent, extent)
        return (x, y) if within_radius(x, y) else None

    def sample_ring() -> tuple[float, float] | None:
        ring_radius = float(position.get("ring_radius", extent * 0.6))
        ring_thickness = float(position.get("ring_thickness", 0.0))
        r = ring_radius + rng.uniform(-ring_thickness / 2.0, ring_thickness / 2.0)
        angle = rng.uniform(0.0, 2 * math.pi)
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        if abs(x) > extent or abs(y) > extent:
            return None
        return (x, y) if within_radius(x, y) else None

    def sample_annulus() -> tuple[float, float] | None:
        inner = float(position.get("annulus_inner", extent * 0.3))
        outer = float(position.get("annulus_outer", extent * 0.9))
        if outer <= inner:
            return None
        r = math.sqrt(rng.uniform(inner * inner, outer * outer))
        angle = rng.uniform(0.0, 2 * math.pi)
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        if abs(x) > extent or abs(y) > extent:
            return None
        return (x, y) if within_radius(x, y) else None

    def sample_gaussian() -> tuple[float, float] | None:
        std = float(position.get("gaussian_std", extent * 0.3))
        x = rng.gauss(0.0, std)
        y = rng.gauss(0.0, std)
        if abs(x) > extent or abs(y) > extent:
            return None
        return (x, y) if within_radius(x, y) else None

    def sample_clusters() -> tuple[float, float] | None:
        if not centers:
            return None
        spread = float(position.get("cluster_spread", extent * 0.12))
        cx, cy = centers[rng.randrange(len(centers))]
        x = rng.gauss(cx, spread)
        y = rng.gauss(cy, spread)
        if abs(x) > extent or abs(y) > extent:
            return None
        return (x, y) if within_radius(x, y) else None

    def sample_spiral() -> tuple[float, float] | None:
        turns = float(position.get("spiral_turns", 3.0))
        spiral_radius = float(position.get("spiral_radius", extent * 0.9))
        jitter = float(position.get("spiral_jitter", 0.0))
        t = rng.uniform(0.0, 1.0)
        angle = t * turns * 2.0 * math.pi
        r = t * spiral_radius
        if jitter > 0:
            r += rng.uniform(-jitter, jitter)
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        if abs(x) > extent or abs(y) > extent:
            return None
        return (x, y) if within_radius(x, y) else None

    samplers = {
        "uniform_square": sample_uniform_square,
        "ring": sample_ring,
        "annulus": sample_annulus,
        "gaussian": sample_gaussian,
        "clusters": sample_clusters,
        "spiral": sample_spiral,
    }
    return samplers.get(ptype, sample_uniform_square)


def sample_speed(rng: random.Random, vel: dict) -> float:
    vtype = (vel.get("type") or "uniform").lower()
    vmin = float(vel.get("min", 0.01))
    vmax = float(vel.get("max", 0.2))
    if vmax < vmin:
        vmin, vmax = vmax, vmin

    if vtype == "log_uniform":
        lo = max(vmin, 1e-6)
        hi = max(vmax, lo + 1e-6)
        val = math.exp(rng.uniform(math.log(lo), math.log(hi)))
        return min(max(val, vmin), vmax)
    if vtype == "normal":
        mean = float(vel.get("mean", (vmin + vmax) * 0.5))
        std = float(vel.get("std", (vmax - vmin) * 0.2))
        for _ in range(50):
            val = rng.gauss(mean, std)
            if val >= 0:
                if vmin is not None:
                    val = max(val, vmin)
                if vmax is not None:
                    val = min(val, vmax)
                return val
        return max(vmin, 0.0)
    return rng.uniform(vmin, vmax)


def heading_for_mode(rng: random.Random, mode: str, x: float, y: float) -> float:
    mode = (mode or "toward_origin").lower()
    if mode == "random":
        return rng.uniform(-180.0, 180.0)

    if abs(x) < 1e-9 and abs(y) < 1e-9:
        return rng.uniform(-180.0, 180.0)

    if mode == "away_origin":
        return heading_from_vector(x, y)
    if mode == "tangent_cw":
        return heading_from_vector(y, -x)
    if mode == "tangent_ccw":
        return heading_from_vector(-y, x)
    return heading_from_vector(-x, -y)


def generate_architrinos(spec: dict, directives: dict) -> tuple[list[dict], list[dict], float]:
    counts = spec.get("counts", {}) or {}
    p_count = int(counts.get("p", counts.get("positrons", 0)) or 0)
    e_count = int(counts.get("e", counts.get("electrons", 0)) or 0)
    seed = spec.get("seed", 1)
    rng = random.Random(seed)

    extent = domain_half_extent(directives)
    position = spec.get("position", {}) or {}
    velocity = spec.get("velocity", {}) or {}
    heading = spec.get("heading", {}) or {}
    constraints = spec.get("constraints", {}) or {}

    min_sep = float(constraints.get("min_separation", 0.0))
    exclude_radius = float(constraints.get("exclude_radius", 0.0))
    max_attempts = MAX_ATTEMPTS

    sampler = build_position_sampler(position, extent, rng)

    template = spec.get("template", {}) or {}
    mover = template.get("mover", "physics")
    phases = template.get("phases")
    if not phases:
        phase = {"mode": "move", "mover": mover}
        if mover == "analytic" and template.get("path"):
            phase["path"] = template.get("path")
        phases = [phase]

    all_points: list[tuple[float, float]] = []
    preview: list[dict] = []
    arch: list[dict] = []

    def valid_point(x: float, y: float) -> bool:
        if exclude_radius > 0 and math.hypot(x, y) < exclude_radius:
            return False
        if min_sep > 0:
            for px, py in all_points:
                if math.hypot(x - px, y - py) < min_sep:
                    return False
        return True

    def add_particle(name: str, polarity: str) -> None:
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            pos = sampler()
            if pos is None:
                continue
            x, y = pos
            if not valid_point(x, y):
                continue
            speed = sample_speed(rng, velocity)
            heading_deg = heading_for_mode(rng, heading.get("mode"), x, y)
            all_points.append((x, y))
            preview.append(
                {
                    "name": name,
                    "polarity": polarity,
                    "x": x,
                    "y": y,
                    "speed": speed,
                    "heading_deg": heading_deg,
                }
            )
            arch.append(
                {
                    "name": name,
                    "polarity": polarity,
                    "start_pos": {"x": round(x, 6), "y": round(y, 6)},
                    "velocity": {"speed": round(speed, 6), "heading_deg": round(heading_deg, 6)},
                    "phases": deepcopy(phases),
                }
            )
            return
        raise RuntimeError("Unable to place particle within constraints.")

    for idx in range(1, p_count + 1):
        add_particle(f"p{idx}", "p")
    for idx in range(1, e_count + 1):
        add_particle(f"e{idx}", "e")

    return arch, preview, extent


class GeneratorHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/bases":
            bases = list_base_files()
            default = bases[0] if bases else None
            return self._send_json({"bases": bases, "default": default})
        if parsed.path == "/api/base":
            params = parse_qs(parsed.query)
            name = params.get("name", [None])[0]
            if not name:
                return self._send_json({"error": "Missing base name."}, HTTPStatus.BAD_REQUEST)
            try:
                payload = load_json_file(name)
            except Exception as exc:
                return self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return self._send_json({"base": payload})
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        try:
            data = json.loads(raw.decode("utf-8")) if raw else {}
        except json.JSONDecodeError:
            return self._send_json({"error": "Invalid JSON."}, HTTPStatus.BAD_REQUEST)

        if parsed.path == "/api/generate":
            base_name = data.get("base")
            try:
                if base_name:
                    base = load_json_file(base_name)
                else:
                    bases = list_base_files()
                    if not bases:
                        raise FileNotFoundError("No base run files found.")
                    base = load_json_file(bases[0])
            except Exception as exc:
                return self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            try:
                directives = base.get("directives", {})
                arch, preview, extent = generate_architrinos(data, directives)
            except Exception as exc:
                return self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

            payload = {"directives": directives, "architrinos": arch}
            meta = {
                "domain_half_extent": extent,
                "seed": data.get("seed"),
                "counts": data.get("counts"),
            }
            return self._send_json({"payload": payload, "preview": preview, "meta": meta})

        if parsed.path == "/api/save":
            name = data.get("name")
            payload = data.get("payload")
            if not isinstance(payload, dict):
                return self._send_json({"error": "Missing payload."}, HTTPStatus.BAD_REQUEST)
            try:
                filename = safe_name(name)
            except Exception as exc:
                return self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            path = JSON_DIR / filename
            try:
                with path.open("w", encoding="utf-8") as handle:
                    json.dump(payload, handle, indent=2)
                    handle.write("\n")
            except Exception as exc:
                return self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return self._send_json({"saved": filename})

        return self._send_json({"error": "Unknown endpoint."}, HTTPStatus.NOT_FOUND)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generator UI server")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    os.chdir(STATIC_DIR)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), GeneratorHandler)
    print(f"Generator UI running at http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
