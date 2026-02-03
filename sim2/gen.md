# Scenario JSON Generator Ideas

This doc captures a design for a creative, deterministic JSON run-file generator.

## Goals

- Generate ready-to-run `json/*.json` files for sim2.
- Keep outputs reproducible via a fixed seed.
- Support creative spatial/velocity patterns without hand-editing large arrays.
- Preserve existing directives by templating from a base run file.

## Core Design

- A small generator script (example: `sim2/scripts/gen_run.py`).
- It loads a base run file (e.g., `json/sim10.json`) for directives, then replaces
  or extends the `architrinos` array.
- Accept a seed for deterministic output.

## Generator Spec (Inputs)

- Counts: `positrons`, `electrons`.
- Position distribution:
  - `uniform_square`
  - `ring`
  - `annulus`
  - `gaussian`
  - `clusters`
  - `spiral`
- Velocity distribution:
  - `uniform`
  - `log_uniform`
  - `normal`
- Heading mode:
  - `toward_origin`
  - `away_origin`
  - `random`
  - `tangent_cw` / `tangent_ccw`
- Constraints:
  - minimum separation between particles
  - exclusion radius around origin
  - max radius / bounds from `world_size` or `domain_half_extent`
- Templates per group:
  - mover (`physics` or `analytic`)
  - phases (default to `mode: move` unless overridden)
  - optional path for analytic modes

## Creativity Hooks

- Composable patterns: e.g., 60% ring + 40% clustered core.
- Symmetry options: mirror pairs across axes.
- Paired p/e variants: same position, opposite velocity (or vice versa).
- Include a `metadata.generator` block with seed/spec/timestamp in output.

## Validation Rules

- Respect bounds derived from `directives.world_size` or `directives.domain_half_extent`.
- Enforce minimum separation (retry placement up to a capped number of attempts).
- Clamp or skip points that fail constraints.

## CLI Shape (Example)

- `python scripts/gen_run.py \
  --base json/sim10.json \
  --out json/sim100.json \
  --seed 100 \
  --p 50 --e 50 \
  --pos uniform_square \
  --speed 0.01..0.2 \
  --heading toward_origin \
  --mover physics`

- Optional weighted patterns:
  - `--pattern ring:0.7,clusters:0.3 \
     --ring_radius 1.4 \
     --clusters 3 \
     --cluster_spread 0.1`

## Spec File Alternative

- Support a small JSON spec file with the same fields.
- Let CLI flags override spec fields when both are provided.

## UI Design (Generator + Preview)

Goal: a small UI to configure a generator spec and preview initial conditions on a
canvas facsimile before exporting the JSON run file.

### Layout

- Left panel: form controls for generator settings.
- Right panel: live preview canvas showing initial positions and velocity vectors.
- Footer: actions (generate, export, copy spec, reset).

### Controls

- Base run file selector (loads directives and bounds).
- Seed (integer) with "reroll" button.
- Counts: positrons, electrons.
- Position distribution:
  - type dropdown (uniform square, ring, annulus, gaussian, clusters, spiral)
  - parameters for the selected type (e.g., ring radius, annulus thickness, cluster count).
- Velocity distribution:
  - type dropdown (uniform, log-uniform, normal)
  - min/max or mean/std depending on selection.
- Heading mode:
  - toward origin, away from origin, random, tangent cw/ccw.
- Constraints:
  - min separation
  - exclusion radius at origin
  - max radius (or auto from world_size/domain_half_extent)
- Templates:
  - mover (physics or analytic)
  - phases (simple list editor or preset select)
  - path (if analytic)

### Preview Behavior

- Show the domain bounds derived from `world_size` or `domain_half_extent`.
- Render points with color by polarity (red/blue).
- Render velocity arrows scaled and clamped for readability.
- Hover or click to show a tooltip with name, speed, heading, polarity.
- Live update on any parameter change; use the same seed to keep it stable.

### Output / Export

- "Generate" updates the preview and JSON payload.
- "Export JSON" writes a new run file under `json/`.
- "Copy Spec" copies the generator spec to clipboard.
- "Copy JSON" copies the generated run file.

### Implementation Notes

- The UI can be a minimal web app that reads/writes local files via a small
  Python (or Node) backend, or run entirely in the browser with manual file save.
- The preview should re-use the same coordinate transform logic as `orbits.py`
  (world to canvas mapping) for consistency.
- Include the `metadata.generator` block in the JSON output for reproducibility
  (seed, spec, timestamp, base file).
