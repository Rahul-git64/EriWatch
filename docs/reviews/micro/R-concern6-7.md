# Micro-Review: Concerns 6 & 7 — Gazette Verification Notice and Statutory FTL Shrinkage Boundary

## Scope of Work
Addressed User Corrections 6 and 7:
1. **Mandatory Gazette Verification Notice in ADR-0004 (Concern 6):**
   - Added explicit policy clause to `ADR-0004` Section 1.
   - Mandates that all LLM-generated petition and complaint drafts must carry a prominent statutory verification notice:
     *"NOTICE: This petition draft cites public statutory provisions as enacted and compiled from public archives. Ayacutdars, petitioners, and legal representatives must verify all cited clauses against the current Tamil Nadu Government Gazette text before formal submission to authorities."*
2. **Statutory Full Tank Level (FTL) Shrinkage Boundary (Concern 7):**
   - Added Section 4.1 in `ADR-0004` and Section 2 in `ADR-0005`.
   - Formally established the statutory legal boundary for water body protection and encroachment eviction under Section 2(d), (e), and (o) of the Tamil Nadu Protection of Tanks and Eviction of Encroachment Act, 2007 (Act 8 of 2007).
   - Formally designated multi-year satellite-derived historical maximum extent as an **empirical remote-sensing proxy** for this statutory FTL boundary.
3. **Stage 2 Geospatial Measurement & Quality Flag Architecture (ADR-0005):**
   - Defined buffered connected-component analysis ($D_{\text{buffer}} = 200\text{ m}$) intersecting nominal tank geometries to eliminate spurious external water bodies while avoiding artificial clipping.
   - Defined automated `needs_review` quality flag for observations extending beyond nominal bounds or merging into adjacent water bodies.
   - Catalogued candidate review tanks (`TN-CGL-001`, `004`, `006`, `009`, `010`, `011`) and established strict policy: no geometry changes without explicit user approval.

## Verification
- `docs/adr/0004-legal-corpus-storage-sar-fusion-and-validation-design.md` updated with Notice and FTL clauses.
- `docs/adr/0005-water-spread-measurement-and-quality-flags.md` authored and indexed in `docs/adr/README.md`.
