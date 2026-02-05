# Weak Mixing in the Architrino Assembly Architecture (CKM-first draft)

## Purpose
Sketch how CKM flavor mixing emerges from the AAA geometry: weak (Active-Triad) basis vs. mass (shielding) basis, and why off-diagonal elements shrink with core depletion.

## Minimal premises
- **Generations = shielding level:** Gen I tri-binary (u,d), Gen II bi-binary (c,s), Gen III uni-binary (t,b).
- **Weak basis = Active Triad:** SU(2) acts on the exposed three decoration sites (polarity = $T_3$). This basis does not align with the shielding (mass) basis once cores differ.
- **Mass basis = shielding eigenstates:** Core shielding/drag sets the mass scale; each generation defines a distinct mass eigenstate per flavor type (up-type, down-type).

## Geometric picture of CKM
- A down-type quark state in the **weak basis** is an Active-Triad configuration living on a specific core (shielding level) but not yet diagonal in mass.
- The **mass basis** is the set of stable shielding eigenstates (Gen I/II/III). The overlap between the weak-basis state and each mass eigenstate gives the CKM elements for that row/column.
- **Suppression intuition:** Larger shielding mismatch → smaller geometric overlap. Thus $|V_{ud}|$ is large (same shielding tier), $|V_{us}|$ smaller (tri ↔ bi), $|V_{ub}|$ tiny (tri ↔ uni). Similar logic for the up-type rows.

## Working hypotheses (needs derivation/simulation)
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
