"""Smoke tests for eriwatch_ml package."""

import eriwatch_ml


def test_ml_version() -> None:
    """Verify package version is exposed."""
    assert eriwatch_ml.__version__ == "0.1.0"
