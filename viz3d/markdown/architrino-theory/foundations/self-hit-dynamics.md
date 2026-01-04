
### Non-Markovian Memory and the Self-Hit Condition

1. **Self-Hit Definition**: A self-hit occurs when an architrino’s current trajectory $(\mathbf{x}(t))$ intersects the expanding potential sphere emitted by itself at a prior time $t_{hist}$.
2. **Intersection Logic**: In absolute Euclidean coordinates, find $t_{hist}$ such that:
   $$|\mathbf{x}(t) - \mathbf{x}(t_{hist})| = c_f (t - t_{hist})$$
3. **The Stability Mechanism**: Self-hit provides the non-linear "push-back" force required to prevent binary collapse. It replaces the "singularities" of 1/r potential with a high-curvature constraint.
4. **Virtual Observer Diagnostics**: Simulation logs must record self-hit frequency and "provenance" (the age of the shell being hit) to distinguish stable Tri-Binary attractors from chaotic or decaying states.

## Self-Hit Detection and Logging (VO-based)

Frame self-hit as a path-history intersection problem:
- Find (t_emit, t_hit) such that:
  |x_emitter(t_hit) − x_emitter(t_emit)| = c_f (t_hit − t_emit)
  with same emitter identity

Simulation requirement:
- Use VO provenance tables to detect/count self-hit events:
  (emitter_id, t_hit, t_emit, impact_parameter, contribution_strength)

Acceptance criteria:
- Self-hit event rates and distributions must converge under:
  - Δt refinement
  - history-resolution refinement
  - integrator swap
If self-hit signatures change qualitatively under refinement, treat as numerical artifact until proven otherwise.

## Addenda (Dyna)

### Self-Hit as a Path-History Intersection in the Absolute Frame

Self‑hit is the key non‑Markovian feature of architrino dynamics. It occurs when an architrino interacts with potential it emitted earlier along its own worldline.

**Geometric condition (absolute coordinates):**

For a given architrino with trajectory \(\mathbf{x}(t)\), a self‑hit event is a pair of times \((t_\text{emit}, t_\text{hit})\) with \(t_\text{hit} > t_\text{emit}\) such that:

\[
|\mathbf{x}(t_\text{hit}) - \mathbf{x}(t_\text{emit})| = c_f (t_\text{hit} - t_\text{emit}),
\]

and the architrino is the source of the potential shell emitted at \(t_\text{emit}\).

Because the underlying coordinates and time are absolute, this condition is unambiguous:

- The virtual observer knows \(\mathbf{x}(t)\) for all \(t\) and can solve for all such pairs \((t_\text{emit}, t_\text{hit})\) along the worldline.
- No coordinate‑gauge ambiguity enters the definition.

**Dynamical role:**

- At low velocities (\(v < c_f\)), self‑hit is rare or absent; dynamics are approximately Markovian.
- As velocities approach and exceed \(c_f\), emission spheres catch up with the emitter’s future positions, generating:
  - Nonlocal feedback on its motion.
  - Effective restoring or destabilizing forces depending on configuration.
- For binary and tri‑binary assemblies, repeated self‑hit events can:
  - Prevent collapse to singularity (short‑distance repulsion),
  - Lock in stable radii and frequencies (Noether‑core formation),
  - Create new limit cycles and attractors in phase space.

**Simulation & diagnostics:**

In simulations:

- Use virtual‑observer provenance tables to record, for each self‑hit:
  - \((t_\text{emit}, \mathbf{x}(t_\text{emit}))\),
  - \((t_\text{hit}, \mathbf{x}(t_\text{hit}))\),
  - Impact parameters and force contributions.
- Check convergence of self‑hit statistics under:
  - Time step refinement,
  - History resolution refinement,
  - Different integrators.

If self‑hit signatures are numerically unstable under refinement, treat any resulting “stable structures” as artifacts until proven otherwise.
