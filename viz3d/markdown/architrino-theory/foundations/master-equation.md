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
  - Apply retarded interactions by solving the emission‑time condition,
  - Track self‑hit events where an architrino’s current position lies on a sphere emitted from its past trajectory.

All emergent fields, metrics, and proper times are functionals of \(S(t)\) and its history, as seen in this absolute frame.

(Note: when describing nonlocal time dependence, we use “path history” rather than “retarded” to avoid confusion with unrelated terminology.)
