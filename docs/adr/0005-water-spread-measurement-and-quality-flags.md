# ADR-0005: Water Spread Measurement Methodology, Connected Components, and Geospatial Quality Flags

## Status
Accepted

## Date
2026-11-02

## Context
During the Stage R pilot registry audit and visual overlay review of the 14 pilot tanks against Sentinel-2 imagery, several critical geospatial boundary anomalies were identified:
1. **Loose Polygons**: OSM / traced boundaries in tanks `TN-CGL-001` (Perumbakkam), `TN-CGL-004` (Thaiyur), `TN-CGL-006` (Vandalur), and `TN-CGL-009` (Kelambakkam) are loose and encompass dry perimeter embankments, adjacent roads, or residential edges.
2. **Water Extending Outside Polygon**: In `TN-CGL-001` (Perumbakkam), `TN-CGL-009` (Kelambakkam), `TN-CGL-010` (Siruseri Navalur), and `TN-CGL-011` (Thiruporur Periya Eri), post-monsoon water spread routinely extends beyond the nominal polygon into connected foreshore marshes, inlet channels, or adjoining wetland patches.
3. **Clipping Risk**: If the water segmentation pipeline strictly clips raster masks to the nominal polygon, water that genuinely belongs to the eri's hydrological body is arbitrarily truncated, skewing surface area measurements and falsely masking expansion or boundary disputes.
4. **Adjacent Water Merging**: In dense wetland complexes, high-water states can cause the water mask of the target tank to merge with neighboring borrow pits, aquaculture ponds, or adjacent tanks.

---

## Decisions

### 1. Water Spread Measurement Algorithm
Water spread area shall **NOT** be measured by strictly clipping water pixels to the nominal polygon. Instead, the Stage 2 geospatial extraction pipeline will use a **buffered connected-component** method:
1. **Polygon Buffer**: Expand the nominal tank polygon by a calibrated buffer distance ($D_{\text{buffer}} = 200\text{ m}$) to define the extraction Region of Interest (ROI).
2. **Water Mask Generation**: Segment water pixels within the buffered ROI using the optical NDWI/MNDWI threshold or Sentinel-1 SAR backscatter threshold.
3. **Connected Components Analysis**: Run connected-component labelling (8-connectivity) on the segmented water raster.
4. **Target Component Intersection**: Retain only those connected water components that **intersect or touch the unbuffered nominal tank polygon**. Spurious isolated water bodies (unconnected farm ponds or roadside puddles within the 200 m buffer) are automatically discarded.
5. **Surface Area Computation**: Sum the area of all retained connected water components:
   $$\text{Area}_{\text{water}} = N_{\text{pixels}} \times (\text{Pixel Resolution})^2$$

### 2. Statutory Legal Boundary & FTL Proxy
Under the Tamil Nadu Protection of Tanks and Eviction of Encroachment Act, 2007 (Act 8 of 2007, Section 2(d), (e), and (o)):
- The statutory boundary of the eri is the **Full Tank Level (FTL)** water spread area (the water level up to the crest of the surplus weir, plus upstream foreshore areas).
- The satellite-derived historical maximum extent is explicitly defined as an **empirical remote-sensing proxy** for this statutory FTL boundary.
- Shrinkage metrics compare current water extents against this proxy to establish permanent capacity loss versus seasonal variance.

### 3. Geospatial Quality Flags
Every satellite observation processed by the pipeline will be tagged with automated quality flags:
- `optical_clean`: Cloud cover $< 20\%$, water fully within normal extent.
- `needs_review`: Flagged whenever:
  - The measured connected water mask extends significantly ($> 20\%$ by area) beyond the nominal polygon boundary.
  - The connected component touches the outer buffer boundary, indicating potential merging with an adjacent water body, urban canal, or neighboring tank.
  - The nominal polygon is known to be loose or misaligned.
- `sar_fallback`: Sentinel-1 SAR used due to optical cloud obstruction.
- `cloud_masked`: Excessive cloud cover without valid optical or SAR observation.

