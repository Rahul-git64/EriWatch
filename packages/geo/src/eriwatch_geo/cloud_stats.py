"""Sentinel-2 L2A multi-year cloud-cover quantification across all pilot tanks (R4.1).

Queries STAC (`sentinel-2-l2a`, 2019-01-01 to present) across the pilot region,
maps every scene footprint to the 35 pilot tanks it covers, computes per-tank-per-month
scene counts, mean eo:cloud_cover, and shares of scenes with <20% and <40% cloud cover.
Saves the complete table to `data/processed/cloud_stats.parquet` and renders a
seasonality chart to `docs/data/cloud_cover_seasonality.png`.
"""

from __future__ import annotations

import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import matplotlib.pyplot as plt
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from shapely.geometry import Point, shape

from eriwatch_geo.registry import load_tank_registry

REPO_ROOT = Path(__file__).resolve().parents[4]
PARQUET_PATH = REPO_ROOT / "data" / "processed" / "cloud_stats.parquet"
CHART_PATH = REPO_ROOT / "docs" / "data" / "cloud_cover_seasonality.png"

STAC_SEARCH_URL = "https://earth-search.aws.element84.com/v1/search"
PILOT_BBOX = [79.55, 12.40, 80.30, 13.10]

MONTH_NAMES = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def fetch_stac_scenes_for_year(
    client: httpx.Client,
    year: int,
    bbox: list[float] | None = None,
) -> list[dict[str, Any]]:
    """Fetch all Sentinel-2 L2A scenes intersecting the pilot bbox in a calendar year."""
    target_bbox = bbox or PILOT_BBOX
    start_iso = f"{year}-01-01T00:00:00Z"
    end_iso = f"{year}-12-31T23:59:59Z"

    features: list[dict[str, Any]] = []
    next_body: dict[str, Any] | None = {
        "collections": ["sentinel-2-l2a"],
        "bbox": target_bbox,
        "datetime": f"{start_iso}/{end_iso}",
        "limit": 250,
    }

    while next_body is not None:
        resp: httpx.Response | None = None
        for attempt in range(4):
            try:
                resp = client.post(STAC_SEARCH_URL, json=next_body, timeout=45.0)
                if resp.status_code in (500, 502, 503, 504, 429):
                    time.sleep(1.5 * (attempt + 1))
                    continue
                resp.raise_for_status()
                break
            except httpx.HTTPError:
                if attempt == 3:
                    raise
                time.sleep(1.5 * (attempt + 1))
        assert resp is not None
        payload = resp.json()
        batch = payload.get("features", [])
        features.extend(batch)

        next_link = None
        for link in payload.get("links", []):
            if link.get("rel") == "next" and link.get("body"):
                next_link = link["body"]
                break
        next_body = next_link

    return features


def compute_cloud_stats(
    start_year: int = 2019,
    end_year: int | None = None,
) -> pa.Table:
    """Query STAC for 2019..end_year and build per-tank, per-year-month cloud statistics."""
    tanks = load_tank_registry(REPO_ROOT / "data" / "processed" / "tank_registry.geojson")
    tank_points = {t.id: (t.district, Point(t.centroid_lon, t.centroid_lat)) for t in tanks}

    current_year = end_year or datetime.now(UTC).year
    all_features: list[dict[str, Any]] = []

    with httpx.Client(
        headers={"User-Agent": "EriWatch-CloudStats/2.0 (academic research; Tamil Nadu)"},
        follow_redirects=True,
    ) as client:
        for yr in range(start_year, current_year + 1):
            yr_feats = fetch_stac_scenes_for_year(client, yr)
            all_features.extend(yr_feats)

    # Deduplicate by (tank_id, acquisition_date, grid_code), keeping lowest-cloud record
    tank_month_scenes: dict[tuple[str, int, int], dict[tuple[str, str], float]] = defaultdict(dict)

    for feat in all_features:
        props = feat.get("properties", {})
        dt_raw = str(props.get("datetime", ""))
        if len(dt_raw) < 10:
            continue
        cloud = props.get("eo:cloud_cover")
        if cloud is None:
            continue
        cloud_val = float(cloud)

        year = int(dt_raw[0:4])
        month = int(dt_raw[5:7])
        date_str = dt_raw[:10]
        grid_code = str(props.get("grid:code", feat.get("id", "")[:10]))

        geom_dict = feat.get("geometry")
        if not geom_dict:
            continue
        poly = shape(geom_dict)

        for tank_id, (_district, pt) in tank_points.items():
            if poly.contains(pt):
                pass_key = (date_str, grid_code)
                existing = tank_month_scenes[(tank_id, year, month)].get(pass_key)
                if existing is None or cloud_val < existing:
                    tank_month_scenes[(tank_id, year, month)][pass_key] = cloud_val

    rows: list[dict[str, Any]] = []
    for (tank_id, year, month), pass_map in sorted(tank_month_scenes.items()):
        clouds = list(pass_map.values())
        if not clouds:
            continue
        n_scenes = len(clouds)
        lt_20 = sum(1 for c in clouds if c < 20.0)
        lt_40 = sum(1 for c in clouds if c < 40.0)
        district = tank_points[tank_id][0]
        season = (
            "NE_Monsoon_Oct_Dec"
            if month in (10, 11, 12)
            else "SW_Monsoon_Jun_Sep"
            if month in (6, 7, 8, 9)
            else "Dry_Jan_May"
        )
        rows.append(
            {
                "tank_id": tank_id,
                "district": district,
                "year": year,
                "month": month,
                "year_month": f"{year:04d}-{month:02d}",
                "season": season,
                "scene_count": n_scenes,
                "mean_cloud_cover_pct": round(float(np.mean(clouds)), 2),
                "median_cloud_cover_pct": round(float(np.median(clouds)), 2),
                "min_cloud_cover_pct": round(float(np.min(clouds)), 2),
                "max_cloud_cover_pct": round(float(np.max(clouds)), 2),
                "scenes_lt_20pct": lt_20,
                "scenes_lt_40pct": lt_40,
                "share_lt_20pct": round(lt_20 / n_scenes, 4),
                "share_lt_40pct": round(lt_40 / n_scenes, 4),
            }
        )

    table = pa.Table.from_pylist(rows)
    return table


