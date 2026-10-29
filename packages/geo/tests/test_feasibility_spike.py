"""Unit tests for Stage 1 feasibility spike artifact and schema."""

from pathlib import Path

from eriwatch_geo.feasibility_spike import PILOT_SAMPLE_TANKS


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


def test_feasibility_spike_artifact_exists_and_valid() -> None:
    """Verify the recorded feasibility_spike.json artifact has real 200 OK responses."""
    import json

    artifact = Path("data/raw/samples/feasibility_spike.json")
    assert artifact.exists(), "feasibility_spike.json must exist"
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    spikes = payload["spikes"]

    s2_tanks = spikes["sentinel2_planetary_computer"]["tanks"]
    assert len(s2_tanks) >= 3
    assert all(t["status_code"] == 200 and t["has_required_bands"] for t in s2_tanks)

    jrc_tanks = spikes["jrc_global_surface_water"]["tanks"]
    assert len(jrc_tanks) >= 3
    assert all(t["status_code"] == 200 and "occurrence" in t["assets"] for t in jrc_tanks)

    rain_tanks = spikes["nasa_power_rainfall"]["tanks"]
    assert len(rain_tanks) >= 3
    assert all(t["status_code"] == 200 and t["days_returned"] == 15 for t in rain_tanks)

    gw = spikes["groundwater_wris_and_subsurface"]
    assert gw["india_wris_probe"]["status_code"] == 200
    assert len(gw["nasa_power_subsurface_tanks"]) >= 3
