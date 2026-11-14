#!/usr/bin/env python3
"""FireHorizon Master Pipeline Runner
Executes the full end-to-end satellite fire harmonization workflow:
1. Ingest 4 original NASA FIRMS ZIP archives.
2. Validate records and generate data audit.
3. Apply official Maharashtra GeoJSON point-in-polygon filtering.
4. Project coordinates to 1km equal-area grid (EPSG:6933).
5. Generate daily grid-cell aggregations.
6. Perform spatial-temporal MODIS-VIIRS candidate co-detection matching.
7. Compute experimental harmonization indices.
8. Generate burning activity calendars and statistical variance metrics.
9. Export frontend bundles and verification artifacts.
"""
from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd

from processing.ingestion import ingest_all_sources
from processing.validation import validate_observations
from processing.geographic_filter import apply_geographic_filters
from processing.spatial_grid import SpatialGridManager, evaluate_grid_sensitivity
from processing.daily_aggregation import aggregate_grid_daily
from processing.sensor_comparison import (
    compute_sensor_comparison_daily,
    find_candidate_matches,
    sensitivity_analysis
)
from processing.harmonization import HarmonizationEngine
from processing.activity_calendar import build_activity_calendar
from processing.anomaly_detection import compute_intra_month_statistical_deviations
from processing.generate_reports import export_frontend_data_bundle


def print_step(msg: str) -> None:
    print(msg, flush=True)


