# Architrino Assembly Animation API

Goal
- Define a small, general-purpose scene API for recursive assembly animations.
- Keep it renderer-agnostic, but align with the existing Node.js viz stack.
- Favor simple, composable primitives over heavy simulation.

Scope (v0)
- Declarative scene spec (JS/TS + JSON/YAML compatible).
- Minimal operations: path, orbit, spin, group velocity, charges, precession, formulas.
- Recursive scene language: a scene can contain nested scenes, and scenes can be animated by paths.

Core idea
- A path is a first-class object that can come from multiple sources.
- Sub-scenes attach to paths and those paths can be visualized with traces.
- Likewise the next level of subscenes or architrinos follow a path.
- Zoom level becomes an important concept.

Absolute vs relative paths (repeating frames)
- A path is defined in a frame. The frame can be absolute (world) or relative to a moving anchor.
- If a path repeats, the repeat happens in its local frame, then the frame is composed into absolute space.
- This lets an orbit be a local repeating path while the parent frame moves through absolute space-time.

FrameSpec (draft)
- `space`: "absolute" | "relative"
- `relativeTo`: anchor or node id (required when space == "relative")
- `repeat`: optional RepeatSpec to loop the local path

RepeatSpec (draft)
- `mode`: "loop" | "pingpong" | "clamp"
- `period`: duration per cycle
- `phase`: normalized phase offset (0..1)
- `timeScale`: optional local time scale

Path sources (generalized)
- Simulated path
  - Produced by a simulation or integration step.
  - Example: numerically integrated orbit or precession.
- Function path
  - Given by a parametric function f(t) -> (x, y, z).
  - Example: ellipses, spirals, Lissajous, etc.
- Assembly/group path
  - Represents the group motion of a sub-assembly centered on a parent reference.
  - Use when describing the center-of-momentum (COM) path of an assembly.
  - Reference must be explicit: parent node, named anchor, or a computed COM.

PathSpec (draft)
- `kind`: "simulated" | "function" | "group"
- `frame`: FrameSpec (absolute or relative, with optional repeat)
- `sampler`: optional sampling hints (rate, duration, bounds)
- `style`: visual and animation styles (trace, fade, opacity, width)
- `payload`: data specific to the path kind

PathSpec payloads
- Simulated
  - `source`: simulation id or data reference
  - `channel`: position key / attribute
  - `cache`: optional stored samples
- Function
  - `fn`: parametric function id
  - `params`: function parameters
  - `domain`: t range
- Group
  - `center`: node id or anchor id
  - `groupId`: assembly/group reference
  - `mode`: "com" | "centroid" | "anchor"

SceneSpec (draft)
- `name`: unique id
- `frame`: local transform (origin, orientation, scale)
- `path`: PathSpec or OrbitSpec
- `children`: nested scenes
- `style`: render style
- `charges`: personality charge specs
- `annotations`: formulas, labels, debug

OrbitSpec (draft)
- `origin`: anchor or node id
- `theta`, `phi`, `r`, `phase`
- `groupVelocity`
- `repeat`: optional RepeatSpec (defaults to loop)
- `formatting`
  - `fadePath`
  - `ellipticalView`
  - `trace`
  - `ellipse`: optional EllipseSpec

Operations (required)
- path
  - arc
  - use for architrino or for a group center of momentum
- relative orbit (origin, theta, phi, r, phase, group velocity)
  - architrino formatting
  - animation settings
  - orbit formatting
    - fading path
    - elliptical path (logical observer view)
  - phase can encode charge orientation
- nested orbits
- personality charges
- ability to show precession via traced or shaded volumes
- ability to show formulas and calculations

Example sketch (JS/TS)

```js
import { scene, path, orbit, charge } from "archviz";

const spec = scene({
  name: "architrino-demo",
  timeScale: 1.0,
  root: scene({
    name: "atom",
    children: [
      scene({
        name: "nucleus",
        children: [
          scene({ name: "proton", children: [/* quark scenes */] }),
          scene({ name: "neutron", children: [/* quark scenes */] }),
        ],
      }),
      scene({
        name: "electron",
        path: orbit({
          origin: "nucleus",
          theta: 0.0,
          phi: 0.0,
          r: 1.5,
          phase: 0.25,
          groupVelocity: 0.8,
          formatting: { fadePath: true, ellipticalView: true },
        }),
        charges: [charge({ kind: "personality", orientation: "phase" })],
      }),
    ],
  }),
});
```

Precession and traced volumes
- PrecessionSpec
  - `type`: "ellipsoid" | "tube" | "shell"
  - `track`: PathSpec or OrbitSpec reference
  - `render`: shaded volume or traced path
  - `style`: opacity, color ramp, density

Scene illustrator program (prototype)
- CLI: `archviz-render input_scene.js --out ./renders --quality preview`
- Inputs: JS/TS module or JSON/YAML spec.
- Outputs: browser preview or frame sequence.
- Toggles: paths, axes, labels, debug overlays.

Scene designer app (JSON authoring)
- Purpose: a visual editor that produces the canonical scene JSON spec.
- Must support:
  - Tree view of nested scenes (add/remove/reorder).
  - Path editor (function vs simulated vs group, with frame + repeat controls).
  - Orbit editor with ellipse settings (sceneRelativeRadius, plane angles).
  - Assembly presets (electron, proton, neutron) with editable parameters.
  - Preview panel driven by the existing viz stack.
  - JSON export/import with schema validation and versioning.
- Workflow:
  - Choose a preset or start from a blank scene.
  - Edit parameters with immediate visual feedback.
  - Save to JSON and run through the renderer CLI or browser preview.

