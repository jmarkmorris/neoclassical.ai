## Causal Self-Action Functional — Coherent Structure

### 1) Problem Statement & Goal
The objective is to explain why only certain assemblies are stable and discrete, and to interpret “mass” as a consequence of causal self‑interaction rather than an external input. The target is a geometric/variational functional derived from the causal‑wake kernel that can be evaluated on periodic orbits, compared across topological classes, and tested against dynamical stability.

### 2) Core Functional Definitions
**Self‑action functional:**
$$
\mathcal{A}_{\text{self}}[\gamma] = \iint_{\gamma \times \gamma}
\frac{\delta\!\big(\|\mathbf{x}(t)-\mathbf{x}(t')\| - c_f(t-t')\big)}
{\|\mathbf{x}(t)-\mathbf{x}(t')\|^2}\,dt\,dt'
$$
We introduce a functional to replace ad‑hoc stability searches with a single quantity that can be compared across trajectories. The goal is to identify which worldlines are dynamically preferred and to connect that preference to discrete, reproducible particle‑like states.

This integrates over all pairs of points on a single worldline and counts only those pairs that are causally connected by a wake moving at speed $c_f$. The $1/r^2$ factor weights nearby self‑hits more strongly than distant ones.

**Interpretation:**
1. **Object:** The full worldline $\gamma$ is treated as a single geometric object.
2. **Constraint:** The delta function enforces the light‑cone condition, selecting causally connected pairs.
3. **Measure:** The $1/r^2$ weight emphasizes close self‑hits over distant ones.

**Normalized (periodic) self‑action:**
$$
\bar{\mathcal{A}}_{\text{self}}[\gamma] =
\frac{1}{T^2}\int_0^T\!\int_0^T
\frac{\delta_\eta\!\big(r(t,t')-c_f|t-t'|\big)}{r(t,t')^2}\,dt\,dt'
$$
with $r(t,t')=\|\mathbf{x}(t)-\mathbf{x}(t')\|$ and $\delta_\eta$ a mollified delta.
This version is defined for periodic orbits. The $T^2$ normalization makes values comparable across different periods, while $\delta_\eta$ regularizes the causal constraint for numerical evaluation.
Dimensional check: $[\bar{\mathcal{A}}_{\text{self}}]=1/\text{Length}^2$ (inverse area), consistent with a surface‑density measure over causal intersections.

**Total action (multi‑assembly):**
$$
\bar{\mathcal{A}}_{\text{total}}[\{\gamma_i\}] =
\sum_{i,j}\frac{1}{T^2}\int_0^T\!\int_0^T
\frac{\delta_\eta\!\big(r_{ij}(t,t')-c_f|t-t'|\big)}{r_{ij}(t,t')^2}\,dt\,dt'
$$
This aggregates self‑terms and cross‑terms between components, so stable multi‑component assemblies are assessed by the full interaction structure rather than self‑hits alone.

**Definitions:** $r(t,t')=\|\mathbf{x}(t)-\mathbf{x}(t')\|$, $r_{ij}(t,t')=\|\mathbf{x}_i(t)-\mathbf{x}_j(t')\|$, and $\Delta t = t-t'$.

**Kernel comparison:**
$$
\text{Force kernel: } \left[ \frac{\hat{\mathbf{r}}(t,t')}{r^2}, \delta\!\big(r-c_f\Delta t\big) \right]
\qquad
\text{Action kernel: } \left[ \frac{1}{r^2}, \delta\!\big(r-c_f\Delta t\big) \right]
$$
The force kernel retains direction via $\hat{\mathbf{r}}$, while the action kernel keeps only the scalar magnitude. This is the minimal change that turns a vector interaction into a scalar functional suitable for variational comparisons.

As a scalar, $\mathcal{A}_{\text{self}}$ summarizes the total strength of causal self‑hits along a worldline. It is derived directly from the interaction structure, but with the directional information removed.

For reference, the self‑interaction term in the master equation uses the same kernel:
$$
\mathbf{a}_{\text{self}}(t)
=\kappa q^2\int dt' \,
\frac{\hat{\mathbf{r}}(t,t')}{r^2(t,t')}
\delta\!\big(r(t,t')-c_f(t-t')\big)
$$

### 3) Rationale for the Functional
- **Natural Lyapunov/action‑like candidate:** If certain motion classes monotonically reduce a single functional, that quantity can label attractors and discrete minima that look like “mass levels” or particle configurations.
- **Bridge to geometric analysis / knot theory:** Showing that simple periodic motions (e.g., maximum‑curvature self‑hit orbits) locally minimize $\mathcal{A}_{\text{self}}$ within a topological class would give a clean geometric explanation for why some orbits are preferred over nearby perturbations.
- **Simulation‑friendly statistic:** Given any numerically computed orbit, we can Monte‑Carlo sample $(t,t')$, test the causal condition, and estimate $\mathcal{A}_{\text{self}}[\gamma]$ to compare shapes. This makes the “stable = local minimum” heuristic empirically testable.
- **Kolmogorov‑style appeal:** The functional is built directly from the microscopic law, convertible to empirical statistics, and a candidate for invariant measures that could explain attractor selection.

### 4) Geometric/Topological Framework
**Causal locus on the torus:** For a periodic orbit the domain $(t,t')\in[0,T]^2$ is a torus. The causal locus
$$
\mathcal{L}_{\text{causal}} = \{(t,t')\in T^2 \mid \|\mathbf{x}(t)-\mathbf{x}(t')\| = c_f|t-t'|\}
$$
is the set of self‑hits. Its winding numbers $(p,q)$ on $T^2$ are **discrete labels** for orbit families. As $R$ or $v$ change, the locus undergoes reconnection events; these are the bifurcations where families appear or disappear, giving a natural quantization of admissible self‑hit patterns. Sub‑$c_f$ motion leaves $\mathcal{L}_{\text{causal}}$ empty; super‑$c_f$ creates branches whose closure determines the integer self‑hit count per period.
The self‑action integral is the **weighted arc length** of $\mathcal{L}_{\text{causal}}$ with weight $1/r^2$, so topology and metric weight enter together.

**Causal writhe (chirality):**
$$
Wr_c[\gamma] = \iint_{\mathcal{L}_{\text{causal}}} \text{sign}\!\big(\mathbf{v}(t)\times\mathbf{v}(t')\cdot\mathbf{r}\big)\,d\tau
$$
is a signed measure of handedness for the self‑interaction pattern. Nonzero $Wr_c$ ties intrinsic chirality/spin to the geometry of the wake rather than an imposed quantum number; changing $Wr_c$ requires tearing the causal locus.

**Topological vs Noether data:** Continuous symmetries (time shifts, rotations) give Noether charges (energy, angular momentum). The winding class of $\mathcal{L}_{\text{causal}}$ supplies **topological charges**. Stable “generations” live where a Noether‑stationary orbit is also topologically locked; decay would require changing the winding class, i.e., a reconnection of $\mathcal{L}_{\text{causal}}$.

**Multi‑component topology:** For assemblies, project the spatial trajectories over one period, classify the resulting link, and when hyperbolic, use the volume of the link complement as a complexity measure. Brunnian or highly knotted complements signal strong causal interlocking and higher action density.

### 5) Analytic Benchmarks (Circular Orbit)
For a circular orbit of radius $R$ and speed $v=\beta c_f$:
$$
2R\left|\sin\left(\frac{\omega\Delta}{2}\right)\right| = c_f\Delta,
\quad \text{with } \omega=\frac{v}{R}
$$
Define $\xi=\frac{\omega\Delta}{2}$, giving the root condition:
$$
\sin\xi = \frac{\xi}{\beta}
$$

**Threshold:** The first non‑trivial self‑hit occurs at $\beta=\pi/2$.

**Closed‑form sum (with Jacobian):**
$$
\bar{\mathcal{A}}_{\text{self}}(\beta,R)=
\frac{\beta^3}{8\pi R^2}\sum_{n=1}^{N_{\text{max}}}
\frac{1}{\xi_n^2\sqrt{\beta^2-\xi_n^2}},
\quad \sin\xi_n=\frac{\xi_n}{\beta}
$$

**Asymptotics:**
$$
\bar{\mathcal{A}}_{\text{self}} \sim \frac{C}{\sqrt{\beta-\pi/2}}
\quad (\beta\to(\pi/2)^+)
$$
$$
\bar{\mathcal{A}}_{\text{self}} \sim \frac{\pi}{48R^2}
\quad (\beta\gg 1)
$$
The number of admissible roots $\xi_n$ (self‑hits per period) is the discrete count that matches the winding numbers of $\mathcal{L}_{\text{causal}}$; new roots appear only when the causal locus reconnects, so this analytic toy mirrors the bifurcation picture in Section 4.

### 6) Dynamical Interpretation
- Stable periodic orbits are **critical points** of $\bar{\mathcal{A}}_{\text{total}}$ constrained within a winding class. The delay flow need not be a gradient flow of this functional, so extremality is a selection principle, not a proof of asymptotic stability.
- **Existence vs. stability:** Topology of $\mathcal{L}_{\text{causal}}$ dictates which families can exist (via bifurcations when branches reconnect). Linear spectra of the delay equation decide which of those families attract. The causal locus is the combinatorial skeleton; Lyapunov exponents tell who survives.
- **Discreteness:** Each winding class gives an integer self‑hit count; moving between classes requires a reconnection event, explaining mass gaps and “generations” without adding quantization by hand.
- **Conservation with memory:** Time‑translation and rotational symmetry of the kernel imply conserved total energy and angular momentum, but energy includes the “virial of the history” stored in active causal wakes.
- **Gradient vs. symplectic:** The master equation is conservative; critical points of $\bar{\mathcal{A}}$ correspond to KAM‑style islands, not sinks. If any dissipation couples to the Noether Sea, minima could become attractors, but absent that, stability means orbital persistence, not asymptotic convergence.

### 7) Emergent Geometry Constraints
Define the coarse‑grained hit density
$$
\mathcal{I}(t,\mathbf{x})=\sum_j\int_{-\infty}^{t}\!\frac{\delta_\eta\!\big(\|\mathbf{x}-\mathbf{x}_j(t')\|-c_f(t-t')\big)}{\|\mathbf{x}-\mathbf{x}_j(t')\|^2}\,dt',
$$
and map it to an effective metric
$$
g_{\mu\nu}dx^\mu dx^\nu = -\alpha^2(\mathcal{I})\,c_f^2 dt^2 + \beta^2(\mathcal{I})\,\delta_{ij}dx^i dx^j,
$$
with small couplings $\alpha=1+\lambda_t\mathcal{I}$, $\beta=1+\lambda_s\mathcal{I}$ in the weak field. Bianchi identities and weak‑equivalence demands constrain the admissible $\lambda_{t,s}$; otherwise the emergent geometry reduces to a scalar‑tensor theory with potentially observable fifth forces. Matching the long‑range limit of test‑assembly motion to geodesics in $g_{\mu\nu}[\mathcal{I}]$ is the consistency check linking microscopic causal hits to macroscopic curvature.
Practical check: drop two assemblies of different internal $\bar{\mathcal{A}}_{\text{total}}$ through the same $\mathcal{I}(t,\mathbf{x})$ background and verify their centers follow the same geodesic to numerical tolerance.
Mean‑field view: in a dilute limit with many architrinos, coarse‑graining the hit process should yield a Vlasov equation for $f(t,\mathbf{x},\mathbf{v})$ with force derived from $\mathcal{I}$, providing the statistical bridge to continuum geometry.

### 8) Implementation Notes (Appendix)
- Use the same $\delta_\eta$ and $\eta$ for force and action estimators.
- For periodic orbits, normalize by $T^2$ and enforce periodic boundary conditions.
- For circular‑orbit calibration, compute $\xi_n$ roots numerically and sum with the Jacobian factor.
- Handle the $\beta=\pi/2$ caustic with care; the unregularized action diverges.
- Keep $\eta>0$ during variation: $\nabla\delta$ terms appear in $\delta\mathcal{A}$; regularization makes the Euler–Lagrange equations well‑posed. Take $\eta\to0$ only after solving or bounding solutions.

### 9) Limitations & caveats
- **Rest mass is not just self-action:** $\mathcal{A}_{\text{self}}$ needs careful units; true rest energy also depends on partner interactions, Noether Sea coupling, and external wakes.
- **Minima ≠ stability without dynamics:** Stability depends on the full DDE flow; the functional must be windowed/normalized (e.g., one period) to avoid divergences and to compare orbits meaningfully.
- **Topology needs precision:** Time is monotone; periodic motion yields a spatially closed path but a helical spacetime curve. Be explicit about which projection/linking notion defines the “topological class.”
- **Cohomology language is aspirational:** A cochain complex over the moduli of periodic orbits is not yet constructed; treat “cohomology of causal interaction” as a research direction, not a result.

### 10) Summary & status
- We defined a causal self-action and total-action functional directly from the $1/r^2$ delayed kernel, plus its normalized form for periodic orbits.
- Topology of the causal locus $\mathcal{L}_{\text{causal}}\subset T^2$ supplies discrete labels (winding, writhe, link type) that naturally segment orbit families.
- The circular-orbit benchmark gives an analytic threshold at $\beta=\pi/2$ and finite high-speed asymptotics, anchoring numerical calibrations.
- An emergent-metric ansatz from coarse-grained hit density $\mathcal{I}$ is proposed but must satisfy weak-field and equivalence constraints; this remains conjectural.
- Overall: this is a promising organizing framework, not a proved breakthrough. The key conjectures (rest-mass correlation with $\bar{\mathcal{A}}$, stability as critical points, effective metric validity) still require targeted analytic and numerical verification.
