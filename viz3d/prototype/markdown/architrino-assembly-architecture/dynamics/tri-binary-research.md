### Tri-Binary Research Plan: Geometry Under High Group Velocity and High Gravitational Gradient

---

**Purpose:** Determine whether delay-coupled tri-binary dynamics admit discrete modes and a terminal aligned state, and characterize the geometry as group velocity approaches $c_f$ and as gravitational gradient increases.

**Scope:** Minimal, testable models with explicit delay and geometry. No full GR. Emphasis on observable invariants and phase-closure diagnostics.

---

## Core Hypotheses (Testable)

1. The formed Noether core has stable invariants ($R_{\text{core}}$, $\omega_{\text{core}}$, fixed phase offsets).
2. The outer-binary delay loop yields discrete plateaus and a terminal aligned mode under increasing stress.
3. High group velocity produces an oblate causal envelope that drives planar alignment in the terminal rung.
4. High gravitational gradient modifies phase closure through tidal or differential delay effects, shifting or destabilizing rungs.

---

## Geometry Focus

### A) High Group Velocity Geometry (Oblate Spheroid)

**Assumption (testable):** The outer binary moving at translational speed $v_{\text{trans}}$ generates a causal interaction envelope that is oblate and flattens along the direction of motion as $v_{\text{trans}} \to c_f$.

**Geometry:** Let the motion define the $z$-axis. Model the envelope as an ellipsoid
$$
\frac{x^2 + y^2}{R_\perp^2} + \frac{z^2}{R_\parallel^2} = 1,
$$
with transverse radius $R_\perp$ and longitudinal radius $R_\parallel$.

Adopt a kinematic contraction law (to be validated by dynamics):
$$
\beta = \frac{v_{\text{trans}}}{c_f}, \quad \gamma = \frac{1}{\sqrt{1-\beta^2}}, \quad R_\parallel = \frac{R_\perp}{\gamma}.
$$
As $\beta \to 1$, $R_\parallel \to 0$ and the envelope collapses toward a disk.
**Right-triangle link:** Treat $c_f$ as the fixed causal propagation speed and decompose it into orthogonal components: one leg is the group translation $v_{\text{trans}}$, the other leg is the longitudinal closure speed $v_\parallel$. Then
$$
c_f^2 = v_{\text{trans}}^2 + v_\parallel^2 \quad \Rightarrow \quad v_\parallel = c_f\sqrt{1-\beta^2}.
$$
Mapping causal speed to closure length gives $R_\parallel = R_\perp (v_\parallel/c_f) = R_\perp\sqrt{1-\beta^2} = R_\perp/\gamma$, recovering the ellipsoid law from the triangle geometry.

**Impact on delay locking:** The round-trip delay $\Delta t_{\text{rt}}$ is the time between an outer-binary architrino’s emission and the moment its wake returns to influence that same architrino, approximating the inner+middle as a compact core at the center. For a ray at polar angle $\theta$ relative to the $z$-axis, the intersection radius with the ellipsoid is
$$
R(\theta) = \left(\frac{\sin^2\theta}{R_\perp^2} + \frac{\cos^2\theta}{R_\parallel^2}\right)^{-1/2}.
$$
Then $\Delta t_{\text{rt}}(\theta) \approx 2 R(\theta)/c_f$, and the phase condition generalizes to
$$
\Phi_n(\theta, \mathbf{v}_{\text{trans}}) = \omega_n\,\Delta t_{\text{rt}}(\theta) + \phi_{\text{geom}}(n).
$$
**Conjecture (velocity convergence):** As translational speed increases, delay-closure constraints drive the orbital degree of freedom to adjust (e.g., by shrinking radius and raising $v_{\text{orb}}^{\text{tan}}$) so that both $v_{\text{trans}}$ and $v_{\text{orb}}^{\text{tan}}$ converge toward $c_f$ at the planar transition.

