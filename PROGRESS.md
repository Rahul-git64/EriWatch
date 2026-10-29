# EriWatch Progress Board

> Live status board tracking every stage and step of the EriWatch engineering roadmap.
> Master prompt: [`docs/MASTER_PROMPT.md`](docs/MASTER_PROMPT.md)

## Stage Summary

| Stage | Name | Status | Gate Report | Tag |
|---|---|---|---|---|
| 0 | Foundations and engineering scaffolding | `IN_PROGRESS` | `docs/reviews/stage-0.md` | - |
| 1 | Data discovery and feasibility spike | `PENDING` | `docs/reviews/stage-1.md` | - |
| 2 | Geospatial pipeline (water spread from satellites) | `PENDING` | `docs/reviews/stage-2.md` | - |
| 3 | Database and data model | `PENDING` | `docs/reviews/stage-3.md` | - |
| 4 | Exploratory data analysis and decision-focused analytics | `PENDING` | `docs/reviews/stage-4.md` | - |
| 5 | Machine learning, forecasting and risk | `PENDING` | `docs/reviews/stage-5.md` | - |
| 6 | Backend API | `PENDING` | `docs/reviews/stage-6.md` | - |
| 7 | Frontend | `PENDING` | `docs/reviews/stage-7.md` | - |
| 8 | Grounded LLM and RAG module | `PENDING` | `docs/reviews/stage-8.md` | - |
| 9 | n8n workflow automation | `PENDING` | `docs/reviews/stage-9.md` | - |
| 10 | Integration, hardening and evaluation | `PENDING` | `docs/reviews/stage-10.md` | - |
| 11 | Deployment | `PENDING` | `docs/reviews/stage-11.md` | - |
| 12 | Documentation, deliverables and viva readiness | `PENDING` | `docs/reviews/stage-12.md` | - |

---

## Stage 0: Foundations and engineering scaffolding

| Done | Step | Description | Status | Commit | Micro-Review |
|---|---|---|---|---|---|
| [x] | 0.1 | Initialise git, `.gitignore`, `README.md`, MIT licence | `DONE` | `5871c64` | [`docs/reviews/micro/0-1.md`](docs/reviews/micro/0-1.md) |
| [x] | 0.2 | Create repository layout with placeholder READMEs | `DONE` | `4e140fc` | [`docs/reviews/micro/0-2.md`](docs/reviews/micro/0-2.md) |
| [x] | 0.3 | Python tooling: `uv`, `ruff`, `mypy`, `pytest`, pre-commit hooks | `DONE` | `d4b62fe` | [`docs/reviews/micro/0-3.md`](docs/reviews/micro/0-3.md) |
| [x] | 0.4 | Web tooling: Next.js 14 TS app, ESLint, Prettier, Vitest, Playwright | `DONE` | `59ad706` | [`docs/reviews/micro/0-4.md`](docs/reviews/micro/0-4.md) |
| [x] | 0.5 | FastAPI skeleton with `/health`, structured JSON logging, Pydantic settings, 1 test | `DONE` | `b290f17` | [`docs/reviews/micro/0-5.md`](docs/reviews/micro/0-5.md) |
| [x] | 0.6 | `docker-compose.yml` with Postgres (PostGIS + pgvector), api, web, n8n + healthchecks | `DONE` | `88220a7` | [`docs/reviews/micro/0-6.md`](docs/reviews/micro/0-6.md) |
| [x] | 0.7 | `Makefile` targets: `setup`, `lint`, `test`, `run`, `db-up`, `db-reset` | `DONE` | `27f854f` | [`docs/reviews/micro/0-7.md`](docs/reviews/micro/0-7.md) |
| [x] | 0.8 | GitHub Actions CI: lint, type-check, tests for api and web on push | `DONE` | `b0b4779` | [`docs/reviews/micro/0-8.md`](docs/reviews/micro/0-8.md) |
| [ ] | 0.9 | ADR-0001 (stack and architecture), ADR-0002 (monorepo and branching) | `IN_PROGRESS` | - | `docs/reviews/micro/0-9.md` |
| [ ] | 0.10 | `PROGRESS.md` board finalize and review folder structure | `PENDING` | - | `docs/reviews/micro/0-10.md` |

