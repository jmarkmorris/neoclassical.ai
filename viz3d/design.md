# viz3d Design Notes

## Goals
- Visualize multiple architrino assembly geometries in 3D.
- Keep architrino size independent of camera distance; allow zoom scaling with clamps.
- Use analytic paths that are easy to specify (e.g., binary orbit with center + plane).
- Support assembly templates (fermion, photon) that expand into 12 architrinos.
- Render animations for desktop and mobile formats.

## Rendering approach
- Use an orthographic camera by default to guarantee constant screen size.
- If perspective is ever needed, render architrinos as screen-space billboards so size stays fixed.
- Keep the render pipeline focused on geometry + motion (no retarded field shading).

## Technology choice
- Prefer a separate app from sim2.
- Candidate stacks:
  - WebGL (three.js) for easy cross-platform playback and capture.
  - Godot for native tooling and in-editor animation preview.

## Analytic path primitives (first pass)
- `orbit`:
  - `center`: [x, y, z]
  - `radius`
  - `plane`: `theta`, `phi` (spherical orientation) or `normal` + `up`
  - `phase`
  - `speed`
- `precession` (optional, for orbiting paths):
  - `axis`: [x, y, z] or spherical angles
  - `rate`: radians per second
  - `show_axis`: bool (render axis for clarity)
- `fixed`: constant position with optional small jitter.
- `spiral`: optional extension if needed later.

## Assembly templates
- `binary`: one positrino + one electrino on an orbit with opposite phase offsets.
- `fermion`: 12 architrinos arranged as multiple binaries in specified planes.
- `photon`: 12 architrinos arranged as multiple binaries with phase offsets.
- Template expansion should be deterministic and parameterized.

## JSON schema sketch (high level)
- `scene`: name, units, time step
- `camera`: type (orthographic), position, target, up, zoom
- `assemblies`: list of template instances with parameters
- `architrinos`: optional explicit list (for overrides)
- `render`: fps, duration, resolution, aspect, output

## Output targets
- Desktop: 16:9 (e.g., 1920x1080, 3840x2160)
- Mobile: 9:16 (e.g., 1080x1920)
- Encoded as mp4 (h264) or webm as needed

## Multi-scale navigation (macro to micro)
- Support continuous zoom across macro scales (e.g., proton → quarks → architrinos).
- As focus shifts, non-selected regions should drift toward the edges and out of frame (space-game feel).
- Use a log-scale parameter `s` to drive zoom and the scale indicator.
- Display a scale range in the corner (e.g., `10^15–10^18` or just `15–18` if space is tight).
- Tie scale bands to real physical ranges where known; allow ranges to be specified per scene.
- Allow drill-in on a selected child to set focus and continue zooming.

## Hierarchical map + fanout
- Treat each scale level as a dynamic map with variable fanout (some levels branch more than others).
- Represent drillable nodes as spheres or simple glyphs that invite tap/selection.
- Allow per-node size encoding via author-specified log exponent ranges (e.g., `15-18`), mapped to a compressed display scale so everything stays visible.
- Normalize exponent ranges against the full domain `-60..60` and map to pixel radii with a compression curve (e.g., `sqrt` or `smoothstep`) to keep extremes readable.

## Initial spherical object ladder
- Universe (context sphere).
- Global set of galaxy clusters.
- Superclusters (clusters moving around each other).
- A focused supercluster.
- A focused galaxy cluster.
- A galaxy.
- Galaxy internals (as spheres): central black hole, stellar populations, star clusters, nebulae, solar systems, neutron stars, black holes.
- A solar system.
- A star with planets, moons, comets, asteroids.
- Molecules -> atoms -> protons/neutrons/electrons.
- Standard model particles.
- Architrino assemblies that compose those particles.

## Top-level objects by distance scale (log10 meters)
- 26 to 27: observable universe (context only).
- 24 to 26: cosmic web and superclusters.
- 22 to 24: galaxy clusters.
- 20 to 22: galaxies.
- 17 to 19: galactic substructures (arms, halos, star clouds).
- 13 to 15: solar systems and planetary systems.
- 9 to 10: stars.
- 6 to 7: planets.
- 3 to 6: moons, asteroids, comets.
- -9 to -6: molecules.
- -10 to -9: atoms.
- -15 to -14: nucleons (protons, neutrons).
- -18 and smaller: standard model particles, spacetime particles
- Below this: architrino assemblies (conceptual substructure).

Notes:
- Ranges are approximate and should be adjustable per scene.
- Use author-specified exponent ranges when literal sizes are not the goal.
- Visual sizes can be illustrative rather than literal; include a legend or tooltip when needed.

## Architrino glyph sizing
- Use orthographic projection so distance does not alter size.
- Allow glyphs to scale with zoom for readability.
- Zoom-driven scaling is intentional and separate from camera-distance scaling.
- Clamp glyph size in screen space (min/max pixels) to avoid vanishing or bloating.
- Optional future toggle: fixed-size glyphs vs. world-scaled-with-clamp.

## Storytelling + info panels
- Provide swipe-driven overlays to reveal context and counts.
- Example: swipe to open a table with counts (protons, neutrons, quarks, positrinos, electrinos).
- Keep overlays lightweight so they do not obscure the main scene; allow quick dismiss.
- Support scripted navigation paths (a sequence of zoom + focus actions) for smooth MP4 exports.

## Labels + annotations
- Support toggleable labels on objects and assemblies.
- Labels should be readable at multiple zoom levels; consider screen-space sizing and decluttering.
