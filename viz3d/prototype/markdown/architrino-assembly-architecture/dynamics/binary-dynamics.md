# Binary Dynamics

This chapter develops two-body architrino dynamics from the appearance of self-hit to stable binaries and their role as measurement standards. It then formalizes the maximum-curvature attractor analysis and closes with the state-space and conservation-law foundations that make the dynamics well-posed. **Status:** (1) self-hit makes the dynamics non-Markovian (path-history dependent), and (2) stability/attractor claims are conjectural unless explicitly established.

## The Spiral Orbiting Binary and the Contraction Phase

An orbiting binary is the simplest emergent assembly, consisting of two architrinos of opposite charge—an electrino and a positrino. With charges $-\epsilon$ and $+\epsilon$, the assembly is electrically neutral overall. This system demonstrates the fundamental principles of interaction, including the consequences of delayed potential and the role of the field-speed symmetry point.

Consider the ideal case of a symmetric orbit in a universe with no other architrinos. In general, each architrino is subject to a superposition of external potential waves from all other sources; the analysis below isolates the binary by setting those external contributions to zero.

Let the electrino be particle 1 and the positrino be particle 2.
-  **Positions:** $\mathbf{s}_1(t)$ and $\mathbf{s}_2(t)$
-  **Charges:** $q_1 = -\epsilon$ and $q_2 = +\epsilon$

The motion of each particle is determined by the field emitted by the other at a delayed time. The acceleration of the electrino (particle 1) at time $t$ is caused by the positrino's (particle 2) field emitted at an emission time $t_0$. This is governed by the interaction condition:
$$
\|\mathbf{s}_1(t) - \mathbf{s}_2(t_0)\| = c_f(t - t_0)
$$
The acceleration vector for the electrino is attractive, pointing towards the positrino's delayed position:
$$
\mathbf{a}_1(t) \propto -\hat{\mathbf{r}}_{21} = - \frac{\mathbf{s}_1(t) - \mathbf{s}_2(t_0)}{\|\mathbf{s}_1(t) - \mathbf{s}_2(t_0)\|}
$$
A symmetric set of equations governs the positrino's motion based on the electrino's emissions.

In the strictly sub-field-speed regime (no self-interaction, $|\mathbf{v}|\le c_f$), a stable, circular orbit is impossible. Because the attractive force on each particle points to the *past* position of its partner, it is not a true central force. This delay yields an **inward spiral that is naturally modeled as exponential in angle** (a logarithmic spiral), consistent with a per-cycle angular-momentum increment $\Delta L_c$ in the partner-only regime. The radius shrinks geometrically per turn and speed increases until the self-interaction threshold ($|\mathbf{v}|>c_f$) is crossed.

**Lemma (No stable circular orbit for $v < c_f$).** In circular motion, $v=s=R\omega$. In the partner-only regime, the per-hit tangential component satisfies
$$
T_p \propto \frac{\sin(\delta_p/2)}{\cos^2(\delta_p/2)} > 0 \quad (0<\delta_p<\pi),
$$
where $\delta_p$ is the partner delay angle. The time-averaged tangential acceleration cannot vanish; a constant-speed circular orbit is impossible.

-  The tangential component of the delayed force sustains the orbital motion.
-  The radial component continuously pulls the particles closer together.

With perfectly symmetric initial conditions (e.g., starting at rest), the paths of the electrino and positrino are distinct but perfect mirror images of each other. As they spiral inward, their speeds continuously increase. Emission cadence and per-wavefront amplitude remain constant; the evolution is driven entirely by delay geometry and, once active, self-interaction.

Initially, and as long as the speeds of both particles are less than or equal to the field speed $c_f$, they are only influenced by their partner's attractive field. The total acceleration is simply the attractive force:
$$
\mathbf{a}_{1, \text{total}}(t) = \mathbf{a}_{1,2}(t) \quad \text{and} \quad \mathbf{a}_{2, \text{total}}(t) = \mathbf{a}_{2,1}(t)
$$
During this phase, the system is purely contractile, with the particles accelerating and spiraling towards each other. The positive tangential component (see Lemma in the prior section) guarantees continued speed-up, so the spiral tightens until the self-hit regime is reached.

