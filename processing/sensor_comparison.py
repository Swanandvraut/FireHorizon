"""FireHorizon Sensor Comparison & Candidate Matching Module
Identifies spatial-temporal candidate co-detections between MODIS and VIIRS sensors.
Explicitly labels matches as candidate co-detections rather than physical fire identity.
Never discards unmatched observations.
"""
from __future__ import annotations
import math
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


def find_candidate_matches(
    modis_df: pd.DataFrame,
    viirs_df: pd.DataFrame,
    distance_threshold_m: float = 1000.0,
    time_threshold_min: float = 60.0,
    methodology_version: str = "v1.0-spatial-temporal"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Match MODIS and VIIRS detections within distance and time thresholds on the same UTC date.
    
    Returns:
        matches_df: Candidate pair co-detections with distance, dt, and observation references
        summary_stats: High-level match statistics and sensitivity parameters
    """
    if len(modis_df) == 0 or len(viirs_df) == 0:
        empty_cols = [
            "modis_obs_id", "viirs_obs_id", "acq_date", "distance_meters",
            "time_diff_minutes", "modis_platform", "viirs_platform",
            "modis_frp", "viirs_frp", "candidate_status", "methodology_version"
        ]
        return pd.DataFrame(columns=empty_cols), {"total_candidates": 0}

    # Group by acquisition date to compare observations occurring on the same UTC day
    all_matches: List[dict] = []
    unique_dates = sorted(list(set(modis_df["acq_date"]).intersection(set(viirs_df["acq_date"]))))

    for d in unique_dates:
        m_day = modis_df[modis_df["acq_date"] == d].copy()
        v_day = viirs_df[viirs_df["acq_date"] == d].copy()

        if len(m_day) == 0 or len(v_day) == 0:
            continue

        # Projected coordinates in meters (grid_x, grid_y from EPSG:6933)
        m_coords = m_day[["grid_x", "grid_y"]].values
        v_coords = v_day[["grid_x", "grid_y"]].values

        tree = cKDTree(v_coords)
        # Query all VIIRS points within distance threshold of each MODIS point
        neighbor_indices = tree.query_ball_point(m_coords, r=distance_threshold_m)

        m_time_secs = pd.to_datetime(m_day["acq_datetime_utc"]).values.astype("int64") // 10**9
        v_time_secs = pd.to_datetime(v_day["acq_datetime_utc"]).values.astype("int64") // 10**9

        m_obs = m_day["obs_id"].values
        v_obs = v_day["obs_id"].values
        m_plats = m_day["platform_name"].values
        v_plats = v_day["platform_name"].values
        m_frps = m_day["frp"].values
        v_frps = v_day["frp"].values

        for i, v_idx_list in enumerate(neighbor_indices):
            if not v_idx_list:
                continue
            m_sec = m_time_secs[i]
            m_x, m_y = m_coords[i]

            for v_idx in v_idx_list:
                dt_minutes = abs(m_sec - v_time_secs[v_idx]) / 60.0

                if dt_minutes <= time_threshold_min:
                    vx, vy = v_coords[v_idx]
                    dist_m = math.hypot(m_x - vx, m_y - vy)
                    all_matches.append({
                        "modis_obs_id": m_obs[i],
                        "viirs_obs_id": v_obs[v_idx],
                        "acq_date": d,
                        "distance_meters": round(dist_m, 1),
                        "time_diff_minutes": round(dt_minutes, 1),
                        "modis_platform": m_plats[i],
                        "viirs_platform": v_plats[v_idx],
                        "modis_frp": round(float(m_frps[i]), 2) if not pd.isna(m_frps[i]) else None,
                        "viirs_frp": round(float(v_frps[v_idx]), 2) if not pd.isna(v_frps[v_idx]) else None,
                        "candidate_status": "candidate_co_detection",
                        "methodology_version": methodology_version
                    })

    matches_df = pd.DataFrame(all_matches)
    summary_stats = {
        "modis_total_evaluated": len(modis_df),
        "viirs_total_evaluated": len(viirs_df),
        "candidate_matches_found": len(matches_df),
        "modis_unique_matched": matches_df["modis_obs_id"].nunique() if len(matches_df) > 0 else 0,
        "viirs_unique_matched": matches_df["viirs_obs_id"].nunique() if len(matches_df) > 0 else 0,
        "distance_threshold_m": distance_threshold_m,
        "time_threshold_min": time_threshold_min,
        "methodology_version": methodology_version
    }
    return matches_df, summary_stats


def compute_sensor_comparison_daily(
    df: pd.DataFrame,
    region_id: str = "india",
    distance_threshold_m: float = 1000.0,
    time_threshold_min: float = 60.0,
    methodology_version: str = "v1.0"
) -> pd.DataFrame:
    """Compute daily comparative metrics between MODIS and VIIRS sensor families."""
    modis_df = df[df["sensor_family"] == "MODIS"].copy()
    viirs_df = df[df["sensor_family"] == "VIIRS"].copy()

    dates = sorted(df["acq_date"].unique())
    daily_records = []

    for d in dates:
        m_day = modis_df[modis_df["acq_date"] == d]
        v_day = viirs_df[viirs_df["acq_date"] == d]

        m_cells = set(m_day["grid_id"].unique())
        v_cells = set(v_day["grid_id"].unique())
        overlap_cells = len(m_cells.intersection(v_cells))

        matches_day, _ = find_candidate_matches(
            m_day, v_day,
            distance_threshold_m=distance_threshold_m,
            time_threshold_min=time_threshold_min,
            methodology_version=methodology_version
        )

        daily_records.append({
            "activity_date": d,
            "region_id": region_id,
            "sensor_a": "MODIS",
            "sensor_b": "VIIRS",
            "sensor_a_count": len(m_day),
            "sensor_b_count": len(v_day),
            "sensor_a_frp_sum": round(float(m_day["frp"].sum()), 2),
            "sensor_b_frp_sum": round(float(v_day["frp"].sum()), 2),
            "candidate_match_count": len(matches_day),
            "co_detected_grid_cells": overlap_cells,
            "distance_threshold_meters": distance_threshold_m,
            "time_threshold_minutes": time_threshold_min,
            "methodology_version": methodology_version
        })

    return pd.DataFrame(daily_records)


def sensitivity_analysis(
    modis_sample: pd.DataFrame,
    viirs_sample: pd.DataFrame,
    distances: List[float] = [500.0, 1000.0, 2000.0],
    times: List[float] = [30.0, 60.0, 120.0]
) -> List[Dict[str, Any]]:
    """Test candidate match sensitivity across varying distance and time windows."""
    results = []
    for d in distances:
        for t in times:
            _, stats = find_candidate_matches(
                modis_sample, viirs_sample,
                distance_threshold_m=d,
                time_threshold_min=t
            )
            results.append({
                "distance_threshold_m": d,
                "time_threshold_min": t,
                "matches": stats["candidate_matches_found"],
                "modis_matched": stats["modis_unique_matched"],
                "viirs_matched": stats["viirs_unique_matched"]
            })
    return results
