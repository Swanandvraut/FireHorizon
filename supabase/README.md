# FireHorizon — Supabase Cloud Database Architecture

This directory contains the database schema, migrations, seed data, and Row Level Security (RLS) policies for **FireHorizon** on Supabase PostgreSQL.

## Architecture & Design Principles

1. **Quota & Size Protection**:
   - The raw archive contains 652,025 satellite detections.
   - For optimal performance and to remain comfortably within Supabase free-tier storage limits, FireHorizon stores the raw data locally while synchronizing the compact derived grid-day aggregations (`fire_grid_daily`), daily burning activity records (`activity_daily`), and sensor comparisons (`sensor_comparison_daily`).
   - If dedicated cloud storage is provisioned, the pipeline provides an optional raw observation table.

2. **Security & RLS**:
   - Row Level Security is enabled on all tables.
   - Anonymous web users have read-only access (`SELECT`) via `anon` key.
   - All write operations (`INSERT`, `UPDATE`, `DELETE`) require authenticated service role or direct connection string credentials.

3. **Reproducibility & Idempotency**:
   - All migrations and seed scripts use idempotent statements (`CREATE TABLE IF NOT EXISTS`, `ON CONFLICT DO UPDATE`).

## Setup Instructions

### Option A: Using Supabase Web Dashboard (Easiest)
1. Create a free project at [supabase.com](https://supabase.com).
2. Go to the **SQL Editor** tab in your dashboard.
3. Open `supabase/schema.sql` and click **Run**.
4. Open `supabase/seed.sql` and click **Run**.
5. Copy your project credentials:
   - Go to **Project Settings -> API** -> Copy `Project URL` and `anon public` key to `.env` as `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY`.
   - Go to **Project Settings -> Database** -> Copy the connection URI string to `.env` as `SUPABASE_DB_URL`.

### Option B: Using Supabase CLI
```bash
# Link local project to Supabase
supabase link --project-ref your-project-id

# Push migrations
supabase db push
```

## Running the Data Importer

Once `SUPABASE_DB_URL` is set in your environment:
```powershell
python scripts/import_to_supabase.py
```