## Spiral Momentum Budget Across the Hinge (Speculative)

We want a single story that links the spiral path, the per-hit force law, and the angular-momentum budget across the full velocity range. Below the field speed, the binary feels only partner hits, yet the tangential component remains positive, so the spiral keeps tightening and the total orbital angular momentum of the **binary** grows each turn. We introduce a per-cycle gain parameter $\Delta L_c$ to track that growth (a **constant** increment per full revolution in this hypothesis).

**Speculative continuity assumption:** as $v \to c_f$, the per-cycle gain transitions smoothly from $\Delta L_\text{cycle} = \Delta L_c$ (sub-field-speed) to $\Delta L_\text{cycle} = 2\Delta L_c$ (self-hit active). 

This section treats an exponential-in-angle spiral (logarithmic spiral) as a **modeling assumption** rather than a derived law. It simply sets the bookkeeping target: a path-history force sum that yields a smooth, finite increase in $\Delta L_\text{cycle}$ at the hinge. The detailed link between the summed per-hit forces and the spiral shape remains to be derived.

## Spiral Binary Symmetry-Breaking Point ($v = c_f$)

The binary system's evolution is organized around the **field-speed symmetry point** $v=c_f$. This is a **hinge** where the causal structure changes: below $c_f$ only partner-delay forces exist, while above $c_f$ self-hit roots appear. The hinge is not a hard barrier; it is a change in **root count**. The transition is smooth as long as the delay roots remain simple (no "causal shock"), which in the symmetric spiral/circular geometry is generically satisfied. At the hinge the principal self-hit branch appears with a small delay angle ($\tilde{\delta}_s\to 0^+$), which geometrically means the self-hit emission point lies almost directly behind the current position.

The radial factor scales like $1/\sin(\tilde{\delta}_s/2)$ and therefore becomes very large as $\tilde{\delta}_s\to 0^+$. This large outward term adds a strong radial component, but it does not necessarily prevent further tightening because tangential acceleration continues to rise; in the working picture the spiral still contracts more each turn, with any true radial arrest pushed to the final, multi-root turn. The maximum-curvature regime does not occur near threshold but only after $\tilde{\delta}_s$ becomes appreciable (higher $s$ and larger-angle roots).

## Self-Hit: Definition and Diagnostics

Self-hit is the key non-Markovian feature of architrino dynamics. It occurs when an architrino interacts with potential it emitted earlier along its own worldline.

**Geometric condition (absolute coordinates):** For a given architrino with trajectory $\mathbf{x}(t)$, a self-hit event is a pair of times $(t_\text{emit}, t_\text{hit})$ with $t_\text{hit} > t_\text{emit}$ such that
$$
|\mathbf{x}(t_\text{hit}) - \mathbf{x}(t_\text{emit})| = c_f (t_\text{hit} - t_\text{emit}),
$$
and the architrino is the source of the causal wake surface emitted at $t_\text{emit}$.

**Dynamical role:**
- At low velocities ($v < c_f$), self-hit is absent, unless previously in the self-hit region ($v > c_f$).
- As velocities exceed $c_f$, emission isochrons catch up with the emitter's future positions, generating nonlocal feedback and effective restoring or destabilizing forces depending on configuration.
- In generic trajectories, once a particle has exceeded $c_f$ and emitted wakes in that regime, it can later slow below $c_f$ and still experience self-hits from those earlier emissions (see **Status** at top for the non-Markovian/path-history caveat).
- For binary and tri-binary assemblies, repeated self-hit events are the proposed mechanism that can prevent collapse, lock in stable radii and frequencies, and create new limit cycles and attractors.

For the circular-geometry details (principal angles, winding numbers, discrete self-hit branches), see **Setup and Notation (Symmetric Frame)** in **Maximum-Curvature Binary — Circular**.

## Spiral Binary Deflationary Phase