---

## Stage 1: Data discovery and feasibility spike

| Done | Step | Description | Status | Commit | Micro-Review |
|---|---|---|---|---|---|
| [ ] | 1.1 | Spike external data sources and log in `docs/data/feasibility.md` | `PENDING` | - | `docs/reviews/micro/1-1.md` |
| [ ] | 1.2 | Decide pilot: 30-50 tanks near Chengalpattu/Kancheepuram with selection criteria | `PENDING` | - | `docs/reviews/micro/1-2.md` |
| [ ] | 1.3 | Build tank registry file (id, name, district, block, centroid, polygon, source, confidence) | `PENDING` | - | `docs/reviews/micro/1-3.md` |
| [ ] | 1.4 | Data dictionary (`docs/data/dictionary.md`) with units and licence | `PENDING` | - | `docs/reviews/micro/1-4.md` |
| [ ] | 1.5 | Licence and ethics note: public sources and attribution | `PENDING` | - | `docs/reviews/micro/1-5.md` |
| [ ] | 1.6 | Collect >=25 government/court order PDFs into `data/raw/legal/` with manifest | `PENDING` | - | `docs/reviews/micro/1-6.md` |

---

## Stage 2: Geospatial pipeline (water spread from satellites)

| Done | Step | Description | Status | Commit | Micro-Review |
|---|---|---|---|---|---|
| [ ] | 2.1 | STAC search client with retries, pagination, caching and typed responses | `PENDING` | - | `docs/reviews/micro/2-1.md` |
| [ ] | 2.2 | Tile and band loader (windowed reads clipped to tank polygon + buffer) | `PENDING` | - | `docs/reviews/micro/2-2.md` |
| [ ] | 2.3 | Cloud, shadow and snow masking using SCL; per-scene valid-pixel fraction | `PENDING` | - | `docs/reviews/micro/2-3.md` |
| [ ] | 2.4 | Water indices: NDWI and MNDWI; Otsu threshold selection + fallback comparison | `PENDING` | - | `docs/reviews/micro/2-4.md` |
| [ ] | 2.5 | Water-spread area (ha) per tank per date, with quality flags | `PENDING` | - | `docs/reviews/micro/2-5.md` |
| [ ] | 2.6 | Validation against JRC Global Surface Water and >=10 tank manual sample | `PENDING` | - | `docs/reviews/micro/2-6.md` |
| [ ] | 2.7 | Batch historical backfill (2019+) and incremental runner; idempotent & resumable | `PENDING` | - | `docs/reviews/micro/2-7.md` |
| [ ] | 2.8 | Persist results to Parquet cache and prepare DB loaders | `PENDING` | - | `docs/reviews/micro/2-8.md` |
| [ ] | 2.9 | Unit tests with fixture rasters + 1 live STAC integration test (`network`) | `PENDING` | - | `docs/reviews/micro/2-9.md` |
| [ ] | 2.10 | Module doc (`docs/modules/geo.md`) and notebook visualising one tank across seasons | `PENDING` | - | `docs/reviews/micro/2-10.md` |

---

## Stage 3: Database and data model

