"""Live feasibility spike runner for Stage 1 Step 1.1.

Executes real HTTP calls against each candidate external data source for at least
3 pilot tanks in Chengalpattu / Kancheepuram districts and records structured
evidence to data/raw/samples/feasibility_spike.json.
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

PILOT_SAMPLE_TANKS: list[dict[str, Any]] = [
    {
        "id": "TN-KPM-001",
        "name": "Chembarambakkam Tank",
        "district": "Kancheepuram",
        "block": "Kundrathur",
        "lat": 13.0116,
        "lon": 80.0592,
        "bbox": [80.0250, 12.9850, 80.0880, 13.0400],
    },
    {
        "id": "TN-CGL-001",
        "name": "Madurantakam Tank",
        "district": "Chengalpattu",
        "block": "Madurantakam",
        "lat": 12.5133,
        "lon": 79.8736,
        "bbox": [79.8450, 12.4900, 79.8950, 12.5450],
    },
    {
        "id": "TN-KPM-002",
        "name": "Thenneri Tank",
        "district": "Kancheepuram",
        "block": "Walajabad",
        "lat": 12.8586,
        "lon": 79.8825,
        "bbox": [79.8650, 12.8420, 79.9020, 12.8780],
    },
    {
        "id": "TN-CGL-002",
        "name": "Kolavai Lake (Chengalpattu)",
        "district": "Chengalpattu",
        "block": "Kattankolathur",
        "lat": 12.7072,
        "lon": 79.9856,
        "bbox": [79.9700, 12.6880, 80.0020, 12.7280],
    },
]


def spike_planetary_computer_stac(client: httpx.Client) -> dict[str, Any]:
    """Query Microsoft Planetary Computer STAC for Sentinel-2 L2A over 4 pilot tanks."""
    url = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
    results: list[dict[str, Any]] = []
    for tank in PILOT_SAMPLE_TANKS:
        t0 = time.perf_counter()
        resp = client.post(
            url,
            json={
                "collections": ["sentinel-2-l2a"],
                "bbox": tank["bbox"],
                "datetime": "2024-01-01T00:00:00Z/2024-12-31T23:59:59Z",
                "limit": 3,
            },
        )
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        resp.raise_for_status()
        payload = resp.json()
        features = payload.get("features", [])
        sample_feature = features[0] if features else {}
        assets = list(sample_feature.get("assets", {}).keys())
        results.append(
            {
                "tank_id": tank["id"],
                "tank_name": tank["name"],
                "status_code": resp.status_code,
                "elapsed_ms": elapsed_ms,
                "returned_scenes": len(features),
                "sample_scene_id": sample_feature.get("id"),
                "sample_datetime": sample_feature.get("properties", {}).get("datetime"),
                "cloud_cover_pct": sample_feature.get("properties", {}).get("eo:cloud_cover"),
                "has_required_bands": all(b in assets for b in ["B03", "B08", "B11", "SCL"]),
            }
        )
    return {
        "source": "Microsoft Planetary Computer STAC (sentinel-2-l2a)",
        "status": "OK",
        "tanks": results,
    }


def spike_copernicus_stac(client: httpx.Client) -> dict[str, Any]:
    """Query Copernicus Data Space OData and Element84 Earth Search STAC fallbacks."""
    tank = PILOT_SAMPLE_TANKS[0]
    odata_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
    filter_expr = (
        "Collection/Name eq 'SENTINEL-2' and "
        f"OData.CSC.Intersects(area=geography'SRID=4326;POINT({tank['lon']} {tank['lat']})') and "
        "ContentDate/Start gt 2024-01-01T00:00:00.000Z"
    )
    t0 = time.perf_counter()
    resp_cdse = client.get(odata_url, params={"$filter": filter_expr, "$top": 2})
    cdse_ms = round((time.perf_counter() - t0) * 1000, 1)
    resp_cdse.raise_for_status()
    cdse_products = resp_cdse.json().get("value", [])

    e84_url = "https://earth-search.aws.element84.com/v1/search"
    t1 = time.perf_counter()
    resp_e84 = client.post(
        e84_url,
        json={
            "collections": ["sentinel-2-l2a"],
            "bbox": tank["bbox"],
            "datetime": "2024-01-01T00:00:00Z/2024-12-31T23:59:59Z",
            "limit": 2,
        },
    )
    e84_ms = round((time.perf_counter() - t1) * 1000, 1)
    resp_e84.raise_for_status()
    e84_features = resp_e84.json().get("features", [])

    return {
        "source": "Copernicus Data Space OData + Element84 Earth Search STAC (Fallbacks)",
        "status": "OK",
        "tank_id": tank["id"],
        "copernicus_odata": {
            "status_code": resp_cdse.status_code,
            "elapsed_ms": cdse_ms,
            "returned_products": len(cdse_products),
            "sample_product_name": cdse_products[0].get("Name") if cdse_products else None,
        },
        "element84_stac_cog": {
            "status_code": resp_e84.status_code,
            "elapsed_ms": e84_ms,
            "returned_scenes": len(e84_features),
            "sample_scene_id": e84_features[0].get("id") if e84_features else None,
        },
    }


def spike_jrc_global_surface_water(client: httpx.Client) -> dict[str, Any]:
    """Query JRC Global Surface Water via Planetary Computer STAC for 4 pilot tanks."""
    url = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
    results: list[dict[str, Any]] = []
    for tank in PILOT_SAMPLE_TANKS:
        t0 = time.perf_counter()
        resp = client.post(
            url,
            json={
                "collections": ["jrc-gsw"],
                "bbox": tank["bbox"],
                "limit": 2,
            },
        )
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        resp.raise_for_status()
        features = resp.json().get("features", [])
        f0 = features[0] if features else {}
        results.append(
            {
                "tank_id": tank["id"],
                "status_code": resp.status_code,
                "elapsed_ms": elapsed_ms,
                "tile_id": f0.get("id"),
                "assets": list(f0.get("assets", {}).keys()),
            }
        )
    return {
        "source": "JRC Global Surface Water (jrc-gsw via STAC)",
        "status": "OK",
        "tanks": results,
    }


def spike_nasa_power_rainfall(client: httpx.Client) -> dict[str, Any]:
    """Query NASA POWER Daily Agroclimatology API (PRECTOTCORR) for 4 pilot tanks."""
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    results: list[dict[str, Any]] = []
    for tank in PILOT_SAMPLE_TANKS:
        t0 = time.perf_counter()
        resp = client.get(
            url,
            params={
                "parameters": "PRECTOTCORR,T2M",
                "community": "AG",
                "longitude": tank["lon"],
                "latitude": tank["lat"],
                "start": "20241001",
                "end": "20241015",
                "format": "JSON",
            },
        )
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        resp.raise_for_status()
        data = resp.json()
        precip = data.get("properties", {}).get("parameter", {}).get("PRECTOTCORR", {})
        results.append(
            {
                "tank_id": tank["id"],
                "status_code": resp.status_code,
                "elapsed_ms": elapsed_ms,
                "days_returned": len(precip),
                "total_rain_mm_15d": round(sum(v for v in precip.values() if v >= 0), 2),
                "sample_values": dict(list(precip.items())[:3]),
            }
        )
    return {
        "source": "NASA POWER Agroclimatology API (PRECTOTCORR)",
        "status": "OK",
        "tanks": results,
    }


def spike_osm_overpass(client: httpx.Client) -> dict[str, Any]:
    """Query OpenStreetMap Nominatim GeoJSON polygon API and Overpass API for pilot tanks."""
    headers = {"User-Agent": "EriWatch-SAIU-Capstone/0.1 (rahul.n-27@scds.saiuniversity.edu.in)"}
    search_queries = {
        "TN-KPM-001": "Chembarambakkam Lake, Tamil Nadu",
        "TN-CGL-001": "Madurantakam Lake, Tamil Nadu",
        "TN-KPM-002": "Thenneri Lake, Tamil Nadu",
        "TN-CGL-002": "Kolavai Lake, Chengalpattu",
    }
    results: list[dict[str, Any]] = []
    for tank in PILOT_SAMPLE_TANKS:
        q = search_queries[tank["id"]]
        t0 = time.perf_counter()
        resp = client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": q, "format": "geojson", "polygon_geojson": 1, "limit": 1},
            headers=headers,
            timeout=15.0,
        )
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        resp.raise_for_status()
        features = resp.json().get("features", [])
        feat = features[0] if features else {}
        props = feat.get("properties", {})
        geom = feat.get("geometry", {})
        results.append(
            {
                "tank_id": tank["id"],
                "query": q,
                "status_code": resp.status_code,
                "elapsed_ms": elapsed_ms,
                "osm_type": props.get("osm_type"),
                "osm_id": props.get("osm_id"),
                "display_name": props.get("display_name"),
                "geometry_type": geom.get("type"),
                "has_polygon": geom.get("type") in ("Polygon", "MultiPolygon"),
            }
        )
        time.sleep(1.1)  # Respect Nominatim 1 req/sec usage policy

    # Also record direct Overpass API status (rate-limited/timeout behaviour on public instances)
    overpass_probe: dict[str, Any] = {}
    try:
        t_ov = time.perf_counter()
        r_ov = client.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": "[out:json][timeout:5];way(24771746);out tags center;"},
            headers=headers,
            timeout=8.0,
        )
        overpass_probe = {
            "status_code": r_ov.status_code,
            "elapsed_ms": round((time.perf_counter() - t_ov) * 1000, 1),
            "elements": len(r_ov.json().get("elements", [])) if r_ov.status_code == 200 else 0,
        }
    except Exception as exc:
        overpass_probe = {"status": "TIMEOUT_ON_PUBLIC_ENDPOINT", "error": str(exc)}

    return {
        "source": "OpenStreetMap (Nominatim GeoJSON Polygon API + Overpass API probe)",
        "status": "OK",
        "overpass_probe": overpass_probe,
        "tanks": results,
    }


def spike_groundwater_and_soil_moisture(client: httpx.Client) -> dict[str, Any]:
    """Spike India-WRIS CGWB endpoint and NASA POWER root-zone/profile wetness."""
    wris_url = "https://indiawris.gov.in/Dataset/Ground%20Water%20Level"
    wris_status: dict[str, Any] = {}
    try:
        t0 = time.perf_counter()
        r = client.post(
            wris_url,
            params={
                "stateName": "Tamil Nadu",
                "districtName": "Kancheepuram",
                "agencyName": "CGWB",
                "startdate": "2024-01-01",
                "enddate": "2024-06-01",
                "download": "false",
                "page": 0,
                "size": 5,
            },
            timeout=15.0,
        )
        wris_status = {
            "status_code": r.status_code,
            "elapsed_ms": round((time.perf_counter() - t0) * 1000, 1),
            "content_type": r.headers.get("content-type"),
            "preview": r.text[:250],
        }
    except Exception as exc:
        wris_status = {"status": "UNREACHABLE_OR_BLOCKED", "error": str(exc)}

    # Also verify NASA POWER GWETROOT / GWETPROF (Root Zone & Profile Soil Wetness, 0-1)
    power_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    gw_results: list[dict[str, Any]] = []
    for tank in PILOT_SAMPLE_TANKS:
        t0 = time.perf_counter()
        resp = client.get(
            power_url,
            params={
                "parameters": "GWETROOT,GWETPROF",
                "community": "AG",
                "longitude": tank["lon"],
                "latitude": tank["lat"],
                "start": "20241001",
                "end": "20241010",
                "format": "JSON",
            },
        )
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        resp.raise_for_status()
        params_data = resp.json().get("properties", {}).get("parameter", {})
        gwetprof = params_data.get("GWETPROF", {})
        gw_results.append(
            {
                "tank_id": tank["id"],
                "status_code": resp.status_code,
                "elapsed_ms": elapsed_ms,
                "days_returned": len(gwetprof),
                "mean_profile_wetness": round(
                    sum(v for v in gwetprof.values() if v >= 0) / max(1, len(gwetprof)),
                    4,
                ),
            }
        )
    return {
        "source": "India-WRIS / CGWB Groundwater & NASA POWER Profile Subsurface Wetness",
        "india_wris_probe": wris_status,
        "nasa_power_subsurface_tanks": gw_results,
    }


def main() -> None:
    """Run all feasibility spikes and write output JSON."""
    out_path = Path("data/raw/samples/feasibility_spike.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        report = {
            "executed_at": datetime.now(UTC).isoformat(),
            "pilot_sample_tanks": PILOT_SAMPLE_TANKS,
            "spikes": {
                "sentinel2_planetary_computer": spike_planetary_computer_stac(client),
                "sentinel2_copernicus_fallback": spike_copernicus_stac(client),
                "jrc_global_surface_water": spike_jrc_global_surface_water(client),
                "nasa_power_rainfall": spike_nasa_power_rainfall(client),
                "osm_overpass_water_bodies": spike_osm_overpass(client),
                "groundwater_wris_and_subsurface": spike_groundwater_and_soil_moisture(client),
            },
        }

    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote feasibility spike results to {out_path}")


if __name__ == "__main__":
    main()
