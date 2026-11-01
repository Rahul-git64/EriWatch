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
- **Shrinkage Baseline**: Historical maximum extent for each tank is established using:
  1. The **JRC Global Surface Water Maximum Water Extent** raster layer (representing 1984–2021 maximum surface water extent).
  2. A multi-year composite of the wettest clean Sentinel-2 passes (the 95th percentile NDWI surface over 2019–2024 post-monsoon passes).
  3. Manual boundary review of 10 pilot tanks comparing cadastral revenue survey boundaries against satellite maximum water spread.
- **Permanent Shrinkage Metric**: Calculated as the percentage area deficit between the verified historical maximum extent and the rolling 3-year peak post-monsoon water spread.

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
