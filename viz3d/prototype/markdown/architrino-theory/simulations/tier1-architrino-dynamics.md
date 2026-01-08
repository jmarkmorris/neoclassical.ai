## Tier-1 Mandatory Unit Tests (Before Self-Hit Claims)

### Provenance-resolved propagation test
Implement 1-architrino and 2-architrino setups with VO sensors arranged on a sphere/ring:
- Verify spherical wavefront propagation at c_f
- Verify correct arrival ordering and phase behavior (per kernel)
- Verify numerical stability of t_emit inversion as Δt → Δt/2
- Produce provenance tables showing correct emitter_id and emission times

### Baseline diagnostics
- Energy/momentum bookkeeping (as defined by the model) must be stable under refinement
- Cross-integrator comparison required for the above propagation test

## Addenda (Sol)

### Grid-Based History Strategy

1. **Problem**: Infinite memory cost for particle-based history in self-hit regimes.
2. **Solution**: Use the VO Grid as the history buffer. Store potential magnitude/gradient at grid nodes.
3. **Algorithm**: When an architrino requires its self-potential from $t-\Delta t$, query the **grid node** closest to where the particle *was*, rather than indexing the particle list.
4. **Deliverable**: Prove convergence of this grid-based history against analytic spherical wavefronts.

## Addenda (Sol - supplemental)

### Grid-Based History

* **Memory Strategy:** Use the fixed grid to store potential history.
* **Lookup:** Query grid nodes for history potential values (O(1) lookup) rather than querying particle history (O(N)).
* **Validation:** Verify spherical wavefront propagation and phase ordering on the grid.
