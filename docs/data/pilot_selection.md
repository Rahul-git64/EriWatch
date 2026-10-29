# Pilot Tank Selection Criteria & Verified Cohort (`R2.1–R2.4`)

## 1. Regional Rationale

EriWatch focuses its verified pilot cohort on **35 irrigation tanks (*eris*)** across **Kancheepuram** (17 tanks) and **Chengalpattu** (18 tanks) districts in northern Tamil Nadu (`12.52°N – 13.02°N, 79.64°E – 80.22°E`). This region was selected for four reasons:

1. **Hydrological & Flood Criticality:** The Adyar, Palar, and Ongur river sub-basins contain dense cascading tank chains (*system* and *non-system* tanks) that buffer Northeast Monsoon floodwaters entering the southern Chennai Metropolitan Area while irrigating *Samba* and *Navarai* paddy crops.
2. **Ground-Truth Accessibility:** Located within 10–75 km of SAI University (Paiyanur / OMR, Chengalpattu District), allowing direct physical verification of tank bunds, sluices, and encroachment patterns.
3. **Sentinel-2 Tile Efficiency:** All 35 tanks fall within three adjacent Sentinel-2 MGRS tiles (`44PLV`, `44PLU`, and `44PMV`), minimizing STAC metadata queries while maximizing temporal revisit consistency (5-day revisit with Sentinel-2A/2B/2C).
4. **Diversity of Urbanisation & Hydrological Stress:** Spans peri-urban IT-corridor and suburban tanks facing real-estate pressure alongside large rural agricultural system tanks.

---

## 2. Stage R Audit & Verification Summary (`R2.1–R2.4`)

### 2.1 Audit of Stage 1 Commit `9b8e68c` (`R2.1`)
In Stage 1 commit `9b8e68c`, `packages/geo/src/eriwatch_geo/registry.py` used a synthetic 16-vertex geometric formula (`_build_crescent_tank_polygon`) for all 36 tanks. That function has been deleted, and every tank polygon in `data/processed/tank_registry.geojson` is now obtained from one of two real, reproducible geospatial sources:
- **OpenStreetMap Extraction (`source = "osm"`, `confidence = "high"`, 21 tanks):** Extracted verbatim from OpenStreetMap (`https://api.openstreetmap.org/api/0.6/{way|relation}/{osm_id}/full.json`) using `fetch_osm_polygon()`.
- **Sentinel-2 L2A NDWI Water-Mask Tracing (`source = "derived"`, `confidence = "medium"`, 14 tanks):** Traced directly from post-monsoon Sentinel-2 L2A 10 m `B03` (Green) and `B08` (NIR) Cloud-Optimized GeoTIFFs (`2026-02-08`, `NDWI = (B03 - B08) / (B03 + B08) >= 0.01`) via `rasterio.features.shapes` and `shapely` using `trace_sentinel2_ndwi_polygon()`.

### 2.2 Reproducible Method & Command for All 14 `"derived"` Tanks (`R2.1`)

