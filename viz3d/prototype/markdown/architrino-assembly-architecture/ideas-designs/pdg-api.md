# PDG Python API (pdg package)

## Purpose
Document how we plan to use the official PDG Python API to access Particle Data Group resources in code. This is the preferred path for programmatic access to PDG data in this repo.

## Scope
- In scope: the PDG Python package `pdg` and its local database workflow.
- Out of scope: the PDG REST API (we are not documenting endpoints or JSON access here).

## Key facts (from PDG docs)
- The `pdg` package provides a high-level API to PDG data and is the recommended programmatic interface for most users.
- The package ships with a PDG SQLite database file and works offline after installation.
- When a new edition of the Review of Particle Physics is released, a new `pdg` package version ships with the updated database.
- Additional PDG database files can be downloaded and used by pointing the API at a different database URL.
- The Python API uses SQLAlchemy; in principle the tables can be hosted in any SQLAlchemy-supported database backend.
- Requirements include Python 3 and SQLAlchemy >= 1.4 (see PDG docs for any legacy support notes).
- The PDG data in the Review of Particle Physics is licensed by PDG (CC BY 4.0 for recent editions); the `pdg` package code is open source under a BSD-style license.

## Documentation
- Python API docs: https://pdgapi.lbl.gov/doc/pythonapi.html
- PDG API general docs: https://pdgapi.lbl.gov/doc/
- PDG database file (schema and download context): https://pdgapi.lbl.gov/doc/schema.html

## Installation
Use standard Python tooling:

```bash
python -m pip install pdg
```

We should install in a virtual environment and pin the package version for reproducibility.

## Connection pattern
Use the package entrypoint and the bundled SQLite database by default:

```python
import pdg

api = pdg.connect()
schema_version = api.info("schema_version")
```

To use a different PDG database file, pass a database URL (downloaded from the PDG website):

```python
api = pdg.connect("sqlite:///pdgall-2025-v0.2.2.sqlite")  # example filename; see PDG API page for current files
```

The `pedantic` flag can be used to enable stricter validation behavior; use it for tests or debug runs if needed.

## Example calls and returned data
The examples below mirror PDG's documented usage. Outputs vary by edition; values shown are representative.

### 1) Connect and inspect the database
```python
import pdg
api = pdg.connect()
print(api.edition)                 # e.g. "2025" (edition-dependent)
print(api.info("schema_version"))  # schema version as a string
```
Example output (edition-specific):
```
<edition>
<schema_version>
```

### 2) Get a particle and simple properties
```python
pi_minus = api.get_particle_by_name("pi-")
print(pi_minus.mcid)       # Monte Carlo particle number (int)
print(pi_minus.mass)       # mass in GeV (float, unrounded)
print(pi_minus.quantum_J)  # spin J (quantum number)
```
Example output (edition-specific):
```
-211
<mass_in_GeV>
<J>
```

### 3) Get all charge states for a PDG identifier
```python
charged_pions = api.get("S008")
print([p.name for p in charged_pions])
```
Expected output:
```
['pi+', 'pi-']
```

### 4) Iterate properties (example)
```python
for p in api.get_particle_by_mcid(211).properties():
    print(p.pdgid, p.description, p.display_value_text)
```
Returned data are per-property objects with identifiers, descriptions, and display-ready values (one per row), for example:
```
S008M  mass (pi+-)  <value +/- error>
```

## Detailed example: list decay modes, products, and probabilities
Below is a narrated example using a particle with multiple exclusive decay modes (the charged pion). The same pattern works for any particle with branching fractions.

### Step 1: connect and select the particle
```python
import pdg
api = pdg.connect()
pi_plus = api.get_particle_by_name("pi+")
```

### Step 2: iterate decay modes and build product lists
Each exclusive decay is a `PdgBranchingFraction`. The `decay_products` list contains `PdgDecayProduct` entries, each with:
- `item`: a `PdgItem` (may be a specific particle or a generic particle class),
- `multiplier`: how many of that item appear in the decay,
- `subdecay`: optional nested decay requirement.

```python
def format_products(decay):
    parts = []
    for dp in decay.decay_products:
        name = dp.item.name
        mult = dp.multiplier
        parts.append(name if mult == 1 else f"{mult}*{name}")
    return " + ".join(parts)

for decay in pi_plus.exclusive_branching_fractions():
    products = format_products(decay)
    prob = decay.display_value_text  # formatted value with uncertainties/limits
    print(decay.description)
    print(f"  products: {products}")
    print(f"  branching: {prob} (limit={decay.is_limit})")
```

### Example output (truncated; edition-specific)
```
pi+ --> mu+ nu_mu
  products: mu+ + nu_mu
  branching: <value +/- error> (limit=False)
<other decay modes omitted>
```

### Notes
- Some products are generic (e.g., "K", "l") rather than a fixed charge state. The `PdgItem` tells you what the term means, and may resolve to more than one particle.
- If you need a structured tree of subdecays, use `decay.subdecays()` to inspect nested modes and their conventions as recorded in the Listings.

## Data versioning and reproducibility
- Pin the `pdg` package version in requirements.
- Record the PDG schema version from `api.info("schema_version")` in any derived datasets.
- Store the database file path in experiment metadata for traceability.

## Caching and offline use
- The Python API is designed for local access and works without network after install.
- Prefer local DB access for bulk or repeated queries.

## Testing guidance
- Unit tests should avoid network access and rely on a pinned `pdg` version.
- Add a small smoke test that opens the default database and reads `schema_version`.

## Open items
- Decide whether to mirror PDG SQLite database files in repo artifacts or rely on pinned `pdg` package versions.
- Define a small wrapper module for the most common PDG queries used by our pipelines.
- Add a short note on where we store downloaded PDG database files for reproducible runs.

## Implementation notes (recommended deployment pattern)
- Do not commit the full PDG SQLite database to git; it is large, changes by edition, and bloats clones.
- Pin a PDG edition and store the edition string and schema version in config/metadata for reproducibility.
- Host the SQLite database on the backend server (not in the GitHub Pages frontend) and expose a thin API or precomputed JSON artifacts for the webapp.
- If you need to distribute the database file, prefer GitHub Releases or LFS rather than normal git history.
- Review PDG redistribution terms and include attribution if you publish derived datasets or APIs.
