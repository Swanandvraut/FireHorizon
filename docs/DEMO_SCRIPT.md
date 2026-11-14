# FireHorizon — Project Demonstration Script

**Event:** NASA Space Apps Challenge 2026 — Kopargaon  
**Challenge:** Harmonization of MODIS and VIIRS Hot Spots  
**Team Members:** Swanand Raut, Swaral Dabhade, Raj Dakle, Vishal Sable

---

## 1. Introduction (0:00 - 0:45)
- **Opening:** Welcome to **FireHorizon: Satellite Harmonization & Integrated Burning Activity Calendar**.
- **The Problem:** NASA operates two premier earth observation instruments for wildfire tracking: MODIS (at 1000m resolution) and VIIRS (at 375m resolution). Because of differing pixel footprints, detection thresholds, and orbital schedules, VIIRS detects roughly 7× more hotspot pixels than MODIS for the same burning area. Environmental managers cannot simply sum these counts without distorting reality.
- **The Solution:** FireHorizon provides an open, mathematically sound pipeline that harmonizes 652,025 real NASA FIRMS observations over India into an intuitive, interactive burning activity calendar.

---

## 2. Walkthrough: The Live Platform (0:45 - 2:30)

### Tab 1: Overview Dashboard
- Show real KPI cards: **652,025 NASA records**, **487,134 active 1km equal-area cells**, and **142,748 candidate co-detections**.
- Toggle between **India (National)** and **Maharashtra (State Pilot)**. Point out that the Maharashtra subset accounts for exactly 77,534 observations (11.89%).
- Show the daily burning trend chart and highlight diurnal breakdown (day vs night passes).

### Tab 2: Interactive Fire Map
- Pan and zoom across India and Maharashtra.
- Point out the official state administrative boundary polygon (from geoBoundaries gbOpen).
- Filter by sensor (MODIS vs VIIRS) and observe how 375m VIIRS reveals finer agricultural burning clusters.
- Click a 1km grid cell to open the inspector popup showing coordinates, detection count, FRP, and mean brightness temperature.

### Tab 3: Burning Activity Calendar (Core Feature)
- Explain the month-at-a-glance heatmap for March 2025.
- Walk through the documented activity intensity tiers: Low, Moderate, Elevated, High, and Extreme.
- Click on the peak burning date (**March 30, 2025**) to display the detailed day inspector with sensor family breakdown and the Experimental Activity Index score.
- Review the weekly rollup table summarizing energy and active cell progression throughout March.

### Tab 4: Sensor Comparison
- Review the quantitative side-by-side comparison table explaining optics, overpass timing, and confidence encodings.
- Show the temporal agreement chart tracking candidate co-detection matches ($\Delta d \le 1\text{km}, \Delta t \le 60\text{min}$).

### Tab 5: Regional Analytics & Open Data Export
- Show the ranked table of top 1 km² hotspot cells across Maharashtra.
- Demonstrate one-click CSV export of derived harmonized daily records.

### Tab 6: Methodology & Scientific Transparency
- Highlight the Experimental Activity Index formula.
- Emphasize our strict adherence to scientific limitations: refusing to make unvalidated early-warning forecast claims without a 5+ year historical baseline.

---

## 3. Conclusion & Takeaway (2:30 - 3:00)
- FireHorizon transforms raw, disparate satellite hot spots into actionable, harmonized fire intelligence.
- Built with React, Leaflet, Python, and Supabase PostgreSQL.
