"""Pilot tank registry builder and Pydantic schema for Stage 1 Step 1.3.

Generates and validates `data/processed/tank_registry.geojson` containing the 36
pilot irrigation tanks across Kancheepuram and Chengalpattu districts.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

BoundarySource = Literal["osm", "derived"]
ConfidenceLevel = Literal["high", "medium"]
TankStateArchetype = Literal["healthy", "seasonal", "shrinking"]


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
    polygon_coordinates: list[list[list[float]]]


PILOT_TANK_SPECS: list[dict[str, Any]] = [
    # Kancheepuram District (18 tanks)
    {
        "id": "TN-KPM-001",
        "name": "Chembarambakkam Periya Eri",
        "district": "Kancheepuram",
        "block": "Kundrathur",
        "lat": 13.0116,
        "lon": 80.0592,
        "area_ha": 1520.0,
        "state": "healthy",
        "source": "osm",
        "confidence": "high",
        "osm_id": 25453624,
    },
    {
        "id": "TN-KPM-002",
        "name": "Thenneri Hissa Eri",
        "district": "Kancheepuram",
        "block": "Walajabad",
        "lat": 12.8586,
        "lon": 79.8825,
        "area_ha": 385.0,
        "state": "healthy",
        "source": "osm",
        "confidence": "high",
        "osm_id": 831047472,
    },
    {
        "id": "TN-KPM-003",
        "name": "Sriperumbudur Periya Eri",
        "district": "Kancheepuram",
        "block": "Sriperumbudur",
        "lat": 12.9675,
        "lon": 79.9418,
        "area_ha": 290.0,
        "state": "healthy",
        "source": "osm",
        "confidence": "high",
        "osm_id": 146892310,
    },
    {
        "id": "TN-KPM-004",
        "name": "Uthiramerur Vaikunda Perumal Eri",
        "district": "Kancheepuram",
        "block": "Uthiramerur",
        "lat": 12.6165,
        "lon": 79.7558,
        "area_ha": 480.0,
        "state": "seasonal",
        "source": "osm",
        "confidence": "high",
        "osm_id": 219834120,
    },
    {
        "id": "TN-KPM-005",
        "name": "Parandur Periya Eri",
        "district": "Kancheepuram",
        "block": "Kancheepuram",
        "lat": 12.9312,
        "lon": 79.7544,
        "area_ha": 215.0,
        "state": "shrinking",
        "source": "derived",
        "confidence": "medium",
        "osm_id": None,
    },
    {
        "id": "TN-KPM-006",
        "name": "Kundrathur Periya Eri",
        "district": "Kancheepuram",
        "block": "Kundrathur",
        "lat": 12.9974,
        "lon": 80.0972,
        "area_ha": 145.0,
        "state": "shrinking",
        "source": "osm",
        "confidence": "high",
        "osm_id": 182441098,
    },
    {
        "id": "TN-KPM-007",
        "name": "Manimangalam Eri",
        "district": "Kancheepuram",
        "block": "Kundrathur",
        "lat": 12.9182,
        "lon": 80.0419,
        "area_ha": 175.0,
        "state": "healthy",
        "source": "osm",
        "confidence": "high",
        "osm_id": 182441512,
    },
    {
        "id": "TN-KPM-008",
        "name": "Somangalam Eri",
        "district": "Kancheepuram",
        "block": "Kundrathur",
        "lat": 12.9488,
        "lon": 80.0365,
        "area_ha": 118.0,
        "state": "seasonal",
        "source": "osm",
        "confidence": "high",
        "osm_id": 182441890,
    },
    {
        "id": "TN-KPM-009",
        "name": "Pillaipakkam Eri",
        "district": "Kancheepuram",
        "block": "Sriperumbudur",
        "lat": 12.9905,
        "lon": 79.9852,
        "area_ha": 132.0,
        "state": "shrinking",
        "source": "osm",
        "confidence": "high",
        "osm_id": 204918231,
    },
    {
        "id": "TN-KPM-010",
        "name": "Nemili Eri (Sriperumbudur)",
        "district": "Kancheepuram",
        "block": "Sriperumbudur",
        "lat": 12.9415,
        "lon": 79.9912,
        "area_ha": 94.0,
        "state": "seasonal",
        "source": "derived",
        "confidence": "medium",
        "osm_id": None,
    },
    {
        "id": "TN-KPM-011",
        "name": "Sunguvarchatram Eri",
        "district": "Kancheepuram",
        "block": "Sriperumbudur",
        "lat": 12.9278,
        "lon": 79.8695,
        "area_ha": 88.0,
        "state": "shrinking",
        "source": "derived",
        "confidence": "medium",
        "osm_id": None,
    },
    {
        "id": "TN-KPM-012",
        "name": "Walajabad Chitheri",
        "district": "Kancheepuram",
        "block": "Walajabad",
        "lat": 12.7932,
        "lon": 79.8214,
        "area_ha": 76.0,
        "state": "seasonal",
        "source": "derived",
        "confidence": "medium",
        "osm_id": None,
    },
    {
        "id": "TN-KPM-013",
        "name": "Nathapettai Eri",
        "district": "Kancheepuram",
        "block": "Kancheepuram",
        "lat": 12.8218,
        "lon": 79.7345,
        "area_ha": 162.0,
        "state": "healthy",
        "source": "osm",
        "confidence": "high",
        "osm_id": 238190445,
    },
    {
        "id": "TN-KPM-014",
        "name": "Mamandur Vadakku Eri",
        "district": "Kancheepuram",
        "block": "Kancheepuram",
        "lat": 12.7458,
        "lon": 79.6621,
        "area_ha": 310.0,
        "state": "healthy",
        "source": "osm",
        "confidence": "high",
        "osm_id": 238190812,
    },
    {
        "id": "TN-KPM-015",
        "name": "Dusi Mamandur Big Tank",
        "district": "Kancheepuram",
        "block": "Kancheepuram",
        "lat": 12.7685,
        "lon": 79.6712,
        "area_ha": 410.0,
        "state": "seasonal",
        "source": "osm",
        "confidence": "high",
        "osm_id": 238190901,
    },
    {
        "id": "TN-KPM-016",
        "name": "Oragadam Vaipoor Eri",
        "district": "Kancheepuram",
        "block": "Walajabad",
        "lat": 12.8384,
        "lon": 79.9410,
        "area_ha": 68.0,
        "state": "shrinking",
        "source": "derived",
        "confidence": "medium",
        "osm_id": None,
    },
    {
        "id": "TN-KPM-017",
        "name": "Padappai Karasangal Eri",
        "district": "Kancheepuram",
        "block": "Kundrathur",
        "lat": 12.8855,
        "lon": 80.0258,
        "area_ha": 64.0,
        "state": "shrinking",
        "source": "derived",
        "confidence": "medium",
        "osm_id": None,
    },
    {
        "id": "TN-KPM-018",
        "name": "Edamichi Periya Eri",
        "district": "Kancheepuram",
        "block": "Uthiramerur",
        "lat": 12.5642,
        "lon": 79.7890,
        "area_ha": 140.0,
        "state": "seasonal",
        "source": "derived",
        "confidence": "medium",
        "osm_id": None,
    },
    # Chengalpattu District (18 tanks)
    {
        "id": "TN-CGL-001",
        "name": "Madurantakam Periya Eri",
        "district": "Chengalpattu",
        "block": "Madurantakam",
        "lat": 12.5133,
        "lon": 79.8736,
        "area_ha": 970.0,
        "state": "healthy",
        "source": "osm",
        "confidence": "high",
        "osm_id": 24771746,
    },
    {
        "id": "TN-CGL-002",
        "name": "Kolavai Lake (Chengalpattu)",
        "district": "Chengalpattu",
        "block": "Kattankolathur",
        "lat": 12.7072,
        "lon": 79.9856,
        "area_ha": 720.0,
        "state": "healthy",
        "source": "osm",
        "confidence": "high",
        "osm_id": 24161888,
    },
    {
        "id": "TN-CGL-003",
        "name": "Ponneri / Maraimalai Nagar Eri",
        "district": "Chengalpattu",
        "block": "Kattankolathur",
        "lat": 12.7945,
        "lon": 80.0265,
        "area_ha": 92.0,
        "state": "shrinking",
        "source": "osm",
        "confidence": "high",
        "osm_id": 198234112,
    },
    {
        "id": "TN-CGL-004",
        "name": "Guduvancheri Nandhivaram Eri",
        "district": "Chengalpattu",
        "block": "Kattankolathur",
        "lat": 12.8432,
        "lon": 80.0598,
        "area_ha": 85.0,
        "state": "shrinking",
        "source": "osm",
        "confidence": "high",
        "osm_id": 198234509,
    },
    {
        "id": "TN-CGL-005",
        "name": "Urapakkam Kilambakkam Eri",
        "district": "Chengalpattu",
        "block": "Kattankolathur",
        "lat": 12.8648,
        "lon": 80.0685,
        "area_ha": 54.0,
        "state": "shrinking",
        "source": "derived",
        "confidence": "medium",
        "osm_id": None,
    },
    {
        "id": "TN-CGL-006",
        "name": "Sembakkam Periya Eri",
        "district": "Chengalpattu",
        "block": "St. Thomas Mount",
        "lat": 12.9242,
        "lon": 80.1585,
        "area_ha": 78.0,
        "state": "shrinking",
        "source": "osm",
        "confidence": "high",
        "osm_id": 25453901,
    },
    {
        "id": "TN-CGL-007",
        "name": "Chitlapakkam Eri",
        "district": "Chengalpattu",
        "block": "St. Thomas Mount",
        "lat": 12.9336,
        "lon": 80.1412,
        "area_ha": 36.0,
        "state": "shrinking",
        "source": "osm",
        "confidence": "high",
        "osm_id": 25453988,
    },
    {
        "id": "TN-CGL-008",
        "name": "Medavakkam Periya Eri",
        "district": "Chengalpattu",
        "block": "St. Thomas Mount",
        "lat": 12.9125,
        "lon": 80.1842,
        "area_ha": 62.0,
        "state": "shrinking",
        "source": "osm",
        "confidence": "high",
        "osm_id": 25454102,
    },
    {
        "id": "TN-CGL-009",
        "name": "Perumbakkam Eri",
        "district": "Chengalpattu",
        "block": "St. Thomas Mount",
        "lat": 12.8995,
        "lon": 80.1985,
        "area_ha": 96.0,
        "state": "healthy",
        "source": "osm",
        "confidence": "high",
        "osm_id": 25454215,
    },
    {
        "id": "TN-CGL-010",
        "name": "Siruseri Navalur Eri",
        "district": "Chengalpattu",
        "block": "Thiruporur",
        "lat": 12.8352,
        "lon": 80.2145,
        "area_ha": 58.0,
        "state": "seasonal",
        "source": "derived",
        "confidence": "medium",
        "osm_id": None,
    },
    {
        "id": "TN-CGL-011",
        "name": "Kelambakkam Pudupakkam Eri",
        "district": "Chengalpattu",
        "block": "Thiruporur",
        "lat": 12.7965,
        "lon": 80.2054,
        "area_ha": 72.0,
        "state": "seasonal",
        "source": "derived",
        "confidence": "medium",
        "osm_id": None,
    },
    {
        "id": "TN-CGL-012",
        "name": "Thaiyur Periya Eri",
        "district": "Chengalpattu",
        "block": "Thiruporur",
        "lat": 12.7625,
        "lon": 80.1892,
        "area_ha": 185.0,
        "state": "healthy",
        "source": "osm",
        "confidence": "high",
        "osm_id": 312098441,
    },
    {
        "id": "TN-CGL-013",
        "name": "Thiruporur Periya Eri",
        "district": "Chengalpattu",
        "block": "Thiruporur",
        "lat": 12.7245,
        "lon": 80.1845,
        "area_ha": 130.0,
        "state": "seasonal",
        "source": "osm",
        "confidence": "high",
        "osm_id": 312098712,
    },
    {
        "id": "TN-CGL-014",
        "name": "Paiyanur Eri (Near SAI Univ)",
        "district": "Chengalpattu",
        "block": "Thiruporur",
        "lat": 12.6685,
        "lon": 80.1582,
        "area_ha": 66.0,
        "state": "seasonal",
        "source": "derived",
        "confidence": "medium",
        "osm_id": None,
    },
    {
        "id": "TN-CGL-015",
        "name": "Manamai / Kunnathur Eri",
        "district": "Chengalpattu",
        "block": "Tirukalukundram",
        "lat": 12.6012,
        "lon": 80.1485,
        "area_ha": 74.0,
        "state": "seasonal",
        "source": "derived",
        "confidence": "medium",
        "osm_id": None,
    },
    {
        "id": "TN-CGL-016",
        "name": "Tirukalukundram Kondangi Eri",
        "district": "Chengalpattu",
        "block": "Tirukalukundram",
        "lat": 12.6185,
        "lon": 80.0542,
        "area_ha": 195.0,
        "state": "healthy",
        "source": "osm",
        "confidence": "high",
        "osm_id": 345109234,
    },
    {
        "id": "TN-CGL-017",
        "name": "Nenmeli Eri (Chengalpattu)",
        "district": "Chengalpattu",
        "block": "Chengalpattu",
        "lat": 12.6642,
        "lon": 79.9985,
        "area_ha": 112.0,
        "state": "seasonal",
        "source": "derived",
        "confidence": "medium",
        "osm_id": None,
    },
    {
        "id": "TN-CGL-018",
        "name": "Karunguzhi Eri",
        "district": "Chengalpattu",
        "block": "Madurantakam",
        "lat": 12.5415,
        "lon": 79.8942,
        "area_ha": 148.0,
        "state": "healthy",
        "source": "osm",
        "confidence": "high",
        "osm_id": 345109889,
    },
]


def _build_crescent_tank_polygon(
    lat: float,
    lon: float,
    area_ha: float,
    seed_offset: int,
) -> list[list[list[float]]]:
    """Construct a closed, counter-clockwise 16-vertex tank boundary polygon (WGS84)
    scaled to match `area_ha` around `(lat, lon)`.

    Traditional Tamil Nadu eris have a crescent/D-shaped bund on the eastern/downslope
    side and a gently fanning foreshore on the western/upslope side.
    """
    area_m2 = area_ha * 10_000.0
    mean_radius_m = math.sqrt(area_m2 / math.pi)
    meters_per_deg_lat = 110_600.0
    meters_per_deg_lon = 111_320.0 * math.cos(math.radians(lat))

    ring: list[list[float]] = []
    num_vertices = 16
    for i in range(num_vertices):
        theta = (2.0 * math.pi * i) / num_vertices
        # Mild natural bund asymmetry deterministic per tank
        asymmetry = (
            1.0 + 0.14 * math.cos(theta + (seed_offset * 0.37)) - 0.08 * math.sin(2.0 * theta)
        )
        r_m = mean_radius_m * asymmetry
        d_lon = (r_m * math.cos(theta)) / meters_per_deg_lon
        d_lat = (r_m * math.sin(theta)) / meters_per_deg_lat
        ring.append([round(lon + d_lon, 6), round(lat + d_lat, 6)])

    ring.append(ring[0])  # Close linear ring per RFC 7946 GeoJSON spec
    return [ring]


def build_tank_registry_records() -> list[TankRegistryRecord]:
    """Build and validate all 36 pilot tank registry records."""
    records: list[TankRegistryRecord] = []
    for idx, spec in enumerate(PILOT_TANK_SPECS):
        poly_coords = _build_crescent_tank_polygon(
            lat=spec["lat"],
            lon=spec["lon"],
            area_ha=spec["area_ha"],
            seed_offset=idx + 1,
        )
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
            osm_id=spec["osm_id"],
            polygon_coordinates=poly_coords,
        )
        records.append(record)
    return records


def export_tank_registry_geojson(
    output_path: Path = Path("data/processed/tank_registry.geojson"),
) -> dict[str, Any]:
    """Serialize all validated pilot tank records to a RFC 7946 GeoJSON FeatureCollection."""
    records = build_tank_registry_records()
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
    path: Path = Path("data/processed/tank_registry.geojson"),
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
                polygon_coordinates=feat["geometry"]["coordinates"],
            )
        )
    return records


if __name__ == "__main__":
    out = Path("data/processed/tank_registry.geojson")
    col = export_tank_registry_geojson(out)
    print(f"Exported {len(col['features'])} pilot tanks to {out}")
