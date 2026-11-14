#!/usr/bin/env python3
"""Prepare a provenance-preserving combined table from NASA FIRMS archive ZIPs.

This script standardizes column names and adds source/platform metadata. It does
NOT remove records, infer that detections are the same fire, or normalize the
sensor-specific confidence values onto a common scale.

Usage:
  python scripts/prepare_firms_data.py --input-dir data/raw --output-dir data/processed

Expected ZIPs (or extracted CSVs) in --input-dir:
  DL_FIRE_SV-C2_846910.zip  (Suomi-NPP VIIRS)
  DL_FIRE_J1V-C2_846908.zip (NOAA-20 VIIRS)
  DL_FIRE_J2V-C2_846909.zip (NOAA-21 VIIRS)
  DL_FIRE_M-C61_846907.zip  (MODIS Terra/Aqua)
"""
from __future__ import annotations
import argparse
import io
import zipfile
from pathlib import Path
import pandas as pd

SOURCES = {
    "DL_FIRE_SV-C2_846910": ("VIIRS", "Suomi-NPP", "VIIRS_SNPP"),
    "DL_FIRE_J1V-C2_846908": ("VIIRS", "NOAA-20", "VIIRS_NOAA20"),
    "DL_FIRE_J2V-C2_846909": ("VIIRS", "NOAA-21", "VIIRS_NOAA21"),
    "DL_FIRE_M-C61_846907": ("MODIS", "Platform in satellite column", "MODIS_C61"),
}
REQUIRED = ["latitude", "longitude", "brightness", "scan", "track", "acq_date",
            "acq_time", "satellite", "instrument", "confidence", "version",
            "bright_t31", "frp", "daynight", "type"]


def read_source(input_dir: Path, stem: str, meta: tuple[str, str, str]) -> pd.DataFrame:
    family, platform_label, product = meta
    zip_path = input_dir / f"{stem}.zip"
    csv_path = input_dir / f"{stem}.csv"
    if zip_path.exists():
        with zipfile.ZipFile(zip_path) as zf:
            csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
            if len(csv_names) != 1:
                raise ValueError(f"Expected one CSV in {zip_path.name}; found {csv_names}")
            with zf.open(csv_names[0]) as f:
                df = pd.read_csv(f, dtype={"acq_time": "string", "confidence": "string"})
    elif csv_path.exists():
        df = pd.read_csv(csv_path, dtype={"acq_time": "string", "confidence": "string"})
    else:
        raise FileNotFoundError(f"Missing {zip_path.name} (or {csv_path.name}) in {input_dir}")

    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"{stem}: missing expected FIRMS fields: {missing}")

    df["source_product"] = product
    df["sensor_family"] = family
    if family == "MODIS":
        df["platform_name"] = df["satellite"].map({"Terra": "Terra", "Aqua": "Aqua"}).fillna(df["satellite"].astype(str))
    else:
        df["platform_name"] = platform_label
    # Keep a raw confidence string and describe its original encoding.
    df["confidence_raw"] = df["confidence"].astype("string")
    df["confidence_encoding"] = "categorical (l/n/h)" if family == "VIIRS" else "numeric product value"
    df["acq_date"] = pd.to_datetime(df["acq_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    # Preserve acquisition time exactly as HHMM text; no timezone conversion is made.
    df["acq_time"] = df["acq_time"].astype("string").str.zfill(4)
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", type=Path, default=Path("data/raw"))
    ap.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    frames = [read_source(args.input_dir, stem, meta) for stem, meta in SOURCES.items()]
    combined = pd.concat(frames, ignore_index=True)
    combined["latitude"] = pd.to_numeric(combined["latitude"], errors="coerce")
    combined["longitude"] = pd.to_numeric(combined["longitude"], errors="coerce")
    combined["frp"] = pd.to_numeric(combined["frp"], errors="coerce")
    combined["brightness"] = pd.to_numeric(combined["brightness"], errors="coerce")

    out = args.output_dir / "combined_observations.csv.gz"
    combined.to_csv(out, index=False, compression="gzip")

    summary = (combined.groupby(["source_product", "sensor_family", "platform_name"], dropna=False)
               .agg(record_count=("latitude", "size"), first_date=("acq_date", "min"),
                    last_date=("acq_date", "max"), latitude_min=("latitude", "min"),
                    latitude_max=("latitude", "max"), longitude_min=("longitude", "min"),
                    longitude_max=("longitude", "max"), frp_mean=("frp", "mean"),
                    frp_median=("frp", "median"), missing_coordinates=("latitude", lambda s: int(s.isna().sum())))
               .reset_index())
    summary.to_csv(args.output_dir / "source_summary.csv", index=False)

    daily = (combined.groupby(["acq_date", "source_product", "sensor_family"])
             .size().rename("observation_count").reset_index())
    daily.to_csv(args.output_dir / "daily_counts_by_source.csv", index=False)

    print(f"Combined rows: {len(combined):,}")
    print(f"Wrote: {out}")
    print(f"Wrote: {args.output_dir / 'source_summary.csv'}")
    print(f"Wrote: {args.output_dir / 'daily_counts_by_source.csv'}")

if __name__ == "__main__":
    main()
