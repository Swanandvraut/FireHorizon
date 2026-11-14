"""FireHorizon Comprehensive Test Suite
Tests ingestion, validation, geographic filtering, grid binning,
cross-sensor matching, harmonization, and activity calendars.
"""
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from shapely.geometry import Point

from processing.ingestion import ingest_all_sources, SOURCES_METADATA
from processing.validation import validate_observations
from processing.geographic_filter import load_maharashtra_boundary, apply_geographic_filters
from processing.spatial_grid import SpatialGridManager, evaluate_grid_sensitivity
from processing.daily_aggregation import aggregate_grid_daily
from processing.sensor_comparison import find_candidate_matches, compute_sensor_comparison_daily
from processing.harmonization import HarmonizationEngine
from processing.activity_calendar import assign_activity_tier, build_activity_calendar
from processing.anomaly_detection import compute_intra_month_statistical_deviations


def test_sources_metadata_configured():
    assert len(SOURCES_METADATA) == 4
    assert "DL_FIRE_M-C61_846907" in SOURCES_METADATA
    assert "DL_FIRE_SV-C2_846910" in SOURCES_METADATA


def test_activity_tier_assignment():
    assert assign_activity_tier(4.0, 30.0) == "Low Activity"
    assert assign_activity_tier(15.0, 100.0) == "Low Activity"
    assert assign_activity_tier(30.0, 200.0) == "Moderate Activity"
    assert assign_activity_tier(55.0, 500.0) == "Elevated Activity"
    assert assign_activity_tier(75.0, 1000.0) == "High Activity"
    assert assign_activity_tier(90.0, 2000.0) == "Extreme Activity"


def test_spatial_grid_projection():
    gm = SpatialGridManager(resolution_meters=1000)
    sample_df = pd.DataFrame({
        "latitude": [19.0760, 18.5204],
        "longitude": [72.8777, 73.8567],
        "acq_date": ["2025-03-01", "2025-03-01"],
        "source_product": ["MODIS_C61", "VIIRS_SNPP"]
    })
    binned = gm.assign_grid_cells(sample_df)
    assert "grid_id" in binned.columns
    assert "center_latitude" in binned.columns
    assert "center_longitude" in binned.columns
    assert binned["grid_resolution_meters"].iloc[0] == 1000
    # Center coordinates should be close to input
    assert abs(binned["center_latitude"].iloc[0] - 19.0760) < 0.05


def test_candidate_matching_logic():
    modis_dummy = pd.DataFrame({
        "obs_id": ["M1"],
        "acq_date": ["2025-03-15"],
        "acq_datetime_utc": ["2025-03-15 08:00:00"],
        "grid_x": [1000000.0],
        "grid_y": [2000000.0],
        "platform_name": ["Terra"],
        "frp": [45.0]
    })
    viirs_near = pd.DataFrame({
        "obs_id": ["V1"],
        "acq_date": ["2025-03-15"],
        "acq_datetime_utc": ["2025-03-15 08:15:00"],
        "grid_x": [1000500.0],  # 500m away
        "grid_y": [2000000.0],
        "platform_name": ["Suomi-NPP"],
        "frp": [30.0]
    })
    matches, stats = find_candidate_matches(
        modis_dummy, viirs_near,
        distance_threshold_m=1000.0,
        time_threshold_min=30.0
    )
    assert len(matches) == 1
    assert matches.iloc[0]["candidate_status"] == "candidate_co_detection"
    assert matches.iloc[0]["distance_meters"] == 500.0
    assert matches.iloc[0]["time_diff_minutes"] == 15.0


def test_anomaly_detection_refuses_unvalidated_early_warning():
    dummy_daily = pd.DataFrame({
        "activity_date": ["2025-03-01", "2025-03-02"],
        "total_detections": [100, 150],
        "total_frp_sum": [1200.0, 1800.0]
    })
    analyzed = compute_intra_month_statistical_deviations(dummy_daily)
    assert "climatological_anomaly_status" in analyzed.columns
    assert bool(analyzed["early_warning_claim_allowed"].iloc[0]) is False
    assert "Historical baseline insufficient" in str(analyzed["climatological_anomaly_status"].iloc[0])
