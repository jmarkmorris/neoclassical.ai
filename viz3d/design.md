# viz3d Design Notes

## Goals
- Multi-scale 3D visualization from cosmic structures down to assembly architecture.
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
- Scale indicator is embedded in each sphere label (use range or single value when space allows).
- Per-node size encoding uses author-specified exponent ranges mapped to a compressed screen-scale curve (sqrt or smoothstep).

## Zoom mechanics (discussion)
- Define transition timing model: S-curve timing (slow start, fast middle, slow end), Star Trek-like warp feel.
- Allow per-transition overrides for duration, easing, and optional pauses.
- Specify blending rules for glyphs and labels during handoff between scales.
- Decide whether zoom in/out symmetry is required or can be asymmetric.

## Scene composition (discussion)
- Define rules for single focus object vs multiple objects at the same scale.
- For each sphere, choose which other spheres appear in the same scene (e.g., solar system shows star, planets, moons).
- Specify layout strategies for multiple objects inside a parent volume (radial, clustered, grid).
- Clarify label anchoring: pinned to glyphs vs screen-space offsets.

## Scale ladder (scenes and objects)
| Scale band (log10 meters) | Scene/anchor | Representative objects and structure |
| --- | --- | --- |
| 26 to 27 | Universe context | Observable universe context and background |
| 24 to 26 | Cosmic web / superclusters | Filaments, voids, superclusters; intergalactic medium |
| 22 to 24 | Galaxy clusters | Cluster dynamics; intracluster medium; cluster mergers |
| 20 to 22 | Galaxies | Spiral, elliptical, irregular; AGN/quasars as optional focal points |
| 17 to 19 | Galactic substructures | Arms, halos, bulge, star clouds; globular/open clusters; nebulae; molecular clouds; supernova remnants |
| 13 to 15 | Solar systems | Planetary systems; asteroid belts, Kuiper belt, Oort cloud; protoplanetary disks |
| 10 to 12 | Supermassive black holes | Event horizon scale; accretion disks; jets |
| 8 to 9 | Stars | Main sequence, giants, supergiants, binaries, variable stars |
| 6 to 7 | Planets and dwarf planets | Terrestrial and gas/ice giants; major moons as subfocus |
| 5 to 6 | Moons | Major natural satellites; ring systems context |
| 4 to 7 | Compact remnants | White dwarfs, neutron stars, pulsars, magnetars, stellar-mass black holes |
| 2 to 5 | Small bodies | Asteroids, comets, cometary nuclei, Kuiper belt objects |
| -9 to -6 | Molecules | Molecular assemblies |
| -10 to -9 | Atoms | Atomic structures |
| -15 to -14 | Atomic nuclei and nucleons | Nuclei, protons, neutrons |
| -18 to -17 | Weak bosons | W/Z; weak interaction range ~1e-18 m |
| -18 to -17 | Higgs boson | Effective electroweak scale ~1e-18 m |
| -18 and smaller | Photons and gluons | Massless; render as spherical or wavelength-dependent |
| -19 and smaller | Quarks | Experimental upper bound on size ~1e-19 m; spherical in rendering |
| -19 and smaller | Charged leptons | Electron/muon/tau; upper bound ~1e-19 m; spherical in rendering |
| -19 and smaller | Neutrinos | Spherical in rendering; use same upper bound |
| -20? to ? | assembly architecture | personality charge layer |
| -20? to -36? | assembly architecture | outer Noether core binary |
| circa Planck -36 | assembly architecture | middle Noether core binary |
| scale of max curvature | assembly architecture | inner Noether core binary |
| Note | assembly scales | Vague/relative until constraints are known; keep flexible |

## Analytic path primitives
- `orbit`: `center`, `radius`, `plane` (theta/phi or normal+up), `phase`, `speed`.
- `precession` (optional for orbit): `axis`, `rate`, `show_axis`.
- `fixed`: constant position with optional jitter.
- `spiral`: optional extension.

## Assembly templates
- `binary`: one positrino + one electrino with opposite phase offsets.
- `fermion`: 12 architrinos arranged as multiple binaries in specified planes.
- `photon`: 12 architrinos arranged as multiple binaries with phase offsets.

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
- Label text includes the scale indicator inside each sphere.
- Labels are rendered inside spheres; reduce font size if needed.
- Swipe-driven info panels show counts and metadata.
- Mobile gesture screens are deferred; web/desktop first.

## Future enhancements (discussion)
- Branching zoom paths and user-directed exploration.
- Integration of external data sources for scale-specific content.
- Richer materials, particles, and effects once core navigation is stable.

## Narrative export
- Scripted navigation paths (sequence of zoom and focus actions) for smooth MP4 output.
- Export presets for desktop (16:9) and mobile (9:16).
- Defer formal narrative/export spec until core interaction flow is stable.
