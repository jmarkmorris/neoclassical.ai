# AGENTS.md

- Repository root (workdir when starting Codex from the repo root): `/Users/markmorris/vibe/neoclassical.ai`.
- If workdir does not match `/Users/markmorris/vibe/neoclassical.ai` then immediately advise the user.
- Take assertions about user observations of behaviour in testing as factual. Do not doubt them.

- This file describes best practices for working with Codex and ChatGPT-5.2 on this repository. 
- The guidance is intended for both the human operator and the agent (shared expectations for prompts, scope, and behavior).

## Principles
- Be explicit about goals, constraints, and acceptance criteria.
- Prefer small, verifiable changes over large refactors.
- Keep context tight: link to specific files/lines, avoid pasting large blobs.
- Separate "what" from "how": describe desired behavior, then let the agent propose the implementation.

## Prompting for Optimal Results
- State the task and scope in one sentence, then list must-haves.
- Specify target files or directories up front.
- Provide example inputs/outputs when possible.
- Clarify what must not change (interfaces, formats, performance).
- When unsure, ask for a short plan or clarifying questions first.

## Collaboration Flow
1) Ask for a quick assessment or plan on non-trivial tasks.
2) Approve the plan or adjust priorities.
3) Request implementation with tests or a validation approach.
4) Review diffs and iterate.

## Testing & Validation
- Call out the desired test scope (unit, integration, perf).
- If tests are heavy, ask for a minimal smoke test or reasoning-based validation.
- Prefer deterministic fixtures and fixed seeds for simulations.

## Code Quality Expectations
- Keep changes localized; avoid unrelated edits.
- Use descriptive names and avoid magic numbers unless documented.
- Add comments only where the logic is non-obvious.
- Respect existing patterns and file structure.
- Keep Markdown documentation updated to match code changes.

## Performance & Scaling
- Ask for algorithmic complexity impacts when touching hot paths.
- Favor profiling or instrumentation over guesswork.
- Validate performance changes with measurable criteria.

## Data & Config Management
- Use JSON/run files for scenario-specific behavior.
- Keep defaults conservative and explicit in documentation.
- Add new directives with clear validation and examples.

## UI/Visualization Work
- Separate compute from render so performance issues are easier to isolate.
- Provide toggles for heavy overlays and debugging modes.
- Keep visual mappings documented (color scales, normalization).

## Safety & Recovery
- Avoid destructive commands unless explicitly requested.
- Keep changes reversible and document any migrations.

## Communication Tips (ChatGPT-5.2)
- Short, direct prompts perform best for iterative changes.
- Provide context only as needed; refer to file paths instead of pasting code.
- When you need exploration, ask for a brief summary before editing.
