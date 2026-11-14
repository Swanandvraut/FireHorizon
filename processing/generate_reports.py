"""FireHorizon Report & Export Generation Module
Generates comprehensive audit documentation, scientific summaries, and pre-packaged
data bundles for the web frontend and external verification.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any
import pandas as pd


def export_frontend_data_bundle(
    overview_stats: Dict[str, Any],
    daily_activity_india: pd.DataFrame,
    daily_activity_mh: pd.DataFrame,
    sensor_comparison: pd.DataFrame,
    calendar_india: Dict[str, Any],
    calendar_mh: Dict[str, Any],
    grid_sample_india: pd.DataFrame,
    grid_sample_mh: pd.DataFrame,
    output_dir: Path
) -> None:
    """Export compact JSON data bundles for frontend consumption."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Overview metrics
    with open(output_dir / "overview_metrics.json", "w", encoding="utf-8") as f:
        json.dump(overview_stats, f, indent=2)

    # 2. Daily activity (India & Maharashtra)
    with open(output_dir / "daily_activity_india.json", "w", encoding="utf-8") as f:
        json.dump(daily_activity_india.to_dict(orient="records"), f, indent=2)

    with open(output_dir / "daily_activity_maharashtra.json", "w", encoding="utf-8") as f:
        json.dump(daily_activity_mh.to_dict(orient="records"), f, indent=2)

    # 3. Sensor comparisons
    with open(output_dir / "sensor_comparison.json", "w", encoding="utf-8") as f:
        json.dump(sensor_comparison.to_dict(orient="records"), f, indent=2)

    # 4. Calendar bundles
    with open(output_dir / "calendar_india.json", "w", encoding="utf-8") as f:
        json.dump(calendar_india, f, indent=2)

    with open(output_dir / "calendar_maharashtra.json", "w", encoding="utf-8") as f:
        json.dump(calendar_mh, f, indent=2)

    # 5. Grid cell layers for map (top active cells / representative sampling)
    with open(output_dir / "grid_cells_india.json", "w", encoding="utf-8") as f:
        json.dump(grid_sample_india.to_dict(orient="records"), f, indent=2)

    with open(output_dir / "grid_cells_maharashtra.json", "w", encoding="utf-8") as f:
        json.dump(grid_sample_mh.to_dict(orient="records"), f, indent=2)

    print(f"Exported frontend data bundle to {output_dir}")
