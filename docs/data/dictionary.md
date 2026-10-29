# EriWatch Data Dictionary (`docs/data/dictionary.md`)

This document specifies every field, data type, unit, valid range, nullability, and licence across all datasets ingested, computed, and persisted by EriWatch.

---

## 1. Pilot Tank Registry (`data/processed/tank_registry.geojson` & `tanks` table)

- **Source:** OpenStreetMap (`osm`) and Sentinel-2 / JRC Global Surface Water digitised boundaries (`derived`).
- **Licence:** Open Database License (`ODbL 1.0`) for OSM features; `CC-BY-4.0` for derived satellite boundaries.

| Field | Type | Unit | Constraints / Range | Description |
|---|---|---|---|---|
| `id` | `string` | - | `^TN-(KPM\|CGL)-\d{3}$`, PK | Unique tank identifier (`TN-KPM-001`..`018`, `TN-CGL-001`..`018`) |
| `name` | `string` | - | Non-empty | Official / local irrigation tank (*eri*) name |
| `district` | `enum` | - | `Kancheepuram`, `Chengalpattu` | Tamil Nadu revenue district |
| `block` | `string` | - | Non-empty | Panchayat union / community development block |
| `centroid_lat` | `float64` | `degrees_north` | `[12.0, 13.5]` (`EPSG:4326`) | Tank centroid latitude (WGS84) |
| `centroid_lon` | `float64` | `degrees_east` | `[79.4, 80.4]` (`EPSG:4326`) | Tank centroid longitude (WGS84) |
| `nominal_max_area_ha` | `float64` | `hectares (ha)` | `>= 12.0` ($1\text{ ha} = 10,000\text{ m}^2$) | Historical maximum water-spread area |
| `state_archetype` | `enum` | - | `healthy`, `seasonal`, `shrinking` | Baseline hydrological behaviour archetype |
| `source` | `enum` | - | `osm`, `derived` | Provenance of the tank polygon boundary |
| `confidence` | `enum` | - | `high`, `medium` | Boundary accuracy confidence (`high` for verified OSM, `medium` for derived) |
| `osm_id` | `int64 \| null` | - | Positive integer or `null` | OpenStreetMap way/relation ID when `source = "osm"` |
| `geometry` | `Polygon` | `degrees` | Closed ring, `EPSG:4326` | Tank boundary polygon |

---

## 2. Sentinel-2 L2A Satellite Imagery & Water-Spread Observations (`observations` table)

- **Source:** Copernicus Sentinel-2 Mission (ESA) via Microsoft Planetary Computer STAC (`sentinel-2-l2a`) and Element84 Earth Search STAC (`sentinel-2-l2a`).
- **Licence:** Copernicus Open Access License (free, full, and open access; attribution: *Contains modified Copernicus Sentinel data*).

### 2.1 Raw Band & Mask Assets

| Band / Asset | Native Resolution | Wavelength | Unit | Usage in EriWatch |
|---|---|---|---|---|
| `B03` (Green) | `10 m` | `560 nm` | Surface reflectance (`DN / 10000`, `0.0–1.0`) | Numerator of NDWI and MNDWI |
| `B08` (NIR) | `10 m` | `842 nm` | Surface reflectance (`DN / 10000`, `0.0–1.0`) | Denominator of NDWI: $(\text{B03} - \text{B08}) / (\text{B03} + \text{B08})$ |
| `B11` (SWIR1) | `20 m` (resampled to `10 m`) | `1610 nm` | Surface reflectance (`DN / 10000`, `0.0–1.0`) | Denominator of MNDWI: $(\text{B03} - \text{B11}) / (\text{B03} + \text{B11})$ |
| `SCL` | `20 m` (resampled to `10 m`) | - | Categorical class (`0–11`) | Scene Classification Layer for cloud/shadow/snow masking (`0: No Data`, `1: Saturated/Defective`, `3: Cloud Shadow`, `8: Cloud Medium Prob`, `9: Cloud High Prob`, `10: Thin Cirrus`, `11: Snow/Ice` masked out) |

