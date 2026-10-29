# Stage 1 / Stage R Feasibility Report: External Data Sources (`R3.1–R3.2`)

- **Executed At:** `2026-10-29T17:50:49Z`
- **Command:** `uv run python -m eriwatch_geo.feasibility_spike`
- **Raw Evidence Artifact:** [`data/raw/samples/feasibility_spike.json`](../../data/raw/samples/feasibility_spike.json)

---

## 1. Honest Assessment: Which Sources Worked Fully, Partly, or Not at All

| Data Source / Endpoint | Outcome (`FULL` / `PARTIAL` / `FAILED`) | Real Payload Evidence Measured | Failure Mode / Limitation Observed | Engineering Mitigation Adopted |
|---|---|---|---|---|
| **1. Microsoft Planetary Computer STAC (`sentinel-2-l2a`)** | **WORKED FULLY** | `70–71` scenes/tank in 2024 (`11` scenes `<20%` cloud, `22–24` scenes `<40%` cloud, mean cloud cover `58.9%–59.7%`); `B03`, `B08`, `B11`, `SCL` verified | Anonymous SAS signing (`/api/sas/v1/sign`) rate-limits (`HTTP 429`) if called per-band without caching the container SAS token | Cache container SAS token per collection/run; use **Element84 Earth Search STAC** (`s3://sentinel-cogs`) for unauthenticated direct COG reads |
| **2. Element84 Earth Search AWS STAC (`sentinel-2-l2a`)** | **WORKED FULLY** | `72` scenes in 2024 for `TN-KPM-001`; unauthenticated direct `rasterio` windowed reads of 10 m COGs (`B02`, `B03`, `B04`, `B08`) | None observed; fastest unauthenticated COG endpoint | Used alongside Planetary Computer as co-primary STAC + COG provider |
| **3. Copernicus Data Space Ecosystem (CDSE)** | **WORKED PARTLY** | OData endpoint (`/odata/v1/Products`) returned `5` `.SAFE` product bundles (`2024-01-05`, `2024-01-10`) in `6.94 s` | CDSE's experimental STAC endpoint (`stac.dataspace.copernicus.eu/v1`) does not index standard Sentinel-2 L2A COGs, and OData serves monolithic `.SAFE` archives requiring OAuth2 rather than windowed COG reads | Do not use CDSE OData for windowed pixel reads; use Planetary Computer STAC + Element84 Earth Search COGs |
| **4. JRC Global Surface Water (`jrc-gsw` via Planetary Computer)** | **WORKED FULLY** | Sampled real 30 m pixel values at all 4 tank centroids via `rasterio`: `occurrence = 48%–83%`, `extent = 1`, `seasonality = 4–12 months` | Requires appending a Planetary Computer SAS query string (`?st=...&se=...&sig=...`) from `/api/sas/v1/sign` before opening COGs in `rasterio` | Cache the JRC container SAS token once per batch run and read 30 m windows via `rasterio` |
| **5. NASA POWER Agroclimatology (`PRECTOTCORR`, `GWETROOT`, `GWETPROF`)** | **WORKED FULLY** | Returned complete 15-day daily rainfall series (`2024-10-01`..`2024-10-15`, peak `69.18 mm` on `2024-10-15`) and 10-day root/profile soil wetness (`0.57–0.70`) | Coarse spatial resolution (`0.5° × 0.625°` MERRA-2/GPM grid), so nearby tanks in the same district share grid cells | Combine grid rainfall with tank-specific historical water-spread lag and storage-capacity features in Stage 4/5 |
| **6. Direct IMD Public Portal REST API** | **DID NOT WORK (NO JSON REST API)** | No unauthenticated per-coordinate JSON REST API exists on `imd.gov.in` / `imdpune.gov.in` (HTML session forms and binary `.grd` files only) | Cannot be queried per-tank via standard REST JSON in automated workflows | Use **NASA POWER `PRECTOTCORR`** (satellite + gauge-calibrated daily precipitation, `mm/day`) as primary daily rainfall source |
| **7. India-WRIS / CGWB Groundwater API (`/Dataset/Ground Water Level`)** | **WORKED PARTLY** | Returned `500` telemetry rows across **25 unique CGWB piezometer stations** in Kancheepuram/Chengalpattu (`-0.47 m` to `-7.51 m bgl`; nearest stations `2.56 km` to `13.50 km` from our sample tanks) | 1) Pre-2019 district split means Chengalpattu stations are indexed under `districtName="Kancheepuram"`; 2) Wide date ranges (`>1 year`) return 200+ 6-hourly rows for a single station (`KANC38`) on page 0; 3) Station density is block-level (`2.5–13.5 km` to tanks) | Query `districtName="Kancheepuram"` over 5-day windows (`size=500`) to capture all 25 stations, map each tank to its nearest CGWB piezometer by WGS84 geodesic distance, and pair with continuous daily **NASA POWER `GWETPROF`** |
| **8. OpenStreetMap Nominatim (`polygon_geojson=1`)** | **WORKED PARTLY (`3 / 4` Polygons)** | Returned full `Polygon` rings for `TN-KPM-001` (`218` vertices), `TN-CGL-001` (`41` vertices), and `TN-CGL-002` (`486` vertices) | For `TN-KPM-002` (`Thenneri, Walajabad`), Nominatim matched the village settlement `node/14271507163` (`Point`, `1` vertex) instead of the adjacent water body `way/34108738` | Do not rely on Nominatim text search alone: extract water polygons directly by `way/<id>` or `relation/<id>` via **OSM REST API v0.6** (`45` vertices for `way/34108738`), and trace unmapped rural tanks directly from **Sentinel-2 L2A NDWI** (`R2.1`) |