def render_seasonality_chart(table: pa.Table, output_path: Path | None = None) -> Path:
    """Plot monthly cloud-cover seasonality and usable pass shares across all 35 pilot tanks."""
    target = output_path or CHART_PATH
    target.parent.mkdir(parents=True, exist_ok=True)

    rows = table.to_pylist()
    by_month_clouds: dict[int, list[float]] = defaultdict(list)
    by_month_lt20: dict[int, list[float]] = defaultdict(list)
    by_month_lt40: dict[int, list[float]] = defaultdict(list)
    by_month_counts: dict[int, list[int]] = defaultdict(list)

    for r in rows:
        m = int(r["month"])
        by_month_clouds[m].append(float(r["mean_cloud_cover_pct"]))
        by_month_lt20[m].append(float(r["share_lt_20pct"]) * 100.0)
        by_month_lt40[m].append(float(r["share_lt_40pct"]) * 100.0)
        by_month_counts[m].append(int(r["scene_count"]))

    months = list(range(1, 13))
    mean_cloud = [float(np.mean(by_month_clouds[m])) for m in months]
    p25_cloud = [float(np.percentile(by_month_clouds[m], 25)) for m in months]
    p75_cloud = [float(np.percentile(by_month_clouds[m], 75)) for m in months]

    share_lt20 = [float(np.mean(by_month_lt20[m])) for m in months]
    share_lt40 = [float(np.mean(by_month_lt40[m])) for m in months]
    mean_scenes = [float(np.mean(by_month_counts[m])) for m in months]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True)

    # Highlight Northeast Monsoon (Oct-Dec, months 10..12 -> indices 9..11)
    for ax in (ax1, ax2):
        ax.axvspan(9.6, 12.4, color="#fee2e2", alpha=0.55, label="NE Monsoon (Oct-Dec)")
        ax.axvspan(5.6, 9.4, color="#fef3c7", alpha=0.40, label="SW Monsoon (Jun-Sep)")

    ax1.plot(
        months,
        mean_cloud,
        marker="o",
        linewidth=2.4,
        color="#dc2626",
        label="Mean eo:cloud_cover (%)",
    )
    ax1.fill_between(
        months,
        p25_cloud,
        p75_cloud,
        color="#fca5a5",
        alpha=0.35,
        label="IQR (25th-75th percentile)",
    )
    ax1.set_ylabel("Scene Cloud Cover (%)", fontsize=10, fontweight="bold")
    ax1.set_ylim(0, 100)
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.legend(loc="upper left", fontsize=8.5, ncol=2)
    ax1.set_title(
        "Sentinel-2 L2A Cloud-Cover Seasonality Across 35 Pilot Tanks (2019-Present)",
        fontsize=12,
        fontweight="bold",
    )

    width = 0.36
    x_arr = np.array(months, dtype=float)
    bars20 = ax2.bar(
        x_arr - width / 2,
        share_lt20,
        width=width,
        color="#0284c7",
        label="Share of passes < 20% cloud cover (%)",
    )
    bars40 = ax2.bar(
        x_arr + width / 2,
        share_lt40,
        width=width,
        color="#38bdf8",
        label="Share of passes < 40% cloud cover (%)",
    )

    for b in bars20:
        h = b.get_height()
        ax2.annotate(
            f"{h:.0f}%",
            xy=(b.get_x() + b.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=7.5,
            color="#0369a1",
            fontweight="bold",
        )
    for b in bars40:
        h = b.get_height()
        ax2.annotate(
            f"{h:.0f}%",
            xy=(b.get_x() + b.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=7.5,
            color="#0284c7",
        )

    ax2_rhs = ax2.twinx()
    ax2_rhs.plot(
        months,
        mean_scenes,
        color="#334155",
        linestyle=":",
        marker="s",
        linewidth=1.6,
        label="Mean passes / tank / month",
    )
    ax2_rhs.set_ylabel("Mean Passes / Tank / Month", fontsize=9.5, color="#334155")
    ax2_rhs.set_ylim(0, max(mean_scenes) * 1.4)

    ax2.set_ylabel("Usable Passes Share (%)", fontsize=10, fontweight="bold")
    ax2.set_xlabel("Calendar Month", fontsize=10, fontweight="bold")
    ax2.set_xticks(months)
    ax2.set_xticklabels(MONTH_NAMES, fontsize=9.5)
    ax2.set_ylim(0, 108)
    ax2.grid(True, linestyle="--", alpha=0.4)
    ax2.legend(loc="upper left", fontsize=8.5)
    ax2_rhs.legend(loc="upper right", fontsize=8.5)

    fig.tight_layout()
    fig.savefig(target, dpi=150)
    plt.close(fig)
    return target


def summarize_cloud_stats(table: pa.Table) -> dict[str, Any]:
    """Summarize seasonal cloud statistics for reporting and PROGRESS.md R-003."""
    rows = table.to_pylist()
    total_tank_months = len(rows)
    total_tank_scenes = sum(int(r["scene_count"]) for r in rows)

    by_season: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_season[str(r["season"])].append(r)

    season_summary: dict[str, Any] = {}
    for s_name, s_rows in sorted(by_season.items()):
        tot_sc = sum(int(r["scene_count"]) for r in s_rows)
        tot_20 = sum(int(r["scenes_lt_20pct"]) for r in s_rows)
        tot_40 = sum(int(r["scenes_lt_40pct"]) for r in s_rows)
        season_summary[s_name] = {
            "tank_months": len(s_rows),
            "total_tank_scenes": tot_sc,
            "mean_scenes_per_tank_month": round(tot_sc / len(s_rows), 2),
            "mean_cloud_cover_pct": round(
                float(np.mean([float(r["mean_cloud_cover_pct"]) for r in s_rows])), 2
            ),
            "share_lt_20pct": round((tot_20 / tot_sc) * 100.0, 2) if tot_sc else 0.0,
            "share_lt_40pct": round((tot_40 / tot_sc) * 100.0, 2) if tot_sc else 0.0,
            "expected_clean_passes_lt20_per_month": round(tot_20 / len(s_rows), 2),
            "expected_clean_passes_lt40_per_month": round(tot_40 / len(s_rows), 2),
        }

    return {
        "total_tank_months": total_tank_months,
        "total_tank_scenes": total_tank_scenes,
        "unique_tanks": len({str(r["tank_id"]) for r in rows}),
        "years_covered": sorted({int(r["year"]) for r in rows}),
        "seasons": season_summary,
    }


def main() -> None:
    PARQUET_PATH.parent.mkdir(parents=True, exist_ok=True)
    table = compute_cloud_stats(start_year=2019)
    pq.write_table(table, PARQUET_PATH, compression="snappy")
    chart_path = render_seasonality_chart(table, CHART_PATH)
    summary = summarize_cloud_stats(table)

    print(f"Wrote {table.num_rows} tank-month rows to {PARQUET_PATH}")
    print(f"Rendered seasonality chart to {chart_path}")
    print(f"Total tank-scene observations: {summary['total_tank_scenes']}")
    for s_name, stats in summary["seasons"].items():
        lt20_mo = stats["expected_clean_passes_lt20_per_month"]
        lt40_mo = stats["expected_clean_passes_lt40_per_month"]
        print(
            f"  [{s_name}] mean_cloud={stats['mean_cloud_cover_pct']}% | "
            f"scenes/mo={stats['mean_scenes_per_tank_month']} | "
            f"<20%={stats['share_lt_20pct']}% ({lt20_mo}/mo) | "
            f"<40%={stats['share_lt_40pct']}% ({lt40_mo}/mo)"
        )


if __name__ == "__main__":
    main()
