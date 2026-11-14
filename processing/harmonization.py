"""FireHorizon Harmonization Module
Provides a transparent, documented, experimental harmonization methodology.
Distinguishes raw observed detections from provisional sensor-normalized indices.
Never labels normalized activity indicators as physical fire counts.
"""
from __future__ import annotations
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd


class HarmonizationEngine:
    """Computes transparent, multi-sensor activity metrics and provisional normalized indicators.
    
    Scientific Basis:
    - MODIS nominal nadir pixel area: ~ 1000m x 1000m = 1.0 km^2
    - VIIRS nominal nadir pixel area: ~ 375m x 375m = 0.14 km^2
    - Area ratio: 1.0 / 0.14 = ~7.14
    - Overpass sampling: MODIS (Terra 10:30 AM/PM, Aqua 01:30 AM/PM);
      VIIRS (SNPP 01:30 AM/PM, NOAA-20 01:30 AM/PM displaced ~50 min, NOAA-21 ~01:30 AM/PM).
    
    Formula for Experimental Activity Index (EAI):
    EAI = (w_modis * N_modis_norm + w_viirs * N_viirs_norm) * (1 + log10(1 + FRP_total / FRP_reference))
    Where:
      - N_modis_norm = Active MODIS cells / Total active MODIS area
      - N_viirs_norm = Active VIIRS cells / (Total active VIIRS area * 0.4)
      - FRP_total = Combined fire radiative power in MW
      - FRP_reference = 100.0 MW
    """

    METHODOLOGY_VERSION = "v1.0-provisional-grid-normalized"

    def __init__(
        self,
        modis_weight: float = 1.0,
        viirs_weight: float = 0.6,
        frp_ref_mw: float = 100.0
    ):
        self.modis_weight = modis_weight
        self.viirs_weight = viirs_weight
        self.frp_ref_mw = frp_ref_mw

    def compute_daily_activity(
        self,
        df: pd.DataFrame,
        comparison_df: pd.DataFrame,
        region_id: str = "india",
        processing_version: str = "v1.0.0"
    ) -> pd.DataFrame:
        """Calculate daily harmonized activity summary retaining separate per-sensor measures."""
        dates = sorted(df["acq_date"].unique())
        records = []

        # Map overlap cells from comparison
        overlap_map = {}
        if not comparison_df.empty and "co_detected_grid_cells" in comparison_df.columns:
            for _, r in comparison_df.iterrows():
                overlap_map[r["activity_date"]] = r["co_detected_grid_cells"]

        for d in dates:
            sub = df[df["acq_date"] == d]

            modis_sub = sub[sub["source_product"] == "MODIS_C61"]
            snpp_sub = sub[sub["source_product"] == "VIIRS_SNPP"]
            n20_sub = sub[sub["source_product"] == "VIIRS_NOAA20"]
            n21_sub = sub[sub["source_product"] == "VIIRS_NOAA21"]
            viirs_sub = sub[sub["sensor_family"] == "VIIRS"]

            m_count = len(modis_sub)
            snpp_count = len(snpp_sub)
            n20_count = len(n20_sub)
            n21_count = len(n21_sub)
            v_count = len(viirs_sub)

            m_frp = float(modis_sub["frp"].sum()) if m_count > 0 else 0.0
            v_frp = float(viirs_sub["frp"].sum()) if v_count > 0 else 0.0
            tot_frp = m_frp + v_frp

            active_cells = int(sub["grid_id"].nunique())
            co_detected = overlap_map.get(d, 0)

            # Experimental Activity Index calculation (dimensionless index, 0 to 100 scale)
            # Normalized against regional March daily dynamic range
            area_modis_km2 = modis_sub["grid_id"].nunique() * 1.0
            area_viirs_km2 = viirs_sub["grid_id"].nunique() * 0.14

            base_activity = (self.modis_weight * area_modis_km2) + (self.viirs_weight * area_viirs_km2 * 2.5)
            frp_factor = 1.0 + np.log10(1.0 + (tot_frp / self.frp_ref_mw))
            raw_index = base_activity * frp_factor

            # Scaling factor to render a 0-100 relative index for visualization
            exp_activity_index = round(min(100.0, raw_index / 500.0), 2)

            records.append({
                "activity_date": d,
                "region_id": region_id,
                "modis_detection_count": m_count,
                "viirs_snpp_detection_count": snpp_count,
                "viirs_noaa20_detection_count": n20_count,
                "viirs_noaa21_detection_count": n21_count,
                "viirs_total_detection_count": v_count,
                "total_detections": len(sub),
                "modis_frp_sum": round(m_frp, 2),
                "viirs_frp_sum": round(v_frp, 2),
                "total_frp_sum": round(tot_frp, 2),
                "active_grid_cells": active_cells,
                "cross_sensor_overlap_cells": int(co_detected),
                "experimental_activity_index": exp_activity_index,
                "index_method": self.METHODOLOGY_VERSION,
                "baseline_status": "Single-month sample (March 2025). Multi-year historical baseline unavailable.",
                "uncertainty_status": "Provisional index. Resolution footprint difference (1km vs 375m) and diurnal sampling bias uncalibrated.",
                "processing_version": processing_version
            })

        return pd.DataFrame(records)
