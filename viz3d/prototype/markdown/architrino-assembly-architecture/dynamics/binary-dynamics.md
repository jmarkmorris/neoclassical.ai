# Binary Dynamics

This chapter develops two-body architrino dynamics from the appearance of self-hit to stable binaries and their role as measurement standards. It then formalizes the maximum-curvature attractor analysis and closes with the state-space and conservation-law foundations that make the dynamics well-posed.

## Self-Hit: Definition and Diagnostics

Self-hit is the key non-Markovian feature of architrino dynamics. It occurs when an architrino interacts with potential it emitted earlier along its own worldline.

**Geometric condition (absolute coordinates):** For a given architrino with trajectory $\mathbf{x}(t)$, a self-hit event is a pair of times $(t_\text{emit}, t_\text{hit})$ with $t_\text{hit} > t_\text{emit}$ such that
$$
|\mathbf{x}(t_\text{hit}) - \mathbf{x}(t_\text{emit})| = c_f (t_\text{hit} - t_\text{emit}),
$$
and the architrino is the source of the causal wake surface emitted at $t_\text{emit}$.

**Dynamical role:**
- At low velocities ($v < c_f$), self-hit is rare or absent; dynamics are approximately Markovian.
- As velocities approach and exceed $c_f$, emission isochrons catch up with the emitter's future positions, generating nonlocal feedback and effective restoring or destabilizing forces depending on configuration.
- In generic trajectories, once a particle has exceeded $c_f$ and emitted wakes in that regime, it can later slow below $c_f$ and still experience self-hits from those earlier emissions; self-hit is a path-history effect, not tied solely to the instantaneous speed.
- For binary and tri-binary assemblies, repeated self-hit events can prevent collapse, lock in stable radii and frequencies, and create new limit cycles and attractors.

**Simulation & diagnostics:**
- Use virtual-observer provenance tables to record, for each self-hit: $(t_\text{emit}, \mathbf{x}(t_\text{emit}))$, $(t_\text{hit}, \mathbf{x}(t_\text{hit}))$, impact parameters, and force contributions.
- Check convergence of self-hit statistics under time-step refinement, history-resolution refinement, and integrator swap.
- If self-hit signatures change qualitatively under refinement, treat any resulting "stable structures" as artifacts until proven otherwise.

For the circular-geometry details (principal angles, winding numbers, discrete self-hit branches), see **Setup and Notation (Symmetric Frame)** in **Maximum-Curvature Limit and Attractor Analysis**.

With self-hit defined, we turn to the simplest assembly where it drives the dynamics: the orbiting binary.

## Orbiting Binary Assembly

An orbiting binary is the simplest emergent assembly, consisting of two architrinos of opposite charge--an electrino and a positrino. With charges $-\epsilon$ and $+\epsilon$, the assembly is electrically neutral overall. This system demonstrates the fundamental principles of interaction, including the consequences of delayed potential and the role of the field-speed symmetry point.

### 1. System Definition and Equations of Motion

Consider the ideal case of a symmetric orbit in a universe with no other architrinos. In general, each architrino is subject to a superposition of external potential waves from all other sources; the analysis below isolates the binary by setting those external contributions to zero.

Let the electrino be particle 1 and the positrino be particle 2.
-   **Positions:** $\mathbf{s}_1(t)$ and $\mathbf{s}_2(t)$
-   **Charges:** $q_1 = -\epsilon$ and $q_2 = +\epsilon$

The motion of each particle is determined by the field emitted by the other at a delayed time. The acceleration of the electrino (particle 1) at time $t$ is caused by the positrino's (particle 2) field emitted at an emission time $t_0$. This is governed by the interaction condition:
$$
\|\mathbf{s}_1(t) - \mathbf{s}_2(t_0)\| = c_f(t - t_0)
$$
The acceleration vector for the electrino is attractive, pointing towards the positrino's delayed position:
$$
\mathbf{a}_1(t) \propto -\hat{\mathbf{r}}_{21} = - \frac{\mathbf{s}_1(t) - \mathbf{s}_2(t_0)}{\|\mathbf{s}_1(t) - \mathbf{s}_2(t_0)\|}
$$
A symmetric set of equations governs the positrino's motion based on the electrino's emissions.

### 2. The Inward Exponential Spiral

In the strictly sub-field-speed regime (no self-interaction, $|\mathbf{v}|\le c_f$), a stable, circular orbit is impossible. Because the attractive force on each particle points to the *past* position of its partner, it is not a true central force. This delay yields an **inward spiral that is naturally modeled as exponential in angle** (a logarithmic spiral), consistent with a per-cycle action increment $\Delta J = h$ in the partner-only regime. The radius shrinks geometrically per turn and speed increases until the self-interaction threshold ($|\mathbf{v}|>c_f$) is crossed.

**Lemma (No stable circular orbit for $v < c_f$).** In circular motion, $v=s=R\omega$. In the partner-only regime, the per-hit tangential component satisfies
$$
T_p \propto \frac{\sin(\delta_p/2)}{\cos^2(\delta_p/2)} > 0 \quad (0<\delta_p<\pi),
$$
where $\delta_p$ is the partner delay angle. The time-averaged tangential acceleration cannot vanish; a constant-speed circular orbit is impossible.

-   The tangential component of the delayed force sustains the orbital motion.
-   The radial component continuously pulls the particles closer together.

With perfectly symmetric initial conditions (e.g., starting at rest), the paths of the electrino and positrino are distinct but perfect mirror images of each other. As they spiral inward, their speeds continuously increase. Emission cadence and per-wavefront amplitude remain constant; the evolution is driven entirely by delay geometry and, once active, self-interaction.

### 3. Evolution Through Velocity Regimes

The binary system's evolution is organized around the **field-speed symmetry point** $v=c_f$. This is a **hinge** where the causal structure changes: below $c_f$ only partner-delay forces exist, while above $c_f$ self-hit roots appear. The hinge is not a hard barrier; it is a change in **root count**. The transition is smooth as long as the delay roots remain simple (no "causal shock"), which in the symmetric spiral/circular geometry is generically satisfied. At the hinge the principal self-hit branch appears with a small delay angle ($\tilde{\delta}_s\to 0^+$), which geometrically means the self-hit emission point lies almost directly behind the current position. The radial factor scales like $1/\sin(\tilde{\delta}_s/2)$ and therefore becomes very large as $\tilde{\delta}_s\to 0^+$. This large outward term initially reduces curvature; the maximum-curvature regime does not occur near threshold but only after $\tilde{\delta}_s$ becomes appreciable (higher $s$ and larger-angle roots).

> **Black Box: Surfing the moving wave (lanes under translation and perturbation)**
>
> Picture the orbit as a surfer riding a **moving wave**, not a fixed landscape. The "wave" is the delay geometry: as the architrino moves, the causal roots reshape the force it feels. There is no static trough; there are **stable lanes**--recurring orbital patterns that can persist even while the whole assembly **translates through the Noether sea**.
>
> As the spiral tightens toward $v=c_f$, the wave develops a sharp **crest**: the first self-hit root appears with $\tilde{\delta}_s \to 0^+$, and the outward radial factor scales like $1/\sin(\tilde{\delta}_s/2)$. That crest is a geometry-driven defocusing surge, not a barrier. The architrino surfs through because tangential drive continues to push it forward. **Lane changes can occur both before and after the crest**; in the spiral case the evolution is continuous in state (C0) but has a **kink** in slope at $v=c_f$ rather than a discontinuous jump.
>
> Past the crest, the wave face relaxes. $\tilde{\delta}_s$ grows, additional self-hit branches open, and outward push spreads over larger angles. This is where **lane changes** remain possible: small energy shifts or **external perturbations** can move the system from one stable orbital lane to another (binary, tri-binary, decorator, photon-like), even though the whole assembly is drifting. The local orbit changes lanes; the global translation continues.
>
> **Working guess (speculative):** in the self-hit regime the effective "quantum jump" scale may be $2h$ rather than $h$, because two accelerating contributions (partner delay and self-hit) act together. If the inward track is well-approximated by a logarithmic spiral (exponential in angle), this would appear as a **kink** in the log-spiral slope at the hinge: $\Delta J = h$ below $c_f$, $\Delta J = 2h$ above. This is a hypothesis, not a derived result.

> **Black Box: Equation of motion near the hinge ($v \approx c_f$)**
>
> For each architrino $i$ interacting with its partner $j$:
> $$
> \ddot{\mathbf{x}}_i(t)=\mathbf{a}_{i,j}(t;\{t_{p,k}\})+H(s-1)\,\mathbf{a}_{i,i}(t;\{t_{s,m}\})+\mathbf{a}_{\text{ext}}(t),
> $$
> with delay constraints (causal roots):
> $$
> \|\mathbf{x}_j(t_{p,k})-\mathbf{x}_i(t)\|=c_f\,(t-t_{p,k}), \quad
> \|\mathbf{x}_i(t_{s,m})-\mathbf{x}_i(t)\|=c_f\,(t-t_{s,m}),
> $$
> and $s=|\mathbf{v}|/c_f$. For symmetric, non-translating circular geometry, the delay angles satisfy
> $$
> \delta_p=2s\cos(\delta_p/2), \qquad \delta_s=2s\sin(\delta_s/2),
> $$
> with no self-hit solution for $s\le 1$ and a small-root branch $\tilde{\delta}_s\to 0^+$ for $s>1$. The radial/tangential split then reads
> $$
> \ddot r-r\dot\theta^2=A_{\text{rad}}(\delta_p,\delta_s), \qquad r\ddot\theta+2\dot r\dot\theta=T(\delta_p,\delta_s).
> $$
> The symmetry breaking at the hinge is geometric: as $\tilde{\delta}_s\to 0^+$ the self-hit radial factor scales like $1/\sin(\tilde{\delta}_s/2)$, turning on a large outward term while the state remains continuous.

#### **Contraction Phase ($|\mathbf{v}| \le c_f$)**
Initially, and as long as the speeds of both particles are less than or equal to the field speed $c_f$, they are only influenced by their partner's attractive field. The total acceleration is simply the attractive force:
$$
\mathbf{a}_{1, \text{total}}(t) = \mathbf{a}_{1,2}(t) \quad \text{and} \quad \mathbf{a}_{2, \text{total}}(t) = \mathbf{a}_{2,1}(t)
$$
During this phase, the system is purely contractile, with the particles accelerating and spiraling towards each other. The positive tangential component (see Lemma in the prior section) guarantees continued speed-up, so the spiral tightens until the self-hit regime is reached.