**Exclusion volume (instantaneous):**
$$
V(v_{\text{trans}}) = \frac{4\pi}{3} R_\perp^2 R_\parallel
= \frac{4\pi}{3} R_\perp^3 \sqrt{1-\left(\frac{v_{\text{trans}}}{c_f}\right)^2}.
$$
If the outer radius is infalling, treat $R_\perp = R_\perp(t)$ so
$$
V(t) = \frac{4\pi}{3} R_\perp(t)^3 \sqrt{1-\left(\frac{v_{\text{trans}}(t)}{c_f}\right)^2}.
$$
**Coupling caveat:** Whether $v_{\text{trans}}$ is independent of the radial infall speed $v_r$ is unresolved. Use the independent form by default, or adopt a coupling $v_{\text{trans}} = f(R_\perp)$ and substitute to test specific scenarios.

### B) High Gravitational Gradient Geometry

**Assumption (testable):** A strong external gradient (tidal field or effective curvature) perturbs the delay loop, altering phase closure and stability of rungs.

**Origin of the gradient (model definition):** Gravitation is implemented as an emergent spatial gradient in Noether core volume. As energy accumulates in dense collections of standard-model assemblies (protons, neutrons, electrons), the local Noether core volume contracts, and surrounding regions experience a gradient in available core volume. This gradient is the effective gravitational field in the delay-geometry model.

**Geometry inputs:** Represent this gradient as a scalar control parameter $G_{\text{grad}}$ (e.g., $|\partial \Phi/\partial r|$ or a tidal tensor magnitude) applied to the outer-binary environment. In simulations, treat $G_{\text{grad}}$ as the local radial derivative of Noether core volume (or its proxy) around the outer-binary orbit.

**Expected effects to test:**
- Differential path delays across the outer orbit (forward vs backward sector).
- Drift in precession cone angle and inter-plane tilt under increasing $G_{\text{grad}}$.
- Shifts in the stability sign $\partial \Phi_n/\partial r$ or loss of plateau behavior.
**Prediction:** Increasing $G_{\text{grad}}$ shifts stable $n$ values and narrows or removes plateaus; strong gradients can pull the terminal alignment inward or erase it.

### C) Exclusion Volume Under Precession (Caveat)

**Implication:** Outer-binary precession sweeps an exclusion region that is larger than a static orbit. The effective exclusion volume is the union of the orbit's causal envelope over a precession cycle, not just a single instantaneous shell.
This union geometry sets packing and overlap limits by construction, rather than relying on point-particle exclusion rules.

**Modeling at $v>0$:** Use the oblate envelope as a time-dependent exclusion region whose axis precesses. The exclusion volume becomes anisotropic and typically increases with precession cone angle.

**As $v_{\text{trans}} \to c_f$:** The envelope flattens toward a disk, so the exclusion volume becomes a thin, swept annulus dominated by the equatorial plane. This tends to amplify planar alignment constraints and reduce accessible 3D configurations.
At sufficiently high stress, this implies a terminal rung: further increases cannot support a stable 3D mode, only a planar aligned state.

**Status:** This precession-expanded exclusion volume is not explicitly modeled in the current minimal system; treat results as lower bounds until the swept-volume effect is added.

### D) Time Distortion: Spacetime Time vs Absolute Time

**Goal:** Define "time in spacetime" as a geometric effect in the delay loop, not a relativistic postulate.

**Absolute clock:** Use the outer-binary Planck cadence as the invariant clock: $T_0 = 1/f_P$. This is a reference for absolute time in the model.

**Local clock from delay geometry:** Define a reference round-trip delay $\Delta t_{\text{rt,ref}}$ and a local delay $\Delta t_{\text{rt}}(\theta, G_{\text{grad}})$. Then
$$
\alpha(\theta, G_{\text{grad}}) = \frac{\Delta t_{\text{rt}}(\theta, G_{\text{grad}})}{\Delta t_{\text{rt,ref}}}
$$
and, for the ellipsoid-only case with no gradient,
$$
\alpha(\theta) = \frac{R(\theta)}{R_{\text{ref}}}
$$
measures how the local phase-closure period compares to the invariant clock:
$$
T_{\text{local}}(\theta) = T_0 \, \alpha(\theta, G_{\text{grad}}).
$$
When $\alpha > 1$, local cycles are longer relative to $T_0$; when $\alpha < 1$, they are shorter. This is the penultimate definition of time distortion in this model.

