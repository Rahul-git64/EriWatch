"""Tests for Sentinel-2 L2A multi-year cloud-cover statistics and seasonality chart (R4.1)."""

from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq

from eriwatch_geo.cloud_stats import CHART_PATH, PARQUET_PATH, summarize_cloud_stats


def test_cloud_stats_parquet_and_seasonality_chart() -> None:
    assert PARQUET_PATH.exists(), f"Missing cloud stats parquet: {PARQUET_PATH}"
    assert CHART_PATH.exists(), f"Missing cloud seasonality chart: {CHART_PATH}"
    assert CHART_PATH.stat().st_size > 25_000, "Seasonality chart PNG is unexpectedly small"

    table = pq.read_table(PARQUET_PATH)
    required_cols = {
        "tank_id",
        "district",
        "year",
        "month",
        "year_month",
        "season",
        "scene_count",
        "mean_cloud_cover_pct",
        "scenes_lt_20pct",
        "scenes_lt_40pct",
        "share_lt_20pct",
        "share_lt_40pct",
    }
    assert required_cols.issubset(set(table.column_names))

    summary = summarize_cloud_stats(table)
    assert summary["unique_tanks"] == 35
    assert 2019 in summary["years_covered"]
    assert 2024 in summary["years_covered"]
    assert summary["total_tank_months"] >= 35 * 70  # >= 70 months across 2019..present
    assert summary["total_tank_scenes"] >= 10_000

    ne_monsoon = summary["seasons"]["NE_Monsoon_Oct_Dec"]
    dry_season = summary["seasons"]["Dry_Jan_May"]
    # Northeast Monsoon must show higher mean cloud cover and lower <20% share than Dry season
    assert ne_monsoon["mean_cloud_cover_pct"] > dry_season["mean_cloud_cover_pct"]
    assert ne_monsoon["share_lt_20pct"] < dry_season["share_lt_20pct"]
    assert Path(CHART_PATH).is_file()