| ID | Tank Name | Sentinel-2 Scene ID | Tracing Method | Vertices | Geodesic Area | Confidence | Reproducible Command |
|---|---|---|---|---|---|---|---|
| `TN-KPM-005` | Parandur Periya Eri | `S2B_44PLV_20260208_0_L2A` | `NDWI >= 0.01` (`B03`,`B08` 10 m COG) | 105 | 41.10 ha | `medium` | `uv run python -m eriwatch_geo.registry --trace-tank TN-KPM-005` |
| `TN-KPM-010` | Nemili / Navalur Eri (Sriperumbudur) | `S2B_44PLV_20260208_0_L2A` | `NDWI >= 0.01` (`B03`,`B08` 10 m COG) | 94 | 55.95 ha | `medium` | `uv run python -m eriwatch_geo.registry --trace-tank TN-KPM-010` |
| `TN-KPM-011` | Sunguvarchatram Molachur Eri | `S2B_44PLV_20260208_0_L2A` | `NDWI >= 0.01` (`B03`,`B08` 10 m COG) | 59 | 14.41 ha | `medium` | `uv run python -m eriwatch_geo.registry --trace-tank TN-KPM-011` |
| `TN-KPM-012` | Vaiyavoor Chitheri | `S2B_44PLV_20260208_0_L2A` | `NDWI >= 0.01` (`B03`,`B08` 10 m COG) | 66 | 41.10 ha | `medium` | `uv run python -m eriwatch_geo.registry --trace-tank TN-KPM-012` |
| `TN-KPM-016` | Oragadam Vaipoor Eri | `S2B_44PLV_20260208_0_L2A` | `NDWI >= 0.01` (`B03`,`B08` 10 m COG) | 54 | 21.23 ha | `medium` | `uv run python -m eriwatch_geo.registry --trace-tank TN-KPM-016` |
| `TN-KPM-017` | Padappai Karasangal Eri | `S2B_44PLV_20260208_0_L2A` | `NDWI >= 0.01` (`B03`,`B08` 10 m COG) | 69 | 41.13 ha | `medium` | `uv run python -m eriwatch_geo.registry --trace-tank TN-KPM-017` |
| `TN-KPM-018` | Edamichi Periya Eri | `S2B_44PLU_20260208_0_L2A` | `NDWI >= 0.01` (`B03`,`B08` 10 m COG) | 119 | 23.51 ha | `medium` | `uv run python -m eriwatch_geo.registry --trace-tank TN-KPM-018` |
| `TN-CGL-005` | Manivakkam / Urapakkam Eri | `S2B_44PLV_20260208_0_L2A` | `NDWI >= 0.01` (`B03`,`B08` 10 m COG) | 65 | 26.29 ha | `medium` | `uv run python -m eriwatch_geo.registry --trace-tank TN-CGL-005` |
| `TN-CGL-010` | Siruseri Navalur Eri | `S2B_44PMV_20260208_0_L2A` | `NDWI >= 0.01` (`B03`,`B08` 10 m COG) | 54 | 24.99 ha | `medium` | `uv run python -m eriwatch_geo.registry --trace-tank TN-CGL-010` |
| `TN-CGL-011` | Kelambakkam Padur Eri | `S2B_44PMV_20260208_0_L2A` | `NDWI >= 0.01` (`B03`,`B08` 10 m COG) | 65 | 22.14 ha | `medium` | `uv run python -m eriwatch_geo.registry --trace-tank TN-CGL-011` |
| `TN-CGL-014` | Paiyanur Eri (Near SAI Univ) | `S2B_44PLV_20260208_0_L2A` | `NDWI >= 0.01` (`B03`,`B08` 10 m COG) | 151 | 74.60 ha | `medium` | `uv run python -m eriwatch_geo.registry --trace-tank TN-CGL-014` |
| `TN-CGL-015` | Manamai / Kunnathur Eri | `S2B_44PLV_20260208_0_L2A` | `NDWI >= 0.01` (`B03`,`B08` 10 m COG) | 117 | 27.40 ha | `medium` | `uv run python -m eriwatch_geo.registry --trace-tank TN-CGL-015` |
| `TN-CGL-017` | Kuzhipanthandalam Eri | `S2B_44PLV_20260208_0_L2A` | `NDWI >= 0.01` (`B03`,`B08` 10 m COG) | 143 | 77.63 ha | `medium` | `uv run python -m eriwatch_geo.registry --trace-tank TN-CGL-017` |

### 2.3 Health Label Audit (`R2.2`)
In Stage 1 commit `9b8e68c`, the pilot tanks were assigned `healthy`, `seasonal`, and `shrinking` labels before any Stage 2 multi-year Sentinel-2 water-spread time series had been measured. Per Integrity Rule 2, all 35 active tanks are now set to `state_archetype = "unverified"` until empirical water-spread time series and shrinkage metrics are computed in Stage 2 and Stage 4.

