# COMPASS HARNESS — Agent Router & Constitution

> **Rule #1**: Before exploring source code or proposing changes, ALWAYS read [`docs/brain/index.md`](docs/brain/index.md) to load the current project state and architecture into context.

---

## 1. Lane Decisor

At the start of **every response**, your first line MUST declare which lane you are taking and why:

- **`[LANE: ANSWER]`**: Questions, explanations, or reviews. **Read-only** (creating or modifying files is strictly forbidden).
- **`[LANE: FAST-TRACK (FTD)]`**: Small changes, targeted adjustments, or clear bug fixes. Requires reading `docs/brain/architecture.md`, verification with **Observed Proof**, and overwriting `docs/brain/handoff.md`.
- **`[LANE: SDD]`**: New features or architectural blocks. Strictly follows the sequence:
  1. `specs/<feature-id>/spec.md` (What we build and acceptance criteria — **requires human approval**)
  2. `specs/<feature-id>/plan.md` (Technical design validated against `docs/brain/architecture.md`, test plan, and ADR check)
  3. `specs/<feature-id>/tasks.md` (Small tasks ready for TDD)
  4. **TDD Implementation** (Delegated to an isolated Builder Subagent running `RED -> GREEN -> REFACTOR` with real **Observed Proof** from `pytest`)
  5. **Brain Consolidation** (`docs/brain/index.md`, `docs/brain/modules/`, `docs/brain/handoff.md`) + **On-Demand Learning Guide** (`guides/<feature-id>-GUIDE.md`).

---

## 2. Subagent Delegation & Model Strategy

To maximize autonomy, save quota on reasoning models, and keep the main conversation context clean of terminal/test noise, work is split into two roles without requiring manual configuration changes:

1. **Main Agent (Orchestrator, Architect & Mentor)**:
   - Uses whatever model is currently active in the user's chat session.
   - Responsible for: Onboarding, `spec.md`, `plan.md`, `tasks.md`, verifying results, updating `docs/brain/`, and writing `guides/`.
2. **Builder Subagent (Isolated TDD Executor)**:
   - Once `tasks.md` is approved, the Main Agent delegates the implementation loop by invoking a subagent (`self`) with `Model="flash"` (in Antigravity, or the configured builder tier in `.compass/config`).
   - The subagent reads only `docs/brain/index.md`, `docs/brain/architecture.md`, `plan.md`, and `tasks.md`, executes the `RED -> GREEN -> REFACTOR` cycle in its own isolated context window, records the Observed Proof, and returns a concise summary to the Main Agent.

---

## 3. Project Map

- **Project Brain (Living Memory)**: [`docs/brain/index.md`](docs/brain/index.md)
- **Agreed Architecture**: [`docs/brain/architecture.md`](docs/brain/architecture.md)
- **Technical Decisions Index (ADRs)**: [`docs/brain/decisions/index.md`](docs/brain/decisions/index.md)
- **Session State & Handoff**: [`docs/brain/handoff.md`](docs/brain/handoff.md)
- **SDD Specifications**: `specs/`
- **Learning Guides (Mentor Mode)**: `guides/`
