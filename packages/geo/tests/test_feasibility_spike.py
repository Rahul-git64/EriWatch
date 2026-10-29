"""Unit and network tests for Stage 1 / Stage R feasibility spike artifact and schema."""

import json
from pathlib import Path

import httpx
import pytest

from eriwatch_geo.feasibility_spike import (
    PILOT_SAMPLE_TANKS,
    spike_nasa_power_rainfall,
)


def test_pilot_sample_tanks_has_at_least_three_tanks() -> None:
    """Verify feasibility spike defines at least 3 pilot tanks across the target districts."""
    assert len(PILOT_SAMPLE_TANKS) >= 3
    districts = {t["district"] for t in PILOT_SAMPLE_TANKS}
    assert "Kancheepuram" in districts
    assert "Chengalpattu" in districts
    for tank in PILOT_SAMPLE_TANKS:
        min_lon, min_lat, max_lon, max_lat = tank["bbox"]
        assert min_lon < tank["lon"] < max_lon
        assert min_lat < tank["lat"] < max_lat


def test_feasibility_spike_artifact_contains_real_payload_metrics() -> None:
    """Verify feasibility_spike.json contains real counts, raster values, distances, vertices."""
    artifact = Path("data/raw/samples/feasibility_spike.json")
    assert artifact.exists(), "feasibility_spike.json must exist"
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    spikes = payload["spikes"]

    # 1. Sentinel-2 STAC counts, dates, and cloud cover
    s2_tanks = spikes["sentinel2_planetary_computer"]["tanks"]
    assert len(s2_tanks) >= 4
    for t in s2_tanks:
        assert t["returned_scenes"] >= 60
        assert t["scenes_cloud_lt_20pct"] >= 5
        assert 0.0 < t["mean_cloud_cover_pct"] < 100.0
        assert t["has_required_bands"] is True
        assert len(t["sample_scenes"]) >= 3

    # 2. JRC Global Surface Water pixel values sampled at centroids
    jrc_tanks = spikes["jrc_global_surface_water"]["tanks"]
    assert len(jrc_tanks) >= 4
    for t in jrc_tanks:
        assert 40 <= t["centroid_occurrence_pct"] <= 100
        assert t["centroid_max_extent_flag"] == 1
        assert 1 <= t["centroid_seasonality_months"] <= 12

    # 3. NASA POWER daily rainfall values with dates
    rain_tanks = spikes["nasa_power_rainfall"]["tanks"]
    assert len(rain_tanks) >= 4
    for t in rain_tanks:
        assert t["days_returned"] == 15
        assert len(t["daily_rainfall_mm"]) == 15
        assert t["peak_daily_rain_mm"] > 20.0
        assert t["peak_daily_rain_date"] == "2024-10-15"

    # 4. CGWB station IDs, real readings, and distance to each tank
    gw = spikes["groundwater_wris_and_subsurface"]
    assert gw["india_wris_probe"]["unique_stations_parsed"] >= 20
    for t in gw["nasa_power_subsurface_tanks"]:
        st = t["nearest_cgwb_station"]
        assert st["station_code"]
        assert 0.5 <= st["distance_to_tank_km"] <= 25.0
        assert st["water_level_m_bgl"] is not None
        assert st["reading_time"]

    # 5. Nominatim / OSM geometry vertex counts
    osm_tanks = spikes["osm_overpass_water_bodies"]["tanks"]
    assert len(osm_tanks) >= 4
    for t in osm_tanks:
        assert t["osm_api_v06_vertex_count"] >= 40
        assert t["osm_api_v06_geodesic_area_ha"] >= 40.0


@pytest.mark.network
def test_live_nasa_power_rainfall_spike() -> None:
    """Live network test verifying NASA POWER daily rainfall API returns 15 days per tank."""
    with httpx.Client(timeout=30.0) as client:
        res = spike_nasa_power_rainfall(client)
    assert res["work_status"] == "WORKED_FULLY"
    assert len(res["tanks"]) == 4
    assert all(len(t["daily_rainfall_mm"]) == 15 for t in res["tanks"])