#### **Deflationary Phase ($|\mathbf{v}| > c_f$)**
Once the particles' speeds exceed the field speed $c_f$, they cross the symmetry point and begin to interact with their own recently emitted, repulsive wakes. The total acceleration on each particle now becomes a superposition of attraction from its partner and self-repulsion. For the electrino:
$$
\mathbf{a}_{1, \text{total}}(t) = \mathbf{a}_{1,2}(t) + \mathbf{a}_{1,1}(t)
$$
At $|\mathbf{v}| > c_f$, a principal self-hit branch ($m=0$) becomes available; at higher speeds, additional branches turn on (see **Self-Hit Multiplicity vs. Speed**). The new self-repulsive term, $\mathbf{a}_{1,1}(t)$, grows rapidly as the path curvature increases; near threshold this outward term defocuses the spiral before tighter, multi-root dynamics can set in. We call this the **deflationary** phase because, while the spiral can continue to tighten, self-repulsion increasingly "deflates" the effective inward pull and can -- in principle -- halt further radial contraction. In the later part of this phase (once $\tilde{\delta}_s$ is large and multiple roots are active), self-interaction may enable approach to the conjectured limiting circular state while preventing singular collapse, but overshoot or destabilization remain possible. Whether this regime actually settles into a limit cycle, or instead overshoots and exhibits sustained oscillations or escape, is an open dynamical question addressed explicitly in the MCB gap ledger.

### 4. The Stable State and Emergent Properties

**Conditional note:** The statements in this section assume the maximum-curvature attractor conjecture; see the gap ledger in **Maximum-Curvature Limit and Attractor Analysis**. Under that assumption, the deflationary spiral does not continue indefinitely and self-repulsive feedback is expected to stabilize the system and prevent a singularity.

#### **Curvature Limit and Stability**
In the working hypothesis, the inward spiral does not end in a singularity. The limiting factor is expected to be the geometry of self-interaction. As the spiral tightens, the path's curvature increases, bringing each architrino closer to its own recent emission points. This proximity dramatically amplifies the self-repulsive force. The system reaches a critical state where any further decrease in orbital radius would cause an overwhelming increase in this self-repulsion, effectively creating a "pressure" that resists further collapse. The inward spiral is halted not by a simple balance of forces, but by this geometric feedback loop. Ruling out true collapse or runaway in the regularized dynamics is the content of gap item MCB-09 (global energy bound). Until that is addressed, singular end-states remain a formal possibility.

Here and below, "potential" or "pressure" is shorthand for deferred work encoded in the path-history of wakes (the Master Equation energy functional), not an instantaneous $U(r)$.

In this picture, the trajectory stabilizes into a **stable, circular orbit of a minimum radius**. This final state is a dynamic equilibrium where the inward pull from the partner is channeled into circular motion while self-repulsion prevents further tightening of the path's curvature. Any minimum-radius circular state occurs only once self-interaction is active ($|\mathbf{v}|>c_f$); in the strictly sub-field-speed regime ($|\mathbf{v}|\le c_f$) no stable circular orbit exists.

#### **Emergent Properties**
The stabilization of the orbiting binary gives rise to fundamental, emergent properties for the universe:
-   No intrinsic speed cap at the architrino level; the assembly imposes an apparent speed bound (group constraints and $d_0$, $t_0$). At the assembly level this practical speed cap is what physical observers infer as a fundamental "speed of light"; it is an emergent consequence of binary/tri-binary structure, not a kinematic axiom of the void.
-   **An Emergent Unit of Distance:** The radius of this stable orbit is a constant, determined by the fundamental parameters of the model (field speed $c_f$, charge $\epsilon$). It serves as the smallest possible orbital radius and thus becomes a natural, emergent unit of distance.
-   **An Imposed Speed Limit:** While individual architrinos have no inherent speed limit, the particles within this stable assembly are constrained to a specific, constant orbital speed. This creates a practical speed limit for particles bound within such structures.
-   **A Zero-Potential Axis (Idealized):** In the ideal symmetric, non-translating, exactly circular orbit, and under linear superposition, the contributions from the two charges cancel almost exactly along the rotation axis, producing a corridor of very low net potential. In that idealization, an architrino traveling perfectly along this axis would experience negligible acceleration from the binary. In practice, discrete-wake geometry, translation, or slight asymmetry will leave residual off-axis hits, so the corridor is approximate rather than exact.

---

**Note on Complex Scenarios:** The analysis above describes a stationary binary system. More complex dynamics arise when the binary assembly is also translating through space, especially when the axis of orbit is not aligned with the direction of the group's velocity.

---

**Falsification signals (two-body level):**
- If high-resolution simulations of isolated opposite-charge pairs never show long-lived bounded orbits for any initial conditions, the stable-binary/MCB hypothesis fails.
- If all inward spirals either (a) collapse to unphysical radii despite regularization, or (b) blow out to infinity without forming a limit cycle, the self-hit stabilization mechanism is wrong or incomplete.
- If, after including all causal roots in the pure two-body kernel, the time-averaged tangential acceleration remains strictly positive for every bounded near-circular trajectory, then an MCB limit cycle cannot exist without additional physics; the current force law is insufficient.

---

## Maximum-Curvature Limit and Attractor Analysis

Once self-hit turns on, the natural question is whether the spiral-in converges to a limiting curvature. We call the candidate limit the **maximum-curvature binary (MCB)**. This section collects the full two-body, self-hit analysis for that candidate, including delay geometry, force components, stability criteria, and computational diagnostics. It is the canonical reference for MCB attractor status.

All claims of MCB stability and unit-definition are conditional on the conjectures and tests summarized in the gap ledger below.

MCB stability claims rely on the well-posedness of the regularized SD-NDDE. In this chapter we treat $\eta > 0$ as fixed and defer the $\eta \to 0$ limit to the MCB gap ledger (MCB-07). The formal state-space framework appears in **State Space and Well-Posedness of the Delayed Two-Body System**.

## Maximum-Curvature Circular Orbit (Opposite Charges)

**Goal**: Characterize the circular, constant-speed, constant-radius configuration of two opposite-charge architrinos and investigate where curvature $\kappa = 1/R$ is maximized. We work in units with field speed $c_f = 1$ and use the canonical delayed, purely radial per-hit law.

**Plain language**: We seek the tightest (smallest-$R$) steady circle an opposite-charge pair can trace when the only forces come from delayed, radial interactions with the partner (multiple-hits) and from one's own past emissions (self-hits, active only when speed exceeds field speed).

---

### Foundational Context (Ontological Clarification)

#### The maximum-curvature binary (MCB) as Fundamental Unit

The architecture hypothesizes that the **maximum-curvature binary (MCB)** would be the **inner binary** of a tri-binary assembly, stabilized by self-hit dynamics when $v > c_f$. Contingent on Conjectures A/B, it would define the **fundamental physical units**:

- **Length standard**: The orbital radius $r_{\text{min}}$ of the MCB would be the **prototype rod**.
- **Time standard**: The orbital period $T_{\text{MCB}} = 1/f_{\text{MCB}}$ would be the **prototype clock tick**.

If realized, the MCB radius $r_{\text{min}}$ is expected to be determined by the balance of:
1. Coulomb-like attraction between opposite charges ($\propto |e/6|^2 / r^2$),
2. Self-hit repulsion (non-Markovian feedback when $v > c_f$),
3. Centripetal requirement for stable circular orbit.

**Expected scale (if realized)**: $r_{\text{min}} \sim 10^{-15}$ to $10^{-12}$ m (classical electron radius to Compton wavelength).

**Dynamical priority (attractor status):** The architecture hypothesizes the MCB is a **robust attractor**, not a finely tuned periodic orbit. This must be established explicitly:
- Start from a reduced two-body model (opposite charges, self-hit enabled, explicit $\eta$).
- Construct a Poincare map (e.g., strobing at orbital phase) and locate the MCB as a fixed point.
- Compute Floquet multipliers / Lyapunov exponents and map the basin of attraction under perturbations in radius, phase, and velocity.
Only if the multipliers lie strictly inside the unit circle and the basin is non-trivial do we have the attractor the architecture relies on. If neutrality or instability is found, the tri-binary ladder and Noether-core claims must be downgraded or the interaction law revised (e.g., additional damping/medium effects).

#### Relationship to Tri-Binary Structure

- **Inner binary** (MCB): $v > c_f$; self-hit stabilized; **would define fundamental units**.
- **Middle binary**: **always** at $v = c_f$ with **variable radius/frequency**; symmetry-breaking threshold and **energy-storage fulcrum**; defines effective light speed $c_{\text{eff}}$.
- **Outer binary**: $v < c_f$; expansion/contraction modes; **couples to Noether sea** for gravitational/cosmological effects.

**This chapter analyzes the isolated two-body problem to understand candidate MCB formation and stability.**

---

### Setup and Notation (Symmetric Frame)

- **Two architrinos** with charges $q_1 = -\epsilon$ and $q_2 = +\epsilon$ (where $\epsilon = |e/6|$).
- **Equal-time positions** (in absolute time $t$) are diametrically opposite on a circle of radius $R$ about the midpoint.
- **Uniform circular motion**: Angular speed $\omega$, constant tangential speed $s = R\omega$.
- **Non-translating binary**: Circle center (midpoint) is fixed in Euclidean 3D space; no net translation.

Let $C_i(t_\text{emit})$ denote the causal wake surface emitted by architrino $i$ at emission time $t_\text{emit}$. For uniform circular motion, self-hit events are discrete intersections between the worldline and its own wake surfaces. Define the **principal self-delay angle** $\tilde{\delta}_s \in (0, \pi]$ as the minimal angular separation between the current position and the emission point that yields a hit. Additional self-hits occur at longer delays indexed by winding number $m \ge 0$, giving a discrete family $\delta_s(m) = \tilde{\delta}_s + 2\pi m$.

#### Phase Angles and Delays

Let $\delta_s$ and $\delta_p$ denote the angular phase separations (measured along the circle) between:
- **Self** (same particle): Current position -> its own past emission position that hits "now."
  - Delay time: $\tau_s$; angular separation: $\delta_s = \omega \tau_s$.
  - Chord length: $r_s = 2R \sin(\delta_s / 2)$.
  
- **Partner** (other particle): Current position -> partner's past emission position that hits "now."
  - Delay time: $\tau_p$; angular separation: $\delta_p = \omega \tau_p$.
  - Chord length: $r_p = 2R \cos(\delta_p / 2)$.

#### Causal-Time Constraints (Field Speed $c_f = 1$)

For a signal to travel from emission point to reception point:
$$
r = c_f \cdot \tau \quad \Rightarrow \quad r = \tau \quad \text{(in units where } c_f = 1\text{)}.
$$

