# FireHorizon — Scientific Assumptions, Uncertainties & Known Limitations

**NASA Space Apps Challenge 2026: Harmonization of MODIS and VIIRS Hot Spots**

Scientific rigor and transparency require explicitly articulating what the data and algorithms can and cannot establish. FireHorizon adheres strictly to these principles.

---

## 1. Detections vs Physical Fire Count Discrepancy

- **Fundamental Distinction:** A satellite thermal anomaly (hotspot) detection signifies that a sub-pixel thermal radiator exceeded the sensor's background threshold at the moment of satellite overpass.
- **Multiple Pixels per Fire:** An intense, large wildfire (e.g., in the Western Ghats) can saturate multiple contiguous 375 m VIIRS pixels or produce blooming across adjacent scan lines.
- **Multiple Satellites per Day:** With Aqua, Terra, Suomi-NPP, NOAA-20, and NOAA-21 orbiting Earth, the same physical fire may be detected 4 to 8 times within a 24-hour cycle.
- **Harmonization Rule:** FireHorizon **never labels raw detection counts as physical fire counts**. All counts are explicitly designated as *satellite observation detections*.

---

## 2. Incompatible Confidence Encodings

- **MODIS Collection 6.1:** Uses an empirical detection probability ranging from 0% to 100%, derived from background temperature variance and potential false-alarm rejection tests.
- **VIIRS Collection 2 (375m):** Assigns categorical classifications:
  - `l` (Low confidence): Often associated with sun glint, saturated water edges, or marginal signal-to-noise ratio.
  - `n` (Nominal confidence): Standard detection during daytime or nighttime.
  - `h` (High confidence): Saturated fire pixel with strong multi-spectral thermal signature.
- **Methodological Stance:** FireHorizon preserves `confidence_raw` and `confidence_encoding` separately. Naive conversions (such as assigning `l=30%`, `n=70%`, `h=95%`) are avoided because they lack published empirical calibration.

---

## 3. Climatological Baseline & Early Warning Bounds

- **Dataset Limitation:** The provided NASA FIRMS archive is bounded between **March 1, 2025 and March 31, 2025**.
- **Seasonal Inferences Prohibited:** March represents late winter/early pre-monsoon dry season in India, during which agricultural post-harvest burning and dry deciduous leaf-litter fires peak. One single month cannot establish whether burning activity in 2025 is "abnormally high" compared to long-term averages.
- **Early Warning Claim Restraint:** Forecasting fire danger or issuing fire alerts without multi-year climatological baselines and real-time meteorological inputs (e.g., relative humidity, wind velocity, vegetation fuel dryness) is scientifically invalid. FireHorizon restricts anomaly metrics to intra-sample variance (Median Absolute Deviation) and explicitly labels climatological baseline as **"Insufficient (requires 5+ years)"**.

---

## 4. Atmospheric & Cloud Obscuration

- Satellite infrared sensors cannot penetrate thick meteorological cloud cover or heavy pyrocumulus smoke columns.
- An apparent drop in detection counts on a given date may result from monsoon cloud cover or thick overcast skies rather than actual fire extinguishment.
- FireHorizon displays missing satellite passes separately from confirmed zero-fire scans.

---

## 5. Candidate Co-Detection Matching Uncertainty

- Cross-sensor matching between MODIS and VIIRS uses an analytical threshold of $\le 1000\text{ m}$ spatial separation and $\le 60\text{ minutes}$ acquisition time offset.
- Satellites pass over at slightly different viewing zenith angles and orbital geometries. A match is therefore designated strictly as a **candidate co-detection**, indicating high spatial-temporal concurrence, rather than ground-truth proof of an identical flaming front.
