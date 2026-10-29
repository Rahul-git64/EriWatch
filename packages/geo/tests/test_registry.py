"""Tests for the pilot tank registry (`packages/geo/src/eriwatch_geo/registry.py`)."""

from pathlib import Path

from eriwatch_geo.registry import (
    build_tank_registry_records,
    compute_geodesic_area_ha,
    export_tank_registry_geojson,
    load_tank_registry,
)


def test_registry_has_36_valid_pilot_tanks_with_unverified_labels() -> None:
    """Verify 36 real pilot tanks with unverified health labels and real polygon geometries."""
    records = build_tank_registry_records()
    assert 30 <= len(records) <= 50
    assert len(records) == 36

    ids = {r.id for r in records}
    assert len(ids) == 36

    sources = {r.source for r in records}
    assert sources == {"osm", "derived"}

    states = {r.state_archetype for r in records}
    assert states == {"unverified"}, (
        "All tank health labels must be 'unverified' until Stage 2 water-spread measurements"
    )

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


def test_registry_geojson_file_roundtrip() -> None:
    """Verify data/processed/tank_registry.geojson exists and round-trips cleanly."""
    geojson_path = Path("data/processed/tank_registry.geojson")
    export_tank_registry_geojson(geojson_path)
    assert geojson_path.exists()

    loaded = load_tank_registry(geojson_path)
    assert len(loaded) == 36
    assert loaded[0].id == "TN-KPM-001"
    assert loaded[-1].id == "TN-CGL-018"
    assert all(r.state_archetype == "unverified" for r in loaded)
