# Phil's Integrated TOC & File Structure: Network-Aware Design

## Executive Summary

Given that the web app supports **network navigation** (not just linear hierarchy), we can design a structure that serves **three modes simultaneously**:

1. **Linear (Textbook)**: Pedagogical reading order for newcomers
2. **Hierarchical (Concept Tree)**: Top-down conceptual navigation
3. **Network (Graph)**: Free exploration of interconnected ideas

The key insight: **Files are nodes, directories are conceptual clusters, and explicit metadata creates the edges.**

---

## 1. Core Design Principles

### 1.1 Files as Network Nodes
- Each markdown file is a **semantic unit** (concept, mechanism, test, or claim)
- Files contain metadata for network navigation
  - **Concept level** (foundational / architectural / phenomenological / applied)
  - **Dependencies** (what must be understood first)
  - **Related concepts** (lateral connections)
  - **Empirical anchors** (which experiments/observations constrain this)

### 1.2 Directories as Conceptual Neighborhoods
- Directories group **thematically related nodes**
- Not strict hierarchy—files can link across directories freely
- Directory structure optimizes **discovery** ("I'm interested in cosmology—where do I start?")

### 1.3 Multiple Navigation Paths
- **Linear path** (textbook TOC): Defined in `TOC.md` as ordered list
- **Hierarchical path** (concept tree): Defined by frontmatter `level` and `parent` fields
- **Network path** (graph): Defined by frontmatter `related` and `dependencies` fields


---

## 3. Final Directory Structure (Network-Optimized)

