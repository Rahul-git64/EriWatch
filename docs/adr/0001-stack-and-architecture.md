# ADR-0001: Core Technology Stack and System Architecture

- **Status:** Accepted
- **Date:** 2026-10-29
- **Stage:** Stage 0

## Context

EriWatch requires an end-to-end platform that:
1. Ingests 10 m Sentinel-2 L2A satellite imagery, masks clouds/shadows, and computes per-tank water-spread areas (`packages/geo`).
2. Trains and serves 30-day water-spread forecasting models with calibrated intervals, dry/overflow risk classifiers, and SHAP explanations (`packages/ml`).
3. Structures Tamil/Tanglish/English complaints and drafts legally cited petitions grounded in public Water Resources Department (WRD) orders, *Kudimaramath* guidelines, and court judgments, refusing when unsupported (`packages/rag`).
4. Exposes role-based APIs (`apps/api`) and an interactive geospatial map interface (`apps/web`).
5. Automates weekly satellite passes, breach alerts, and complaint routing (`workflows/n8n`).
6. Deploys cleanly on free-tier infrastructure and remains explainable by a final-year B.Tech student during university evaluation.

## Decision

We adopt the following unified architecture and technology stack:

1. **Geospatial, ML, and RAG Core (`Python >= 3.11`, managed via `uv` workspace):**
   - `packages/geo`: `pystac-client` / `planetary-computer` for STAC queries, `rasterio` / `odc-stac` for windowed COG reads (avoiding full-scene downloads), `shapely` / `geopandas` for vector boundaries, and `scikit-image` / `numpy` for NDWI/MNDWI + Otsu thresholding.
   - `packages/ml`: `pandas` / `pyarrow` for feature matrices, `scikit-learn` for baselines, `lightgbm` for global multi-tank forecasting, PyTorch (`torch`) for sequence model comparison, and `shap` for local/global feature attribution.
   - `packages/rag`: `pymupdf` (with OCR fallback) for legal corpus ingestion, `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`) for Tamil + English embeddings, PostgreSQL `pgvector` + full-text keyword search for hybrid retrieval, and a provider-agnostic LLM adapter supporting Gemini Flash, Groq, and local deterministic testing.
2. **Backend API (`apps/api`):**
   - **FastAPI** with **Pydantic v2** (`pydantic-settings`), **SQLAlchemy 2.0** (typed ORM), **Alembic** migrations, **Argon2** password hashing, and JWT access/refresh tokens with role-based access control (`citizen`, `panchayat`, `officer`, `admin`).
3. **Database (`PostgreSQL 16` + `PostGIS 3.4` + `pgvector`):**
   - A single unified PostgreSQL database stores relational state, spatial tank polygons/centroids (`PostGIS` with GiST indexes), time-series observations/forecasts, and legal document chunk embeddings (`pgvector` with HNSW indexes).
4. **Frontend (`apps/web`):**
   - **Next.js 14** (App Router, TypeScript, Tailwind CSS) with **Leaflet / MapLibre** for interactive tank maps, bilingual Tamil/English support, Vitest unit tests, and Playwright E2E tests.
5. **Workflow Automation (`workflows/n8n` + GitHub Actions):**
   - **n8n** orchestrates weekly monitoring triggers, threshold branching, evidence report dispatch, complaint intake webhooks, and cloudy-pass fallback/retry state machines. Heavy satellite batch backfills run via GitHub Actions or CLI runners so the live API server stays lightweight.

## Alternatives Considered

1. **Separate Vector DB (Pinecone / Qdrant) + Separate Spatial DB:**
   - *Rejected:* Splits transactional consistency across three services, complicates free-tier deployment, and adds operational overhead when `PostgreSQL + PostGIS + pgvector` handles 50 pilot tanks and ~1,000 legal chunks in a single ACID store.
2. **Google Earth Engine (GEE) Python API instead of Planetary Computer STAC + Windowed COGs:**
   - *Rejected:* GEE requires individual institutional account approval and non-portable service account credentials, breaking clean-clone reproducibility (`make setup && make test`). Planetary Computer STAC provides anonymous/public COG access with Copernicus Data Space as fallback.
3. **Unconstrained Conversational Chatbot for Legal Grievances:**
   - *Rejected:* High risk of hallucinated Government Orders or legal sections. A structured complaint extractor + hybrid RAG petition drafter with strict schema validation, inline citations, refusal guardrails, and mandatory human-in-the-loop approval is safer and directly verifiable.

## Consequences

- **Positive:** Single database engine (`PostgreSQL + PostGIS + pgvector`) simplifies local Docker Compose and cloud deployment (Supabase/Neon); strict typing across Python (`mypy --strict`, Pydantic v2) and TypeScript (`tsc --noEmit`) catches contract drift early.
- **Negative / Risks:** Combining PostGIS and pgvector in a local container requires a custom `Dockerfile.db` (`postgis/postgis:16-3.4` + `postgresql-16-pgvector`), which we built and verified in `infra/docker/Dockerfile.db`.
