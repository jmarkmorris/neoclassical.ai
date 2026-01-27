# MCB Attractor and Max-Curvature Orbit

This document collects the full two-body, self-hit analysis for the maximum-curvature binary (MCB), including delay geometry, force components, stability criteria, and computational diagnostics. It is the canonical reference for MCB attractor status.

# Maximum-Curvature Circular Orbit (Opposite Charges)

**Goal**: Characterize the circular, constant-speed, constant-radius configuration of two opposite-charge architrinos and investigate where curvature $\kappa = 1/R$ is maximized. We work in units with field speed $c_f = 1$ and use the canonical delayed, purely radial per-hit law.

**Plain language**: We seek the tightest (smallest-$R$) steady circle an opposite-charge pair can trace when the only forces come from delayed, radial interactions with the partner (multiple-hits) and from one's own past emissions (self-hits, active only when speed exceeds field speed).

---

## Foundational Context (Ontological Clarification)

### The Maximal Curvature Binary (MCB) as Fundamental Unit

In the architrino framework, the **Maximal Curvature Binary (MCB)** is the **inner binary** of a tri-binary assembly, stabilized by self-hit dynamics when $v > c_f$. It defines the **fundamental physical units**:

- **Length standard**: The orbital radius $r_{\text{min}}$ of the MCB is the **prototype rod**.
- **Time standard**: The orbital period $T_{\text{MCB}} = 1/f_{\text{MCB}}$ is the **prototype clock tick**.

The MCB radius $r_{\text{min}}$ is determined by the balance of:
1. Coulomb-like attraction between opposite charges ($\propto |e/6|^2 / r^2$),
2. Self-hit repulsion (non-Markovian feedback when $v > c_f$),
3. Centripetal requirement for stable circular orbit.

**Expected scale**: $r_{\text{min}} \sim 10^{-15}$ to $10^{-12}$ m (classical electron radius to Compton wavelength).

**Dynamical priority (attractor status):** The architecture assumes the MCB is a **robust attractor**, not a finely tuned periodic orbit. This must be established explicitly:
- Start from a reduced two-body model (opposite charges, self-hit enabled, explicit $\eta$).
- Construct a Poincaré map (e.g., strobing at orbital phase) and locate the MCB as a fixed point.
- Compute Floquet multipliers / Lyapunov exponents and map the basin of attraction under perturbations in radius, phase, and velocity.
Only if the multipliers lie strictly inside the unit circle and the basin is non-trivial do we have the attractor the architecture relies on. If neutrality or instability is found, the tri-binary ladder and Noether-core claims must be downgraded or the interaction law revised (e.g., additional damping/medium effects).

### Relationship to Tri-Binary Structure

- **Inner binary** (MCB): $v > c_f$; self-hit stabilized; **defines fundamental units**.
- **Middle binary**: **always** at $v = c_f$ with **variable radius/frequency**; symmetry-breaking threshold and **energy-storage fulcrum**; defines effective light speed $c_{\text{eff}}$.
- **Outer binary**: $v < c_f$; expansion/contraction modes; **couples to Noether Sea** for gravitational/cosmological effects.

**This document analyzes the isolated two-body problem to understand MCB formation and stability.**

---

## Setup and Notation (Symmetric Frame)

- **Two architrinos** with charges $q_1 = -\epsilon$ and $q_2 = +\epsilon$ (where $\epsilon = |e/6|$).
- **Equal-time positions** (in absolute time $t$) are diametrically opposite on a circle of radius $R$ about the midpoint.
- **Uniform circular motion**: Angular speed $\omega$, constant tangential speed $s = R\omega$.
- **Non-translating binary**: Circle center (midpoint) is fixed in Euclidean 3D space; no net translation.

### Phase Angles and Delays

Let $\delta_s$ and $\delta_p$ denote the angular phase separations (measured along the circle) between:
- **Self** (same particle): Current position → its own past emission position that hits "now."
  - Delay time: $\tau_s$; angular separation: $\delta_s = \omega \tau_s$.
  - Chord length: $r_s = 2R \sin(\delta_s / 2)$.
  
- **Partner** (other particle): Current position → partner's past emission position that hits "now."
  - Delay time: $\tau_p$; angular separation: $\delta_p = \omega \tau_p$.
  - Chord length: $r_p = 2R \cos(\delta_p / 2)$.

### Causal-Time Constraints (Field Speed $c_f = 1$)

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

### Terminology: Roots and Winding Numbers

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

## Per-Hit Directions and Force Components

### Local Coordinate Frame at Receiver

- **Radial outward**: $\hat{e}_r$ (from rotation center toward receiver).
- **Tangential**: $\hat{e}_t$ (direction of motion along circle).

