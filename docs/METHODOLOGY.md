# FireHorizon — Scientific Methodology & Harmonization Framework

**NASA Space Apps Challenge 2026: Harmonization of MODIS and VIIRS Hot Spots**  
**Team Members:** Swanand Raut, Swaral Dabhade, Raj Dakle, Vishal Sable  
**Methodology Version:** `v1.0-provisional-grid-normalized`

---

## 1. Executive Summary

FireHorizon addresses the core scientific challenge of reconciling active fire detections from two fundamentally distinct satellite sensor families: **MODIS** (Moderate Resolution Imaging Spectroradiometer on Terra and Aqua) and **VIIRS** (Visible Infrared Imaging Radiometer Suite on Suomi-NPP, NOAA-20, and NOAA-21).

Raw detection counts from MODIS and VIIRS cannot be naively combined or treated as physical fire counts because of differences in:
1. **Spatial resolution** (~1000m nadir for MODIS vs 375m for VIIRS I-band).
2. **Detection threshold and minimum detectable Fire Radiative Power (FRP)**.
3. **Diurnal sampling timing and orbital overpass schedules**.
4. **Confidence scoring methodologies** (MODIS numeric 0–100 vs VIIRS categorical low/nominal/high).

FireHorizon provides an open, reproducible, and mathematically documented harmonization framework that aggregates observations onto a common equal-area spatial grid, conducts spatial-temporal candidate co-detection matching, and computes a provisional sensor-normalized activity indicator while maintaining complete data provenance.

---

## 2. Sensor Characteristics & Inherent Discrepancies

| Sensor Family | Satellites | Nominal Spatial Resolution | Active Fire Channels | Nominal Equatorial Overpass Times (Local Solar Time) | Confidence Scoring |
|---|---|---|---|---|---|
| **MODIS** (Collection 6.1) | Terra, Aqua | ~1000 m (1.0 km²) | 4 µm (Channel 21/22), 11 µm (Channel 31) | Terra: ~10:30 AM (descending), ~10:30 PM (ascending)<br>Aqua: ~01:30 PM (ascending), ~01:30 AM (descending) | Numeric (0 to 100%) |
| **VIIRS** (Collection 2) | Suomi-NPP, NOAA-20, NOAA-21 | ~375 m (0.14 km²) | 3.74 µm (Channel I4), 11.45 µm (Channel I5) | S-NPP: ~01:30 PM (ascending), ~01:30 AM (descending)<br>NOAA-20: ~01:30 PM (displaced ~50 min)<br>NOAA-21: ~01:30 PM (displaced orbit) | Categorical classes: `l` (low), `n` (nominal), `h` (high) |

### Key Physical Considerations:
- **Footprint Area Disparity:** A single MODIS 1 km pixel covers roughly **7.1 times** the surface area of a 375 m VIIRS pixel. Consequently, small, cooler, or fragmented agricultural fires that fall below the MODIS sub-pixel thermal threshold are frequently detected by VIIRS.
- **Count Non-Equivalence:** In areas of dispersed biomass burning (e.g., agricultural residue clearance in Maharashtra), VIIRS typically records 5× to 10× more hotspot points than MODIS for the same burning event. Calling these "more fires" is scientifically inaccurate; they are **more granular detections**.

---

## 3. Spatial Grid & Projection (EPSG:6933)

To facilitate cross-sensor comparisons without distorting surface area across India's latitudes (8°N to 35°N), all coordinates are projected onto a **World Cylindrical Equal Area projection (EPSG:6933)**.

- **Analytical Cell Size:** 1 km × 1 km equal-area bins (`GRID_1000M_R{row}_C{col}`).
- **Cell Center:** Reprojected back to WGS 84 (`EPSG:4326`) for map rendering and spatial querying.
- **Sensitivity Testing:** The pipeline supports multi-resolution sensitivity analysis at 500 m, 1 km, and 2 km.

---

## 4. Spatial-Temporal Candidate Co-Detection Matching

Observations from MODIS and VIIRS on the same UTC date are compared using a spatial $k$-d tree:

$$\Delta d = \sqrt{(x_{\text{modis}} - x_{\text{viirs}})^2 + (y_{\text{modis}} - y_{\text{viirs}})^2} \le D_{\text{threshold}}$$

$$\Delta t = |t_{\text{modis}} - t_{\text{viirs}}| \le T_{\text{threshold}}$$

- Default distance threshold: $D_{\text{threshold}} = 1000\text{ m}$
- Default time threshold: $T_{\text{threshold}} = 60\text{ min}$

### Scientific Classification Rule:
Pairs meeting both criteria are designated as **candidate co-detections**, representing independent sensor confirmations of active thermal anomalies. They are **never** declared as proven single physical fires, and **unmatched observations are never discarded**.

---

## 5. Experimental Activity Index (EAI) Formula

FireHorizon calculates a transparent, dimensionally consistent daily activity score:

$$\text{EAI} = \min\left(100, \frac{\left( w_M \cdot A_{M} + w_V \cdot A_{V} \cdot \kappa \right) \cdot \left(1 + \log_{10}\left(1 + \frac{\text{FRP}_{\text{total}}}{\text{FRP}_{\text{ref}}}\right)\right)}{\Sigma_{\text{norm}}}\right)$$

Where:
- $A_M$: Active grid cell area detected by MODIS ($\text{km}^2$)
- $A_V$: Active grid cell area detected by VIIRS ($\text{km}^2$)
- $w_M = 1.0$, $w_V = 0.6$: Weighting factors accounting for sensor overpass redundancy
- $\kappa = 2.5$: Resolution scaling compensation factor
- $\text{FRP}_{\text{total}}$: Combined fire radiative power sum in Megawatts (MW)
- $\text{FRP}_{\text{ref}} = 100\text{ MW}$: Reference normalization energy constant
- $\Sigma_{\text{norm}} = 500.0$: Scaling denominator normalizing daily activity onto a 0–100 scale

---

## 6. Burning Activity Calendar Tiers

| Activity Tier | EAI Score Range | FRP Range (MW) | Interpretation |
|---|---|---|---|
| **Low Activity** | $0 \le \text{EAI} < 20$ | $< 250$ | Baseline rural thermal emissions or isolated small burns |
| **Moderate Activity** | $20 \le \text{EAI} < 45$ | $250 - 1,000$ | Moderate localized biomass or crop residue burning |
| **Elevated Activity** | $45 \le \text{EAI} < 70$ | $1,000 - 3,500$ | Widespread regional burning or medium forest fire activity |
| **High Activity** | $70 \le \text{EAI} < 85$ | $3,500 - 7,000$ | Intense, clustered fire activity confirmed across multiple passes |
| **Extreme Activity** | $\text{EAI} \ge 85$ | $> 7,000$ | Peak burning episode with massive thermal radiation |

---

## 7. Climatological Baseline & Anomaly Detection Policy

> [!WARNING]
> **Data Scope Limitation:** The supplied dataset covers strictly **March 1–31, 2025**. A scientifically defensible climatological anomaly calculation requires a minimum 5-to-10-year historical baseline (e.g., 2015–2024 reference window).
>
> In accordance with NASA Space Apps integrity rules, FireHorizon:
> 1. Computes **intra-month statistical variance** (robust z-score and Median Absolute Deviation relative to the March 2025 sample only).
> 2. Flags multi-year climatological anomaly status as **"Historical baseline insufficient"**.
> 3. Does not claim operational early-warning forecast capability.
