# Walkthrough Step 7 — Superposition and locality

Existing text excerpt:
> -   **Superposition:** The potential fields from all sources superpose linearly. The net potential at any point is the sum of the individual potentials:
>     $$
>     \Phi_{\text{net}} = \sum_{i} \Phi_i
>     $$
>     The total acceleration on a particle at any instant is the vector sum of the contributions from every intersecting causal wake surface. Operationally, every Architrino is continuously immersed in the superposed wakes of all others (and, when kinematics permit, its own); calculating the path-history integral is tractable by isolating each causal emission event, evaluating the $1/r^2$ kernel at that emission, and then summing—nearby sources dominate because their contributions fall off most slowly and cancelation is more complete at long range.

Detailed explanation (why near fields dominate):

  - Linear addition at the causal-surface level:
    - Because each source contributes a distribution supported on its causal wake surfaces, the total field is a sum of these measures; the acceleration law is linear in the summed contributions.

  - Locality from $1/r^2$:
    - The surface density on each causal wake surface scales as $1/r^2$, so nearby hits contribute disproportionately compared to distant ones. Random phases and geometries of distant sources enhance cancellation.

- Practical consequence:
  - Simulations can prioritize nearby sources and recent roots, using multipole or sampling approximations for far-field backgrounds.

Plain language: Add the pushes from all causal wake surfaces; the closest ones matter most because each hit falls off like one over distance squared, and distant pushes mostly cancel out.
