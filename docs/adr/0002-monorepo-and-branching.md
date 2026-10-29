# ADR-0002: Monorepo Layout, Branching Strategy, and Stage-Gated Review Protocol

- **Status:** Accepted
- **Date:** 2026-10-29
- **Stage:** Stage 0

## Context

EriWatch spans five tightly coupled domains: satellite image processing (`geo`), hydrological forecasting (`ml`), grounded legal RAG (`rag`), backend APIs (`api`), web UI (`web`), and workflow automation (`n8n`). Keeping these in separate repositories would cause version skew across shared schemas (e.g., observation flags, complaint schemas, petition citations) and make reproducible grading difficult.

## Decision

1. **Monorepo Structure:**
   - All applications (`apps/api`, `apps/web`), domain packages (`packages/geo`, `packages/ml`, `packages/rag`), automation (`workflows/n8n`), infrastructure (`infra/docker`, `infra/github`), and documentation (`docs/`) live in a single repository.
   - Python packages share a single root `uv` workspace (`pyproject.toml` + `uv.lock`) so `eriwatch-api` can import `eriwatch-geo`, `eriwatch-ml`, and `eriwatch-rag` directly with editable workspace resolution and unified linting/type-checking.
2. **Trunk-Based Workflow with Small Atomic Commits:**
   - Development proceeds on `main` (or short-lived feature branches merged without squashing) using **one logical change per commit**.
   - Every commit follows **Conventional Commits** (`feat(scope): ...`, `fix(scope): ...`, `chore(scope): ...`, `docs(scope): ...`, `test(scope): ...`, `ci(scope): ...`).
   - Every commit is immediately followed by a micro-review in `docs/reviews/micro/<stage>-<step>.md` and recorded in `PROGRESS.md`.
3. **Stage-Gated Delivery:**
   - At the end of each stage `N`, a comprehensive gate report is written to `docs/reviews/stage-<N>.md`, the repository is tagged `stage-<N>-pass` once all exit criteria pass, and execution pauses until the user replies `APPROVED STAGE N`.

## Alternatives Considered

1. **Polyrepo (Separate Repos for Web, API, ML, Geo):**
   - *Rejected:* Breaks atomic cross-stack changes, requires publishing internal wheels, and complicates `make setup && make test && make run`.
2. **Large Mega-Commits per Stage:**
   - *Rejected:* Hides regressions, makes `git bisect` impossible, and violates Non-Negotiable Rule #1 and #2.

## Consequences

- **Positive:** Full traceability from every rubric item to a specific commit hash, micro-review, and stage gate report; a single `Makefile` drives setup, linting, testing, and Docker orchestration.
- **Negative / Risks:** Discipline is required to keep commits small and ensure `PROGRESS.md` and `docs/reviews/micro/` stay synchronized at every step.