This yields two delay equations:

1. **Self-hit**:
   $$
   \delta_s = \omega \tau_s = \omega \cdot r_s = \omega \cdot 2R \sin(\delta_s / 2) = 2s \sin(\delta_s / 2).
   $$

2. **Partner hit**:
   $$
   \delta_p = \omega \tau_p = \omega \cdot r_p = \omega \cdot 2R \cos(\delta_p / 2) = 2s \cos(\delta_p / 2).
   $$

**These two transcendental equations determine** $(\delta_s, \delta_p)$ **as functions of speed** $s$.

**Critical threshold**: Self-hits exist only when $s > 1$ (i.e., $v > c_f$). For $s \le 1$, no self-hits occur.

---

#### Terminology: Roots and Winding Numbers

**Root**: An emission time $t_0 < t$ (from either self or partner) that satisfies the causal constraint $r = c_f (t - t_0)$ and produces a hit at reception time $t$.

**Integer-indexed older roots (winding numbers)**:

Let $\tilde{\delta}_s \in (0, \pi]$ and $\tilde{\delta}_p \in (0, \pi]$ denote the **minimal (principal) angular separations** that determine the chord lengths and force directions.

The full families of causal delays are:

- **Self**: 
  $$
  \delta_s(m) = \tilde{\delta}_s + 2\pi m = 2s \sin(\tilde{\delta}_s / 2), \quad m = 0, 1, 2, \dots
  $$
  
- **Partner**: 
  $$
  \delta_p(m) = \tilde{\delta}_p + 2\pi m = 2s \cos(\tilde{\delta}_p / 2), \quad m = 0, 1, 2, \dots
  $$

**Geometric interpretation**:
- The minimal separations $\tilde{\delta}_s$, $\tilde{\delta}_p$ determine the **geometry** (chord lengths, force directions).
- The winding index $m$ affects **timing/ordering** of multiple hits but does not change the **sign** or **direction** of force components (all derived from principal geometry).

---

### Per-Hit Directions and Force Components

#### Local Coordinate Frame at Receiver

- **Radial outward**: $\hat{e}_r$ (from rotation center toward receiver).
- **Tangential**: $\hat{e}_t$ (direction of motion along circle).

#### Unit Directions of Lines of Action (Emission -> Reception)

**Self-hit**:
$$
\hat{u}_s = \sin(\delta_s / 2) \, \hat{e}_r + \cos(\delta_s / 2) \, \hat{e}_t.
$$

**Partner hit** (geometric chord across circle):
$$
\hat{u}_p = \cos(\delta_p / 2) \, \hat{e}_r - \sin(\delta_p / 2) \, \hat{e}_t.
$$

#### Canonical Per-Hit Accelerations

Using the delayed, radial law with magnitude $\kappa \epsilon^2 / r^2$ (where $\kappa$ is a coupling constant and $\epsilon = |e/6|$):

**Self-hit** (like charges -> repulsive):
$$
\mathbf{a}_s = +\kappa \epsilon^2 \frac{1}{r_s^2} \hat{u}_s.
$$

**Partner hit** (opposite charges -> attractive):
$$
\mathbf{a}_p = -\kappa \epsilon^2 \frac{1}{r_p^2} \hat{u}_p.
$$

---

#### Radial and Tangential Components

Define **inward radial** as positive (toward center) and **tangential** as positive in direction of motion.

**Chord lengths**:
$$
r_s = 2R \sin(\delta_s / 2), \quad r_p = 2R \cos(\delta_p / 2).
$$

**Inward radial components**:

- **Self** (repulsive -> outward -> negative):
  $$
  A_{s,\text{rad}} = -\kappa \epsilon^2 \frac{\sin(\delta_s / 2)}{r_s^2} = -\frac{\kappa \epsilon^2}{4R^2 \sin(\delta_s / 2)}.
  $$

- **Partner** (attractive -> inward -> positive):
  $$
  A_{p,\text{rad}} = +\kappa \epsilon^2 \frac{\cos(\delta_p / 2)}{r_p^2} = +\frac{\kappa \epsilon^2}{4R^2 \cos(\delta_p / 2)}.
  $$

**Net inward radial acceleration**:
$$
A_{\text{rad}} = \frac{\kappa \epsilon^2}{4R^2} \left( \frac{1}{\cos(\delta_p / 2)} - \frac{1}{\sin(\delta_s / 2)} \right).
$$

**Tangential components** (both non-negative for $0 < \delta_s, \delta_p < \pi$):

- **Self**:
  $$
  T_s = +\kappa \epsilon^2 \frac{\cos(\delta_s / 2)}{r_s^2} = \frac{\kappa \epsilon^2 \cos(\delta_s / 2)}{4R^2 \sin^2(\delta_s / 2)}.
  $$

- **Partner**:
  $$
  T_p = +\kappa \epsilon^2 \frac{\sin(\delta_p / 2)}{r_p^2} = \frac{\kappa \epsilon^2 \sin(\delta_p / 2)}{4R^2 \cos^2(\delta_p / 2)}.
  $$

**Net tangential acceleration**:
$$
T = T_s + T_p \ge 0.
$$

---

#### Sub-Field-Speed Simplification ($s \le 1$; No Self-Hits)

When $s \le 1$, self-hits do not occur ($\delta_s$ has no solution). Only the partner contributes:

$$
T(s < 1) = T_p = \frac{\kappa \epsilon^2}{4R^2} \frac{\sin(\delta_p / 2)}{\cos^2(\delta_p / 2)}.
$$

Using the delay relation $\delta_p = 2s \cos(\delta_p / 2)$:

$$
T(s < 1) = \frac{\kappa \epsilon^2 s^2}{R^2} \frac{\sin(\delta_p / 2)}{\delta_p^2} > 0.
$$

**Interpretation**: Even at sub-field speeds, there is always a **net positive tangential force** (accelerating the binary). This prevents a truly stable, constant-speed circular orbit.

---

### Requirements for True Circular Orbit (Working Hypothesis)

For uniform circular motion at fixed radius $R$ and constant speed $s$:

1. **Centripetal balance**:
   $$
   A_{\text{rad}} = \frac{s^2}{R}.
   $$

2. **Net-zero tangential power** (constant speed on average):
   $$
   \langle T \rangle = 0.
   $$

---

#### Apparent Obstruction: Non-Negativity of Tangential Components

**Key Result**: For the symmetric, non-translating two-body circle geometry, and for **any** single causal root (including all older roots with winding index $m \ge 0$), the tangential components satisfy:

$$
T_s \ge 0, \quad T_p \ge 0 \quad \Rightarrow \quad T = T_s + T_p > 0.
$$

**Conclusion (provisional)**: The per-hit analysis yields $T \ge 0$ for every root. Because all roots for a given speed have the same sign of tangential projection (the chords all lean the same way), the **bare two-body kernel tends to monotonically increase orbital speed at fixed radius**. A genuine $\langle T \rangle = 0$ circle from this kernel alone would require **nontrivial** geometric/time-averaged cancellation across many roots; it is not guaranteed. The existence of an MCB in the pure two-body system is therefore a conjecture that must be directly tested; if simulations fail to find such a cycle, the architecture must invoke either additional physics (e.g., medium coupling, radiation, velocity dependence) or a modified interaction law.

- **Nontrivial multi-root cancellation** from geometry/time-weighting across roots,
- **Additional interactions** that provide negative tangential work on average (medium coupling, radiation, velocity dependence),
- **Multi-body stabilization** (tri-binary structure with nested pairs) that changes the root geometry.

**Plain language**: The isolated pair shows persistent tangential drive at the per-hit level; cancellation is hard because every root pushes the same way. A steady circle must come from exceptional multi-root averaging or from extra physics beyond the bare kernel. This is a primary test of the MCB attractor hypothesis.

---

### What "Maximum Curvature" Demands

From the radial component formula:

$$
A_{\text{rad}} = \frac{\kappa \epsilon^2}{4R^2} \left( \frac{1}{\cos(\delta_p / 2)} - \frac{1}{\sin(\delta_s / 2)} \right).
$$

**Increasing curvature** ($\kappa = 1/R$ larger -> $R$ smaller) requires **stronger inward radial force**. This occurs when:

1. **$\delta_p$ increases** -> $\cos(\delta_p / 2)$ decreases -> partner term $1/\cos(\delta_p / 2)$ **increases** (stronger inward pull).
2. **$\delta_s$ increases** -> $\sin(\delta_s / 2)$ increases -> self term $1/\sin(\delta_s / 2)$ **decreases** (weaker outward repulsion).

**Critical observation**: Near the self-hit threshold ($s \to 1^+$, $\delta_s \to 0^+$):

$$
\frac{1}{\sin(\delta_s / 2)} \to \infty \quad \text{(strong outward repulsion)}.
$$

Therefore, **just-above-threshold self-hits do not maximize curvature**--they **strongly oppose** it by blowing up the outward radial component.

**Maximum curvature** (smallest stable $R$) likely occurs at **higher speeds** ($s \gg 1$) where:
- Multiple self-hits ($m \ge 1$) are active,
- $\delta_s$ is large (approaching $\pi$),
- Outward self-repulsion is minimized while inward partner attraction is maximized.

**However**: Due to the per-hit $T > 0$ result, this "maximum curvature" state is a **hypothesis** for the isolated two-body system. Its stability must be verified by the full, multi-root time-averaged dynamics.

---

### Self-Hit Multiplicity vs. Speed

**Definition**: A self-hit is an emission time from the same architrino that satisfies the causal constraint $r = (t - t_0)$ and arrives "now." In uniform circular, non-translating geometry, admissible self-roots are indexed by winding number $m \ge 0$ and minimal angular separation $\tilde{\delta}_s \in (0, \pi]$:

$$
\delta_s = \tilde{\delta}_s + 2\pi m = 2s \sin(\tilde{\delta}_s / 2).
$$

#### Counting Self-Hits by Winding Index

A new self-hit branch (for winding $m$) appears when:

$$
s \ge s_m^\star = \frac{(2m + 1) \pi}{2}.
$$

Therefore, the number of distinct self-hits at speed $s$ is:

$$
N_{\text{self}}(s) = \begin{cases}
0, & s \le 1, \\
1 + \max\!\left(0, \left\lfloor \frac{s}{\pi} - \frac{1}{2} \right\rfloor \right), & s > 1.
\end{cases}
$$

**Examples**:

