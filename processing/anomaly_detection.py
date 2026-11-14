"""FireHorizon Anomaly Detection Module
Computes robust intra-month statistical variance metrics (MAD, robust z-scores).
Explicitly marks historical anomaly detection as disabled/insufficient due to
single-month data constraints (March 1-31, 2025). Disallows unvalidated early warning claims.
"""
from __future__ import annotations
from typing import Dict, Any, List
import numpy as np
import pandas as pd


def compute_intra_month_statistical_deviations(
    daily_df: pd.DataFrame
) -> pd.DataFrame:
    """Compute intra-month statistical deviation relative to the March 2025 sample.
    
    CRITICAL SCIENTIFIC NOTICE:
    This computes intra-sample deviations relative to the 31 days of March 2025 ONLY.
    It does NOT represent a true multi-year climatological anomaly or early warning alert.
    """
    df = daily_df.copy()
    counts = df["total_detections"].values.astype(float)
    frps = df["total_frp_sum"].values.astype(float)

    # Median Absolute Deviation (MAD) for robust intra-month variation
    det_median = np.median(counts)
    det_mad = np.median(np.abs(counts - det_median))
    # Normalized MAD (consistent with standard normal distribution std)
    det_mad_norm = det_mad * 1.4826 if det_mad > 0 else 1.0

    frp_median = np.median(frps)
    frp_mad = np.median(np.abs(frps - frp_median))
    frp_mad_norm = frp_mad * 1.4826 if frp_mad > 0 else 1.0

    # Robust z-score relative to March 2025 monthly median
    robust_z_det = (counts - det_median) / det_mad_norm
    robust_z_frp = (frps - frp_median) / frp_mad_norm

    df["intra_month_detection_zscore"] = np.round(robust_z_det, 2)
    df["intra_month_frp_zscore"] = np.round(robust_z_frp, 2)
    df["climatological_anomaly_status"] = "Historical baseline insufficient"
    df["climatological_baseline_required_years"] = ">= 5 years (2020-2024 historical reference period)"
    df["early_warning_claim_allowed"] = False

    return df