**Geometric source of distortion:** The causal envelope shape sets $\Delta t_{\text{rt}}$. As the tri-binary tilts out of planar and loses energy, the envelope becomes less oblate (larger $R_\parallel/R_\perp$), increasing some path lengths and stretching $T_{\text{local}}$; as it flattens, $R_\parallel$ shrinks and the corresponding delays contract. Gradients ($G_{\text{grad}}$) further skew delays across the orbit.

**Lorentz beta in geometric form:** In Lorentz kinematics, $\beta = v/c$ and $\gamma = 1/\sqrt{1-\beta^2}$. In this model, use $\beta = v_{\text{trans}}/c_f$ and the oblate ellipsoid relation
$$
R_\parallel = R_\perp \sqrt{1-\beta^2} = \frac{R_\perp}{\gamma}.
$$
Geometrically, $\beta$ is the axis-squash control: as $\beta \to 1$, the causal envelope collapses along the motion axis, shrinking longitudinal path lengths and altering the delay.

**Where it enters phase closure:** In scans, treat the local clock as an effective frequency $\omega_n/\alpha$ inside $\Phi_n$ for the sector under consideration. Redshift follows because emitted periodicity inherits the local clock rate: longer causal loops (larger $\alpha$) yield lower observed frequency at fixed absolute-time reference.

---

## Minimal Models and Experiments

### 1) Noether Core Baseline (Inner + Middle Fixed)

**Goal:** Treat inner + middle as a formed Noether core and establish its internal timescales, radii, and phase relations before stressing the outer binary.

**Concrete tasks:**
1. Hold the Noether core fixed (or slowly varying) with center of mass at rest.
2. Run long enough to stabilize internal phase relationships (use convergence checks in $\Delta t$, $\eta$).
3. Measure $R_{\text{core}}$, $\omega_{\text{core}}$, and stable phase offsets.
4. Verify repeatability across nearby initial conditions and whether any core element rides $v = c_f$ continuously.

### 2) Outer-Binary Delay Loop Model with Formed Core

**Goal:** Test the discrete ladder / top-rung hypothesis in a minimal delay system and quantify geometry at high $v_{\text{trans}}$ and high $G_{\text{grad}}$.

**Model:**
- Inner + middle modeled as a rigid core with fixed timescales.
- Outer binary orbits the core with non-coplanar planes initially.
- Translational speed $\mathbf{v}_{\text{trans}}$ and gradient $G_{\text{grad}}$ are control parameters.
- Use ellipsoid-based $\Delta t_{\text{rt}}(\theta)$ for high-velocity geometry.

**Phase condition:**
$$
\Phi_n(\theta, \mathbf{v}_{\text{trans}}, G_{\text{grad}}) = \omega_n\,\Delta t_{\text{rt}}(\theta) + \phi_{\text{geom}}(n),
$$
and track when $\partial \Phi_n/\partial r$ changes sign.
Quantization here is emergent: only delay-locked, stable closures persist as discrete rungs, not imposed eigenmodes.

### 3) Alignment Invariants and Configuration Diagnostics

**Goal:** Define computable invariants that separate 3D precessing regimes from planar aligned regimes and test the SU(2) to U(1) collapse narrative.

