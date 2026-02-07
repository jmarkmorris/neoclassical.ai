# Geometry & Dynamics Working Group - Consolidated Initial Observations (Second Draft)

**Compiled by Dyna, Lead Coordinator**  
**Date**: Initial Session (Revised incorporating Andrey Kolmogorov feedback)  
**Purpose**: Establish shared mathematical foundation and identify promising research directions for the architrino assembly architecture

---

## Structural Overview

The ontology presents us with an unusually clean separation:

- **Substrate**: Flat Newton–Cartan-like background with absolute time $t \in \mathbb{R}$ and Euclidean spatial metric $h_{ij} = \delta_{ij}$ on $\mathbb{R}^3$
- **Dynamics**: Point entities (architrinos) interacting via finite-speed causal wake surfaces with path-history dependence
- **Emergence**: All non-trivial structure—geometry, particles, fields—lives in the *bundle of worldlines and wakes*, not in the substrate itself

This separation enables a **hierarchy of dynamical atlases**: local charts of assembly phase space organized by regime (low/high density, weak/strong self-hit, sub/super-$c_f$) with explicit gluing maps between regions. The emergence layer should be formalized as a **sheaf of local assembly states** over absolute timespace, so that sheaf cohomology can classify global excitations (e.g., field-like twists in orientation fields). If we construct this atlas correctly, the entire architecture—emergent metric, probabilistic laws, particle taxonomy—will have a coherent backbone and remain simulation-ready.

---

## The Path-History Interaction as Infinite-Dimensional Phase Space

### Core Mathematical Challenge (Grothendieck, Tao)

The master equation defines acceleration via intersections with past causal wake surfaces:
$$
\frac{d^2 \mathbf{x}_i}{dt^2} = \sum_j \sum_{t_0 \in \mathcal{C}_j(t)} \kappa\,\sigma_{ij}\,\frac{|q_i q_j|}{r_{ij}^2(t;t_0)}\,\hat{\mathbf{r}}_{ij}(t;t_0)
$$

**Key insight**: The "state" at time $t$ is not the finite-dimensional tuple $(\mathbf{x}_i(t), \mathbf{v}_i(t))$ but rather the **entire trajectory history** $h_t(\theta) = \mathbf{x}(t+\theta)$ for $\theta \in [-\tau_{\max}, 0]$ over the causal horizon. Formally, this is a **Neutral Functional Differential Equation (NFDE)** with state-dependent delays, making the effective phase space **infinite-dimensional**.

Yet the ontology asserts the existence of **stable, discrete assemblies** (Noether cores, electrons, quarks) with fixed finite-dimensional properties. This presents the central puzzle:

> **How does a finite-dimensional stable manifold (a particle) emerge from an infinite-dimensional history-dependent delay system?**

### Proposed Resolution (Grothendieck, Kolmogorov)

The answer likely lies in the **moduli space of self-intersecting trajectories**, but it is enforced by three concrete physical filters: **locality**, **finite field speed $c_f$**, and **distance-decaying potentials**. Because interactions propagate at finite speed and fall off with distance, the most recent and most local segments of history dominate the force budget; distant segments contribute weakly and with long delay. This creates conditions where **local paths in timespace have the most influence**, allowing stable assemblies to form as **isolated strata** in the space of histories—essentially **topologically protected knots of causality** that effectively screen off the infinite past and behave as finite-memory objects.

Mathematically, we should organize assemblies into **categories** where:
- **Objects**: Assembly configurations equipped with their internal dynamics and invariants
- **Morphisms**: Cobordisms of worldline knots embedded in the causal wake field; decay/transformation channels, coarse-graining maps, adiabatic deformations preserving key invariants (charge, topological type, action)
- **Stable particles**: Objects with no (or highly suppressed) outgoing morphisms

**Action item (categorical dynamics):** Define the **elementary cobordisms** allowed by the interaction law (e.g., strand crossing with energy penalty, loop creation/annihilation). These generate the morphisms and enable computation of transition amplitudes between assembly types (categorical precursor to decay rates and cross-sections).