| Done | Step | Description | Status | Commit | Micro-Review |
|---|---|---|---|---|---|
| [ ] | 3.1 | Alembic setup; enable PostGIS and pgvector extensions | `PENDING` | - | `docs/reviews/micro/3-1.md` |
| [ ] | 3.2 | Core tables creation (users, roles, tanks, observations, rainfall, forecasts, etc.) | `PENDING` | - | `docs/reviews/micro/3-2.md` |
| [ ] | 3.3 | Indexes (GiST, composite, HNSW/IVFFlat), constraints and enums | `PENDING` | - | `docs/reviews/micro/3-3.md` |
| [ ] | 3.4 | Seed scripts loading tank registry and observations from Stage 2 | `PENDING` | - | `docs/reviews/micro/3-4.md` |
| [ ] | 3.5 | Repository layer with typed queries and tests against real Postgres container | `PENDING` | - | `docs/reviews/micro/3-5.md` |
| [ ] | 3.6 | Documented ERD in `docs/` (Mermaid) and migration up/down test | `PENDING` | - | `docs/reviews/micro/3-6.md` |

---

## Stage 4: Exploratory data analysis and decision-focused analytics

| Done | Step | Description | Status | Commit | Micro-Review |
|---|---|---|---|---|---|
| [ ] | 4.1 | Data quality report: gaps, cloud missingness, outliers, duplicates; cleaning rules | `PENDING` | - | `docs/reviews/micro/4-1.md` |
| [ ] | 4.2 | Seasonality and monsoon response: rainfall-to-spread lag per tank | `PENDING` | - | `docs/reviews/micro/4-2.md` |
| [ ] | 4.3 | Tank typology clustering into archetypes | `PENDING` | - | `docs/reviews/micro/4-3.md` |
| [ ] | 4.4 | Shrinkage analysis: current vs historical maximum extent per tank | `PENDING` | - | `docs/reviews/micro/4-4.md` |
| [ ] | 4.5 | District and block level comparison table and map-ready aggregates | `PENDING` | - | `docs/reviews/micro/4-5.md` |
| [ ] | 4.6 | Document decision supported by each analysis | `PENDING` | - | `docs/reviews/micro/4-6.md` |
| [ ] | 4.7 | Export analytics as API-ready materialised views or tables | `PENDING` | - | `docs/reviews/micro/4-7.md` |

---

## Stage 5: Machine learning, forecasting and risk

| Done | Step | Description | Status | Commit | Micro-Review |
|---|---|---|---|---|---|
| [ ] | 5.1 | Feature engineering (lags, rolling rainfall, seasonal, GW, typology, days since pass) | `PENDING` | - | `docs/reviews/micro/5-1.md` |
| [ ] | 5.2 | Evaluation protocol: time-based split, rolling-origin CV, MAE/RMSE/sMAPE & event metrics | `PENDING` | - | `docs/reviews/micro/5-2.md` |
| [ ] | 5.3 | Baselines: persistence, seasonal naive, linear model | `PENDING` | - | `docs/reviews/micro/5-3.md` |
| [ ] | 5.4 | Advanced models: LightGBM global + sequence model (LSTM/TCN) + calibrated intervals | `PENDING` | - | `docs/reviews/micro/5-4.md` |
| [ ] | 5.5 | Risk classifier (`likely dry`, `overflow risk`) with domain-justified thresholds | `PENDING` | - | `docs/reviews/micro/5-5.md` |
| [ ] | 5.6 | Explainability: SHAP for LightGBM and plain-language per-tank explanation | `PENDING` | - | `docs/reviews/micro/5-6.md` |
| [ ] | 5.7 | Encroachment and shrinkage detector using persistent-water masks + validation | `PENDING` | - | `docs/reviews/micro/5-7.md` |
| [ ] | 5.8 | Model registry with versioned artifacts, metadata and fallback loader | `PENDING` | - | `docs/reviews/micro/5-8.md` |
| [ ] | 5.9 | Batch inference job writing to `forecasts` and `risk_assessments` | `PENDING` | - | `docs/reviews/micro/5-9.md` |
| [ ] | 5.10 | Model card in `docs/modules/ml.md` | `PENDING` | - | `docs/reviews/micro/5-10.md` |

---

## Stage 6: Backend API

