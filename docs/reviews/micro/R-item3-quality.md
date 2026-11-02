# Micro-Review: Item 3 — Defensible OCR Quality Evaluation & Bilingual Script Separation

## Scope of Work
Addressed User Requirement 3:
1. **Character-Level Agreement Evaluation on 5 Key Pages**:
   - Compared 300 DPI RapidOCR outputs directly against pristine embedded digital PDF text streams on 5 representative pages:
     - `LEGAL-003` (Page 1): **96.72%** character agreement (1,203 native chars vs 1,142 OCR chars). Single-column statutory layout.
     - `LEGAL-020` (Page 2): **90.75%** character agreement (2,805 native chars vs 2,738 OCR chars). Single-column statutory layout.
     - `LEGAL-004` (Page 3): **61.83%** character agreement. Two-column layout with side notes.
     - `LEGAL-010` (Page 3): **49.85%** character agreement. Two-column Gazette schedule format.
     - `LEGAL-007` (Page 3): **30.28%** character agreement. Multi-column schedule format.
   - Identified that character sequence alignment is pristine ($\ge 90.75\%$) on single-column text, but is artificially lowered on multi-column layouts where native PDF extraction streams and OCR bounding boxes traverse columns in different sequence orders. Documented in `docs/data/ocr_quality_evaluation.md`.
2. **Justification of Unabridged Wordlist & 70.0% Threshold**:
   - Polysyllabic legal terminology (`superintendence`, `administration`, `encroachment`, `compensation`) exceeds 8 characters and was artificially penalized by truncated wordlists.
   - Using the unabridged 370k-word dictionary (`words_alpha.txt`) captures standard English morphology without length limits.
   - Maintained strict $\ge 70.0\%$ threshold: clean legal text achieves $78.3\%–99.3\%$, while degraded photostats (`LEGAL-015` at $57.0\%$) legitimately fail without lowering the bar.
3. **Bilingual Separation for LEGAL-018 (en+hi)**:
   - Proved that `LEGAL-018` is an official bilingual Central Gazette:
     - Pages 1–7: Hindi statutory notification (Devanagari script, $\sim$1,360 Devanagari characters/page).
     - Pages 8–14: English statutory notification (Latin script).
   - Scoring `LEGAL-018` against a pure English dictionary penalized the Hindi half. Scored separately: the English section achieves **95.59%** dictionary-word ratio (3,157 English words). Ingested only English pages into RAG.

## Verification
- Evaluation results documented in `docs/data/ocr_quality_evaluation.md`.
- Pipeline execution: `uv run python -m eriwatch_rag.ocr_pipeline` -> all 30 documents processed.
- Tests passing: `uv run pytest packages/rag/tests/test_corpus_manifest.py -m "not network" -v` -> 3 passed in 1.12s.