### 4. Pilot Tanks Flagged for Manual Review
The following 6 pilot tanks are flagged as `needs_review` based on overlay audit findings:
- `TN-CGL-001` (Perumbakkam Lake): Loose southern boundary; post-monsoon water extends east into connected wetland interface.
- `TN-CGL-004` (Thaiyur Eri): Loose northern contour along highway.
- `TN-CGL-006` (Vandalur Eri): Embankment boundary includes dry scrub along railway.
- `TN-CGL-009` (Kelambakkam Eri): Loose boundary; water extends outside nominal polygon into southern feeder swamp.
- `TN-CGL-010` (Siruseri Navalur Eri / Navalur Lake):
  - **Site Identity & Project Sources**: Corresponds to Navalur Periya Eri (~33.43 acres), situated within the SIPCOT IT Park in Siruseri, Thiruporur taluk, Chengalpattu district. Rejuvenated by the State Industries Promotion Corporation of Tamil Nadu (SIPCOT) at an estimated ₹30 crore as the "Navalur Lake Eco Park" (*Namma Navalur*, [nammanavalur.com](https://nammanavalur.com); covered in regional press regarding eco-restoration and local concerns over peripheral filling along original wetland margins).
  - **Unverified Status**: Satellite imagery displays distinctive circular features and bright green reflectance. However, specific claims regarding "aeration islands" and "seasonal algal blooms" have no logged field sensor data and are formally marked **`unverified`** in both registry notes and this ADR. Water extends into southern drainage/park channels during post-monsoon passes. The polygon geometry is retained strictly unchanged.
- `TN-CGL-011` (Thiruporur Periya Eri): Coastal low-gradient tank where water spills into western inflow marsh.

### 5. Geometry Integrity Standing Policy
**No polygon geometry in `data/processed/tank_registry.geojson` will be altered without explicit user review and approval.**
During Stage 2, candidate polygon corrections will be generated as separate geo-layers (`data/interim/candidate_boundaries/`) and presented to the user with overlay comparison plots before any updates to the production registry are committed.

### 6. Stage 2 Quantitative Performance Targets (Measurable Gates)
To ensure the Stage 2 geospatial extraction pipeline is rigorous, defensible, and objectively verifiable, the following four quantitative criteria are formally established:

| Metric | Target Specification | Measurement Method & Ground Truth |
|---|---|---|
| **Mean IoU (Intersection over Union)** | $\ge \mathbf{0.75}$ across all benchmark tanks ($\ge 0.70$ on small tanks $<20\text{ ha}$) | Evaluated pixel-by-pixel against the 10-tank independent manual validation dataset (`docs/data/manual_validation/`) and JRC Global Surface Water seasonal extent masks. |
| **Mean Relative Area Error** | $\le \mathbf{15.0\%}$ ($|\text{Area}_{\text{pred}} - \text{Area}_{\text{true}}| / \text{Area}_{\text{true}}$) | Computed across all cloud-free validation passes against manual digitized benchmark extents. |
| **Usable Observations per Tank per Season** | $\ge \mathbf{15}$ observations per tank during the Northeast Monsoon (Oct 15 – Jan 15); $\ge \mathbf{4}$ obs/month in dry season | Combined optical (Sentinel-2 L2A with SCL valid pixel fraction $\ge 80\%$) and Sentinel-1 SAR RTC backscatter observations. |
| **Maximum Monsoon Observation Gap** | $\le \mathbf{12}$ calendar days | Maximum gap between consecutive valid water-spread measurements during peak monsoon (Oct–Dec), bridged by Sentinel-1 SAR 6-to-12 day repeat passes. |

---

## Consequences

### Positive
- Prevents artificial truncation of tank water spread during high-monsoon fill periods.
- Rejects unconnected roadside ponds and distant water bodies within the catchment buffer.
- Provides automated data quality alerts (`needs_review`) for hydrologists and municipal engineers.
- Strictly adheres to Tamil Nadu Act 8 of 2007 definitions while maintaining honest remote sensing boundaries.
- Preserves auditability: no geometries are modified behind the user's back.

### Negative
- Connected components analysis adds a modest computational overhead (~50–100 ms per tank scene).
- In extreme flood events, merging with adjacent lakes requires human review via the `needs_review` flag.
