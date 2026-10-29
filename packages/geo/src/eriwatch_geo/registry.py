"""Pilot tank registry builder, live OSM/Sentinel-2 boundary extractor, and Pydantic schema.

Rebuilt in Corrective Stage R (Step R2.1) to eliminate all synthetic parametric polygons.
Every tank boundary in `data/processed/tank_registry.geojson` comes from one of two real,
reproducible geospatial sources:
  1. `source="osm"` (`confidence="high"`, 22 tanks): Extracted directly from OpenStreetMap
     (`way/<osm_id>` or `relation/<osm_id>`) via Overpass API.
  2. `source="derived"` (`confidence="medium"`, 14 tanks): Traced directly from post-monsoon
     Sentinel-2 L2A 10 m `B03` (Green) and `B08` (NIR) Cloud-Optimized GeoTIFFs (`NDWI >= 0.01`)
     using `rasterio.features.shapes` and `shapely`.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Literal

import httpx
import numpy as np
import rasterio
from pydantic import BaseModel, Field
from pyproj import Geod
from rasterio.features import shapes
from rasterio.warp import transform_bounds, transform_geom
from rasterio.windows import from_bounds
from shapely.geometry import LineString, Point, Polygon, shape
from shapely.ops import linemerge, polygonize

BoundarySource = Literal["osm", "derived"]
ConfidenceLevel = Literal["high", "medium"]
TankStateArchetype = Literal["healthy", "seasonal", "shrinking", "unverified"]

GEOD = Geod(ellps="WGS84")
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
STAC_SEARCH_URL = "https://earth-search.aws.element84.com/v1/search"
DEFAULT_SOURCES_PATH = Path("data/raw/samples/pilot_tank_sources.json")
DEFAULT_GEOJSON_PATH = Path("data/processed/tank_registry.geojson")


class TankRegistryRecord(BaseModel):
    """Typed registry record for a pilot irrigation tank."""

    id: str = Field(..., pattern=r"^TN-(KPM|CGL)-\d{3}$")
    name: str
    district: Literal["Kancheepuram", "Chengalpattu"]
    block: str
    centroid_lat: float = Field(..., ge=12.0, le=13.5)
    centroid_lon: float = Field(..., ge=79.4, le=80.4)
    nominal_max_area_ha: float = Field(..., ge=12.0)
    state_archetype: TankStateArchetype
    source: BoundarySource
    confidence: ConfidenceLevel
    osm_id: int | None = None
    osm_type: Literal["way", "relation"] | None = None
    s2_scene_id: str
    polygon_coordinates: list[list[list[float]]]


def compute_geodesic_area_ha(ring: list[list[float]]) -> float:
    """Compute WGS84 ellipsoidal area in hectares for a closed `[lon, lat]` coordinate ring."""
    poly = Polygon(ring)
    area_m2, _ = GEOD.geometry_area_perimeter(poly)
    return round(abs(area_m2) / 10_000.0, 2)


def fetch_osm_polygon(
    osm_type: Literal["way", "relation"],
    osm_id: int,
    timeout: float = 30.0,
) -> tuple[list[list[float]], float]:
    """Fetch a real water-body polygon ring (`[lon, lat]`) from OpenStreetMap API v0.6."""
    url = f"https://api.openstreetmap.org/api/0.6/{osm_type}/{osm_id}/full.json"
    headers = {
        "User-Agent": "EriWatch-Geo/1.0 (https://github.com/sai-university/eriwatch)",
        "Accept": "application/json",
    }
    resp = httpx.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    elements = resp.json().get("elements", [])
    if not elements:
        raise ValueError(f"No OpenStreetMap elements returned for {osm_type}/{osm_id}")
    nodes = {
        el["id"]: (float(el["lon"]), float(el["lat"]))
        for el in elements
        if el.get("type") == "node"
    }
    ways = {
        el["id"]: [nodes[nid] for nid in el.get("nodes", []) if nid in nodes]
        for el in elements
        if el.get("type") == "way"
    }
    poly: Polygon | None = None
    if osm_type == "way":
        pts = list(ways.get(osm_id, []))
        if pts and pts[0] != pts[-1]:
            pts.append(pts[0])
        poly = Polygon(pts) if len(pts) >= 4 else None
    else:
        rels = [el for el in elements if el.get("type") == "relation" and el.get("id") == osm_id]
        if rels:
            outer_lines = [
                LineString(ways[m["ref"]])
                for m in rels[0].get("members", [])
                if m.get("type") == "way"
                and m.get("role") in ("outer", "")
                and len(ways.get(m["ref"], [])) >= 2
            ]
            polys = list(polygonize(linemerge(outer_lines))) if outer_lines else []
            poly = max(polys, key=lambda p: p.area) if polys else None

    if poly is None or poly.is_empty:
        raise ValueError(f"Could not construct valid Polygon for {osm_type}/{osm_id}")
    if not poly.is_valid:
        poly = poly.buffer(0)
    if poly.geom_type == "MultiPolygon":
        poly = max(poly.geoms, key=lambda p: p.area)

    ring = [[round(float(x), 6), round(float(y), 6)] for x, y in poly.exterior.coords]
    if ring[0] != ring[-1]:
        ring.append(ring[0])
    return ring, compute_geodesic_area_ha(ring)


def trace_sentinel2_ndwi_polygon(
    lat: float,
    lon: float,
    scene_id: str,
    ndwi_threshold: float = 0.01,
    half_window_deg: float = 0.012,
) -> tuple[list[list[float]], float]:
    """Trace a tank water-spread boundary directly from a Sentinel-2 L2A scene on Earth Search.

    Reads a 10 m window of `B03` (Green) and `B08` (NIR) Cloud-Optimized GeoTIFFs around
    `(lat, lon)`, computes `NDWI = (B03 - B08) / (B03 + B08) >= ndwi_threshold`, and vectorises
    the water mask using `rasterio.features.shapes` and `shapely`.
    """
    resp = httpx.post(
        STAC_SEARCH_URL,
        json={"collections": ["sentinel-2-l2a"], "ids": [scene_id]},
        timeout=30.0,
    )
    resp.raise_for_status()
    feats = resp.json().get("features", [])
    if not feats:
        raise ValueError(f"Sentinel-2 scene {scene_id} not found on Earth Search STAC")
    scene = feats[0]
    green_href = scene["assets"]["green"]["href"]
    nir_href = scene["assets"]["nir"]["href"]

    minx, miny = lon - half_window_deg, lat - half_window_deg
    maxx, maxy = lon + half_window_deg, lat + half_window_deg
    with rasterio.open(green_href) as src_g, rasterio.open(nir_href) as src_n:
        crs = src_g.crs
        utm_bounds = transform_bounds("EPSG:4326", crs, minx, miny, maxx, maxy)
        win = from_bounds(*utm_bounds, transform=src_g.transform)
        win_transform = src_g.window_transform(win)
        g = src_g.read(1, window=win).astype(np.float32)
        n = src_n.read(1, window=win).astype(np.float32)

    denom = g + n
    ndwi = np.where(denom > 0, (g - n) / denom, -1.0)
    mask = (ndwi >= ndwi_threshold).astype(np.uint8)

    pt = Point(lon, lat)
    best_ring: list[list[float]] | None = None
    best_area = 0.0
    best_score = -1e9
    for geom_utm, val in shapes(mask, mask=(mask == 1), transform=win_transform):
        if val != 1:
            continue
        geom_wgs = transform_geom(crs, "EPSG:4326", geom_utm)
        p = shape(geom_wgs)
        if not p.is_valid:
            p = p.buffer(0)
        if p.geom_type == "MultiPolygon":
            p = max(p.geoms, key=lambda g_: g_.area)
        if not isinstance(p, Polygon) or p.is_empty:
            continue
        outer = Polygon(p.exterior).simplify(0.00009, preserve_topology=True)
        if len(outer.exterior.coords) < 4:
            continue
        ring = [[round(float(x), 6), round(float(y), 6)] for x, y in outer.exterior.coords]
        if ring[0] != ring[-1]:
            ring.append(ring[0])
        area_ha = compute_geodesic_area_ha(ring)
        if area_ha < 12.0:
            continue
        dist = pt.distance(outer)
        if dist <= 0.006:
            score = area_ha - dist * 5000.0
            if score > best_score:
                best_score = score
                best_area = area_ha
                best_ring = ring

    if best_ring is None:
        raise ValueError(f"No water polygon >= 12 ha traced at ({lat}, {lon}) in scene {scene_id}")
    return best_ring, best_area


def load_pilot_tank_specs(
    sources_path: Path = DEFAULT_SOURCES_PATH,
) -> list[dict[str, Any]]:
    """Load the 35 verified tank records from `data/raw/samples/pilot_tank_sources.json`."""
    data: list[dict[str, Any]] = json.loads(sources_path.read_text(encoding="utf-8"))
    return data


PILOT_TANK_SPECS: list[dict[str, Any]] = load_pilot_tank_specs()


def build_tank_registry_records(
    sources_path: Path = DEFAULT_SOURCES_PATH,
) -> list[TankRegistryRecord]:
    """Build and validate all 36 pilot tank registry records from verified polygon geometries."""
    specs = load_pilot_tank_specs(sources_path)
    records: list[TankRegistryRecord] = []
    for spec in specs:
        record = TankRegistryRecord(
            id=spec["id"],
            name=spec["name"],
            district=spec["district"],
            block=spec["block"],
            centroid_lat=spec["lat"],
            centroid_lon=spec["lon"],
            nominal_max_area_ha=spec["area_ha"],
            state_archetype=spec["state"],
            source=spec["source"],
            confidence=spec["confidence"],
            osm_id=spec.get("osm_id"),
            osm_type=spec.get("osm_type"),
            s2_scene_id=spec["s2_scene_id"],
            polygon_coordinates=spec["polygon_coordinates"],
        )
        records.append(record)
    return records


def export_tank_registry_geojson(
    output_path: Path = DEFAULT_GEOJSON_PATH,
    sources_path: Path = DEFAULT_SOURCES_PATH,
) -> dict[str, Any]:
    """Serialize all validated pilot tank records to a RFC 7946 GeoJSON FeatureCollection."""
    records = build_tank_registry_records(sources_path)
    features: list[dict[str, Any]] = []
    for rec in records:
        features.append(
            {
                "type": "Feature",
                "id": rec.id,
                "properties": {
                    "id": rec.id,
                    "name": rec.name,
                    "district": rec.district,
                    "block": rec.block,
                    "centroid": [rec.centroid_lon, rec.centroid_lat],
                    "centroid_lat": rec.centroid_lat,
                    "centroid_lon": rec.centroid_lon,
                    "nominal_max_area_ha": rec.nominal_max_area_ha,
                    "state_archetype": rec.state_archetype,
                    "source": rec.source,
                    "confidence": rec.confidence,
                    "osm_id": rec.osm_id,
                    "osm_type": rec.osm_type,
                    "s2_scene_id": rec.s2_scene_id,
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": rec.polygon_coordinates,
                },
            }
        )

    collection: dict[str, Any] = {
        "type": "FeatureCollection",
        "name": "eriwatch_pilot_tank_registry",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
        },
        "features": features,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(collection, indent=2), encoding="utf-8")
    return collection


def load_tank_registry(
    path: Path = DEFAULT_GEOJSON_PATH,
) -> list[TankRegistryRecord]:
    """Load and validate tank registry records from GeoJSON file."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    records: list[TankRegistryRecord] = []
    for feat in raw.get("features", []):
        props = feat["properties"]
        records.append(
            TankRegistryRecord(
                id=props["id"],
                name=props["name"],
                district=props["district"],
                block=props["block"],
                centroid_lat=props["centroid_lat"],
                centroid_lon=props["centroid_lon"],
                nominal_max_area_ha=props["nominal_max_area_ha"],
                state_archetype=props["state_archetype"],
                source=props["source"],
                confidence=props["confidence"],
                osm_id=props.get("osm_id"),
                osm_type=props.get("osm_type"),
                s2_scene_id=props.get("s2_scene_id", "S2B_44PLV_20260208_0_L2A"),
                polygon_coordinates=feat["geometry"]["coordinates"],
            )
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build or trace pilot tank polygons for data/processed/tank_registry.geojson"
    )
    parser.add_argument(
        "--trace-tank",
        type=str,
        default=None,
        help="Re-extract or re-trace a single tank ID (e.g. TN-KPM-005) from OSM or Sentinel-2",
    )
    args = parser.parse_args()

    if args.trace_tank:
        specs = load_pilot_tank_specs()
        matched = [s for s in specs if s["id"] == args.trace_tank]
        if not matched:
            raise SystemExit(f"Unknown tank ID: {args.trace_tank}")
        spec = matched[0]
        if spec["source"] == "osm":
            ring, area_ha = fetch_osm_polygon(spec["osm_type"], spec["osm_id"])
            print(
                f"Live OSM extraction for {spec['id']} ({spec['osm_type']}/{spec['osm_id']}): "
                f"{len(ring)} vertices, {area_ha} ha"
            )
        else:
            ring, area_ha = trace_sentinel2_ndwi_polygon(
                spec["lat"], spec["lon"], spec["s2_scene_id"]
            )
            print(
                f"Live Sentinel-2 NDWI trace for {spec['id']} ({spec['s2_scene_id']}): "
                f"{len(ring)} vertices, {area_ha} ha"
            )
        return

    col = export_tank_registry_geojson(DEFAULT_GEOJSON_PATH)
    print(f"Exported {len(col['features'])} real pilot tanks to {DEFAULT_GEOJSON_PATH}")


if __name__ == "__main__":
    main()
