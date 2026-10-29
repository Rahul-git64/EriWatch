"""Strict verification tests for the real legal corpus (`packages/rag/tests/test_corpus_manifest.py`).

Tests Step R1.5 requirements:
1. At least 25 real documents in `data/raw/legal/manifest.json`.
2. All required fields present and non-empty (`id`, `filename`, `title`, `issuer`,
   `document_type`, `date`, `language`, `source_url`, `retrieved_at`, `sha256`,
   `page_count`, `licence_note`, `extraction_method`).
3. `sha256` matches the actual file bytes on disk.
4. `page_count` matches `len(PdfReader(file).pages)`.
5. `source_url` is a well-formed `https://` URL pointing to `.pdf`.
6. Neither the manifest nor any `.pdf` in `data/raw/legal/` is in `BANNED_GENERATED_SHA256S`.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

import pytest
from pypdf import PdfReader

from eriwatch_rag.corpus_manifest import (
    BANNED_GENERATED_SHA256S,
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
        assert pdf_path.exists(), f"{entry.id} missing PDF on disk: {pdf_path}"
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


@pytest.mark.network
def test_legal_corpus_live_urls_reachable() -> None:
    """Verify every source_url in manifest.json is live over HTTPS (network test)."""
    report = verify_legal_corpus(check_urls=True)
    assert report["ok"] is True, f"Corpus verification failed: {report}"
    assert report["dead_links"] == []