- $1 < s < 3\pi/2 \approx 4.712$ -> $N_{\text{self}} = 1$ (only $m = 0$).
- $s \ge 3\pi/2$ -> $N_{\text{self}} \ge 2$ ($m = 0$ and $m = 1$).
- Higher $m$ branches turn on at $s \ge 5\pi/2$, $7\pi/2$, etc.

**Note**: Straight-line motion admits **no self-hits** even if $s > 1$; **curvature is required**. The above statements apply specifically to uniform circular, non-translating geometry.

---

### Where Do Causal Hits Come From on the Circle? (Discrete Azimuth Pattern)

**Context**: Non-translating, uniform circular binary at fixed speed $s$. Receiver "now" at azimuth $\theta = 0$.

The emission points on the circle that can produce hits "now" form a **finite, discrete set** of azimuths determined by the delay equations--**not arbitrary locations**.

#### Partner Hits

- Minimal angular separation: $\tilde{\delta}_p \in (0, \pi]$.
- Causal delays:
  $$
  \delta_p(m) = \tilde{\delta}_p + 2\pi m = 2s \cos(\tilde{\delta}_p / 2), \quad m = 0, 1, 2, \dots
  $$

- **Emission azimuth** at reception:
  $$
  \varphi_p(m; s) = \pi - \tilde{\delta}_p(m; s).
  $$

- **Existence thresholds**: For each $m \ge 0$, a solution exists only if $s > m\pi$.
- As $m$ increases, $\tilde{\delta}_p$ decreases -> $\varphi_p$ drifts monotonically toward $\pi$ (diametrically opposite point).

#### Self-Hits

- Minimal angular separation: $\tilde{\delta}_s \in (0, \pi]$.
- Causal delays:
  $$
  \delta_s(m) = \tilde{\delta}_s + 2\pi m = 2s \sin(\tilde{\delta}_s / 2), \quad m = 0, 1, 2, \dots
  $$

- **Emission azimuth** at reception:
  $$
  \varphi_s(m; s) = -\tilde{\delta}_s(m; s).
  $$

- **Existence windows**:
  - Principal branch ($m = 0$): exists only for $1 < s \le \pi/2$; terminates at $\tilde{\delta}_s = \pi$ when $s = \pi/2$.
  - For $m \ge 1$: new branch appears when
    $$
    s \ge s_m^\star = \frac{(2m + 1) \pi}{2}.
    $$
  - Within a branch, $\tilde{\delta}_s$ decreases with $s$ -> $\varphi_s$ drifts toward $-\pi$.

#### Multiplicity and Pattern

- At any fixed $s$, the admissible emission azimuths form a **finite, ordered "comb"** of discrete points.
- These points accumulate toward the diametric opposite direction:
  - $\varphi = \pi$ for partner,
  - $\varphi = -\pi$ for self.
- As $s$ increases, the set grows in **steps** at the thresholds above; more roots appear but they **never fill the circle**.
- Multiple hits at the same "now" correspond to different winding indices $m$ (and occasionally multiple $\tilde{\delta}_s$ solutions within a branch); all are fixed by the delay equations and circle geometry.

**Plain language**: For a given speed, hits come from a **short list of specific angles** set by causality and delay--not from arbitrary points all around the circle. Going faster unlocks more of these specific angles at predictable threshold speeds.

---

### Practical Recipe (Computational)

To explore the two-body circular dynamics numerically:

1. **Pick a speed** $s > 1$ (to activate self-hits).

2. **Solve the delay equations**:
   $$
   \delta_s = 2s \sin(\delta_s / 2), \quad \delta_p = 2s \cos(\delta_p / 2),
   $$
   for $(\delta_s, \delta_p) \in (0, \pi]$ (principal solutions).

3. **Enumerate causal roots** by winding index $m \ge 0$:
   - Use minimal angular separations $\tilde{\delta}_s$, $\tilde{\delta}_p$ to compute chord lengths and force components.
   - Winding index $m$ affects emission timing/ordering but not the sign or direction of components (all derived from principal geometry).

4. **Compute radial and tangential accelerations**:
   $$
   A_{\text{rad}}(s), \quad T(s).
   $$
   Verify that $T(s) > 0$ (no constant-speed equilibrium without external physics).

5. **Identify speed regimes**:
   - Near $s \to 1^+$: Strong outward self-repulsion ($1/\sin(\delta_s/2) \to \infty$) -> low curvature.
   - Higher $s$ ($s \gg 1$): Multiple self-hits active; $\delta_s$ large -> outward repulsion minimized -> higher curvature possible (but still not stable due to $T > 0$).

---

### MCB Attractor Hypothesis and Test Plan

**Working hypothesis**: An isolated electrino--positrino pair spirals inward until self-hit feedback halts the collapse and a steady circular orbit forms at $r_{\text{min}}$. This is the MCB, and it would be a natural attractor of the two-body delay dynamics.

#### Mechanism and geometric expectations

The hypothesis has three dynamical phases. In the spiral-in phase ($v < c_f$), partner attraction dominates, the net tangential drive is positive, and the radius decreases while speed rises. Once self-hits activate ($v > c_f$), non-Markovian feedback begins to oppose further collapse. In the MCB regime ($v \gg c_f$), radial self-repulsion is minimized while partner attraction accumulates across multiple causal roots; the orbit stabilizes at maximal curvature if the time-averaged tangential drive satisfies $\langle T \rangle \approx 0$.

Two geometric expectations follow. The MCB is not realized near the self-hit threshold: $\delta_s \to 0^+$ makes the outward radial term large and blocks tight orbits. At high speed, $\delta_s \to \pi$ minimizes radial self-repulsion, while multiple partner hits increase inward pull; balance occurs at finite $r_{\text{min}}$.

If the hypothesis holds, $r_{\text{min}}$ defines the prototype rod and $T_{\text{MCB}}$ the prototype clock tick, both emergent from the balance of partner attraction, self-hit repulsion, and centripetal requirement.

#### Attractor test requirements (summary)

Use the Poincare map and reduced variables defined in the next section to: (1) locate a candidate fixed point, (2) estimate nontrivial multipliers, and (3) map a basin of attraction under perturbations in radius, phase, and velocity. The detailed protocol and diagnostics appear in **Poincare Map, Stability, and Basins of Attraction for the MCB**.

#### Finite-dimensional projection caveat

All diagnostics use reduced coordinates; stability in the full history space remains a separate proof obligation.

### Poincare Map, Stability, and Basins of Attraction for the MCB

We work in the regularized two-body model defined in this chapter and in `dynamics/master-equation.md`:

- Two opposite-charge architrinos (electrino-positrino), charges $q_1=-\epsilon$, $q_2=+\epsilon$.
- Dynamics given by the delayed, purely radial Master Equation with regularization $\eta>0$.
- Field speed $c_f$ (typically set to 1 in simulation units).
- Focus on the maximum-curvature binary (MCB): the putative tight, self-hit-stabilized circular orbit.

State is infinite-dimensional (history segment), but for diagnostics we project to a finite set of effective variables (radius, speed, delay phases) consistent with the MCB test plan.

---

#### 1. Poincare Section and Return Map

##### Definition 1 (Configuration variables for the reduced binary)

In the symmetric, non-translating binary frame, let

- $R(t)$ - instantaneous orbital radius of particle 1 about the binary center,
- $s(t)$ - instantaneous tangential speed ($s = R\dot\theta$),
- $\delta_s(t)$ - principal self-delay angle (minimal self-hit separation; if none, set $\delta_s = 0$),
- $\delta_p(t)$ - principal partner-delay angle.

We group these into a reduced state vector
$$
\mathbf{z}(t) = \big(R(t),\,s(t),\,\delta_s(t),\,\delta_p(t)\big)\in\mathbb{R}^4.
$$

This is a projection of the full history state; it is not a complete description but suffices for local stability diagnostics near a circular orbit.

##### Definition 2 (Poincare section for the binary)

Fix an inertial Cartesian frame in the Euclidean void and define the section
$$
\Sigma = \Big\{ \mathbf{z}(t) \;\Big|\; \theta_1(t) = 0,\; \dot\theta_1(t) > 0 \Big\},
$$
where $\theta_1(t)$ is the polar angle of particle 1 about the binary center.

Equivalently: $\Sigma$ is the set of up-crossings where particle 1 passes through the positive $x$-axis with counterclockwise motion.

The full state at a section crossing is the history segment $\mathbf{x}_t \in \mathcal{H}$; $\mathbf{z}(t)$ is its reduced coordinate.

##### Definition 3 (Poincare return map)

Let $\Phi^t$ denote the semiflow generated by the regularized Master Equation on the history space $\mathcal{H}$, and let $T(\phi)>0$ be the first return time to the section:
$$
T(\phi) = \inf\{\,\tau>0 : \Phi^\tau(\phi)\in\Sigma\,\}.
$$

The Poincare map on the full phase space is
$$
P : \Sigma \to \Sigma,\qquad
P(\phi) = \Phi^{T(\phi)}(\phi).
$$

On the reduced variables we define the reduced Poincare map
$$
P_{\text{red}} : \Sigma_{\text{red}} \to \Sigma_{\text{red}},\qquad
P_{\text{red}}(\mathbf{z}_n) = \mathbf{z}_{n+1},
$$
where $\mathbf{z}_n = \mathbf{z}(t_n)$ and $t_{n+1}=t_n+T(\mathbf{x}_{t_n})$ is the time of the next $\Sigma$-crossing.

Here $\Sigma_{\text{red}}$ is the image of $\Sigma$ under the projection to $(R,s,\delta_s,\delta_p)$.

**Remark.** $P$ is the mathematically natural object; $P_{\text{red}}$ is the simulation-friendly shadow used to test attractor status of the MCB.

---

#### 2. Fixed-Point Formulation of the MCB

##### Definition 4 (MCB orbit as a periodic solution)

An MCB orbit is a $T$-periodic solution of the two-body delay system,
$$
\mathbf{x}_i(t+T) = \mathbf{x}_i(t),\qquad i=1,2,
$$
such that:

1. The motion of each particle is (approximately) circular about the center with constant radius $R_{\text{MCB}}$ and speed $s_{\text{MCB}}>c_f$,
2. The associated self-hit pattern is stationary in the co-rotating frame (principal self-delay angle and winding structure repeat each period),
3. The orbit has maximum curvature among stable periodic orbits: $1/R_{\text{MCB}}$ is locally maximal among stable $T$-periodic solutions.

##### Definition 5 (MCB as a fixed point of the Poincare map)

Let $\phi^* \in \Sigma$ be the history segment corresponding to one snapshot of the periodic MCB solution at a section crossing. Then $\phi^*$ satisfies
$$
P(\phi^*) = \phi^*.
$$

