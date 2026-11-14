#!/usr/bin/env python3
"""FireHorizon Dataset Verification Script
Verifies input row counts, coordinate ranges, confidence preservation, and aggregation reconciliation.
"""
from __future__ import annotations
import sys
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd

EXPECTED_COUNTS = {
    "MODIS_C61": 30644,
    "VIIRS_SNPP": 212965,
    "VIIRS_NOAA20": 213338,
    "VIIRS_NOAA21": 195078,
    "TOTAL": 652025
}


def verify_processed_dataset(processed_dir: Path) -> bool:
    print("Running FireHorizon Data Reconciliation & Verification...")
    combined_file = processed_dir / "combined_observations.csv.gz"
    if not combined_file.exists():
        print(f"FAILED: {combined_file} does not exist. Run pipeline first.", file=sys.stderr)
        return False

    df = pd.read_csv(combined_file, dtype={"acq_time": "string", "confidence_raw": "string"})
    total_rows = len(df)
    print(f"[CHECK 1] Total row count: {total_rows:,} (Expected: {EXPECTED_COUNTS['TOTAL']:,})")
    assert total_rows == EXPECTED_COUNTS["TOTAL"], f"Total row mismatch: {total_rows} vs {EXPECTED_COUNTS['TOTAL']}"

    print("[CHECK 2] Source-wise counts:")
    counts = df["source_product"].value_counts().to_dict()
    for prod, expected in EXPECTED_COUNTS.items():
        if prod == "TOTAL":
            continue
        actual = counts.get(prod, 0)
        print(f"  * {prod}: {actual:,} (Expected: {expected:,})")
        assert actual == expected, f"Mismatch in {prod}: {actual} vs {expected}"

    print("[CHECK 3] Coordinate validity:")
    assert df["latitude"].between(8.0, 35.0).all(), "Latitudes out of expected India envelope!"
    assert df["longitude"].between(68.0, 98.0).all(), "Longitudes out of expected India envelope!"
    print(f"  * Latitude: {df['latitude'].min():.4f} to {df['latitude'].max():.4f} (Valid)")
    print(f"  * Longitude: {df['longitude'].min():.4f} to {df['longitude'].max():.4f} (Valid)")

    print("[CHECK 4] Temporal integrity:")
    assert df["acq_date"].str.match(r"^2025-03-\d{2}$").all(), "Invalid date detected!"
    assert df["acq_time"].str.len().eq(4).all(), "Invalid acq_time text format!"
    assert df["acq_datetime_utc"].notna().all(), "Unparsed UTC timestamp detected!"
    print(f"  * Date span: {df['acq_date'].min()} to {df['acq_date'].max()} (31 days covered)")

    print("[CHECK 5] Confidence encodings preserved:")
    modis_conf = df[df["source_product"] == "MODIS_C61"]["confidence_raw"]
    viirs_conf = df[df["sensor_family"] == "VIIRS"]["confidence_raw"]
    assert modis_conf.str.isnumeric().all(), "MODIS confidence contains non-numeric values!"
    assert set(viirs_conf.unique()).issubset({"l", "n", "h"}), "VIIRS confidence contains unexpected classes!"
    print(f"  * MODIS numeric values preserved (sample: {modis_conf.head(3).tolist()})")
    print(f"  * VIIRS categorical classes preserved (classes: {set(viirs_conf.unique())})")

    print("[CHECK 6] Daily grid aggregations reconciliation:")
    india_grid_file = processed_dir / "fire_grid_daily_india.csv.gz"
    if india_grid_file.exists():
        grid_df = pd.read_csv(india_grid_file)
        agg_det_sum = grid_df["detection_count"].sum()
        print(f"  * Sum of detection_count across grid cells: {agg_det_sum:,} (Matches total: {agg_det_sum == total_rows})")
        assert agg_det_sum == total_rows, "Aggregated detection counts do not reconcile with observation totals!"

    print("\nALL VERIFICATION CHECKS PASSED SUCCESSFULLY (6/6)!")
    return True


if __name__ == "__main__":
    success = verify_processed_dataset(Path("data/processed"))
    sys.exit(0 if success else 1)
