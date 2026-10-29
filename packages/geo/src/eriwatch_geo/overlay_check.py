"""Sentinel-2 L2A RGB + NDWI water-mask + polygon overlay check (Corrective Stage R Step R2.3).

For every tank in `data/processed/tank_registry.geojson`, fetches one clear post-monsoon
Sentinel-2 L2A scene (`2026-02-08`, `< 1.5%` cloud cover across tiles `44PLV`, `44PLU`, `44PMV`),
renders a 2-panel figure (True-Color RGB + NDWI water-mask preview) with the tank polygon outline
overlaid, saves `docs/data/overlays/<TANK_ID>.png`, and writes quantitative match metrics to
`docs/data/overlays/overlay_summary.json`.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
from typing import Any

import httpx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.warp import transform_bounds, transform_geom
from rasterio.windows import from_bounds
from shapely.geometry import Polygon

from eriwatch_geo.registry import TankRegistryRecord, load_tank_registry

STAC_SEARCH_URL = "https://earth-search.aws.element84.com/v1/search"
DEFAULT_OVERLAYS_DIR = Path("docs/data/overlays")


def _fetch_stac_scenes(scene_ids: list[str]) -> dict[str, dict[str, Any]]:
    resp = httpx.post(
        STAC_SEARCH_URL,
        json={"collections": ["sentinel-2-l2a"], "ids": scene_ids},
        timeout=30.0,
    )
    resp.raise_for_status()
    return {f["id"]: f for f in resp.json().get("features", [])}


def _read_band_windows_for_scene(
    href: str,
    tank_windows: list[tuple[str, tuple[float, float, float, float]]],
) -> dict[str, tuple[np.ndarray, Any, Any]]:
    """Open a single COG band once and read all tank windows in that tile."""
    out: dict[str, tuple[np.ndarray, Any, Any]] = {}
    with rasterio.open(href) as src:
        crs = src.crs
        for tank_id, (minx, miny, maxx, maxy) in tank_windows:
            utm_bounds = transform_bounds("EPSG:4326", crs, minx, miny, maxx, maxy)
            win = from_bounds(*utm_bounds, transform=src.transform)
            win_transform = src.window_transform(win)
            arr = src.read(1, window=win).astype(np.float32)
            out[tank_id] = (arr, win_transform, crs)
    return out


def _stretch_rgb(r: np.ndarray, g: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Contrast-stretch 10 m Sentinel-2 surface reflectance bands to [0, 1] RGB."""
    rgb = np.stack([r, g, b], axis=-1)
    valid = rgb[rgb > 0]
    if valid.size == 0:
        return np.zeros_like(rgb)
    lo = float(np.percentile(valid, 2))
    hi = float(np.percentile(valid, 98))
    if hi <= lo:
        hi = lo + 1.0
    stretched = np.clip((rgb - lo) / (hi - lo), 0.0, 1.0)
    # Mild gamma for perceptual clarity
    return np.power(stretched, 0.85)