def run_pipeline(
    raw_dir: Path,
    processed_dir: Path,
    boundary_path: Path,
    frontend_data_dir: Path
) -> None:
    t0 = time.time()
    print_step("=" * 70)
    print_step("FIREHORIZON — NASA SPACE APPS CHALLENGE 2026")
    print_step("Harmonization of MODIS and VIIRS Hot Spots")
    print_step("=" * 70)

    processed_dir.mkdir(parents=True, exist_ok=True)
    audit_dir = processed_dir / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # STAGE 1: INGESTION
    # ---------------------------------------------------------
    print_step("\n[STAGE 1/8] Ingesting NASA FIRMS archives...")
    df_all = ingest_all_sources(raw_dir)
    print_step(f"-> Successfully ingested {len(df_all):,} records.")
    for prod, cnt in df_all["source_product"].value_counts().items():
        print_step(f"   * {prod}: {cnt:,}")

    # ---------------------------------------------------------
    # STAGE 2: DATA VALIDATION & AUDITING
    # ---------------------------------------------------------
    print_step("\n[STAGE 2/8] Validating observations and running audit checks...")
    df_all, audit_report = validate_observations(df_all, audit_dir)
    print_step(f"-> Data validation completed. All rows accounted for ({audit_report['total_records_ingested']:,}).")
    print_step(f"-> Latitudes: {audit_report['coordinate_checks']['latitude_min']:.4f} to {audit_report['coordinate_checks']['latitude_max']:.4f}")
    print_step(f"-> Longitudes: {audit_report['coordinate_checks']['longitude_min']:.4f} to {audit_report['coordinate_checks']['longitude_max']:.4f}")

    # ---------------------------------------------------------
    # STAGE 3: GEOGRAPHIC FILTERING (MAHARASHTRA)
    # ---------------------------------------------------------
    print_step("\n[STAGE 3/8] Applying point-in-polygon filtering with official Maharashtra GeoJSON...")
    df_all, df_mh, boundary_meta = apply_geographic_filters(df_all, boundary_path)
    print_step(f"-> India-wide total records: {len(df_all):,}")
    print_step(f"-> Maharashtra subset records: {len(df_mh):,} ({(len(df_mh)/len(df_all))*100:.2f}% of India detections)")
    print_step(f"   Boundary source: {boundary_meta.get('source')}")

    # ---------------------------------------------------------
    # STAGE 4: COMMON EQUAL-AREA SPATIAL GRID (EPSG:6933, 1km)
    # ---------------------------------------------------------
    print_step("\n[STAGE 4/8] Assigning observations to 1km equal-area spatial grid (EPSG:6933)...")
    grid_mgr = SpatialGridManager(resolution_meters=1000)
    df_all = grid_mgr.assign_grid_cells(df_all)
    df_mh = df_all[df_all["in_maharashtra"]].copy()

    # Save enriched combined observations to processed directory
    combined_out = processed_dir / "combined_observations.csv.gz"
    print_step(f"-> Writing enriched observations to {combined_out}...")
    df_all.to_csv(combined_out, index=False, compression="gzip")

    # Run sensitivity check on a representative sample
    print_step("-> Running grid resolution sensitivity analysis (500m, 1km, 2km)...")
    sens_sample = df_mh.head(10000)
    grid_sensitivity = evaluate_grid_sensitivity(sens_sample)
    with open(audit_dir / "grid_sensitivity_analysis.json", "w", encoding="utf-8") as f:
        json.dump(grid_sensitivity, f, indent=2)

    # ---------------------------------------------------------
    # STAGE 5: DAILY SENSOR-SPECIFIC AGGREGATION
    # ---------------------------------------------------------
    print_step("\n[STAGE 5/8] Computing daily grid-cell aggregations...")
    grid_agg_india = aggregate_grid_daily(df_all, region_id="india")
    grid_agg_mh = aggregate_grid_daily(df_mh, region_id="maharashtra")

    grid_agg_india.to_csv(processed_dir / "fire_grid_daily_india.csv.gz", index=False, compression="gzip")
    grid_agg_mh.to_csv(processed_dir / "fire_grid_daily_maharashtra.csv.gz", index=False, compression="gzip")
    print_step(f"-> India grid-day cells: {len(grid_agg_india):,}")
    print_step(f"-> Maharashtra grid-day cells: {len(grid_agg_mh):,}")

    # ---------------------------------------------------------
    # STAGE 6: CROSS-SENSOR MATCHING & COMPARISON
    # ---------------------------------------------------------
    print_step("\n[STAGE 6/8] Performing MODIS-VIIRS spatial-temporal candidate co-detection matching...")
    sensor_comp_india = compute_sensor_comparison_daily(df_all, region_id="india")
    sensor_comp_mh = compute_sensor_comparison_daily(df_mh, region_id="maharashtra")

    sensor_comp_india.to_csv(processed_dir / "sensor_comparison_daily_india.csv", index=False)
    sensor_comp_mh.to_csv(processed_dir / "sensor_comparison_daily_maharashtra.csv", index=False)

    print_step(f"-> Total candidate co-detection matches in India: {sensor_comp_india['candidate_match_count'].sum():,}")
    print_step(f"-> Total candidate co-detection matches in Maharashtra: {sensor_comp_mh['candidate_match_count'].sum():,}")

    # ---------------------------------------------------------
    # STAGE 7: HARMONIZATION & ACTIVITY CALENDAR
    # ---------------------------------------------------------
    print_step("\n[STAGE 7/8] Generating harmonized daily activity and burning calendars...")
    engine = HarmonizationEngine()
    activity_india = engine.compute_daily_activity(df_all, sensor_comp_india, region_id="india")
    activity_mh = engine.compute_daily_activity(df_mh, sensor_comp_mh, region_id="maharashtra")

    # Add intra-month statistical variance
    activity_india = compute_intra_month_statistical_deviations(activity_india)
    activity_mh = compute_intra_month_statistical_deviations(activity_mh)

    activity_india.to_csv(processed_dir / "activity_daily_india.csv", index=False)
    activity_mh.to_csv(processed_dir / "activity_daily_maharashtra.csv", index=False)

    cal_india = build_activity_calendar(activity_india, region_id="india")
    cal_mh = build_activity_calendar(activity_mh, region_id="maharashtra")

    # ---------------------------------------------------------
    # STAGE 8: FRONTEND DATA BUNDLES & SUMMARY REPORT
    # ---------------------------------------------------------
    print_step("\n[STAGE 8/8] Exporting frontend JSON bundles and verification reports...")
    
    # Calculate overall summary metrics
    overview_stats = {
        "dataset_name": "FireHorizon NASA FIRMS Archive (India)",
        "coverage_period": "2025-03-01 to 2025-03-31",
        "archive_status": "Archived Research Dataset (Not a live telemetry feed)",
        "total_observations": len(df_all),
        "modis_observations": int((df_all["sensor_family"] == "MODIS").sum()),
        "viirs_observations": int((df_all["sensor_family"] == "VIIRS").sum()),
        "viirs_snpp": int((df_all["source_product"] == "VIIRS_SNPP").sum()),
        "viirs_noaa20": int((df_all["source_product"] == "VIIRS_NOAA20").sum()),
        "viirs_noaa21": int((df_all["source_product"] == "VIIRS_NOAA21").sum()),
        "total_frp_mw": round(float(df_all["frp"].sum()), 2),
        "mean_frp_mw": round(float(df_all["frp"].mean()), 2),
        "active_grid_cells_1km_india": int(df_all["grid_id"].nunique()),
        "active_grid_cells_1km_maharashtra": int(df_mh["grid_id"].nunique()),
        "maharashtra_observations": len(df_mh),
        "candidate_matches_india": int(sensor_comp_india["candidate_match_count"].sum()),
        "candidate_matches_maharashtra": int(sensor_comp_mh["candidate_match_count"].sum()),
        "day_observations": int((df_all["daynight"] == "D").sum()),
        "night_observations": int((df_all["daynight"] == "N").sum()),
        "pipeline_execution_time_seconds": round(time.time() - t0, 2)
    }

    # Extract representative top active grid cells for web map rendering
    grid_sample_india = (
        grid_agg_india.groupby(["grid_id", "center_latitude", "center_longitude"])
        .agg(
            detection_count=("detection_count", "sum"),
            frp_sum=("frp_sum", "sum"),
            brightness_mean=("brightness_mean", "mean"),
            active_dates=("activity_date", "nunique")
        )
        .reset_index()
        .sort_values("frp_sum", ascending=False)
        .head(2500)
    )

    grid_sample_mh = (
        grid_agg_mh.groupby(["grid_id", "center_latitude", "center_longitude"])
        .agg(
            detection_count=("detection_count", "sum"),
            frp_sum=("frp_sum", "sum"),
            brightness_mean=("brightness_mean", "mean"),
            active_dates=("activity_date", "nunique")
        )
        .reset_index()
        .sort_values("frp_sum", ascending=False)
        .head(2000)
    )

    # Export to both frontend public directory and data/processed/bundle/
    export_dirs = [frontend_data_dir, processed_dir / "bundle"]
    for ed in export_dirs:
        export_frontend_data_bundle(
            overview_stats=overview_stats,
            daily_activity_india=activity_india,
            daily_activity_mh=activity_mh,
            sensor_comparison=sensor_comp_india,
            calendar_india=cal_india,
            calendar_mh=cal_mh,
            grid_sample_india=grid_sample_india,
            grid_sample_mh=grid_sample_mh,
            output_dir=ed
        )

    elapsed = time.time() - t0
    print_step("\n" + "=" * 70)
    print_step(f"PIPELINE COMPLETE! Execution time: {elapsed:.2f} seconds.")
    print_step(f"Outputs written to {processed_dir} and {frontend_data_dir}")
    print_step("=" * 70)


def main() -> None:
    ap = argparse.ArgumentParser(description="Run FireHorizon Harmonization Pipeline")
    ap.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    ap.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    ap.add_argument("--boundary", type=Path, default=Path("data/boundaries/maharashtra.geojson"))
    ap.add_argument("--frontend-data-dir", type=Path, default=Path("frontend/public/data"))
    args = ap.parse_args()

    run_pipeline(args.raw_dir, args.processed_dir, args.boundary, args.frontend_data_dir)


if __name__ == "__main__":
    main()
