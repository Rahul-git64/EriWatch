"""Tests for Stage 1 Step 1.6 legal corpus PDFs and manifest (`packages/rag`)."""

from pathlib import Path

from pypdf import PdfReader

from eriwatch_rag.corpus_manifest import build_legal_corpus, load_legal_manifest


def test_legal_corpus_has_at_least_25_documents_with_valid_pdfs() -> None:
    """Verify >=25 legal PDFs and manifest entries exist and parse cleanly with pypdf."""
    legal_dir = Path("data/raw/legal")
    entries = build_legal_corpus(legal_dir)
    assert len(entries) >= 25
    assert len(entries) == 28

    loaded = load_legal_manifest(legal_dir / "manifest.json")
    assert len(loaded) == 28

    categories = {e.category for e in loaded}
    assert "WRD Government Order" in categories
    assert "Kudimaramath Guideline" in categories
    assert "Madras High Court Judgment" in categories
    assert "NGT Southern Zone Order" in categories

    for entry in loaded:
        pdf_path = legal_dir / entry.filename
        assert pdf_path.exists(), f"Missing PDF {pdf_path}"
        reader = PdfReader(str(pdf_path))
        assert len(reader.pages) == 2
        p1_text = reader.pages[0].extract_text()
        p2_text = reader.pages[1].extract_text()
        assert entry.doc_id in p1_text
        assert "CLAUSE 1:" in p2_text