Once the architrinos' speeds exceed the field speed $c_f$, they cross the symmetry point and begin to interact with their own recently emitted, repulsive wakes. The total acceleration on each particle now becomes a superposition of attraction from its partner and self-repulsion. For the electrino:
$$
\mathbf{a}_{1, \text{total}}(t) = \mathbf{a}_{1,2}(t) + \mathbf{a}_{1,1}(t)
$$
At $|\mathbf{v}| > c_f$, a principal self-hit branch ($m=0$) becomes available; at higher speeds, additional branches turn on (see **Self-Hit Multiplicity vs. Speed**). The new self-repulsive term, $\mathbf{a}_{1,1}(t)$, grows rapidly as the path curvature increases, and it also adds tangential acceleration. In this regime the spiral typically tightens **more** each turn: the radius decreases faster while speed continues to rise. We still call this the **deflationary** phase, but in the sense that any radial arrest is a **late** effect—there is no soft landing early on. The balance that halts contraction is expected, if realized, only near the final turn where the orbit settles into the conjectured limiting circle; see **What "Maximum Curvature" Demands** for the balance mechanism.

## Maximum-Curvature Binary — Circular

Once self-hit turns on, the natural question is whether the dynamics converge to a limiting curvature. We call the candidate limit the **maximum-curvature binary (MCB)**. This section collects the full two-body, self-hit analysis for that candidate, including delay geometry, force components, and stability criteria. It is the canonical reference for MCB attractor status.

MCB stability claims rely on the well-posedness of the regularized SD-NDDE. In this chapter we treat $\eta > 0$ as fixed and defer the $\eta \to 0$ limit to future work. The formal state-space framework appears in **State Space and Well-Posedness of the Delayed Two-Body System**.

**Goal**: Characterize the circular, constant-speed, constant-radius configuration of two opposite-charge architrinos and investigate where curvature $\kappa = 1/R$ is maximized. We work in units with field speed $c_f = 1$ and use the canonical delayed, purely radial per-hit law.

**Plain language**: We seek the tightest (smallest-$R$) steady circle an opposite-charge pair can trace when the only forces come from delayed, radial interactions with the partner (multiple-hits) and from one's own past emissions (self-hits, active only when speed exceeds field speed).

### Foundational Context (Ontological Clarification)

#### The Maximum-Curvature Binary (MCB) as Fundamental Unit

The architecture hypothesizes that the **maximum-curvature binary (MCB)** would be reachable first by the **inner binary** of a tri-binary assembly, stabilized by self-hit dynamics when $v > c_f$. Contingent on Conjectures A/B, it would supply the **fundamental physical units** (length and time); see **Emergent Properties and Measurement Standards** below for the explicit definitions.

**Universal cap (explicit):** The MCB is treated as a single, universal limit state (one defining radius/speed). Binaries may sit below this limit, but no binary can exceed the MCB curvature or pass beyond its defining radius/speed.

If realized, the MCB radius $r_{\text{min}}$ is expected to be determined by the balance of:
1. Coulomb-like attraction between opposite charges ($\propto |e/6|^2 / r^2$),
2. Self-hit repulsion (non-Markovian feedback when $v > c_f$),
3. Centripetal requirement for stable circular orbit.

**Dynamical priority (attractor status):** The architecture hypothesizes the MCB is a **robust attractor**, not a finely tuned periodic orbit. Only if the multipliers lie strictly inside the unit circle and the basin is non-trivial do we have the attractor the architecture relies on. If neutrality or instability is found, the tri-binary ladder and Noether-core claims must be downgraded or the interaction law revised (e.g., additional damping/medium effects).

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

When $s \le 1$, self-hits do not occur ($\delta_s$ has no solution). Only the partner contributes, so the tangential drive remains strictly positive, consistent with the lemma above:

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

**Mechanism summary (self-hit balance):** once $s>1$, each self-hit contributes a **repulsive acceleration away from its own past emission point**. In the symmetric circular geometry that repulsion has a **radial outward component** (opposing further contraction) and a **positive tangential component** (continuing to speed up the architrino). As the radius shrinks, both partner attraction and self-hit repulsion scale like $1/R^2$, while the **self-hit factor** also grows because the path curvature brings the particle closer to its own past wakes and because **new self-hit roots appear** at higher $s$. Maximum curvature is reached when the **outward self-hit radial component balances the inward partner pull**; beyond that point the radius cannot decrease without an overwhelming self-hit response.

