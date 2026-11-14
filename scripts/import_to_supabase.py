#!/usr/bin/env python3
"""FireHorizon Supabase Bulk Data Importer
Securely imports derived grid-day aggregates and daily activity metrics to Supabase PostgreSQL.
Uses psycopg for secure, parameterized batch insertion with idempotent ON CONFLICT clauses.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

# Ensure repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import json
import pandas as pd
import psycopg

def get_db_url() -> str:
    db_url = os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("SUPABASE_DB_URL="):
                        db_url = line.split("=", 1)[1].strip()
                        break
    return db_url


def import_data(processed_dir: Path) -> None:
    db_url = get_db_url()
    if not db_url:
        print("\n" + "!" * 70)
        print("NOTICE: SUPABASE_DB_URL is not set.")
        print("To configure Supabase cloud database synchronization:")
        print("1. Create a Supabase project at https://supabase.com")
        print("2. Run the SQL schema found in supabase/schema.sql via the Supabase SQL editor.")
        print("3. Set SUPABASE_DB_URL in your .env file or Windows PowerShell environment:")
        print("   $env:SUPABASE_DB_URL = 'postgresql://postgres.[ID]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres'")
        print("4. Re-run this script: python scripts/import_to_supabase.py")
        print("!" * 70 + "\n")
        sys.exit(0)

    print(f"Connecting to PostgreSQL database at {db_url.split('@')[-1]}...")
    
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            # 1. Regions
            print("Importing reference regions...")
            regions = [
                ("india", "India (National)", "India", "Country", "Survey of India / Natural Earth", "Public Domain / Open Data"),
                ("maharashtra", "Maharashtra", "India", "State", "geoBoundaries (gbOpen ADM1) / DataMeet", "Creative Commons Attribution 2.5 India (CC BY 2.5 IN)")
            ]
            cur.executemany("""
                INSERT INTO public.regions (id, region_name, country, region_type, boundary_source, boundary_license)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING;
            """, regions)

            # 2. Daily Activity (India & Maharashtra)
            for region_file, r_id in [("activity_daily_india.csv", "india"), ("activity_daily_maharashtra.csv", "maharashtra")]:
                fpath = processed_dir / region_file
                if fpath.exists():
                    df = pd.read_csv(fpath)
                    print(f"Importing {len(df)} daily activity records for {r_id}...")
                    rows = []
                    for _, r in df.iterrows():
                        rows.append((
                            r["activity_date"], r["region_id"], r["modis_detection_count"],
                            r["viirs_snpp_detection_count"], r["viirs_noaa20_detection_count"],
                            r["viirs_noaa21_detection_count"], r["total_detections"],
                            r["modis_frp_sum"], r["viirs_frp_sum"], r["total_frp_sum"],
                            r["active_grid_cells"], r["cross_sensor_overlap_cells"],
                            r["experimental_activity_index"], r["index_method"],
                            r["baseline_status"], r["uncertainty_status"], r["processing_version"]
                        ))
                    cur.executemany("""
                        INSERT INTO public.activity_daily (
                            activity_date, region_id, modis_detection_count,
                            viirs_snpp_detection_count, viirs_noaa20_detection_count,
                            viirs_noaa21_detection_count, total_detections,
                            modis_frp_sum, viirs_frp_sum, total_frp_sum,
                            active_grid_cells, cross_sensor_overlap_cells,
                            experimental_activity_index, index_method,
                            baseline_status, uncertainty_status, processing_version
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (activity_date, region_id) DO UPDATE SET
                            total_detections = EXCLUDED.total_detections,
                            total_frp_sum = EXCLUDED.total_frp_sum,
                            experimental_activity_index = EXCLUDED.experimental_activity_index;
                    """, rows)

            # 3. Sensor Comparison Daily
            for comp_file, r_id in [("sensor_comparison_daily_india.csv", "india"), ("sensor_comparison_daily_maharashtra.csv", "maharashtra")]:
                cpath = processed_dir / comp_file
                if cpath.exists():
                    cdf = pd.read_csv(cpath)
                    print(f"Importing {len(cdf)} sensor comparison records for {r_id}...")
                    c_rows = []
                    for _, r in cdf.iterrows():
                        c_rows.append((
                            r["activity_date"], r["region_id"], r["sensor_a"], r["sensor_b"],
                            r["sensor_a_count"], r["sensor_b_count"], r["candidate_match_count"],
                            r["co_detected_grid_cells"], r["distance_threshold_meters"],
                            r["time_threshold_minutes"], r["methodology_version"]
                        ))
                    cur.executemany("""
                        INSERT INTO public.sensor_comparison_daily (
                            activity_date, region_id, sensor_a, sensor_b,
                            sensor_a_count, sensor_b_count, candidate_match_count,
                            co_detected_grid_cells, distance_threshold_meters,
                            time_threshold_minutes, methodology_version
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (activity_date, region_id, sensor_a, sensor_b) DO UPDATE SET
                            candidate_match_count = EXCLUDED.candidate_match_count,
                            co_detected_grid_cells = EXCLUDED.co_detected_grid_cells;
                    """, c_rows)

        conn.commit()
    print("Database synchronization completed successfully!")


if __name__ == "__main__":
    import_data(Path("data/processed"))
