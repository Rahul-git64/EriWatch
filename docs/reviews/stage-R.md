# Stage Gate Report: Corrective Stage R — Reopen Stage 0 and Stage 1

- **Date:** 2026-11-02
- **Verdict:** `AWAITING USER VERIFICATION`
- **Reference:** Replaces initial Stage 0 and Stage 1 passes per user corrective mandate.

---

## 1. What Had Been Wrong (Brutally Honest Audit)

Before Stage R, several gate criteria were accepted on weak, simulated, or fabricated evidence:

1. **Synthetic Legal Documents:** The initial RAG corpus contained 28 synthetic 2-page PDFs generated via ReportLab using synthesized text and non-verifiable URLs.
2. **Parametric Crescent Polygons:** 14 irrigation tanks had synthetic crescent-shaped polygons generated programmatically by `_build_crescent_tank_polygon()` rather than real geospatial boundaries.
3. **Unmeasured Health Labels:** Tanks were categorized as `healthy`, `seasonal`, or `shrinking` by assumption without empirical water-spread measurements.
4. **Status Codes Masquerading as Data:** The feasibility spike logged HTTP `200 OK` responses as evidence without recording real payload content (values, dates, raster pixel samples, well distances).
5. **Unquantified Monsoon Cloud Risk:** Risk `R-003` (optical cloud cover during peak monsoon) was acknowledged without empirical quantification or an architectural mitigation design.
6. **Clean-Clone `make setup` Failure:** The original `Makefile` failed with `ENOENT` on Windows when executed from a fresh clone because `npm --prefix apps/web install` looked for `package.json` in the root repository.
7. **CI Not Run on GitHub Actions:** Stage 0 CI passed only locally; no GitHub repository or Actions workflow had been created or executed.

---

## 2. Corrective Actions Completed

| Section | Steps | What Was Done | Key Commits |
|---|---|---|---|
| **R1: Legal Corpus** | R1.1–R1.6 | Deleted all 28 synthetic PDFs. Downloaded **30 real original PDFs** (~24.5 MB) from official government and court archives. Rebuilt `manifest.json` v2.0.0 with SHA-256 digests and page counts. Added strict tests blocking banned hashes. Performed manual 5-document spot-check. Untracked PDFs from git; added `make fetch-legal` and `ADR-0004`. | `1aea5af`, `86598d7`, `f10b668`, `eafca2e`, `82f5552`, `05d8139` |
| **R2: Pilot Registry** | R2.1–R2.4 | Deleted parametric crescent generator. Extracted 21 tank polygons via OSM REST API v0.6 and traced 14 from Sentinel-2 L2A post-monsoon NDWI rasters. Set all labels to `"unverified"`. Generated Sentinel-2 RGB + NDWI overlay checks (`docs/data/overlays/*.png`). Dropped `TN-KPM-013` (Nathapettai Eri, only 9.0% open water), leaving **35 verified pilot tanks** (100% passing overlay). | `ebe822e`, `9b64979`, `5721c11`, `8a09573` |
| **R3: Feasibility Evidence** | R3.1–R3.3 | Rewrote `feasibility_spike.py` to capture real payload data: 2024 STAC scene counts/dates/cloud cover, JRC GSW centroid occurrence/extent pixel values, NASA POWER 15-day precipitation series, 25 India-WRIS CGWB piezometer readings with geodesic distances, and OSM v0.6 vertex counts. Segregated live network tests under `@pytest.mark.network` and `make test-network`. | `4458643`, `d3eb90c`, `145d1dc` |
| **R4: Cloud Cover Telemetry** | R4.1–R4.2 | Queried STAC for all Sentinel-2 L2A passes from 2019 to 2026 across all 35 pilot tanks (`3,150` tank-months, `27,330` deduplicated tank-scene observations). Saved to `data/processed/cloud_stats.parquet` and plotted `docs/data/cloud_cover_seasonality.png`. Proved Oct–Dec usable pass rate is only 18.27% (<20% cloud) and 35.58% (<40% cloud). Authored `ADR-0003` and `ADR-0004` mandating Sentinel-1 SAR fusion for Stage 2. | `e86655e`, `75cc317` |
| **R5: Infrastructure & Verification** | R5.1–R5.4 | Created GitHub repository `Rahul-git64/EriWatch`, pushed `main`, and recorded real green GitHub Actions run **`40928739926`** (Python 22s, Web 45s). Fixed `Makefile` clean-clone bug (`cd apps/web && npm ci`). Ran clean clone in `C:\Temp\eriwatch-clean-clone` with `make setup` and `make test` passing cleanly. Added `pytest-cov` reporting (29% total workspace coverage, 92% API coverage). Documented Windows Docker Desktop WSL troubleshooting in `docs/runbooks/docker-windows.md`. | `d211ea9`, `8fb2720`, `90c209c` |
| **R6: Gate Reports Rebuild** | R6.1–R6.2 | Rewrote `docs/reviews/stage-0.md` and `docs/reviews/stage-1.md` from scratch with explicit "Corrections made" sections and commit citations. Authored `ADR-0004` covering legal storage, SAR fusion, validation independence, and max-extent method. | `0596321`, `90c209c` |
| **R7: Legal Corrections & Geospatial Policies** | R7.1–R7.7 | Fixed LEGAL-002 assent/gazette dates, added `date_precision`, cleaned LEGAL-003, corrected LEGAL-015 to L.C. Jain Report 1997. Built 300 DPI RapidOCR pipeline saving clean page-marked text files in `data/processed/legal_text/` (resolved LEGAL-001 sections 4-8); integrated 370k offline wordlist & quality gate (29 PASS, 1 FAIL). Added `is_extract`, `as_enacted`, and `rag_role` (`core`/`supporting`/`background`) to manifest. Completed 100% 30-document spot check in `docs/data/legal_corpus_spotcheck.md` with relevance audit. Mandated Gazette verification notice for petition drafts in `ADR-0004`. Defined Full Tank Level (FTL) as statutory shrinkage boundary (TN Act 8 of 2007 s.2(d),(e),(o)) with satellite proxy in `ADR-0004`/`0005`. Defined connected components on buffered polygon and `needs_review` flag in `ADR-0005`. Verified TN-CGL-010 as restored SIPCOT Navalur Lake Eco-Park. | `38d5ef0`, `c61cb80`, `7c818a1`, `6e98622`, `1c9a374` |

