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

**Impact on delay locking:** The round-trip delay becomes anisotropic. For a ray at polar angle $\theta$ relative to the $z$-axis, the intersection radius with the ellipsoid is
$$
R(\theta) = \left(\frac{\sin^2\theta}{R_\perp^2} + \frac{\cos^2\theta}{R_\parallel^2}\right)^{-1/2}.
$$
Then $\Delta t_{\text{rt}}(\theta) \approx 2 R(\theta)/c_f$, and the phase condition generalizes to
$$
\Phi_n(\theta, \mathbf{v}_{\text{trans}}) = \omega_n\,\Delta t_{\text{rt}}(\theta) + \phi_{\text{geom}}(n).
$$

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

**Geometry inputs:** Represent the gradient as a scalar control parameter $G_{\text{grad}}$ (e.g., $|\partial \Phi/\partial r|$ or a tidal tensor magnitude) applied to the outer-binary environment.

**Expected effects to test:**
- Differential path delays across the outer orbit (forward vs backward sector).
- Drift in precession cone angle and inter-plane tilt under increasing $G_{\text{grad}}$.
- Shifts in the stability sign $\partial \Phi_n/\partial r$ or loss of plateau behavior.

### C) Exclusion Volume Under Precession (Caveat)

**Implication:** Outer-binary precession sweeps an exclusion region that is larger than a static orbit. The effective exclusion volume is the union of the orbit's causal envelope over a precession cycle, not just a single instantaneous shell.

**Modeling at $v>0$:** Use the oblate envelope as a time-dependent exclusion region whose axis precesses. The exclusion volume becomes anisotropic and typically increases with precession cone angle.

**As $v_{\text{trans}} \to c_f$:** The envelope flattens toward a disk, so the exclusion volume becomes a thin, swept annulus dominated by the equatorial plane. This tends to amplify planar alignment constraints and reduce accessible 3D configurations.

**Status:** This precession-expanded exclusion volume is not explicitly modeled in the current minimal system; treat results as lower bounds until the swept-volume effect is added.

### D) Time Distortion: Spacetime Time vs Absolute Time (Call-Out)

**Goal:** Make explicit how "time in spacetime" is distorted relative to absolute time by delay geometry and gradient effects.

**Effective lapse from delays:** Define a reference round-trip delay $\Delta t_{\text{rt,ref}}$ and a local delay $\Delta t_{\text{rt}}(\theta, G_{\text{grad}})$. Then
$$
\alpha(\theta, G_{\text{grad}}) = \frac{\Delta t_{\text{rt}}(\theta, G_{\text{grad}})}{\Delta t_{\text{rt,ref}}}
$$
acts as an effective time-dilation factor: clocks tied to local dynamics tick slower (larger $\alpha$) or faster (smaller $\alpha$) relative to absolute time.

**Interpretation:** High group velocity flattens the envelope and shortens forward delays, creating anisotropic clock rates. High gradients stretch or skew delays across the orbit, producing redshift-like effects. This provides a geometric analog to GR time dilation without invoking full metric dynamics.

**Lorentz beta in geometric form:** In Lorentz kinematics, $\beta = v/c$ and $\gamma = 1/\sqrt{1-\beta^2}$. In this model, use $\beta = v_{\text{trans}}/c_f$ and the oblate ellipsoid relation
$$
R_\parallel = R_\perp \sqrt{1-\beta^2} = \frac{R_\perp}{\gamma}.
$$
Geometrically, $\beta$ is the axis-squash control: as $\beta \to 1$, the causal envelope collapses along the motion axis, shrinking longitudinal path lengths and altering the delay.

**Why time appears to dilate:** The "clock" in this framework is the round-trip delay that closes phase in the outer-binary loop. As motion or gradient changes the causal path length, the local period inferred from phase closure changes:
$$
T_{\text{local}}(\theta) = T_0 \, \alpha(\theta, G_{\text{grad}}),
$$
with $T_0$ referenced to a baseline configuration (e.g., low speed, weak gradient). When $\alpha > 1$, the local dynamics take longer to complete a cycle relative to absolute time, which reads as time dilation. When $\alpha < 1$, the local cycle runs faster. This is the geometric analog: time dilation is a statement about how geometry (ellipsoid shape and gradient-induced delays) stretches or compresses the effective causal loop length.

**Action item:** Add a short derivation or narrative example that translates delay-based time distortion into a spacetime-style statement (e.g., "local clock period = intrinsic period x $\alpha$") and specify where this enters phase closure and stability.

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

### 3) Alignment Invariants and Configuration Diagnostics

**Goal:** Define computable invariants that separate 3D precessing regimes from planar aligned regimes and test the SU(2) to U(1) collapse narrative.

**Diagnostics:**
- Inter-plane angles from unit normals $\hat{n}_{\text{inner}}, \hat{n}_{\text{mid}}, \hat{n}_{\text{outer}}$.
- Precession cone angle of the net tri-binary axis over one outer period.
- Rotation test: does a $2\pi$ spatial rotation return the causal configuration or require $4\pi$?

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
