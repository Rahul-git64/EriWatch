# ADR-0003: Sentinel-2 Monsoon Cloud-Cover Mitigation and Irregular-Cadence Forecasting Design

- **Status:** Accepted
- **Date:** 2026-10-29
- **Stage:** Corrective Stage R (Step R4.2)

## Context

In Step R4.1 (`packages/geo/src/eriwatch_geo/cloud_stats.py`), we queried the Element84 Earth Search STAC API (`sentinel-2-l2a`) across all **35 verified pilot tanks** in Kancheepuram and Chengalpattu from `2019-01-01` to `2026-10-29` (`3,150` tank-months, `27,330` deduplicated tank-scene observations, saved in `data/processed/cloud_stats.parquet` and plotted in `docs/data/cloud_cover_seasonality.png`).

The empirical measurements show a severe seasonal drop in usable optical satellite passes during the monsoon months when flood-overflow and rapid tank-inflow monitoring matter most:

| Hydrological Season | Months | Tank-Months | Total Scenes | Mean Passes / Tank / Month | Mean `eo:cloud_cover` | Share `< 20%` Cloud (Passes/Mo) | Share `< 40%` Cloud (Passes/Mo) |
|---|---|---|---|---|---|---|---|
| **Dry / Post-Monsoon** | Jan–May | 1,400 | 11,970 | `8.55` | `34.52%` | **`43.40%`** (`3.71 / mo`) | **`65.70%`** (`5.62 / mo`) |
| **Southwest Monsoon** | Jun–Sep | 1,120 | 9,748 | `8.70` | `65.58%` | **`17.59%`** (`1.53 / mo`) | **`29.38%`** (`2.56 / mo`) |
| **Northeast Monsoon** | Oct–Dec | 630 | 5,612 | `8.85` | `58.15%` | **`18.27%`** (`1.62 / mo`) | **`35.58%`** (`3.15 / mo`) |

During the **Northeast Monsoon (October–December)**—which delivers ~60% of northern Tamil Nadu's annual rainfall and drives tank overflow risk—only **`18.27%`** of Sentinel-2 scenes have scene-wide `eo:cloud_cover < 20%` (`1.62` passes per tank per month, dropping to **`12%`** in November), and **`35.58%`** have `< 40%` cloud cover (`3.15` passes per tank per month). Consequently, a naive pipeline that filters scenes strictly on tile-wide `eo:cloud_cover < 20%` or assumes a fixed 5-day optical time series will frequently experience 15-to-30-day observation blind spots during peak monsoon storms.

## Decision

We adopt a three-tier architectural mitigation across **Stage 2 (Geospatial Pipeline)**, **Stage 5 (Machine Learning & Forecasting)**, and **Stage 9 (n8n Automation)**:

### 1. Stage 2 (`packages/geo`): Polygon-Clipped `SCL` Valid-Pixel Gating Instead of Scene-Wide `eo:cloud_cover` Rejection
- A Sentinel-2 MGRS tile (`44PLV`, `44PLU`, `44PMV`) covers `100 km × 100 km` (`1,000,000 ha`), whereas our 35 pilot tanks span `19.65 ha` to `2,175.66 ha`. A tile with `eo:cloud_cover = 65%` often has cloud-free gaps directly over individual village tanks.
- **Stage 2 Rule:** Fetch candidate STAC scenes up to `eo:cloud_cover <= 80%`, perform a fast windowed read of the 20 m Scene Classification Layer (`SCL`) clipped to the tank polygon (`+ 100 m` buffer), and mask out classes `3` (cloud shadow), `8` (cloud medium probability), `9` (cloud high probability), `10` (thin cirrus), and `11` (snow/ice).
- Compute `valid_pixel_fraction = valid_pixels / total_polygon_pixels` per tank per pass:
  - `valid_pixel_fraction >= 0.85`: **`HIGH_QUALITY`** observation (direct NDWI/MNDWI water-spread calculation).
  - `0.60 <= valid_pixel_fraction < 0.85`: **`PARTIAL_CLOUD`** observation (water spread computed with quality flag and wider observation uncertainty).
  - `valid_pixel_fraction < 0.60`: **`CLOUDY_REJECTED`** (observation masked out as missing; logged for retry/fallback).

