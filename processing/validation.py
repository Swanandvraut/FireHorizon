"""FireHorizon Validation Module
Performs comprehensive data auditing, boundary validation, missing value inspection,
and duplicate detection. Writes separate audit outputs without silent data loss.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

EXPECTED_ROW_COUNTS = {
    "VIIRS_SNPP": 212965,
    "VIIRS_NOAA20": 213338,
    "VIIRS_NOAA21": 195078,
    "MODIS_C61": 30644,
    "TOTAL": 652025
}


def validate_observations(
    df: pd.DataFrame,
    audit_dir: Path
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Validate observations, produce audit report, and flag questionable records."""
    audit_dir.mkdir(parents=True, exist_ok=True)
    report: Dict[str, Any] = {
        "total_records_ingested": len(df),
        "source_breakdown": {},
        "row_count_reconciliation": {},
        "coordinate_checks": {},
        "temporal_checks": {},
        "frp_checks": {},
        "missing_values": {},
        "duplicate_records": {},
        "questionable_records_count": 0,
        "rejected_records_count": 0,
        "is_valid": True
    }

    # 1. Source breakdown & Row count reconciliation
    counts_by_prod = df["source_product"].value_counts().to_dict()
    report["source_breakdown"] = counts_by_prod

    reconciliation = {}
    for prod, expected in EXPECTED_ROW_COUNTS.items():
        if prod == "TOTAL":
            actual = len(df)
        else:
            actual = counts_by_prod.get(prod, 0)
        reconciliation[prod] = {
            "expected": expected,
            "actual": actual,
            "matches": actual == expected
        }
        if actual != expected:
            report["is_valid"] = False
    report["row_count_reconciliation"] = reconciliation

    # 2. Coordinate range checks
    invalid_lat = (df["latitude"].isna()) | (df["latitude"] < -90) | (df["latitude"] > 90)
    invalid_lon = (df["longitude"].isna()) | (df["longitude"] < -180) | (df["longitude"] > 180)
    outside_india = (df["latitude"] < 6.0) | (df["latitude"] > 38.0) | (df["longitude"] < 68.0) | (df["longitude"] > 98.0)

    report["coordinate_checks"] = {
        "invalid_latitude_count": int(invalid_lat.sum()),
        "invalid_longitude_count": int(invalid_lon.sum()),
        "outside_india_envelope_count": int(outside_india.sum()),
        "latitude_min": float(df["latitude"].min()),
        "latitude_max": float(df["latitude"].max()),
        "longitude_min": float(df["longitude"].min()),
        "longitude_max": float(df["longitude"].max()),
    }

    # 3. Temporal checks
    invalid_date = df["acq_date"].isna() | (~df["acq_date"].str.match(r"^2025-03-\d{2}$"))
    time_numeric = pd.to_numeric(df["acq_time"], errors="coerce")
    hours = time_numeric // 100
    minutes = time_numeric % 100
    invalid_time = df["acq_time"].isna() | (hours < 0) | (hours > 23) | (minutes < 0) | (minutes > 59)

    report["temporal_checks"] = {
        "invalid_date_count": int(invalid_date.sum()),
        "invalid_time_count": int(invalid_time.sum()),
        "first_acquisition_date": str(df["acq_date"].min()),
        "last_acquisition_date": str(df["acq_date"].max()),
        "total_days_covered": int(df["acq_date"].nunique())
    }

    # 4. FRP checks
    negative_frp = df["frp"] < 0
    extreme_frp = df["frp"] > 10000.0  # Physical check for extreme values (>10,000 MW)
    report["frp_checks"] = {
        "frp_min": float(df["frp"].min()) if not df["frp"].isna().all() else None,
        "frp_max": float(df["frp"].max()) if not df["frp"].isna().all() else None,
        "frp_mean": float(df["frp"].mean()) if not df["frp"].isna().all() else None,
        "frp_median": float(df["frp"].median()) if not df["frp"].isna().all() else None,
        "negative_frp_count": int(negative_frp.sum()),
        "extreme_frp_count": int(extreme_frp.sum())
    }

    # 5. Missing values
    missing_map = {col: int(df[col].isna().sum()) for col in df.columns}
    report["missing_values"] = missing_map

    # 6. Duplicate checks within identical source product
    # Note: Satellite scans occasionally have identical lat/lon/time records for high-energy saturated events
    duplicate_mask = df.duplicated(
        subset=["latitude", "longitude", "acq_date", "acq_time", "satellite", "source_product"],
        keep=False
    )
    exact_duplicates = df.duplicated(keep=False)
    report["duplicate_records"] = {
        "candidate_duplicate_count": int(duplicate_mask.sum()),
        "exact_identical_row_count": int(exact_duplicates.sum()),
        "policy": "Preserved in pipeline; flagged in audit log. No records silently deleted."
    }

    # Separate questionable records for audit output without modifying main dataset
    questionable_mask = invalid_lat | invalid_lon | invalid_date | invalid_time | negative_frp
    report["questionable_records_count"] = int(questionable_mask.sum())
    report["rejected_records_count"] = 0  # We do not silently drop any rows

    if questionable_mask.sum() > 0:
        questionable_df = df[questionable_mask]
        questionable_df.to_csv(audit_dir / "questionable_records.csv", index=False)

    # Save duplicate audit report if any
    if duplicate_mask.sum() > 0:
        duplicates_sample = df[duplicate_mask].head(1000)
        duplicates_sample.to_csv(audit_dir / "audit_candidate_duplicates_sample.csv", index=False)

    # Write audit report JSON
    with open(audit_dir / "data_validation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return df, report