---

## 2. Quantitative Payload Evidence per Source (`data/raw/samples/feasibility_spike.json`)

### 2.1 Sentinel-2 L2A STAC Inventory & Cloud Cover (Full Year 2024)

| Tank ID | Tank Name | 2024 Total Scenes | Scenes `< 20%` Cloud | Scenes `< 40%` Cloud | Mean Cloud Cover (%) | Min / Max Cloud (%) | Date Range Verified | Required Bands (`B03`,`B08`,`B11`,`SCL`) |
|---|---|---|---|---|---|---|---|---|
| `TN-KPM-001` | Chembarambakkam Periya Eri | `70` | `11` | `24` | `59.21%` | `0.001%` / `100.0%` | `2024-01-05` .. `2024-12-30` | `true` |
| `TN-CGL-001` | Madurantakam Periya Eri | `70` | `11` | `22` | `58.90%` | `0.008%` / `100.0%` | `2024-01-05` .. `2024-12-30` | `true` |
| `TN-KPM-002` | Thenneri Hissa Eri | `71` | `11` | `24` | `59.65%` | `0.001%` / `100.0%` | `2024-01-05` .. `2024-12-30` | `true` |
| `TN-CGL-002` | Kolavai Lake (Chengalpattu) | `70` | `11` | `24` | `59.43%` | `0.001%` / `100.0%` | `2024-01-05` .. `2024-12-30` | `true` |

### 2.2 JRC Global Surface Water (`jrc-gsw`) Pixel Values Sampled at Tank Centroids

| Tank ID | Tank Name | JRC Tile ID | Centroid (`lon, lat`) | Centroid Occurrence (`0–100%`) | 5×5 Patch Max Occurrence (`%`) | Max Extent Flag (`0/1`) | Seasonality (`1–12` months/yr) |
|---|---|---|---|---|---|---|---|
| `TN-KPM-001` | Chembarambakkam Periya Eri | `80E_20Nv1_3_2020` | `80.055489, 13.008220` | **`77%`** | `78%` | `1` | `12` months |
| `TN-CGL-001` | Madurantakam Periya Eri | `70E_20Nv1_3_2020` | `79.875534, 12.525171` | **`48%`** | `50%` | `1` | `4` months |
| `TN-KPM-002` | Thenneri Hissa Eri | `70E_20Nv1_3_2020` | `79.885503, 12.851600` | **`60%`** | `62%` | `1` | `12` months |
| `TN-CGL-002` | Kolavai Lake (Chengalpattu) | `70E_20Nv1_3_2020` | `79.988345, 12.707142` | **`83%`** | `83%` | `1` | `12` months |

