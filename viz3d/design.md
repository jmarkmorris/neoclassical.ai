# viz3d Design Notes

## Goals
- Multi-scale 3D visualization from cosmic structures down to architrino assemblies.
- Drill-down navigation with log-scale zoom and focus on selected parts.
- Analytic path specification for orbits and assemblies.
- Cross-platform rendering with MP4 export (desktop/mobile).
- Glyph sizing independent of camera distance; zoom scaling is allowed with clamps.

## Scope and technology
- Separate app from sim2; no retarded-field shading.
- Default rendering: orthographic camera.
- Candidate stacks: WebGL (three.js) or Godot.

## Scale model and navigation
- Use a log-scale parameter `s` to drive zoom, with total exponent range `-60..60`.
- Continuous zoom across macro scales; non-selected regions drift toward edges as focus shifts.
- Scale indicator shows a range (for example `10^15-10^18` or `15-18` if space is tight).
- Per-node size encoding uses author-specified exponent ranges mapped to a compressed screen-scale curve (sqrt or smoothstep).

## Object ladder (spherical glyphs)
- Universe context.
- Global set of galaxy clusters.
- Superclusters.
- Galaxy clusters (moving around each other).
- Focused supercluster -> focused cluster -> galaxy.
- Galaxy internals: central black hole, stellar populations, star clusters, nebulae, solar systems, neutron stars, black holes.
- Solar system: star, planets, moons, comets, asteroids.
- Molecules -> atoms -> nucleons (protons, neutrons) -> standard model particles -> architrino assemblies.

## Top-level objects by distance scale (log10 meters)
- 26 to 27: observable universe (context).
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
- -18 and smaller: standard model particles (pointlike).
- Below this: architrino assemblies (conceptual substructure).
- Ranges are approximate and should be configurable per scene.

## Analytic path primitives
- `orbit`: `center`, `radius`, `plane` (theta/phi or normal+up), `phase`, `speed`.
- `precession` (optional for orbit): `axis`, `rate`, `show_axis`.
- `fixed`: constant position with optional jitter.
- `spiral`: optional extension.

## Assembly templates
- `binary`: one positrino + one electrino with opposite phase offsets.
- `fermion`: 12 architrinos arranged as multiple binaries in specified planes.
- `photon`: 12 architrinos arranged as multiple binaries with phase offsets.
- Expansion should be deterministic and parameterized.

## JSON schema sketch
- `scene`: name, units, time step, scale bands.
- `camera`: type, position, target, up, zoom.
- `assemblies`: list of template instances with parameters.
- `architrinos`: explicit list for overrides or manual scenes.
- `render`: fps, duration, resolution, aspect, output.

## Glyphs, labels, and overlays
- Architrino glyphs scale with zoom; clamp to min/max pixels.
- Labels are toggleable and decluttered; screen-space sizing.
- Swipe-driven info panels show counts and metadata.

## Narrative export
- Scripted navigation paths (sequence of zoom and focus actions) for smooth MP4 output.
- Export presets for desktop (16:9) and mobile (9:16).
