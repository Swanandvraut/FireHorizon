# FireHorizon — NASA Space Apps Challenge 2026

**One Earth. Multiple Satellites. One Unified Fire Intelligence View.**

[![License: MIT](https://img.shields.io/badge/License-MIT-amber.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![React: 19](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![Database: Supabase](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-emerald.svg)](https://supabase.com/)
[![NASA Space Apps](https://img.shields.io/badge/NASA%20Space%20Apps-2026%20Kopargaon-orange.svg)](https://www.spaceappschallenge.org/)

---

## Challenge & Objective

- **Challenge:** Harmonization of MODIS and VIIRS Hot Spots  
- **Event:** NASA Space Apps Challenge 2026 — Kopargaon  
- **Team Members:**
  1. **Swanand Raut** — Full-Stack Software Engineer & Lead Architect
  2. **Swaral Dabhade** — Geospatial Data Scientist & Remote Sensing Analyst
  3. **Raj Dakle** — Database Architect & Cloud Infrastructure Engineer
  4. **Vishal Sable** — UI/UX Designer & Frontend Geospatial Developer

### Objective
FireHorizon reconciles active-fire observations from NASA **MODIS** (Terra & Aqua, 1000m nominal resolution) and **VIIRS** (Suomi-NPP, NOAA-20, NOAA-21, 375m resolution) into a consistent, spatially and temporally organized **Burning Activity Calendar**.

---

## Verified Dataset Snapshot (India, March 2025)

Ingested and verified from the 4 original NASA FIRMS archives with 100% provenance preservation:

| NASA FIRMS Archive File | Product | Instrument & Platform | Nominal Nadir Resolution | Verified Records |
|---|---|---|---|---:|
| `DL_FIRE_M-C61_846907.zip` | MODIS C6.1 | MODIS (Terra & Aqua) | 1000 m (1.0 km²) | **30,644** |
| `DL_FIRE_SV-C2_846910.zip` | VIIRS C2 | VIIRS (Suomi-NPP) | 375 m (0.14 km²) | **212,965** |
| `DL_FIRE_J1V-C2_846908.zip` | VIIRS C2 | VIIRS (NOAA-20 / JPSS-1) | 375 m (0.14 km²) | **213,338** |
| `DL_FIRE_J2V-C2_846909.zip` | VIIRS C2 | VIIRS (NOAA-21 / JPSS-2) | 375 m (0.14 km²) | **195,078** |
| **Combined National Total** | | | | **652,025** |
| **Maharashtra Subregion (Verified Polygon)** | | | | **77,534** (11.89%) |
| **Candidate MODIS-VIIRS Co-Detections** | $\Delta d \le 1\text{km}, \Delta t \le 60\text{min}$ | | | **142,748** |

---

## System Architecture

```mermaid
flowchart TD
    subgraph Ingestion ["1. Data Ingestion & Auditing"]
        Zips["NASA FIRMS Archives (4 ZIPs)"] --> Ingest["processing/ingestion.py"]
        Ingest --> Validate["processing/validation.py"]
    end

    subgraph SpatialFilter ["2. Spatial & Geographic Normalization"]
        GeoJSON["geoBoundaries Maharashtra GeoJSON"] --> Filter["processing/geographic_filter.py (Point-in-Polygon)"]
        Validate --> Filter
        Filter --> Grid["processing/spatial_grid.py (EPSG:6933 1km Grid)"]
    end

    subgraph Analytics ["3. Harmonization Engine"]
        Grid --> Agg["processing/daily_aggregation.py"]
        Agg --> Match["processing/sensor_comparison.py (KD-Tree Matching)"]
        Match --> Harmonize["processing/harmonization.py (Experimental Activity Index)"]
        Harmonize --> Calendar["processing/activity_calendar.py"]
        Harmonize --> Anomaly["processing/anomaly_detection.py (Intra-Month MAD)"]
    end

    subgraph StorageLayer ["4. Dual-Mode Storage & Presentation"]
        Calendar --> LocalBundle["frontend/public/data/ (Offline Fallback)"]
        Calendar --> Supabase["Supabase PostgreSQL (Row Level Security)"]
        LocalBundle --> ReactApp["FireHorizon React + Leaflet Dashboard"]
        Supabase -.-> ReactApp
    end
```

---

## Quickstart & Execution Guide

### 1. Python Geospatial Pipeline

```powershell
# Install Python dependencies
pip install pandas numpy scipy shapely pyproj pyyaml pytest requests psycopg[binary] supabase

# Download authentic Maharashtra administrative boundary GeoJSON
python scripts/download_boundary.py

# Execute the complete 8-stage processing pipeline
python -u scripts/run_pipeline.py

# Verify dataset reconciliation (confirms 652,025 rows and aggregations)
python scripts/verify_dataset.py

# Run Python automated test suite
python -m pytest tests/test_pipeline.py -v
```

### 2. Frontend Web Application

```powershell
# Navigate to frontend directory
cd frontend

# Install Node modules
npm install

# Run Vitest test suite
npx vitest run

# Run production build
npm run build

# Start local dev server
npm run dev
```

Open your browser at `http://localhost:5173`.

---

## Supabase PostgreSQL Cloud Integration

FireHorizon supports seamless synchronization to Supabase PostgreSQL:
1. Create a project at [supabase.com](https://supabase.com).
2. Execute `supabase/schema.sql` and `supabase/seed.sql` in the Supabase SQL editor.
3. Add your database connection URI to `.env`:
   ```env
   VITE_SUPABASE_URL=https://your-project.supabase.co
   VITE_SUPABASE_PUBLISHABLE_KEY=your-anon-key
   SUPABASE_DB_URL=postgresql://postgres:[PASSWORD]@db.your-project.supabase.co:5432/postgres
   ```
4. Run bulk import:
   ```powershell
   python scripts/import_to_supabase.py
   ```

*Strict Row Level Security (RLS) is enabled across all tables. Public clients have read-only (`SELECT`) access.*

---

## Repository Structure

```
FireHorizon/
│
├── frontend/                   # React 19 + Vite + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── components/         # Sidebar, Header, MetricCard
│   │   ├── views/              # Overview, FireMap, Calendar, Comparison, Analytics, Methodology, About
│   │   ├── services/           # Supabase & DataService (with resilient offline fallback)
│   │   └── types/              # TypeScript interfaces
│   └── public/data/            # Pipeline-generated JSON bundles & GeoJSON
│
├── processing/                 # Core Python Harmonization Engine
│   ├── ingestion.py            # Provenance-preserving archive ingestion
│   ├── validation.py           # Coordinate & row-count validation
│   ├── geographic_filter.py    # Maharashtra point-in-polygon filtering
│   ├── spatial_grid.py         # EPSG:6933 1km equal-area spatial grid
│   ├── daily_aggregation.py    # Grid-day sensor metrics
│   ├── sensor_comparison.py    # Spatial-temporal KD-Tree candidate matching
│   ├── harmonization.py        # Experimental Activity Index (EAI)
│   ├── activity_calendar.py    # Daily, weekly, monthly calendar hierarchy
│   ├── anomaly_detection.py    # Intra-month statistical variance (MAD)
│   └── generate_reports.py     # Frontend JSON bundle export
│
├── scripts/
│   ├── run_pipeline.py         # Master pipeline runner
│   ├── verify_dataset.py       # Automated data reconciliation script
│   ├── download_boundary.py    # Official Maharashtra boundary retriever
│   └── import_to_supabase.py   # Bulk importer for Supabase PostgreSQL
│
├── config/
│   └── settings.yaml           # Pipeline & grid configuration
│
├── supabase/
│   ├── migrations/             # Versioned SQL migrations
│   ├── schema.sql              # Complete PostgreSQL DDL with RLS
│   ├── seed.sql                # Reference metadata seed script
│   └── README.md               # Database setup guide
│
├── data/
│   ├── raw/                    # Original 4 NASA FIRMS ZIP archives (Preserved)
│   ├── boundaries/             # Official Maharashtra GeoJSON boundary
│   └── processed/              # Aggregated datasets, audits, and exports
│
├── docs/
│   ├── DATA_AUDIT.md           # Comprehensive data audit report
│   ├── METHODOLOGY.md          # Scientific methodology & EAI mathematical formula
│   ├── ARCHITECTURE.md         # System architecture & component design
│   ├── DATABASE.md             # Supabase table specifications & RLS policies
│   ├── SETUP_GUIDE.md          # Step-by-step installation instructions
│   ├── POWERSHELL_GUIDE.md     # Windows PowerShell commands
│   ├── TESTING.md              # Testing & validation evidence
│   ├── LIMITATIONS.md          # Scientific assumptions & uncertainties
│   ├── DEMO_SCRIPT.md          # Hackathon demonstration presentation script
│   ├── CITATIONS.md            # NASA FIRMS & boundary citations
│   └── NASA_SUBMISSION.md      # Space Apps submission summary
│
├── tests/
│   └── test_pipeline.py        # Pytest pipeline test suite
│
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
└── PROJECT_PROGRESS.md         # Implementation tracking dashboard
```

---

## Core Scientific Ground Rules

1. **Detections ≠ Physical Fires:** A satellite hotspot is an observation event, not a unique physical fire perimeter or ignition point.
2. **Confidence Scales are Segregated:** MODIS numeric (0–100%) and VIIRS categorical (`l`, `n`, `h`) are kept separate without arbitrary conversions.
3. **Verified Polygon Geometry:** Maharashtra is filtered via official administrative boundaries (geoBoundaries / DataMeet), never rough bounding boxes.
4. **Transparent Limitation Bounds:** The archive covers March 1–31, 2025. FireHorizon restricts anomaly calculations to intra-sample variance (MAD robust z-scores) and explicitly notes that multi-year seasonal baselines require 5+ years of data. Unvalidated early-warning forecast claims are prohibited.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.  
Satellite active fire data courtesy of NASA FIRMS. Administrative boundary courtesy of geoBoundaries gbOpen (CC BY 2.5 IN).
#   F i r e H o r i z o n  
 #   F i r e H o r i z o n  
 #   F i r e H o r i z o n  
 