This categorical structure can be organized as **fibered categories over absolute timespace**: over each region of $\mathbb{R}^3 \times \mathbb{R}$ lives a category of assemblies and their morphisms, glued by compatibility of interaction laws.

---

## Delay Dynamics and the Self-Hit Regime

### Qualitatively New Dynamical System (Poincaré, Cartan)

The path-history / self-hit mechanism is **not a perturbation but structural**. When $|\mathbf{v}_a| > c_f$, an architrino's future depends on the *geometric configuration* of its entire past worldline, creating phase-space flows unlike anything in classical mechanics.

**Key features**:
- Multiple causal roots $\mathcal{C}_j(t)$ act as **built-in nonlocal feedback loops**
- Rich bifurcation structure even for simple binaries
- **Coexisting attractors and deterministic multistability** at threshold regimes
- Natural emergence of chaotic scattering

The self-hit regime is best understood as **delay-coupled oscillators** in flat absolute timespace. The architecture naturally generates a **zoo of attractors**:
- Limit cycles
- Quasi-periodic tori
- Chaotic self-hit orbits
- Maximum-curvature organizing centers

**Research priority**: Map this zoo systematically via bifurcation diagrams parameterized by wake strength vs velocity relative to $c_f$.
- Use $(\kappa, \beta)$ with $\beta = v/c_f$ as primary controls.
- Start with a minimal binary, then extend to tri-binary.
- Sweep a grid in $(\kappa,\beta)$ and classify attractors (fixed points, cycles, tori, chaotic).
- Track stability via Floquet multipliers / Lyapunov exponents and label bifurcation types.
- Use continuation (e.g., pseudo-arclength) to follow branches and locate transitions.

### Singularity Structure and Well-Posedness (Tao)

The $1/r^2$ interaction kernel is singular on causal wake surfaces. When $|\mathbf{v}| > c_f$ causes a particle to traverse its own past wake (the "shock cone"), the force term potentially diverges. 

**Current status**: At present, existence and uniqueness are only clear for **mollified interactions** (finite regularization parameter $\eta$). When delays are state-dependent, the root set $\mathcal{C}_j(t)$ can bifurcate or merge, and the delay derivative can blow up, breaking Lipschitz continuity. Whether the $\eta \to 0$ limit exists as a mathematically well-posed theory is an **open question**; until this is resolved, all claims using sharp $1/r^2$ hits should be labeled as **formal** or **heuristic**.

**Critical dichotomy**: Either
1. The dynamics remain well-posed in the limit $\eta \to 0$ (perhaps maximum-curvature constraints naturally avoid the singularity), or
2. We must accept $\eta$ as a fundamental non-zero length scale, mollifying the theory at the definition level

The "meta-stable branching" likely arises precisely where Lipschitz continuity breaks down near these singularities. We may need to define a **weak solution concept** with a selection principle (analogous to entropy conditions in conservation laws) to maintain determinism.

**First task**: Treat $\eta > 0$ as the fundamental regularized system, prove local existence/uniqueness for the state-dependent delay equation, then attempt a controlled $\eta \to 0$ weak/viscosity limit. Any derivations assuming $\eta \to 0$ should be marked **(formal limit; analytic control TBD)**. Sol’s simulations should converge to the $\eta > 0$ dynamics as $\Delta t \to 0$; if not, the code is wrong.

---

## Topology, Geometry, and Assembly Classification

### Worldline Knots as Particle Types (Thurston, Grothendieck)

Since the substrate $\mathbb{R}^3 \times \mathbb{R}$ is topologically trivial, all interesting topology lives in the **braiding and linking of worldlines** and the structure of recurrent trajectories.

