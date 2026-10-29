"""Legal corpus manifest schema and verification utilities for Stage R (`packages/rag`).

Every document in `data/raw/legal/` MUST be a real original PDF downloaded from an
official government, statutory, or judicial URL. Synthetic or agent-generated PDFs
are strictly prohibited and blocked by SHA-256 hash.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

ExtractionMethod = Literal["text_layer", "ocr_needed"]

# Permanent blocklist of the 28 agent-generated PDFs from commit 859c32a (audited in R1.1).
BANNED_GENERATED_SHA256S: frozenset[str] = frozenset(
    {
        "d4ec8cb6e8a1f97700c47dc13f9ac8ab8b48fddf925dc4293d728e54a4d6a408",
        "33376dcf5d7cee7407ac946603eeb5b2c42aafdff159da32a81af1e63ac6cddd",
        "47ac3663002072ba99976c1d8cd60092d256f3dbc584dea7a2cf6ef8bb568b17",
        "37d6edf2130c1aa5b38a443c30c1e7f0d6e7b1c2d38c08d647c011e52a6ff2e2",
        "ac71e46dd3207f09701b73e264cb7f33c77af9400af80dc80f94ed3ba80bf4c5",
        "4e671e4d7dab23c56dac4eb1f175d853d11dae40e847ae8ef98759605b0ee87c",
        "b73b01648078adfde53314e13a3084d3dc3ad221b4eef3a11addfd0c6dff74d1",
        "2610cc8fd55e2cc3d054687d01abb4c1adcf97a27bc01bc7c3d77f92394ed0b5",
        "96656df124ecf63117c0ef1a8a1b302bad532971b2312b88c66b0e57d30f38e0",
        "bd6057e6940898a01715d76da1500f0f3e39b4b4b614cf25f46f2756f2593394",
        "eafff6df9d15d351eaeb790a31c4449c955e079c883dadf794fd76518c74f156",
        "b169144b2bad040ef5c603459d0d5a062d90b8f8f80c8777e91a51d04b8a50e9",
        "be8118d0294e8619e74bb7a33e4cfefcf7b91a9ef1302855d9fd6782a2b78a9c",
        "9e92ed4c4ae5949acaf532d6220505b425511ad7db0eace9eb76e979291c3fb1",
        "57e269484e975398e2d3bedf6990504eb0b97612f1a5a0224f1e5f74ca5511e9",
        "992ca04bba88c2527418f37797db98f1b4a27103555093334e29ae117f17f5b5",
        "a5fd29ae31fe162aebe153eac77d6743309927a4cf98dacdcf89dea56896ce07",
        "162d824bb2c2f3e458bb2f3626bfb4e73c79dac14d0ddc318e86a53ab5053590",
        "d5d1b93d30865cf876911ee04c67c9e0af2cd172b9bc7d6f01e6b9137841c520",
        "fafddd9f026914fe92727a30cbe7a7bd6acf8761cf2402f029af283175073d43",
        "c320ae43b21f7cf9920c2e82c5f6a62d084fab8fe7a056df2fd9f730af0f7081",
        "fc095b8ef2e8882f5ee0dbb1aea959774e7335f7fd4908c06a34562e3d25e176",
        "b2a673b41e5988ad567ca9ab60ff67a550fd70c878b8dbcef5719614e257bc90",
        "9f29e8a81a0fddbd82403a2f355ef4f163b221576f4f41a173e37dc6a8d94fd3",
        "3ad9d8bc24a8f19a90d42967c6153ecec053d1f171985e8c667a4b51e25889e8",
        "30fccc41b218145098b1cb61d481d67784f6aa65d825f7a07567c477a06850a2",
        "b205331e5fa0bcbab31d839b738551f97c68b327f5bf01f00afa5366da59b952",
        "84c3b8cb6a84591d09fc8a5222e66c882d70905a1b4567bc322d38c24d060074",
    }
)


class LegalCorpusEntry(BaseModel):
    """Required schema for each verified original document in `data/raw/legal/manifest.json`."""

    id: str = Field(..., pattern=r"^LEGAL-\d{3}$")
    filename: str
    title: str
    issuer: str
    document_type: str
    date: str
    language: str
    source_url: str
    retrieved_at: str
    sha256: str = Field(..., min_length=64, max_length=64)
    page_count: int = Field(..., ge=1)
    licence_note: str
    extraction_method: ExtractionMethod


def compute_file_sha256(path: Path) -> str:
    """Compute hex SHA-256 digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_legal_manifest(
    manifest_path: Path = Path("data/raw/legal/manifest.json"),
) -> list[LegalCorpusEntry]:
    """Load and validate the legal corpus manifest."""
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    return [LegalCorpusEntry(**doc) for doc in raw.get("documents", [])]
