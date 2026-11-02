# Micro-Review: Concern 5 — 30-Document Spot-Check, Relevance Audit, and RAG Role Tagging

## Scope of Work
Addressed User Correction 5 on the legal corpus:
1. **100% Spot-Check Across All 30 Documents:** Verified Title, Issuer, and Date on Page 1 / Preamble against `data/raw/legal/manifest.json`. Documented results in `docs/data/legal_corpus_spotcheck.md` with explicit per-document `PASS/FAIL`.
2. **Detailed Relevance Audit for LEGAL-012, 013, 014, and 015:**
   - **LEGAL-012 (G.O. Ms. No. 96, RD&PR 2019):** Tagged `core`. Direct statutory guidelines for rejuvenating minor irrigation tanks under Kudimaramath convergence, mandating desilting of water-spread area, bund revetment, surplus weir/sluice reconstruction, and clearance of cascading feeder channels.
   - **LEGAL-013 (G.O. Ms. No. 97, RD&PR 2016):** Tagged `supporting`. Operational mechanics for minor irrigation tank desilting under MGNREGS, specifying excavation depths, silt application on farmers' fields under Rule 12(2-A), and desilting order of priority.
   - **LEGAL-014 (G.O. Ms. No. 23, RD&PR 2024):** Tagged `supporting`. Updated 2024 guidelines for rural water bodies and minor irrigation works, mandating public display of FTL / water spread, prohibiting non-water dumpings, and fixing BDO grievance accountability.
   - **LEGAL-015 (L.C. Jain Report Chapter 4.3, 1997):** Tagged `supporting`. Landmark commission analysis on Minor Irrigation and Water Management devolution under Section 133 of the Tamil Nadu Panchayats Act 1994, affirming minor irrigation tanks (<40 ha ayacut) as non-alienable commons.
3. **Corpus-Wide RAG Role Tiering:** Tagged every entry in `manifest.json` with `rag_role`:
   - `core`: 9 documents (30.0%) — binding statutory acts and landmark Supreme Court / High Court precedents on water body protection, FTL, and eviction.
   - `supporting`: 19 documents (63.3%) — operational schemes, guidelines, water user rules, pollution acts.
   - `background`: 2 documents (6.7%) — hydrogeological baseline brochure and Easements Act riparian rights.

## Verification Commands & Recorded Results
1. **Manifest Integrity & RAG Role Distribution Tests:**
   Command: `uv run pytest packages/rag/tests/test_corpus_manifest.py -m "not network" -v`
   Result: `3 passed in 1.15s` (validates `rag_role` in `REQUIRED_MANIFEST_FIELDS`, 9 core, 19 supporting, 2 background, and specific roles for LEGAL-012 through 015).

2. **Lint and Formatting:**
   Command: `uv run ruff check packages/rag && uv run ruff format --check packages/rag`
   Result: All checks passed.
