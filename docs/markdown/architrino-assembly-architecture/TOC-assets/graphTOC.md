# Phil's Integrated TOC & File Structure: Network-Aware Design

## Executive Summary

Given that the web app supports **network navigation** (not just linear hierarchy), we can design a structure that serves **three modes simultaneously**:

1. **Linear (Textbook)**: Pedagogical reading order for newcomers
2. **Hierarchical (Concept Tree)**: Top-down conceptual navigation
3. **Network (Graph)**: Free exploration of interconnected ideas

The key insight: **Files are nodes, directories are conceptual clusters, and explicit metadata creates the edges.**

---

## Core Design Principles

### Files as Network Nodes
- Each markdown file is a **semantic unit** (concept, mechanism, test, or claim)
- Files contain metadata for network navigation
  - **Concept level** (foundational / architectural / phenomenological / applied)
  - **Dependencies** (what must be understood first)
  - **Related concepts** (lateral connections)
  - **Empirical anchors** (which experiments/observations constrain this)

### Directories as Conceptual Neighborhoods
- Directories group **thematically related nodes**
- Not strict hierarchy—files can link across directories freely
- Directory structure optimizes **discovery** ("I'm interested in cosmology—where do I start?")

### Multiple Navigation Paths
- **Linear path** (textbook TOC): Defined in `TOC.md` as ordered list
- **Hierarchical path** (concept tree): Defined by frontmatter `level` and `parent` fields
- **Network path** (graph): Defined by frontmatter `related` and `dependencies` fields


---

## Directory Structure (Network-Optimized)

```
architrino-assembly-architecture/
├── README.md                          # Landing page: navigation guide
see the latest directory....