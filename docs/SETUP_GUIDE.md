# FireHorizon — Setup & Installation Guide

This guide provides complete instructions for setting up, running, testing, and deploying **FireHorizon** on local developer machines (Windows / macOS / Linux) and connecting to Supabase Cloud.

---

## 1. Prerequisites

- **Python 3.10+** (Python 3.11, 3.12, or 3.13 tested)
- **Node.js 18+** (Node v20 or v24 tested)
- **Git**
- Optional: Free account at [supabase.com](https://supabase.com)

---

## 2. Python Backend & Data Engine Setup

### Step 1: Install Python Dependencies
```bash
pip install pandas numpy scipy shapely pyproj pyyaml pytest requests psycopg[binary] supabase
```

### Step 2: Acquire Official Maharashtra Administrative Boundary
```bash
python scripts/download_boundary.py
```
*Extracts the verified administrative GeoJSON polygon from geoBoundaries gbOpen (`data/boundaries/maharashtra.geojson`).*

### Step 3: Run the Master Processing Pipeline
```bash
python -u scripts/run_pipeline.py
```
*This executes all 8 stages:*
1. Ingests all 4 NASA FIRMS archives (652,025 records).
2. Validates coordinates and generates audit logs.
3. Filters Maharashtra observations using authentic polygon geometry.
4. Projects observations into 1km equal-area spatial grid (`EPSG:6933`).
5. Generates daily sensor-specific grid aggregations.
6. Conducts spatial-temporal candidate co-detection matching.
7. Calculates the Experimental Activity Index (EAI) and calendar hierarchy.
8. Exports optimized JSON bundles into `frontend/public/data/`.

### Step 4: Run Verification Tests
```bash
# Run automated reconciliation check
python scripts/verify_dataset.py

# Run unit tests
python -m pytest tests/test_pipeline.py
```

---

## 3. Frontend Web Application Setup

### Step 1: Install Dependencies
```bash
cd frontend
npm install
```

### Step 2: Start Development Server
```bash
npm run dev
```
Open your browser at `http://localhost:5173`.

### Step 3: Run Frontend Unit Tests & Build
```bash
# Run unit tests
npx vitest run

# Test production build
npm run build
```

---

## 4. Supabase Cloud Database Integration (Optional Cloud Mode)

FireHorizon is built with **hybrid cloud-resilient architecture**: it runs 100% offline using pre-packaged verified data bundles, and can seamlessly connect to a live Supabase PostgreSQL database when configured.

1. Create a project at [supabase.com](https://supabase.com).
2. Run `supabase/schema.sql` and `supabase/seed.sql` in the Supabase SQL Editor.
3. Configure your `.env` in the repository root:
   ```env
   VITE_SUPABASE_URL=https://your-project.supabase.co
   VITE_SUPABASE_PUBLISHABLE_KEY=your-anon-key
   SUPABASE_DB_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres
   ```
4. Bulk-import the derived records into Supabase:
   ```bash
   python scripts/import_to_supabase.py
   ```