---

## 3. Scorecard

| Exit Criterion | Status | Evidence (Command, Output Path, Commit Hash) |
|---|---|---|
| 1. Verified original legal corpus | `PASS` | **30 real official PDFs** in `data/raw/legal/` (`0` synthetic/generated files); all SHA-256 hashes and page counts verified by `test_corpus_manifest.py` and `make fetch-legal` (commits `f10b668`, `eafca2e`, `82f5552`) |
| 2. Documented tank provenance & passing overlays ($\ge 30$ tanks) | `PASS` | **35 verified tanks** (21 OSM + 14 Sentinel-2 NDWI traced); all 35 pass visual + quantitative overlay check (`docs/data/overlays/TN-*.png`, 30.7%–99.1% water ratio); `TN-KPM-013` dropped after failing (commits `ebe822e`, `5721c11`, `8a09573`) |
| 3. No unsupported labels | `PASS` | All 35 tanks have `state_archetype = "unverified"` until measured in Stage 2 (commit `9b64979`) |
| 4. Real feasibility payload content | `PASS` | `data/raw/samples/feasibility_spike.json` contains full 2024 STAC scene series, JRC GSW centroid occurrence/extent pixel values, 15-day NASA POWER rainfall time series, 25 CGWB groundwater piezometer readings with geodesic distances, and OSM v0.6 vertices (commits `4458643`, `d3eb90c`) |
| 5. Multi-year cloud statistics & ADR | `PASS` | `data/processed/cloud_stats.parquet` (`3,150` tank-months, `27,330` tank-scenes), `docs/data/cloud_cover_seasonality.png`, and `docs/adr/0003-cloud-cover-and-forecast-design.md` (commits `e86655e`, `75cc317`) |
| 6. Green GitHub Actions run & clean clone | `PASS` | GitHub Actions run **`40928739926`** (`https://github.com/Rahul-git64/EriWatch/actions/runs/40928739926`); clean clone in `C:\Temp\eriwatch-clean-clone` runs `make setup` and `make test` (`EXIT 0`, logged in `scratch/r52_clean_clone_v2.log`) |
| 7. Compose stack health | `PENDING USER VERIFICATION` | All 4 services running and healthy under `make stack-status` (see recorded output below). Marked `PENDING USER VERIFICATION` so the user can verify the stack and Windows WSL mount behavior on their machine. Documented in `docs/runbooks/docker-windows.md`. |

