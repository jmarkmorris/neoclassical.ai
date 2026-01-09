# 00.2.A — Self-energy and regularization notes

Purpose: explain why classical “point-charge self-energy” divergences do not arise in this framework, and summarize the role of measure-valued shells, the H(0)=0 convention, and $\eta$-mollification.

## 1) Classical self-energy pathology (contrast)

In classical electrostatics, a static 1/r potential yields an electric field E ∝ 1/r² with energy density ∝ |E|² ∝ 1/r⁴. Integrating 1/r⁴ over a ball produces a divergent ∫(1/r²)dr near r→0, the textbook “infinite self-energy of a point charge.” This is an artifact of modeling the source as an enduring, everywhere-filled near field.

## 2) Why the divergence is absent here

This project does not posit a static near field. Instead:

- Measure-valued expanding shells (no static 1/r near field):
  - Each emission is a razor-thin spherical shell with surface density q/(4$\pi$r²), represented by $\rho$(t,s) = (q/(4$\pi$r²)) $\delta$(r − v$\tau$) H($\tau$). The field support at fixed t is a sphere S_r, not a 3D 1/r² fill down to r=0. See 00.1.0 — Architrino (Analytic form).

- H(0)=0 (no coincident self-kick):
  - The instantaneous emission ($\tau$=0) contributes nothing to the force on the emitter; r=0 roots beyond $\tau$=0 do not exist because r = v(t − t₀). This removes the only event where a literal r=0 could enter. See 00.1.4 — Action (conventions).

- $\eta$-mollification (finite, well-defined work over resolved windows):
  - Replace $\delta$(r − v$\tau$) by a narrow Gaussian $\delta$_$\eta$ with width $\eta$>0 when differentiability is required. Potentials $\Phi$_$\eta$ and forces −∇(q′$\Phi$_$\eta$) are then regular functions; on any resolved interval the work–energy identity holds:
    $\Delta$E_k = −$\Delta$U, with U = q′ $\Phi$_$\eta$,
    and remains finite. As $\eta$→0, integrals converge in the weak sense to the impulsive model without introducing infinities. See 00.2.1.6 — Well-posedness and regularization.

- Event-driven geometry (self-hits occur at r>0):
  - Self-interaction requires outrunning recent shells (|v|>v). Self-hits are intersections with one’s own earlier shells at strictly positive radius r>0, yielding finite 1/r² impulses (repulsive, like-on-like). There is no accumulation of divergent near-field energy at r→0.

Net effect: the canonical ontology (moving surface measures, H(0)=0, mollification for analysis) avoids the classical point-charge self-energy divergence by construction.

## 3) Practical guidance (numerics and analysis)

- Choose $\eta$ small relative to local geometry (path curvature radius, inter-source spacing) for smooth ODE integration; verify $\Delta$E_k = −$\Delta$U on resolved windows.
- Calibrate $\kappa$ using stationary/slow benchmarks (Method 2) and use the event-driven law (Method 3) for many-body dynamics; no per-hit emitter-speed amplitude weighting is introduced.
- Treat self-hits as ordinary finite r>0 events; ensure H(0)=0 in implementation to exclude coincident-time artifacts.

Plain language: We don’t keep a permanent 1/r field glued to the point. Instead we use thin expanding shells, ignore the instant of emission for self-push, and (when needed) slightly thicken shells so calculus works—so nothing ever “blows up” at r=0.
