### Master Simulation Protocol (Absolute Frame)

1. **Coordinate Anchor**: All simulations run on a fixed Cartesian grid. `Grid[x][y][z]` represents the Euclidean Void.
2. **Clock Rate**: The simulator uses a global `Time` counter (absolute $t$). No relativistic scaling is applied to the integration step itself.
3. **Virtual Observer (VO) Interface**: Every run must instantiate an array of fixed Virtual Sensors to log $\Phi$ and $\nabla\Phi$ at absolute addresses.
4. **Noether Sea Initialization**: Standard "Vacuum" runs must pre-populate the grid with a lattice of coupled pro/anti tri-binary assemblies to simulate the medium's influence on test particles.
5. **Convergence**: Δt refinement must be accompanied by "History Resolution" refinement to ensure self-hit calculations are numerically stable.
