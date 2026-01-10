### Master Simulation Protocol (Absolute Frame)

1. **Coordinate Anchor**: All simulations run on a fixed Cartesian grid. `Grid[x][y][z]` represents the Euclidean Void.
2. **Clock Rate**: The simulator uses a global `Time` counter (absolute $t$). No relativistic scaling is applied to the integration step itself.
3. **Virtual Observer (VO) Interface**: Every run must instantiate an array of fixed Virtual Sensors to log $\Phi$ and $\nabla\Phi$ at absolute addresses.
4. **Noether Sea Initialization**: Standard "Vacuum" runs must pre-populate the grid with a lattice of coupled pro/anti tri-binary assemblies to simulate the medium's influence on test particles.
5. **Convergence**: $\Delta$t refinement must be accompanied by "History Resolution" refinement to ensure self-hit calculations are numerically stable.

## Run Protocol: Absolute Frame Integration + Mandatory VO Logging

### Absolute frame rule
All simulations integrate dynamics in the absolute Euclidean frame:
- Fixed Cartesian coordinates (x,y,z) representing the Euclidean void
- Global absolute time t with step $\Delta$t
- No relativistic time dilation applied to the integration clock (proper time is derived only in post-processing)

### Void vs medium terminology (simulation-facing)
- "Void" = the coordinate container / grid indices
- "Spacetime medium" = Noether-core sea (coupled pro/anti cores) instantiated as objects/fields in the void

### Mandatory Virtual Observer (VO) grid
Every run must instantiate VO sensors:
- VO grid definition: points/worldlines, spacing, bounds, boundary conditions
- Logged channels (minimum): $\Phi$, ∇$\Phi$
- Optional: medium state variables ($\rho$_core, alignment metrics)
- Provenance tables: (receiver_id, t, emitter_id, t_emit, contribution_strength) when feasible

### Retarded-time bookkeeping requirement
When a potential wake surface intersects a VO sensor or contributes to $\Phi$(x,t), the code must:
- Solve for emission time t_emit using |x − x_emitter(t_emit)| = c_f (t − t_emit)
- Record emitter identity + t_emit (provenance logging)

### Metadata (required)
Each run must store:
- c_f, kernel parameters, $\Delta$t, integrator name/order, tolerances
- history-window/compression settings (if any)
- initial conditions seed
- version hash / commit id

### Acceptance gate
No major physical claim is accepted without:
- VO logs
- $\Delta$t convergence
- history-resolution convergence
- cross-integrator comparison (for critical results)

## Addenda (Sol)

### Virtual Observer Implementation & Grid Protocols

1. **Grid Initialization**: All simulations run on a rigid Cartesian grid representing the **Euclidean Void**. The grid is pre-loaded with a lattice of coupled Noether cores to simulate the "Vacuum."
2. **Fiducial Observer Array**: Instantiate a grid of "Virtual Sensors" at fixed $(x,y,z)$. Each records $\Phi$ and $\nabla\Phi$.
3. **Causal Time Lookup**: When a causal isochron intersects a sensor, the simulator uses the grid history to "look back" to the emitter's position at $t_{history}$.
4. **Logging Standard**: All runs must log VO channels ($\Phi$, $\nabla\Phi$, provenance tables) to allow cross-run convergence auditing.

## Addenda (Sol - supplemental)

### Absolute Observer Grid

* **Grid:** Initialize rigid Cartesian `Grid[x][y][z]` for the Void.
* **Sea Initialization:** Pre-load the grid with coupled Noether cores for "Vacuum" runs.
* **Logging:** Record $\Phi$ and $\nabla\Phi$ at fixed nodes (Virtual Observers).
* **Time:** Global step $\Delta t$ (Absolute Time).
