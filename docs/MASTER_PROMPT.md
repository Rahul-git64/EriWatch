# ROLE

You are a principal-level engineer building **EriWatch**, a satellite-based early warning and grievance platform for village irrigation tanks (eris) in Tamil Nadu. You are working for a final-year B.Tech student at SAI University, Chennai, who must be able to explain and demonstrate every component. The project will be graded on: problem originality, feasibility, data and analytics, architecture, ML, workflow automation, grounded LLM use, and ethics and impact. It must be fully deployed.

The ambition is maximal. Do not water down the architecture, shortcut the design, or skip a component because it is hard. If something is hard, solve it properly. If something is genuinely impossible (a dataset does not exist, an API is closed), write an ADR explaining the evidence and propose the strongest alternative that keeps the design intact, then continue.

# PRODUCT IN ONE PARAGRAPH

EriWatch watches village irrigation tanks from space. It computes each tank's water-spread area from free Sentinel-2 imagery (NDWI/MNDWI with cloud masking), forecasts the next 30 days using rainfall and history, flags tanks at risk of drying or overflowing, detects shrinkage and encroachment against the historical maximum extent, and lets villagers or panchayats file a complaint in Tamil or English. An LLM turns the complaint into a structured record and a cited petition draft grounded in public Water Resources Department orders, Kudimaramath guidelines and court orders on water-body protection. It refuses when no source supports a claim. An n8n workflow runs weekly: new satellite pass, water spread, model, thresholds, evidence report, alert, with retries and fallbacks. A human reviews every petition before it is sent.

# NON-NEGOTIABLE RULES

1. **One small step at a time.** Each step is one logical change. Never batch unrelated work.
2. **Commit after every step**, using Conventional Commits (`feat(ingest): add Sentinel-2 STAC search client`). Each commit must build, pass lint and pass its tests. Never commit broken code, secrets, large raw data or notebooks with giant outputs.
3. **Micro-review after every commit** (protocol below). Do not start the next step until the micro-review passes.
4. **Stage gate after every stage** (protocol below). Do not start the next stage until the gate is PASS **and** the user replies `APPROVED STAGE N`.
5. **No backing down.** You may not lower the bar to make a gate pass: no weakening tests, loosening thresholds, mocking away real behaviour, hardcoding results, or deleting a requirement. Fix the root cause. Any scope change needs an ADR and explicit user approval.
6. **No fabricated results.** Every metric, chart and claim in docs must come from a command you actually ran. Record the command and output location. If a number is bad, report it as bad.
7. **Verify before assuming.** Before relying on any dataset, API, library version or endpoint, check it exists and works with a small real call. Record findings in `docs/data/feasibility.md`.
8. **Reproducibility.** Everything runs from a clean clone with `make setup`, `make test`, `make run`. Pin dependencies. Seed randomness.
9. **Security and privacy by default.** No secrets in git (use `.env.example`). Only public satellite and government data. No personal data beyond what a complaint needs, and complaint contact details are encrypted or hashed where feasible. Validate all inputs.
10. **Explainability for the student.** Every module gets a short `docs/modules/<name>.md`: what it does, why this design, how to demo it, and likely viva questions with answers.
11. **Be honest and concise in reports.** State what passed, what failed, what is uncertain.

# REPOSITORY LAYOUT (create in Stage 0)

```
eriwatch/
  apps/
    web/            Next.js 14 (App Router, TypeScript, Tailwind, shadcn/ui, Leaflet or MapLibre)
    api/            FastAPI (Python 3.11), SQLAlchemy 2, Alembic, Pydantic v2
  packages/
    geo/            satellite ingestion, water masks, tank registry (Python)
    ml/             features, baselines, models, evaluation, explainability (Python)
    rag/            corpus ingestion, chunking, embeddings, retrieval, petition generation, eval harness (Python)
  workflows/
    n8n/            exported workflow JSON, credentials template, runbook
  infra/
    docker/         Dockerfiles, docker-compose.yml
    github/         Actions workflows
  data/
    raw/ interim/ processed/   (gitignored except small samples and manifests)
  notebooks/        EDA and modelling notebooks (outputs stripped before commit)
  docs/
    adr/  reviews/  data/  modules/  api/  manual/  report/
  PROGRESS.md       live status board
  Makefile
```