**Central hypothesis**: Stable assemblies are not generic knots of worldlines (since 1D curves in $\mathbb{R}^3 \times \mathbb{R}$ can typically be untied), but are protected by a **causal self-linking obstruction**. The obstruction is the self-hit singularity barrier (or its regularized high-potential shell): trajectories cannot be continuously deformed across the divergent self-force region.

**Topological Periodic Table**:
Classify assemblies by:
- **Knot/link type** of representative orbits
- **Winding numbers** around self-hit regions
- **Handedness** (pro/anti: H/M/L vs H/L/M frequency ordering)
- **Orbit chirality** (CW vs CCW around the momentum vector)
- **Charge decoration** on six polar sites ($\pm \epsilon$ assignments)

**Causal self-linking (action item):** Define a **Causal Linking Number** $Lk_{\text{causal}}$ by treating the trajectory $\gamma(t)$ together with its primary causal wake vector $\hat{\mathbf{r}}(t)$ as a ribbon. When $|\mathbf{v}| > c_f$, the trajectory winds around its own past causal cone, creating a topological obstruction in the complement of the causal wake. This supplies a nontrivial winding invariant that cannot be removed without crossing the self-hit barrier.

**Working definition (first pass):** Let $\gamma(t)$ be a worldline segment over a long period and define its causal offset curve $\gamma_\epsilon(t) = \gamma(t) + \epsilon\,\hat{\mathbf{r}}(t)$, where $\hat{\mathbf{r}}(t)$ points toward the dominant causal-hit direction at time $t$. Then define
$$
Lk_{\text{causal}} = \text{Link}(\gamma, \gamma_\epsilon),
$$
the linking number of the trajectory and its causal-offset ribbon. This is well-defined only when the self-hit barrier keeps $\gamma$ and $\gamma_\epsilon$ disjoint; changes in $Lk_{\text{causal}}$ require passing through the divergent self-hit region, making it a topological invariant of stable assemblies.

**Key conjecture**: Discrete charge quantization ($\epsilon = e/6$) is not arbitrary. The unit magnitude is fixed per architrino/site, while $Lk_{\text{causal}}$ (and related winding/linking counts) selects which counts and sign patterns are stable, yielding quantized net charge for the assembly.

The tri-binary structure (three nested counter-rotating binaries at radii $R_{\text{inner}}, R_{\text{middle}}, R_{\text{outer}}$, with **energy-separated** radii/frequencies in low-energy conditions and orbital planes tending toward near-orthogonality) has inherent topological rigidity. Combined with geometric parameters, this creates a **finite classification space**—a genuine periodic table of possible assemblies.

**Critical stability assumption** ⚠️ **[HIGH RISK]**: It is not yet proven that maximum-curvature orbits are **robust attractors** rather than finely tuned periodic solutions. This is a critical structural assumption; if typical perturbations cause secular drift rather than attraction to these orbits, the proposed particle architecture must be revised. Proving attractor stability (or identifying its failure) is a **top priority** for analytic and simulation work.

### Emergent Geometry from Assembly Fields (Cartan)

The fixed Euclidean void plus dynamical Noether Sea enables clean separation:
- **Background connection**: Trivial (flat Newton–Cartan)
- **Effective connection**: Built from assembly fields

**Construction**: Define a **moving-frame field** $e^a{}_\mu(x)$ whose orientation and norm are functionals of explicitly defined, measurable assembly fields:
- Tri-binary density $\rho_{\text{core}}(\mathbf{x},t)$
- Flow velocity $u^\alpha_{\text{core}}$ (an operationally defined local transport velocity)
- Orientation fields (neutral-axis directions with a specified estimator)
- Internal tri-binary state (radii, frequencies)

**Caution on coarse-graining:** Modeling at the “core” level is tempting but can drift from true N-architrino dynamics. Any effective-field or core-level model should be validated against explicit N-body delay simulations to avoid introducing artifacts.

**Target effective metric** (underspecified until $e^a{}_\mu$ is made explicit):
$$
g_{\mu\nu}^{\text{eff}} = e^a{}_\mu e^b{}_\nu \eta_{ab}
$$

