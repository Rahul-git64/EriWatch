# Stage 1 Feasibility Report: External Data Sources

- **Executed At:** `2026-10-29T13:13:29Z`
- **Command:** `uv run python -m eriwatch_geo.feasibility_spike`
- **Raw Evidence Artifact:** [`data/raw/samples/feasibility_spike.json`](../../data/raw/samples/feasibility_spike.json)

## 1. Executive Summary

Every external data category required by EriWatch (Sentinel-2 L2A optical imagery, fallback STAC/OData catalogs, JRC Global Surface Water validation rasters, daily rainfall, groundwater/subsurface wetness, and OpenStreetMap tank boundaries) was tested with live HTTP calls across 4 pilot tanks in Kancheepuram and Chengalpattu districts:

1. `TN-KPM-001` — **Chembarambakkam Tank** (`13.0116, 80.0592`, Kundrathur Block, Kancheepuram)
2. `TN-CGL-001` — **Madurantakam Tank** (`12.5133, 79.8736`, Madurantakam Block, Chengalpattu)
3. `TN-KPM-002` — **Thenneri Tank** (`12.8586, 79.8825`, Walajabad Block, Kancheepuram)
4. `TN-CGL-002` — **Kolavai Lake** (`12.7072, 79.9856`, Kattankolathur Block, Chengalpattu)

| Data Category | Primary Endpoint | Fallback Endpoint | Live Status | Mean Latency | Tanks Verified |
|---|---|---|---|---|---|
| **Sentinel-2 L2A (10 m / 20 m COGs)** | Microsoft Planetary Computer STAC (`sentinel-2-l2a`) | Element84 Earth Search STAC (`sentinel-2-l2a`) + Copernicus Data Space OData | `PASS (200 OK)` | `402.8 ms` (PC) / `356.8 ms` (E84) | 4 / 4 |
| **Historical Water Validation** | JRC Global Surface Water via Planetary Computer STAC (`jrc-gsw`) | JRC Google/EC direct tile archive | `PASS (200 OK)` | `331.2 ms` | 4 / 4 |
| **Daily Rainfall (`PRECTOTCORR`)** | NASA POWER Agroclimatology Daily API | Open-Meteo Historical Weather API (ERA5/IMD-calibrated) | `PASS (200 OK)` | `874.4 ms` | 4 / 4 |
| **Groundwater & Subsurface Wetness** | India-WRIS CGWB Groundwater Level API (`/Dataset/Ground Water Level`) | NASA POWER Root-Zone & Profile Soil Wetness (`GWETROOT`, `GWETPROF`) | `PASS (200 OK)` | `609.3 ms` (WRIS) / `891.2 ms` (POWER) | 4 / 4 |
| **Water-Body Boundaries** | OpenStreetMap Nominatim GeoJSON Polygon API (`polygon_geojson=1`) | Satellite MNDWI/JRC-derived maximum extent polygon (`source=derived`) | `PASS (200 OK)` | `516.1 ms` | 3 / 4 OSM (`Polygon`), 1 / 4 (`derived` fallback) |

---

## 2. Detailed Findings per Source

### 2.1 Sentinel-2 L2A Optical Imagery

- **Primary (`https://planetarycomputer.microsoft.com/api/stac/v1/search`):**
  - Returned HTTP `200 OK` across all 4 pilot tanks (`MGRS` tiles `44PMV`, `44PLV`, `44PLU`).
  - Confirmed presence of required Cloud-Optimized GeoTIFF (COG) band assets on every scene: `B03` (Green, 10 m), `B08` (NIR, 10 m), `B11` (SWIR1, 20 m), and `SCL` (Scene Classification Layer, 20 m).
  - Sample scenes verified:
    - `TN-KPM-001`: `S2A_MSIL2A_20241230T050221_R119_T44PMV_20241230T080646` (`eo:cloud_cover = 49.18%`)
    - `TN-CGL-001`: `S2A_MSIL2A_20241230T050221_R119_T44PLU_20241230T080646` (`eo:cloud_cover = 88.84%`)
    - `TN-KPM-002` & `TN-CGL-002`: `S2A_MSIL2A_20241230T050221_R119_T44PLV_20241230T080646` (`eo:cloud_cover = 87.06%`)
- **Fallbacks Verified:**
  1. **Element84 Earth Search AWS STAC (`https://earth-search.aws.element84.com/v1/search`):** Returned HTTP `200 OK` in `356.8 ms` (`S2A_44PLV_20241230_0_L2A`) with unauthenticated COG band access.
  2. **Copernicus Data Space Ecosystem OData (`https://catalogue.dataspace.copernicus.eu/odata/v1/Products`):** Returned HTTP `200 OK` (`S2A_MSIL1C_20240105T050211_N0510_R119_T44PLV_20240105T064258.SAFE`). Note that Copernicus's experimental STAC endpoint (`stac.dataspace.copernicus.eu/v1`) only indexes CCM commercial/contributing missions, whereas Sentinel-2 is served via OData on CDSE and via STAC COGs on Planetary Computer and Element84.