On the reduced coordinates, the corresponding fixed point is
$$
\mathbf{z}^*=\big(R^*,s^*,\delta_s^*,\delta_p^*\big)\in\Sigma_{\text{red}}
\quad\text{with}\quad
P_{\text{red}}(\mathbf{z}^*) = \mathbf{z}^*.
$$

Here:

- $R^* = R_{\text{MCB}}$ (candidate fundamental length),
- $T_{\text{MCB}}$ is the return time at $\phi^*$ (candidate time standard),
- $s^* = R^*\,2\pi/T_{\text{MCB}}$.

##### Lemma 1 (Equivalence: periodic orbit vs fixed point)

Let $\Phi^t$ be the flow on the history space. Then:

1. If there exists a nontrivial periodic orbit $\Phi^t(\phi^*)$ with period $T>0$ that intersects the section $\Sigma$ transversely, then $\phi^*$ is a fixed point of $P$.
2. Conversely, if $\phi^*$ is a fixed point of $P$ and the associated return time $T(\phi^*)$ is positive and finite, then the trajectory $\Phi^t(\phi^*)$ is periodic with period $T(\phi^*)$.

*Proof sketch.* Standard Poincare theory: transversality of the section gives a unique crossing per period; periodicity in time implies the map brings $\phi^*$ back to itself; conversely, time invariance of the flow dynamics implies that if the state returns to the same section configuration after time $T$, the entire history segment repeats with period $T$.

**Remark.** In the reduced coordinates, the same logic holds: a fixed point $\mathbf{z}^*$ of $P_{\text{red}}$ corresponds to a periodic two-body configuration if the reduced variables faithfully parametrize the underlying history (no hidden drift in unobserved degrees of freedom).

---

#### 3. Linear Stability and Floquet Multipliers

We analyze linear stability of the fixed point $\phi^*$ (or $\mathbf{z}^*$) using the derivative (Jacobian) of the Poincare map.

##### Definition 6 (Monodromy operator and multipliers - full space)

Let $DP(\phi^*) : T_{\phi^*}\Sigma \to T_{\phi^*}\Sigma$ be the Frechet derivative of the Poincare map at $\phi^*$. Its spectrum
$$
\{\lambda_k\}_{k\in\mathcal{I}}
$$
are the Floquet multipliers of the periodic MCB orbit.

- $\lambda=1$ always appears, associated with phase or temporal invariance (shift along the orbit).
- All other multipliers control stability of perturbations transverse to the orbit in the full history space.

##### Definition 7 (Floquet multipliers - reduced map)

On the reduced Poincare map $P_{\text{red}}$, the Jacobian is the $4\times 4$ matrix
$$
J = DP_{\text{red}}(\mathbf{z}^*)
=
\begin{pmatrix}
\partial R'/\partial R & \cdots \\
\vdots & \ddots
\end{pmatrix}_{\mathbf{z}=\mathbf{z}^*}
$$
with eigenvalues
$$
\{\lambda^{\text{(red)}}_1,\dots,\lambda^{\text{(red)}}_4\},
$$
where one eigenvalue should be close to $1$ (orbital phase), and the others describe transverse stability in $(R,s,\delta_s,\delta_p)$.

##### Theorem 1 (Linear stability criterion via multipliers)

Let $\phi^*$ be a fixed point of $P$ corresponding to a periodic MCB orbit. Then:

1. If all multipliers satisfy
   $$
   |\lambda_k| < 1 \quad \text{for all nontrivial }k
   $$
   (excluding one $\lambda=1$), then the MCB orbit is linearly asymptotically stable: small perturbations decay geometrically on successive Poincare returns.

2. If any multiplier satisfies $|\lambda_k| > 1$, the MCB is linearly unstable: there exist perturbations that grow geometrically.

3. If some $|\lambda_k| = 1$ (other than the trivial $\lambda=1$), the MCB is neutrally stable in that direction (center manifold or marginal stability).

*Proof sketch.* Standard Floquet-Poincare theory: the periodic orbit induces a linearized time-periodic variational equation. The monodromy operator over one period has eigenvalues $\lambda_k$. Crossings of the section sample this variational flow; the repeated application of $DP$ governs perturbation evolution at section hits. Spectral radius $<1$ implies exponential contraction under iteration; spectral radius $>1$ implies exponential growth.

---

#### 3.1 Numerical Estimation of Floquet Multipliers

##### Lemma 2 (Finite-difference Jacobian approximation)

Assume we have an approximate fixed point $\mathbf{z}^*$ such that
$$
\|P_{\text{red}}(\mathbf{z}^*) - \mathbf{z}^*\| \ll 1.
$$
Let $e_k$ denote the $k$-th coordinate basis vector in $\mathbb{R}^4$ and $\delta \ll 1$ a small perturbation amplitude. Define the columns of $J_{\text{num}}$ by
$$
J_{\text{num}} e_k
\;\approx\;
\frac{
P_{\text{red}}(\mathbf{z}^* + \delta e_k)
- P_{\text{red}}(\mathbf{z}^*)
}{\delta}.
$$

Then $J_{\text{num}}$ converges to $DP_{\text{red}}(\mathbf{z}^*)$ as $\delta \to 0$, provided $P_{\text{red}}$ is differentiable at $\mathbf{z}^*$ and the integrator error is controlled.

*Proof sketch.* This is standard finite-difference approximation for differentiable maps. The subtlety here is that each evaluation of $P_{\text{red}}$ entails integrating a state-dependent delay system to the next section crossing; however, as long as the integration is consistent and smooth in initial data (for fixed $\eta$ and step size), the overall mapping remains differentiable.

##### Definition 8 (Numerical Floquet multipliers)

The numerical Floquet multipliers are the eigenvalues of $J_{\text{num}}$:
$$
\lambda^{\text{(num)}}_k = \lambda_k\big(J_{\text{num}}\big).
$$

We identify:

- One multiplier close to $1$ (orbital phase symmetry),
- Remaining multipliers; their moduli indicate transverse stability.

##### Protocol 1 (Floquet multiplier estimation - MCB test)

1. **Model and regularization.**
   - Use two opposite charges with no translation and full delayed interaction including self-hits.
   - Fix $\eta$ with $\eta \ll R_{\text{MCB}}$, and choose $\Delta t \ll \eta$ and $\Delta t \ll T_{\text{MCB}}$.

2. **Locate candidate MCB fixed point.**
   - Use long-time spiral-in simulations to approximate a steady circular orbit.
   - Refine by periodic-orbit shooting: adjust initial $(R,s,\delta_s,\delta_p)$ so that after one return, the difference is minimized.

3. **Build the reduced Poincare map.**
   - Define section $\Sigma$ as particle 1 at angle $\theta=0$ with $\dot\theta>0$.
   - Implement $P_{\text{red}}$ as integrate from one section crossing to the next and record $(R,s,\delta_s,\delta_p)$.

4. **Finite-difference Jacobian.**
   - Choose $\delta$ (e.g. $10^{-4}$-$10^{-3}$ in dimensionless units).
   - For each coordinate direction $e_k$, compute $P_{\text{red}}(\mathbf{z}^* + \delta e_k)$.
   - Assemble $J_{\text{num}}$ as in Lemma 2.

5. **Eigenanalysis.**
   - Compute eigenvalues of $J_{\text{num}}$.
   - Identify $\lambda_{\text{phase}}\approx 1$ and check the remaining three multipliers for stability.

6. **Convergence checks.**
   - Reduce $\delta$ and check stability of eigenvalues.
   - Refine integration step $\Delta t$ and regularization width $\eta$; verify that multipliers converge as $\Delta t,\eta\to 0$.

**Criterion:** For the MCB attractor claim to hold in this reduced space, we require
$$
\max_{k\ne \text{phase}}
|\lambda^{\text{(num)}}_k|\;<\;1
\quad\text{(robust under refinement).}
$$

If any $|\lambda^{\text{(num)}}_k|>1$ persists under refinement, the MCB is not a stable attractor of the reduced dynamics.

---

#### 3.2 MCB Attractor Conjectures (Existence and Spectral Stability)

We formalize the physical hypothesis of the MCB as conjectures about the Poincare map defined above.

##### Conjecture A (Existence of the MCB Limit Cycle)
There exists a fixed point $\phi^* \in \Sigma$ corresponding to a periodic solution $\mathbf{x}^*(t)$ with period $T_{MCB}$. This solution corresponds to the Maximum-Curvature Orbit.

##### Conjecture B (Spectral Stability)
Let $DP(\phi^*)$ be the linearized monodromy operator of the Poincare map.
The spectrum $\sigma(DP(\phi^*))$ lies strictly within the unit disk in the complex plane, excluding the trivial eigenvalue $\lambda=1$ associated with time translation.
$$
\sup \{ |\lambda| : \lambda \in \sigma(DP(\phi^*)) \setminus \{1\} \} < 1.
$$

**Physical implication:** If Conjecture B holds, the MCB is an asymptotic attractor. If the spectrum contains elements with $|\lambda| > 1$, the MCB is unstable. If $|\lambda| = 1$, it is a center (non-generic in dissipative delay systems).

---

#### 4. Basins of Attraction and Separatrices

Assuming a stable fixed point (in reduced space), we next characterize its basin and the separatrices delineating its domain of attraction.

##### Definition 9 (Basin of attraction - reduced binary)

Let $\mathbf{z}^*$ be a stable fixed point of $P_{\text{red}}$. The basin of attraction $\mathcal{B}(\mathbf{z}^*)$ is
$$
\mathcal{B}(\mathbf{z}^*) =
\Big\{\mathbf{z}_0\in\Sigma_{\text{red}}
\;\Big|\;
\lim_{n\to\infty} P_{\text{red}}^{(n)}(\mathbf{z}_0) = \mathbf{z}^*
\Big\}.
$$

If a stable MCB fixed point exists and the binary remains bound, perturbations that stay within $\mathcal{B}(\mathbf{z}^*)$ return to the MCB; perturbations outside the basin may escape, collapse, or transition to other attractors.

In practice, we restrict to a 2D slice (e.g. $(R_0,s_0)$ with $\delta_s,\delta_p$ fixed at $\delta_s^*,\delta_p^*$) and study
$$
\mathcal{B}_{2D} = \mathcal{B}(\mathbf{z}^*)\cap\{(\delta_s,\delta_p)=(\delta_s^*,\delta_p^*)\}.
$$

##### Definition 10 (Separatrix - reduced slice)

In a 2D slice (e.g., $(R,s)$ plane), a separatrix is a curve (possibly fractal) that separates initial conditions with different asymptotic fates, e.g.:

