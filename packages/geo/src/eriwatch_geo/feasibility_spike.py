"""Live feasibility spike runner for Stage 1 / Corrective Stage R (Steps R3.1 & R3.2).

Executes real HTTP and raster queries against each external data source for 4 pilot tanks
across Kancheepuram and Chengalpattu districts and records real payload measurements
(not just HTTP status codes) to `data/raw/samples/feasibility_spike.json`:
  1. STAC item counts, scene dates, and cloud-cover statistics per tank (2024 full year).
  2. JRC Global Surface Water (`jrc-gsw`) pixel values (`occurrence`, `seasonality`, `extent`)
     sampled directly at each tank's water centroid via Planetary Computer SAS + `rasterio`.
  3. NASA POWER daily rainfall values (`mm/day`) with exact dates (`2024-10-01`..`2024-10-15`).
  4. India-WRIS CGWB groundwater station IDs, coordinates, real water-level readings (`m bgl`),
     reading timestamps, and WGS84 geodesic distance (`km`) to each tank.
  5. OpenStreetMap Nominatim and OSM REST API v0.6 geometry vertex counts and geodesic areas.
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import numpy as np
import rasterio
from pyproj import Geod
from rasterio.windows import Window

from eriwatch_geo.registry import fetch_osm_polygon

GEOD = Geod(ellps="WGS84")

PILOT_SAMPLE_TANKS: list[dict[str, Any]] = [
    {
        "id": "TN-KPM-001",
        "name": "Chembarambakkam Periya Eri",
        "district": "Kancheepuram",
        "block": "Kundrathur",
        "lat": 13.00822,
        "lon": 80.055489,
        "osm_type": "way",
        "osm_id": 25453624,
        "bbox": [80.0250, 12.9850, 80.0880, 13.0400],
    },
    {
        "id": "TN-CGL-001",
        "name": "Madurantakam Periya Eri",
        "district": "Chengalpattu",
        "block": "Madurantakam",
        "lat": 12.525171,
        "lon": 79.875534,
        "osm_type": "way",
        "osm_id": 176519614,
        "bbox": [79.8450, 12.4900, 79.8950, 12.5450],
    },
    {
        "id": "TN-KPM-002",
        "name": "Thenneri Hissa Eri",
        "district": "Kancheepuram",
        "block": "Walajabad",
        "lat": 12.851600,
        "lon": 79.885503,
        "osm_type": "way",
        "osm_id": 34108738,
        "bbox": [79.8650, 12.8420, 79.9020, 12.8780],
    },
    {
        "id": "TN-CGL-002",
        "name": "Kolavai Lake (Chengalpattu)",
        "district": "Chengalpattu",
        "block": "Kattankolathur",
        "lat": 12.707142,
        "lon": 79.988345,
        "osm_type": "way",
        "osm_id": 24161888,
        "bbox": [79.9700, 12.6880, 80.0020, 12.7280],
    },
]


def _geodesic_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    _, _, dist_m = GEOD.inv(lon1, lat1, lon2, lat2)
    return float(round(abs(float(dist_m)) / 1000.0, 2))


def _count_geojson_vertices(geom: dict[str, Any]) -> int:
    gtype = geom.get("type")
    coords = geom.get("coordinates", [])
    if gtype == "Polygon" and coords:
        return len(coords[0])
    if gtype == "MultiPolygon" and coords:
        return sum(len(poly[0]) for poly in coords if poly)
    if gtype == "Point":
        return 1
    return 0


def spike_planetary_computer_stac(client: httpx.Client) -> dict[str, Any]:
    """Query Planetary Computer STAC for all 2024 Sentinel-2 L2A scenes per tank."""
    url = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
    results: list[dict[str, Any]] = []
    for tank in PILOT_SAMPLE_TANKS:
        t0 = time.perf_counter()
        resp = client.post(
            url,
            json={
                "collections": ["sentinel-2-l2a"],
                "intersects": {"type": "Point", "coordinates": [tank["lon"], tank["lat"]]},
                "datetime": "2024-01-01T00:00:00Z/2024-12-31T23:59:59Z",
                "limit": 250,
            },
        )
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        resp.raise_for_status()
        features = resp.json().get("features", [])
        cloud_vals = [
            float(f["properties"]["eo:cloud_cover"])
            for f in features
            if f.get("properties", {}).get("eo:cloud_cover") is not None
        ]
        clear_lt_20 = [
            f
            for f in features
            if float(f.get("properties", {}).get("eo:cloud_cover", 100.0)) < 20.0
        ]
        clear_lt_40 = [
            f
            for f in features
            if float(f.get("properties", {}).get("eo:cloud_cover", 100.0)) < 40.0
        ]
        sample_scenes = [
            {
                "scene_id": f["id"],
                "date": f["properties"]["datetime"][:10],
                "cloud_cover_pct": round(float(f["properties"].get("eo:cloud_cover", 0.0)), 2),
            }
            for f in features[:5]
        ]
        f0 = features[0] if features else {}
        assets = list(f0.get("assets", {}).keys())
        results.append(
            {
                "tank_id": tank["id"],
                "tank_name": tank["name"],
                "status_code": resp.status_code,
                "elapsed_ms": elapsed_ms,
                "returned_scenes": len(features),
                "scenes_cloud_lt_20pct": len(clear_lt_20),
                "scenes_cloud_lt_40pct": len(clear_lt_40),
                "mean_cloud_cover_pct": round(float(np.mean(cloud_vals)), 2)
                if cloud_vals
                else None,
                "min_cloud_cover_pct": round(float(np.min(cloud_vals)), 3) if cloud_vals else None,
                "max_cloud_cover_pct": round(float(np.max(cloud_vals)), 2) if cloud_vals else None,
                "earliest_2024_date": features[-1]["properties"]["datetime"][:10]
                if features
                else None,
                "latest_2024_date": features[0]["properties"]["datetime"][:10]
                if features
                else None,
                "has_required_bands": all(b in assets for b in ["B03", "B08", "B11", "SCL"]),
                "sample_scenes": sample_scenes,
            }
        )
    return {
        "source": "Microsoft Planetary Computer STAC (sentinel-2-l2a)",
        "work_status": "WORKED_FULLY",
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
    resp_cdse = client.get(odata_url, params={"$filter": filter_expr, "$top": 5})
    cdse_ms = round((time.perf_counter() - t0) * 1000, 1)
    resp_cdse.raise_for_status()
    cdse_products = resp_cdse.json().get("value", [])

    e84_url = "https://earth-search.aws.element84.com/v1/search"
    t1 = time.perf_counter()
    resp_e84 = client.post(
        e84_url,
        json={
            "collections": ["sentinel-2-l2a"],
            "intersects": {"type": "Point", "coordinates": [tank["lon"], tank["lat"]]},
            "datetime": "2024-01-01T00:00:00Z/2024-12-31T23:59:59Z",
            "limit": 250,
        },
    )
    e84_ms = round((time.perf_counter() - t1) * 1000, 1)
    resp_e84.raise_for_status()
    e84_features = resp_e84.json().get("features", [])

    return {
        "source": "Element84 Earth Search STAC + Copernicus Data Space OData (Fallbacks)",
        "work_status": "WORKED_FULLY",
        "tank_id": tank["id"],
        "copernicus_odata": {
            "status_code": resp_cdse.status_code,
            "elapsed_ms": cdse_ms,
            "returned_products": len(cdse_products),
            "sample_products": [
                {
                    "name": p.get("Name"),
                    "start_date": p.get("ContentDate", {}).get("Start", "")[:10],
                }
                for p in cdse_products[:3]
            ],
        },
        "element84_stac_cog": {
            "status_code": resp_e84.status_code,
            "elapsed_ms": e84_ms,
            "returned_2024_scenes": len(e84_features),
            "sample_scenes": [
                {
                    "scene_id": f["id"],
                    "date": f["properties"]["datetime"][:10],
                    "cloud_cover_pct": round(float(f["properties"].get("eo:cloud_cover", 0.0)), 2),
                }
                for f in e84_features[:3]
            ],
        },
    }


def _get_jrc_sas_query(client: httpx.Client, sample_href: str) -> str:
    for attempt in range(4):
        resp = client.get(
            "https://planetarycomputer.microsoft.com/api/sas/v1/sign",
            params={"href": sample_href},
        )
        if resp.status_code == 429:
            time.sleep(2.0 * (attempt + 1))
            continue
        resp.raise_for_status()
        signed = str(resp.json()["href"])
        return signed.split("?", 1)[1]
    raise RuntimeError("Rate-limited by Planetary Computer SAS endpoint")


def spike_jrc_global_surface_water(client: httpx.Client) -> dict[str, Any]:
    """Query JRC Global Surface Water via Planetary Computer STAC and sample centroid pixels."""
    search_url = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
    sas_query: str | None = None

    results: list[dict[str, Any]] = []
    for tank in PILOT_SAMPLE_TANKS:
        t0 = time.perf_counter()
        resp = client.post(
            search_url,
            json={
                "collections": ["jrc-gsw"],
                "intersects": {"type": "Point", "coordinates": [tank["lon"], tank["lat"]]},
                "limit": 1,
            },
        )
        resp.raise_for_status()
        features = resp.json().get("features", [])
        f0 = features[0]
        assets = f0["assets"]

        if sas_query is None:
            sas_query = _get_jrc_sas_query(client, assets["occurrence"]["href"])

        occ_href = f"{assets['occurrence']['href']}?{sas_query}"
        ext_href = f"{assets['extent']['href']}?{sas_query}"
        sea_href = f"{assets['seasonality']['href']}?{sas_query}"

        with rasterio.open(occ_href) as src_occ:
            row, col = src_occ.index(tank["lon"], tank["lat"])
            win = Window(col - 2, row - 2, 5, 5)
            occ_patch = src_occ.read(1, window=win)
            centroid_occ = int(occ_patch[2, 2])
            patch_max_occ = int(occ_patch.max())

        with rasterio.open(ext_href) as src_ext:
            row, col = src_ext.index(tank["lon"], tank["lat"])
            win = Window(col - 2, row - 2, 5, 5)
            ext_patch = src_ext.read(1, window=win)
            centroid_ext = int(ext_patch[2, 2])

        with rasterio.open(sea_href) as src_sea:
            row, col = src_sea.index(tank["lon"], tank["lat"])
            win = Window(col - 2, row - 2, 5, 5)
            sea_patch = src_sea.read(1, window=win)
            centroid_sea = int(sea_patch[2, 2])

        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        results.append(
            {
                "tank_id": tank["id"],
                "tank_name": tank["name"],
                "status_code": resp.status_code,
                "elapsed_ms": elapsed_ms,
                "tile_id": f0.get("id"),
                "assets": list(assets.keys()),
                "centroid_lon_lat": [tank["lon"], tank["lat"]],
                "centroid_occurrence_pct": centroid_occ,
                "patch_5x5_max_occurrence_pct": patch_max_occ,
                "centroid_max_extent_flag": centroid_ext,
                "centroid_seasonality_months": centroid_sea,
            }
        )
    return {
        "source": (
            "JRC Global Surface Water (jrc-gsw via Planetary Computer STAC + COG pixel sampling)"
        ),
        "work_status": "WORKED_FULLY",
        "tanks": results,
    }


def spike_nasa_power_rainfall(client: httpx.Client) -> dict[str, Any]:
    """Query NASA POWER Daily Agroclimatology API (PRECTOTCORR) and record date-value series."""
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
        precip_raw = data.get("properties", {}).get("parameter", {}).get("PRECTOTCORR", {})
        daily_rain = {
            f"{k[:4]}-{k[4:6]}-{k[6:8]}": round(float(v), 2)
            for k, v in precip_raw.items()
            if float(v) >= 0
        }
        peak_date, peak_mm = max(daily_rain.items(), key=lambda kv: kv[1])
        results.append(
            {
                "tank_id": tank["id"],
                "tank_name": tank["name"],
                "status_code": resp.status_code,
                "elapsed_ms": elapsed_ms,
                "days_returned": len(daily_rain),
                "total_rain_mm_15d": round(sum(daily_rain.values()), 2),
                "peak_daily_rain_date": peak_date,
                "peak_daily_rain_mm": peak_mm,
                "daily_rainfall_mm": daily_rain,
            }
        )
    return {
        "source": "NASA POWER Agroclimatology API (PRECTOTCORR)",
        "work_status": "WORKED_FULLY",
        "tanks": results,
    }


def spike_osm_overpass(client: httpx.Client) -> dict[str, Any]:
    """Query OpenStreetMap Nominatim GeoJSON API and Direct OSM REST API v0.6 for vertex counts."""
    headers = {
        "User-Agent": "EriWatch-SAIU-Capstone/1.0 (https://github.com/sai-university/eriwatch)"
    }
    search_queries = {
        "TN-KPM-001": "Chembarambakkam Lake, Tamil Nadu",
        "TN-CGL-001": "Lake Maduranthakam, Tamil Nadu",
        "TN-KPM-002": "Thenneri, Walajabad, Tamil Nadu",
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
        nom_verts = _count_geojson_vertices(geom)

        # Also fetch direct OSM API v0.6 way geometry for exact water-body vertex count and area
        ring, area_ha = fetch_osm_polygon(tank["osm_type"], tank["osm_id"])

        results.append(
            {
                "tank_id": tank["id"],
                "tank_name": tank["name"],
                "nominatim_query": q,
                "status_code": resp.status_code,
                "elapsed_ms": elapsed_ms,
                "nominatim_osm_type": props.get("osm_type"),
                "nominatim_osm_id": props.get("osm_id"),
                "nominatim_geometry_type": geom.get("type"),
                "nominatim_vertex_count": nom_verts,
                "osm_api_v06_element": f"{tank['osm_type']}/{tank['osm_id']}",
                "osm_api_v06_vertex_count": len(ring),
                "osm_api_v06_geodesic_area_ha": area_ha,
            }
        )
        time.sleep(1.1)

    return {
        "source": "OpenStreetMap (Nominatim GeoJSON + Direct OSM REST API v0.6)",
        "work_status": "WORKED_PARTLY_NOMINATIM_FULLY_OSM_API",
        "tanks": results,
    }


def spike_groundwater_and_soil_moisture(client: httpx.Client) -> dict[str, Any]:
    """Query India-WRIS CGWB Groundwater stations, distances, and NASA POWER GWETPROF."""
    wris_url = "https://indiawris.gov.in/Dataset/Ground%20Water%20Level"
    t0 = time.perf_counter()
    r = client.post(
        wris_url,
        params={
            "stateName": "Tamil Nadu",
            "districtName": "Kancheepuram",
            "agencyName": "CGWB",
            "startdate": "2024-01-01",
            "enddate": "2024-01-05",
            "download": "false",
            "page": 0,
            "size": 500,
        },
        timeout=25.0,
    )
    wris_ms = round((time.perf_counter() - t0) * 1000, 1)
    r.raise_for_status()
    wris_json = r.json()
    records = wris_json.get("data", [])

    stations_by_code: dict[str, dict[str, Any]] = {}
    for rec in records:
        code = rec.get("stationCode")
        lat = rec.get("latitude")
        lon = rec.get("longitude")
        val = rec.get("dataValue")
        if not code or lat is None or lon is None or val is None:
            continue
        stations_by_code[code] = {
            "station_code": code,
            "station_name": rec.get("stationName"),
            "district": rec.get("district"),
            "tehsil_or_block": rec.get("tehsil"),
            "lat": float(lat),
            "lon": float(lon),
            "water_level_m_bgl": float(val),
            "reading_time": rec.get("dataTime"),
            "well_type": rec.get("wellType"),
            "well_depth_m": rec.get("wellDepth"),
        }

    station_list = list(stations_by_code.values())

    power_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    tank_gw_results: list[dict[str, Any]] = []
    for tank in PILOT_SAMPLE_TANKS:
        # Find nearest CGWB station to this tank
        ranked = sorted(
            station_list,
            key=lambda s: _geodesic_distance_km(tank["lat"], tank["lon"], s["lat"], s["lon"]),
        )
        nearest = ranked[0]
        dist_km = _geodesic_distance_km(tank["lat"], tank["lon"], nearest["lat"], nearest["lon"])

        t_p = time.perf_counter()
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
        power_ms = round((time.perf_counter() - t_p) * 1000, 1)
        resp.raise_for_status()
        params_data = resp.json().get("properties", {}).get("parameter", {})
        gwetprof = {
            f"{k[:4]}-{k[4:6]}-{k[6:8]}": round(float(v), 4)
            for k, v in params_data.get("GWETPROF", {}).items()
            if float(v) >= 0
        }
        tank_gw_results.append(
            {
                "tank_id": tank["id"],
                "tank_name": tank["name"],
                "nearest_cgwb_station": {
                    "station_code": nearest["station_code"],
                    "station_name": nearest["station_name"],
                    "station_lat": nearest["lat"],
                    "station_lon": nearest["lon"],
                    "distance_to_tank_km": dist_km,
                    "water_level_m_bgl": nearest["water_level_m_bgl"],
                    "reading_time": nearest["reading_time"],
                    "well_type": nearest["well_type"],
                },
                "nasa_power_gwetprof": {
                    "status_code": resp.status_code,
                    "elapsed_ms": power_ms,
                    "days_returned": len(gwetprof),
                    "mean_profile_wetness": round(
                        sum(gwetprof.values()) / max(1, len(gwetprof)), 4
                    ),
                    "daily_profile_wetness": gwetprof,
                },
            }
        )

    return {
        "source": "India-WRIS / CGWB Groundwater Stations + NASA POWER Profile Subsurface Wetness",
        "work_status": "WORKED_PARTLY_SPARSE_STATIONS_MITIGATED_WITH_GWETPROF",
        "india_wris_probe": {
            "status_code": r.status_code,
            "elapsed_ms": wris_ms,
            "records_returned": len(records),
            "unique_stations_parsed": len(station_list),
            "stations": station_list,
        },
        "nasa_power_subsurface_tanks": tank_gw_results,
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
    print(f"Wrote deep feasibility spike results to {out_path}")


if __name__ == "__main__":
    main()