| Done | Step | Description | Status | Commit | Micro-Review |
|---|---|---|---|---|---|
| [ ] | 6.1 | Auth: registration, login, JWT access/refresh, argon2, RBAC roles | `PENDING` | - | `docs/reviews/micro/6-1.md` |
| [ ] | 6.2 | Tank endpoints: list with bbox, detail, observations, forecast, risk, encroachment | `PENDING` | - | `docs/reviews/micro/6-2.md` |
| [ ] | 6.3 | Analytics endpoints serving Stage 4 outputs | `PENDING` | - | `docs/reviews/micro/6-3.md` |
| [ ] | 6.4 | Complaint endpoints: create (text, language, photo validation), list own, status | `PENDING` | - | `docs/reviews/micro/6-4.md` |
| [ ] | 6.5 | Petition endpoints: generate draft, review, approve, reject, export PDF | `PENDING` | - | `docs/reviews/micro/6-5.md` |
| [ ] | 6.6 | Alert subscription endpoints and delivery log | `PENDING` | - | `docs/reviews/micro/6-6.md` |
| [ ] | 6.7 | Admin endpoints: user management, workflow runs, model versions, audit log | `PENDING` | - | `docs/reviews/micro/6-7.md` |
| [ ] | 6.8 | Cross-cutting: validation, error format, rate limiting, CORS, request IDs, DB audit log | `PENDING` | - | `docs/reviews/micro/6-8.md` |
| [ ] | 6.9 | OpenAPI documentation with examples exported to `docs/api/` | `PENDING` | - | `docs/reviews/micro/6-9.md` |
| [ ] | 6.10 | Unit, integration (>=80% coverage) and security tests | `PENDING` | - | `docs/reviews/micro/6-10.md` |

---

## Stage 7: Frontend

| Done | Step | Description | Status | Commit | Micro-Review |
|---|---|---|---|---|---|
| [ ] | 7.1 | Design system: typography, water/earth palette, themes, responsive, a11y target | `PENDING` | - | `docs/reviews/micro/7-1.md` |
| [ ] | 7.2 | Auth screens and role-aware navigation | `PENDING` | - | `docs/reviews/micro/7-2.md` |
| [ ] | 7.3 | Map home: all pilot tanks with risk colours, filters, clustering and legend | `PENDING` | - | `docs/reviews/micro/7-3.md` |
| [ ] | 7.4 | Tank detail: time series, forecast + interval, rainfall, before/after slider, risk, encroachment | `PENDING` | - | `docs/reviews/micro/7-4.md` |
| [ ] | 7.5 | Analytics dashboard: Stage 4 insights and decisions | `PENDING` | - | `docs/reviews/micro/7-5.md` |
| [ ] | 7.6 | Complaint flow: guided form, Tamil/English input, photo upload, live structured preview | `PENDING` | - | `docs/reviews/micro/7-6.md` |
| [ ] | 7.7 | Petition review screen: draft with inline citations, edit, approve/reject | `PENDING` | - | `docs/reviews/micro/7-7.md` |
| [ ] | 7.8 | Alerts & subscriptions page; admin console for workflows, models and audit log | `PENDING` | - | `docs/reviews/micro/7-8.md` |
| [ ] | 7.9 | Model and LLM performance dashboard | `PENDING` | - | `docs/reviews/micro/7-9.md` |
| [ ] | 7.10 | Loading/empty/error states, Tamil i18n, keyboard and screen-reader checks | `PENDING` | - | `docs/reviews/micro/7-10.md` |
| [ ] | 7.11 | Playwright E2E tests for the three core journeys | `PENDING` | - | `docs/reviews/micro/7-11.md` |

---

## Stage 8: Grounded LLM and RAG module

