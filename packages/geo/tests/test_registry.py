"""Tests for the pilot tank registry (`packages/geo/src/eriwatch_geo/registry.py`)."""

import json
from pathlib import Path

import pytest

from eriwatch_geo.registry import (
    build_tank_registry_records,
    compute_geodesic_area_ha,
    export_tank_registry_geojson,
    fetch_osm_polygon,
    load_tank_registry,
)


def test_registry_has_35_verified_pilot_tanks_with_unverified_labels() -> None:
    """Verify 30-50 pilot tanks (35 after dropping TN-KPM-013 in R2.4) with real polygons and overlays."""
    records = build_tank_registry_records()
    assert 30 <= len(records) <= 50
    assert len(records) == 35

    ids = {r.id for r in records}
    assert len(ids) == 35
    assert "TN-KPM-013" not in ids, "TN-KPM-013 failed R2.3 NDWI overlay check and must be dropped"

    sources = {r.source for r in records}
    assert sources == {"osm", "derived"}

    states = {r.state_archetype for r in records}
    assert states == {"unverified"}, (
        "All tank health labels must be 'unverified' until Stage 2 water-spread measurements"
    )

    overlay_summary = json.loads(
        Path("docs/data/overlays/overlay_summary.json").read_text(encoding="utf-8")
    )
    overlay_by_id = {row["id"]: row for row in overlay_summary["tanks"]}

    for rec in records:
        ring = rec.polygon_coordinates[0]
        assert len(ring) >= 18, f"Tank {rec.id} has too few vertices ({len(ring)})"
        assert ring[0] == ring[-1], f"Polygon ring for {rec.id} must be closed"
        measured_area = compute_geodesic_area_ha(ring)
        assert measured_area >= 12.0, f"Tank {rec.id} geodesic area {measured_area} ha < 12 ha"
        assert abs(measured_area - rec.nominal_max_area_ha) <= 0.1
        if rec.source == "derived":
            assert rec.confidence == "medium"
            assert rec.osm_id is None
        else:
            assert rec.confidence == "high"
            assert rec.osm_id is not None
            assert rec.osm_type in ("way", "relation")

        # Verify Sentinel-2 overlay PNG exists and passed water-body check
        png_path = Path(f"docs/data/overlays/{rec.id}.png")
        assert png_path.exists() and png_path.stat().st_size > 10_000
        assert overlay_by_id[rec.id]["matches_real_water_body"] is True


def test_registry_geojson_file_roundtrip() -> None:
    """Verify data/processed/tank_registry.geojson exists and round-trips cleanly."""
    geojson_path = Path("data/processed/tank_registry.geojson")
    export_tank_registry_geojson(geojson_path)
    assert geojson_path.exists()

    loaded = load_tank_registry(geojson_path)
    assert len(loaded) == 35
    assert loaded[0].id == "TN-KPM-001"
    assert loaded[-1].id == "TN-CGL-018"
    assert all(r.state_archetype == "unverified" for r in loaded)


@pytest.mark.network
def test_live_osm_way_polygon_extraction() -> None:
    """Live network test verifying OpenStreetMap API v0.6 returns Chembarambakkam Lake way."""
    ring, area_ha = fetch_osm_polygon("way", 25453624)
    assert len(ring) == 218
    assert ring[0] == ring[-1]
    assert abs(area_ha - 1991.29) <= 0.5

