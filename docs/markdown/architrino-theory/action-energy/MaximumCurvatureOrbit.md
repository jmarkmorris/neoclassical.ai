# 00.2.3.3 — Maximum-Curvature Circular Orbit (opposite charges)

Goal: characterize the circular, constant‑speed, constant‑radius configuration of two opposite Architrinos and ask where curvature $\kappa$ = 1/R is maximized. We work in units with field speed v=1 and use the canonical delayed, purely radial per‑hit law.

Plain language: We look for the tightest (smallest‑R) steady circle an opposite‑charge pair can trace when the only pushes come from delayed, radial hits from the partner and from one’s own past emissions (self‑hits, active only when speed exceeds field speed).

---

## Setup and notation (symmetric frame)

- Two Architrinos with charges q1 = −$\epsilon$ and q2 = +$\epsilon$; equal‑time positions are always diametrically opposite on a circle of radius R about the midpoint.
- Uniform circular motion with angular speed $\omega$ and constant speed s = R$\omega$.
- Non-translating binary: the circle center (midpoint) is fixed in 3D Euclidean space; there is no net translational motion of the assembly.
- Let $\delta$s and $\delta$p denote the angular phase between the receiver’s current position and the source’s emission position along the circle for self and partner, respectively:
  - Self (same particle): $\delta$s ≡ $\omega$$\tau$s with delay $\tau$s; chord length rs = 2R sin($\delta$s/2).
  - Partner (other particle): $\delta$p ≡ $\omega$$\tau$p with delay $\tau$p; chord length rp = 2R cos($\delta$p/2).
- Causal‑time constraints (derived from r = $\tau$ with v=1):
  - Self: $\tau$s = 2R sin($\delta$s/2) and $\delta$s = $\omega$$\tau$s ⇒ $\delta$s = 2s sin($\delta$s/2).
  - Partner: $\tau$p = 2R cos($\delta$p/2) and $\delta$p = $\omega$$\tau$p ⇒ $\delta$p = 2s cos($\delta$p/2).

These two scalar equations determine ($\delta$s, $\delta$p) given s (provided s>1 so that self‑hits exist; see Walkthrough Step 8).

Terminology (root): At observation time t, a root is any emission time t0<t for which the causal‑distance constraint r = v(t − t0) holds between the receiver‑now and the source‑at‑t0. In uniform circular motion, roots correspond to angular separations $\delta$ that satisfy the delay equations; “older roots” are indexed by an integer m ≥ 0.

Integer‑indexed older roots (winding numbers):
- Let $\delta$̃s ∈ (0, $\pi$] and $\delta$̃p ∈ (0, $\pi$] denote the minimal angular separations at reception (principal separations that determine the chords).
- The full families of causal delays are
  - Self: $\delta$s(m) = 2s sin($\delta$̃s/2) + 2$\pi$ m,
  - Partner: $\delta$p(m) = 2s cos($\delta$̃p/2) + 2$\pi$ m,
  for m = 0,1,2,… (v=1 units).
- Geometric components (unit directions and 1/r²‑weighted magnitudes) depend only on the minimal separations $\delta$̃s, $\delta$̃p via the chords; the winding index m affects timing/ordering but not the sign of those components.

---

## Per‑hit directions and components

Choose local axes at the receiver: radial outward $\hat{e}_r$ (from the rotation center) and tangential $\hat{e}_t$ (direction of motion).

- Unit directions of the lines of action (source emission → receiver now):
  - Self: $\hat{u}_s = \sin(\delta_s/2)\,\hat{e}_r + \cos(\delta_s/2)\,\hat{e}_t$.
  - Partner (geometric chord): $\hat{u}_p = \cos(\delta_p/2)\,\hat{e}_r - \sin(\delta_p/2)\,\hat{e}_t$.
- Canonical per‑hit accelerations (magnitudes $\kappa$|q q′|/r² with signs):
  - Self is like‑on‑like (repulsive): $a_s = +\,\kappa\,\epsilon^2\, r_s^{-2}\,\hat{u}_s$.
  - Partner is unlike (attractive): $a_p = -\,\kappa\,\epsilon^2\, r_p^{-2}\,\hat{u}_p$.

Radial (inward taken as positive) and tangential components at an instant:

- $r_s = 2R \sin(\delta_s/2)$, $r_p = 2R \cos(\delta_p/2)$.
- Inward radial:
  - Self (repulsive, outward): $A_{s,\text{rad}} = -\,\kappa\,\epsilon^2 \,\frac{\sin(\delta_s/2)}{r_s^2} = -\,\frac{\kappa\,\epsilon^2}{4R^2 \sin(\delta_s/2)}$.
  - Partner (attractive, inward): $A_{p,\text{rad}} = +\,\kappa\,\epsilon^2 \,\frac{\cos(\delta_p/2)}{r_p^2} = +\,\frac{\kappa\,\epsilon^2}{4R^2 \cos(\delta_p/2)}$.
  - Net inward radial:
    $$
    A_{\text{rad}} = \frac{\kappa\,\epsilon^2}{4R^2}\Big(\frac{1}{\cos(\delta_p/2)} - \frac{1}{\sin(\delta_s/2)}\Big).
    $$