From the radial component formula:

$$
A_{\text{rad}} = \frac{\kappa \epsilon^2}{4R^2} \left( \frac{1}{\cos(\delta_p / 2)} - \frac{1}{\sin(\delta_s / 2)} \right).
$$

**Increasing curvature** ($\kappa = 1/R$ larger -> $R$ smaller) requires **stronger inward radial force**. This occurs when:

1. **$\delta_p$ increases** -> $\cos(\delta_p / 2)$ decreases -> partner term $1/\cos(\delta_p / 2)$ **increases** (stronger inward pull).
2. **$\delta_s$ increases** -> $\sin(\delta_s / 2)$ increases -> self term $1/\sin(\delta_s / 2)$ **decreases** (weaker outward repulsion).

**Maximum curvature** (smallest stable $R$) likely occurs at **higher speeds** ($s \gg 1$) where:
- Multiple self-hits ($m \ge 1$) are active,
- $\delta_s$ is large (approaching $\pi$),
- Outward self-repulsion is minimized while inward partner attraction is maximized.

**However**: Due to the per-hit $T > 0$ result, this "maximum curvature" state remains unverified for the isolated two-body system. Its stability must be tested by the full, multi-root time-averaged dynamics.

---

### Emergent Properties and Measurement Standards

If a stable MCB exists, it provides a concrete **rod** and **clock** defined entirely by the two-body delay dynamics. Let
$$
d_0 := R_{\text{MCB}}, \qquad T_0 := \frac{2\pi}{\omega_{\text{MCB}}}.
$$
Then $d_0$ is the fundamental length scale of the architecture, and $T_0$ is the fundamental time scale. The field speed becomes the ratio
$$
c_f = \frac{d_0}{T_0},
$$
so the universal speed bound is not an external postulate but an emergent relation among the MCB radius and period.

In this view, any ruler or clock built from architrino assemblies ultimately reduces to multiples of $(d_0, T_0)$. Measurement standards are therefore **dynamical invariants** of the two-body attractor: they persist because the underlying limit cycle (if realized) is stable and reproducible across assemblies.

If the MCB does not exist as a stable attractor, these emergent standards must be replaced by whatever stable limit structure the dynamics actually support.

### Self-Hit Multiplicity vs. Speed

In uniform circular, non-translating geometry, admissible self-roots are indexed by winding number $m \ge 0$ and minimal angular separation $\tilde{\delta}_s \in (0, \pi]$:

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

The emission points on the circle that can produce hits "now" form a **finite, discrete set** of azimuths determined by the delay equations--**not arbitrary locations**. Because roots are indexed by winding number $m$, multiple hits at the same "now" can occur for different windings, but the admissible azimuths remain a finite comb and never fill the circle.

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

---





#### Finite-dimensional projection caveat

The circular formulas below use reduced coordinates; stability in the full history space remains a separate proof obligation.

## State Space and Well-Posedness of the Delayed Two-Body System

### Introduction and Scope

The master equation of Motion for the architrino system constitutes a system of **State-Dependent Neutral Delay Differential Equations (SD-NDDEs)**. Unlike ordinary differential equations (ODEs) where the state is a point in $\mathbb{R}^{6N}$, the state of this system is a **function segment** representing the past history of the particles.

We denote the position of the $i$-th architrino as $\mathbf{x}_i(t) \in \mathbb{R}^3$. We work in the **Euclidean Void** with fixed metric $\delta_{ij}$.

---

### Functional Phase Space

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

### The Regularized Interaction Functional

We formalize the force term derived in the master equation.

#### Definition 2 (Causal Constraint Functional)
For a target particle $i$ at time $t$ and source $j$, the delay $\tau_{ij}(t)$ is implicitly defined by the light-cone condition. Let $\phi \in \mathcal{H}$ be the history. A **causal root** is a value $\tau > 0$ satisfying:
$$
g_{ij}(\tau, \phi) \equiv \|\phi_i(0) - \phi_j(-\tau)\| - c_f \tau = 0.
$$

