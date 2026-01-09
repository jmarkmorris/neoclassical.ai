
| ID | Parameter Name | Category | Value/Form (Provisional) | Notes |
|:---|:---|:---|:---|:---|
| **A1** | **Field Speed** | Fundamental | $c_f$ | Fundamental speed of potential propagation in the Euclidean void. Defines causality. |
| **A2** | **Interaction Kernel** | Fundamental | $\Phi(\vec{x}, t; \vec{x}', t') = \frac{q}{\|\vec{x} - \vec{x}'\|}$ for $t' = t - \|\vec{x}-\vec{x}'\|/c_f$ | Explicit retarded Coulomb potential. Defines the force law. |
| **A3** | **Charge Magnitude** | Fundamental (Unit) | $\|q\| = 1$ (Normalized) | Sets the scale for coupling strength and, via the action principle, inertial response. |
| **A4** | **Polarity Balance** | Postulate | $\sum q = 0$ (Global) | Initial condition enforcing universe neutrality. |
| **A5** | **Particle Geometry** | Fundamental | $r=0$ (Point) | Architrinos are mathematical point transceivers; interaction is purely field-based. |
| **A6** | **Worldline Action** | Fundamental Law | $S[\gamma] = \int dt \left( \frac{\|q\|}{2}\|\dot{\vec{x}}\|^2 + \sum_{j} \int d\tau'\, q \Phi(\vec{x}(t), \vec{x}_j(\tau')) \right)$ | **Proposed master law.** Yields equations of motion with delay. Kinetic term defines inertia. |
| **A7** | **Memory Cutoff** | Regularization | $\tau_{mem}$ or $\Lambda$ | Required to render self-energy integrals finite. Could be linked to dynamical timescales (e.g., orbit period). |
| **B1** | **Volumetric Architrino Density** | Scale Setter | $\rho_{arch}$ | Number density of architrinos in the void. Sets background medium properties. |
| **B2** | **Inner Binary Scale** | Derived (Estimate) | $R_{inner} \sim \frac{\|q\|}{c_f^2}$ | Dimensional estimate from balancing self-force at $v \to c_f$. Defines the "maximum curvature" regime. |
| **C1** | **Time Step** | Computational | $\Delta t \ll R_{inner}/c_f$ | Courant-type condition for stable simulation of delay dynamics. |
| **C2** | **Simulation Volume** | Computational | $L \gg \rho_{arch}^{-1/3}$ | Must be large relative to mean inter-particle spacing to approach continuum behavior. |