```
architrino-assembly-architecture/
├── README.md                          # Landing page: navigation guide
├── TOC.md                             # Linear reading order (textbook mode)
├── CONCEPT-TREE.md                    # Hierarchical concept outline
├── NETWORK-MAP.md                     # Graph visualization metadata
├── GLOSSARY.md                        # Indexed term definitions
├── CHANGELOG.md                       # Version history
│
├── substrate/                         # Level 1: What fundamentally exists
│   ├── README.md                      # "The Substrate: Space, Time, and Entities"
│   ├── absolute-time.md               # Why absolute time; defend vs relativity
│   ├── euclidean-void.md              # The 3D container
│   ├── architrino-entity.md           # Point transmitters/receivers
│   └── substrate-summary.md           # Integration: the stage is set
│
├── dynamics/                          # Level 2: How things move and interact
│   ├── README.md                      # "Fundamental Dynamics"
│   ├── master-equation.md             # The governing law
│   ├── causal-structure.md            # Delay geometry, path history
│   ├── self-hit-mechanism.md          # Non-Markovian memory
│   ├── velocity-regimes.md            # v < c_f, v = c_f, v > c_f
│   ├── two-body-systems.md            # Analytic solutions
│   ├── regularization.md              # Well-posedness, numerical handling
│   └── dynamics-summary.md
│
├── assemblies/                        # Level 3: Stable configurations
│   ├── README.md                      # "From Architrinos to Structure"
│   ├── binary-formation.md            # Two-body bound states
│   ├── maximum-curvature-orbit.md     # The fundamental length scale
│   ├── tri-binary-architecture.md     # Noether core: three nested binaries
│   ├── ellipsoidal-vs-planar.md       # Fermion/boson geometry
│   ├── assembly-atlas.md              # Catalog of stable configurations
│   ├── stability-analysis.md          # Attractors, basins, selection rules
│   ├── velocity-regime-transitions.md # How assemblies change with energy
│   └── assemblies-summary.md
│
├── particles/                         # Level 4: Standard Model mapping
│   ├── README.md                      # "Mapping Assemblies to Particles"
│   ├── effective-lagrangian.md        # From geometry to fields
│   ├── charge-quantization.md         # Why |e/6| → e/3, 2e/3, e
│   ├── fermions/
│   │   ├── electron.md
│   │   ├── muon-tau.md
│   │   ├── neutrinos.md
│   │   └── quarks.md
│   ├── bosons/
│   │   ├── photon.md
│   │   ├── gluons.md
│   │   ├── weak-bosons.md
│   │   └── higgs.md
│   ├── gauge-symmetries.md            # SU(3) × SU(2) × U(1) from geometry
│   ├── spin-statistics.md             # Derivation (not postulate)
│   ├── particle-masses.md             # Predicted vs observed
│   └── precision-tests.md             # g-2, α, CKM, PMNS
│
├── nuclear-atomic/                    # Level 5: Composite matter
│   ├── README.md                      # "From Particles to Atoms"
│   ├── nucleon-structure.md           # Protons, neutrons from quarks
│   ├── nuclear-binding.md             # Deuteron, alpha, magic numbers
│   ├── atomic-structure.md            # Electron orbitals, shells
│   ├── spectroscopy.md                # Predicted spectral lines
│   ├── molecular-geometry.md          # VSEPR, bond angles
│   ├── condensed-matter.md            # Phases, crystals, conductivity
│   └── dense-matter-eos.md            # White dwarfs, neutron stars
│
├── spacetime/                         # Level 6: Emergent geometry
│   ├── README.md                      # "Spacetime as Aether"
│   ├── aether-ontology.md             # Graviton-Higgs-binary sea
│   ├── emergent-metric.md             # g_μν(x) from assembly density
│   ├── proper-time.md                 # dτ/dt from assembly clocks
│   ├── gr-phenomenology.md            # Light bending, perihelion, frame drag
│   ├── ppn-parameters.md              # Post-Newtonian tests
│   ├── gravitational-waves.md         # Speed, polarization, dispersion
│   ├── singularity-resolution.md      # Planck cores, no r=0
│   ├── hierarchy-problem.md           # Energy shielding
│   └── spacetime-summary.md
│
├── cosmology/                         # Level 7: Universe-scale
│   ├── README.md                      # "Cosmology and the Universe"
│   ├── cosmological-ontology.md       # Steady-state vs Big Bang
│   ├── expansion-mechanism.md         # In-place expansion, not metric
│   ├── inflation-model.md             # Local deflation/inflation
│   ├── cmb-origin.md                  # Reinterpreted CMB
│   ├── bbn-predictions.md             # Light element abundances
│   ├── structure-formation.md         # P(k), σ_8, BAO
│   ├── h0-tension.md                  # Resolution pathway
│   ├── sigma8-tension.md              # LSS discrepancy
│   └── cosmology-summary.md
│
├── quantum/                           # Level 8: Interpretation
│   ├── README.md                      # "Quantum Mechanics Reinterpreted"
│   ├── pilot-wave-character.md        # Guidance from potential structure
│   ├── wavefunction-ontology.md       # What ψ represents
│   ├── superposition-mechanism.md     # Path history interference
│   ├── measurement-ontology.md        # No observer postulate
│   ├── entanglement-nonlocality.md    # Correlations in absolute time
│   ├── bell-theorem.md                # Loophole analysis
│   ├── collapse-problem.md            # Decoherence without collapse
│   └── quantum-summary.md
│
├── foundations/                       # Meta-level: Theory structure
│   ├── README.md                      # "Foundational Commitments"
│   ├── ontology.md                    # What exists (master reference)
│   ├── parameter-ledger.md            # A/B/C/D categories
│   ├── validation-protocols.md        # How we test claims
│   ├── no-go-theorems.md              # Bell, Coleman-Mandula, etc.
│   ├── theory-virtues.md              # Parsimony, depth, testability
│   ├── explanatory-scoreboard.md      # What we explain vs SM+GR
│   └── failure-criteria.md            # When would we pivot/halt?
│
├── simulations/                       # Computational implementation
│   ├── README.md                      # "Numerical Implementation"
│   ├── tier1-architrino.md            # Two-body, few-body validation
│   ├── tier2-binary.md                # Formation and stability
│   ├── tier3-tribinary.md             # Attractors and basins
│   ├── tier4-continuum.md             # Coarse-graining handoff
│   ├── convergence-tests.md           # Resolution, integrator, parameter sweeps
│   ├── run-protocols.md               # Reproducibility standards
│   ├── synthetic-observables.md       # Mock data generation
│   └── pdg-solver-ideas.md            # Future: PDE solver integration
│
├── experiments/                       # Empirical anchors (NEW)
│   ├── README.md                      # "Experimental Constraints and Tests"
│   ├── constraint-ledger.md           # Tier 1/2/3 bounds
│   ├── lorentz-tests.md               # Michelson-Morley, modern SME
│   ├── equivalence-principle.md       # Eötvös, LLR, MICROSCOPE
│   ├── charge-conservation.md         # Limits on charge violation
│   ├── proton-stability.md            # Super-K, Hyper-K bounds
│   ├── gw-tests.md                    # LIGO/Virgo speed, polarization
│   ├── cmb-observations.md            # Planck data
│   ├── bbn-abundances.md              # Light element measurements
│   ├── precision-qed.md               # g-2, α measurements
│   └── proposed-tests.md              # Killer experiments for our theory
│
├── philosophy-history/                # Context and interpretation
│   ├── README.md                      # "Intellectual Context"
│   ├── crisis-in-physics.md           # Why rethink foundations now
│   ├── historical-context.md          # Ether, pilot-wave, emergent gravity
│   ├── lorentz-ether.md               # Neo-Lorentzian relativity
│   ├── bohmian-mechanics.md           # Comparison to de Broglie-Bohm
│   ├── major-thinkers.md              # Intellectual influences
│   ├── theory-mapping.md              # How we relate to SM/GR/QFT
│   ├── open-questions.md              # Unknowns and paradoxes
│   └── future-vision.md               # Long-term research program
│
├── adversarial/                       # Red team materials
│   ├── README.md                      # "Critical Assessment"
│   ├── parameter-audit.md             # Count and naturalness (FTQ)
│   ├── stop-conditions.md             # When to pivot/halt
│   ├── theory-health.md               # Quarterly dashboard
│   └── known-tensions.md              # Where we're struggling
│
├── synthesis/                         # High-level integration (NEW)
│   ├── README.md                      # "Putting It All Together"
│   ├── unsolved-problems.md           # What we address (measurement, dark matter, etc.)
│   ├── empirical-scorecard.md         # Pass/fail summary across all domains
│   ├── integration-map.md             # How pieces fit together
│   └── research-roadmap.md            # Next 5-10 years
│
├── team/                              # Internal operations
│   ├── README.md
│   ├── team-charter.md
│   ├── roles/
│   │   ├── phil.md
│   │   ├── dyna.md
│   │   ├── phe.md
│   │   ├── alfa.md
│   │   ├── cos.md
│   │   ├── sol.md
│   │   ├── sig.md
│   │   └── red.md
│   ├── governance.md
│   ├── communication-standards.md
│   ├── mathematical-style-guide.md
│   └── quarterly-review-template.md
│
└── appendices/
    ├── glossary.md
    ├── notation.md
    ├── units-conventions.md
    ├── bibliography.md
    └── index.md
```

---