### 2.4 Sentinel-2 RGB + NDWI Water-Mask Overlay Verification (`R2.3 & R2.4`)
We ran `uv run python -m eriwatch_geo.overlay_check` across all 36 candidate tanks (`docs/data/overlays/overlay_summary.json`):
- **35 of 36 tanks (`97.2%`)** visibly and quantitatively matched an active open-water body on the `2026-02-08` Sentinel-2 L2A scenes (`inside_water_ratio` from **30.7% to 99.1%**, `inside_water_px` from **650 to 193,672** 10 m pixels).
- **1 of 36 tanks (`TN-KPM-013`, Nathapettai Eri, `way/34108726`, `111.44 ha`)** failed the `>= 15%` open-water NDWI check (`inside_water_ratio = 9.0%`, `9.96 ha` open water; see [`docs/data/overlays/TN-KPM-013.png`](overlays/TN-KPM-013.png)), because the tank bed is bisected by the NH48 highway causeway and its northern basin is covered by dense emergent macrophytes (`NDWI < 0`).
- Per **R2.3 & R2.4**, `TN-KPM-013` has been dropped from the active pilot registry, bringing the verified pilot cohort to **35 tanks** (`17` Kancheepuram, `18` Chengalpattu; `35 >= 30` minimum requirement), with **100% (`35 / 35`)** passing the Sentinel-2 overlay check.

---

## 3. Verified Pilot Cohort Table (35 Tanks)

