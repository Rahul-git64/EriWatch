# ADR-0004: Legal Corpus Storage Strategy, Sentinel-1 SAR Fusion, and Independent Validation Architecture

## Status
Accepted

## Date
2026-11-02

## Context
During the Stage R audit, four structural concerns were identified across EriWatch's data and evaluation pipelines:

1. **Repository Bloat & Legal Corpus Storage (A1)**:
   The legal corpus contains 30 verified authentic PDF documents (~24.5 MB total). Tracking raw PDFs directly in Git bloats repository clone size, degrades `git fetch` performance, and couples version control with binary asset storage.
2. **Monsoon Cloud Blindness & SAR Necessity (A3)**:
   Analysis of 27,330 Sentinel-2 tank-scenes across 2019–2026 revealed that only 18.27% of scenes during the critical Northeast Monsoon (October–December) have `<20%` cloud cover. Relying solely on optical Sentinel-2 imagery would create blind spots lasting 3 to 6 weeks during peak inflow and flood hazard periods.
3. **Validation Independence & Circular Evaluation Risk (A4)**:
   Tank boundary polygons for 14 pilot tanks were traced from specific cloud-free Sentinel-2 NDWI scenes. Using these traced geometries as ground truth for water-spread validation would introduce circular reasoning and inflate evaluation metrics.
4. **Historical Maximum Extent Methodology (A5)**:
   A single-date traced polygon reflects the instantaneous water spread on that observation date, not the legal tank water spread boundary or historical maximum extent required for encroachment and shrinkage detection.

---

## Decisions

### 1. Legal Corpus Storage & Verification (A1)
- **Gitignore Raw PDFs**: All raw PDF binaries (`data/raw/legal/*.pdf`) are untracked and excluded from git tracking via `.gitignore`.
- **Manifest as Canonical Record**: `data/raw/legal/manifest.json` is committed to git as the canonical cryptographic ledger. It records the ID, title, issuer, date, language, official source URL, page count, and SHA-256 digest for every document.
- **Idempotent Automated Fetching**: A reproducible command `make fetch-legal` (backed by `eriwatch_rag.corpus_manifest --download --verify`) downloads the 30 PDFs from official sources on a fresh clone and verifies their SHA-256 digests against `manifest.json`. Any mismatch or banned hash fails the build.

### 2. Sentinel-1 SAR Fusion for Stage 2 (A3)
- **SAR Integration**: Sentinel-1 Radiometrically Terrain Corrected (RTC) C-Band SAR imagery from Microsoft Planetary Computer STAC (`sentinel-1-rtc`) IS an explicit component of the Stage 2 geospatial pipeline.
- **Licence & Access**: Open access under Copernicus Sentinel Data Policy via Planetary Computer STAC API (no paid API key required).
- **Water Detection Algorithm**:
  1. Extract both VV and VH polarisation backscatter amplitude ($dB$).
  2. Apply speckle noise reduction using a $3 \times 3$ or $5 \times 5$ median/Lee filter.
  3. Apply dual-polarisation backscatter thresholding (typically $VV < -15.5\text{ dB}$ and $VH < -23.0\text{ dB}$, calibrated against clear-sky optical passes) to segment open water surface.
- **Fusion Architecture**:
  - When a Sentinel-2 optical scene has cloud cover $\le 20\%$ within the tank bounding box, optical NDWI/MNDWI is the primary observation.
  - When cloud cover exceeds $20\%$, the pipeline queries the nearest Sentinel-1 SAR acquisition ($\pm 3$ days) and extracts the water-spread area.
  - Every database observation record is tagged with an explicit quality flag: `optical_clear`, `optical_partial_cloud`, `sar_only`, or `fused`.

### 3. Validation Independence Guarantee (A4)
- **Prohibition of Circular Validation**: Traced polygons from the tank registry are strictly prohibited from being used as ground truth for water-spread validation.
- **Independent Validation Sources**:
  1. **JRC Global Surface Water (GSW)**: Validated against JRC GSW Occurrence and Seasonality layers (30m spatial resolution).
  2. **Independent Manual Sample**: A curated benchmark dataset of at least 10 tanks (`docs/data/manual_validation/`) with pixel-level ground truth manually annotated from high-resolution satellite imagery on dates and scenes completely distinct from the scenes used for registry tracing.

### 4. Historical Maximum Extent Methodology (A5)

#### 4.1 Rationale & Problem Statement
A single-date traced polygon reflects only the instantaneous water surface on that specific satellite overpass date. Depending on whether that pass occurred in a drought year, mid-monsoon, or post-monsoon, the traced area may represent as little as 30% or as much as 100% of the true hydrological water-spread capacity. Using instantaneous polygons as the benchmark for shrinkage or encroachment would yield severe false-positive or false-negative alarms. Therefore, an objective, multi-year historical maximum extent must be established for each tank.

