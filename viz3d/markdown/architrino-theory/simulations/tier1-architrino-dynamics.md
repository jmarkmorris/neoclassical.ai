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
