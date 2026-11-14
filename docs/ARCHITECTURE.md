# FireHorizon — System Architecture

**NASA Space Apps Challenge 2026: Harmonization of MODIS and VIIRS Hot Spots**

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph Data Sources ["NASA FIRMS Raw Archives (India 2025-03)"]
        MODIS["MODIS C6.1 Terra & Aqua<br/>(30,644 rows)"]
        SNPP["VIIRS Suomi-NPP C2<br/>(212,965 rows)"]
        NOAA20["VIIRS NOAA-20 C2<br/>(213,338 rows)"]
        NOAA21["VIIRS NOAA-21 C2<br/>(195,078 rows)"]
    end

    subgraph Processing Engine ["Python Geospatial Processing Pipeline"]
        Ingest["ingestion.py<br/>Standardize & Preserve Provenance"]
        Validate["validation.py<br/>Audits, Coordinate & FRP Bounds"]
        GeoFilter["geographic_filter.py<br/>Maharashtra Boundary Point-in-Polygon"]
        Grid["spatial_grid.py<br/>1km Equal-Area Grid (EPSG:6933)"]
        DailyAgg["daily_aggregation.py<br/>Grid-Day Sensor Metrics"]
        SensorMatch["sensor_comparison.py<br/>MODIS-VIIRS Spatial-Temporal KD-Tree Match"]
        Harmonize["harmonization.py<br/>Experimental Activity Index (EAI)"]
        Calendar["activity_calendar.py<br/>Daily, Weekly & Monthly Calendar Tiers"]
        Anomaly["anomaly_detection.py<br/>Intra-Month Variance (MAD, Robust Z)"]
    end

    subgraph Storage ["Database & Storage Layer"]
        LocalData["Local Processed CSV & JSON Exports<br/>(Full Provenance / Offline Fallback)"]
        Supabase["Supabase Cloud PostgreSQL<br/>(RLS, Idempotent Bulk Imports, PostGIS)"]
    end

    subgraph Frontend ["FireHorizon Interactive Web Dashboard"]
        Vite["React 18 + Vite + TypeScript + Tailwind CSS"]
        Overview["1. Overview Dashboard"]
        Map["2. Interactive Leaflet Fire Map"]
        CalView["3. Burning Activity Calendar"]
        SensorComp["4. Sensor Comparison Module"]
        RegAnalytics["5. Regional Analytics"]
        Methodology["6. Scientific Methodology & Provenance"]
        About["7. Team & Challenge Information"]
    end

    MODIS --> Ingest
    SNPP --> Ingest
    NOAA20 --> Ingest
    NOAA21 --> Ingest

    Ingest --> Validate --> GeoFilter --> Grid --> DailyAgg
    DailyAgg --> SensorMatch --> Harmonize --> Calendar --> Anomaly

    DailyAgg --> LocalData
    Harmonize --> LocalData
    Calendar --> LocalData
    SensorMatch --> LocalData

    LocalData --> Supabase
    LocalData --> Frontend
    Supabase -.-> Frontend
```

---

## 2. Component Breakdown

### A. Python Geospatial Pipeline
- **Environment:** Python 3.11+
- **Core Libraries:** `pandas`, `numpy`, `scipy.spatial` (`cKDTree`), `shapely`, `pyproj`, `psycopg`
- **Projection Standard:** Equal-area `EPSG:6933` (World Cylindrical Equal Area) eliminates latitude distortion across the Indian subcontinent.

### B. Cloud Database (Supabase PostgreSQL)
- **Engine:** PostgreSQL 15+ hosted on Supabase
- **Security:** Strict Row Level Security (RLS) enabled on all 7 tables. Public anonymous access is read-only (`SELECT`). Bulk write operations use direct database connection strings via `psycopg`.
- **Performance Indexes:** B-tree indexes on `(activity_date)`, `(region_id)`, `(grid_id)`, and `(center_latitude, center_longitude)`.

### C. Frontend Web Application
- **Framework:** React + Vite + TypeScript + Tailwind CSS
- **Interactive Geospatial Visualization:** Leaflet & React Leaflet with dynamic layer switching (MODIS, VIIRS SNPP, VIIRS NOAA-20, VIIRS NOAA-21, Composite Activity).
- **Analytics & Time Series:** Recharts for sensor comparisons, FRP distribution, and diurnal profiles.
- **Data Resilience:** Direct Supabase client integration with automatic fallback to pre-computed JSON bundles for offline demonstration.
