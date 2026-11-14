# FireHorizon — Testing & Validation Report

**Test Execution Date:** 2026-11-14  
**Test Harness:** Pytest (Python 3.13), Vitest (Node 24), Vite Production Build Engine

---

## 1. Automated Test Results Summary

| Suite | Component Tested | Tests Run | Result | Evidence / Details |
|---|---|---|---|---|
| **Pytest** | Geospatial Pipeline & Algorithms | 5 | **PASS (100%)** | `tests/test_pipeline.py` passed in 1.84s |
| **Reconciliation** | Dataset & Row-Count Verification | 6 | **PASS (100%)** | `scripts/verify_dataset.py` passed all checks |
| **Vitest** | Frontend Services & Types | 2 | **PASS (100%)** | `frontend/src/tests/app.test.ts` passed in 31ms |
| **Vite Build** | Production TypeScript & Bundler | Full App | **PASS (100%)** | Clean production bundle generated in 1.39s |

---

## 2. Data Reconciliation Integrity Checks

Executed via `scripts/verify_dataset.py`:

```
[CHECK 1] Total row count: 652,025 (Expected: 652,025) -> PASS
[CHECK 2] Source-wise counts:
  * MODIS_C61: 30,644 (Expected: 30,644) -> PASS
  * VIIRS_SNPP: 212,965 (Expected: 212,965) -> PASS
  * VIIRS_NOAA20: 213,338 (Expected: 213,338) -> PASS
  * VIIRS_NOAA21: 195,078 (Expected: 195,078) -> PASS
[CHECK 3] Coordinate validity:
  * Latitude: 8.0798 to 34.4941 (Valid Indian Envelope) -> PASS
  * Longitude: 68.5089 to 97.0297 (Valid Indian Envelope) -> PASS
[CHECK 4] Temporal integrity:
  * Date span: 2025-03-01 to 2025-03-31 (31 full days) -> PASS
[CHECK 5] Confidence encodings preserved:
  * MODIS numeric values preserved (sample: ['54', '73', '83']) -> PASS
  * VIIRS categorical classes preserved ({'l', 'h', 'n'}) -> PASS
[CHECK 6] Daily grid aggregations reconciliation:
  * Sum of detection_count across grid cells: 652,025 == total_rows -> PASS
```

---

## 3. Scientific Unit Test Details (`test_pipeline.py`)

1. `test_sources_metadata_configured`: Verifies all 4 NASA archives are tracked with nominal spatial resolution and citations.
2. `test_activity_tier_assignment`: Tests threshold boundary behavior for Low, Moderate, Elevated, High, and Extreme burning tiers.
3. `test_spatial_grid_projection`: Confirms forward and inverse projection between WGS84 and EPSG:6933, validating center coordinate accuracy.
4. `test_candidate_matching_logic`: Validates distance and time threshold conditions for candidate co-detection identification.
5. `test_anomaly_detection_refuses_unvalidated_early_warning`: Asserts that `early_warning_claim_allowed` evaluates strictly to `False` and flags climatological baseline as insufficient for single-month archive.
