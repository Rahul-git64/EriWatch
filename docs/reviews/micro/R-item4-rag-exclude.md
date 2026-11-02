# Micro-Review: Item 4 — LEGAL-015 Status and RAG Exclusion Policy

## Scope of Work
Addressed User Requirement 4:
1. **Explicit Corpus Standing of LEGAL-015**:
   - `LEGAL-015` (`LEGAL-015_TNRD_Report_Maintenance_of_Minor_Irrigation_Tanks_and_Water_Bodies.pdf`, SHA-256 `91b59cebd1f14079c1a7fa8336897f0079c9217d393edc39363a0332d7247a7b`) is an authentic original download of Chapter 4.3 ("Minor Irrigation and Water Management") of the First High-Level Committee on Panchayat Raj Institutions (L.C. Jain Report, April 1997) from `www.tnrd.tn.gov.in`.
   - **Quality Gate Outcome**: Failed the automated dictionary-ratio quality gate at **57.0%** (below the 70.0% threshold) due to degraded typewriter photostat spacing where inter-word blanks are frequently lost or narrowed.
   - **Corpus Retention**: Retained in `data/raw/legal/` as a permanent primary record for historical provenance and devolution statutory principles under Section 133 of the Tamil Nadu Panchayats Act 1994.
2. **Strict RAG Corpus Exclusion**:
   - Added schema field `rag_excluded: bool` to `LegalCorpusEntry` and `data/raw/legal/manifest.json`.
   - Flagged `LEGAL-015` as `"rag_excluded": true` (all other 29 documents set to `false`).
   - Downstream Stage 8 RAG chunking and vector indexing pipelines will programmatically filter out any document where `rag_excluded == True`, ensuring degraded text never pollutes LLM generation context until a clean manual line-by-line transcription is integrated.

## Verification
- Manifest updated with `rag_excluded: true` on `LEGAL-015`.
- Unit test `test_specific_legal_metadata_corrections` in `packages/rag/tests/test_corpus_manifest.py` strictly asserts `entries["LEGAL-015"].rag_excluded is True` and all other documents `False`.
- `uv run pytest packages/rag/tests/test_corpus_manifest.py -m "not network" -v` -> 3 passed in 1.28s.
