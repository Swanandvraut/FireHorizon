# FireHorizon — NASA Space Apps Challenge 2026 Submission Summary

**Challenge:** Harmonization of MODIS and VIIRS Hot Spots  
**Project Title:** FireHorizon — Satellite Harmonization & Integrated Burning Activity Calendar  
**Team Name:** FireHorizon Team  
**Event Location:** Kopargaon, India  
**Team Members:**
1. Swanand Raut
2. Swaral Dabhade
3. Raj Dakle
4. Vishal Sable

---

## Short Description
FireHorizon is a scientific web application and geospatial processing pipeline that harmonizes NASA MODIS and VIIRS satellite active fire observations into an intuitive, spatially and temporally organized burning activity calendar.

---

## Detailed Project Description

### The Challenge
Environmental researchers, forest managers, and emergency response teams rely on NASA FIRMS satellite active-fire observations to track wildfires and biomass burning. However, the two primary observation instruments—MODIS (Terra & Aqua, 1000m nominal resolution) and VIIRS (Suomi-NPP, NOAA-20, NOAA-21, 375m resolution)—operate with distinct optical footprints, detection thresholds, and overpass orbits. A single physical fire can produce 5 to 10 times more detection points in VIIRS than in MODIS. Summing them naively distorts true fire activity.

### Our Solution
FireHorizon delivers an end-to-end open-source solution:
1. **Provenance-Preserving Ingestion:** Ingests and standardizes 652,025 raw observations from all 4 NASA FIRMS archives covering India (March 1–31, 2025).
2. **Equal-Area Grid Normalization:** Projects observations into `EPSG:6933` (World Cylindrical Equal Area) 1km grid cells, eliminating latitudinal surface area distortions.
3. **Verified Administrative Filtering:** Accurately isolates Maharashtra using authentic administrative boundaries (77,534 detections) rather than rough bounding rectangles.
4. **Spatial-Temporal Candidate Matching:** Employs $k$-d trees to identify 142,748 candidate co-detections ($\Delta d \le 1\text{km}, \Delta t \le 60\text{min}$) without discarding unmatched observations.
5. **Experimental Activity Index (EAI):** Formulates a transparent, dimensionally sound composite index that normalizes for sensor footprint areas and logarithmic fire radiative energy.
6. **Burning Activity Calendar:** Features daily, weekly, and monthly heatmaps with documented intensity categories (Low, Moderate, Elevated, High, Extreme).
7. **Cloud Database Architecture:** Backed by Supabase PostgreSQL with strict Row Level Security (RLS) policies and idempotent psycopg bulk import scripts.
8. **Scientific Integrity:** Strictly avoids unvalidated early-warning claims, respecting data limitations by computing intra-month statistical variance (MAD / robust z-scores) while noting that multi-year seasonal baselines require 5+ years of data.

---

## Links & Deliverables
- **GitHub Repository:** Complete source code, migrations, tests, and documentation.
- **Data Provenance:** NASA FIRMS (MODIS Collection 6.1, VIIRS Collection 2).
- **Interactive UI:** React + Leaflet + Recharts web dashboard.