- Convergence to MCB,
- Escape to unbound states,
- Collapse (if allowed by the dynamics),
- Transition to other attractors or chaotic sets.

Formally, in the slice $U\subset\mathbb{R}^2$, the separatrix set $\mathcal{S}\subset U$ is the boundary (in the topological sense) of $\mathcal{B}_{2D}$.

##### Lemma 3 (Separatrix as projection of invariant manifolds)

In the full phase space, stable and unstable manifolds of saddle-type periodic orbits and chaotic invariant sets project to boundaries in the $(R,s)$ slice. Under mild regularity assumptions, these projections form the separatrix structure $\mathcal{S}$.

*Proof sketch.* Standard invariant manifold theory: boundaries of basins are often (though not always) formed by the stable manifolds of saddles and their heteroclinic or homoclinic tangles. Projection to a low-dimensional slice preserves these boundaries except where folds or overlaps occur.

---

#### 4.1 Basin Mapping Protocol (Numerical)

##### Protocol 2 (2D basin map for the MCB)

1. **Fix $\delta_s$ and $\delta_p$** at their candidate MCB values $(\delta_s^*,\delta_p^*)$.

2. **Choose a rectangular grid** in $(R_0,s_0)$:
   $$
   R_0 \in [R^*(1-\epsilon_R), R^*(1+\epsilon_R)],\quad
   s_0 \in [s^*(1-\epsilon_s), s^*(1+\epsilon_s)],
   $$
   with $\epsilon_R,\epsilon_s\sim 0.1$ to begin.

3. **For each grid point $(R_0,s_0)$**:
   - Construct an initial binary configuration consistent with those values and with the chosen $(\delta_s^*,\delta_p^*)$.
   - Integrate the full delay system for $N_{\text{ret}}$ section returns (e.g., $N_{\text{ret}}\sim 10^3$--$10^4$).
   - At each return, compute the distance to $\mathbf{z}^*$:
     $$
     d_n = \big\|P_{\text{red}}^{(n)}(R_0,s_0,\delta_s^*,\delta_p^*) - \mathbf{z}^*\big\|.
     $$
   - Classification rule:
     - If $d_n \to 0$ (below tolerance) as $n\to N_{\text{ret}}$, mark the point as MCB-attracted.
     - If $R$ or $s$ drifts beyond preset bounds (escape, collapse, or wild oscillation), classify as non-MCB with sub-labels (e.g. unbound, chaotic candidate).
     - If $d_n$ stalls at a nonzero value but remains bounded, suspect a secondary attractor or quasi-periodic motion.

4. **Plot the basin map** in $(R_0,s_0)$ space using color codes:
   - One color for points converging to MCB,
   - Others for different outcomes.

5. **Resolution and convergence checks**:
   - Refine the grid near boundaries of the MCB region to resolve the separatrix.
   - Repeat with smaller $\Delta t$ and $\eta$ to test for numerical artifacts.

**Interpretation.** A robust attractor should have a visibly nontrivial basin: a 2D region of appreciable area converging to the MCB, with well-resolved separatrix curves or fractal boundaries.

---

#### 5. Failure Modes and Bifurcation Routes as Speed Crosses $c_f$

We now interpret how the qualitative dynamics of the binary change as speed crosses the field speed $c_f$. This follows the delay-geometry framework of this chapter.

##### 5.1 Regime I: Sub-Field-Speed ($s < c_f$) - No Self-Hit

- Only partner-delay forces contribute.
- The delayed attraction produces:
  - Inward radial component (spiral-in),
  - Positive tangential component (continual speed-up).

##### Lemma 4 (No stable circular orbit for $s<c_f$)

In the strictly sub-field-speed regime, every circular configuration exhibits positive net tangential acceleration (see the simplified expressions in the canonical derivation). Therefore no exact constant-speed circular orbit is possible: the binary tends to accelerate and spiral inward.

*Proof sketch.* From the partner-only analysis in the symmetric circular geometry, the tangential component $T_p$ is strictly positive for $0<\delta_p<\pi$. For a circular solution to persist, the time-averaged tangential acceleration must vanish. This cannot hold if $T_p>0$ at all hits.

**Consequence.** The Poincare map does not admit a true fixed point with constant $R,s$ in this regime. We instead see an inward spiral toward higher speeds.

##### 5.2 Regime II: Near Threshold ($s\approx c_f$) - Onset of Self-Hit

When the spiral drives $s$ to $c_f$, self-hits become geometrically possible:

- New causal roots appear for self-hit at $s>c_f$,
- Self-hit creates a repulsive contribution opposite to partner attraction.

Possible dynamical routes here:

1. Hopf-like bifurcation: The inward spiral (focus) could bifurcate to a limit cycle at the MCB radius as self-hit competes with partner delay. This would be a genuine birth of the MCB as a stable periodic orbit. We use "Hopf-like" here because the system is an SD-NDDE; rigorous Hopf theorems require smoothness and nondegeneracy conditions that have not yet been verified for this kernel.
2. Subcritical behavior or blow-up: Self-hit may overcompensate or mis-time its repulsion, yielding overshoot to large $R$ or unstable oscillations in $R,s$ that do not settle.
3. Fold (saddle-node) of cycles: A stable-unstable pair of periodic orbits might appear, with the MCB as the stable member and an outer unstable cycle defining the separatrix.

##### Conjecture (Hopf-type onset of MCB)

As an effective control parameter (e.g., energy or an external density) passes a critical value at which $s$ first crosses $c_f$, the two-body system undergoes a delay-induced Hopf-like bifurcation that creates the MCB as an attracting limit cycle.

This is formalized in the gap ledger below; current status: conjectural.

##### 5.3 Regime III: Super-Field-Speed ($s> c_f$) - Multi-Hit and High Curvature

As speed increases:

- Self-hit multiplicity grows (more winding branches),
- Partner-delay geometry changes,
- The balance between inward partner attraction and outward self-repulsion changes non-trivially.

Possible bifurcation routes as $s$ increases further:

1. Period-doubling cascade ($|\lambda|$ crosses $-1$): The MCB orbit may lose stability via a multiplier hitting $-1$, leading to period-2, period-4, and eventually chaotic dynamics.
2. Neimark-Sacker (torus) bifurcation ($\lambda$ crosses the unit circle off the real axis): quasi-periodic modulations of $R,s$ emerge, creating an invariant torus in the reduced space rather than a single limit cycle.
3. Global homoclinic tangles: Stable and unstable manifolds of saddles intersect, giving rise to fractal basins and sensitive dependence on initial conditions (chaos).

**Failure modes of the MCB across $c_f$:**

- Non-existence: No fixed point of $P$ survives once self-hit is included (the spiral never closes into a cycle).
- Existence but unstable: Fixed point exists but has $|\lambda|>1$; MCB is a repellor or saddle, not an attractor.
- Artifact of regularization: Stability depends crucially on $\eta$; as $\eta\to 0$, multipliers migrate onto or outside the unit circle.

Each of these failure modes would invalidate the attractor role of the MCB assumed by the architecture.

**Self-hit instability note:** A high-risk failure mode is runaway acceleration when self-hit repulsion is not sufficiently strong or timely to counteract orbital collapse, or when it adds energy faster than the system can dissipate. This is tracked explicitly in the global energy bound gap (MCB-09).

---

#### 6. Gap Ledger: Missing Proofs and Open Problems

We collect the specific nonlinear dynamics questions that remain open and must be resolved to solidify the MCB picture.

| ID | Item | Statement / Needed Result | Status | Risk |
|----|------|---------------------------|--------|------|
| MCB-01 | Existence of Poincare map | Show that for the regularized two-body system with $v$ crossing $c_f$, the section $\Sigma$ is transverse and every trajectory near the candidate MCB crosses it again in finite time, defining $P$ (and $P_{\text{red}}$) locally. | Assumed; not rigorously proven for all regimes | Medium |
| MCB-02 | Existence of MCB fixed point | Prove that $P$ (or at least $P_{\text{red}}$) admits a fixed point corresponding to a finite-radius, finite-speed limit cycle (MCB) for physically relevant parameters $(\kappa,\epsilon,c_f,\eta)$. | Conjectural; numerical search planned | Critical |
| MCB-03 | Local uniqueness and smoothness of MCB | Show the fixed point is isolated and depends smoothly on parameters; rule out families of neutrally stable cycles (centers) in the physically relevant regime. | Open | High |
| MCB-04 | Floquet spectrum of MCB | Establish that all nontrivial Floquet multipliers of $DP(\phi^*)$ lie strictly inside the unit circle (or, minimally, that the reduced multipliers of $DP_{\text{red}}$ do). | Only numerical estimates planned; no analytic bounds | Critical |
| MCB-05 | Hopf-like bifurcation at $s=c_f$ | Use center-manifold or normal-form theory for state-dependent delay equations to show that as $s$ crosses $c_f$, a stable limit cycle (MCB) is born from the inward spiral. | Conjecture; no rigorous proof | High |
| MCB-06 | Global basin structure | Characterize the topology of the MCB basin in $(R,s)$ (simply connected vs fractal), identify main separatrices and competing attractors (escape, secondary cycles, chaos). | Only exploratory numerics | Medium |
| MCB-07 | Regularization limit $\eta \to 0$ for $P$ | Show that if an MCB fixed point $\mathbf{z}^*_\eta$ and its multipliers are stable for all sufficiently small $\eta$, then a meaningful limiting object exists as $\eta \to 0$; rule out that stability is purely a smoothing artifact. | Open | Critical |
| MCB-08 | Correlation with full history dynamics | Prove that stability of the reduced fixed point $\mathbf{z}^*$ implies stability of the full periodic orbit in the infinite-dimensional history space (no hidden unstable modes). | Open | High |
| MCB-09 | Global energy bound | Establish an a priori bound on $\|\mathbf{v}(t)\|$ for the regularized self-force to rule out runaway acceleration. | Missing | Critical |

**Summary:**  
- The definition of the Poincare map, MCB fixed point, Floquet multipliers, and basins is clear and consistent with the delay geometry.
- The numerical protocols for estimating multipliers and mapping basins are explicit and implementable.
- The critical gaps remain: existence of the MCB fixed point, spectral stability, and the $\eta \to 0$ limit for any stability claims.

Until MCB-02, MCB-04, and MCB-07 are addressed (at least numerically with strong convergence evidence, ideally analytically), the MCB must be treated as a working hypothesis, not yet a proven dynamical attractor.