### 2.2 Derived Observation Records

| Field | Type | Unit | Constraints / Range | Description |
|---|---|---|---|---|
| `tank_id` | `string` | - | FK → `tanks.id` | Pilot tank identifier |
| `obs_date` | `date` | `ISO-8601 (YYYY-MM-DD)` | `>= 2019-01-01` | Satellite pass acquisition date (UTC) |
| `scene_id` | `string` | - | Non-empty | Sentinel-2 L2A STAC item ID |
| `water_area_ha` | `float64` | `hectares (ha)` | `>= 0.0` | Computed water-spread area inside tank polygon |
| `fill_fraction` | `float64` | `ratio (0–1)` | `[0.0, 1.5]` | `water_area_ha / nominal_max_area_ha` |
| `ndwi_area_ha` | `float64` | `hectares (ha)` | `>= 0.0` | Water area estimated via NDWI |
| `mndwi_area_ha` | `float64` | `hectares (ha)` | `>= 0.0` | Water area estimated via MNDWI |
| `otsu_threshold` | `float64` | `index value` | `[-0.5, 0.5]` | Selected Otsu (or fallback `0.0`) water index threshold |
| `valid_fraction` | `float64` | `ratio (0–1)` | `[0.0, 1.0]` | Fraction of tank polygon pixels free of clouds, shadows, and defects |
| `cloud_fraction` | `float64` | `ratio (0–1)` | `[0.0, 1.0]` | `1.0 - valid_fraction` |
| `quality_flag` | `enum` | - | `clean`, `partial`, `cloudy`, `low_confidence` | `clean` ($\text{valid\_fraction} \ge 0.85$), `partial` ($0.50 \le \text{valid\_fraction} < 0.85$), `cloudy` ($< 0.50$), `low_confidence` (fallback threshold or sensor artifact) |

---

## 3. JRC Global Surface Water Validation Dataset (`jrc-gsw`)

- **Source:** European Commission Joint Research Centre (Pekel et al., *Nature* 2016) via Planetary Computer STAC (`jrc-gsw`).
- **Licence:** Copernicus / European Union Open Reuse Policy (`CC-BY-4.0` equivalent).

| Asset / Field | Type | Unit | Constraints / Range | Description |
|---|---|---|---|---|
| `occurrence` | `uint8` raster (`30 m`) | `percent (%)` | `0–100` (`255 = No Data`) | Historical frequency (1984–2021) with which water was present on the surface |
| `extent` | `uint8` raster (`30 m`) | `binary (0/1)` | `0` (never water), `1` (water detected) | Maximum historical water extent mask |
| `seasonality` | `uint8` raster (`30 m`) | `months/year` | `0–12` | Number of months water is present in a single year |

---

## 4. Meteorological & Hydrological Covariates (`rainfall` & groundwater tables)

- **Sources:**
  - **NASA POWER Agroclimatology API (`power.larc.nasa.gov`):** MERRA-2 / GPM daily meteorological time series.
  - **India-WRIS / Central Ground Water Board (`indiawris.gov.in`):** Official CGWB piezometer observations.
- **Licence:** NASA Open Data Policy (Public Domain / `CC0`) and Government of India Open Data License (`GODL-India`).

| Field | Type | Unit | Constraints / Range | Description |
|---|---|---|---|---|
| `tank_id` | `string` | - | FK → `tanks.id` | Pilot tank identifier |
| `obs_date` | `date` | `ISO-8601 (YYYY-MM-DD)` | `>= 2019-01-01` | Observation date |
| `rainfall_mm` | `float64` | `mm/day` | `>= 0.0` | Daily bias-corrected precipitation (`PRECTOTCORR`) |
| `temp_mean_c` | `float64` | `°C` | `[10.0, 50.0]` | Daily 2-meter air temperature (`T2M`) driving evaporation |
| `root_zone_wetness` | `float64` | `fraction (0–1)` | `[0.0, 1.0]` | NASA POWER root-zone soil wetness (`GWETROOT`) |
| `profile_wetness` | `float64` | `fraction (0–1)` | `[0.0, 1.0]` | NASA POWER total profile subsurface wetness (`GWETPROF`) |
| `cgwb_gw_depth_mbgl` | `float64 \| null` | `m bgl` | `>= 0.0` or `null` | Nearest CGWB station depth to water level (meters below ground level) |
| `cgwb_station_code` | `string \| null` | - | e.g., `TNGW0029`, `CGWBTN45` | Identifier of nearest CGWB monitoring well |