| Done | Step | Description | Status | Commit | Micro-Review |
|---|---|---|---|---|---|
| [ ] | 8.1 | Corpus ingestion: PDF extraction with OCR fallback, cleaning, section-aware chunking | `PENDING` | - | `docs/reviews/micro/8-1.md` |
| [ ] | 8.2 | Multilingual embeddings in pgvector; hybrid retrieval (vector + keyword) with reranking | `PENDING` | - | `docs/reviews/micro/8-2.md` |
| [ ] | 8.3 | Complaint structuring into strict Pydantic JSON schema + clarifying question trigger | `PENDING` | - | `docs/reviews/micro/8-3.md` |
| [ ] | 8.4 | Tank linking by name, location and geospatial proximity | `PENDING` | - | `docs/reviews/micro/8-4.md` |
| [ ] | 8.5 | Petition drafting with inline citations (doc, page, clause) validated against schema | `PENDING` | - | `docs/reviews/micro/8-5.md` |
| [ ] | 8.6 | Refusal and guardrails + prompt-injection defences | `PENDING` | - | `docs/reviews/micro/8-6.md` |
| [ ] | 8.7 | Human-in-the-loop approval flow and logging | `PENDING` | - | `docs/reviews/micro/8-7.md` |
| [ ] | 8.8 | Privacy controls: PII masking before external LLM calls + retention policy | `PENDING` | - | `docs/reviews/micro/8-8.md` |
| [ ] | 8.9 | Evaluation harness (>=50 test cases: Tamil, adversarial, out-of-scope) + JSON report | `PENDING` | - | `docs/reviews/micro/8-9.md` |
| [ ] | 8.10 | Model abstraction layer (Gemini Flash, Groq, local) with caching and cost controls | `PENDING` | - | `docs/reviews/micro/8-10.md` |

---

## Stage 9: n8n workflow automation

| Done | Step | Description | Status | Commit | Micro-Review |
|---|---|---|---|---|---|
| [ ] | 9.1 | Workflow A: weekly monitor (schedule, STAC fetch, spread, model, thresholds, branch) | `PENDING` | - | `docs/reviews/micro/9-1.md` |
| [ ] | 9.2 | Branch on breach: evidence report (map, chart, risk, explanation) + email/Telegram | `PENDING` | - | `docs/reviews/micro/9-2.md` |
| [ ] | 9.3 | Failure handling: cloudy fallback, exponential backoff retry, error workflow, DLQ | `PENDING` | - | `docs/reviews/micro/9-3.md` |
| [ ] | 9.4 | Workflow B: complaint intake webhook, structuring, linking, draft, routing, SLA nudges | `PENDING` | - | `docs/reviews/micro/9-4.md` |
| [ ] | 9.5 | Workflow C: scheduled rainfall and groundwater data refresh | `PENDING` | - | `docs/reviews/micro/9-5.md` |
| [ ] | 9.6 | Idempotency keys to prevent duplicate alerts | `PENDING` | - | `docs/reviews/micro/9-6.md` |
| [ ] | 9.7 | Execution logging to `workflow_runs` visible in admin console | `PENDING` | - | `docs/reviews/micro/9-7.md` |
| [ ] | 9.8 | Export workflow JSONs to `workflows/n8n/`, credential template, and runbook | `PENDING` | - | `docs/reviews/micro/9-8.md` |
| [ ] | 9.9 | Scenario tests: happy path, cloudy pass, API timeout, duplicate trigger, invalid payload | `PENDING` | - | `docs/reviews/micro/9-9.md` |

---

## Stage 10: Integration, hardening and evaluation

| Done | Step | Description | Status | Commit | Micro-Review |
|---|---|---|---|---|---|
| [ ] | 10.1 | Full end-to-end automated scenario script | `PENDING` | - | `docs/reviews/micro/10-1.md` |
| [ ] | 10.2 | Load and smoke tests (latency targets, GeoJSON size budgets) | `PENDING` | - | `docs/reviews/micro/10-2.md` |
| [ ] | 10.3 | Security review: dependency scan, secret scan, OWASP checklist, authz, rate limits | `PENDING` | - | `docs/reviews/micro/10-3.md` |
| [ ] | 10.4 | Observability: structured logs, health endpoints, uptime check, error tracking | `PENDING` | - | `docs/reviews/micro/10-4.md` |
| [ ] | 10.5 | Data and model monitoring: feature drift check and scheduled re-evaluation | `PENDING` | - | `docs/reviews/micro/10-5.md` |
| [ ] | 10.6 | Usability test protocol and capture for >=5 users | `PENDING` | - | `docs/reviews/micro/10-6.md` |
| [ ] | 10.7 | Consolidated evaluation report matching proposal testing table | `PENDING` | - | `docs/reviews/micro/10-7.md` |

