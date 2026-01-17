# Particle Masses: Emergent Inertia in the Noether Sea

**Purpose:** Capture how “mass” arises in the architrino architecture and what remains to be derived.

## Architectural stance
- Mass is **not intrinsic** at the substrate. Architrinos carry kinetic/potential energy but no innate characteristic mass $m$.
- Assemblies acquire **apparent inertial mass** from two coupled effects (see `validation/simulations/action-energy/potential-kinetic-energy.md`):
  - **Shielding:** Internal pro/anti structure plus sea polarization hide most internal energy; only a leakage fraction $\zeta \ll 1$ couples externally.
  - **Sea coupling/drag:** Moving assemblies must reorganize the tri-binary Noether Sea; resistance rises with speed and local sea density, yielding an emergent $c_{\text{eff}}$ and relativistic-like response.
- Operationally, $m_{\text{inertial}} \propto \zeta\,E_{\text{internal}}$ and grows with coupling to the surrounding sea.

## Fermions (ellipsoidal tri-binaries)
- **Origin of inertia:** Noether cores store large internal energy; far-field cancellation and sea shielding set $\zeta$, so external pushes see only a small “handle,” producing inertia.
- **Environment dependence:** Local sea density/strain modulate effective drag; stable atoms require near-zero net drag in equilibrium (see `foundations/ontology.md` stability note).
- **Generational structure:** Heavier generations expose more of the inner binaries (reduced shielding), increasing $\zeta$ and apparent mass.
- **Neutrinos:** Nearly complete shielding; tiny residual axial imbalance yields minuscule apparent mass and chiral selection in weak docking (see `assemblies/fermions/neutrinos.md`).
- **Binary energy hierarchy:** Each H/M/L binary carries a vastly different energy scale (frequency, orbital radius, architrino speed). Shielding is **geometry- and phase-dependent**, so the externally visible mass fluctuates with configuration; neutrino oscillations are a direct witness of this fluctuating shielding of internal energy.
- **Configuration ↔ PDG masses:** Different allowed binary configurations map to different apparent energies seen in experiments (PDG mass values and spreads). “Mass variation” tracks which internal mode is exposed; energy = mass in this bookkeeping.

## Bosons
- **Photon:** Planar corridor; edge-on propagation through the sea → effectively zero drag and no rest mass (`assemblies/bosons/electroweak-bosons.md`).
- **W/Z:** Short-lived corridors; apparent $80/91$ GeV peaks are **confinement energy + drag** of an inflated corridor in the sea. Widths/peaks may shift with medium stiffness.
- **Higgs:** Radial breathing mode of the sea; not a source of mass but a scalar excitation of the medium’s stiffness.

## Chirality and mass
- **What’s supported:** Chiral docking rules for weak corridors (W/Z) follow from phase geometry; matter/antimatter braid order distinguishes cores (`assemblies/fermions/fermion-mapping.md`, `assemblies/bosons/electroweak-bosons.md`).
- **What’s pending:** A derivation that left/right geometries couple with different drag coefficients to the polarized sea (i.e., chirality-driven mass splittings) is **not yet written**. Needs explicit sea polarization model and fit to fermion masses.

## Validation hooks
- Show $m_{\text{inertial}}$ scaling with $\zeta\,E_{\text{internal}}$ in simulations; verify emergent $E \sim m(\gamma-1)$ near $c_{\text{eff}}$.
- Bound sea-induced drag to avoid orbital decay (see `validation/adversarial/failure-criteria.md`).
- Test medium-dependence of W/Z peaks in dense plasma scenarios.
- Derive/fit the chirality–sea coupling if it is to explain mass splittings; otherwise mark as unsupported.
- Verify that coupling strength between spacetime assemblies (sea) and fermionic assemblies quantitatively matches inferred masses (mass = coupling to the sea).
