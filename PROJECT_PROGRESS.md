# FireHorizon — Project Progress & Implementation Tracker
**Event:** NASA Space Apps Challenge 2026 — Kopargaon  
**Challenge:** Harmonization of MODIS and VIIRS Hot Spots  
**Team:** Swanand Raut, Swaral Dabhade, Raj Dakle, Vishal Sable  
**Application:** FireHorizon (Satellite Harmonization & Integrated Burning Activity Calendar)

---

## Progress Dashboard

| Phase | Description | Status | Evidence / Artifacts |
|---|---|---|---|
| **Phase 1** | Inspect Existing Data & Setup Project Structure | **COMPLETED** | 4 original NASA ZIPs verified, 652,025 raw rows confirmed |
| **Phase 2** | Complete Python Processing Pipeline | **COMPLETED** | `processing/` modules (ingestion, validation, grid, aggregation, matching, harmonization) |
| **Phase 3** | Maharashtra Geographic Filtering (GeoJSON Boundary) | **COMPLETED** | `data/boundaries/maharashtra.geojson` (geoBoundaries gbOpen ADM1), 77,534 records filtered |
| **Phase 4** | Common Spatial Grid (EPSG:6933) & Daily Aggregations | **COMPLETED** | 1km equal-area grid, 487,134 India grid-day cells, 59,901 Maharashtra cells |
| **Phase 5** | Sensor Comparison & Transparent Harmonization | **COMPLETED** | 142,748 candidate co-detections ($\Delta d \le 1\text{km}, \Delta t \le 60\text{min}$), EAI formulated |
| **Phase 6** | Supabase PostgreSQL Schema, RLS & Importers | **COMPLETED** | `supabase/schema.sql`, migrations, seed script, idempotent `scripts/import_to_supabase.py` |
| **Phase 7** | Frontend Web Application (React + Vite + TS + Tailwind) | **COMPLETED** | 7 polished views: Overview, FireMap, Calendar, Comparison, Analytics, Methodology, About |
| **Phase 8** | Supabase Integration & Offline Fallback Pipeline | **COMPLETED** | `dataService.ts` with direct Supabase client + verified `/data/` JSON bundle fallback |
| **Phase 9** | Comprehensive Testing & Scientific Validation | **COMPLETED** | Pytest (5/5 PASS), Vitest (2/2 PASS), verification script (6/6 checks PASS), clean Vite build |
| **Phase 10** | Documentation, Screenshots & NASA Deliverables | **COMPLETED** | All 12 required docs, PowerShell commands, citations, demo script, and Space Apps submission |

---

## Key Scientific Ground Rules Maintained
1. **Never alter or overwrite original raw NASA ZIP archives:** All 4 raw archives preserved in `data/raw/`.
2. **Detection count $\ne$ unique physical fires:** Clearly labeled as satellite observation detections / candidate co-detections.
3. **MODIS numeric confidence $\ne$ VIIRS categorical confidence:** Preserved distinctly without naive conversion.
4. **Historical baseline limitation explicitly stated:** Single-month sample (March 1–31, 2025); climatological early-warning claims held unvalidated pending multi-year archive.
5. **Accurate administrative boundary:** Official geoBoundaries polygon used for Maharashtra with CC BY 2.5 IN attribution.
