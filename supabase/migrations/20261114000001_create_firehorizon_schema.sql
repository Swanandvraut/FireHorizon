-- ==============================================================================
-- Migration: 20261114000001_create_firehorizon_schema.sql
-- Description: Initial schema for FireHorizon satellite harmonization database
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS public.data_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_product TEXT NOT NULL UNIQUE,
    sensor_family TEXT NOT NULL,
    satellite_platform TEXT NOT NULL,
    product_version TEXT NOT NULL,
    nominal_resolution_m INTEGER NOT NULL,
    date_start DATE NOT NULL,
    date_end DATE NOT NULL,
    source_filename TEXT NOT NULL,
    source_url TEXT,
    row_count INTEGER NOT NULL,
    imported_at TIMESTAMPTZ DEFAULT NOW(),
    citation TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS public.regions (
    id TEXT PRIMARY KEY,
    region_name TEXT NOT NULL,
    country TEXT NOT NULL,
    region_type TEXT NOT NULL,
    boundary_geojson JSONB,
    boundary_source TEXT NOT NULL,
    boundary_license TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.processing_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    processing_version TEXT NOT NULL,
    source_dataset TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    input_count INTEGER NOT NULL,
    output_count INTEGER NOT NULL,
    rejected_count INTEGER DEFAULT 0,
    status TEXT NOT NULL,
    configuration JSONB,
    report_path TEXT
);

CREATE TABLE IF NOT EXISTS public.fire_grid_daily (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    activity_date DATE NOT NULL,
    region_id TEXT NOT NULL REFERENCES public.regions(id) ON DELETE CASCADE,
    grid_id TEXT NOT NULL,
    grid_resolution_meters INTEGER NOT NULL,
    center_latitude DOUBLE PRECISION NOT NULL,
    center_longitude DOUBLE PRECISION NOT NULL,
    source_product TEXT NOT NULL,
    sensor_family TEXT NOT NULL,
    satellite_platform TEXT NOT NULL,
    detection_count INTEGER NOT NULL,
    frp_sum DOUBLE PRECISION NOT NULL,
    frp_mean DOUBLE PRECISION NOT NULL,
    frp_median DOUBLE PRECISION,
    frp_max DOUBLE PRECISION,
    brightness_mean DOUBLE PRECISION,
    day_count INTEGER NOT NULL,
    night_count INTEGER NOT NULL,
    confidence_summary JSONB,
    processing_version TEXT NOT NULL,
    CONSTRAINT uq_fire_grid_daily UNIQUE (activity_date, region_id, grid_id, source_product)
);

CREATE TABLE IF NOT EXISTS public.activity_daily (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    activity_date DATE NOT NULL,
    region_id TEXT NOT NULL REFERENCES public.regions(id) ON DELETE CASCADE,
    modis_detection_count INTEGER NOT NULL,
    viirs_snpp_detection_count INTEGER NOT NULL,
    viirs_noaa20_detection_count INTEGER NOT NULL,
    viirs_noaa21_detection_count INTEGER NOT NULL,
    total_detections INTEGER NOT NULL,
    modis_frp_sum DOUBLE PRECISION NOT NULL,
    viirs_frp_sum DOUBLE PRECISION NOT NULL,
    total_frp_sum DOUBLE PRECISION NOT NULL,
    active_grid_cells INTEGER NOT NULL,
    cross_sensor_overlap_cells INTEGER NOT NULL,
    experimental_activity_index DOUBLE PRECISION NOT NULL,
    index_method TEXT NOT NULL,
    baseline_status TEXT NOT NULL,
    uncertainty_status TEXT NOT NULL,
    processing_version TEXT NOT NULL,
    CONSTRAINT uq_activity_daily UNIQUE (activity_date, region_id)
);

CREATE TABLE IF NOT EXISTS public.sensor_comparison_daily (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    activity_date DATE NOT NULL,
    region_id TEXT NOT NULL REFERENCES public.regions(id) ON DELETE CASCADE,
    sensor_a TEXT NOT NULL,
    sensor_b TEXT NOT NULL,
    sensor_a_count INTEGER NOT NULL,
    sensor_b_count INTEGER NOT NULL,
    candidate_match_count INTEGER NOT NULL,
    co_detected_grid_cells INTEGER NOT NULL,
    distance_threshold_meters DOUBLE PRECISION NOT NULL,
    time_threshold_minutes DOUBLE PRECISION NOT NULL,
    methodology_version TEXT NOT NULL,
    CONSTRAINT uq_sensor_comparison_daily UNIQUE (activity_date, region_id, sensor_a, sensor_b)
);

CREATE TABLE IF NOT EXISTS public.candidate_sensor_matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    activity_date DATE NOT NULL,
    modis_obs_id TEXT NOT NULL,
    viirs_obs_id TEXT NOT NULL,
    distance_meters DOUBLE PRECISION NOT NULL,
    time_diff_minutes DOUBLE PRECISION NOT NULL,
    modis_platform TEXT,
    viirs_platform TEXT,
    modis_frp DOUBLE PRECISION,
    viirs_frp DOUBLE PRECISION,
    candidate_status TEXT NOT NULL,
    methodology_version TEXT NOT NULL,
    CONSTRAINT uq_candidate_match UNIQUE (modis_obs_id, viirs_obs_id)
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_fire_grid_date ON public.fire_grid_daily(activity_date);
CREATE INDEX IF NOT EXISTS idx_fire_grid_region ON public.fire_grid_daily(region_id);
CREATE INDEX IF NOT EXISTS idx_fire_grid_id ON public.fire_grid_daily(grid_id);
CREATE INDEX IF NOT EXISTS idx_fire_grid_coords ON public.fire_grid_daily(center_latitude, center_longitude);
CREATE INDEX IF NOT EXISTS idx_fire_grid_product ON public.fire_grid_daily(source_product);

CREATE INDEX IF NOT EXISTS idx_activity_daily_date ON public.activity_daily(activity_date);
CREATE INDEX IF NOT EXISTS idx_activity_daily_region ON public.activity_daily(region_id);

CREATE INDEX IF NOT EXISTS idx_sensor_comp_date ON public.sensor_comparison_daily(activity_date);
CREATE INDEX IF NOT EXISTS idx_sensor_comp_region ON public.sensor_comparison_daily(region_id);

-- Row Level Security
ALTER TABLE public.data_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.regions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processing_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fire_grid_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sensor_comparison_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.candidate_sensor_matches ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read data_sources" ON public.data_sources FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read regions" ON public.regions FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read processing_runs" ON public.processing_runs FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read fire_grid_daily" ON public.fire_grid_daily FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read activity_daily" ON public.activity_daily FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read sensor_comparison_daily" ON public.sensor_comparison_daily FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public read candidate_sensor_matches" ON public.candidate_sensor_matches FOR SELECT TO anon, authenticated USING (true);
