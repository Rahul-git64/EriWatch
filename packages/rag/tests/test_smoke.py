"""Smoke tests for eriwatch_rag package."""

import eriwatch_rag


def test_rag_version() -> None:
    """Verify package version is exposed."""
    assert eriwatch_rag.__version__ == "0.1.0"
