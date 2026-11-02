# Micro-Review: Concern 3 — OCR Pipeline, Text Quality Metrics, and Quality Gate

## Scope of Work
Addressed User Correction 3 on the legal corpus:
1. **Re-OCR Scanned & Low-Quality Documents at 300 DPI:** Implemented `packages/rag/src/eriwatch_rag/ocr_pipeline.py` using `pypdfium2` (300 DPI page rendering) and `rapidocr-onnxruntime` (offline deep learning OCR).
2. **Page-Marked Clean Legal Text:** Extracted and saved clean text with explicit `--- Page N ---` page delimiters under `data/processed/legal_text/LEGAL-*.txt` for all 30 documents.
3. **Resolved Garbled LEGAL-001 Page 3:** Re-OCR'd `LEGAL-001` (Tamil Nadu Protection of Tanks and Eviction of Encroachment Act, 2007) from 300 DPI page renders. Recovered clean, readable text for Section 2(d),(e),(o) Full Tank Level definitions, Section 4 (Survey Officers), Section 5 (Powers), Section 6 (Survey Report), Section 7 (Eviction of Encroachment), and Section 8 (Offences and Penalties).
4. **Dictionary-Word Ratio Quality Gate:** Integrated comprehensive 370,105-word offline English dictionary (`packages/rag/src/eriwatch_rag/wordlist.txt`) plus regional irrigation terminology (`ayacut`, `kudimaramath`, `poramboke`, `oorani`, `weir`, `sluice`, `FTL`).
5. **Quality Gate Threshold:** Defined `quality_gate = "PASS" if dictionary_word_ratio >= 0.70 and word_count >= 50 else "FAIL"`.

## Verification Commands & Recorded Results
1. **Pipeline Execution:**
   Command: `uv run python -m eriwatch_rag.ocr_pipeline`
   Result: Processed all 30 documents; 29 documents PASS the quality gate with dictionary-word ratios between 78.3% and 99.3%.
   - `LEGAL-001` [ocr_300dpi]: 1,445 words, 93.6% dictionary ratio (Gate: PASS).
   - `LEGAL-002` [ocr_300dpi]: 6,623 words, 78.3% dictionary ratio (Gate: PASS).
   - `LEGAL-006` [ocr_300dpi]: 1,195 words, 93.4% dictionary ratio (Gate: PASS).
   - `LEGAL-012` [ocr_300dpi]: 1,106 words, 95.0% dictionary ratio (Gate: PASS).
   - `LEGAL-013` [ocr_300dpi]: 4,101 words, 94.3% dictionary ratio (Gate: PASS).
   - `LEGAL-014` [ocr_300dpi]: 4,539 words, 95.5% dictionary ratio (Gate: PASS).
   - `LEGAL-015` [ocr_300dpi]: 782 words, 57.0% dictionary ratio (Gate: FAIL due to degraded 1997 typewriter photostat scan; reported honestly).
   - `LEGAL-003..005, 007..011, 016..030` [native_text_layer]: 90.6%–99.3% dictionary ratios (all Gate: PASS).

2. **Automated Unit Tests:**
   Command: `uv run pytest packages/rag/tests/test_corpus_manifest.py -m "not network" -v`
   Result: `3 passed in 1.13s` (validates manifest schema, metadata corrections, text quality, page markers, and Section 2/4-8 resolution).

3. **Code Quality:**
   Command: `uv run ruff check packages/rag && uv run ruff format --check packages/rag`
   Result: All checks passed.