def generate_all_tank_overlays(
    overlays_dir: Path = DEFAULT_OVERLAYS_DIR,
) -> dict[str, Any]:
    """Generate `docs/data/overlays/<TANK_ID>.png` and `overlay_summary.json` for all pilot tanks."""
    records = load_tank_registry()
    overlays_dir.mkdir(parents=True, exist_ok=True)

    by_scene: dict[str, list[TankRegistryRecord]] = {}
    for rec in records:
        by_scene.setdefault(rec.s2_scene_id, []).append(rec)

    scenes = _fetch_stac_scenes(list(by_scene.keys()))
    summary_rows: list[dict[str, Any]] = []

    for scene_id, scene_records in by_scene.items():
        scene = scenes[scene_id]
        dt_str = scene["properties"]["datetime"][:10]
        cloud_pct = round(float(scene["properties"].get("eo:cloud_cover", 0.0)), 3)

        tank_windows: list[tuple[str, tuple[float, float, float, float]]] = []
        tank_bounds_map: dict[str, tuple[float, float, float, float]] = {}
        for rec in scene_records:
            poly = Polygon(rec.polygon_coordinates[0])
            minx, miny, maxx, maxy = poly.bounds
            dx = max((maxx - minx) * 0.35, 0.004)
            dy = max((maxy - miny) * 0.35, 0.004)
            b = (minx - dx, miny - dy, maxx + dx, maxy + dy)
            tank_windows.append((rec.id, b))
            tank_bounds_map[rec.id] = b

        band_hrefs = {
            "red": scene["assets"]["red"]["href"],
            "green": scene["assets"]["green"]["href"],
            "blue": scene["assets"]["blue"]["href"],
            "nir": scene["assets"]["nir"]["href"],
        }

        print(f"Reading 4 bands in parallel for {len(scene_records)} tanks in {scene_id} ...")
        band_data: dict[str, dict[str, tuple[np.ndarray, Any, Any]]] = {}
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {
                band: pool.submit(_read_band_windows_for_scene, href, tank_windows)
                for band, href in band_hrefs.items()
            }
            for band, fut in futures.items():
                band_data[band] = fut.result()

        for rec in scene_records:
            r, win_transform, crs = band_data["red"][rec.id]
            g, _, _ = band_data["green"][rec.id]
            b_arr, _, _ = band_data["blue"][rec.id]
            n, _, _ = band_data["nir"][rec.id]

            denom = g + n
            ndwi = np.where(denom > 0, (g - n) / denom, -1.0)
            water_mask = ndwi >= 0.0

            # Rasterize tank polygon in UTM window to measure inside-polygon water pixels
            poly_wgs = {"type": "Polygon", "coordinates": rec.polygon_coordinates}
            poly_utm = transform_geom("EPSG:4326", crs, poly_wgs)
            poly_mask = rasterize(
                [(poly_utm, 1)],
                out_shape=g.shape,
                transform=win_transform,
                fill=0,
                dtype=np.uint8,
            ).astype(bool)

            inside_total_px = int(poly_mask.sum())
            inside_water_px = int((poly_mask & water_mask).sum())
            window_water_px = int(water_mask.sum())
            inside_water_ha = round(inside_water_px * 0.01, 2)
            inside_water_ratio = (
                round(inside_water_px / inside_total_px, 3) if inside_total_px > 0 else 0.0
            )
            matches_water_body = bool(inside_water_px >= 250 and inside_water_ratio >= 0.15)

            minx, miny, maxx, maxy = tank_bounds_map[rec.id]
            extent = [minx, maxx, miny, maxy]
            ring = rec.polygon_coordinates[0]
            xs = [pt[0] for pt in ring]
            ys = [pt[1] for pt in ring]

            rgb_img = _stretch_rgb(r, g, b_arr)

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), dpi=120)
            fig.suptitle(
                f"{rec.id}: {rec.name} ({rec.district} / {rec.block})\n"
                f"Source: {rec.source} (confidence={rec.confidence}) | Nominal Area: {rec.nominal_max_area_ha:.2f} ha | "
                f"Scene: {scene_id} ({dt_str}, cloud={cloud_pct}%)",
                fontsize=10.5,
                fontweight="bold",
            )

            ax1.imshow(rgb_img, extent=extent, origin="upper", aspect="auto")
            ax1.plot(xs, ys, color="#00E5FF", linewidth=2.0, label="Tank Polygon")
            ax1.set_title("Sentinel-2 True Color RGB (B04/B03/B02) + Polygon", fontsize=9.5)
            ax1.set_xlabel("Longitude (°E)")
            ax1.set_ylabel("Latitude (°N)")
            ax1.legend(loc="upper right", fontsize=8)

            im2 = ax2.imshow(
                ndwi,
                extent=extent,
                origin="upper",
                aspect="auto",
                cmap="RdYlBu",
                vmin=-0.4,
                vmax=0.5,
            )
            ax2.contour(
                np.linspace(minx, maxx, ndwi.shape[1]),
                np.linspace(maxy, miny, ndwi.shape[0]),
                water_mask.astype(float),
                levels=[0.5],
                colors=["#004D40"],
                linewidths=1.0,
            )
            ax2.plot(xs, ys, color="#FF1744", linewidth=2.0, label="Tank Polygon")
            ax2.set_title(
                f"NDWI Water Mask (inside water: {inside_water_ha:.1f} ha, "
                f"{inside_water_ratio * 100:.1f}% of polygon)",
                fontsize=9.5,
            )
            ax2.set_xlabel("Longitude (°E)")
            ax2.set_ylabel("Latitude (°N)")
            ax2.legend(loc="upper right", fontsize=8)
            fig.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04, label="NDWI")

            fig.tight_layout()
            out_png = overlays_dir / f"{rec.id}.png"
            fig.savefig(out_png)
            plt.close(fig)

            summary_rows.append(
                {
                    "id": rec.id,
                    "name": rec.name,
                    "district": rec.district,
                    "source": rec.source,
                    "confidence": rec.confidence,
                    "scene_id": scene_id,
                    "scene_date": dt_str,
                    "nominal_max_area_ha": rec.nominal_max_area_ha,
                    "inside_polygon_px": inside_total_px,
                    "inside_water_px": inside_water_px,
                    "inside_water_ha": inside_water_ha,
                    "inside_water_ratio": inside_water_ratio,
                    "window_water_px": window_water_px,
                    "matches_real_water_body": matches_water_body,
                    "overlay_png": f"docs/data/overlays/{rec.id}.png",
                }
            )

    summary_rows.sort(key=lambda r: r["id"])
    matched_count = sum(1 for r in summary_rows if r["matches_real_water_body"])
    summary = {
        "total_tanks_checked": len(summary_rows),
        "matched_water_body_count": matched_count,
        "failed_count": len(summary_rows) - matched_count,
        "tanks": summary_rows,
    }
    summary_path = overlays_dir / "overlay_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    res = generate_all_tank_overlays()
    print(
        f"Generated {res['total_tanks_checked']} overlay PNGs: "
        f"{res['matched_water_body_count']}/{res['total_tanks_checked']} visibly match a real water body"
    )