### Unit Directions of Lines of Action (Emission → Reception)

**Self-hit**:
$$
\hat{u}_s = \sin(\delta_s / 2) \, \hat{e}_r + \cos(\delta_s / 2) \, \hat{e}_t.
$$

**Partner hit** (geometric chord across circle):
$$
\hat{u}_p = \cos(\delta_p / 2) \, \hat{e}_r - \sin(\delta_p / 2) \, \hat{e}_t.
$$

### Canonical Per-Hit Accelerations

Using the delayed, radial law with magnitude $\kappa \epsilon^2 / r^2$ (where $\kappa$ is a coupling constant and $\epsilon = |e/6|$):

**Self-hit** (like charges → repulsive):
$$
\mathbf{a}_s = +\kappa \epsilon^2 \frac{1}{r_s^2} \hat{u}_s.
$$

**Partner hit** (opposite charges → attractive):
$$
\mathbf{a}_p = -\kappa \epsilon^2 \frac{1}{r_p^2} \hat{u}_p.
$$

---

### Radial and Tangential Components

Define **inward radial** as positive (toward center) and **tangential** as positive in direction of motion.

**Chord lengths**:
$$
r_s = 2R \sin(\delta_s / 2), \quad r_p = 2R \cos(\delta_p / 2).
$$

**Inward radial components**:

- **Self** (repulsive → outward → negative):
  $$
  A_{s,\text{rad}} = -\kappa \epsilon^2 \frac{\sin(\delta_s / 2)}{r_s^2} = -\frac{\kappa \epsilon^2}{4R^2 \sin(\delta_s / 2)}.
  $$

- **Partner** (attractive → inward → positive):
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

### Sub-Field-Speed Simplification ($s \le 1$; No Self-Hits)

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

## Requirements for True Circular Orbit (Working Hypothesis)

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

### Apparent Obstruction: Non-Negativity of Tangential Components

**Key Result**: For the symmetric, non-translating two-body circle geometry, and for **any** single causal root (including all older roots with winding index $m \ge 0$), the tangential components satisfy:

$$
T_s \ge 0, \quad T_p \ge 0 \quad \Rightarrow \quad T = T_s + T_p > 0.
$$

**Conclusion (provisional)**: The per-hit analysis yields $T \ge 0$, which appears to obstruct strict $T = 0$ at the level of a single-root snapshot. The working hypothesis is that the full multi-root, time-averaged dynamics admit a steady circular orbit with $\langle T \rangle = 0$ once self-hits are fully active.

- External fields or assemblies (e.g., embedding in Noether Sea),
- Modified interaction rules (e.g., velocity-dependent forces, radiation damping),
- Or multi-body stabilization (tri-binary structure with three nested pairs).

**Plain language**: The isolated pair shows persistent tangential drive at the per-hit level, so a steady circle must arise from averaging over many self-hit roots or from additional structure in the delay law. This is a primary test of the MCB attractor hypothesis.

---

## What "Maximum Curvature" Demands

From the radial component formula:

$$
A_{\text{rad}} = \frac{\kappa \epsilon^2}{4R^2} \left( \frac{1}{\cos(\delta_p / 2)} - \frac{1}{\sin(\delta_s / 2)} \right).
$$

**Increasing curvature** ($\kappa = 1/R$ larger → $R$ smaller) requires **stronger inward radial force**. This occurs when:

1. **$\delta_p$ increases** → $\cos(\delta_p / 2)$ decreases → partner term $1/\cos(\delta_p / 2)$ **increases** (stronger inward pull).
2. **$\delta_s$ increases** → $\sin(\delta_s / 2)$ increases → self term $1/\sin(\delta_s / 2)$ **decreases** (weaker outward repulsion).

**Critical observation**: Near the self-hit threshold ($s \to 1^+$, $\delta_s \to 0^+$):

$$
\frac{1}{\sin(\delta_s / 2)} \to \infty \quad \text{(strong outward repulsion)}.
$$

Therefore, **just-above-threshold self-hits do not maximize curvature**—they **strongly oppose** it by blowing up the outward radial component.

**Maximum curvature** (smallest stable $R$) likely occurs at **higher speeds** ($s \gg 1$) where:
- Multiple self-hits ($m \ge 1$) are active,
- $\delta_s$ is large (approaching $\pi$),
- Outward self-repulsion is minimized while inward partner attraction is maximized.

**However**: Due to the per-hit $T > 0$ result, this "maximum curvature" state is a **hypothesis** for the isolated two-body system. Its stability must be verified by the full, multi-root time-averaged dynamics.

---

## Self-Hit Multiplicity vs. Speed