- Tangential (along ê_t, positive in direction of motion):
  - Self: $T_s = +\,\kappa\,\epsilon^2 \,\frac{\cos(\delta_s/2)}{r_s^2} = \frac{\kappa\,\epsilon^2 \cos(\delta_s/2)}{4R^2 \sin^2(\delta_s/2)}$.
  - Partner: $T_p = +\,\kappa\,\epsilon^2 \,\frac{\sin(\delta_p/2)}{r_p^2} = \frac{\kappa\,\epsilon^2 \sin(\delta_p/2)}{4R^2 \cos^2(\delta_p/2)}$.
  - Net tangential: $T = T_s + T_p$ (both terms are nonnegative for $0<\delta_s,\delta_p<\pi$).

Sub-field-speed simplification (s ≤ 1; no self-hits):
- Net tangential reduces to the partner term,
  $$
  T(s<1) = T_p = \frac{\kappa\,\epsilon^2}{4R^2}\,\frac{\sin(\delta_p/2)}{\cos^2(\delta_p/2)}.
  $$
  Using the delay relation $\delta_p = 2s\cos(\delta_p/2)$, this can be written as
  $$
  T(s<1) = \frac{\kappa\,\epsilon^2\,s^2}{R^2}\,\frac{\sin(\delta_p/2)}{\delta_p^2} \;>\; 0.
  $$

Uniform circular motion requires, in a time‑averaged sense over a small window that resolves mollified wake surfaces ($\eta$>0):
- Centripetal balance: $A_{\text{rad}} = s^2/R$.
- Zero power / constant speed: $T = 0$.

Non‑negativity of tangential components (obstruction): For the symmetric, non‑translating two‑body circle and any causal root (including older roots reduced to their minimal angular separations $\delta$̃s, $\delta$̃p ∈ (0, $\pi$]), the tangential components satisfy $T_s \ge 0$ and $T_p \ge 0$, hence $T = T_s + T_p > 0$ at any instant. Therefore an isolated two‑body cannot achieve $T = 0$; a true constant‑speed, fixed‑radius circle would require additional physics (e.g., external fields/assemblies or a modified interaction rule) to cancel tangential power.

---

## What “maximum curvature” demands

For a true constant‑speed circular orbit at speed s and radius R you would require both:
- Centripetal balance $A_{\text{rad}} = s^2/R$, and
- Zero tangential power $T = 0$.
However, in the isolated, non‑translating two‑body case T>0 for all causal roots (see obstruction above). Therefore no constant‑speed, fixed‑radius circular orbit exists under the canonical law.

From the component formulas,
- Inward radial increases if 1/ cos($\delta$p/2) grows (partner emission more “ahead”) and/or 1/ sin($\delta$s/2) shrinks (self emission not too “recent”). Near $\delta$s→0⁺ the self term blows up like 1/sin($\delta$s/2), i.e., strong outward repulsion; hence “just‑above‑threshold” self‑hits do not maximize curvature—they strongly oppose it.


---

## Practical recipe (computational)

1) Pick a speed s>1 (self‑hits active). Solve
   - $\delta$s = 2s sin($\delta$s/2),
   - $\delta$p = 2s cos($\delta$p/2),
   for ($\delta$s, $\delta$p) ∈ (0,$\pi$).

2) Enumerate causal roots by integer index m ≥ 0 at the chosen s. Use the minimal angular separations $\delta$̃s, $\delta$̃p ∈ (0, $\pi$] (principal geometry) to compute chords and components; the winding index m only affects emission timing and arrival ordering. If desired, accumulate radial and tangential contributions with 1/r² weighting to verify that T(s) > 0.



Notes:
- Near the self‑hit threshold (s↘1), the self radial term is large and outward (∝1/sin($\delta$s/2)); tight circles are therefore not realized there.

---

## Self-hit multiplicity vs. speed (uniform circle, non-translating)

Definition (root): a self-hit is an emission time from the same Architrino that satisfies the causal constraint r = (t−t0) and arrives “now.” In the uniform circular, non‑translating geometry, admissible self roots are indexed by an integer winding number m ≥ 0 and a minimal angular separation $\delta$̃s ∈ (0, $\pi$], related by
$$
\underbrace{\delta_s}_{=\ \tilde{\delta}_s+2\pi m}
\;=\;
2s\,\sin\!\big(\tilde{\delta}_s/2\big).
$$

