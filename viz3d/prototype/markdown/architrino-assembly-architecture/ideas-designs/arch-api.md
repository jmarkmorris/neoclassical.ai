# Architrino Assembly Animation API

Goal
- Define a small, general-purpose scene API for recursive assembly animations.
- Keep it renderer-agnostic, but align with the existing Node.js viz stack.
- Favor simple, composable primitives over heavy simulation.

Scope (v0)
- Declarative scene spec (JS/TS + JSON/YAML compatible).
- Minimal operations: path, orbit, spin, group velocity, charges, precession, formulas.
- Recursive scene language: a scene can contain nested scenes, and scenes can be animated by paths.
- Explicit time, units, and validation rules for canonical JSON output.

Core idea
- A path is a first-class object that can come from multiple sources.
- Sub-scenes attach to paths and those paths can be visualized with traces.
- Likewise the next level of subscenes or architrinos follow a path.
- Viewport/zoom becomes an important concept.

Absolute vs relative paths (repeating frames)
- A path is defined in a frame. The frame can be absolute (world) or relative to a moving anchor.
- If a path repeats, the repeat happens in its local frame, then the frame is composed into absolute space.
- This lets an orbit be a local repeating path while the parent frame moves through absolute space-time.

FrameSpec (draft)
- `space`: "absolute" | "relative"
- `relativeTo`: anchor or scene id (required when space == "relative")
- `repeat`: optional RepeatSpec to loop the local path
- Note: FrameSpec defines the reference frame only. Use TransformSpec for pos/rot/scale.

TransformSpec (draft)
- `position`: [x, y, z]
- `rotation`: [rx, ry, rz] (degrees)
- `scale`: [sx, sy, sz] or scalar

AnchorSpec (draft)
- `id`: unique anchor id
- `kind`: "point" | "axis" | "com"
- `target`: scene id or group id
- `offset`: optional local offset or axis vector

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
  - Reference must be explicit: parent scene, named anchor, or a computed COM.

PathSpec (draft)
- `kind`: "simulated" | "function" | "group"
- `frame`: FrameSpec (absolute or relative, with optional repeat)
- `sampler`: optional SamplerSpec
- `style`: optional StyleSpec
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
  - `center`: scene id or anchor id
  - `groupId`: assembly/group reference
  - `mode`: "com" | "centroid" | "anchor"

StyleSpec (draft)
- `color`: hex or named
- `opacity`: 0..1
- `lineWidth`: number
- `glow`: optional intensity
- `trace`: { length, density, fade }
- `lod`: { preview, final }
- `shading`: optional ShadingSpec

SamplerSpec (draft)
- `rate`: samples per second
- `adaptive`: boolean
- `maxPoints`: cap for traces

ShadingSpec (optional)
- `mode`: "flat" | "gradient" | "volume" | "density"
- `source`: "charge" | "path" | "custom"
- `intensity`: 0..1
- `ramp`: color ramp id or list

FrequencyInteractionSpec (optional)
- `targets`: ["phase", "precession", "charge", "path"]
- `waves`: [{ freq, amp, phase, waveform }]
- `coupling`: "additive" | "multiplicative" | "envelope"

SceneSpec (draft)
- `schemaVersion`: required at root (e.g., "0.1.0")
- `name`: unique id
- `frame`: local frame reference (FrameSpec)
- `transform`: local transform (TransformSpec)
- `time`: optional local time override (TimeSpec)
- `units`: optional units override (UnitsSpec, typically root only)
- `path`: PathSpec or OrbitSpec
- `children`: nested scenes
- `interactions`: optional InteractionSpec[] (typically root)
- `transfers`: optional TransferSpec[] (typically root)
- `style`: render style (StyleSpec)
- `charges`: personality charge specs
- `frequencies`: optional FrequencyInteractionSpec
- `annotations`: formulas, labels, debug

TimeSpec (draft)
- `timeBase`: "seconds" | "normalized"
- `playbackRate`: scalar
- `start`: start time
- `end`: end time
- `loop`: boolean
- Note: default uses real seconds; add an opt-in live clock mode only if needed.

UnitsSpec (draft)
- `length`: "scene" | "meters" | "arbitrary"
- `angle`: "degrees" | "radians"
- `time`: "seconds" | "normalized"
- Defaults: length="scene", angle="degrees", time="seconds"

OrbitSpec (draft)
- `origin`: anchor or scene id
- `theta`, `phi`, `r`, `phase`
- `groupVelocity`
- `repeat`: optional RepeatSpec (defaults to loop)
- `ellipse`: optional EllipseSpec
- `formatting`
  - `fadePath`
  - `ellipticalView`
  - `trace`

