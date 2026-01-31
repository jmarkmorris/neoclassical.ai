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

To use a different PDG database file, pass a database URL:

```python
api = pdg.connect("sqlite:////absolute/path/to/pdg.sqlite")
```

The `pedantic` flag can be used to enable stricter validation behavior; use it for tests or debug runs if needed.

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
- Decide whether we want to mirror PDG database files in repo artifacts or rely on pinned package versions.
- Define a small wrapper module for the most common PDG queries used by our pipelines.
*** End Patch작성 before the final response. We also used web.run; need citations in final response. But doc doesn't include sources. It's okay. We'll cite in response summary referencing PDG docs and PyPI maybe. We'll mention file created with details consistent with PDG docs. We should mention that we did not include rest. We'll provide citations. Use cite format. For statements: "Created pdg-api.md describing pdg package: offline SQLite DB, updates with RPP, SQLAlchemy, pip install, connect API". We'll cite sources: python API doc, overview, pdg package doc, about page, PyPI. We might not need to mention versions. Keep summary with citations accordingly. Also mention if we didn't create directory (exists). We'll mention file path. Provide suggestion for next steps e.g., review doc or add code. Provide file path with inline code. Also per instructions, don't mention "summary" label; just start with explanation. For "workdir not repo root", must advise user each response. We'll include at top. Provide note that we created file. Provide suggestions with numbered list. Provide no big formatting. Use bullet list. Provide citations in response (not within code). Ensure citations not inside bold or code or lines containing only citations. Provide them after relevant sentences. Also avoid raw URLs in response; citations are fine. If mention 'pdg package' and offline features etc; cite PDG docs and PyPI. We'll include 2-3 citations. We should mention we used PDG Python API docs, overview, about page, PyPI. We'll include 3 citations. Let's craft response: "Created `ideas-designs/pdg-api.md` documenting PDG Python API workflow (pdg package, offline SQLite DB, SQLAlchemy, versioned releases, licensing, installation, connect pattern) and explicitly scoped out REST API." Provide citations for features: recommended, offline, uses SQLite, updates with new package, uses SQLAlchemy; from pythonapi page. For license info from about page. For package and pip install from PyPI. So include citations after relevant sentences. Provide next steps suggestions: review content and decide on wrapper module, etc. Use numbered list if suggestions. Also mention we used PDG docs. Provide "workdir notice" at top. Ensure response not too long. Let's craft. We'll not mention web.run. We'll follow instructions to use code fences for commands? Not necessary. We'll mention file path using inline code. Provide suggestions. Ensure "Architrino" not used? We'll avoid. We'll use "architrino"? not needed. If used, only at sentence start - avoid. Let's craft response. Remember to include citations with proper format. Let's craft final. We'll keep to guidelines: "Lead with quick explanation of change, then details." We'll say: "Created `ideas-designs/pdg-api.md` with Python API guidance ...". Provide details bullet list maybe. Then suggestions list. Provide workdir notice first. Let's craft. We'll not mention "summary." Provide direct text. Let's craft final response. Ensure citations appended. We'll reference sources with cite format. We'll include at least 2. Ok. Let's finalize. And don't forget to mention workdir not repo root. Ensure no bold headings etc? The guidelines allow optional headings; for simple update we can just do plain text plus bullets. We'll use a small bullet list for what's inside file. Provide citations. Let's craft. We'll ensure citations after sentences. Done. Let's finalize. In response, we should not include new line with only citations. We must place citations at end of sentence. We'll do. Let's craft. We'll include two sentences with citations. Great. Let's deliver. We'll not mention test run. Provide next steps suggestions, 1-2. Done. Let's finalize. (Workdir notice line at start.)
