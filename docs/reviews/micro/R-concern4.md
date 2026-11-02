# Micro-Review: Corrective Stage R — Concern 4 (`is_extract` and `as_enacted` Flags)

- **Goal:** Add `is_extract` and `as_enacted` boolean flags to `LegalCorpusEntry` schema and `manifest.json`, accurately mark LEGAL-005 and LEGAL-006 as extracts, update their titles, and distinguish principal as-enacted statutory texts from executive orders and judgments.
- **Files Modified:**
  - `packages/rag/src/eriwatch_rag/corpus_manifest.py`
  - `data/raw/legal/manifest.json`
  - `packages/rag/tests/test_corpus_manifest.py`

## Summary of Changes
1. **`is_extract` Flag**:
   - Explicitly marks excerpted documents:
     - `LEGAL-005`: "The Tamil Nadu Panchayats Act, 1994 (Excerpts — Water Supply, Sanitation and Minor Irrigation Provisions)" (`is_extract: true`)
     - `LEGAL-006`: "Water Policy for Tamil Nadu, 1994 (Policy Statement Excerpts as published by PWD)" (`is_extract: true`)
     - `LEGAL-011`: "The Tamil Nadu District Municipalities Act, 1920 (Excerpts — Water Supply, Drainage and Public Water Sources)" (`is_extract: true`)
     - `LEGAL-015`: "L.C. Jain High Level Committee Report on Devolution of Powers to Panchayat Raj Institutions (Chapter 4.3: Minor Irrigation and Water Management Excerpts)" (`is_extract: true`)
     - `LEGAL-022`: "The Indian Easements Act, 1882 (Excerpts — Riparian and Surface Water Rights Provisions)" (`is_extract: true`)
   - All 25 other complete documents marked `is_extract: false`.
2. **`as_enacted` Flag**:
   - Identifies whether the document represents statutory text as originally enacted without subsequent consolidated amendments:
     - All 14 statutory Acts and Rules (`LEGAL-001`, `002`, `003`, `004`, `005`, `007`, `008`, `009`, `010`, `011`, `018`, `020`, `021`, `022`) are marked `as_enacted: true`.
     - Executive Government Orders (`LEGAL-012`, `013`, `014`, `016`), administrative guidelines (`LEGAL-017`, `019`), and court judgments (`LEGAL-024` through `LEGAL-030`) are marked `as_enacted: false`.
3. **Verification**:
   - `test_corpus_manifest.py` verifies both fields are present and populated across all 30 documents.

## Verdict
`PASS` — Excerpt status and enactment authenticity fields explicitly documented across the legal corpus.
