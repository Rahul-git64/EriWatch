"""Tests for legal corpus integrity (`packages/rag`)."""

from pathlib import Path

from eriwatch_rag.corpus_manifest import (
    BANNED_GENERATED_SHA256S,
    compute_file_sha256,
    load_legal_manifest,
)


def test_no_generated_pdfs_exist_in_legal_corpus() -> None:
    """Ensure none of the 28 agent-generated PDFs from commit 859c32a exist in data/raw/legal."""
    legal_dir = Path("data/raw/legal")
    assert legal_dir.exists()

    for pdf_path in legal_dir.glob("*.pdf"):
        digest = compute_file_sha256(pdf_path)
        assert digest not in BANNED_GENERATED_SHA256S, (
            f"Generated file {pdf_path.name} ({digest}) must not exist in production corpus"
        )

    entries = load_legal_manifest(legal_dir / "manifest.json")
    for entry in entries:
        assert entry.sha256 not in BANNED_GENERATED_SHA256S
