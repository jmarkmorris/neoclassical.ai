
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