#### Lemma 1 (Regularity of the Delay Map)
*Assumption:* The velocities are sub-luminal relative to the separation, i.e., $|\mathbf{v}_j| < c_f$ (Single-Hit Regime) OR we isolate a specific branch of the multi-hit solution where the relative radial velocity is not $c_f$.

*Statement:* If $\phi \in \mathcal{H}$ and $\tau^*$ is a simple root of $g_{ij}(\tau, \phi) = 0$ (i.e., $\partial_\tau g_{ij} \neq 0$), then there exists a neighborhood $U \subset \mathcal{H}$ of $\phi$ and a continuously differentiable functional $\tau: U \to \mathbb{R}^+$ such that $\tau(\phi) = \tau^*$.

*Proof Sketch:* Apply the Implicit Function Theorem to $g_{ij}$. The condition $\partial_\tau g \neq 0$ corresponds to the source not moving exactly at the speed of light *towards* the receiver at the retarded time (no "causal shock" accumulation).

#### Definition 3 (Regularized Force Field)
To ensure the vector field is Lipschitz, we replace the distributional Dirac delta of the master equation with the mollifier $\rho_\eta$ (see `dynamics/master-equation.md`). The acceleration functional $F_i: \mathcal{H} \to \mathbb{R}^3$ is:
$$
F_i(\phi) = \sum_{j} \kappa \sigma_{ij} q_i q_j \int_{-h}^0 \frac{\phi_i(0) - \phi_j(\theta)}{\|\phi_i(0) - \phi_j(\theta)\|^3} \, \rho_\eta\left( \|\phi_i(0) - \phi_j(\theta)\| + c_f \theta \right) \, d\theta.
$$
**Crucial Property:** For $\eta > 0$ and smooth $\rho_\eta$, this integral operator maps $C^1$ histories to continuous accelerations.

---

### Local Well-Posedness

#### Theorem 1 (Local Existence and Uniqueness)
**Assumptions:**
1. $\eta > 0$ (Finite regularization).
2. The initial history $\phi^0 \in \mathcal{H}$ satisfies the "gluing condition" at $t=0$ (acceleration computed from history matches $\ddot{\phi}^0(0-)$) to ensure $C^2$ smoothness at the junction, though $C^1$ solutions exist without this.
3. No "tangential" causal intersections in the history (roots are simple).

**Statement:**
There exists a maximal time $T > 0$ and a unique solution $\mathbf{x}(t)$ on $[-h, T)$ such that $\mathbf{x}_0 = \phi^0$ and $\mathbf{x}(t)$ satisfies the regularized master equation.

*Proof Strategy:*
The problem is reduced to $\dot{\mathbf{x}}(t) = \mathbf{v}(t), \dot{\mathbf{v}}(t) = F(\mathbf{x}_t)$. Since $F$ is locally Lipschitz on the open subset of $\mathcal{H}$ where causal roots are simple (Lemma 1), the Picard-Lindelof theorem for Banach spaces applies.

---

### Global Existence vs. Blow-Up

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

### Introduction

Standard conservation laws (energy, momentum, angular momentum) rely on the application of Noether's Theorem to local Lagrangian densities. In this delayed setting, the force at time $t$ depends on the phase-space trajectory over the interval $[t - h, t]$.

Symmetries of the substrate (Euclidean Void + Absolute Time) still imply conservation laws, but the conserved quantities are no longer simple functions of the instantaneous state $(\mathbf{x}, \mathbf{v})$. Instead, they are **functionals on the history space** $\mathcal{H}$.

This section derives these functionals, establishes the exact symmetry group of the regularized dynamics ($\eta > 0$), and provides the *a priori* bounds required to ensure physical well-posedness (preventing unphysical runaway acceleration).

---

### The Global Symmetry Group

We consider the regularized two-body system in the Euclidean Void $\mathbb{R}^3$ with metric $\delta_{ij}$ and absolute time $t$.