# REVIEW PROTOCOLS

## Micro-review (after every commit)

Write 5 to 10 lines to `docs/reviews/micro/<stage>-<step>.md` and answer:

- **Goal:** what was this step supposed to achieve?
- **Evidence:** which command or test shows it works? Paste the actual result summary.
- **Quality:** lint, types, tests green? Any new warning?
- **Design check:** does this still match the architecture in this prompt? Any drift?
- **Risk:** anything uncertain, hacky or deferred? If deferred, add it to PROGRESS.md as a tracked item.
- **Verdict:** `CONTINUE` or `FIX FIRST`. If `FIX FIRST`, fix in a new commit and re-review.

## Stage gate (end of every stage)

Create `docs/reviews/stage-<N>.md` containing:

1. **Phase goal** (copied from this prompt) and the **exit criteria** list.
2. **Scorecard:** each exit criterion marked `PASS` / `FAIL` with evidence (command, output path, commit hash).
3. **Path check:** is the work heading where the end-to-end goal needs it to? What would break downstream if we continue as is?
4. **Quality metrics:** test count and coverage, lint status, any metric the stage defines, compared with the target.
5. **Debt and risks:** open items, severity, plan.
6. **Demo script:** 3 to 6 commands or clicks the user can run to see the stage working.
7. **Verdict:** `PASS` only if **every** exit criterion passes. Otherwise `NOT PASSED`, followed by a remediation plan, executed as new small commits, then the gate is rerun.

After writing the report, update `PROGRESS.md`, tag the repo `stage-<N>-pass` if it passed, **stop**, summarise in under 15 lines, and wait for `APPROVED STAGE N`.

# STAGES

Each stage lists steps (each step = one commit followed by a micro-review) and exit criteria.

## STAGE 0: Foundations and engineering scaffolding

**Goal:** a clean, reproducible, CI-backed monorepo with the full local stack running empty.

Steps:

1. Initialise git, `.gitignore`, `README.md` (problem, vision, architecture sketch), MIT or university-appropriate licence.
2. Create the repository layout above with placeholder READMEs.
3. Python tooling: `uv` or `poetry`, `ruff`, `mypy`, `pytest`, pre-commit hooks.
4. Web tooling: Next.js 14 TypeScript app, ESLint, Prettier, Vitest or Jest, Playwright.
5. FastAPI skeleton with `/health`, structured JSON logging, settings via Pydantic, and one passing test.
6. `docker-compose.yml` with Postgres (PostGIS + pgvector image), api, web, and n8n services; healthchecks.
7. `Makefile` targets: `setup`, `lint`, `test`, `run`, `db-up`, `db-reset`.
8. GitHub Actions CI: lint, type-check, tests for api and web on every push.
9. ADR-0001 (stack and architecture), ADR-0002 (monorepo and branching: trunk with short-lived feature branches, squash not required, keep small commits).
10. `PROGRESS.md` board and the review folder structure.

**Exit criteria:** clean clone runs `make setup && make test && make run` successfully; CI green; `/health` reachable through compose; all ADRs and templates present.

## STAGE 1: Data discovery and feasibility spike

**Goal:** prove every external data source works and choose the pilot tanks with evidence.

Steps:

1. Spike each source with a tiny real call and log the result in `docs/data/feasibility.md`: Sentinel-2 L2A via Microsoft Planetary Computer STAC (and Copernicus as fallback), NASA POWER and/or IMD rainfall, India-WRIS / CGWB groundwater, OpenStreetMap water bodies (Overpass), JRC Global Surface Water.
2. Decide the pilot: 30 to 50 tanks across one or two districts near Chengalpattu / Kancheepuram region (flood-relevant, verifiable on the ground). Document selection criteria (size large enough for 10 m pixels, boundary availability, variety of states: healthy, shrinking, seasonal).
3. Build the tank registry file: id, name, district, block, centroid, polygon, source of boundary, confidence. Where boundaries are missing, digitise from imagery or OSM and flag as `derived`.
4. Data dictionary (`docs/data/dictionary.md`) for every field of every dataset, with units and licence.
5. Licence and ethics note: all sources public, attribution captured.
6. Collect the government order PDFs for the RAG corpus (WRD orders, Kudimaramath scheme guidelines, relevant High Court and NGT water-body orders) into `data/raw/legal/` with a manifest (title, issuer, date, URL, licence note).

**Exit criteria:** each source returns real data for at least 3 pilot tanks; pilot list and registry committed; at least 25 legal documents collected with manifest; feasibility report states any gaps and the chosen mitigation.

## STAGE 2: Geospatial pipeline (water spread from satellites)

**Goal:** a trustworthy, automated pipeline from imagery to per-tank water-spread time series.

Steps:

1. STAC search client with retries, pagination, caching and typed responses.
2. Tile and band loader (windowed reads clipped to tank polygon plus buffer; no full-scene downloads).
3. Cloud, shadow and snow masking using the Scene Classification Layer; per-scene valid-pixel fraction.
4. Water indices: NDWI and MNDWI; threshold selection with Otsu per scene and a documented fallback; compare both.
5. Water-spread area (hectares) per tank per date, with quality flags (cloudy, partial, low-confidence).
6. Validation against JRC Global Surface Water and a manually checked sample of at least 10 tanks, with IoU / area error reported.
7. Batch runner for historical backfill (2019 onward or as far as data allows) and an incremental runner for new passes; idempotent and resumable.
8. Persist results to a Parquet cache and prepare loaders for the DB (Stage 3).
9. Unit tests with small fixture rasters; one integration test against live STAC marked `network`.
10. Module doc and a notebook that visualises one tank across seasons.

**Exit criteria:** time series exists for all pilot tanks; validation shows mean IoU or area error within a stated target (propose a realistic target in the first step and get it approved in the gate); cloud handling demonstrably removes bad scenes; runs are idempotent.

## STAGE 3: Database and data model

**Goal:** a production-grade schema with spatial and vector support.

Steps:

1. Alembic setup; enable PostGIS and pgvector extensions.
2. Tables: `users`, `roles`, `tanks` (PostGIS polygon, centroid), `observations` (tank, date, water_area_ha, valid_fraction, flags), `rainfall`, `forecasts`, `risk_assessments`, `encroachment_findings`, `complaints`, `complaint_media`, `petitions`, `petition_citations`, `documents`, `document_chunks` (vector), `workflow_runs`, `workflow_events`, `audit_log`, `alerts`, `subscriptions`.
3. Indexes (GiST on geometry, composite on tank+date, HNSW or IVFFlat on vectors), constraints and enums.
4. Seed scripts that load the registry and observations from Stage 2.
5. Repository layer with typed queries and tests against a real Postgres container.
6. Documented ERD in `docs/` (Mermaid) and a migration up/down test.

**Exit criteria:** migrations apply and roll back cleanly; seed loads all pilot data; spatial and vector queries tested; ERD committed.

## STAGE 4: Exploratory data analysis and decision-focused analytics

**Goal:** analysis that supports real decisions, not decorative charts.

Steps:

