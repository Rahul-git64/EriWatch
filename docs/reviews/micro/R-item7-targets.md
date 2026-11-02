# Micro-Review: Item 7 — Stage 2 Measurable Performance Targets in ADR-0005

## Scope of Work
Addressed User Requirement 7:
1. **Target Specification in ADR-0005 Section 6**:
   - Formally documented the four quantitative measurable targets governing the Stage 2 geospatial extraction and water-spread pipeline:
     1. **Mean IoU (Intersection over Union)**: $\ge 0.75$ across all validation benchmark tanks ($\ge 0.70$ on small tanks $<20\text{ ha}$ with high littoral vegetation). Evaluated against independent 10-tank manual benchmark dataset and JRC GSW seasonal extents.
     2. **Mean Relative Area Error**: $\le 15.0\%$ relative absolute error ($|\Delta \text{Area}| / \text{Area}_{\text{true}}$) across clear-sky passes.
     3. **Usable Observations per Tank per Season**: $\ge 15$ observations per tank during the Northeast Monsoon (Oct 15 – Jan 15); $\ge 4$ observations per month in dry season, achieved via optical + Sentinel-1 SAR fusion.
     4. **Maximum Monsoon Observation Gap**: $\le 12$ calendar days maximum gap during the cloudy Northeast Monsoon, eliminating historical 30–45 day optical blind spots.
2. **Explicit Stop for User Alignment**:
   - Standing by for explicit user approval (`APPROVED TARGETS`) before executing Stage 2 implementation.

## Verification
- Targets defined in `docs/adr/0005-water-spread-measurement-and-quality-flags.md` Section 6.
- `make lint` and `make test` pass cleanly.
