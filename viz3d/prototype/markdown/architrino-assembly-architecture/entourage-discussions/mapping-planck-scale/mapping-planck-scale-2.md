# Mapping Planck Scale v2 (Synthesis)

This note summarizes the current reframing of Planck scale in AAA and the related horizon/alignment discussion.

## Core Reframe

- **Planck scale is not the maximal-curvature inner binary by default.**
- **Planck scale is treated as an event-horizon alignment condition** in strong-field environments:
  - A component of architrino velocity reaches field speed (component not fixed a priori).
  - Orbital planes become coplanar/co-linear.
  - Precession damps to zero at alignment.
- **Middle binary always rides field speed** ($v=c_f$) and acts as the energy-storage fulcrum; its radius/frequency vary with conditions.
- **Outer binary** may be driven toward $v=c_f$ as horizon alignment is approached (not assumed by default).

## Low-Energy vs Strong-Field Regimes

- **Low-energy spacetime:** tri-binary radii/frequencies are **energy-separated**, and orbital planes tend toward near-orthogonality.
- **Strong-field/horizon:** radii may compress, planes align, and precession ceases; alignment is the relevant Planck-scale condition.

## Velocity Decomposition at the Horizon

Define total velocity as:

- $\mathbf{v}_{\text{total}} = \mathbf{v}_{\text{orb}} + \mathbf{v}_{\text{trans}}$
- $\mathbf{v}_{\text{trans}} = v_r \hat{\mathbf{r}}$ (radial toward BH center)

**Horizon condition (component-based):**

- $|\mathbf{v}_{\text{total}} \cdot \hat{\mathbf{u}}| = c_f$ for some relevant unit direction $\hat{\mathbf{u}}$
- Which component reaches $c_f$ (radial, tangential, or a combination) is an open question at this stage.

## Translation as the Lever (Phase-Lock Focus)

Working hypothesis: **translational velocity is the lever** that adjusts tri-binary phase locking. Assume the middle and outer binaries are phase-locked at distinct frequencies. That lock depends on:

- **Timing** of received potentials (delay geometry),
- **Magnitude** of received potentials (1/r^2 scaling and superposition),
- **Direction** of received potentials (radial vs tangential components).

As translational velocity increases, the **retarded reception times** and **incident directions** shift, which changes the effective coupling between middle and outer binaries and can drive the system toward new lock plateaus (including the horizon-alignment condition), without assuming which velocity component saturates at $c_f$.

**Focus path:** start from **assembly velocity = 0**, then accelerate the assembly through the Noether Sea and track how phase locking changes as a function of translation. This is the mechanism target that should lead into the **equivalence principle** in AAA.

### Minimal Delay-Geometry Sketch

Let an emitter in one binary at emission time $t_0$ be at position $\mathbf{x}_e(t_0)$ and a receiver in the other binary at time $t$ be at $\mathbf{x}_r(t)$. The causal constraint is:
$$
\|\mathbf{x}_r(t) - \mathbf{x}_e(t_0)\| = c_f (t - t_0)
$$
Decompose positions into orbital + translational motion:
$$
\mathbf{x}(t) = \mathbf{x}_{\text{orbit}}(t) + \mathbf{x}_{\text{trans}}(t), \quad \dot{\mathbf{x}}_{\text{trans}} = \mathbf{v}_{\text{trans}}
$$
As $\mathbf{v}_{\text{trans}}$ increases, the **solution set** for $t_0$ shifts, changing:
- **Timing**: $\Delta t = t - t_0$ (phase of received potential),
- **Direction**: $\hat{\mathbf{r}} = (\mathbf{x}_r(t) - \mathbf{x}_e(t_0)) / \|\mathbf{x}_r(t) - \mathbf{x}_e(t_0)\|$,
- **Magnitude**: $\propto 1/\|\mathbf{x}_r(t) - \mathbf{x}_e(t_0)\|^2$.
Those shifts modify the effective coupling between middle and outer binaries, providing a concrete pathway for translation-driven phase-lock adjustment.

## Frequency/Radius Relationships

For any orbit at $v=c_f$:

- $\omega = c_f / R$
- $f = c_f / (2\pi R)$

Thus, if middle/outer reach $v=c_f$ at alignment, their frequencies are fixed by radius via inverse scaling.

## Translation-Driven Ratchet (Quantized Lock Steps)

A proposed addition is **translation-driven ratcheting**: as translational velocity increases, phase locking advances in **integer frequency lock steps**.

- "Quanta" here means **integer frequency increments that correspond to phase-locked plateaus**, not particle quanta.
- This implies discrete alignment plateaus, resonance windows, and potential hysteresis in strong-field transitions.

## Open Questions / Derivation Targets

- What fixes the alignment radius numerically to $\ell_P$? (Derive $R_{\text{outer}}(\text{horizon}) = F(c_f, \epsilon, \kappa, \rho_{vac}, \ldots)$).
- Which velocity component reaches $c_f$ at alignment (radial, tangential, or mixed), and under what conditions?
- Does alignment imply radius convergence or only plane co-linearity?
- How does the radial ratchet couple to tri-binary frequencies and energy transfer?

## Current Working Statement

- **Planck scale = event-horizon alignment condition**, not inner-binary maximal curvature by default.
- **Middle binary rides $v=c_f$** across regimes and serves as the energy fulcrum.
- **Outer binary may reach $v=c_f$** as the horizon is approached; alignment collapses planes and damps precession.
- **Low-energy regime** retains energy-separated radii/frequencies and near-orthogonal planes.
