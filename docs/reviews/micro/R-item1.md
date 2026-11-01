# Micro-Review: Corrective Stage R — Item 1 (Historical Maximum Extent Specification)

- **Goal:** Document the exact methodology for establishing historical maximum extent for shrinkage analysis (percentile composite method + 10-tank manual review protocol) in `ADR-0004`.
- **Files Modified:** `docs/adr/0004-legal-corpus-storage-sar-fusion-and-validation-design.md`

## Summary of Changes
1. **Rationale & Problem Statement (§4.1):** Explained why single-date traced polygons cannot serve as shrinkage baselines (captures instantaneous filling state rather than hydrological capacity).
2. **Multi-Year Percentile Composite Method (§4.2):** Formally specified the dual-source fusion:
   - Pixel-wise 95th percentile ($P_{95}$) NDWI composite over all cloud-screened ($<15\%$ SCL cloud/shadow) post-monsoon passes (Oct 15 – Jan 31) from 2019 to 2024.
   - Fusion with 38-year JRC Global Surface Water Maximum Water Extent raster (1984–2021) and morphological regularisation.
3. **Ten-Tank Manual Review Protocol (§4.3):** Specified the 10 pilot tanks (5 in Kancheepuram: `TN-KPM-001`, `002`, `003`, `005`, `010`; 5 in Chengalpattu: `TN-CGL-001`, `002`, `005`, `008`, `011`), inspection against cadastral/FMB FTL boundaries, and logging in `docs/data/manual_validation/max_extent_review.md`.
4. **Permanent Shrinkage Metric (§4.4):** Defined the mathematical formulation comparing historical maximum extent against 3-year rolling post-monsoon peak area, with a $>20\%$ loss threshold over 3 consecutive seasons.

## Verdict
`PASS` — Section 4 of ADR-0004 now comprehensively details the historical maximum extent methodology and 10-tank review protocol.