#### Definition 1 (The Fundamental Symmetry Group)
The background substrate and the master equation interaction kernel
$$
\mathbf{a}_{ij}(t) \propto \frac{\mathbf{x}_i(t) - \mathbf{x}_j(t_0)}{\|\mathbf{x}_i(t) - \mathbf{x}_j(t_0)\|^2}
$$
(regularized by $\eta$) respect the group:
$$
G_{\text{fund}} = E(3) \times \mathbb{R}_{\text{time}}
$$
where $E(3) = \mathbb{R}^3 \rtimes O(3)$ is the Euclidean group of spatial translations and rotations, and $\mathbb{R}_{\text{time}}$ denotes time translation.

#### Theorem 1 (Invariance of the Equations of Motion)
Let $\mathbf{x}(t)$ be a solution to the master equation.
1. **Time Translation:** For any $\tau \in \mathbb{R}$, $\mathbf{y}(t) = \mathbf{x}(t + \tau)$ is also a solution.
2. **Spatial Isometry:** For any $R \in O(3)$ and $\mathbf{b} \in \mathbb{R}^3$, $\mathbf{y}(t) = R\mathbf{x}(t) + \mathbf{b}$ is also a solution.

*Proof Sketch:*
The causal constraint $\|\mathbf{x}_i(t) - \mathbf{x}_j(t_0)\| = c_f(t - t_0)$ depends only on the Euclidean distance and time difference. Both are invariants of $G_{\text{fund}}$. The vector direction $\hat{\mathbf{r}}$ rotates covariantly with $R$. Thus, the dynamics are form-invariant.

**Implication:** There exist exact integrals of motion corresponding to these symmetries. However, because the interaction is non-local in time, these integrals must account for "momentum and energy in flight" (stored in the wake surfaces).

---

### Conservation of Generalized Momentum

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

### Energy and The Lyapunov Functional

Energy conservation is the critical constraint preventing runaway solutions (MCB-09).

#### Definition 3 (The History Hamiltonian)
Since the system is time-translation invariant, there exists a conserved quantity $\mathcal{H}$. For state-dependent delays, this is a **Lyapunov-Krasovskii Functional**:
$$
\mathcal{H}(\mathbf{x}_t) = K(\mathbf{v}(t)) + \mathcal{U}_{\text{history}}(\mathbf{x}_t).
$$

1. **Kinetic Energy:** $K(t) = \sum \frac{1}{2} m_i \|\mathbf{v}_i(t)\|^2$.
2. **Potential Functional:** $\mathcal{U}_{\text{history}}$ accumulates the work done by the conservative forces. Unlike an instantaneous potential $V(r)$, this depends on the configuration of all active wake surfaces.

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
In the master equation dynamics, an isolated binary cannot undergo runaway acceleration ($v \to \infty$) *unless* the potential energy functional $\mathcal{W}(t)$ diverges to $-\infty$.

*Proof Logic:*
Since $\mathcal{E}_{\text{tot}}$ is constant:
$$
K(t) = \mathcal{E}_{\text{tot}} - \mathcal{W}(t).
$$
For $K(t)$ to diverge, $\mathcal{W}(t)$ must decrease without bound.
1. **Partner Attraction:** $q_1 q_2 < 0$. The potential is negative (attractive). As $r \to 0$, $V \to -\infty$. Collapse leads to infinite kinetic energy (standard Kepler singularity, resolved by self-hit).
2. **Self-Hit Repulsion:** $q_1 q_1 > 0$. The force is **repulsive**. The potential contribution is **positive**.
  *  Work done by self-hit: If a particle is pushed "from behind" by its own wake, it gains $K$.
  *  However, this energy must come from the $\mathcal{W}$ term.
  *  Since self-hit potential is repulsive (positive energy hill), converting it to kinetic energy lowers the total potential.
  *  **Crucial Bound:** The deferred work encoded in a self-wake is finite (determined by emission charge). A particle cannot extract infinite energy from its own past unless it puts infinite energy *into* the field first.

**Conclusion:** The "free lunch" runaway, where a particle accelerates itself indefinitely using self-forces, is forbidden by the conservation of $\mathcal{H}$. The system can oscillate or settle, but it cannot explode to $v=\infty$ without singular collapse of the radius.

---