**Diagnostics (operational):**
- **Inter-plane angles:** $\theta_{ij} = \arccos(\hat{n}_i \cdot \hat{n}_j)$ for $(i,j)\in\{\text{inner, mid, outer}\}$. Track $\max(\theta_{ij})$ over an outer period.
- **Planarity threshold:** Declare “planar aligned” if $\max(\theta_{ij}) < \epsilon_\theta$ for $N$ consecutive outer periods.
- **Precession cone angle:** Let $\hat{n}_{\text{net}}$ be the normalized sum of plane normals. Define $\theta_{\text{cone}} = \max_t \arccos(\hat{n}_{\text{net}}(t)\cdot\langle\hat{n}_{\text{net}}\rangle)$ over one outer period.
- **Rotation test (SU(2) vs U(1)):** Evolve the same state under an imposed $2\pi$ spatial rotation and compare the causal configuration $\mathcal{C}(t)$ to the unrotated one (e.g., phase-closure residuals and relative plane phases). If $\mathcal{C}(t)$ matches only after $4\pi$, treat as SU(2)-like; if after $2\pi$, treat as U(1)-like.
- **Prediction:** As alignment strengthens, $\theta_{ij}$ and $\theta_{\text{cone}}$ should decrease monotonically; the rotation test should transition from $4\pi$ to $2\pi$ return.
As alignment increases and planes coincide, the remaining degree of freedom is a single in-plane phase (U(1)-like), consistent with a boson-like terminal configuration.

---

## Observables and Diagnostics (Summary)

- Core invariants: $R_{\text{core}}$, $\omega_{\text{core}}$, phase offsets.
- Ladder metrics: $R_{\text{out}}(t)$, $\omega_{\text{out}}(t)$, plateau stability.
- Geometry metrics: anisotropy ratio $A = R_\parallel/R_\perp$, forward vs backward delay ratio.
- Orientation metrics: inter-plane angles, precession cone angle.
- Stability metrics: sign of $\partial \Phi_n/\partial r$, phase-closure residuals.
- Gradient metric: $G_{\text{grad}}$ and its effect on stability thresholds.

---

## Decision Gates

1. **Core stability:** If invariants are unstable or non-repeatable, pause outer-binary claims.
2. **Discrete rungs:** If plateaus do not exist or terminate, revise the top-rung thesis.
3. **High-velocity geometry:** If oblate geometry does not improve phase closure, revise the envelope model.
4. **High-gradient behavior:** If strong gradients erase alignment, document the failure mode and boundary conditions.

---

## Execution Order

1. Noether core baseline and invariants.
2. Outer-binary delay loop without gradient; validate oblate geometry at high $v_{\text{trans}}$.
3. Add $G_{\text{grad}}$ and scan stability vs gradient.
4. Run alignment invariants across low-stress and high-stress regimes.

---

## Equivalence Principle (Working Interpretation)

**Premise:** In high gravity, Noether cores become more oblate as the local delay geometry is distorted by the surrounding volume gradient. In pure acceleration (deep space), an object’s internal delay geometry also becomes more oblate. If the equivalence principle is to hold locally, the surrounding spacetime must adapt as well.

**Local-equivalence statement (model-level):** A uniformly accelerated assembly should experience the same local delay geometry as a stationary assembly in a corresponding Noether core volume gradient. This requires the local spacetime delay structure (pilot-wave environment) to co-distort with the accelerated object, not just the object alone.

**Implementation idea:** Treat acceleration as imposing an effective gradient in the experienced field, mediated by the pilot-wave structure. In the minimal model:
- High gravity: oblate cores arise because $G_{\text{grad}}$ skews delays across the orbit.
- Uniform acceleration: oblate cores arise because the pilot-wave environment rephases so that the same $\Delta t_{\text{rt}}(\theta)$ pattern appears in the accelerated frame.

**Testable consequence:** If equivalence holds, the same delay-closure diagnostics (phase residuals, anisotropy ratios, stability thresholds) should match between (i) a gradient-driven case and (ii) an acceleration-driven case with matched effective $\alpha(\theta)$.

**Momentum after acceleration:** During acceleration, the object and its pilot-wave environment rephase into a moving, oblate configuration. When the external acceleration ceases, the established delay-closure state persists (no gradient remains to unwind it), so translation continues. Momentum is the conserved motion state of this locked geometry; it relaxes only if interactions or gradients rephase the delays.
