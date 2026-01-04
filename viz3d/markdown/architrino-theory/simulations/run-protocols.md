### Master Simulation Protocol (Absolute Frame)

1. **Coordinate Anchor**: All simulations run on a fixed Cartesian grid. `Grid[x][y][z]` represents the Euclidean Void.
2. **Clock Rate**: The simulator uses a global `Time` counter (absolute $t$). No relativistic scaling is applied to the integration step itself.
3. **Virtual Observer (VO) Interface**: Every run must instantiate an array of fixed Virtual Sensors to log $\Phi$ and $\nabla\Phi$ at absolute addresses.
4. **Noether Sea Initialization**: Standard "Vacuum" runs must pre-populate the grid with a lattice of coupled pro/anti tri-binary assemblies to simulate the medium's influence on test particles.
5. **Convergence**: Δt refinement must be accompanied by "History Resolution" refinement to ensure self-hit calculations are numerically stable.

## Run Protocol: Absolute Frame Integration + Mandatory VO Logging

### Absolute frame rule
All simulations integrate dynamics in the absolute Euclidean frame:
- Fixed Cartesian coordinates (x,y,z) representing the Euclidean void
- Global absolute time t with step Δt
- No relativistic time dilation applied to the integration clock (proper time is derived only in post-processing)

### Void vs medium terminology (simulation-facing)
- "Void" = the coordinate container / grid indices
- "Spacetime medium" = Noether-core sea (coupled pro/anti cores) instantiated as objects/fields in the void

### Mandatory Virtual Observer (VO) grid
Every run must instantiate VO sensors:
- VO grid definition: points/worldlines, spacing, bounds, boundary conditions
- Logged channels (minimum): Φ, ∇Φ
- Optional: medium state variables (ρ_core, alignment metrics)
- Provenance tables: (receiver_id, t, emitter_id, t_emit, contribution_strength) when feasible

### Retarded-time bookkeeping requirement
When a potential shell intersects a VO sensor or contributes to Φ(x,t), the code must:
- Solve for emission time t_emit using |x − x_emitter(t_emit)| = c_f (t − t_emit)
- Record emitter identity + t_emit (provenance logging)

### Metadata (required)
Each run must store:
- c_f, kernel parameters, Δt, integrator name/order, tolerances
- history-window/compression settings (if any)
- initial conditions seed
- version hash / commit id

### Acceptance gate
No major physical claim is accepted without:
- VO logs
- Δt convergence
- history-resolution convergence
- cross-integrator comparison (for critical results)