| ID | Tank Name | District | Block | Centroid (`lat, lon`) | Area (ha) | State Archetype | Source | Confidence | OSM Element | S2 Water Overlap (`2026-02-08`) | Overlay PNG |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `TN-KPM-001` | Chembarambakkam Periya Eri | Kancheepuram | Kundrathur | `13.008220, 80.055489` | 1991.29 | `unverified` | `osm` | `high` | `way/25453624` | 1936.72 ha (97.3%) | [`TN-KPM-001.png`](overlays/TN-KPM-001.png) |
| `TN-KPM-002` | Thenneri Hissa Eri | Kancheepuram | Walajabad | `12.851600, 79.885503` | 43.27 | `unverified` | `osm` | `high` | `way/34108738` | 24.81 ha (57.5%) | [`TN-KPM-002.png`](overlays/TN-KPM-002.png) |
| `TN-KPM-003` | Sriperumbudur Periya Eri | Kancheepuram | Sriperumbudur | `12.967178, 79.934356` | 278.94 | `unverified` | `osm` | `high` | `way/34108765` | 204.16 ha (73.2%) | [`TN-KPM-003.png`](overlays/TN-KPM-003.png) |
| `TN-KPM-004` | Uthiramerur Vaikunda Perumal Eri | Kancheepuram | Uthiramerur | `12.623749, 79.736060` | 100.44 | `unverified` | `osm` | `high` | `way/117698592` | 99.62 ha (99.1%) | [`TN-KPM-004.png`](overlays/TN-KPM-004.png) |
| `TN-KPM-005` | Parandur Periya Eri | Kancheepuram | Kancheepuram | `12.930752, 79.760544` | 41.10 | `unverified` | `derived` | `medium` | `—` | 40.32 ha (98.0%) | [`TN-KPM-005.png`](overlays/TN-KPM-005.png) |
| `TN-KPM-006` | Kundrathur Periya Eri | Kancheepuram | Kundrathur | `13.012842, 80.097520` | 58.73 | `unverified` | `osm` | `high` | `way/178751060` | 30.78 ha (52.5%) | [`TN-KPM-006.png`](overlays/TN-KPM-006.png) |
| `TN-KPM-007` | Manimangalam Eri | Kancheepuram | Kundrathur | `12.903737, 80.037853` | 122.84 | `unverified` | `osm` | `high` | `way/26188360` | 121.62 ha (99.0%) | [`TN-KPM-007.png`](overlays/TN-KPM-007.png) |
| `TN-KPM-008` | Somangalam Eri | Kancheepuram | Kundrathur | `12.946344, 80.040718` | 25.45 | `unverified` | `osm` | `high` | `way/383852845` | 22.26 ha (87.6%) | [`TN-KPM-008.png`](overlays/TN-KPM-008.png) |
| `TN-KPM-009` | Pillaipakkam Eri | Kancheepuram | Sriperumbudur | `12.993620, 79.979867` | 21.19 | `unverified` | `osm` | `high` | `way/38424012` | 6.50 ha (30.7%) | [`TN-KPM-009.png`](overlays/TN-KPM-009.png) |
| `TN-KPM-010` | Nemili / Navalur Eri (Sriperumbudur) | Kancheepuram | Sriperumbudur | `12.945761, 79.993448` | 55.95 | `unverified` | `derived` | `medium` | `—` | 55.20 ha (98.8%) | [`TN-KPM-010.png`](overlays/TN-KPM-010.png) |
| `TN-KPM-011` | Sunguvarchatram Molachur Eri | Kancheepuram | Sriperumbudur | `12.877923, 79.869874` | 14.41 | `unverified` | `derived` | `medium` | `—` | 13.86 ha (96.5%) | [`TN-KPM-011.png`](overlays/TN-KPM-011.png) |
| `TN-KPM-012` | Vaiyavoor Chitheri | Kancheepuram | Kancheepuram | `12.840291, 79.738863` | 41.10 | `unverified` | `derived` | `medium` | `—` | 39.15 ha (95.5%) | [`TN-KPM-012.png`](overlays/TN-KPM-012.png) |
| `TN-KPM-014` | Mamandur Vadakku Eri | Kancheepuram | Kancheepuram | `12.751576, 79.647382` | 1291.20 | `unverified` | `osm` | `high` | `relation/16179862` | 1086.73 ha (84.2%) | [`TN-KPM-014.png`](overlays/TN-KPM-014.png) |
| `TN-KPM-015` | Damal Periya Eri | Kancheepuram | Kancheepuram | `12.905823, 79.750763` | 29.15 | `unverified` | `osm` | `high` | `way/34108732` | 28.44 ha (97.7%) | [`TN-KPM-015.png`](overlays/TN-KPM-015.png) |
| `TN-KPM-016` | Oragadam Vaipoor Eri | Kancheepuram | Walajabad | `12.849977, 79.948756` | 21.23 | `unverified` | `derived` | `medium` | `—` | 20.08 ha (95.2%) | [`TN-KPM-016.png`](overlays/TN-KPM-016.png) |
| `TN-KPM-017` | Padappai Karasangal Eri | Kancheepuram | Kundrathur | `12.875214, 80.026177` | 41.13 | `unverified` | `derived` | `medium` | `—` | 39.87 ha (97.3%) | [`TN-KPM-017.png`](overlays/TN-KPM-017.png) |
| `TN-KPM-018` | Edamichi Periya Eri | Kancheepuram | Uthiramerur | `12.566679, 79.784082` | 23.51 | `unverified` | `derived` | `medium` | `—` | 22.27 ha (94.9%) | [`TN-KPM-018.png`](overlays/TN-KPM-018.png) |
| `TN-CGL-001` | Madurantakam Periya Eri | Chengalpattu | Madurantakam | `12.525171, 79.875534` | 690.59 | `unverified` | `osm` | `high` | `way/176519614` | 543.53 ha (78.8%) | [`TN-CGL-001.png`](overlays/TN-CGL-001.png) |
| `TN-CGL-002` | Kolavai Lake (Chengalpattu) | Chengalpattu | Kattankolathur | `12.707142, 79.988345` | 567.25 | `unverified` | `osm` | `high` | `way/24161888` | 475.53 ha (83.9%) | [`TN-CGL-002.png`](overlays/TN-CGL-002.png) |
| `TN-CGL-003` | Ponneri / Maraimalai Nagar Eri | Chengalpattu | Kattankolathur | `12.795929, 80.032283` | 41.04 | `unverified` | `osm` | `high` | `way/102309331` | 26.17 ha (63.8%) | [`TN-CGL-003.png`](overlays/TN-CGL-003.png) |
| `TN-CGL-004` | Guduvancheri Nandhivaram Eri | Chengalpattu | Kattankolathur | `12.833654, 80.077605` | 84.02 | `unverified` | `osm` | `high` | `way/384854734` | 58.25 ha (69.3%) | [`TN-CGL-004.png`](overlays/TN-CGL-004.png) |
| `TN-CGL-005` | Manivakkam / Urapakkam Eri | Chengalpattu | Kattankolathur | `12.879729, 80.058771` | 26.29 | `unverified` | `derived` | `medium` | `—` | 24.83 ha (94.6%) | [`TN-CGL-005.png`](overlays/TN-CGL-005.png) |
| `TN-CGL-006` | Madambakkam / Sembakkam Eri | Chengalpattu | St. Thomas Mount | `12.910336, 80.165300` | 36.56 | `unverified` | `osm` | `high` | `relation/17972561` | 21.87 ha (59.9%) | [`TN-CGL-006.png`](overlays/TN-CGL-006.png) |
| `TN-CGL-007` | Chitlapakkam Eri | Chengalpattu | St. Thomas Mount | `12.934286, 80.136295` | 20.11 | `unverified` | `osm` | `high` | `way/23648229` | 16.38 ha (81.5%) | [`TN-CGL-007.png`](overlays/TN-CGL-007.png) |
| `TN-CGL-008` | Perumbakkam / Medavakkam West Eri | Chengalpattu | St. Thomas Mount | `12.896961, 80.189026` | 66.45 | `unverified` | `osm` | `high` | `way/30424450` | 50.97 ha (76.6%) | [`TN-CGL-008.png`](overlays/TN-CGL-008.png) |
| `TN-CGL-009` | Sholinganallur / Perumbakkam East Eri | Chengalpattu | St. Thomas Mount | `12.909513, 80.216759` | 19.56 | `unverified` | `osm` | `high` | `way/595615732` | 16.48 ha (84.2%) | [`TN-CGL-009.png`](overlays/TN-CGL-009.png) |
| `TN-CGL-010` | Siruseri Navalur Eri | Chengalpattu | Thiruporur | `12.837270, 80.198221` | 24.99 | `unverified` | `derived` | `medium` | `—` | 23.60 ha (94.9%) | [`TN-CGL-010.png`](overlays/TN-CGL-010.png) |
| `TN-CGL-011` | Kelambakkam Padur Eri | Chengalpattu | Thiruporur | `12.802095, 80.212621` | 22.14 | `unverified` | `derived` | `medium` | `—` | 21.01 ha (95.4%) | [`TN-CGL-011.png`](overlays/TN-CGL-011.png) |
| `TN-CGL-012` | Thaiyur Periya Eri | Chengalpattu | Thiruporur | `12.778009, 80.183445` | 163.02 | `unverified` | `osm` | `high` | `way/30425446` | 63.44 ha (38.9%) | [`TN-CGL-012.png`](overlays/TN-CGL-012.png) |
| `TN-CGL-013` | Thiruporur Periya Eri | Chengalpattu | Thiruporur | `12.728084, 80.159807` | 44.08 | `unverified` | `osm` | `high` | `way/641992830` | 41.93 ha (95.3%) | [`TN-CGL-013.png`](overlays/TN-CGL-013.png) |
| `TN-CGL-014` | Paiyanur Eri (Near SAI Univ) | Chengalpattu | Thiruporur | `12.682833, 80.146665` | 74.60 | `unverified` | `derived` | `medium` | `—` | 72.93 ha (97.9%) | [`TN-CGL-014.png`](overlays/TN-CGL-014.png) |
| `TN-CGL-015` | Manamai / Kunnathur Eri | Chengalpattu | Tirukalukundram | `12.597532, 80.141838` | 27.40 | `unverified` | `derived` | `medium` | `—` | 26.26 ha (95.9%) | [`TN-CGL-015.png`](overlays/TN-CGL-015.png) |
| `TN-CGL-016` | Tirukalukundram Kondangi Eri | Chengalpattu | Tirukalukundram | `12.641407, 80.056329` | 38.06 | `unverified` | `osm` | `high` | `way/642028874` | 22.42 ha (58.9%) | [`TN-CGL-016.png`](overlays/TN-CGL-016.png) |
| `TN-CGL-017` | Kuzhipanthandalam Eri | Chengalpattu | Tirukalukundram | `12.662268, 80.139658` | 77.63 | `unverified` | `derived` | `medium` | `—` | 75.73 ha (97.6%) | [`TN-CGL-017.png`](overlays/TN-CGL-017.png) |
| `TN-CGL-018` | Karunguzhi Eri | Chengalpattu | Madurantakam | `12.537374, 79.899018` | 30.77 | `unverified` | `osm` | `high` | `way/117698722` | 27.94 ha (90.7%) | [`TN-CGL-018.png`](overlays/TN-CGL-018.png) |
