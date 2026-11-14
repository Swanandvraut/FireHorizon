"""FireHorizon Spatial Grid Module
Constructs an equal-area spatial grid (EPSG:6933) for sensor comparison and aggregation.
Supports configurable grid resolutions (500m, 1km, 2km).
Maintains grid row/col, cell identifiers, center coordinates, and resolution metadata.
"""
from __future__ import annotations
from typing import Tuple, Dict
import numpy as np
import pandas as pd
from pyproj import Transformer

DEFAULT_PROJECTION = "EPSG:6933"  # WGS 84 / World Cylindrical Equal Area


class SpatialGridManager:
    """Manages projection and spatial binning onto a regular equal-area grid."""

    def __init__(self, resolution_meters: int = 1000, crs: str = DEFAULT_PROJECTION):
        self.resolution_meters = resolution_meters
        self.crs = crs
        # EPSG:4326 (lat, lon) to EPSG:6933 (x, y in meters)
        self.to_proj = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
        # EPSG:6933 to EPSG:4326
        self.to_wgs84 = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)

    def assign_grid_cells(self, df: pd.DataFrame) -> pd.DataFrame:
        """Assign equal-area grid cell ID, row, col, and cell center coordinates."""
        lons = df["longitude"].values
        lats = df["latitude"].values

        # Project lon, lat to x, y in meters
        x_coords, y_coords = self.to_proj.transform(lons, lats)

        res = self.resolution_meters
        # Snap to grid cell integer indices
        grid_col = np.floor(x_coords / res).astype(np.int64)
        grid_row = np.floor(y_coords / res).astype(np.int64)

        # Compute cell centers in projected coordinates
        center_x = (grid_col + 0.5) * res
        center_y = (grid_row + 0.5) * res

        # Transform center points back to geographic WGS84 coordinates (lon, lat)
        center_lon, center_lat = self.to_wgs84.transform(center_x, center_y)

        # Build standardized grid ID
        res_tag = f"{int(res)}M"
        grid_id = [
            f"GRID_{res_tag}_R{r}_C{c}" for r, c in zip(grid_row, grid_col)
        ]

        df = df.copy()
        df["grid_id"] = grid_id
        df["grid_row"] = grid_row
        df["grid_col"] = grid_col
        df["grid_resolution_meters"] = res
        df["grid_x"] = x_coords
        df["grid_y"] = y_coords
        df["center_latitude"] = np.round(center_lat, 5)
        df["center_longitude"] = np.round(center_lon, 5)

        return df


def evaluate_grid_sensitivity(df_sample: pd.DataFrame, resolutions: list[int] = [500, 1000, 2000]) -> Dict[int, dict]:
    """Evaluate grid sensitivity across resolutions (e.g. 500m, 1km, 2km)."""
    sensitivity_results = {}
    for res in resolutions:
        gm = SpatialGridManager(resolution_meters=res)
        res_df = gm.assign_grid_cells(df_sample)
        unique_cells = res_df["grid_id"].nunique()
        mean_obs_per_cell = len(res_df) / max(unique_cells, 1)
        sensitivity_results[res] = {
            "resolution_meters": res,
            "total_observations": len(res_df),
            "unique_active_cells": unique_cells,
            "mean_observations_per_cell": round(mean_obs_per_cell, 3)
        }
    return sensitivity_results
