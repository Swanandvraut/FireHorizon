-- ==============================================================================
-- FireHorizon Seed Data (Initial Reference Metadata)
-- ==============================================================================

-- 1. Insert Reference Regions
INSERT INTO public.regions (id, region_name, country, region_type, boundary_source, boundary_license)
VALUES
    ('india', 'India (National)', 'India', 'Country', 'Survey of India / Natural Earth', 'Public Domain / Open Data'),
    ('maharashtra', 'Maharashtra', 'India', 'State', 'geoBoundaries (gbOpen ADM1) / DataMeet / Election Commission of India', 'Creative Commons Attribution 2.5 India (CC BY 2.5 IN)')
ON CONFLICT (id) DO NOTHING;

-- 2. Insert Data Sources Provenance Metadata
INSERT INTO public.data_sources (
    source_product, sensor_family, satellite_platform, product_version,
    nominal_resolution_m, date_start, date_end, source_filename,
    row_count, citation
)
VALUES
    (
        'MODIS_C61', 'MODIS', 'Terra/Aqua', 'Collection 6.1', 1000,
        '2025-03-01', '2025-03-31', 'DL_FIRE_M-C61_846907.zip', 30644,
        'NASA FIRMS MODIS Collection 6.1 Active Fire Product (MOD14/MYD14)'
    ),
    (
        'VIIRS_SNPP', 'VIIRS', 'Suomi-NPP', 'Collection 2', 375,
        '2025-03-01', '2025-03-31', 'DL_FIRE_SV-C2_846910.zip', 212965,
        'NASA FIRMS Suomi-NPP VIIRS 375m Active Fire Product (VNP14IMGTDL_NRT / Collection 2)'
    ),
    (
        'VIIRS_NOAA20', 'VIIRS', 'NOAA-20', 'Collection 2', 375,
        '2025-03-01', '2025-03-31', 'DL_FIRE_J1V-C2_846908.zip', 213338,
        'NASA FIRMS NOAA-20 (JPSS-1) VIIRS 375m Active Fire Product (VJ114IMGTDL_NRT / Collection 2)'
    ),
    (
        'VIIRS_NOAA21', 'VIIRS', 'NOAA-21', 'Collection 2', 375,
        '2025-03-01', '2025-03-31', 'DL_FIRE_J2V-C2_846909.zip', 195078,
        'NASA FIRMS NOAA-21 (JPSS-2) VIIRS 375m Active Fire Product (VJ214IMGTDL_NRT / Collection 2)'
    )
ON CONFLICT (source_product) DO UPDATE SET
    row_count = EXCLUDED.row_count,
    imported_at = NOW();