### 2.3 NASA POWER Daily Rainfall (`PRECTOTCORR`, `2024-10-01` to `2024-10-15`)

| Tank ID | Days Returned | 15-Day Cumulative Rain (`mm`) | Peak Rain Date | Peak Daily Rain (`mm`) | Sample Daily Values (`mm`) |
|---|---|---|---|---|---|
| `TN-KPM-001` | `15` | `175.16 mm` | `2024-10-15` | `69.18 mm` | `10-03: 7.28`, `10-11: 8.53`, `10-14: 43.95`, `10-15: 69.18` |
| `TN-CGL-001` | `15` | `156.76 mm` | `2024-10-15` | `54.88 mm` | `10-03: 6.71`, `10-11: 9.88`, `10-14: 31.51`, `10-15: 54.88` |
| `TN-KPM-002` | `15` | `175.16 mm` | `2024-10-15` | `69.18 mm` | `10-03: 7.28`, `10-11: 8.53`, `10-14: 43.95`, `10-15: 69.18` |
| `TN-CGL-002` | `15` | `156.76 mm` | `2024-10-15` | `54.88 mm` | `10-03: 6.71`, `10-11: 9.88`, `10-14: 31.51`, `10-15: 54.88` |

### 2.4 India-WRIS CGWB Groundwater Stations & Geodesic Distance to Each Tank

- **Total Unique CGWB Stations Parsed (`2024-01-01`..`2024-01-05`):** `25` stations (`KANC36`, `KANC38`..`KANC46`, `KANC403`..`KANC405`, `TNGW0017`, `TNGW0023`, `TNGW0024`, `TNGW0029`..`TNGW0031`, `CGWBTN45`..`CGWBTN49`).

| Tank ID | Tank Name | Nearest CGWB Station Code | Nearest Station Name | Station (`lat, lon`) | Distance to Tank (`km`) | Reading (`m bgl`) | Reading Timestamp | NASA POWER `GWETPROF` (10-d mean) |
|---|---|---|---|---|---|---|---|---|
| `TN-KPM-001` | Chembarambakkam Periya Eri | `CGWBTN49` | Kunnattur Sriperumbudur | `13.0027, 80.0992` | **`4.78 km`** | `-5.122 m` | `2024-01-05T18:00:00` | `0.689` |
| `TN-CGL-001` | Madurantakam Periya Eri | `KANC41` | Maduranthakam_1 | `12.5083, 79.8917` | **`2.56 km`** | `-0.520 m` | `2024-01-02T00:00:00` | `0.578` |
| `TN-KPM-002` | Thenneri Hissa Eri | `CGWBTN47` | Panruti Kandigai Sriperumbudur | `12.8506, 79.9119` | **`2.87 km`** | `-2.654 m` | `2024-01-05T18:00:00` | `0.689` |
| `TN-CGL-002` | Kolavai Lake (Chengalpattu) | `KANC43` | Vadakkupattu pz | `12.8181, 79.9367` | **`13.50 km`** | `-0.990 m` | `2024-01-05T18:00:00` | `0.578` |

### 2.5 OpenStreetMap Nominatim vs. Direct OSM REST API v0.6 Geometry Vertex Counts

| Tank ID | Nominatim Query | Nominatim Geometry Type | Nominatim Vertex Count | Direct OSM API v0.6 Element | OSM API v0.6 Vertex Count | Geodesic Area (`ha`) |
|---|---|---|---|---|---|---|
| `TN-KPM-001` | `Chembarambakkam Lake, Tamil Nadu` | `Polygon` | `218` | `way/25453624` | **`218`** | `1991.29 ha` |
| `TN-CGL-001` | `Lake Maduranthakam, Tamil Nadu` | `Polygon` | `41` | `way/176519614` | **`41`** | `690.57 ha` |
| `TN-KPM-002` | `Thenneri, Walajabad, Tamil Nadu` | `Point` (village node) | `1` | `way/34108738` | **`45`** | `43.27 ha` |
| `TN-CGL-002` | `Kolavai Lake, Chengalpattu` | `Polygon` | `486` | `way/24161888` | **`486`** | `567.25 ha` |