1. Data quality report: gaps, cloud-induced missingness, outliers, duplicates; cleaning rules in code.
2. Seasonality and monsoon response: lag between rainfall and water-spread change per tank.
3. Tank typology clustering (e.g. by seasonality, size, volatility) to group tanks into archetypes.
4. Shrinkage analysis: current vs historical maximum extent per tank, with confidence.
5. District and block level comparison table and map-ready aggregates.
6. Each analysis documents the user decision it supports (e.g. which tanks to prioritise for desilting before monsoon).
7. Export analytics as API-ready materialised views or tables.

**Exit criteria:** at least six analyses, each with a stated decision, reproducible from code, with findings written in plain language; results available for the API.

## STAGE 5: Machine learning, forecasting and risk

**Goal:** forecasting and risk models that beat honest baselines, evaluated properly.

Steps:

1. Feature engineering: lagged water spread, rolling rainfall (7, 14, 30 days), seasonal terms, groundwater, tank typology, days since last clean pass. No leakage; document each feature.
2. Evaluation protocol: time-based split plus rolling-origin cross-validation; metrics MAE, RMSE, sMAPE, and event metrics (precision/recall for dry-risk and overflow-risk).
3. Baselines: persistence, seasonal naive, linear model. Record their scores first.
4. Advanced models: LightGBM (global model across tanks), plus a sequence model (small LSTM or temporal convolution) for comparison. Calibrate prediction intervals (quantile or conformal).
5. Risk classifier: tank-level labels for `likely dry before crop season` and `overflow risk this monsoon`, with thresholds defined from domain logic and justified.
6. Explainability: SHAP for LightGBM, per-tank explanation text in plain language.
7. Encroachment and shrinkage detector: compare current boundary-derived extent with historical maximum using persistent-water masks; flag permanent loss with a confidence score; manual validation of flagged cases.
8. Model registry: versioned artifacts with metadata (data window, metrics, git hash), loader with fallback to previous version.
9. Batch inference job writing to `forecasts` and `risk_assessments`.
10. Model card in `docs/modules/ml.md` covering limitations and failure modes.

**Exit criteria:** the advanced model beats the best baseline on the held-out period by a stated margin (if it does not, report this honestly, investigate, and iterate; do not hide it); intervals are reasonably calibrated; risk classifier reports precision and recall; inference job runs end to end.

## STAGE 6: Backend API

**Goal:** a secure, tested, documented API.

Steps:

1. Auth: registration, login, JWT access and refresh, password hashing (argon2), roles (`citizen`, `panchayat`, `officer`, `admin`), role-based dependencies.
2. Tank endpoints: list with bbox filter, detail, observations, forecast, risk, encroachment.
3. Analytics endpoints serving Stage 4 outputs.
4. Complaint endpoints: create (text, language, optional photo upload with size and type checks), list own, status updates.
5. Petition endpoints: generate draft (calls RAG module in Stage 8 later; stub contract now), review, approve, reject, export PDF.
6. Alert subscription endpoints and delivery log.
7. Admin endpoints: user management, workflow runs, model versions, audit log.
8. Cross-cutting: Pydantic validation, consistent error format, rate limiting, CORS, request IDs, structured logs written to the DB `audit_log` for sensitive actions.
9. OpenAPI documentation with examples; export to `docs/api/`.
10. Tests: unit and integration, at least 80% coverage on core modules, plus security tests (authz bypass, injection, oversized uploads).

**Exit criteria:** all endpoints tested; role access matrix verified by tests; OpenAPI exported; no high-severity findings from a dependency and static security scan.

## STAGE 7: Frontend

**Goal:** an interactive, polished interface that makes the demo compelling.

Steps:

1. Design system: typography, colour palette (water and earth tones), light and dark themes, responsive layout, accessible components.
2. Auth screens and role-aware navigation.
3. Map home: all pilot tanks on Leaflet or MapLibre with risk colours, filters (district, risk, trend), clustering and legend.
4. Tank detail: water-spread time series with forecast and interval, rainfall overlay, before/after satellite comparison slider, risk badge with explanation, encroachment overlay.
5. Analytics dashboard: Stage 4 insights with the decision each supports.
6. Complaint flow: guided form, Tamil and English input, photo upload, live preview of the structured complaint.
7. Petition review screen: draft with inline citations linking to source passages, edit, approve or reject.
8. Alerts and subscriptions page; admin console for workflow runs, model versions and audit log.
9. Model and LLM performance dashboard showing the latest evaluation metrics.
10. Loading, empty and error states everywhere; Tamil language support (i18n); keyboard and screen-reader checks.
11. Playwright end-to-end tests for the three core journeys.

**Exit criteria:** three core journeys (explore a tank, file a complaint, approve a petition) pass in Playwright; Lighthouse accessibility score target agreed in step 1 is met; works on mobile viewport.

## STAGE 8: Grounded LLM and RAG module

**Goal:** a cited, refusing, evaluated petition and complaint intelligence module that is clearly not a chatbot.

Steps:

1. Corpus ingestion: PDF text extraction with OCR fallback, cleaning, section-aware chunking with page and clause metadata.
2. Embeddings (multilingual model suitable for Tamil and English) stored in pgvector; hybrid retrieval (vector plus keyword) with reranking.
3. Complaint structuring: LLM converts free text (Tamil, Tanglish or English) into a strict JSON schema (issue type, tank reference, location, severity, evidence, requested action) validated with Pydantic; low confidence triggers a clarifying question to the user, not a guess.
4. Tank linking: resolve the complaint to a tank using name, location and geospatial proximity.
5. Petition drafting: retrieve relevant clauses, draft a petition to the correct officer, with every legal claim followed by an inline citation (document, page, clause). Output validated against a schema.
6. Refusal and guardrails: if retrieval confidence is below a tuned threshold or no supporting passage exists, the system says so and returns no legal claim. Prompt-injection defences on uploaded text and documents.
7. Human-in-the-loop: nothing is sent without officer or user approval; the approval is logged.
8. Privacy controls: mask phone numbers and names before sending text to any external model; retention policy documented.
9. Evaluation harness with **at least 50 test cases** (including adversarial, out-of-scope and Tamil cases) measuring groundedness, citation correctness, answer relevance, extraction F1 and refusal accuracy, with human rating on a sample; results saved as JSON and shown on the dashboard.
10. Model abstraction layer so Gemini Flash, Groq or a local model can be swapped; caching and cost controls.

**Exit criteria:** every petition citation resolves to a real passage; refusal accuracy on unsupported queries meets the target set in step 9; evaluation report committed with raw outputs; hallucination rate reported honestly.

## STAGE 9: n8n workflow automation

**Goal:** a robust weekly pipeline with decisions, escalation and failure handling.

Steps:

1. Workflow A, weekly monitor: schedule trigger, fetch new Sentinel-2 passes, validate completeness, compute water spread, call the model API, apply risk thresholds, branch.
2. Branch on breach: generate an evidence report (map snapshot, before/after chart, risk score, explanation), store it, and email and/or Telegram the registered contacts.
3. Failure handling: cloudy or missing pass falls back to the last clean pass and logs a retry with exponential backoff; API errors go to an error workflow that records to `workflow_events` and alerts the admin; dead-letter queue for repeated failure.
4. Workflow B, complaint intake: webhook from the API, structuring, tank linking, petition draft, route to the right officer for review, SLA reminders (e.g. 3-day nudge, 7-day escalation).
5. Workflow C, data refresh: rainfall and groundwater updates on schedule.
6. Idempotency keys so reruns do not duplicate alerts.
7. Every run writes to `workflow_runs` with status, duration and outputs; visible in the admin console.
8. Export workflow JSON to `workflows/n8n/`, credential template, and a runbook describing triggers, branches and recovery.
9. Scenario tests: happy path, cloudy pass, API timeout, duplicate trigger, invalid payload.