InteractionSpec (draft)
- `participants`: [sceneId, sceneId]
- `mode`: "couple" | "exchange" | "resonance" | "handoff"
- `trigger`: time window or condition
- `effects`: changes to path, phase, charge distribution, or bindings

TransferSpec (draft)
- `child`: scene id
- `from`: parent scene id
- `to`: parent scene id
- `at`: time or condition
- `handoffPath`: optional PathSpec for smooth transfer
- `blend`: duration for interpolation

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
  schemaVersion: "0.1.0",
  name: "architrino-demo",
  units: { length: "scene", angle: "degrees", time: "seconds" },
  time: { timeBase: "seconds", playbackRate: 1.0, loop: true },
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

Scene + reaction designer (JSON authoring)
- Purpose: a single visual editor that produces the canonical scene JSON spec for one or many assemblies.
- Must support:
  - Tree view of nested scenes (add/remove/reorder).
  - Path editor (function vs simulated vs group, with frame + repeat controls).
  - Orbit editor with ellipse settings (sceneRelativeRadius, plane angles).
  - Assembly presets (electron, proton, neutron) with editable parameters.
  - Interactions between assemblies (coupling, exchange, handoff).
  - Multi-outcome reaction design with branching outcomes and probabilities/confidence.
  - Preview panel driven by the existing viz stack.
  - JSON export/import with schema validation and versioning.
- Workflow:
  - Choose a preset or start from a blank scene.
  - Edit parameters with immediate visual feedback.
  - Save to JSON and run through the renderer CLI or browser preview.

Composer app (scene design)
- Purpose: a focused authoring app for SceneSpec + assembly presets using the primitives in this doc.
- Entry point: a small icon on the scene frame opens the composer with that scene selected.
- Primary output: canonical JSON (schemaVersioned) that round-trips into the renderer.
- Layout (MVP):
  - Left: scene tree + search + reorder.
  - Center: live preview (viz3d/three.js) with viewport controls.
  - Right: inspector (properties, path/orbit editor, style, annotations).
  - Bottom: time controls + quality toggles.
- Canvas behavior (path-first, local-frame):
  - Single 3D viewport with free camera (position + orientation) and arbitrary zoom.
  - Grid aligns to the selected path’s local frame, not world space.
  - Path is edited as an arbitrary 3D curve (spline or primitive), transformed in its frame.
  - Larger motion and context come from nesting: parent frames move, children inherit.
- Path editing (visual-first):
  - Modes: spline (freeform), line, circle, ellipse, helix/spiral.
  - Control points and tangents are edited directly in 3D with axis constraints.
  - Primitives expose exact parameters, then can be converted to spline for refinement.
  - Time mapping options: uniform by arc length, or param-based, with repeat modes.
- Camera controls (composer canvas):
  - Orbit + pan + dolly for quick framing.
  - Free-fly mode for precise placement anywhere in space.
  - Speed scaling (orders of magnitude) for large scenes.
  - Focus on selection re-centers the view on the active path.
- Modes:
  - Guided (preset-first): exposes safe parameters and hides raw fields.
  - Advanced (spec-first): full SceneSpec editor with validation + diff.
- Data flow:
  - Composer edits update a DraftSpec (normalized, but not auto-filled).
  - Export produces canonical JSON with defaults applied.
  - Renderer never guesses; composer is responsible for explicit values.

PathSpec examples (draft, 3D paths)
- Spline path (function-backed):

```json
{
  "kind": "function",
  "frame": { "space": "relative", "relativeTo": "parent", "repeat": { "mode": "loop", "period": 6 } },
  "payload": {
    "fn": "spline",
    "params": {
      "points": [[0, 0, 0], [1, 0.2, 0.4], [1.8, 0.6, 0.1], [2.2, 1.0, 0.0]],
      "tension": 0.4,
      "closed": false
    },
    "domain": [0, 1]
  }
}
```

- Ellipse primitive (function-backed):

```json
{
  "kind": "function",
  "frame": { "space": "relative", "relativeTo": "parent" },
  "payload": {
    "fn": "ellipse",
    "params": {
      "center": [0, 0, 0],
      "radiusX": 1.5,
      "radiusY": 0.8,
      "normal": [0, 1, 0]
    },
    "domain": [0, 1]
  }
}
```

Composer balance decisions (how to trade off ideas)
- Simplicity vs expressiveness: default to presets + small parameter sets; unlock full spec only in Advanced.
- Live feedback vs fidelity: preview uses adaptive sampling and reduced traces; final render uses full settings.
- Overlay UI vs in-scene gizmos: overlay panels are primary; limited gizmos for transforms only.
- Explicit data vs computed helpers: allow computed COM/anchors in the editor, but export explicit anchors.
- Schema rigidity vs experimentation: strict validation on export; allow draft-only fields during editing.
- Reuse vs one-offs: presets are first-class, but any scene can be promoted to a reusable preset.
- Performance vs clarity: prefer fewer on-canvas overlays; show debug layers only when toggled.

