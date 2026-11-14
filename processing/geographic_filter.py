"""FireHorizon Geographic Filtering Module
Provides point-in-polygon filtering against verified administrative boundaries.
Never uses rough bounding boxes as an approximation for final filtering.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Tuple, Optional
import numpy as np
import pandas as pd
from shapely.geometry import shape, Point, MultiPolygon, Polygon
from shapely.prepared import prep


class BoundaryNotFoundError(FileNotFoundError):
    """Raised when an administrative boundary file is missing."""
    pass


def load_maharashtra_boundary(geojson_path: Path) -> Tuple[MultiPolygon | Polygon, dict]:
    """Load and validate the official Maharashtra boundary polygon."""
    if not geojson_path.exists():
        raise BoundaryNotFoundError(
            f"Required Maharashtra administrative boundary file not found at: {geojson_path}. "
            "Per scientific rules, bounding box approximations are disallowed. "
            "Please run scripts/download_boundary.py to fetch the authentic geoBoundaries file."
        )

    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data.get("features"):
        raise ValueError(f"GeoJSON at {geojson_path} contains no features.")

    feature = data["features"][0]
    geom = shape(feature["geometry"])
    metadata = data.get("metadata", {
        "region_name": "Maharashtra",
        "country": "India",
        "source": "geoBoundaries gbOpen (ADM1) / DataMeet",
        "license": "Creative Commons Attribution 2.5 India (CC BY 2.5 IN)"
    })
    return geom, metadata


def apply_geographic_filters(
    df: pd.DataFrame,
    geojson_path: Path
) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Apply point-in-polygon filtering for Maharashtra while preserving India-wide dataset.
    
    Returns:
        df_india: full dataset with 'in_maharashtra' boolean column
        df_maharashtra: subset matching Maharashtra polygon
        metadata: boundary provenance information
    """
    import shapely
    mh_geom, metadata = load_maharashtra_boundary(geojson_path)
    minx, miny, maxx, maxy = mh_geom.bounds

    lats = df["latitude"].values
    lons = df["longitude"].values

    # Pre-filter candidate points using polygon bounding box
    in_bbox = (lons >= minx) & (lons <= maxx) & (lats >= miny) & (lats <= maxy)
    bbox_indices = np.where(in_bbox)[0]

    # Vectorized C-level GEOS point-in-polygon test
    in_poly_flags = np.zeros(len(df), dtype=bool)
    if len(bbox_indices) > 0:
        poly_matches = shapely.contains_xy(mh_geom, lons[bbox_indices], lats[bbox_indices])
        in_poly_flags[bbox_indices] = poly_matches

    df = df.copy()
    df["in_maharashtra"] = in_poly_flags
    df_maharashtra = df[df["in_maharashtra"]].copy()

    return df, df_maharashtra, metadata
