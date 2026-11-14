# FireHorizon — Database Documentation & Schema Reference

**Database Platform:** Supabase PostgreSQL  
**Authentication & Security:** Row Level Security (RLS) Active  
**Projection & Coordinates:** WGS 84 (`EPSG:4326`) and Equal Area Grid (`EPSG:6933`)

---

## 1. Table Specifications

### `public.data_sources`
Tracks original NASA satellite product metadata and download provenance.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PRIMARY KEY | Unique identifier |
| `source_product` | `TEXT` | NOT NULL UNIQUE | E.g. `MODIS_C61`, `VIIRS_SNPP` |
| `sensor_family` | `TEXT` | NOT NULL | `MODIS` or `VIIRS` |
| `satellite_platform` | `TEXT` | NOT NULL | E.g. `Terra/Aqua`, `Suomi-NPP`, `NOAA-20`, `NOAA-21` |
| `product_version` | `TEXT` | NOT NULL | E.g. `Collection 6.1`, `Collection 2` |
| `nominal_resolution_m` | `INTEGER` | NOT NULL | 1000m for MODIS; 375m for VIIRS |
| `date_start` | `DATE` | NOT NULL | Start date of archive |
| `date_end` | `DATE` | NOT NULL | End date of archive |
| `source_filename` | `TEXT` | NOT NULL | Archive ZIP file name |
| `source_url` | `TEXT` | NULLABLE | NASA FIRMS source URL |
| `row_count` | `INTEGER` | NOT NULL | Total verified raw rows |
| `imported_at` | `TIMESTAMPTZ` | DEFAULT NOW() | Timestamp of import |
| `citation` | `TEXT` | NOT NULL | Official NASA product citation |

---

### `public.regions`
Stores administrative spatial entities and boundaries.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `TEXT` | PRIMARY KEY | E.g. `india`, `maharashtra` |
| `region_name` | `TEXT` | NOT NULL | Display name |
| `country` | `TEXT` | NOT NULL | Country name |
| `region_type` | `TEXT` | NOT NULL | `Country`, `State`, etc. |
| `boundary_geojson`| `JSONB` | NULLABLE | Boundary GeoJSON geometry |
| `boundary_source` | `TEXT` | NOT NULL | E.g. `geoBoundaries gbOpen (ADM1) / DataMeet` |
| `boundary_license` | `TEXT` | NOT NULL | E.g. `Creative Commons Attribution 2.5 India` |

---

### `public.fire_grid_daily`
Compact spatial grid-day aggregations per sensor.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `UUID` | PRIMARY KEY | Unique identifier |
| `activity_date` | `DATE` | NOT NULL | UTC observation date |
| `region_id` | `TEXT` | NOT NULL, FK(`regions.id`) | Geographic region reference |
| `grid_id` | `TEXT` | NOT NULL | 1km grid cell ID (`GRID_1000M_R{r}_C{c}`) |
| `grid_resolution_meters` | `INTEGER` | NOT NULL | Grid cell size (1000m) |
| `center_latitude` | `DOUBLE PRECISION` | NOT NULL | Cell center latitude |
| `center_longitude` | `DOUBLE PRECISION` | NOT NULL | Cell center longitude |
| `source_product` | `TEXT` | NOT NULL | Satellite product name |
| `sensor_family` | `TEXT` | NOT NULL | `MODIS` or `VIIRS` |
| `satellite_platform`| `TEXT` | NOT NULL | E.g. `Terra`, `Aqua`, `Suomi-NPP` |
| `detection_count` | `INTEGER` | NOT NULL | Satellite observation count (NOT unique fires) |
| `frp_sum` | `DOUBLE PRECISION` | NOT NULL | Summed FRP (MW) |
| `frp_mean` | `DOUBLE PRECISION` | NOT NULL | Average FRP (MW) |
| `frp_median` | `DOUBLE PRECISION` | NULLABLE | Median FRP (MW) |
| `frp_max` | `DOUBLE PRECISION` | NULLABLE | Peak FRP (MW) |
| `brightness_mean` | `DOUBLE PRECISION` | NULLABLE | Mean 4µm brightness temp (Kelvin) |
| `day_count` | `INTEGER` | NOT NULL | Daytime pass detections |
| `night_count` | `INTEGER` | NOT NULL | Nighttime pass detections |
| `confidence_summary` | `JSONB` | NOT NULL | Breakdown by sensor confidence |
| `processing_version` | `TEXT` | NOT NULL | Version of the pipeline |

---

### `public.activity_daily`
Daily aggregated burning activity indices and cross-sensor overlap metrics.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `activity_date` | `DATE` | NOT NULL | UTC observation date |
| `region_id` | `TEXT` | NOT NULL, FK(`regions.id`) | Geographic region reference |
| `modis_detection_count` | `INTEGER` | NOT NULL | Daily MODIS detections |
| `viirs_snpp_detection_count`| `INTEGER` | NOT NULL | Suomi-NPP detections |
| `viirs_noaa20_detection_count`| `INTEGER` | NOT NULL | NOAA-20 detections |
| `viirs_noaa21_detection_count`| `INTEGER` | NOT NULL | NOAA-21 detections |
| `total_detections` | `INTEGER` | NOT NULL | Total satellite detections |
| `modis_frp_sum` | `DOUBLE PRECISION` | NOT NULL | MODIS total FRP (MW) |
| `viirs_frp_sum` | `DOUBLE PRECISION` | NOT NULL | VIIRS total FRP (MW) |
| `total_frp_sum` | `DOUBLE PRECISION` | NOT NULL | Combined FRP (MW) |
| `active_grid_cells` | `INTEGER` | NOT NULL | Distinct 1km grid cells active |
| `cross_sensor_overlap_cells`| `INTEGER` | NOT NULL | Cells with simultaneous detections |
| `experimental_activity_index`| `DOUBLE PRECISION` | NOT NULL | Normalized activity score (0–100) |
| `index_method` | `TEXT` | NOT NULL | Method label (`v1.0-provisional`) |
| `baseline_status` | `TEXT` | NOT NULL | Climatological baseline status note |
| `uncertainty_status` | `TEXT` | NOT NULL | Scientific uncertainty notice |

---

## 2. Row Level Security (RLS)

All tables strictly enforce:
```sql
ALTER TABLE public.<table_name> ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read <table_name>" ON public.<table_name> FOR SELECT TO anon, authenticated USING (true);
```
Direct writes are prohibited from client-side public tokens.