PDG integration (optional)
- Link reaction inputs/outputs to PDG ids and metadata where relevant.
- Use PDG data to prefill masses, charges, and known decay modes.
- Keep PDG references optional so speculative assemblies can still be expressed.

Viewport and live preview
- A scene should be fully translatable, rotatable, and scalable via its frame.
- Rendering a scene in a corner is just a viewport + scale transform on the same scene graph.
- Live preview should degrade quality gracefully (sampling rate, trace density, particle counts) to stay realtime.

ViewportSpec (draft)
- `center`: [x, y, z]
- `scale`: scalar
- `camera`: { position, target, fov }
- `fit`: "contain" | "cover"

Designer UI approach comparison (priority order)

| Priority | Criterion | Overlay editor (HTML/CSS over canvas) | In-scene 3D editor (gizmos in world) |
|---|---|---|---|
| 1 | Time to MVP | Fast (reuse web UI components) | Slow (custom 3D UI + interaction) |
| 2 | Usability / clarity | High (familiar panels, forms) | Medium (cool but can be confusing) |
| 3 | Precision editing | High (numeric inputs, sliders) | Medium (gizmo drift, depth ambiguity) |
| 4 | Implementation risk | Low | High |
| 5 | Maintenance cost | Low | High |
| 6 | Performance impact | Low (UI separate from 3D) | Medium/High (more draw + hit tests) |
| 7 | Immersion / “feel” | Medium | High |
| 8 | Direct spatial manipulation | Medium (limited) | High (natural in 3D) |

Decision
- Use the overlay editor as the primary UI approach.

Nested assembly principle
- Prefer deeper nesting that mirrors the actual assembly (inner -> middle -> outer).
- Each level is a reusable scene with its own frame and path, composed into the parent.
- This reduces special cases and increases code reuse in both the renderer and the designer app.

Prototype path (designer -> JSON -> player)
- Step 1: Define canonical JSON schema and a validator/normalizer.
- Step 2: Build a minimal scene player that loads JSON and renders via viz3d/three.js.
- Step 3: Prototype the designer as a JSON-first UI with live preview and export/import.
- Step 4: Iterate on presets, interactions, and reaction outcomes.

Canonical JSON contract
- The scene designer outputs a canonical, fully-populated JSON spec.
- Canonical means:
  - `schemaVersion` is required at the root.
  - Required fields are present with defaults applied.
  - Units, scales, and time bases are explicit.
  - All references (scene ids, anchors, frames) are resolved or resolvable.
  - Versioned schema for forward compatibility.
- The renderer can derive computed values (sampling function paths, resolving COM), but should not guess missing inputs.

Validation rules (minimum)
- Unique ids for scenes and anchors.
- References must resolve (anchors, frames, group ids).
- Time ranges must be valid (start < end, positive period).
- Sampling limits respected in preview mode.

Open questions
- How should `frame` references be resolved (id, path, or implicit parent)?
- What is the default unit scale (1.0 == 1 meter or symbolic unit)?
- How should anchors be authored (manual vs computed COM) and exposed to the designer?
- Should simulated paths be cached as arrays or streamed?

Electron assembly (draft API spec)
- Electron is a nested scene with a tri-binary Noether core and six electrinos.
- Three elliptical binaries (high/med/low), squashed according to group velocity.
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
- `energy`: "high" | "med" | "low"
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
          ellipse: {
            sceneRelativeRadius: 0.4,
            eccentricity: 0.6,
            plane: { tilt: 15, azimuth: 0 },
            inPlaneRotation: 0,
          },
          formatting: { ellipticalView: true },
        }),
      },
      {
        energy: "med",
        phase: 120,
        orbit: orbit({
          r: 0.4,
          ellipse: {
            sceneRelativeRadius: 0.4,
            eccentricity: 0.6,
            plane: { tilt: 15, azimuth: 120 },
            inPlaneRotation: 120,
          },
          formatting: { ellipticalView: true },
        }),
      },
      {
        energy: "low",
        phase: 240,
        orbit: orbit({
          r: 0.4,
          ellipse: {
            sceneRelativeRadius: 0.4,
            eccentricity: 0.6,
            plane: { tilt: 15, azimuth: 240 },
            inPlaneRotation: 240,
          },
          formatting: { ellipticalView: true },
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