#### 4.2 Multi-Year Percentile Composite Method
The baseline historical maximum extent is computed through a dual-source remote sensing fusion:
1. **Sentinel-2 Multi-Year $P_{95}$ NDWI Composite**:
   - **Temporal Scope**: 2019–2024 post-monsoon observation windows (October 15 through January 31 of each water year).
   - **Quality Filtering**: Only Sentinel-2 L2A scenes with SCL cloud/shadow mask $< 15\%$ across the tank bounding box + 500 m buffer are admitted.
   - **Spectral Index**: Green/NIR Normalized Difference Water Index:
     $$\text{NDWI} = \frac{\text{B03} - \text{B08}}{\text{B03} + \text{B08}}$$
   - **Temporal Aggregation**: For each 10 m pixel within the buffered bounding box, the 95th percentile ($P_{95}$) NDWI value across all admitted scenes is computed. Taking $P_{95}$ rather than the maximum ($P_{100}$) eliminates residual cloud edge artifacts, sun glint, and single-pass sensor anomalies while capturing peak flood/monsoon water levels.
   - **Segmentation**: An Otsu adaptive threshold is applied to the $P_{95}$ raster (clamped to $[0.0, 0.2]$) to generate the empirical maximum water mask.
2. **JRC Global Surface Water (GSW) Maximum Water Extent Layer**:
   - The JRC GSW Maximum Water Extent raster (representing 38 years of surface water detection from 1984 to 2021 at 30 m resolution) is clipped to each tank's buffered catchment.
   - The fused historical maximum extent polygon is the union of the JRC GSW Maximum Extent and the Sentinel-2 $P_{95}$ water mask, regularized using morphological opening (radius 1 pixel) to eliminate spurious isolated pixels.

#### 4.3 Ten-Tank Manual Review Protocol
To ground-truth and calibrate the automated maximum-extent methodology, an explicit manual audit is conducted on 10 representative pilot tanks:
- **Kancheepuram District (5 major irrigation tanks)**:
  1. `TN-KPM-001` — Madurantakam Eri (largest tank in the district, 988.7 ha)
  2. `TN-KPM-002` — Uthiramerur Eri (major historical system tank, 442.2 ha)
  3. `TN-KPM-003` — Tenneri Eri (385.1 ha)
  4. `TN-KPM-005` — Damal Eri (231.5 ha)
  5. `TN-KPM-010` — Walajabad Eri (115.4 ha)
- **Chengalpattu District (5 peri-urban and urban-interface tanks)**:
  6. `TN-CGL-001` — Perumbakkam Lake (peri-urban wetland interface, 102.3 ha)
  7. `TN-CGL-002` — Nanmangalam Lake (forest-adjacent peri-urban tank, 68.4 ha)
  8. `TN-CGL-005` — Sembakkam Lake (dense urban fringe, 45.2 ha)
  9. `TN-CGL-008` — Keelkattalai Lake (flood-moderating wetland, 52.8 ha)
  10. `TN-CGL-011` — Thiruporur Periya Eri (historical coastal temple tank, 84.6 ha)

**Protocol Steps**:
1. For each of the 10 tanks, overlay the fused $P_{95}$ / JRC maximum extent against high-resolution optical imagery (Sentinel-2 10 m RGB, Google/Bing aerial basemaps) and available Tamil Nadu Survey & Settlement / FMB (Field Measurement Book) Full Tank Level (FTL) revenue boundaries.
2. Measure discrepancy between nominal registry area and fused maximum extent. If discrepancy exceeds $\pm 15\%$, identify whether the difference stems from bund expansion, foreshore siltation, or upstream seasonal marshes.
3. Record visual inspection notes, before/after boundary plots, and verified FTL coordinates in `docs/data/manual_validation/max_extent_review.md`.
4. Surface any proposed polygon adjustments to the user for explicit approval before modifying the production registry.

#### 4.4 Shrinkage and Encroachment Metric
Permanent loss is formally decoupled from seasonal dry-downs:
$$\text{Permanent Loss (\%)} = \frac{\text{Historical Maximum Extent (ha)} - \text{Peak Area}_{3\text{-yr rolling post-monsoon (ha)}}}{\text{Historical Maximum Extent (ha)}} \times 100\%$$
- **Shrinking Flag**: Triggered only when $\text{Permanent Loss} > 20\%$ for 3 consecutive post-monsoon seasons (November–January), confirming irreversible hydrological capacity reduction or bund encroachment rather than weather-driven drought.

---

## Consequences

### Positive
- Clones remain lightweight (<15 MB) without multi-megabyte PDF binaries.
- All 30 legal documents are cryptographically verifiable from original official URLs.
- The monitoring system maintains continuous water-spread time series through the cloudy Northeast Monsoon.
- Water-spread evaluation metrics are honest, rigorous, and completely decoupled from polygon tracing artifacts.

### Trade-offs & Mitigations
- `make fetch-legal` requires network access during setup if legal PDFs are needed locally. (Mitigated by graceful handling in offline test suites where synthetic fixtures are used).
- Sentinel-1 SAR can suffer from wind-induced surface roughness and emergent vegetation backscatter. (Mitigated by dual-polarisation VV/VH ratio analysis and speckle filtering).
