"""FireHorizon Ingestion Module
Standardizes and ingests NASA FIRMS archive datasets from raw ZIP files.
Preserves original columns, datatypes, and confidence encodings.
"""
from __future__ import annotations
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd

SOURCES_METADATA: Dict[str, Dict[str, Any]] = {
    "DL_FIRE_SV-C2_846910": {
        "family": "VIIRS",
        "platform_default": "Suomi-NPP",
        "product": "VIIRS_SNPP",
        "instrument": "VIIRS",
        "confidence_encoding": "categorical (l/n/h)",
        "nominal_resolution_m": 375,
        "archive_file": "DL_FIRE_SV-C2_846910.zip",
        "citation": "NASA FIRMS Suomi-NPP VIIRS 375m Active Fire Product (VNP14IMGTDL_NRT / Collection 2)"
    },
    "DL_FIRE_J1V-C2_846908": {
        "family": "VIIRS",
        "platform_default": "NOAA-20",
        "product": "VIIRS_NOAA20",
        "instrument": "VIIRS",
        "confidence_encoding": "categorical (l/n/h)",
        "nominal_resolution_m": 375,
        "archive_file": "DL_FIRE_J1V-C2_846908.zip",
        "citation": "NASA FIRMS NOAA-20 (JPSS-1) VIIRS 375m Active Fire Product (VJ114IMGTDL_NRT / Collection 2)"
    },
    "DL_FIRE_J2V-C2_846909": {
        "family": "VIIRS",
        "platform_default": "NOAA-21",
        "product": "VIIRS_NOAA21",
        "instrument": "VIIRS",
        "confidence_encoding": "categorical (l/n/h)",
        "nominal_resolution_m": 375,
        "archive_file": "DL_FIRE_J2V-C2_846909.zip",
        "citation": "NASA FIRMS NOAA-21 (JPSS-2) VIIRS 375m Active Fire Product (VJ214IMGTDL_NRT / Collection 2)"
    },
    "DL_FIRE_M-C61_846907": {
        "family": "MODIS",
        "platform_default": "Terra/Aqua",
        "product": "MODIS_C61",
        "instrument": "MODIS",
        "confidence_encoding": "numeric product value (0-100)",
        "nominal_resolution_m": 1000,
        "archive_file": "DL_FIRE_M-C61_846907.zip",
        "citation": "NASA FIRMS MODIS Collection 6.1 Active Fire Product (MOD14/MYD14)"
    },
}

REQUIRED_FIRMS_COLUMNS = [
    "latitude", "longitude", "brightness", "scan", "track", "acq_date",
    "acq_time", "satellite", "instrument", "confidence", "version",
    "bright_t31", "frp", "daynight", "type"
]


def load_single_source(input_dir: Path, stem: str, meta: Dict[str, Any]) -> pd.DataFrame:
    """Read a single FIRMS source from ZIP or extracted CSV."""
    zip_path = input_dir / f"{stem}.zip"
    csv_path = input_dir / f"{stem}.csv"

    if zip_path.exists():
        with zipfile.ZipFile(zip_path) as zf:
            csv_candidates = [n for n in zf.namelist() if n.lower().endswith(".csv")]
            if len(csv_candidates) != 1:
                raise ValueError(f"Expected 1 CSV inside {zip_path.name}, found: {csv_candidates}")
            with zf.open(csv_candidates[0]) as f:
                df = pd.read_csv(f, dtype={"acq_time": "string", "confidence": "string"})
    elif csv_path.exists():
        df = pd.read_csv(csv_path, dtype={"acq_time": "string", "confidence": "string"})
    else:
        raise FileNotFoundError(f"Missing archive {zip_path.name} (or extracted CSV) in {input_dir}")

    missing_cols = [c for c in REQUIRED_FIRMS_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Source {stem} is missing required FIRMS columns: {missing_cols}")

    # Provenance fields
    df["source_archive"] = f"{stem}.zip"
    df["source_product"] = meta["product"]
    df["sensor_family"] = meta["family"]
    df["nominal_resolution_m"] = meta["nominal_resolution_m"]
    df["citation"] = meta["citation"]

    # Platform normalization
    if meta["family"] == "MODIS":
        df["platform_name"] = df["satellite"].map({"Terra": "Terra", "Aqua": "Aqua"}).fillna(df["satellite"].astype(str))
    else:
        df["platform_name"] = meta["platform_default"]

    # Confidence raw preservation & encoding definition
    df["confidence_raw"] = df["confidence"].astype("string")
    df["confidence_encoding"] = meta["confidence_encoding"]

    # Acquisition Date & Time formatting (preserving original UTC basis)
    df["acq_date"] = pd.to_datetime(df["acq_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["acq_time"] = df["acq_time"].astype("string").str.zfill(4)

    # Standardized ISO UTC acquisition timestamp
    df["acq_datetime_utc"] = pd.to_datetime(
        df["acq_date"] + " " + df["acq_time"].str.slice(0, 2) + ":" + df["acq_time"].str.slice(2, 4) + ":00",
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce"
    )

    # Convert numeric fields
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["brightness"] = pd.to_numeric(df["brightness"], errors="coerce")
    df["scan"] = pd.to_numeric(df["scan"], errors="coerce")
    df["track"] = pd.to_numeric(df["track"], errors="coerce")
    df["bright_t31"] = pd.to_numeric(df["bright_t31"], errors="coerce")
    df["frp"] = pd.to_numeric(df["frp"], errors="coerce")
    df["type"] = pd.to_numeric(df["type"], errors="coerce")

    # Generate deterministic unique observation ID
    df["obs_id"] = meta["product"] + "_" + df.index.astype(str)

    return df


def ingest_all_sources(input_dir: Path) -> pd.DataFrame:
    """Ingest all four NASA FIRMS sources into a unified observations DataFrame."""
    frames = []
    for stem, meta in SOURCES_METADATA.items():
        sub_df = load_single_source(input_dir, stem, meta)
        frames.append(sub_df)

    combined = pd.concat(frames, ignore_index=True)
    # Refresh obs_id across combined dataset to ensure global uniqueness
    combined["obs_id"] = (
        combined["source_product"] + "_" +
        combined["acq_date"].str.replace("-", "") + "_" +
        combined.index.astype(str)
    )
    return combined
