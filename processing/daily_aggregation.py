"""FireHorizon Daily Aggregation Module
Aggregates satellite detections into spatial grid cells by UTC date and sensor product.
Explicitly distinguishes satellite observation detections from unique physical fires.
"""
from __future__ import annotations
import json
from typing import Dict, Any, List
import numpy as np
import pandas as pd


def aggregate_grid_daily(
    df: pd.DataFrame,
    region_id: str = "india",
    processing_version: str = "v1.0.0"
) -> pd.DataFrame:
    """Aggregate observations by (grid_id, activity_date, source_product) using vectorized operations."""
    df_work = df.copy()
    df_work["is_day"] = (df_work["daynight"] == "D").astype(np.int32)
    df_work["is_night"] = (df_work["daynight"] == "N").astype(np.int32)

    group_cols = [
        "grid_id",
        "acq_date",
        "source_product",
        "sensor_family",
        "platform_name",
        "grid_resolution_meters",
        "center_latitude",
        "center_longitude"
    ]

    grouped = df_work.groupby(group_cols, dropna=False)

    agg_df = grouped.agg(
        detection_count=("latitude", "size"),
        frp_sum=("frp", "sum"),
        frp_mean=("frp", "mean"),
        frp_median=("frp", "median"),
        frp_max=("frp", "max"),
        brightness_mean=("brightness", "mean"),
        day_count=("is_day", "sum"),
        night_count=("is_night", "sum")
    ).reset_index()

    agg_df = agg_df.rename(columns={
        "acq_date": "activity_date",
        "platform_name": "satellite_platform"
    })

    agg_df["confidence_summary"] = "{}"
    agg_df["region_id"] = region_id
    agg_df["processing_version"] = processing_version
    agg_df["frp_sum"] = np.round(agg_df["frp_sum"], 2)
    agg_df["frp_mean"] = np.round(agg_df["frp_mean"], 2)
    agg_df["frp_median"] = np.round(agg_df["frp_median"], 2)
    agg_df["frp_max"] = np.round(agg_df["frp_max"], 2)
    agg_df["brightness_mean"] = np.round(agg_df["brightness_mean"], 2)

    return agg_df