**First working ansatz (weak-field, quasi-static):** Commit to a concrete leading-order frame field:
$$
e^0{}_0(\mathbf{x}) \approx 1 + \alpha\,\Phi_{\text{core}}(\mathbf{x}),\qquad
e^i{}_j(\mathbf{x}) \approx \delta^i{}_j + \beta\,\Psi^i{}_j(\mathbf{x}),
$$
where $\Phi_{\text{core}}$ is a scalar functional of $\rho_{\text{core}}$ (Noether-core overdensity) and $\Psi^i{}_j$ encodes anisotropic orientation of neutral axes. Even with provisional $\alpha,\beta$, this provides a concrete metric to test: recover the Newtonian limit and check the sign/order of light bending.

**Emergent curvature**: The Cartan curvature of this frame bundle, not of the void. Operational observers measure geodesics of $g_{\mu\nu}^{\text{eff}}$, not of the substrate, but this claim must be tied to explicit observables (e.g., redshift, light bending) in defined regimes.

**Research program** *(design goals, not established results)*:
1. Derive explicit functional form $g_{\mu\nu}[\rho_{\text{core}}, u_{\text{core}}, \text{orientations}]$
2. Identify a minimal test set (redshift, light bending, orbital precession) and the regimes where geodesics should shadow GR (Schwarzschild, FRW, etc.)—recovery of GR is a **design goal**, not yet an established result
3. Identify breakdown regimes and novel predictions

**Scale-separation criterion (GR vs. non-GR):**
- Define $\epsilon_{\text{geo}} \sim \ell_{\text{core}} / L_{\text{curv}}$, comparing core scale to curvature radius inferred from $\rho_{\text{core}}$.
- For $\epsilon_{\text{geo}} \ll 1$ and weak time-dependence of $\rho_{\text{core}}$, the effective connection from $e^a{}_\mu[\rho_{\text{core}}, u_{\text{core}}]$ should approximate a GR connection to $O(\epsilon_{\text{geo}}^2)$; use perihelion precession, Shapiro delay, and light bending to bound $\epsilon_{\text{geo}}$.
- For $\epsilon_{\text{geo}} \sim 1$ (near black-hole cores, sharp gradients, Planck-alignment layers), expect refractive/anisotropic deviations that are not describable by an Einstein metric sourced by a smooth stress-energy tensor.

This is **refractive gravity**: geodesics are Fermat paths in an inhomogeneous medium. Import machinery from **optical metrics and eikonal limits**.

---

## Energy, Conservation Laws, and the Noether Sea

**Locality and dominance:** All architrinos are in causal relation and can exchange energy in principle (kinetic and wake/bookkeeping energy), but finite field speed and distance falloff make local interactions **dominant**. Distant couplings are delayed and weak, so they contribute corrections rather than setting the primary dynamics. This dominance of local exchange is what allows stable assemblies and meaningful energy bookkeeping in practice.

**Maximal-curvature binary (MCB) and energy flow:** In a steady, phase-locked MCB orbit, each architrino’s kinetic energy is approximately constant over a cycle, while the “potential” is best treated as a time-dependent wake/history functional that oscillates but returns to its prior value when the loop closes. The binary generates a dynamic potential wake, but in the ideal periodic state this wake is predominantly **reactive** (near-field): it can exchange energy with nearby assemblies yet carries **zero net energy flux** over a cycle. Apparent energy export only arises when the loop is perturbed (asymmetry, gradients, dissipation), at which point part of the wake becomes **radiative** and the binary’s kinetic energy can change. Thus the MCB is a singularity preventer by trapping energy in a tight, self-consistent feedback loop, not by creating energy ex nihilo.

> **Example (black-hole core):** If binaries survive in the core, their rapid orbital motion contributes to the *internal* energy density of the core. The core “gains” energy only through compression and infall (more assemblies packed at tighter radii), not by creation. In a closed region, total energy remains conserved; the accounting shifts toward high-frequency orbital motion and wake energy concentrated in a dense volume.