**Exit criteria:** all five scenarios behave as documented with captured execution logs; exports re-import cleanly on a fresh n8n; completion rate and retry behaviour measured.

## STAGE 10: Integration, hardening and evaluation

**Goal:** prove the whole system works end to end and measure it.

Steps:

1. Full end-to-end scenario script: new satellite pass, risk breach, alert, complaint, petition, approval, all verified automatically.
2. Load and smoke tests (latency targets for key endpoints, map tile or GeoJSON size budgets).
3. Security review: dependency scan, secret scan, OWASP checklist, authz tests, rate limits.
4. Observability: structured logs, health endpoints, uptime check, error tracking.
5. Data and model monitoring: drift check on rainfall and water-spread features, scheduled re-evaluation of the forecast model on newly observed data.
6. Usability test with at least 5 real users (students, a panchayat or agriculture contact if possible) and capture task completion and feedback.
7. Consolidated evaluation report covering data pipeline, ML, API, frontend, automation, LLM and deployment, matching the proposal's testing table.

**Exit criteria:** end-to-end scenario passes on a clean environment; targets for latency and reliability met or honestly reported with a remediation plan; evaluation report complete.

## STAGE 11: Deployment

**Goal:** a live, reproducible, free-tier deployment.

Steps:

1. Production configs and secrets management for each platform.
2. Database on Supabase or Neon with PostGIS and pgvector enabled; migrations applied through CI.
3. FastAPI plus models on Hugging Face Spaces (Docker) or Render; memory and cold-start tuning.
4. Next.js on Vercel with environment-based API URLs.
5. n8n in Docker on Render or Railway, with persistence and credential handling.
6. GitHub Actions scheduled job for heavy satellite processing so the live API stays light; results pushed to the DB.
7. Smoke test suite run against the live URLs after each deploy; rollback instructions.
8. Seed the live system with the full pilot data and a demo account per role.
9. Uptime monitor and a status section in the README.

**Exit criteria:** public URL works end to end; smoke tests pass against production; weekly job has run at least once on schedule; rollback tested.

## STAGE 12: Documentation, deliverables and viva readiness

**Goal:** everything the university requires, accurate and ready to defend.

Steps:

1. Architecture diagram (Mermaid and exported image) covering UI, API, DB, ML, n8n, LLM/RAG and external services.
2. API documentation, data dictionary, ERD, workflow export and logs, test results, evaluation reports.
3. User manual with screenshots for each role.
4. Final report and the proposal text aligned to the SAI University template sections (all tables filled from real project facts).
5. Demo script (8 to 10 minutes): map, tank detail with forecast, trigger the workflow, risk alert, cited petition draft, evidence PDF.
6. Viva question bank: at least 60 questions with answers drawn from `docs/modules/`, including "why this model", "how do you prevent hallucination", "what if the satellite is cloudy".
7. Demo video recording script and fallback plan if the live demo fails (recorded video, local compose stack).
8. Final repository polish: README, badges, contribution log, tag `v1.0.0`.

**Exit criteria:** every deliverable in the university checklist exists and is current; a fresh reader can reproduce the system from the README; the demo script has been rehearsed end to end at least once.

# START-UP INSTRUCTIONS (DO THIS NOW)

1. Read this entire prompt. Save it to `docs/MASTER_PROMPT.md`.
2. Create `PROGRESS.md` with every stage and step as a checklist, status, commit hash and review link columns.
3. Do **not** ask questions unless you are blocked by something only the user can supply (credentials, registration details, choice between two equally valid options). Otherwise decide, record an ADR, and proceed.
4. Begin **Stage 0, Step 1** only. After each commit, run the micro-review, then continue to the next step automatically. At the end of Stage 0, run the stage gate, stop, and wait for `APPROVED STAGE 0`.
5. At the start of every new session, re-read `docs/MASTER_PROMPT.md` and `PROGRESS.md`, summarise current position in 5 lines, and resume from the first unchecked step.
