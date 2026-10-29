"""Smoke tests for eriwatch_geo package."""

import eriwatch_geo


def test_geo_version() -> None:
    """Verify package version is exposed."""
    assert eriwatch_geo.__version__ == "0.1.0"