**Note:** The system is locally well-posed for $\eta > 0$, but global stability is not guaranteed. Simulations should explicitly test MCB-09 (runaway acceleration) and MCB-05 (existence of the cycle). If the numerical eigenvalues of the Poincare map are outside the unit circle, the MCB attractor hypothesis is false for this force law.

### Additional diagnostics

**Energy accounting (numerical)**:
- **Calculated total energy:**  
  $$
  E_{\text{calc}}(t) = K(t) + \mathcal{W}(t)
  $$
  with
  $$
  \mathcal{W}(t_{n+1}) = \mathcal{W}(t_n) - \sum_i \mathbf{v}_i(t_n) \cdot \mathbf{a}_i(t_n) \Delta t.
  $$
- **Energy drift:** $\delta E(t) = |(E_{\text{calc}}(t) - E_{\text{calc}}(0)) / E_{\text{calc}}(0)|$.
- **Expected drift rates:** Tier-1 pass $\delta E < 10^{-9}$ per orbit (symplectic/geometric); Tier-2 pass $\delta E < 10^{-6}$ per orbit (standard RK4).

**Angular momentum / planarity**:
- For planar initial data, the direction of $\mathbf{L}_{\text{mech}} = \sum \mathbf{x} \times \mathbf{p}$ should be conserved:
  $$
  \hat{\mathbf{n}} = \frac{\mathbf{L}_{\text{mech}}}{\|\mathbf{L}_{\text{mech}}\|},\quad \frac{d}{dt}\hat{\mathbf{n}} \approx 0.
  $$
- Planarity check: track $\mathbf{x}_i \cdot \hat{\mathbf{z}}$ if initialized in the $xy$ plane.

**Symmetry drift metric**:
$$
\Delta_{\text{sym}}(t) = \|\mathbf{x}_1(t) + \mathbf{x}_2(t)\|.
$$
In the center-of-mass frame, this should remain near zero for symmetric binaries.

**Self-work vs. partner-work**: Accumulate $\mathcal{W}_{\text{self}}$ and $\mathcal{W}_{\text{partner}}$ separately to diagnose which interaction drives instability.

**Eta dependence**: Track $R_{\text{MCB}}(\eta)$, $s_{\text{MCB}}(\eta)$, and nontrivial multipliers versus $\eta$. If stability degrades as $\eta \to 0$, the MCB is likely a regularization artifact.

**Tangential balance**: Measure $\langle T \rangle$ over an orbit and decompose it into self/partner contributions. Require $\langle T \rangle \to 0$ as $\Delta t,\eta \to 0$.

**Near-orbit structure**: Compute a short Lyapunov exponent and a frequency spectrum of $R(t)$ or $\theta(t)$ to distinguish true limit cycles from nearby tori or chaos.

**Failure conditions (falsification signals)**:
- **Secular energy drift:** If $E_{\text{calc}}$ drifts monotonically (not oscillating), the regularized interaction kernel is non-conservative (numerical heating).
- **Runaway:** If $K(t) \to \infty$ while $r(t) > r_{\min}$, the no-runaway criterion is violated, implying the discrete approximation has broken causality constraints.

### Architectural implications

If the attractor test succeeds, the MCB is the natural building block for tri-binaries and larger assemblies. If it fails (neutral or unstable), the interaction law or medium coupling must be revised before claiming a stable ladder of modes.

### Tri-Binary Bridge

If the MCB exists as a stable attractor, it serves as the **inner binary** of tri-binary assemblies. The outer pair then evolves in a broader, typically precessing orbit around the inner MCB, with additional modes (middle binary at $v=c_f$, outer binary at $v<c_f$) supplying energy storage and coupling to the Noether sea. This chapter focuses on the two-body MCB; tri-binary dynamics are treated separately.

---

## Emergent Measurement of Time and Distance

While the model is founded on the concepts of absolute space and absolute time, these are featureless, continuous arenas. They provide the mathematical background for geometry and motion but contain no inherent "ruler" or "clock." There are no fundamental, pre-defined units of distance or time. Instead, these units must emerge from the dynamics of the system itself.

### The Stable Binary as a Universal Standard

The necessary physical standard for measurement arises from the most fundamental assembly: the **stable orbiting binary**. If the MCB attractor conjecture holds (see the gap ledger: MCB-02, MCB-04, MCB-07), an isolated electrino-positrino pair is expected to avoid singular collapse. Instead, due to the interplay between delayed attraction and self-repulsive feedback, it should settle into a stable, circular orbit characterized by:
-   A **minimum possible radius**.
-   A **maximum possible orbital frequency** (and thus a minimum period).

Under this conjecture, the stable state is a universal attractor for a binary system, and its properties are determined solely by the fundamental constants of the model (such as field speed $c_f$ and charge $\epsilon$). It is this predictable, reproducible configuration that provides the foundation for all measurement.

### An Emergent Unit of Distance

Under the MCB attractor conjecture, the radius of the stable binary orbit is the smallest possible radius for such a system. This invariant length serves as a natural, emergent unit of distance. We can denote this fundamental length as $d_0$.

-   **Definition (conditional):** $d_0$ is defined as the radius of a stable, circular electrino-positrino orbit if the MCB attractor conjecture holds.
-   **Universality:** Any observer in the universe can, in principle, construct this standard by observing an isolated binary system.
-   **Function:** All other spatial measurements, from the size of more complex assemblies to the distances between them, can be expressed in terms of $d_0$.

### An Emergent Unit of Time

Under the MCB attractor conjecture, the motion within this stable orbit also provides a fundamental unit of time. The time it takes for the binary to complete one full revolution is its orbital period. Since the orbit has a minimum radius and a corresponding fixed speed, this period is the shortest possible for any binary assembly.

-   **Definition (conditional):** The fundamental unit of time, $t_0$, is defined as the orbital period of a stable, circular electrino-positrino orbit if the MCB attractor conjecture holds.
-   **Universality:** Like the unit of distance, this period is a constant derived from the system's fundamental dynamics.
-   **Function:** All other temporal measurements, such as the duration of events or the lifetimes of unstable assemblies, can be measured in multiples of $t_0$.

### Establishing a Physical Coordinate System

With the emergent units $d_0$ and $t_0$, we can move from the abstract, uncalibrated coordinates of absolute space and time to a concrete, physical coordinate system. Any measurement of a physical quantity can be rendered dimensionless by expressing it in these natural units. For example, the fundamental field speed $c_f$ can be written as a constant multiple of $d_0/t_0$.

This framework establishes that while the *arena* of space and time is absolute, the *measurement* of space and time is necessarily relative to the properties of the emergent structures that populate it.

## State Space and Well-Posedness of the Delayed Two-Body System

### 1. Introduction and Scope

The Master Equation of Motion for the architrino system constitutes a system of **State-Dependent Neutral Delay Differential Equations (SD-NDDEs)**. Unlike ordinary differential equations (ODEs) where the state is a point in $\mathbb{R}^{6N}$, the state of this system is a **function segment** representing the past history of the particles.

We denote the position of the $i$-th architrino as $\mathbf{x}_i(t) \in \mathbb{R}^3$. We work in the **Euclidean Void** with fixed metric $\delta_{ij}$.

---

### 2. Functional Phase Space

To define the evolution at time $t$, we require knowledge of the trajectory over an interval $[t - \tau_{\max}, t]$, where $\tau_{\max}$ is the maximum causal lookback time relevant to the current dynamics.

#### Definition 1 (The History Space)
Let $h > 0$ be a history horizon (sufficiently large to capture all active causal roots). The **history space** $\mathcal{H}$ is defined as the Banach space of continuously differentiable functions mapping the delay interval to the configuration space:
$$
\mathcal{H} = C^1\left([-h, 0]; (\mathbb{R}^3)^N\right).
$$
For a trajectory $\mathbf{x}: [-h, \infty) \to (\mathbb{R}^3)^N$, the **state at time $t$**, denoted $\mathbf{x}_t$, is the element of $\mathcal{H}$ given by:
$$
\mathbf{x}_t(\theta) = \mathbf{x}(t + \theta), \quad \theta \in [-h, 0].
$$
The norm is the standard $C^1$ sup-norm: $\|\phi\|_\mathcal{H} = \sup_{\theta \in [-h,0]} (\|\phi(\theta)\| + \|\dot{\phi}(\theta)\|)$.

**Remark:** We require $C^1$ rather than $C^0$ because the delay $\tau$ depends on the state (state-dependent delay). In such systems, the vector field is typically not Lipschitz continuous in the $C^0$ topology, endangering uniqueness.

---

### 3. The Regularized Interaction Functional

We formalize the force term derived in the Master Equation.

#### Definition 2 (Causal Constraint Functional)
For a target particle $i$ at time $t$ and source $j$, the delay $\tau_{ij}(t)$ is implicitly defined by the light-cone condition. Let $\phi \in \mathcal{H}$ be the history. A **causal root** is a value $\tau > 0$ satisfying:
$$
g_{ij}(\tau, \phi) \equiv \|\phi_i(0) - \phi_j(-\tau)\| - c_f \tau = 0.
$$

#### Lemma 1 (Regularity of the Delay Map)
*Assumption:* The velocities are sub-luminal relative to the separation, i.e., $|\mathbf{v}_j| < c_f$ (Single-Hit Regime) OR we isolate a specific branch of the multi-hit solution where the relative radial velocity is not $c_f$.

*Statement:* If $\phi \in \mathcal{H}$ and $\tau^*$ is a simple root of $g_{ij}(\tau, \phi) = 0$ (i.e., $\partial_\tau g_{ij} \neq 0$), then there exists a neighborhood $U \subset \mathcal{H}$ of $\phi$ and a continuously differentiable functional $\tau: U \to \mathbb{R}^+}$ such that $\tau(\phi) = \tau^*$.

*Proof Sketch:* Apply the Implicit Function Theorem to $g_{ij}$. The condition $\partial_\tau g \neq 0$ corresponds to the source not moving exactly at the speed of light *towards* the receiver at the retarded time (no "causal shock" accumulation).

#### Definition 3 (Regularized Force Field)
To ensure the vector field is Lipschitz, we replace the distributional Dirac delta of the Master Equation with the mollifier $\rho_\eta$ (see `dynamics/master-equation.md`). The acceleration functional $F_i: \mathcal{H} \to \mathbb{R}^3$ is:
$$
F_i(\phi) = \sum_{j} \kappa \sigma_{ij} q_i q_j \int_{-h}^0 \frac{\phi_i(0) - \phi_j(\theta)}{\|\phi_i(0) - \phi_j(\theta)\|^3} \, \rho_\eta\left( \|\phi_i(0) - \phi_j(\theta)\| + c_f \theta \right) \, d\theta.
$$
**Crucial Property:** For $\eta > 0$ and smooth $\rho_\eta$, this integral operator maps $C^1$ histories to continuous accelerations.