### 2. Stage 5 (`packages/ml`): Irregular-Cadence Features, Explicit `days_since_last_clean_pass`, and Rainfall-Driven Fallback
- Because optical observations arrive at irregular intervals (`5 days` in Feb–Apr vs `10–25 days` in Oct–Dec), the 30-day forecasting model must **not** assume uniform 5-day time steps without missingness awareness:
  1. **Explicit Observation-Gap Features:** Include `days_since_last_valid_pass`, `last_valid_spread_ha`, `last_valid_fraction`, and exponentially decayed observation weights alongside continuous daily **NASA POWER (`PRECTOTCORR`)** rainfall accumulations (`3d`, `7d`, `14d`, `30d` rolling sums) and **NASA POWER (`GWETPROF`) / CGWB groundwater** covariates—which are 100% cloud-independent.
  2. **Monsoon Inflow / Overflow Regime:** During consecutive cloudy passes (`days_since_last_valid_pass > 10`) accompanied by heavy Northeast Monsoon rainfall (`7d_rainfall_mm >= 100 mm`), the LightGBM quantile regressor and overflow risk classifier rely primarily on cumulative basin rainfall and tank capacity ratio (`last_valid_spread_ha / nominal_max_area_ha`), while **widening the 80%/90% prediction interval** proportionally to `days_since_last_valid_pass`.
  3. **Evaluation Stratification:** Stage 5 rolling-origin cross-validation will report MAE/RMSE/sMAPE and overflow-event precision/recall **separately for Northeast Monsoon (`Oct–Dec`) vs Dry Season (`Jan–May`)** to prove the model does not degrade silently during cloudy months.

### 3. Stage 9 (`workflows/n8n`): Cloudy-Pass Fallback State Machine and Transparent Alert Provenance
- When the weekly n8n monitoring workflow (`Workflow A`) triggers on a pass where `valid_pixel_fraction < 0.60` (`CLOUDY_REJECTED`):
  1. The workflow falls back to the **last clean optical pass** (`valid_pixel_fraction >= 0.85`) combined with **up-to-date daily NASA POWER rainfall** through the current date to run the 30-day forecast and overflow/dry risk check.
  2. Every generated alert or evidence report explicitly stamps `optical_pass_date`, `days_since_clean_pass`, `cloud_fallback_used = true`, and `recent_7d_rainfall_mm` so panchayat officers know whether an overflow warning is driven by a fresh optical water mask or by heavy monsoon rainfall following the last clean satellite pass.
  3. The workflow schedules a mid-week retry (`+3 days`, corresponding to the next Sentinel-2A/2B twin-satellite sub-swath revisit) and logs the cloudy fallback event to `workflow_runs`.

## Alternatives Considered

1. **Sentinel-1 SAR (C-Band Radar) Primary Pipeline:**
   - *Rejected as primary Stage 2 requirement, retained as documented future extension:* While Sentinel-1 VV/VH backscatter penetrates clouds, wind-roughened water surfaces during cyclones and emergent aquatic vegetation (`prosopis` / water hyacinth) in shallow Tamil Nadu *eris* cause high false-negative water masks at 10 m resolution, and Sentinel-1B's December 2021 power anomaly reduced revisit frequency to 12 days through 2022–2024. Polygon-clipped Sentinel-2 `SCL` gating + cloud-free NASA POWER daily rainfall covariates provide a cleaner, verifiable solution within the capstone scope.
2. **Linear Interpolation Across Cloudy Gaps Before Model Training:**
   - *Rejected:* Linearly interpolating water spread across a 20-day monsoon cloud gap fabricates smooth trajectories that hide sudden 48-hour cyclone fill events and leaks future observations into training features.

## Consequences

- **Positive:** Maximizes usable observations during Oct–Dec by evaluating cloud cover inside each tank's actual polygon rather than rejecting entire `100 km × 100 km` tiles; prevents forecast failure during prolonged monsoon cloud cover; ensures honest uncertainty intervals and user-facing provenance.
- **Negative / Risks:** Stage 2 must read the `SCL` COG window for candidate scenes up to `80%` tile cloud cover before deciding whether to read `B03`/`B08`/`B11`, adding ~`0.15 s` per cloudy candidate scene during backfill.