**Potential and kinetic energy (step-by-step):**
1. **Kinetic energy (KE):** For each architrino $i$, define $K_i(t) = \tfrac{1}{2} m_i |\mathbf{v}_i(t)|^2$.
2. **Pairwise wake contribution:** For each ordered pair $(i,j)$, define a wake functional that depends on the emitter’s history and the receiver’s trajectory:

    $$
    W_{ij}(t) = \mathcal{W}\!\left[\{\mathbf{x}_j(t') : t' \le t\},\, \mathbf{x}_i(t)\right],
    $$

    with the delay roots $t_0 \in \mathcal{C}_j(t)$ setting the interaction geometry.
3. **Potential energy (PE):** The potential energy at time $t$ is the superposed wake bookkeeping:

    $$
    U(t) = \sum_i \sum_{j\ne i} W_{ij}(t).
    $$

    This is not a static scalar field at $\mathbf{x}$ but a history-dependent functional.
4. **Energy accounting:** The total energy is $E(t) = \sum_i K_i(t) + U(t)$; conservation follows from time-translation symmetry of the non-local action but must be verified for the explicit $\eta>0$ form of $\mathcal{W}$.

At higher levels, $U(t)$ coarse-grains into a local Noether-core volume gradient (assembly/core scale) and then into an effective refractive/metric field (continuum scale). The ontology shift is that PE is fundamentally geometry of causal history, with the familiar potential emerging by coarse-graining.

This step-by-step $U(t)$ construction is the concrete candidate for $E_{\text{wake}}$ in the next section.

> **Example (spherical wake and energy extraction):** A causal wake emitted on a spherical surface carries a fixed total flux $q = |e/6|$ and propagates indefinitely, but its influence dilutes with distance. The energy flux per area falls with radius, so each architrino only samples a small, weakening patch. Many receivers can interact with the same wake, yet the total extractable energy is bounded by what the wake carries; infinite propagation does not imply infinite energy.

### Path-History Energy Functional (Noether, Kolmogorov)

Standard energy conservation assumes instantaneous potentials. Here, the interaction law is **non-Markovian**: forces at $t$ depend on past trajectories via wake geometry, and the dominant contributions are local in timespace due to finite $c_f$ and distance falloff.

**Symmetry requirement**: Absolute time-translation invariance ($t \to t + \delta t$) in $\mathbb{R}^3 \times \mathbb{R}$ mandates a conserved energy functional even for delay systems. The conserved quantity is **not** simply $T+V(\mathbf{x})$ but a history functional over the delay segment. A schematic form is:
$$
H(t) = \sum_i \frac{1}{2}m_i v_i^2 + \frac{1}{2}\sum_{i,j}\int_{-\tau_{\max}}^0 \mathcal{E}_{ij}(h_t)\, d\theta,
$$
where the integral accounts for “potential in flight” carried by the causal wakes. This functional **is** the definition of $E_{\text{wake}}$ and must be derived from the action.

**Working action (η-regularized)**: Use the non-local action in `dynamics/master-equation.md` (Section 1.4) as the starting point. The Noether energy derived from time translations of that action is the explicit $E_{\text{wake}}$.

**History integral (path-integral form):** For the $\eta>0$ system, the working explicit form is
$$
E_{\text{wake}}(t) =
\frac{1}{2}\sum_{i,j} \kappa\,\sigma_{ij}\,|q_i q_j|
\int_{t-\tau_{\max}}^{t} dt_0\;
\frac{1}{r_{ij}^2(t; t_0)}\,
\delta_\eta\!\big(r_{ij}(t; t_0) - c_f(t - t_0)\big),
$$
which is the history (path) integral of causal-wake energy in flight. Prefactors and boundary terms should be confirmed by the full Noether derivation.

**Ontological clarification**: In this framework, "wake energy" is **not an independent field energy density living in the void**. It is the canonical history functional conjugate to time translations, derived from the non-local action. All energy ultimately resides in architrino kinetic and assembly-internal motion; $E_{\text{wake}}$ encodes how much of that capacity for kinetic change is geometrically allocated by past emissions but not yet realized. In periodic MCB states the wake is predominantly reactive (near-field) and carries no net energy flux; radiative components appear only when symmetry is broken.

**Self-hit interpretation**: When a particle intersects its own wake, energy transfers between the history bookkeeping and instantaneous kinetic energy. The "mass" of stable assemblies may be the **trapped energy of self-intersecting history loops**.

**Open problems**:
- Write the non-local action $S$ that yields the master equation and derive the exact conserved energy via time-translation symmetry.
- Express $E_{\text{wake}}$ explicitly (e.g., in pairwise $W_{ij}$ form) and verify conservation in the regularized $\eta > 0$ system.
- If conservation fails in practice, identify which assumptions break (regularization artifacts, missing terms, or explicit time dependence).
- Relate $E_{\text{wake}}$ to assembly binding energy and mass.

Whether we truly have conservative microdynamics affects the statistical framework (invariant measures, equilibrium) profoundly.

### Statistical Structure and Emergent Probability (Kolmogorov)

The deterministic delay dynamics, immense number of architrinos, and meta-stable branching points create highly complex attractor basins.

**Framework**: Define **invariant measures on trajectory space** (SRB-like measures for the delayed dynamical system) rather than on instantaneous state space.

**Target emergent probabilities**: Effective quantum-like statistics should arise from **typicality with respect to these measures** when observers are assemblies embedded in the same dynamics.

**Action item (make probability precise):** Define a concrete probability space and invariant measure for a minimal branching scenario.
1. Pick a minimal branching example (e.g., a tri-binary near a self-hit bifurcation with two attractors $A_1, A_2$).
2. Specify the sample space $\Omega$ (initial microstates or history segments on $[t_0-T, t_0]$ that include internal phase and local Noether Sea micro-configuration).
3. Define a measure $\mu$ on $\Omega$ (e.g., invariant measure for the local Sea microdynamics; uniform phase for internal angle).
4. Define the outcome map $\Phi:\Omega \to \{A_1, A_2\}$ as the attractor reached by deterministic evolution.
5. Define outcome probabilities as basin measures:
$$
P(A_k) = \mu\big(\Phi^{-1}(A_k)\big).
$$
Only after this can we ask whether $P(A_k)$ varies smoothly with macroscopic controls or reduces to $|\psi|^2$ in interference-like regimes.

**Status**: Whether a Born-rule form $P \propto |\psi|^2$ can be derived from typicality with respect to invariant measures over trajectory space is currently **conjectural**. It is a major target, not an assumption.

**Research path**:
1. Construct invariant measures for binaries/tri-binaries in background Noether Sea
2. Derive effective probability distributions from basin structure
3. Test whether typicality arguments yield Born-rule form in regimes where standard QM is well tested

**Failure mode**: If typicality arguments yield outcome weights that systematically deviate from $|\psi|^2$ in regimes where standard QM is well tested, the current microdynamics must be revised.

---

## Immediate Research Priorities

### Well-Posedness and Bifurcation Analysis (Poincaré, Tao)
- Prove local existence/uniqueness for the state-dependent delay system with finite $\eta$ (treat $\eta > 0$ as fundamental)
- Investigate $\eta \to 0$ limit via a weak/viscosity selection; if it fails, determine minimal physical $\eta$
- Validate simulations: as $\Delta t \to 0$, numerical trajectories must converge to the $\eta > 0$ dynamics
- Map phase space near $v = c_f$ bifurcation
- Classify attractor zoo for binaries and tri-binaries
- **HIGH PRIORITY**: Establish whether maximum-curvature orbits are robust attractors

### Emergent Metric Derivation (Cartan)
- Explicit functional form for $g_{\mu\nu}[\rho_{\text{core}}, u_{\text{core}}, \text{orientations}]$
- Geodesic equation and connection to operational measurements
- Define a minimal test set (redshift, light bending, orbital precession) and the regimes where GR should be reproduced (target effective theory)
- **Note**: GR recovery is a design goal, not yet established

### Assembly Atlas Construction (Thurston, Grothendieck)
- Topological classification of tri-binary configurations
- Moduli space structure and invariants
- Stability analysis (basins of attraction, escape times, Lyapunov spectra)
- Mapping from topology to physical properties (mass, charge, spin)
- Test robustness of maximum-curvature configurations

### Energy Functional and Conservation (Noether)
- Rigorous definition of wake energy $E_{\text{wake}}$ as a worldline functional (e.g., from pairwise $W_{ij}$)
- Attempt proof of conservation for isolated systems; if it fails, characterize deviations
- Connection to mass, binding energy, and stability
- Clarify ontological status: bookkeeping vs. substance

### Statistical Framework (Kolmogorov)
- Invariant measures on trajectory space
- Large-N continuum limits (hydrodynamic equations, kinetic theory)
- **Derivation of Born rule**: Test whether typicality yields $P \propto |\psi|^2$
- Identify parameter regimes where statistical predictions are testable

### Continuum Field Limits (Tao, Cartan)
- Rigorously derive Maxwell, Dirac, Yang-Mills as $N \to \infty$ with error bounds (target effective theories)
- Specify approximation hierarchies and breakdown regimes
- Connect to Cartan's effective metric structure
- Mark all derivations with their formal vs. controlled status

### Lorentz Suppression Mechanism ⚠️ **[HIGH RISK]**
The claim that assembly dynamics in the Noether Sea automatically produce Lorentz-like length contraction and time dilation (to $\lesssim 10^{-17}$ precision) is currently a **hypothesis**. If detailed assembly models fail to generate this suppression mechanically and exactly, the ontology with a detectable absolute frame will be falsified by existing experiments (Michelson-Morley, modern Lorentz-violation tests).

**Priority**: Frame this as a **group mismatch** problem (Galilean substrate vs Poincaré effective symmetry) and derive the Lorentz factor from the delay geometry. The required theorem: after a Galilean boost, the assembly relaxes to a new equilibrium whose internal clocks/rulers are isomorphic to the rest state **iff** the transformation uses $\gamma = 1/\sqrt{1-v^2/c_f^2}$. This should be derived from Doppler shifts in the causal feedback loop and action minimization, not imposed by hand.
**Cartan reformulation:** Under a substrate Galilean boost followed by relaxation, the effective tetrad should transform as
$$
\tilde e^a{}_\mu = \Lambda^a{}_b(\mathbf{v})\, e^b{}_\mu,\quad
\Lambda^a{}_b(\mathbf{v})\ \text{Lorentz with }\gamma = (1-v^2/c_f^2)^{-1/2}.
$$
This gives a concrete simulation diagnostic: reconstruct $e^a{}_\mu$ from internal periods and bond lengths of a moving tri-binary and test whether it transforms Lorentzian.
**Moduli-space test:** Treat the space of stable tri-binary configurations $\mathcal{M}_{TB}$ as a fiber bundle over velocity space. The Lorentz-suppression claim requires $\mathcal{M}_{TB}(\mathbf{v})$ to be canonically isomorphic to $\mathcal{M}_{TB}(\mathbf{0})$ only after rescaling the internal metric by $\gamma^{-1}$. If the fiber changes shape (e.g., inner/outer radius ratios drift) rather than scale, the particle changes identity under motion and the mechanism fails.

---

## Methodological Principles

### Explicit Regime Labeling
Every derivation must specify:
- Parameter regimes (densities, velocities, coupling strengths, $\eta$ values)
- Approximation assumptions (weak self-hit, large N, adiabatic, formal $\eta \to 0$ limit, etc.)
- Validity boundaries and breakdown conditions

### Status Discipline
Clearly distinguish:
- **Established results** (proven under stated assumptions)
- **Design goals / target theories** (GR recovery, Maxwell emergence, Born rule)
- **Conjectures** (maximum-curvature stability, energy conservation)
- **Open problems** (well-posedness in $\eta \to 0$ limit, Lorentz suppression mechanism)

### Terminology Discipline
Avoid deprecated terms and maintain clarity:
- ~~"Retarded"~~ → **"Path-history," "causal wake surface," "emission time"**
- ~~"Shell"~~ → **"Causal wake surface," "isochron"**
- ~~"Vacuum"~~ (alone) → **"Noether Sea," "Spacetime medium"**
- ~~"Curved space"~~ → **"Effective metric," "Refractive gravity"**
- Always qualify "spacetime": **"absolute timespace"** (substrate) vs **"effective spacetime/metric"** (emergent)

### Simulation Interface
All theoretical constructs must be:
- Translatable into simulation diagnostics
- Testable via numerical experiments
- Accompanied by convergence criteria and regularization parameters

### Falsifiability
Every major claim requires:
- Testable prediction
- Failure condition
- Uncertainty estimate
- Explicit marking of assumptions most vulnerable to falsification

---

## High-Risk Assumptions Requiring Priority Attention

The following architectural pieces are **most fragile** and require focused analytic/simulation effort:

### **Lorentz Suppression Mechanism** ⚠️ **[CRITICAL]**
-- **Claim**: Assembly dynamics rearrange symmetry so that internal clocks/rulers transform with the Lorentz factor, yielding effective Poincaré invariance to $< 10^{-17}$ precision
- **Status**: Hypothesis
- **Failure mode**: If assemblies do not naturally contract/dilate, absolute frame becomes operationally detectable → immediate falsification by existing experiments
- **Required**: Explicit derivation showing the boosted equilibrium is isomorphic to the rest state only under $\gamma$, from Doppler-shifted delay feedback and action minimization; equivalently, show the effective tetrad transforms as $\tilde e = \Lambda e$.

### **Maximum-Curvature Orbit Stability** ⚠️ **[CRITICAL]**
- **Claim**: Maximum-curvature configurations are robust attractors
- **Status**: Conjecture
- **Failure mode**: If typical perturbations cause secular drift rather than return to orbit, stable particle architecture collapses
- **Required**: Basin-of-attraction analysis, Lyapunov stability proof, long-time simulations

### **Energy Conservation**
- **Claim**: A conserved total energy $E_{\text{total}} = K + E_{\text{wake}}$ exists for isolated systems
- **Status**: Open problem
- **Failure mode**: If exact conservation fails, statistical framework (equilibrium, invariant measures) requires revision
- **Required**: Rigorous proof or counterexample

### **Born Rule Emergence**
- **Claim**: Typicality with respect to invariant measures yields $P \propto |\psi|^2$
- **Status**: Conjectural target
- **Failure mode**: Systematic deviations in well-tested QM regimes → microdynamics must be revised
- **Required**: Explicit derivation + numerical tests

---

## Unifying Perspective: Separation of Scales

The architecture operates at three coupled scales:

1. **Micro** ($\sim R_{\text{inner}}$): Discrete architrino dynamics, self-hit nonlinearity, delay feedback
2. **Meso** (tri-binary assemblies): Topology and geometry create stable structures (particles)
3. **Macro** (Noether Sea): Statistical ensembles yield effective fields and emergent effective spacetime

The mathematical challenge is to rigorously connect these scales:
- **Micro → Meso**: Stability analysis, attractor classification, topological protection
- **Meso → Macro**: Statistical mechanics, coarse-graining, continuum limits
- **Macro feedback**: Effective metric influences micro-dynamics via "gravitational" coupling

---

**End of Consolidated Observations (Second Draft)**

**Document Status**: Living reference for Geometry & Dynamics Working Group