---

### 4. Local Well-Posedness

#### Theorem 1 (Local Existence and Uniqueness)
**Assumptions:**
1. $\eta > 0$ (Finite regularization).
2. The initial history $\phi^0 \in \mathcal{H}$ satisfies the "gluing condition" at $t=0$ (acceleration computed from history matches $\ddot{\phi}^0(0-)$) to ensure $C^2$ smoothness at the junction, though $C^1$ solutions exist without this.
3. No "tangential" causal intersections in the history (roots are simple).

**Statement:**
There exists a maximal time $T > 0$ and a unique solution $\mathbf{x}(t)$ on $[-h, T)$ such that $\mathbf{x}_0 = \phi^0$ and $\mathbf{x}(t)$ satisfies the regularized Master Equation.

*Proof Strategy:*
The problem is reduced to $\dot{\mathbf{x}}(t) = \mathbf{v}(t), \dot{\mathbf{v}}(t) = F(\mathbf{x}_t)$. Since $F$ is locally Lipschitz on the open subset of $\mathcal{H}$ where causal roots are simple (Lemma 1), the Picard-Lindelof theorem for Banach spaces applies.

---

### 5. Global Existence vs. Blow-Up

Unlike Newtonian gravity, global existence is **not guaranteed** simply by avoiding collisions, because the delay equation can harbor "runaway" modes where self-acceleration diverges.

#### Theorem 2 (Continuation Principle)
The solution $\mathbf{x}(t)$ can be extended as long as the state $\mathbf{x}_t$ remains within a compact subset of the phase space where causal roots are simple.

#### Definition 4 (Blow-Up Criteria)
The solution ceases to exist at finite time $T^*$ if:
1. **Collision:** $\inf_{i,j} \|\mathbf{x}_i(t) - \mathbf{x}_j(t')\| \to 0$ inside the regularization kernel support.
2. **Infinite Speed:** $\sup_i \|\mathbf{v}_i(t)\| \to \infty$.
3. **Causal Shock:** The derivative of the delay $\dot{\tau}(t)$ diverges (Doppler factor becomes singular). This occurs if a particle moves directly toward a receiver at speed $v = c_f$.

---

## Symmetry, Conservation, and Lyapunov Functionals

### 1. Introduction

Standard conservation laws (energy, momentum, angular momentum) rely on the application of Noether's Theorem to local Lagrangian densities. In this delayed setting, the force at time $t$ depends on the phase-space trajectory over the interval $[t - h, t]$.

Symmetries of the substrate (Euclidean Void + Absolute Time) still imply conservation laws, but the conserved quantities are no longer simple functions of the instantaneous state $(\mathbf{x}, \mathbf{v})$. Instead, they are **functionals on the history space** $\mathcal{H}$.

This section derives these functionals, establishes the exact symmetry group of the regularized dynamics ($\eta > 0$), and provides the *a priori* bounds required to ensure physical well-posedness (preventing unphysical runaway acceleration).

---

### 2. The Global Symmetry Group

We consider the regularized two-body system in the Euclidean Void $\mathbb{R}^3$ with metric $\delta_{ij}$ and absolute time $t$.

#### Definition 1 (The Fundamental Symmetry Group)
The background substrate and the Master Equation interaction kernel
$$
\mathbf{a}_{ij}(t) \propto \frac{\mathbf{x}_i(t) - \mathbf{x}_j(t_0)}{\|\mathbf{x}_i(t) - \mathbf{x}_j(t_0)\|^2}
$$
(regularized by $\eta$) respect the group:
$$
G_{\text{fund}} = E(3) \times \mathbb{R}_{\text{time}}
$$
where $E(3) = \mathbb{R}^3 \rtimes O(3)$ is the Euclidean group of spatial translations and rotations, and $\mathbb{R}_{\text{time}}$ denotes time translation.

#### Theorem 1 (Invariance of the Equations of Motion)
Let $\mathbf{x}(t)$ be a solution to the Master Equation.
1.  **Time Translation:** For any $\tau \in \mathbb{R}$, $\mathbf{y}(t) = \mathbf{x}(t + \tau)$ is also a solution.
2.  **Spatial Isometry:** For any $R \in O(3)$ and $\mathbf{b} \in \mathbb{R}^3$, $\mathbf{y}(t) = R\mathbf{x}(t) + \mathbf{b}$ is also a solution.

*Proof Sketch:*
The causal constraint $\|\mathbf{x}_i(t) - \mathbf{x}_j(t_0)\| = c_f(t - t_0)$ depends only on the Euclidean distance and time difference. Both are invariants of $G_{\text{fund}}$. The vector direction $\hat{\mathbf{r}}$ rotates covariantly with $R$. Thus, the dynamics are form-invariant.

**Implication:** There exist exact integrals of motion corresponding to these symmetries. However, because the interaction is non-local in time, these integrals must account for "momentum and energy in flight" (stored in the wake surfaces).

---

### 3. Conservation of Generalized Momentum

In a delay system, Newton's Third Law ($\mathbf{F}_{12}(t) = -\mathbf{F}_{21}(t)$) fails instantaneously because $\mathbf{F}_{12}(t)$ originates from particle 2 at $t-\tau_1$, while $\mathbf{F}_{21}(t)$ originates from particle 1 at $t-\tau_2$.

#### Definition 2 (Mechanical Momentum)
The instantaneous mechanical momentum is:
$$
\mathbf{P}_{\text{mech}}(t) = \sum_{i} m_i \mathbf{v}_i(t).
$$
Because of the delay, $\frac{d}{dt}\mathbf{P}_{\text{mech}} \neq 0$ generally.

#### Theorem 2 (Conservation of Total Momentum Functional)
There exists a functional $\mathbf{P}_{\text{field}}[\mathbf{x}_t]$ representing the momentum flux encoded in the active causal wake surfaces such that the total momentum:
$$
\mathbf{P}_{\text{tot}} = \mathbf{P}_{\text{mech}}(t) + \mathbf{P}_{\text{field}}[\mathbf{x}_t]
$$
is strictly conserved ($\frac{d}{dt}\mathbf{P}_{\text{tot}} = 0$).

**Explicit Form (Weak Coupling Limit):**
For $\eta \to 0$, the field momentum can be approximated by integrating the force impulse over the delay time:
$$
\mathbf{P}_{\text{field}} \approx \sum_{i \neq j} \int_{t - \tau_{ij}(t)}^{t} \mathbf{F}_{ij}^{\text{emit}}(s) \, ds.
$$
*Physical Interpretation:* The "missing" momentum is strictly accounted for by the wake surfaces currently traversing the space between sources and receivers.

**Corollary (Center of Mass Motion):**
For an isolated binary, the center of mass $\mathbf{x}_{\text{cm}}$ does not move at constant velocity. Instead, it oscillates around a mean trajectory. However, **self-acceleration of the center of mass to infinity is forbidden** by the exact translation invariance of the Lagrangian. The system cannot "bootstrap" itself to arbitrary speeds without external interaction.

---

### 4. Energy and The Lyapunov Functional

Energy conservation is the critical constraint preventing runaway solutions (MCB-09).

#### Definition 3 (The History Hamiltonian)
Since the system is time-translation invariant, there exists a conserved quantity $\mathcal{H}$. For state-dependent delays, this is a **Lyapunov-Krasovskii Functional**:
$$
\mathcal{H}(\mathbf{x}_t) = K(\mathbf{v}(t)) + \mathcal{U}_{\text{history}}(\mathbf{x}_t).
$$

1.  **Kinetic Energy:** $K(t) = \sum \frac{1}{2} m_i \|\mathbf{v}_i(t)\|^2$.
2.  **Potential Functional:** $\mathcal{U}_{\text{history}}$ accumulates the work done by the conservative forces. Unlike an instantaneous potential $V(r)$, this depends on the configuration of all active wake surfaces.

#### Theorem 3 (Energy Balance Equation)
$$
\frac{dK}{dt} = \sum_{i} \mathbf{v}_i(t) \cdot \mathbf{F}_i(t).
$$
We define the **Interaction Potential Functional** $\mathcal{W}(t)$ such that:
$$
\mathcal{W}(t) = -\int_{t_0}^t \sum_i \mathbf{v}_i(s) \cdot \mathbf{F}_i(s) \, ds.
$$
This functional is nonlocal in time: it accumulates deferred work along the path-history of wakes and is not an instantaneous potential $U(r)$.
Then, by construction, $\mathcal{E}_{\text{tot}} = K(t) + \mathcal{W}(t)$ is constant.

#### Lemma 1 (Boundedness of the Potential)
**Assumption:** The interaction is regularized with width $\eta > 0$ such that the maximum force is bounded: $\|\mathbf{F}_{ij}\| \le F_{\max}(\eta)$.
**Statement:** For a bound system (particles confined to a finite volume $V$), the rate of work is bounded by $N F_{\max} v_{\max}$.

#### Theorem 4 (No-Runaway Criterion)
In the Master Equation dynamics, an isolated binary cannot undergo runaway acceleration ($v \to \infty$) *unless* the potential energy functional $\mathcal{W}(t)$ diverges to $-\infty$.

*Proof Logic:*
Since $\mathcal{E}_{\text{tot}}$ is constant:
$$
K(t) = \mathcal{E}_{\text{tot}} - \mathcal{W}(t).
$$
For $K(t)$ to diverge, $\mathcal{W}(t)$ must decrease without bound.
1.  **Partner Attraction:** $q_1 q_2 < 0$. The potential is negative (attractive). As $r \to 0$, $V \to -\infty$. Collapse leads to infinite kinetic energy (standard Kepler singularity, resolved by self-hit).
2.  **Self-Hit Repulsion:** $q_1 q_1 > 0$. The force is **repulsive**. The potential contribution is **positive**.
    *   Work done by self-hit: If a particle is pushed "from behind" by its own wake, it gains $K$.
    *   However, this energy must come from the $\mathcal{W}$ term.
    *   Since self-hit potential is repulsive (positive energy hill), converting it to kinetic energy lowers the total potential.
    *   **Crucial Bound:** The deferred work encoded in a self-wake is finite (determined by emission charge). A particle cannot extract infinite energy from its own past unless it puts infinite energy *into* the field first.

**Conclusion:** The "free lunch" runaway, where a particle accelerates itself indefinitely using self-forces, is forbidden by the conservation of $\mathcal{H}$. The system can oscillate or settle, but it cannot explode to $v=\infty$ without singular collapse of the radius.

---
