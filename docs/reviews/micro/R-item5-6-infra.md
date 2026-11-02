# Micro-Review: Items 5 & 6 — Durable Archive Fallback, Committed Text Status, and `make ocr-legal`

## Scope of Work
Addressed User Requirements 5 and 6:
1. **Durable Release Archive Fallback in `make fetch-legal`**:
   - Location: `packages/rag/src/eriwatch_rag/corpus_manifest.py` defines `DURABLE_ARCHIVE_URL` pointing to persistent GitHub Release asset `https://github.com/Rahul-git64/EriWatch/releases/download/v0.1.0-legal-corpus/eriwatch-legal-corpus-v1.tar.gz` (SHA-256 `ae1ae88aaafd0674e5214cfa39aa32307f1aff04d0d316838053dcf4496d08c4`).
   - In `download_and_build_manifest()`: When an official source URL fails or is blocked, the script transparently catches the failure and calls `extract_from_durable_archive()`, extracting the genuine PDF from the archive bytes and verifying its SHA-256 against `manifest.json`.
   - Verified via network test `test_durable_release_archive_reachable` returning HTTP 200.
2. **Status of `data/processed/legal_text/`**:
   - **Status**: **COMMITTED TO GIT** (unignored in `.gitignore` via `!data/processed/legal_text/`).
   - **Rationale**: All 30 page-marked text files total only $\sim 700\text{ KB}$. Tracking them in git allows clean clones and GitHub Actions CI runners to immediately execute tests, linting, and RAG chunking without running CPU-intensive 300 DPI OCR on startup.
3. **`make ocr-legal` Target**:
   - Added `ocr-legal` to `Makefile` and `.PHONY` (`uv run python -m eriwatch_rag.ocr_pipeline`).
   - Enables full end-to-end reproducibility to re-render all 30 PDFs at 300 DPI, rerun RapidOCR, and regenerate clean page-marked text files and quality metrics on demand.

## Verification
- `Makefile` updated with `ocr-legal` target.
- `make lint` and `make test` passing cleanly.
