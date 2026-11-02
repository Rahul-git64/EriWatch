"""OCR processing, clean text extraction, and text quality gate for EriWatch RAG corpus.

Produces clean, page-marked text files under `data/processed/legal_text/{LEGAL_ID}.txt`
and computes dictionary-word ratios and quality metrics for `data/raw/legal/manifest.json`.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Literal

import pypdfium2 as pdfium  # type: ignore[import-untyped]
from pydantic import BaseModel, Field
from pypdf import PdfReader
from rapidocr_onnxruntime import RapidOCR  # type: ignore[import-untyped]

logging.getLogger("pypdf").setLevel(logging.ERROR)

QualityGateStatus = Literal["PASS", "FAIL"]
ExtractionSource = Literal["ocr_300dpi", "native_text_layer"]

LEGAL_DIR = Path("data/raw/legal")
PROCESSED_TEXT_DIR = Path("data/processed/legal_text")
WORDLIST_PATH = Path(__file__).parent / "wordlist.txt"

COMMON_TAMIL_LEGAL_TERMS = frozenset(
    {
        "ayacut",
        "ayacutdars",
        "kudimaramath",
        "poramboke",
        "oorani",
        "ooranies",
        "eri",
        "eris",
        "panchayat",
        "panchayats",
        "kancheepuram",
        "chengalpattu",
        "tamil",
        "nadu",
        "tahsildar",
        "taluk",
        "subdivision",
        "grama",
        "bund",
        "bunds",
        "sluice",
        "sluices",
        "annicut",
        "weir",
        "weirs",
        "savudu",
        "inflow",
        "outflow",
        "fts",
        "ftl",
        "mgnregs",
        "pwd",
        "wrd",
        "cmwssb",
        "palar",
        "thiruporur",
        "madurantakam",
        "uthiramerur",
        "tenneri",
        "walajabad",
        "siruseri",
        "navalur",
        "perumbakkam",
        "nanmangalam",
        "sembakkam",
        "keelkattalai",
    }
)


class TextQualityMetrics(BaseModel):
    """Quality metrics for processed legal text."""

    extraction_source: ExtractionSource
    char_count: int = Field(..., ge=0)
    word_count: int = Field(..., ge=0)
    dictionary_word_ratio: float = Field(..., ge=0.0, le=1.0)
    quality_gate: QualityGateStatus


def load_english_wordlist() -> set[str]:
    """Load standard dictionary words + regional legal domain terminology."""
    if not WORDLIST_PATH.exists():
        msg = f"Wordlist missing at {WORDLIST_PATH}"
        raise FileNotFoundError(msg)
    words = set(WORDLIST_PATH.read_text(encoding="utf-8").splitlines())
    words.update(COMMON_TAMIL_LEGAL_TERMS)
    return words


def compute_text_metrics(text: str, dictionary_words: set[str]) -> tuple[int, int, float]:
    """Return (char_count, word_count, dictionary_word_ratio) for a text string."""
    char_count = len(text)
    tokens = [w.lower() for w in re.findall(r"\b[a-zA-Z]{2,}\b", text)]
    word_count = len(tokens)
    if not word_count:
        return char_count, 0, 0.0
    valid_count = sum(1 for w in tokens if w in dictionary_words)
    ratio = round(valid_count / word_count, 4)
    return char_count, word_count, ratio


def extract_native_text(pdf_path: Path) -> list[str]:
    """Extract embedded PDF text layer page by page."""
    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for page in reader.pages:
        txt = (page.extract_text() or "").strip()
        pages.append(txt)
    return pages


def ocr_pdf_300dpi(pdf_path: Path, ocr_engine: RapidOCR | None = None) -> list[str]:
    """Render PDF pages at 300 dpi and extract text via RapidOCR."""
    if ocr_engine is None:
        ocr_engine = RapidOCR()
    doc = pdfium.PdfDocument(str(pdf_path))
    pages: list[str] = []
    for i in range(len(doc)):
        img = doc[i].render(scale=300 / 72).to_pil()
        res, _ = ocr_engine(img)
        page_lines = [line[1] for line in res] if res else []
        pages.append("\n".join(page_lines).strip())
    return pages


def process_document(
    doc_id: str,
    pdf_path: Path,
    dictionary_words: set[str],
    ocr_engine: RapidOCR,
    force_ocr: bool = False,
) -> tuple[str, TextQualityMetrics]:
    """Process a single PDF into page-marked clean text and compute quality metrics."""
    # Scanned Gazette PDFs or documents with garbled / zero native text must be OCR'd
    known_ocr_needed = {
        "LEGAL-001",
        "LEGAL-002",
        "LEGAL-006",
        "LEGAL-012",
        "LEGAL-013",
        "LEGAL-014",
        "LEGAL-015",
    }

    # First inspect embedded text
    native_pages = extract_native_text(pdf_path)
    combined_native = "\n\n".join(native_pages)
    _, native_words, native_ratio = compute_text_metrics(combined_native, dictionary_words)

    use_ocr = (
        force_ocr
        or doc_id in known_ocr_needed
        or native_words < 50
        or (native_ratio < 0.70 and native_words > 0 and doc_id in known_ocr_needed)
    )

    if use_ocr:
        pages = ocr_pdf_300dpi(pdf_path, ocr_engine)
        source: ExtractionSource = "ocr_300dpi"
    else:
        pages = native_pages
        source = "native_text_layer"

    # Assemble clean text with page markers
    formatted_chunks: list[str] = []
    for page_num, content in enumerate(pages, start=1):
        formatted_chunks.append(f"--- Page {page_num} ---\n{content.strip()}")
    full_text = "\n\n".join(formatted_chunks) + "\n"

    # For bilingual documents (e.g. LEGAL-018 with pp. 1-7 Hindi, pp. 8-14 English),
    # score the English section against the English dictionary to avoid penalizing Hindi text.
    if doc_id == "LEGAL-018":
        english_chunks = formatted_chunks[7:]  # pages 8-14
        scoring_text = "\n\n".join(english_chunks)
    else:
        scoring_text = full_text

    # Compute final metrics
    char_count, word_count, ratio = compute_text_metrics(scoring_text, dictionary_words)
    quality_gate: QualityGateStatus = "PASS" if ratio >= 0.70 and word_count >= 50 else "FAIL"

    metrics = TextQualityMetrics(
        extraction_source=source,
        char_count=char_count,
        word_count=word_count,
        dictionary_word_ratio=ratio,
        quality_gate=quality_gate,
    )
    return full_text, metrics


def run_pipeline(
    legal_dir: Path = LEGAL_DIR,
    output_dir: Path = PROCESSED_TEXT_DIR,
    manifest_path: Path = LEGAL_DIR / "manifest.json",
    force_ocr: bool = False,
) -> dict[str, Any]:
    """Run full OCR and text extraction pipeline on all documents in manifest."""
    output_dir.mkdir(parents=True, exist_ok=True)
    dictionary_words = load_english_wordlist()
    ocr_engine = RapidOCR()

    raw_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    documents = raw_manifest.get("documents", [])

    results: list[dict[str, Any]] = []
    before_after_report: list[dict[str, Any]] = []

    for doc in documents:
        doc_id = doc["id"]
        filename = doc["filename"]
        pdf_path = legal_dir / filename
        if not pdf_path.exists():
            continue

        text_file = output_dir / f"{doc_id}.txt"

        # Compute raw before metrics
        raw_native = extract_native_text(pdf_path)
        _, raw_words, raw_ratio = compute_text_metrics("\n\n".join(raw_native), dictionary_words)

        if text_file.exists() and not force_ocr:
            clean_text = text_file.read_text(encoding="utf-8")
            if doc_id == "LEGAL-018":
                pages = clean_text.split("--- Page ")
                scoring_text = "--- Page ".join(pages[8:]) if len(pages) > 8 else clean_text
            else:
                scoring_text = clean_text
            chars, words, ratio = compute_text_metrics(scoring_text, dictionary_words)
            source: ExtractionSource = (
                "ocr_300dpi"
                if doc_id
                in {
                    "LEGAL-001",
                    "LEGAL-002",
                    "LEGAL-006",
                    "LEGAL-012",
                    "LEGAL-013",
                    "LEGAL-014",
                    "LEGAL-015",
                }
                else "native_text_layer"
            )
            gate: QualityGateStatus = "PASS" if ratio >= 0.70 and words >= 50 else "FAIL"
            metrics = TextQualityMetrics(
                extraction_source=source,
                char_count=chars,
                word_count=words,
                dictionary_word_ratio=ratio,
                quality_gate=gate,
            )
        else:
            # Process clean text
            clean_text, metrics = process_document(
                doc_id, pdf_path, dictionary_words, ocr_engine, force_ocr=force_ocr
            )
            text_file.write_text(clean_text, encoding="utf-8")

        # Update manifest document entry
        doc["text_quality"] = metrics.model_dump()
        doc["extraction_method"] = metrics.extraction_source

        before_after_report.append(
            {
                "id": doc_id,
                "raw_words": raw_words,
                "raw_ratio": raw_ratio,
                "clean_words": metrics.word_count,
                "clean_ratio": metrics.dictionary_word_ratio,
                "source": metrics.extraction_source,
                "quality_gate": metrics.quality_gate,
            }
        )
        results.append(doc)

    raw_manifest["documents"] = results
    manifest_path.write_text(
        json.dumps(raw_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    return {
        "processed_count": len(results),
        "report": before_after_report,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    print("Starting EriWatch legal text extraction and 300 dpi OCR pipeline...")
    report = run_pipeline()
    print(f"Completed text processing for {report['processed_count']} documents.")
    for item in report["report"]:
        print(
            f"{item['id']:9s} | Raw: {item['raw_ratio']:.1%} ({item['raw_words']}w) -> "
            f"Clean: {item['clean_ratio']:.1%} ({item['clean_words']}w) [{item['source']}] "
            f"Gate: {item['quality_gate']}"
        )


if __name__ == "__main__":
    main()
