# viz3d Design Notes

## Goals
- Multi-scale 3D visualization from cosmic structures down to architrino assemblies.
- Drill-down navigation with log-scale zoom and focus on selected parts.
- Analytic path specification for orbits and assemblies.
- Cross-platform rendering with MP4 export (desktop/mobile).
- Glyph sizing independent of camera distance; zoom scaling is allowed with clamps.
- Preserve relative scale fidelity across classical and quantum domains; keep scale transitions educational and legible.
- Convey architrino assembly architecture clearly without distorting scale relationships.

## Scope and technology
- Separate app from sim2; no retarded-field shading.
- Default rendering: orthographic camera.
- Candidate stacks: WebGL (three.js) or Godot.

## Scale model and navigation
- Use a log-scale parameter `s` to drive zoom, with total exponent range `-60..60`.
- Continuous zoom across macro scales; non-selected regions drift toward edges as focus shifts.
- Scale indicator shows a range (for example `10^15-10^18` or `15-18` if space is tight).
- Scale indicator updates continuously during zoom; 
- Per-node size encoding uses author-specified exponent ranges mapped to a compressed screen-scale curve (sqrt or smoothstep).

## Zoom mechanics (discussion)
- Define transition timing model: zoom effect without being tediously slow
- Allow per-transition overrides for duration, easing, and optional pauses.
- Specify blending rules for glyphs and labels during handoff between scales.
- Decide whether zoom in/out symmetry is required or can be asymmetric.

## Scene composition (discussion)
- Define rules for single focus object vs multiple objects at the same scale.
- Specify layout strategies for multiple objects inside a parent volume (radial, clustered, grid).
- Clarify label anchoring: pinned to glyphs vs screen-space offsets.

## Scenes (approx scale anchors)
| Anchor | Scale (log10 meters) | Notes |
| --- | --- | --- |
| Universe context | 26 to 27 | Full scene context and background |
| Cosmic web / superclusters | 24 to 26 | Regional structure |
| Galaxy clusters | 22 to 24 | Cluster scale |
| Galaxies | 20 to 22 | Focused galaxy |
| Galactic substructures | 17 to 19 | Arms, halos, star clouds |
| Solar systems | 13 to 15 | Planetary systems |
| Stars | 9 to 10 | Individual stars |
| Planets | 6 to 7 | Planet scale |
| Small bodies | 3 to 6 | Moons, asteroids, comets |
| Molecules | -9 to -6 | Molecular scale |
| Atoms | -10 to -9 | Atomic scale |
| Nucleons | -15 to -14 | Proton/neutron scale |
| Standard model particles | -18 and smaller | Pointlike representation |
| Architrino assemblies | below | Conceptual substructure |

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

## Config and sequencing (discussion)
- Define global defaults plus per-scene object lists and references.
- Describe navigation sequences explicitly (from/to, direction, duration, easing).
- Reserve optional slots for audio or narration cues aligned to the sequence.

## Tooling and run modes (discussion)
- JSON flags for config path, quality preset, output location, preview toggle.
- Provide a fast "simple mode" for quick validation vs full fidelity renders.

## Asset pipeline (discussion)
- Per-scene asset directories with naming conventions for imagery or textures.
- Supported formats and a fallback strategy when assets are missing.

## Architecture (discussion)
- Base scene class with per-scale subclasses and a scene/zoom manager.
- Separate config loading, asset loading, and scene layout from rendering.
- Define a cache/cleanup strategy for large or repeated assets.

## Execution flow (discussion)
- Load config, initialize scene registry, and execute navigation sequence.
- Update scale indicator and overlays continuously during transitions.
- Clean up or recycle resources between segments to control memory.

## Visual defaults (configurable)
- Base output: desktop and mobile format, with per-export overrides in JSON.
- Background: neutral dark tone or subtle gradient; keep high contrast for labels.
- Glyph styling: spherical glyphs with configurable stroke width and optional fill.
- Typography: Helvetica Neue font with consistent sizing for labels and indicators.

## Overlays (discussion)
- Optional metadata overlays (timestamp, scale readout, object counts).
- Toggleable debug overlays for layout bounds and scale bands.

## Glyphs, labels, and overlays
- Architrino glyphs scale with zoom; clamp to min/max pixels.
- Labels are toggleable and decluttered; screen-space sizing.
- Swipe-driven info panels show counts and metadata.

## Future enhancements (discussion)
- Branching zoom paths and user-directed exploration.
- Integration of external data sources for scale-specific content.
- Richer materials, particles, and effects once core navigation is stable.

## Narrative export
- Scripted navigation paths (sequence of zoom and focus actions) for smooth MP4 output.
- Export presets for desktop (16:9) and mobile (9:16).
