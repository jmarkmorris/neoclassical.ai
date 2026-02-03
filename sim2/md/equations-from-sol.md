### Assumptions (sim2 Simulator)
1. Field speed \(c_f\) is constant and the simulator already supplies, for every causal hit, the emitter’s state at emission time \(t_{\text{emit}}\):  
   \(\{q_j,\mathbf{r}_j(t_{\text{emit}}),\mathbf{v}_j(t_{\text{emit}})\}\)  
   and the receiver’s current state at \(t_n\):  
   \(\{q_i,\mathbf{r}_i(t_n),\mathbf{v}_i(t_n)\}\).
2. Interaction is purely radial with magnitude \(\kappa\,q_i q_j/r_{ij}^2\) and direction from emitter-at-emission to receiver-now (history already baked into the supplied vectors).  
3. Time advance uses a simple explicit scheme over timestep \(\Delta t = t_{n+1}-t_n\). (Leapfrog or higher-order can be swapped in later.)

---

### Per-Hit Contribution (Emitter \(j\) → Receiver \(i\))

Given:
- Displacement vector at reception:  
  \(\mathbf{d}_{ij} = \mathbf{r}_i(t_n) - \mathbf{r}_j(t_{\text{emit}})\)
- Distance: \(r_{ij} = \|\mathbf{d}_{ij}\|\)
- Unit vector: \(\hat{\mathbf{d}}_{ij} = \mathbf{d}_{ij}/r_{ij}\)

Field contribution (acceleration) from this hit:
\[
\mathbf{a}_{ij}(t_n) = \kappa\,\frac{q_i q_j}{r_{ij}^2}\,\hat{\mathbf{d}}_{ij}
\]

Notes:
- Self-hits are included automatically when \(j=i\) (the provided emission state already accounts for the particle’s earlier location).  
- If desired, you can add velocity-dependent corrections later; for the sim2 engine this 1/r² radial form suffices.

---

### Superposition Over All Hits on Receiver \(i\)

Let \(\mathcal{H}_i(t_n)\) be the set of all emitters contributing causal hits to \(i\) during this timeslice (including self). Then total acceleration:
\[
\mathbf{a}_i(t_n) = \sum_{j \in \mathcal{H}_i(t_n)} \mathbf{a}_{ij}(t_n)
= \kappa \sum_{j \in \mathcal{H}_i(t_n)} \frac{q_i q_j}{r_{ij}^3}\,\mathbf{d}_{ij}
\]

(Second form folds the unit vector into the numerator.)

---

### State Update for Receiver \(i\) (Explicit Euler version)

Velocity advance:
\[
\mathbf{v}_i(t_{n+1}) = \mathbf{v}_i(t_n) + \mathbf{a}_i(t_n)\,\Delta t
\]

Position advance:
\[
\mathbf{r}_i(t_{n+1}) = \mathbf{r}_i(t_n) + \mathbf{v}_i(t_{n+1})\,\Delta t
\]

(If you prefer standard Euler‑forward for position, use \(\mathbf{v}_i(t_n)\) in the second equation. For a simple semi-implicit step that’s slightly more stable, use the updated velocity as written.)

Charge is fixed: \(q_i(t_{n+1}) = q_i(t_n)\).

---

### Summary Pseudocode

```python
for each receiver i:
    a_i = 0
    for each causal hit j -> i:
        d = r_i_now - r_j_emit
        r = norm(d)
        a_i += kappa * q_i*q_j / r**3 * d
    v_i_next = v_i_now + a_i * dt
    r_i_next = r_i_now + v_i_next * dt
```

This matches your sim2 simulator’s available data: per-hit emission states plus the receiver’s current state are sufficient to evaluate the update for every architrino each timestep.