**Definition**: A self-hit is an emission time from the same architrino that satisfies the causal constraint $r = (t - t_0)$ and arrives "now." In uniform circular, non-translating geometry, admissible self-roots are indexed by winding number $m \ge 0$ and minimal angular separation $\tilde{\delta}_s \in (0, \pi]$:

$$
\delta_s = \tilde{\delta}_s + 2\pi m = 2s \sin(\tilde{\delta}_s / 2).
$$

### Counting Self-Hits by Winding Index

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

- $1 < s < 3\pi/2 \approx 4.712$ → $N_{\text{self}} = 1$ (only $m = 0$).
- $s \ge 3\pi/2$ → $N_{\text{self}} \ge 2$ ($m = 0$ and $m = 1$).
- Higher $m$ branches turn on at $s \ge 5\pi/2$, $7\pi/2$, etc.

**Note**: Straight-line motion admits **no self-hits** even if $s > 1$; **curvature is required**. The above statements apply specifically to uniform circular, non-translating geometry.

---

## Where Do Causal Hits Come From on the Circle? (Discrete Azimuth Pattern)

**Context**: Non-translating, uniform circular binary at fixed speed $s$. Receiver "now" at azimuth $\theta = 0$.

The emission points on the circle that can produce hits "now" form a **finite, discrete set** of azimuths determined by the delay equations—**not arbitrary locations**.

### Partner Hits

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
- As $m$ increases, $\tilde{\delta}_p$ decreases → $\varphi_p$ drifts monotonically toward $\pi$ (diametrically opposite point).

### Self-Hits

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
  - Within a branch, $\tilde{\delta}_s$ decreases with $s$ → $\varphi_s$ drifts toward $-\pi$.

### Multiplicity and Pattern

- At any fixed $s$, the admissible emission azimuths form a **finite, ordered "comb"** of discrete points.
- These points accumulate toward the diametric opposite direction:
  - $\varphi = \pi$ for partner,
  - $\varphi = -\pi$ for self.
- As $s$ increases, the set grows in **steps** at the thresholds above; more roots appear but they **never fill the circle**.
- Multiple hits at the same "now" correspond to different winding indices $m$ (and occasionally multiple $\tilde{\delta}_s$ solutions within a branch); all are fixed by the delay equations and circle geometry.

**Plain language**: For a given speed, hits come from a **short list of specific angles** set by causality and delay—not from arbitrary points all around the circle. Going faster unlocks more of these specific angles at predictable threshold speeds.

---

## Practical Recipe (Computational)

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
   - Near $s \to 1^+$: Strong outward self-repulsion ($1/\sin(\delta_s/2) \to \infty$) → low curvature.
   - Higher $s$ ($s \gg 1$): Multiple self-hits active; $\delta_s$ large → outward repulsion minimized → higher curvature possible (but still not stable due to $T > 0$).

---

## MCB Attractor Hypothesis and Test Plan

**Working hypothesis**: An isolated electrino–positrino pair spirals inward until self-hit feedback halts the collapse and a steady circular orbit forms at $r_{\text{min}}$. This is the MCB, and it is a natural attractor of the two-body delay dynamics.

**Mechanism (summary)**:
1. **Spiral-in** ($v < c_f$): Partner attraction dominates; tangential drive accelerates; radius decreases.
2. **Self-hit onset** ($v > c_f$): Non-Markovian feedback activates and begins to oppose further collapse.
3. **MCB regime** ($v \gg c_f$): Self-repulsion is minimized in radial direction while partner attraction accumulates across multiple roots; the orbit stabilizes at maximal curvature if $\langle T \rangle \approx 0$.

**Key geometric expectations**:
- **Not** at the self-hit threshold: $\delta_s \to 0^+$ gives large outward radial term; tight orbits are blocked there.
- **High-speed regime**: $\delta_s \to \pi$ minimizes radial self-repulsion; multiple partner hits raise inward pull; balance occurs at finite $r_{\text{min}}$.

**Fundamental units (hypothesis)**:
- $r_{\text{min}}$ defines the prototype rod and $T_{\text{MCB}}$ the prototype clock tick, emergent from the balance of partner attraction, self-hit repulsion, and centripetal requirement.

**Attractor test requirements**:
- **Poincaré map**: locate the MCB as a fixed point of the stroboscopic map.
- **Floquet multipliers / Lyapunov exponents**: require all multipliers strictly inside the unit circle.
- **Basin scan**: verify non-trivial attraction under perturbations in radius, phase, and velocity.

**Architectural implications**:
- If the attractor test succeeds, the MCB is the natural building block for tri-binaries and larger assemblies.
- If it fails (neutral or unstable), the interaction law or medium coupling must be revised before claiming a stable ladder of modes.