- **Mitigation:** Configure `packages/geo` STAC client with **Planetary Computer STAC** as primary and **Element84 Earth Search STAC** as automatic anonymous COG fallback.

### 2.2 JRC Global Surface Water (`jrc-gsw`)

- **Endpoint:** `https://planetarycomputer.microsoft.com/api/stac/v1/search` (`collections=["jrc-gsw"]`).
- **Result:** HTTP `200 OK` for all 4 tanks (`80E_20Nv1_3_2020` and `70E_20Nv1_3_2020`).
- **Assets verified:** `occurrence`, `extent` (historical maximum water extent), `seasonality`, `recurrence`, `change`, and `transitions`.
- **Usage in EriWatch:** `occurrence` and `extent` rasters will validate our Sentinel-2 NDWI/MNDWI water masks in Stage 2 (Step 2.6) and provide long-term baseline masks for encroachment/shrinkage detection in Stage 5 (Step 5.7).

### 2.3 Daily Rainfall (`NASA POWER` / IMD Grid)

- **Endpoint:** `https://power.larc.nasa.gov/api/temporal/daily/point` (`parameters=PRECTOTCORR,T2M`, `community=AG`).
- **Result:** HTTP `200 OK` across all 4 tanks (~`874 ms`).
- **Sample Output (Oct 1–15, 2024 Northeast Monsoon onset):**
  - `TN-KPM-001` & `TN-KPM-002`: `175.16 mm` over 15 days (`2024-10-03`: `7.28 mm`).
  - `TN-CGL-001` & `TN-CGL-002`: `156.76 mm` over 15 days (`2024-10-03`: `6.71 mm`).
- **Gap & Mitigation:** IMD's direct public web portal uses session-gated HTML forms/NetCDF binary downloads rather than a JSON REST API per coordinate. NASA POWER `PRECTOTCORR` (MERRA-2 / GPM gauge-calibrated daily precipitation in `mm/day`) provides a reliable, unauthenticated JSON REST API for any `(lat, lon)` coordinate from 1981 to near-real-time.

### 2.4 Groundwater Level (`India-WRIS CGWB` + `NASA POWER Subsurface`)

- **India-WRIS Endpoint:** `POST https://indiawris.gov.in/Dataset/Ground%20Water%20Level`
  - **Result:** HTTP `200 OK` (`609.3 ms`), returning official Central Ground Water Board (CGWB) station telemetry in Kancheepuram/Chengalpattu (`stationCode: "TNGW0029"`, `stationName: "PUDUPATTINAM"`, `latitude: 12.5035`, `longitude: 80.1547`, and `stationCode: "CGWBTN45"`, `stationName: "Ponmar KATTANKOLATHUR"`).
- **Gap & Mitigation:** CGWB piezometer stations are sparse (block-level rather than one sensor inside every village tank) and occasionally have multi-week reporting lags. We pair nearest-station CGWB groundwater levels (`m bgl`) with continuous daily **NASA POWER Root-Zone & Profile Soil Wetness (`GWETROOT`, `GWETPROF`)** at each tank's exact centroid (`mean_profile_wetness = 0.689` in Kancheepuram, `0.578` in Chengalpattu) so ML features in Stage 5 never suffer from missing groundwater covariates.

### 2.5 OpenStreetMap Water-Body Boundaries

- **Findings:**
  - Public Overpass interpreter instances (`overpass-api.de`, `overpass.kumi.systems`) experienced high load / read timeouts (`>15 s`) on bounding-box queries during testing.
  - Conversely, **OpenStreetMap Nominatim GeoJSON API (`https://nominatim.openstreetmap.org/search?format=geojson&polygon_geojson=1`)** returned exact OSM `Polygon` geometries in `412–555 ms` for named tanks (`Chembarambakkam Lake` → `way/25453624`, `Thenneri Lake` → `way/831047472`, `Kolavai Lake` → `way/24161888`).
  - For tanks where a specific spelling is not indexed in Nominatim (e.g., `Madurantakam Lake` vs `Maduranthakam Eri`) or where rural tanks lack a closed OSM way, we digitise/derive the boundary polygon from historical maximum water extent (`source: "derived"`) and commit the complete GeoJSON registry (`data/processed/tank_registry.geojson`) into git in Step 1.3 so downstream stages never depend on live Overpass uptime.
