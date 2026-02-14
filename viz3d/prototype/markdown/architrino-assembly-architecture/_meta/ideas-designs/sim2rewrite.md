# Viz3D ⇄ Sim2 Rewrite Plan

This document captures the integration strategy for porting the sim2 physics generator/simulator into the Viz3D web experience and retiring the Python runtime.

## High-level goals
1. Replace the Python physics loop with a JavaScript implementation that shares the Viz3D rendering pipeline (no separate backend).
2. Run the simulator on a dedicated worker/compute routine so physics updates remain deterministic and the renderer can sample the latest state without blocking.
3. Keep emissions/causal sets inside the worker/compute kernel; the main thread only renders positions, velocities, and optionally exposes diagnostics to the UI.
4. Port the generator UI into the Viz3D codebase so authors can produce new scenarios directly in the browser; generator outputs adopt the new Viz3D native scene format.

## Phase 0 – Discovery & prep
* **Audit Viz3D scene assets** (`viz3d/prototype/json/`, existing orbit/orbit nodes) to identify necessary data (positions, trails, metadata) that the new simulator must supply. Confirm desired scene format (node graph + animation metadata) and define how architrino states map to nodes/items in the scene.
* **Gather sim2 requirements** from `sim2/motion.py`/`sim2/orbits.py`/`sim2/json/*.json` so the new JS module implements the same physics (causal hits, 1/r², walker integration, phases, emit history). Note directives we no longer need.
* **Outline worker/compute architecture**: choose between Web Worker (JS) vs WebGL2 compute shader depending on future numerical need. For now assume a Worker exposes a shared `Float32Array` for positions+velocities and handles the `emissions` queue.
* **Define generator spec**: revisit `sim2/gen.md`/`generator-ui/README.md` and rewrite the spec to output Viz3D-friendly scenes (positions, velocities, optional metadata) rather than sim2 directives.

## Phase 1 – JS physics port
1. **Encapsulate sim2 logic in a module** inside `viz3d/prototype/` (e.g., `sim2/physics.js` or `sim2/worker/physicsWorker.js`). The module should expose:
   * scene loader that reads the new scene JSON and configures watcher/emissions data,
   * `step(dt)` that advances velocity/position per architrino via the 1/r² sum,
   * emission bookkeeping to publish hits to the renderer (positions, velocities, charge sign) and optionally the current causal set for debugging.
2. **Worker integration**:
   * Create a Web Worker that loads the physics module, receives serialized scenario data from the main thread, and runs a fixed-timestep loop (e.g., 1 kHz).
   * The worker should write the latest positions/velocities (and maybe wake strength) into a transferable `ArrayBuffer` (two floats per architrino plus metadata). Provide a simple handshake API for start/pause/reset.
   * The worker retains all emission history, hit detection, and `KAPPA` constant usage. The main thread only fetches the shared buffer each render frame.
3. **Main thread bridge**:
   * In `app.js`, load the worker, pass in scene data when a sim scenario is selected, and subscribe to per-entity updates. Update the three.js objects’ transforms from the buffer each frame before rendering.
   * Provide controls for pausing/resuming the worker and toggling any visualization overlays (e.g., showing wakes or the causal set info supplied by the worker).
4. **Fallback/standalone runner**: add a development switch to run the physics loop on the main thread for debugging (reuse `sim2/motion.py` logic ported to JS) in case Worker support is unavailable.

## Phase 2 – Generator port
1. **UI placement**: add a “Scenario Generator” panel in the Viz3D HUD (maybe reuse the markdown panel area). The panel exposes controls similar to `gen.md` (counts, distributions, headings, speed ranges, seeds). Keep live preview via the same three.js canvas if you can overlay the initial configuration before committing.
2. **Spec-to-JSON pipeline**: implement a JS generator that builds the new Viz3D scene JSON (with `architrinos` array or new `entities` nodes) using the chosen distributions. The generator should output the file for download (or copy-to-clipboard) so you can import it like any other scene. Optionally persist specs to `localStorage`.
3. **Reuse physics module**: run the generator preview through the same worker/physics module so the preview is faithful to the final simulation (no separate Python preview). That also lets you validate that the newly generated scene works without extra translation.
4. **Documentation updates**: replace `sim2/gen.md` and `generator-ui` docs with a section in `viz3d/prototype/README.md` describing how to use the new generator and how to author scenario files.

## Phase 3 – Integration & QA
1. **Scene selector integration**: add sim2 scenes to the Viz3D “scene list” and reuse the same loader so selecting a scenario automatically spins up the worker with the generated data.
2. **Performance testing**: stress-test with increasing architrino counts; measure worker update rate and main-thread render latency. Adjust the worker timestep or implement spatial acceleration structures (grid partitions or cell lists) if hit computations become the bottleneck.
3. **Fallbacks and debugging**: add dev charts/logging to expose worker health, number of hits per frame, and any dropped contributions. Provide a “dump hits” button that logs current causal sets for inspection.
4. **Clean-up**: once stable, remove the `sim2/` Python folder (or keep it archived for reference) and delete references from `README`s that mention the old runtime.

## Phase 4 – Deployment & docs
* Update `viz3d/prototype/README.md`, `vision` docs, and any release notes to describe the new simulator architecture and generator.
* Ensure `npm`/`yarn` build pipeline copies over worker scripts (if separate files) and `sim2` scenes.
* Add tests or manual checklists verifying the worker runs in browsers of interest and that generated scenes load correctly.