Counting by winding index:
- Self-hits exist only for s > 1 (the sub‑field‑speed regime has no self-hits).
- A new self‑hit branch (for winding m) appears when
  $$
  s \;\ge\; s_m^\star \;=\; \frac{(2m+1)\,\pi}{2}\,.
  $$
- Hence the number of distinct self‑hits by winding index at speed s is
  $$
  N_{\text{self}}(s)
  \;=\;
  \begin{cases}
  0, & s \le 1,\\[4pt]
  1 + \max\!\big(0,\ \big\lfloor s/\pi - \tfrac{1}{2}\big\rfloor\big), & s > 1.
  \end{cases}
  $$

Examples:
- 1 < s < 2 ⇒ Nself = 1 (exactly one self‑hit, m = 0).
- 2 ≤ s < 3$\pi$/2 ≈ 4.712 ⇒ Nself = 1.
- s ≥ 3$\pi$/2 ⇒ Nself ≥ 2 (m = 0 and m = 1 turn on); higher m appear at s ≥ 5$\pi$/2, 7$\pi$/2, …

Note: Straight‑line motion admits no self‑hits even if s > 1; curvature is required. The statements above apply to the uniform circular, non‑translating geometry.

---

## Summary answers

- Isolated two‑body universe (non‑translating): A true constant‑speed, fixed‑radius circular state does not appear to exist under the canonical delayed, purely radial law with constant per‑wavefront amplitude. In the symmetric circle geometry all causal roots contribute non‑negative tangential power, so T(s)>0 and constant speed cannot be maintained without additional physics (external fields/assemblies or a modified interaction rule).

Plain language: In the isolated pair, tangential pushes never cancel, so a steady circle is not available.

---

## Where do causal hits come from on the circle? (discrete azimuth pattern)

Context: non‑translating, uniform circular binary at fixed speed $s$ (receiver “now” at azimuth $0$). The emission points on the circle that can produce hits “now” form a finite, discrete set of azimuths determined by the delay equations; they are not arbitrary locations.

Partner hits
- Minimal angular separation $\tilde{\delta}_p \in (0,\pi]$; causal delays
  $$
  \delta_p(m) \;=\; \tilde{\delta}_p + 2\pi m \;=\; 2s\,\cos\!\big(\tfrac{\tilde{\delta}_p}{2}\big),\qquad m=0,1,2,\dots
  $$
- Emission azimuth at reception: $\varphi_p(m;s) = \pi - \tilde{\delta}_p(m;s)$.
- Existence (thresholds): for each $m\ge 0$ a solution exists only if $s > m\pi$. New partner azimuths turn on as $s$ crosses $\pi, 2\pi, 3\pi,\dots$; as $m$ increases, $\tilde{\delta}_p$ decreases and $\varphi_p$ drifts monotonically toward $\pi$ (the diametrically opposite point).

Self hits
- Minimal angular separation $\tilde{\delta}_s \in (0,\pi]$; causal delays
  $$
  \delta_s(m) \;=\; \tilde{\delta}_s + 2\pi m \;=\; 2s\,\sin\!\big(\tfrac{\tilde{\delta}_s}{2}\big),\qquad m=0,1,2,\dots
  $$
- Emission azimuth at reception: $\varphi_s(m;s) = -\,\tilde{\delta}_s(m;s)$.
- Existence (windows and thresholds):
  - Principal branch $m=0$ exists only for $1 < s \le \tfrac{\pi}{2}$ and terminates at $\tilde{\delta}_s=\pi$ when $s=\tfrac{\pi}{2}$.
  - For $m\ge 1$, a new branch appears when
    $$
    s \;\ge\; s_m^\star \;=\; \frac{(2m+1)\,\pi}{2}\,,
    $$
    i.e., at $3\pi/2,\ 5\pi/2,\ 7\pi/2,\dots$. Within a branch, $\tilde{\delta}_s$ decreases with $s$, so $\varphi_s$ drifts toward $-\pi$.

Multiplicity and pattern
- At any fixed $s$, the admissible emission azimuths form a finite, ordered “comb” of discrete points; they accumulate toward the diametric opposite direction ($\varphi=\pi$ for partner, $\varphi=-\pi$ for self) as $m$ increases.
- As $s$ increases, the set grows in steps at the thresholds above; more roots appear but they never fill the circle.
- Multiple hits at the same “now” correspond to different winding indices $m$ (and, for self, occasionally multiple $\tilde{\delta}_s$ solutions within a branch); all are fixed by the two delay equations and the circle geometry.

Plain language: For a given speed, hits come from a short list of specific angles set by delay—not from arbitrary points all around the circle. Going faster unlocks more of these specific angles at predictable threshold speeds.
