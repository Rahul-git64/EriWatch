# Stage Gate Report: Stage 0 — Foundations and Engineering Scaffolding

- **Date:** 2026-10-29
- **Verdict:** `NOT PASSED` (3 of 4 exit criteria `PASS`; 1 blocked on host OS administrator action to start `com.docker.service` / Docker Desktop)

## 1. Phase Goal & Exit Criteria

**Goal:** A clean, reproducible, CI-backed monorepo with the full local stack running empty.

**Exit Criteria:**
- [x] Clean clone runs `make setup && make test` successfully
- [ ] `make run` and `/health` reachable through Docker Compose
- [x] CI configuration valid and all CI steps (`ruff`, `mypy`, `pytest`, `eslint`, `tsc`, `prettier`, `vitest`) green
- [x] All ADRs (`ADR-0001`, `ADR-0002`, `0000-template`) and review templates (`micro-review-template.md`, `stage-gate-template.md`) present

## 2. Scorecard

| Exit Criterion | Status (`PASS`/`FAIL`) | Evidence (Command, Output Path, Commit Hash) |
|---|---|---|
| Clean clone runs `make setup && make test` | `PASS` | `make lint && make test` passed (`ruff`, `mypy` on 7 files, `pytest` 5 passed in 2.01s, `next lint`, `tsc --noEmit`, `prettier --check`, `vitest` 1 passed); commit [`27f854f`](../../Makefile) |
| `make run` & `/health` reachable through compose | `FAIL` (Host daemon stopped) | `docker compose -f docker-compose.yml config --services` validated (`db`, `api`, `web`, `n8n`, commit [`88220a7`](../../infra/docker/docker-compose.yml)), and `uv run pytest` verified `/health` returns `200 OK` (`{"status":"ok","service":"EriWatch API"}`), but Windows service `com.docker.service` is `Stopped` and requires Administrator privileges (`net start com.docker.service` or launching Docker Desktop from Windows) before `make run` can start containers |
| CI green | `PASS` | [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) validated via PyYAML and every CI step executed and passed locally (`b0b4779`) |
| All ADRs and templates present | `PASS` | [`docs/adr/0000-template.md`](../adr/0000-template.md), [`docs/adr/0001-stack-and-architecture.md`](../adr/0001-stack-and-architecture.md), [`docs/adr/0002-monorepo-and-branching.md`](../adr/0002-monorepo-and-branching.md) (`573ccc7`), [`docs/reviews/templates/micro-review-template.md`](templates/micro-review-template.md), [`docs/reviews/templates/stage-gate-template.md`](templates/stage-gate-template.md) (`c79d01f`) |

## 3. Path Check

- **Downstream readiness:** The monorepo structure (`apps/api`, `apps/web`, `packages/geo`, `packages/ml`, `packages/rag`, `workflows/n8n`, `infra/docker`, `infra/github`, `data/`, `notebooks/`, `docs/`) is complete and locked (`uv.lock` + `apps/web/package-lock.json`).
- **What would break downstream if we continue as is:** Stage 1 (`Data discovery and feasibility spike`) and Stage 2 (`Geospatial pipeline`) do not depend on the local Postgres container, but Stage 3 (`Database and data model`) requires the `db` container (`PostGIS + pgvector`) running via Docker Compose. Starting Docker Desktop now resolves this completely.

## 4. Quality Metrics

- **Python Lint & Type-Check:** `uv run ruff check .` (`All checks passed!`), `uv run mypy apps/api/src packages/geo/src packages/ml/src packages/rag/src` (`Success: no issues found in 7 source files`)
- **Python Unit Tests:** `5 passed in 1.46s` (`apps/api/tests/test_health.py`, `packages/geo/tests/test_smoke.py`, `packages/ml/tests/test_smoke.py`, `packages/rag/tests/test_smoke.py`), 0 warnings
- **Web Lint, Types & Formatting:** `next lint` (`✔ No ESLint warnings or errors`), `tsc --noEmit` (0 errors), `prettier --check` (`All matched files use Prettier code style!`)
- **Web Unit Tests:** `vitest run` (`1 passed (1)` in `src/__tests__/page.test.tsx`)
- **Micro-Reviews Completed:** 10 / 10 (`docs/reviews/micro/0-1.md` through `docs/reviews/micro/0-10.md`)

## 5. Debt & Risks

| ID | Description | Severity | Remediation Plan |
|---|---|---|---|
| R-001 | Next.js 14.2.x transitive npm audit advisories | Low | Address in Stage 6/10 dependency security hardening |
| R-002 | Windows `com.docker.service` is stopped and non-elevated shell cannot start it | High (Blocks Gate 0) | User starts Docker Desktop (or runs `Start-Service com.docker.service` in an elevated PowerShell), then we run `make run` and `curl http://localhost:8000/health` to flip Gate 0 to `PASS` and tag `stage-0-pass` |

## 6. Demo Script

1. Run `make setup` to verify Python workspace (`uv sync`) and Next.js (`npm install`) dependencies are in sync.
2. Run `make lint` to run Ruff, Mypy (strict), ESLint, TypeScript (`tsc --noEmit`), and Prettier across all packages.
3. Run `make test` to execute Pytest (5 tests across `api`, `geo`, `ml`, `rag`) and Vitest (`apps/web`).
4. Start Docker Desktop on Windows, then run `make run` and `curl http://localhost:8000/health` to verify the live container stack.

## 7. Verdict

`NOT PASSED` — Honest report per Rule #5 & #6: all code, tests, linters, ADRs, and Dockerfiles are complete and committed, but `com.docker.service` is stopped on the host OS and cannot be started from a non-elevated shell. Once Docker Desktop is started and `make run` + `/health` are verified, this gate will be re-run and tagged `stage-0-pass`.