---

## Stage 11: Deployment

| Done | Step | Description | Status | Commit | Micro-Review |
|---|---|---|---|---|---|
| [ ] | 11.1 | Production configs and secrets management for each platform | `PENDING` | - | `docs/reviews/micro/11-1.md` |
| [ ] | 11.2 | Database deployment config (Supabase/Neon with PostGIS & pgvector) + CI migrations | `PENDING` | - | `docs/reviews/micro/11-2.md` |
| [ ] | 11.3 | FastAPI + models deployment (HF Spaces Docker / Render) + cold-start tuning | `PENDING` | - | `docs/reviews/micro/11-3.md` |
| [ ] | 11.4 | Next.js deployment config for Vercel | `PENDING` | - | `docs/reviews/micro/11-4.md` |
| [ ] | 11.5 | n8n Docker deployment config (Render/Railway) with persistence | `PENDING` | - | `docs/reviews/micro/11-5.md` |
| [ ] | 11.6 | GitHub Actions scheduled job for weekly satellite processing | `PENDING` | - | `docs/reviews/micro/11-6.md` |
| [ ] | 11.7 | Live smoke test suite and rollback instructions | `PENDING` | - | `docs/reviews/micro/11-7.md` |
| [ ] | 11.8 | Seed script for live system with full pilot data and demo accounts per role | `PENDING` | - | `docs/reviews/micro/11-8.md` |
| [ ] | 11.9 | Uptime monitor and status section in README | `PENDING` | - | `docs/reviews/micro/11-9.md` |

---

## Stage 12: Documentation, deliverables and viva readiness

| Done | Step | Description | Status | Commit | Micro-Review |
|---|---|---|---|---|---|
| [ ] | 12.1 | Architecture diagram (Mermaid and exported image) | `PENDING` | - | `docs/reviews/micro/12-1.md` |
| [ ] | 12.2 | Complete API docs, data dictionary, ERD, workflow logs, test & eval reports | `PENDING` | - | `docs/reviews/micro/12-2.md` |
| [ ] | 12.3 | User manual with screenshots for each role | `PENDING` | - | `docs/reviews/micro/12-3.md` |
| [ ] | 12.4 | Final report and proposal aligned to SAI University template | `PENDING` | - | `docs/reviews/micro/12-4.md` |
| [ ] | 12.5 | Demo script (8-10 minutes) | `PENDING` | - | `docs/reviews/micro/12-5.md` |
| [ ] | 12.6 | Viva question bank (>=60 questions and answers) | `PENDING` | - | `docs/reviews/micro/12-6.md` |
| [ ] | 12.7 | Demo video recording script and offline fallback plan | `PENDING` | - | `docs/reviews/micro/12-7.md` |
| [ ] | 12.8 | Final repository polish: README, badges, contribution log, tag `v1.0.0` | `PENDING` | - | `docs/reviews/micro/12-8.md` |

---

## Tracked Risks & Deferred Items

| ID | Stage.Step | Description | Severity | Status |
|---|---|---|---|---|
| R-001 | 0.4 | Next.js 14.2.x transitive npm audit advisories; evaluate minor patch/overrides in Stage 6/10 security gate | Low | `OPEN` |
| R-002 | 0.6 | Docker Desktop engine daemon (`dockerDesktopLinuxEngine`) not started on host; verify daemon startup for compose `/health` check | Medium | `OPEN` |
