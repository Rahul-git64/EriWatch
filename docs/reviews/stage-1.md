# Stage Gate Report: Stage 1 — Data Discovery and Feasibility Spike

- **Date:** 2026-10-29
- **Verdict:** `PASS`

## 1. Phase Goal & Exit Criteria

**Goal:** Prove every external data source works and choose the pilot tanks with evidence.

**Exit Criteria:**
- [x] Each source returns real data for at least 3 pilot tanks
- [x] Pilot list and registry committed (`30–50` tanks)
- [x] At least 25 legal documents collected with manifest
- [x] Feasibility report states any gaps and the chosen mitigation

## 2. Scorecard

| Exit Criterion | Status (`PASS`/`FAIL`) | Evidence (Command, Output Path, Commit Hash) |
|---|---|---|
| Each source returns real data for $\ge 3$ pilot tanks | `PASS` | `uv run python -m eriwatch_geo.feasibility_spike` returned HTTP `200 OK` across **4 pilot tanks** (`TN-KPM-001` Chembarambakkam, `TN-CGL-001` Madurantakam, `TN-KPM-002` Thenneri, `TN-CGL-002` Kolavai Lake) for Planetary Computer STAC (`sentinel-2-l2a`), Copernicus OData + Element84 STAC fallbacks, JRC Global Surface Water (`jrc-gsw`), NASA POWER (`PRECTOTCORR`, `GWETROOT`, `GWETPROF`), India-WRIS CGWB Groundwater (`TNGW0029`, `CGWBTN45`), and OpenStreetMap Nominatim GeoJSON polygons; saved to [`data/raw/samples/feasibility_spike.json`](../../data/raw/samples/feasibility_spike.json) and tested in [`test_feasibility_spike.py`](../../packages/geo/tests/test_feasibility_spike.py) (`4338779`) |
| Pilot list and registry committed | `PASS` | **36 pilot tanks** (18 Kancheepuram, 18 Chengalpattu; 12 `healthy`, 13 `seasonal`, 11 `shrinking`; 22 `osm` high-confidence + 14 `derived` medium-confidence) documented in [`docs/data/pilot_selection.md`](../data/pilot_selection.md) (`23365f1`) and generated/validated in [`data/processed/tank_registry.geojson`](../../data/processed/tank_registry.geojson) via [`packages/geo/src/eriwatch_geo/registry.py`](../../packages/geo/src/eriwatch_geo/registry.py) (`9b8e68c`) |
| At least 25 legal documents collected with manifest | `PASS` | **28 legal PDFs** (`LEGAL-001` through `LEGAL-028`) and [`data/raw/legal/manifest.json`](../../data/raw/legal/manifest.json) built and verified via `pypdf.PdfReader` in [`test_corpus_manifest.py`](../../packages/rag/tests/test_corpus_manifest.py) (`859c32a`) |
| Feasibility report states gaps & chosen mitigations | `PASS` | Documented in [`docs/data/feasibility.md`](../data/feasibility.md), [`docs/data/dictionary.md`](../data/dictionary.md) (`c3d88d2`), and [`docs/data/licensing_and_ethics.md`](../data/licensing_and_ethics.md) (`f5cc634`) |

## 3. Path Check

- **Is the work heading where the end-to-end goal needs it to?** Yes:
  1. Stage 2 (`Geospatial pipeline`) can immediately consume [`data/processed/tank_registry.geojson`](../../data/processed/tank_registry.geojson) (36 closed `Polygon` geometries in `EPSG:4326`) and query Planetary Computer STAC (`sentinel-2-l2a`) with Element84 Earth Search STAC as fallback.
  2. Stage 3 (`Database and data model`) has an exact field-by-field specification in [`docs/data/dictionary.md`](../data/dictionary.md) for all spatial, time-series, and vector tables.
  3. Stage 8 (`Grounded LLM and RAG module`) has 28 real statutory/WRD/Kudimaramath/HC/NGT two-page PDFs with explicit page numbers, clause numbers, and designated officers in [`data/raw/legal/manifest.json`](../../data/raw/legal/manifest.json).
- **What would break downstream if we continue as is?** Nothing; all external API gaps (public Overpass bbox timeouts, CDSE STAC vs OData, sparse CGWB well spacing) were caught during Step 1.1 and mitigated with deterministic local registries and dual-source fallbacks.

## 4. Quality Metrics

- **Python Lint & Type-Check:** `uv run ruff check .` (`All checks passed!`), `uv run mypy apps/api/src packages/geo/src packages/ml/src packages/rag/src` (`Success: no issues found in 10 source files`)
- **Python Unit Tests:** `10 passed in 1.99s` (including `test_feasibility_spike.py`, `test_registry.py`, and `test_corpus_manifest.py`)
- **Web Tests & Lint:** `1 passed (1)` in Vitest, 0 ESLint/TypeScript errors
- **Pilot Cohort Size:** `36 tanks` (Target: `30–50 tanks`)
- **Legal Corpus Size:** `28 PDFs + manifest.json` (Target: `>= 25 documents`)
- **Micro-Reviews Completed:** 6 / 6 (`docs/reviews/micro/1-1.md` through `docs/reviews/micro/1-6.md`)

## 5. Debt & Risks

| ID | Description | Severity | Remediation Plan |
|---|---|---|---|
| R-001 | Next.js 14.2.x transitive npm audit advisories | Low | Address in Stage 6/10 dependency security hardening |
| R-003 | Monsoon cloud cover in Oct–Dec over Kancheepuram/Chengalpattu can exceed 80% (`eo:cloud_cover` up to 88.8% observed in Dec 2024 spike) | Medium | Implement SCL pixel-level cloud/shadow masking, `valid_fraction` quality flags, and last-clean-pass fallback in Stage 2 & Stage 9 |

## 6. Demo Script

1. Run `uv run python -m eriwatch_geo.feasibility_spike` to execute live HTTP queries against Planetary Computer STAC, Copernicus OData, Element84 STAC, JRC Global Surface Water, NASA POWER, India-WRIS CGWB, and OpenStreetMap Nominatim.
2. Run `uv run python -m eriwatch_geo.registry` to generate and validate the 36-tank GeoJSON registry (`data/processed/tank_registry.geojson`).
3. Run `uv run python -m eriwatch_rag.corpus_manifest` to verify all 28 legal PDFs and `data/raw/legal/manifest.json`.
4. Run `make lint && make test` to verify all 10 Python tests, strict Mypy checks, Ruff lint, and Web tests pass.

## 7. Verdict

`PASS` — All 4 Stage 1 exit criteria passed with live evidence; repository tagged `stage-1-pass`.
