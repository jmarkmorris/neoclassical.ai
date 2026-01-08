## Addenda (Dyna)

### State and Evolution from the View of the Virtual Observer

We formulate the master equations with respect to the absolute coordinates and time:

- **State at time \(t\)**:
  \[
  S(t) = \{ (\mathbf{x}_i(t), \mathbf{v}_i(t), q_i, \sigma_i, \ldots ) \}_{i=1}^N
  \]
  where:
  - \(\mathbf{x}_i \in \mathbb{R}^3\),
  - \(\mathbf{v}_i = d\mathbf{x}_i/dt\),
  - \(q_i\) is the architrino’s charge/personality,
  - \(\sigma_i\) collects internal or polarization-like variables if needed.

- **Potential field** (schematic):
  \[
  \Phi(\mathbf{x}, t) = \sum_i K\big(\mathbf{x} - \mathbf{x}_i(t_\text{emit}), q_i, \sigma_i, \ldots\big)
  \]
  with emission time \(t_\text{emit}\) determined by:
  \[
  |\mathbf{x} - \mathbf{x}_i(t_\text{emit})| = c_f (t - t_\text{emit}),\quad t_\text{emit} \le t.
  \]

- **Master evolution map**:
  \[
  S(t+\Delta t) = \mathcal{F}[S(\cdot)\text{ on }[t-T_\text{mem},t]; \Delta t],
  \]
  where \(\mathcal{F}\) is, in general, **non‑Markovian** due to self‑hit: it depends on a finite history window \([t-T_\text{mem}, t]\) of each worldline.

The virtual observer:

- Uses the fixed Euclidean chart to:
  - Integrate the equations of motion for all architrinos,
  - Apply history interactions by solving the emission‑time condition,
  - Track self‑hit events where an architrino’s current position lies on a sphere emitted from its past trajectory.

All emergent fields, metrics, and proper times are functionals of \(S(t)\) and its history, as seen in this absolute frame.

(Note: when describing nonlocal time dependence, we use “path history” rather than “history” to avoid confusion with unrelated terminology.)

## Addenda (Dyna)

### Master Equation from the View of the Absolute Observer

All dynamical laws are written with respect to the fixed Euclidean coordinates $(x,y,z)$ and absolute time $t$.

1. **State Definition**: The state $S(t)$ is a list of all architrino positions, velocities, and charges at time $t$.
2. **The Equation**: The Master Equation is a deterministic map $S(t+\Delta t) = \mathcal{F}[S(t); \Delta t]$, incorporating finite propagation speed $c_f$ and history interactions.
3. **Background Coupling**: An isolated binary is an idealization. The real equation must include the "Sea of Cores" interaction:
   $$ \\vec{a}_i = \\sum_{j \\in \\text{System}} \\vec{F}_{ji} + \\sum_{k \\in \\text{Vacuum}} \\vec{F}_{ki} $$
   The second term represents the drag/inertia from the Noether Core lattice.

## Addenda (Dyna - supplemental)

### Master Equation via Absolute Observer

* **State Space:** The equation evolves the state $S(t)$ in fixed coordinates.
* **Forces:** $\vec{a}_i = \sum \vec{F}_{sys} + \sum \vec{F}_{vac}$. The vacuum term represents the coupling to the "Sea of Noether Cores."
* **Retardation:** Interaction terms are functions of history in absolute coordinates: $|\mathbf{x}_{rec}(t) - \mathbf{x}_{em}(t')| = c_f(t-t')$.
