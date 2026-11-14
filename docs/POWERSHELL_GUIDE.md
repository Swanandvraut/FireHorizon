# FireHorizon — Windows PowerShell Command Reference

This document provides exact, copy-pasteable Windows PowerShell terminal commands for running every component of FireHorizon.

---

## 1. Setup & Python Environment

```powershell
# Verify Python and Node installations
python --version
node -v
npm -v

# Install required Python packages
pip install pandas numpy scipy shapely pyproj pyyaml pytest requests psycopg[binary] supabase
```

---

## 2. Running Data Processing & Verification

```powershell
# 1. Download official Maharashtra GeoJSON boundary
python scripts/download_boundary.py

# 2. Execute full end-to-end data processing pipeline
python -u scripts/run_pipeline.py

# 3. Verify data reconciliation (asserts 652,025 rows, coordinates, and aggregation match)
python scripts/verify_dataset.py

# 4. Run Pytest suite
python -m pytest tests/test_pipeline.py -v
```

---

## 3. Running the Frontend Web Dashboard

```powershell
# Move to frontend directory
cd frontend

# Install dependencies
npm install

# Run Vitest test suite
npx vitest run

# Test production build
npm run build

# Start local development server
npm run dev
```

---

## 4. Supabase Database Synchronization

```powershell
# Set Supabase connection string in PowerShell session (example):
$env:SUPABASE_DB_URL = "postgresql://postgres.[PROJECT_ID]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres"

# Execute bulk import of derived tables
python scripts/import_to_supabase.py
```
