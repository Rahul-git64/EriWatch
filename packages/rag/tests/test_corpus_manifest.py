"""Strict verification tests for the real legal corpus (`test_corpus_manifest.py`).

Tests Step R1.5 requirements:
1. At least 25 real documents in `data/raw/legal/manifest.json`.
2. All required fields present and non-empty (`id`, `filename`, `title`, `issuer`,
   `document_type`, `date`, `language`, `source_url`, `retrieved_at`, `sha256`,
   `page_count`, `licence_note`, `extraction_method`).
3. Durable GitHub release archive URL and SHA-256 recorded in manifest.
4. If files are on disk, `sha256` matches the actual file bytes and `page_count` matches.
5. `source_url` is a well-formed `https://` URL pointing to `.pdf`.
6. Neither the manifest nor any `.pdf` in `data/raw/legal/` is in `BANNED_GENERATED_SHA256S`.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

import httpx
import pytest
from pypdf import PdfReader

from eriwatch_rag.corpus_manifest import (
    BANNED_GENERATED_SHA256S,
    DURABLE_ARCHIVE_SHA256,
    DURABLE_ARCHIVE_URL,
    compute_file_sha256,
    load_legal_manifest,
    verify_legal_corpus,
)

REQUIRED_MANIFEST_FIELDS = {
    "id",
    "filename",
    "title",
    "issuer",
    "document_type",
    "date",
    "language",
    "source_url",
    "retrieved_at",
    "sha256",
    "page_count",
    "licence_note",
    "extraction_method",
    "gazette_date",
    "date_precision",
    "metadata_verified",
    "is_extract",
    "as_enacted",
    "rag_role",
}


def test_legal_corpus_manifest_required_fields_and_integrity() -> None:
    """Verify required fields, SHA-256, page_count, well-formed URL, and non-generated status."""
    legal_dir = Path("data/raw/legal")
    manifest_path = legal_dir / "manifest.json"
    assert manifest_path.exists(), "Missing data/raw/legal/manifest.json"

    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    docs = raw.get("documents", [])
    assert len(docs) >= 25, f"Expected >= 25 real legal documents, got {len(docs)}"
    assert raw.get("document_count") == len(docs)
    assert raw.get("archive_url") == DURABLE_ARCHIVE_URL
    assert raw.get("archive_sha256") == DURABLE_ARCHIVE_SHA256

    for doc in docs:
        missing = REQUIRED_MANIFEST_FIELDS - set(doc.keys())
        assert not missing, f"Document {doc.get('id')} missing fields: {missing}"

    entries = load_legal_manifest(manifest_path)
    assert len(entries) >= 25

    seen_ids: set[str] = set()
    seen_shas: set[str] = set()

    for entry in entries:
        assert entry.id not in seen_ids, f"Duplicate id {entry.id}"
        seen_ids.add(entry.id)

        assert entry.sha256 not in BANNED_GENERATED_SHA256S, (
            f"{entry.id} has banned synthetic SHA-256 {entry.sha256}"
        )
        assert entry.sha256 not in seen_shas, f"Duplicate file SHA-256 in {entry.id}"
        seen_shas.add(entry.sha256)

        parsed = urlparse(entry.source_url)
        assert parsed.scheme == "https", f"{entry.id} source_url must use https: {entry.source_url}"
        assert bool(parsed.netloc), f"{entry.id} source_url missing netloc: {entry.source_url}"
        assert parsed.path.lower().endswith(".pdf"), (
            f"{entry.id} source_url must point to a .pdf file: {entry.source_url}"
        )

        pdf_path = legal_dir / entry.filename
        if pdf_path.exists():
            assert pdf_path.stat().st_size > 10_000, (
                f"{entry.id} suspiciously small PDF ({pdf_path.stat().st_size} bytes)"
            )
            actual_sha = compute_file_sha256(pdf_path)
            assert actual_sha == entry.sha256, (
                f"{entry.id} SHA-256 mismatch: manifest={entry.sha256}, disk={actual_sha}"
            )
            reader = PdfReader(str(pdf_path))
            assert len(reader.pages) == entry.page_count, (
                f"{entry.id} page_count mismatch: manifest={entry.page_count}, pdf={len(reader.pages)}"
            )

    for disk_pdf in legal_dir.glob("*.pdf"):
        disk_sha = compute_file_sha256(disk_pdf)
        assert disk_sha not in BANNED_GENERATED_SHA256S, (
            f"Disk file {disk_pdf.name} matches banned synthetic SHA-256"
        )


def test_specific_legal_metadata_corrections() -> None:
    """Verify specific metadata corrections for LEGAL-002, LEGAL-003, and LEGAL-015."""
    manifest_path = Path("data/raw/legal/manifest.json")
    entries = {e.id: e for e in load_legal_manifest(manifest_path)}

    # LEGAL-002: Presidential assent date and Gazette date
    l002 = entries["LEGAL-002"]
    assert l002.date == "2001-02-25", f"LEGAL-002 expected assent 2001-02-25, got {l002.date}"
    assert l002.gazette_date == "2001-03-05", (
        f"LEGAL-002 expected gazette 2001-03-05, got {l002.gazette_date}"
    )
    assert l002.date_precision == "exact"
    assert l002.metadata_verified is True

    # LEGAL-003: Unverified G.O. and date removed, metadata_verified is False
    l003 = entries["LEGAL-003"]
    assert "G.O." not in l003.title, "LEGAL-003 title should not claim unverified G.O."
    assert l003.date == "2002-01-01"
    assert l003.date_precision == "year_only"
    assert l003.metadata_verified is False

    # LEGAL-015: L.C. Jain Committee Report April 1997 (not 2001 placeholder)
    l015 = entries["LEGAL-015"]
    assert "L.C. Jain" in l015.title or "Jain" in l015.title
    assert l015.date == "1997-04-01", f"LEGAL-015 expected 1997-04-01, got {l015.date}"
    assert l015.date_precision == "approximate"
    assert l015.metadata_verified is True
    assert l015.is_extract is True

    # LEGAL-005 and LEGAL-006: Excerpts correctly marked with updated titles
    l005 = entries["LEGAL-005"]
    assert l005.is_extract is True
    assert "Excerpts" in l005.title

    l006 = entries["LEGAL-006"]
    assert l006.is_extract is True
    assert "Excerpts" in l006.title

    # Principal statutory acts marked as as_enacted
    assert entries["LEGAL-001"].as_enacted is True
    assert entries["LEGAL-002"].as_enacted is True
    assert entries["LEGAL-004"].as_enacted is True
    assert entries["LEGAL-020"].as_enacted is True
    # Executive GOs and Judgments marked as not as_enacted
    assert entries["LEGAL-012"].as_enacted is False
    assert entries["LEGAL-026"].as_enacted is False

    # RAG role tiering distribution
    core_docs = [e for e in entries.values() if e.rag_role == "core"]
    supporting_docs = [e for e in entries.values() if e.rag_role == "supporting"]
    background_docs = [e for e in entries.values() if e.rag_role == "background"]
    assert len(core_docs) == 9, f"Expected 9 core documents, got {len(core_docs)}"
    assert len(supporting_docs) == 19, (
        f"Expected 19 supporting documents, got {len(supporting_docs)}"
    )
    assert len(background_docs) == 2, f"Expected 2 background documents, got {len(background_docs)}"

    # Specific audited documents
    assert entries["LEGAL-012"].rag_role == "core"
    assert entries["LEGAL-013"].rag_role == "supporting"
    assert entries["LEGAL-014"].rag_role == "supporting"
    assert entries["LEGAL-015"].rag_role == "supporting"


def test_legal_corpus_text_quality_and_page_markers() -> None:
    """Verify text quality metrics, page markers, and OCR resolution for garbled pages."""
    manifest_path = Path("data/raw/legal/manifest.json")
    text_dir = Path("data/processed/legal_text")
    entries = {e.id: e for e in load_legal_manifest(manifest_path)}

    assert len(entries) == 30

    for doc_id, entry in entries.items():
        assert entry.text_quality is not None, f"{doc_id} missing text_quality in manifest"
        assert entry.text_quality.char_count > 0, f"{doc_id} char_count must be > 0"
        assert entry.text_quality.word_count >= 50, f"{doc_id} word_count must be >= 50"
        assert entry.text_quality.dictionary_word_ratio >= 0.50, (
            f"{doc_id} dictionary_word_ratio suspiciously low: {entry.text_quality.dictionary_word_ratio}"
        )
        assert entry.extraction_method in {"ocr_300dpi", "native_text_layer"}

        txt_file = text_dir / f"{doc_id}.txt"
        assert txt_file.exists(), f"Missing processed text file for {doc_id}"
        content = txt_file.read_text(encoding="utf-8")
        assert "--- Page 1 ---" in content, f"{doc_id} text missing '--- Page 1 ---' marker"

        # Gate pass expectations: 29 documents pass; LEGAL-015 fails due to degraded 1997 photostat
        if doc_id == "LEGAL-015":
            assert entry.text_quality.quality_gate == "FAIL"
        else:
            assert entry.text_quality.quality_gate == "PASS", (
                f"{doc_id} expected PASS, got {entry.text_quality.quality_gate} "
                f"({entry.text_quality.dictionary_word_ratio:.1%})"
            )

    # Specific check: LEGAL-001 Sections 4-8 and Section 2 FTL definitions cleanly resolved
    legal_001_txt = (text_dir / "LEGAL-001.txt").read_text(encoding="utf-8")
    assert "--- Page 3 ---" in legal_001_txt
    assert "full tank" in legal_001_txt.lower()
    assert "water spread" in legal_001_txt.lower()
    assert "eviction of" in legal_001_txt.lower()
    assert "encroach" in legal_001_txt.lower()
    assert "survey" in legal_001_txt.lower()


@pytest.mark.network
def test_legal_corpus_live_urls_reachable() -> None:
    """Verify every source_url in manifest.json is live over HTTPS (network test)."""
    report = verify_legal_corpus(check_urls=True)
    assert report["ok"] is True, f"Corpus verification failed: {report}"
    assert report["dead_links"] == []


@pytest.mark.network
def test_durable_release_archive_reachable() -> None:
    """Verify that the durable GitHub Release archive is live and reachable over HTTPS."""
    with httpx.Client(follow_redirects=True, timeout=30.0) as client:
        resp = client.head(DURABLE_ARCHIVE_URL)
        assert resp.status_code == 200, f"Durable archive URL returned status {resp.status_code}"
