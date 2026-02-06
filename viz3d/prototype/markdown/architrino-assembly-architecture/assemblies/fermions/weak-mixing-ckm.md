# Weak Mixing in the Architrino Assembly Architecture (CKM)

## Purpose
Sketch how CKM flavor mixing emerges from the AAA geometry: weak (Active-Triad) basis vs. mass (shielding) basis, and why off-diagonal elements shrink with core depletion.

## Minimal premises
- **Generations = shielding level:** Gen I tri-binary (u,d), Gen II bi-binary (c,s), Gen III uni-binary (t,b).
- **Weak basis = Active Triad:** SU(2) acts on the exposed three decoration sites (polarity = $T_3$). This basis does not align with the shielding (mass) basis once cores differ.
- **Mass basis = shielding eigenstates:** Core shielding/drag sets the mass scale; each generation defines a distinct mass eigenstate per flavor type (up-type, down-type).

 Active-Triad exposure (working hypothesis): in translation, the three **forward** personality sites are more exposed (outside the particle’s own wake), so they form the Active Triad; trailing sites are likely shielded by the wake/slipstream. Needs simulation confirmation.

 Vacuum sourcing note: in AAA there is no empty vacuum—only the Noether Sea. Weak reconfigurations (e.g., heavy → light generation) may draw assembly parts from the Sea; treat any net architrino “gain” during decay as speculative until energy/number flow is explicitly budgeted.

## Geometric picture of CKM
- A down-type quark state in the **weak basis** is an Active-Triad configuration living on a specific core (shielding level) but not yet diagonal in mass.
- The **mass basis** is the set of stable shielding eigenstates (Gen I/II/III). The overlap between the weak-basis state and each mass eigenstate gives the CKM elements for that row/column.
- **Suppression intuition:** Larger shielding mismatch → smaller geometric overlap. Thus $|V_{ud}|$ is large (same shielding tier), $|V_{us}|$ smaller (tri ↔ bi), $|V_{ub}|$ tiny (tri ↔ uni). Similar logic for the up-type rows.

### Wolfenstein parametrization (to 𝒪(λ³))

Use this as a target when deriving overlaps/angles from shielding geometry and Active-Triad alignment.

With the parameters below, this Wolfenstein form reproduces the PDG magnitudes to 𝒪(λ³).

Matrix form (Wolfenstein to 𝒪(λ³)):

$$
V \simeq
\begin{pmatrix}
1 - \tfrac12\lambda^2 & \lambda & A\lambda^3(\rho - i\eta)\\
-\lambda & 1 - \tfrac12\lambda^2 & A\lambda^2\\
A\lambda^3(1-\rho - i\eta) & -A\lambda^2 & 1
\end{pmatrix},\quad
\lambda\approx0.225,\ A\approx0.83,\ \rho\approx0.14,\ \eta\approx0.35.
$$

### PDG CKM (2024 central values, magnitude)

<div align="center">

|   | d | s | b |
|---|---|---|---|
| u | 0.974 | 0.225 | 0.0037 |
| c | 0.225 | 0.973 | 0.041 |
| t | 0.0087 | 0.040 | 0.999 |

</div>

### AAA shielding-tier view (IMO = Inner/Middle/Outer present)

Interpretation (hypothesis): overlaps fall with shielding mismatch. Rows = up-type cores, cols = down-type cores. What “overlap” means here: the projection of a weak-basis state (Active-Triad configuration) onto a mass eigenstate (shielding geometry). In practice it is an inner product of their wavefunctions/configurations; $|\langle \text{mass} | \text{weak} \rangle|^2$ would give the CKM entry’s probability weight. We still need an explicit functional form for this projection.

<div align="center">

|   | d (IMO) | s (IM–) | b (I– –) |
|---|---------|---------|---------|
| u (IMO) | high overlap | medium | tiny |
| c (IM–) | medium | high | medium–low |
| t (I– –) | tiny | medium–low | high |

</div>

Legend: IMO = Inner+Middle+Outer; IM– = Inner+Middle; I– – = Inner only. Qualitative “high/medium/tiny” encodes the shielding-match hypothesis; actual values must be derived from overlap integrals. 

### Using CKM in amplitudes (quick examples)

- **Rule:** For a charged-current vertex with $W$, multiply by $V_{ij}$ where $i$ is up-type (u,c,t) and $j$ is down-type (d,s,b); rates scale with $|V_{ij}|^2$. Neutral currents (Z/γ) are flavor-diagonal (no CKM).
- **Beta decay:** $d \to u\,e^- \bar\nu_e$ uses $V_{ud}\approx0.974$; $\mathcal{M}\propto G_F V_{ud}$, rate $\propto |V_{ud}|^2$ times nuclear form factors.
- **Semileptonic $B$ decay:** $b \to c\,\ell^- \bar\nu_\ell$ uses $V_{cb}\approx0.041$; $\Gamma \propto |V_{cb}|^2 G_F^2 m_b^5$ (times hadronic form factor).
- **Loop/rare $b\to s$:** factors like $V_{tb} V^*_{ts}$ set the suppression and the CP phase in interference terms.

## Working hypotheses
1. **Basis misalignment source:** The Active Triad orientation couples weakly to shielding-induced drag axes, producing a small rotation between weak and mass bases proportional to the shielding contrast.
2. **Matrix structure:** Off-diagonal CKM elements scale with overlap integrals of Active-Triad waveforms on different shielding geometries; expect hierarchical suppression matching observed pattern ($|V_{ub}| \ll |V_{us}| \ll |V_{ud}|$).
3. **CP phase:** A relative geometric phase in the triad/braid ordering could supply the CKM phase; requires explicit braid/triad transport calculation.

## What to compute next
- Define explicit weak-basis states for each down-type quark as Active-Triad charge configurations on tri/bi/uni cores.
- Compute overlaps with mass eigenstates (shielding eigenmodes) to extract a CKM-like matrix; compare hierarchy to data.
- Track possible geometric phases in braids/triads to see if a CP-violating phase emerges naturally.
- Test sensitivity to core depletion: vary shielding strength and see how off-diagonals shrink.

## Pointers
- Active Triad & shielding definitions: `assemblies/fermions/quantum-number-mapping.md` (Sections on weak isospin, generation hierarchy).
- Gauge-boson couplings: `assemblies/bosons/electroweak-bosons.md` (W/Z corridors acting on Active Triad).

_Status: speculative scaffold for a derivation. Fill in with explicit states, overlaps, and phase calculations._