Viewport and live preview
- A scene should be fully translatable, rotatable, and scalable via its frame.
- Rendering a scene in a corner is just a viewport + scale transform on the same scene graph.
- Live preview should degrade quality gracefully (sampling rate, trace density, particle counts) to stay realtime.

Nested assembly principle
- Prefer deeper nesting that mirrors the actual assembly (inner -> middle -> outer).
- Each level is a reusable scene with its own frame and path, composed into the parent.
- This reduces special cases and increases code reuse in both the renderer and the designer app.

Open questions
- How should `frame` references be resolved (id, path, or implicit parent)?
- What is the default unit scale (1.0 == 1 meter or symbolic unit)?
- Do we want a first-class `anchor` type for explicit COM references?
- Should simulated paths be cached as arrays or streamed?

Electron assembly (draft API spec)
- Electron is a nested scene with a tri-binary Noether core and six electrinos.
- Three high-energy elliptical binaries, squashed according to group velocity.
- Six electrinos bounce around axial vortexes (jiggle or tight-orbit motion).

ElectronSpec (assembly)
- `kind`: "electron"
- `groupVelocity`: vector or scalar magnitude
- `core`: NoetherCoreSpec
- `electrinos`: ElectrinoSpec[]
- `style`: optional display style

NoetherCoreSpec (tri-binary)
- `kind`: "tri-binary"
- `binaries`: BinarySpec[3]
- `layout`: phase offsets (e.g., 0, 120, 240 degrees)
- `axis`: core axis or frame reference
- `squashBy`: "groupVelocity" | number

BinarySpec (elliptical pair)
- `orbit`: OrbitSpec or PathSpec (elliptical)
- `energy`: "high"
- `phase`: phase offset for the pair
- `squash`: optional override for orbital squash

EllipseSpec (orbital ellipse)
- `sceneRelativeRadius`: scalar multiplier relative to the parent scene scale
- `semiMajor`: optional absolute value (if not using sceneRelativeRadius)
- `semiMinor`: optional absolute value
- `eccentricity`: optional; if provided, derive semiMinor from semiMajor
- `plane`
  - `tilt`: angle from parent plane (e.g., inclination)
  - `azimuth`: rotation around parent axis
- `inPlaneRotation`: ellipse rotation within its own plane (argument of periapsis)

ElectrinoSpec (axial vortex motion)
- `count`: number of electrinos (total 6)
- `vortexes`: [{ axis, count, motion }]
- `motion`:
  - `kind`: "jiggle" | "orbit"
  - `radius`: tight circle radius
  - `frequency`: local oscillation rate
  - `phase`: phase offset

Personality charge distribution (electrino/positrino)
- Allow explicit distribution patterns (e.g., 5/1, 4/2) and per-binary assignment.
- Charges can be bound to a specific binary and given a phase offset.

ChargeDistributionSpec
- `total`: total number of charges (default 6)
- `split`: { electrino: number, positrino: number }
- `assignments`: ChargeAssignmentSpec[]

ChargeAssignmentSpec
- `binary`: index 0..2 (tri-binary core) or binary id
- `polarity`: "electrino" | "positrino"
- `count`: number of charges on that binary
- `phase`: phase offset or phase list

Geometry language (tri-binary Noether core)
- Define the tri-binary core as three elliptical binaries spaced by phase.
- Each binary is an ellipse in a local plane; planes may tilt around the core axis.
- Apply an anisotropic squash derived from group velocity (e.g., scale along velocity axis).
- Allow optional precession of the binary planes (slow rotation of the ellipse normals).

Example electron sketch (spec fragment)

```js
const electron = {
  kind: "electron",
  groupVelocity: 0.8,
  core: {
    kind: "tri-binary",
    axis: "electron-axis",
    layout: [0, 120, 240],
    squashBy: "groupVelocity",
    binaries: [
      {
        energy: "high",
        phase: 0,
        orbit: orbit({
          r: 0.4,
          formatting: {
            ellipticalView: true,
            ellipse: {
              sceneRelativeRadius: 0.4,
              eccentricity: 0.6,
              plane: { tilt: 15, azimuth: 0 },
              inPlaneRotation: 0,
            },
          },
        }),
      },
      {
        energy: "med",
        phase: 120,
        orbit: orbit({
          r: 0.4,
          formatting: {
            ellipticalView: true,
            ellipse: {
              sceneRelativeRadius: 0.4,
              eccentricity: 0.6,
              plane: { tilt: 15, azimuth: 120 },
              inPlaneRotation: 120,
            },
          },
        }),
      },
      {
        energy: "low",
        phase: 240,
        orbit: orbit({
          r: 0.4,
          formatting: {
            ellipticalView: true,
            ellipse: {
              sceneRelativeRadius: 0.4,
              eccentricity: 0.6,
              plane: { tilt: 15, azimuth: 240 },
              inPlaneRotation: 240,
            },
          },
        }),
      },
    ],
  },
  electrinos: [
    {
      count: 6,
      vortexes: [
        { axis: "electron-axis", count: 3, motion: { kind: "jiggle", radius: 0.05, frequency: 6 } },
        { axis: "electron-axis", count: 3, motion: { kind: "orbit", radius: 0.08, frequency: 4 } },
      ],
    },
  ],
  chargeDistribution: {
    total: 6,
    split: { electrino: 4, positrino: 2 },
    assignments: [
      { binary: 0, polarity: "electrino", count: 2, phase: 0 },
      { binary: 1, polarity: "electrino", count: 2, phase: 120 },
      { binary: 2, polarity: "positrino", count: 2, phase: 240 },
    ],
  },
};
```