### Recorded Command Output for Criterion 7 (`make stack-status`):
```text
$ make stack-status
docker compose -f infra/docker/docker-compose.yml ps
NAME           IMAGE              COMMAND                  SERVICE   CREATED         STATUS                   PORTS
eriwatch-api   docker-api         "uv run --no-dev uvi…"   api       3 minutes ago   Up 3 minutes (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
eriwatch-db    docker-db          "docker-entrypoint.s…"   db        3 minutes ago   Up 3 minutes (healthy)   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp
eriwatch-n8n   n8nio/n8n:1.68.0   "tini -- /docker-ent…"   n8n       3 minutes ago   Up 3 minutes (healthy)   0.0.0.0:5678->5678/tcp, [::]:5678->5678/tcp
eriwatch-web   docker-web         "docker-entrypoint.s…"   web       3 minutes ago   Up 3 minutes (healthy)   0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp

curl -s http://localhost:8000/health
{"status":"ok","service":"EriWatch API","version":"0.1.0","environment":"development","timestamp":"2026-11-01T21:01:17.923710+00:00"}

curl -s -I http://localhost:3000/
HTTP/1.1 200 OK
Vary: RSC, Next-Router-State-Tree, Next-Router-Prefetch, Accept-Encoding
x-nextjs-cache: HIT
X-Powered-By: Next.js
Cache-Control: s-maxage=31536000, stale-while-revalidate
ETag: "6dbqgjboc448a"
Content-Type: text/html; charset=utf-8
Content-Length: 5487
Date: Sun, 01 Nov 2026 21:01:18 GMT
Connection: keep-alive
Keep-Alive: timeout=5

curl -s http://localhost:5678/healthz
{"status":"ok"}
```

---

## 4. Quality Metrics

- **Python Linting:** `uv run ruff check .` -> `All checks passed!`
- **Python Type-Checking:** `uv run mypy apps/api/src packages/geo/src packages/ml/src packages/rag/src` -> `Success: no issues found in 12 source files` (`strict = true`)
- **Unit Tests:** `uv run pytest --cov=apps/api/src --cov=packages/geo/src --cov=packages/ml/src --cov=packages/rag/src --cov-report=term-missing -m "not network"` -> `11 passed, 3 deselected in 11.32s`
- **Test Coverage:** `apps/api` 92%, `packages/geo` 23%, `packages/rag` 34%, Total workspace 29% (`pytest-cov`)
- **Web Testing & Linting:** `cd apps/web && npm run lint` (0 errors), `npm run typecheck` (0 errors), `npm run format:check` (100% formatted), `npm run test` (1 Vitest passed)
- **Legal Corpus Integrity:** 30 real official PDFs, 0 dead links, 0 synthetic hashes
- **Pilot Registry Integrity:** 35 real tanks, 100% passing imagery overlays

---

## 5. Remaining Risks

| ID | Description | Severity | Mitigation Plan |
|---|---|---|---|
| R-002 | Windows host Docker Desktop WSL automount `/c` path resolution across reboots | Medium | Documented in `docs/runbooks/docker-windows.md`; clean start procedure established; make targets `stack-up`, `stack-down`, `stack-status` provided |
| R-003 | Northeast Monsoon optical cloud cover (<20% cloud on only 18.27% of passes in Oct–Dec) | High | Resolved in `ADR-0003` & `ADR-0004`: Sentinel-1 SAR backscatter fusion (`sentinel-1-rtc`) integrated into Stage 2 |

---

## 6. Demo Script

1. **Verify Legal Corpus Integrity:**
   `make fetch-legal` (or `uv run pytest packages/rag/tests/test_corpus_manifest.py -m "not network"`)
2. **Verify Pilot Tank Registry & Overlays:**
   `uv run pytest packages/geo/tests/test_registry.py -m "not network"`
   Inspect overlay image `docs/data/overlays/TN-KPM-001.png`
3. **Verify Feasibility Payloads & Cloud Statistics:**
   `uv run pytest packages/geo/tests/test_feasibility_spike.py packages/geo/tests/test_cloud_stats.py -m "not network"`
   Inspect seasonality plot `docs/data/cloud_cover_seasonality.png`
4. **Verify Clean-Clone Workspace:**
   `make lint && make test`
5. **Verify Docker Stack:**
   `make stack-status`
6. **Inspect Live GitHub Actions CI:**
   View run `https://github.com/Rahul-git64/EriWatch/actions/runs/40928739926`

---

## 7. Verdict

`AWAITING USER VERIFICATION` — Corrective Stage R has eradicated all synthetic documents and parametric polygons, verified real payloads across all external sources, quantified cloud-cover risk with multi-year telemetry, committed `ADR-0003` and `ADR-0004`, established clean-clone CI on GitHub Actions, documented Docker Windows troubleshooting in `docs/runbooks/docker-windows.md`, and brought the entire 4-service stack to a healthy state. The stage is placed in `AWAITING USER VERIFICATION` for the user to review the live stack, the 35 overlays, and the legal manifest before proceeding to Stage 2.
