# FireHorizon — NASA FIRMS Comprehensive Data Audit Report

**Audit Date:** 2026-11-14  
**Project:** FireHorizon — NASA Space Apps Challenge 2026  
**Challenge:** Harmonization of MODIS and VIIRS Hot Spots  
**Area Covered:** India (with pilot state administrative filter: Maharashtra)  
**Observation Period:** 2025-03-01 to 2025-03-31 (31 Calendar Days, UTC)

---

## 1. Verified Archives & Input Accounting

All four original NASA FIRMS ZIP archives were ingested, standardized, and validated with zero data loss:

| FIRMS Archive Filename | Sensor Family | Satellites | Product Label | Nominal Resolution | Verified Row Count |
|---|---|---|---|---|---|
| `DL_FIRE_M-C61_846907.zip` | **MODIS** | Terra & Aqua | `MODIS_C61` | 1000 m (1.0 km²) | **30,644** |
| `DL_FIRE_SV-C2_846910.zip` | **VIIRS** | Suomi-NPP | `VIIRS_SNPP` | 375 m (0.14 km²) | **212,965** |
| `DL_FIRE_J1V-C2_846908.zip` | **VIIRS** | NOAA-20 (JPSS-1) | `VIIRS_NOAA20` | 375 m (0.14 km²) | **213,338** |
| `DL_FIRE_J2V-C2_846909.zip` | **VIIRS** | NOAA-21 (JPSS-2) | `VIIRS_NOAA21` | 375 m (0.14 km²) | **195,078** |
| **Combined Total** | | | | | **652,025** |

- **Missing Values:** Zero nulls in core coordinate, temporal, or FRP fields across all 652,025 ingested rows.
- **Coordinate Envelopes:**
  - Latitude: 8.0798°N to 34.4941°N (consistent with Indian landmass).
  - Longitude: 68.5089°E to 97.0297°E (consistent with Indian landmass).
- **Temporal Coverage:** 100% complete daily observation presence for all 31 dates in March 2025 across all 4 products.

---

## 2. Provenance & Confidence Encodings Preservation

In strict compliance with NASA remote sensing practices:
1. **MODIS Numeric Probabilities:** Preserved as numeric strings (e.g. `54`, `73`, `100`). Range: 0 to 100%.
2. **VIIRS Categorical Classes:** Preserved as categorical characters (`l` = Low, `n` = Nominal, `h` = High).
3. **No Naive Merging:** The pipeline segregates confidence distributions to prevent misleading statistical averaging across disparate scales.

---

## 3. Geographic Subsetting: Maharashtra Administrative Boundary

- **Boundary Source:** geoBoundaries Open Database (`gbOpen ADM1`) in conjunction with DataMeet India and Election Commission of India.
- **License:** Creative Commons Attribution 2.5 India (CC BY 2.5 IN).
- **Filtering Methodology:** C-accelerated Point-in-Polygon testing (`shapely.contains_xy`) against the authentic MultiPolygon boundary.
- **Maharashtra Detection Count:** **77,534 records** (**11.89%** of national India total).
- **Active 1km Equal-Area Cells in Maharashtra:** **28,450 cells**.

---

## 4. Harmonization & Co-Detection Statistics

- **Spatial Coordinate Standard:** Projected into `EPSG:6933` (World Cylindrical Equal Area) at 1 km × 1 km grid cells.
- **Candidate Co-Detection Matching:** Evaluated across $\le 1000\text{ m}$ spatial distance and $\le 60\text{ min}$ acquisition time offset.
- **India Candidate Co-Detections:** **142,748 pairs**.
- **Maharashtra Candidate Co-Detections:** **11,748 pairs**.
- **Observation-to-Fire Rule:** Every match is labeled as a *candidate co-detection*. Detection count is never represented as physical fire count.

---

## 5. Audit Conclusion

The dataset has undergone automated reconciliation (`scripts/verify_dataset.py`) confirming:
1. `652,025 == 652,025` total record parity.
2. Sum of grid cell detections matches raw observation totals with 100% mathematical fidelity.
3. Audit outputs and sensitivity analysis logs are saved under `data/processed/audit/`.
