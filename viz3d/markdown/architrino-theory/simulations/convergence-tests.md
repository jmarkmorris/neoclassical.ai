## Convergence in Non-Markovian (Self-Hit) Dynamics

### Required refinements (beyond standard Δt)
1) Temporal refinement:
- Run with Δt and Δt/2; compare VO observables (Φ, ∇Φ, self-hit event rates)

2) History-resolution refinement:
- Halve history sampling interval OR increase interpolation order for emission-time inversion (t_emit)
- Require VO observables and provenance distributions to stabilize

3) Spatial refinement:
- Increase spatial resolution (particle resolution or field grid) and confirm stability of:
  - field maps
  - self-hit counts
  - binary/tri-binary stability windows

4) Cross-integrator validation:
- For key claims, run two integrators (e.g., symplectic vs RK) and compare VO outputs

### Provenance stability metric (mandatory)
For a fixed receiver point and time window, compare distributions of solved t_emit:
- Must be stable under Δt and history-resolution refinement
- Instability indicates numerical artifact in delayed interaction evaluation

### Negative control (null test)
Intentionally use a wrong history kernel / wrong c_f / wrong emission-time solver:
- Expected invariants (e.g., binary stability window, energy-flow signature) must fail
- Confirms the code is sensitive to the correct physics and not producing “numerical conspiracy”