---

## 5. ML Forecasts, Risk Assessments & Shrinkage (`forecasts`, `risk_assessments`, `encroachment_findings`)

- **Source:** Generated internally by `packages/ml`.
- **Licence:** MIT (EriWatch project output).

| Field | Type | Unit | Constraints / Range | Description |
|---|---|---|---|---|
| `tank_id` | `string` | - | FK → `tanks.id` | Pilot tank identifier |
| `forecast_date` | `date` | `YYYY-MM-DD` | Target date ($t + 1 \dots t + 30$) | Date for which water spread is predicted |
| `horizon_days` | `int` | `days` | `1–30` | Forecast lead time in days |
| `predicted_area_ha` | `float64` | `hectares (ha)` | `>= 0.0` | Point forecast of water-spread area |
| `lower_80_ha` / `upper_80_ha` | `float64` | `hectares (ha)` | `>= 0.0` | Calibrated 80% conformal/quantile prediction interval |
| `lower_95_ha` / `upper_95_ha` | `float64` | `hectares (ha)` | `>= 0.0` | Calibrated 95% conformal/quantile prediction interval |
| `dry_risk_flag` | `bool` | - | `true`/`false` | `likely_dry_before_crop_season` alert flag |
| `overflow_risk_flag` | `bool` | - | `true`/`false` | `overflow_risk_this_monsoon` alert flag |
| `risk_score` | `float64` | `probability (0–1)` | `[0.0, 1.0]` | Calibrated risk probability score |
| `shap_explanation` | `string` | - | Non-empty plain text | Human-readable explanation derived from top SHAP contributors |
| `shrinkage_pct` | `float64` | `percent (%)` | `[0.0, 100.0]` | Persistent loss of water-bearing footprint vs historical maximum extent |

---

## 6. Legal RAG Corpus, Complaints & Cited Petitions (`documents`, `complaints`, `petitions`)

- **Sources:** Tamil Nadu Water Resources Department (WRD / PWD) Government Orders, *Kudimaramath* scheme guidelines, Madras High Court judgments, and National Green Tribunal (NGT) Southern Zone orders (`data/raw/legal/manifest.json`).
- **Licence:** Public legal/judicial records and Government of India / Tamil Nadu public orders (fair use for statutory grievance redressal; full source attribution stored per chunk).

| Field | Type | Unit | Constraints / Range | Description |
|---|---|---|---|---|
| `doc_id` | `string` | - | `^LEGAL-\d{3}$` | Unique identifier in `data/raw/legal/manifest.json` |
| `title` | `string` | - | Non-empty | Official Government Order, Statute, or Court Order title |
| `issuer` | `string` | - | WRD / PWD / Madras HC / NGT SZ | Issuing authority or court |
| `issue_date` | `date` | `YYYY-MM-DD` | Valid historical date | Date of order/judgment |
| `embedding` | `vector(384)` | `L2-normalized float32` | 384 dimensions | Multilingual embedding (`paraphrase-multilingual-MiniLM-L12-v2`) |
| `issue_type` | `enum` | - | `encroachment`, `bund_breach`, `sluice_damage`, `siltation`, `inflow_blockage`, `pollution`, `other` | Structured complaint classification |
| `language` | `enum` | - | `ta`, `en`, `tanglish` | Input complaint language |
| `citations` | `jsonb` | - | Array of `{doc_id, page, clause, quote}` | Verifiable inline legal citations supporting every petition claim |
| `refusal_reason` | `string \| null` | - | Non-null when refused | Populated when retrieval confidence is below threshold or no legal source backs the claim |
