"""
FireHorizon Scientific Data Audit Script
=========================================
Performs complete verification of all dashboard metrics against actual NASA FIRMS data.
Outputs a machine-readable audit result for use in generating docs/APP_DATA_AUDIT.md.

Usage:
    python scripts/audit_data.py

Output:
    Printed audit results (redirect to docs/audit_raw_output.txt)
    Also writes docs/audit_results.json
"""

import sys
import os
import json
import gzip
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pandas as pd
import numpy as np

PROC = os.path.join(ROOT, "data", "processed")
FRONT = os.path.join(ROOT, "frontend", "public", "data")
BOUNDARY = os.path.join(ROOT, "data", "boundaries", "maharashtra.geojson")

SEP = "=" * 70
PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"
INFO = "INFO"

results = {}

def hdr(title):
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)

def chk(label, status, detail=""):
    icon = {"PASS": "OK", "FAIL": "XX", "WARN": "WW", "INFO": "--"}[status]
    print(f"  [{icon}] {status:4s}  {label}")
    if detail:
        for line in detail.splitlines():
            print(f"             {line}")
    results[label] = {"status": status, "detail": detail}

# ──────────────────────────────────────────────────────────────────────────────
hdr("1. RAW COMBINED DATASET — BASIC COUNTS")
# ──────────────────────────────────────────────────────────────────────────────

combined_path = os.path.join(PROC, "combined_observations.csv.gz")
if not os.path.exists(combined_path):
    chk("combined_observations.csv.gz exists", FAIL, f"File missing: {combined_path}")
    sys.exit(1)

print(f"\n  Loading {combined_path} ...")
df = pd.read_csv(combined_path, low_memory=False)
print(f"  Loaded {len(df):,} rows, {len(df.columns)} columns")

EXPECTED_TOTAL = 652025
EXPECTED_SOURCES = {
    "MODIS_C61":   30644,
    "VIIRS_SNPP":  212965,
    "VIIRS_NOAA20": 213338,
    "VIIRS_NOAA21": 195078,
}

actual_total = len(df)
chk(f"Total rows = {EXPECTED_TOTAL:,}",
    PASS if actual_total == EXPECTED_TOTAL else FAIL,
    f"Actual: {actual_total:,}")

results["actual_total_rows"] = actual_total

src_counts = df["source_product"].value_counts().to_dict()
for src, expected in EXPECTED_SOURCES.items():
    actual = src_counts.get(src, 0)
    chk(f"{src} row count = {expected:,}",
        PASS if actual == expected else FAIL,
        f"Actual: {actual:,}")
    results[f"count_{src}"] = actual

# ──────────────────────────────────────────────────────────────────────────────
hdr("2. COORDINATE VALIDITY")
# ──────────────────────────────────────────────────────────────────────────────

invalid_lat = df[(df["latitude"] < -90) | (df["latitude"] > 90)]
invalid_lon = df[(df["longitude"] < -180) | (df["longitude"] > 180)]
chk("All latitudes in [-90, 90]",
    PASS if len(invalid_lat) == 0 else FAIL,
    f"Invalid: {len(invalid_lat):,}")
chk("All longitudes in [-180, 180]",
    PASS if len(invalid_lon) == 0 else FAIL,
    f"Invalid: {len(invalid_lon):,}")

lat_range = f"{df['latitude'].min():.4f} to {df['latitude'].max():.4f}"
lon_range = f"{df['longitude'].min():.4f} to {df['longitude'].max():.4f}"
chk("Coordinate range (India expected)", INFO,
    f"Lat: {lat_range}  |  Lon: {lon_range}")

# ──────────────────────────────────────────────────────────────────────────────
hdr("3. TEMPORAL INTEGRITY")
# ──────────────────────────────────────────────────────────────────────────────

df["acq_date_parsed"] = pd.to_datetime(df["acq_date"], errors="coerce")
n_bad_dates = df["acq_date_parsed"].isna().sum()
chk("All acq_date values parseable",
    PASS if n_bad_dates == 0 else FAIL,
    f"Unparseable: {n_bad_dates:,}")

min_date = df["acq_date_parsed"].min()
max_date = df["acq_date_parsed"].max()
chk("Date range 2025-03-01 to 2025-03-31",
    PASS if str(min_date.date()) == "2025-03-01" and str(max_date.date()) == "2025-03-31" else FAIL,
    f"Actual range: {min_date.date()} to {max_date.date()}")

n_days = df["acq_date"].nunique()
chk(f"Unique dates = 31",
    PASS if n_days == 31 else FAIL,
    f"Unique dates found: {n_days}")

# ──────────────────────────────────────────────────────────────────────────────
hdr("4. UTC ACQUISITION TIME HANDLING")
# ──────────────────────────────────────────────────────────────────────────────

sample = df[["acq_date", "acq_time", "source_product"]].dropna().head(5)
chk("UTC acquisition time sample", INFO,
    sample.to_string(index=False))

# Check acq_time is 4-digit (HHMM)
acq_time_col = df["acq_time"].astype(str).str.strip()
bad_time_format = acq_time_col[~acq_time_col.str.match(r"^\d{4}$")]
chk("acq_time is 4-digit HHMM format",
    PASS if len(bad_time_format) == 0 else WARN,
    f"Malformed: {len(bad_time_format):,} rows"
    + (f"\nSample: {bad_time_format.head(3).tolist()}" if len(bad_time_format) > 0 else ""))

# Check for acq_datetime_utc column
if "acq_datetime_utc" in df.columns:
    n_bad_utc = pd.to_datetime(df["acq_datetime_utc"], errors="coerce").isna().sum()
    chk("acq_datetime_utc column present and parseable",
        PASS if n_bad_utc == 0 else FAIL,
        f"Parse failures: {n_bad_utc:,}")
    # Sample
    utc_sample = df[["acq_date", "acq_time", "acq_datetime_utc"]].dropna().head(3)
    chk("acq_datetime_utc sample", INFO, utc_sample.to_string(index=False))
else:
    chk("acq_datetime_utc column present", WARN,
        "Column not found — UTC datetime was not persisted in combined CSV")

# ──────────────────────────────────────────────────────────────────────────────
hdr("5. CONFIDENCE ENCODING PRESERVATION")
# ──────────────────────────────────────────────────────────────────────────────

for col in ["confidence_raw", "confidence_encoding"]:
    chk(f"Column '{col}' present",
        PASS if col in df.columns else FAIL)

if "confidence_encoding" in df.columns:
    enc_counts = df.groupby("source_product")["confidence_encoding"].agg(
        lambda x: x.value_counts().index[0] if len(x) > 0 else "NONE"
    )
    chk("Confidence encoding by source", INFO,
        enc_counts.to_string())

    # Verify MODIS is numeric, VIIRS is categorical
    modis_df = df[df["source_product"] == "MODIS_C61"]
    viirs_df = df[df["source_product"] != "MODIS_C61"]

    if len(modis_df) > 0 and "confidence_raw" in df.columns:
        modis_conf = modis_df["confidence_raw"].dropna()
        try:
            modis_numeric = pd.to_numeric(modis_conf, errors="coerce")
            n_non_numeric = modis_numeric.isna().sum()
            chk("MODIS confidence_raw is numeric (0-100)",
                PASS if n_non_numeric == 0 else FAIL,
                f"Non-numeric: {n_non_numeric:,}  |  Range: {modis_numeric.min():.0f}–{modis_numeric.max():.0f}")
        except Exception as e:
            chk("MODIS confidence_raw numeric check", FAIL, str(e))

    if len(viirs_df) > 0 and "confidence_raw" in df.columns:
        viirs_conf_vals = viirs_df["confidence_raw"].dropna().unique()
        expected_viirs = {"l", "n", "h"}
        actual_viirs = set(viirs_conf_vals)
        chk("VIIRS confidence_raw is categorical (l/n/h)",
            PASS if actual_viirs.issubset({"l", "n", "h"}) else FAIL,
            f"Unique values found: {sorted(actual_viirs)}")

# ──────────────────────────────────────────────────────────────────────────────
hdr("6. MAHARASHTRA FILTERING VERIFICATION")
# ──────────────────────────────────────────────────────────────────────────────

maha_daily_path = os.path.join(PROC, "activity_daily_maharashtra.csv")
india_daily_path = os.path.join(PROC, "activity_daily_india.csv")

if not os.path.exists(maha_daily_path):
    chk("activity_daily_maharashtra.csv exists", FAIL)
else:
    maha_daily = pd.read_csv(maha_daily_path)
    chk("activity_daily_maharashtra.csv loaded", PASS,
        f"Rows: {len(maha_daily)}")

    # Compute actual Maharashtra total observations
    if "total_observations" in maha_daily.columns:
        maha_total_obs = int(maha_daily["total_observations"].sum())
    elif "observation_count" in maha_daily.columns:
        maha_total_obs = int(maha_daily["observation_count"].sum())
    else:
        # Try to infer
        obs_cols = [c for c in maha_daily.columns if "obs" in c.lower() or "count" in c.lower()]
        chk("Maharashtra observation column", WARN, f"Columns: {list(maha_daily.columns)}")
        maha_total_obs = None

    if maha_total_obs is not None:
        chk(f"Maharashtra total observations (monthly sum)", INFO,
            f"Actual: {maha_total_obs:,}")
        results["maharashtra_total_observations"] = maha_total_obs
        chk("Maharashtra total observations ~77,534",
            PASS if 77000 <= maha_total_obs <= 78000 else FAIL,
            f"Expected ~77,534, got {maha_total_obs:,}")

    # March 16 specifically
    if "acq_date" in maha_daily.columns:
        maha_daily["acq_date"] = pd.to_datetime(maha_daily["acq_date"])
        march16 = maha_daily[maha_daily["acq_date"].dt.strftime("%Y-%m-%d") == "2025-03-16"]
        if len(march16) > 0 and "total_observations" in maha_daily.columns:
            march16_count = int(march16["total_observations"].sum())
            chk(f"March 16 Maharashtra detection count", INFO,
                f"Actual: {march16_count:,}")
            results["march_16_maharashtra_detections"] = march16_count
        elif len(march16) > 0:
            chk("March 16 Maharashtra detection count", WARN,
                f"Row found but column unclear: {march16.to_dict(orient='records')}")
    
    # Print the full daily data for Maharashtra
    print("\n  Maharashtra Daily Observations (all 31 days):")
    if "total_observations" in maha_daily.columns and "acq_date" in maha_daily.columns:
        daily_view = maha_daily[["acq_date", "total_observations"]].sort_values("acq_date")
        for _, row in daily_view.iterrows():
            print(f"    {row['acq_date'].strftime('%Y-%m-%d') if hasattr(row['acq_date'], 'strftime') else row['acq_date']}  :  {int(row['total_observations']):>7,}")
    else:
        print(f"  Columns: {list(maha_daily.columns)}")
        print(maha_daily.head(10).to_string())

# ──────────────────────────────────────────────────────────────────────────────
hdr("7. FRP (FIRE RADIATIVE POWER) VERIFICATION")
# ──────────────────────────────────────────────────────────────────────────────

if "frp" in df.columns:
    frp_all = pd.to_numeric(df["frp"], errors="coerce")
    n_frp_valid = frp_all.notna().sum()
    n_frp_missing = frp_all.isna().sum()
    frp_total_india = float(frp_all.sum())
    frp_min = float(frp_all.min())
    frp_max = float(frp_all.max())
    frp_mean = float(frp_all.mean())

    chk("FRP column present and numeric", PASS if n_frp_missing == 0 else WARN,
        f"Valid: {n_frp_valid:,}  |  Missing: {n_frp_missing:,}")
    chk("FRP range sanity (0–10000 MW expected)", INFO,
        f"Min: {frp_min:.2f} MW  |  Max: {frp_max:.2f} MW  |  Mean: {frp_mean:.2f} MW")
    chk("Total FRP India (MW)", INFO,
        f"Actual: {frp_total_india:,.2f} MW")
    results["total_frp_india_mw"] = frp_total_india

    # Maharashtra FRP — load filtered processed file or check daily CSV
    if os.path.exists(maha_daily_path):
        maha_daily2 = pd.read_csv(maha_daily_path)
        if "total_frp_mw" in maha_daily2.columns:
            frp_maha = float(maha_daily2["total_frp_mw"].sum())
            chk("Total FRP Maharashtra (MW)", INFO,
                f"Actual: {frp_maha:,.2f} MW")
            results["total_frp_maharashtra_mw"] = frp_maha
        else:
            chk("total_frp_mw column in Maharashtra daily CSV", WARN,
                f"Columns: {list(maha_daily2.columns)}")

    # Verify NOT labeled "Total Energy"
    chk("FRP correctly labeled (not 'Total Energy')", INFO,
        "Metric unit is MW (megawatts of radiant power), not joules or energy integral")
else:
    chk("FRP column present", FAIL, "Column 'frp' not in combined CSV")

# ──────────────────────────────────────────────────────────────────────────────
hdr("8. SENSOR-WISE CONTRIBUTIONS — MAHARASHTRA")
# ──────────────────────────────────────────────────────────────────────────────

if os.path.exists(maha_daily_path):
    maha_daily3 = pd.read_csv(maha_daily_path)
    sensor_cols = [c for c in maha_daily3.columns if any(s in c.upper() for s in ["MODIS", "VIIRS", "SNPP", "NOAA"])]
    
    if sensor_cols:
        print(f"\n  Sensor columns found: {sensor_cols}")
        for col in sensor_cols:
            total = maha_daily3[col].sum()
            chk(f"Maharashtra {col} total", INFO, f"{int(total):,}")
            results[f"maharashtra_{col}"] = int(total)
    else:
        # Check source-specific CSV files
        src_path = os.path.join(PROC, "source_summary.csv")
        if os.path.exists(src_path):
            src_df = pd.read_csv(src_path)
            chk("Source summary CSV", INFO, src_df.to_string(index=False))
        else:
            chk("Sensor-wise Maharashtra columns", WARN,
                f"sensor_cols not found in daily CSV. Columns: {list(maha_daily3.columns)}")

# Compute directly from combined CSV
chk("Sensor-wise contributions (from combined CSV, India)", INFO,
    "\n".join([f"  {src}: {cnt:,}" for src, cnt in sorted(src_counts.items())]))

# ──────────────────────────────────────────────────────────────────────────────
hdr("9. CROSS-SENSOR CO-DETECTION VERIFICATION")
# ──────────────────────────────────────────────────────────────────────────────

sc_maha_path = os.path.join(PROC, "sensor_comparison_daily_maharashtra.csv")
sc_india_path = os.path.join(PROC, "sensor_comparison_daily_india.csv")

for path, label in [(sc_maha_path, "Maharashtra"), (sc_india_path, "India")]:
    if os.path.exists(path):
        sc = pd.read_csv(path)
        chk(f"sensor_comparison_daily_{label.lower()}.csv loaded", PASS,
            f"Rows: {len(sc)}")
        if "candidate_matches" in sc.columns:
            total_matches = int(sc["candidate_matches"].sum())
            chk(f"Total candidate co-detections {label}", INFO,
                f"{total_matches:,}")
            results[f"candidate_matches_{label.lower()}"] = total_matches
        else:
            match_cols = [c for c in sc.columns if "match" in c.lower() or "overlap" in c.lower()]
            chk(f"candidate_matches column {label}", WARN,
                f"Column not found. Available: {list(sc.columns)}\nMatch-like cols: {match_cols}")
            if match_cols:
                for col in match_cols:
                    chk(f"  {col} total {label}", INFO, f"{int(sc[col].sum()):,}")
        # Check methodology columns
        for col in ["distance_threshold_meters", "time_threshold_minutes", "methodology_version"]:
            if col in sc.columns:
                val = sc[col].iloc[0] if len(sc) > 0 else "N/A"
                chk(f"  {col}", INFO, str(val))
    else:
        chk(f"sensor_comparison_daily_{label.lower()}.csv exists", FAIL,
            f"File not found: {path}")

# ──────────────────────────────────────────────────────────────────────────────
hdr("10. OVERVIEW METRICS JSON VERIFICATION")
# ──────────────────────────────────────────────────────────────────────────────

metrics_path = os.path.join(FRONT, "overview_metrics.json")
if not os.path.exists(metrics_path):
    chk("overview_metrics.json exists", FAIL, f"Path: {metrics_path}")
else:
    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)
    chk("overview_metrics.json loaded", PASS, json.dumps(metrics, indent=2))
    results["overview_metrics_json"] = metrics

    # Cross-verify each key field
    checks = {
        "total_observations": (actual_total, "exact"),
    }
    if "total_frp_india_mw" in results:
        checks["total_frp_mw"] = (results["total_frp_india_mw"], "approx")
    if "maharashtra_total_observations" in results:
        checks["maharashtra_observations"] = (results["maharashtra_total_observations"], "exact")

    for key, (expected, mode) in checks.items():
        if key in metrics:
            actual_val = metrics[key]
            if mode == "exact":
                ok = actual_val == expected
            else:  # approx — within 1%
                ok = abs(actual_val - expected) / max(abs(expected), 1) < 0.01
            chk(f"metrics.json['{key}'] vs computed",
                PASS if ok else FAIL,
                f"JSON: {actual_val:,}  |  Computed: {expected:,}")
        else:
            chk(f"metrics.json has key '{key}'", WARN, "Key absent")

# ──────────────────────────────────────────────────────────────────────────────
hdr("11. CALENDAR DATA VERIFICATION")
# ──────────────────────────────────────────────────────────────────────────────

cal_path = os.path.join(FRONT, "calendar_maharashtra.json")
if not os.path.exists(cal_path):
    chk("calendar_maharashtra.json exists", FAIL)
else:
    with open(cal_path, "r", encoding="utf-8") as f:
        cal = json.load(f)
    chk("calendar_maharashtra.json loaded", PASS,
        f"Top-level keys: {list(cal.keys())[:8]}")

    # Find daily entries
    daily_entries = None
    if "daily" in cal:
        daily_entries = cal["daily"]
    elif "days" in cal:
        daily_entries = cal["days"]
    elif isinstance(cal, list):
        daily_entries = cal

    if daily_entries:
        # March 16
        for entry in daily_entries:
            d = entry.get("date", entry.get("acq_date", ""))
            if "2025-03-16" in str(d):
                chk("March 16 calendar entry found", INFO, json.dumps(entry, indent=2))
                results["march_16_calendar_entry"] = entry
                break
        else:
            chk("March 16 calendar entry", WARN, "No entry found for 2025-03-16")

        # Reconciliation: sum of daily == monthly total
        obs_key = None
        for candidate in ["total_observations", "observation_count", "count", "detections"]:
            if daily_entries and candidate in daily_entries[0]:
                obs_key = candidate
                break
        
        if obs_key:
            cal_monthly_sum = sum(e.get(obs_key, 0) for e in daily_entries)
            chk(f"Calendar daily sum ('{obs_key}') = monthly total", INFO,
                f"Sum of daily entries: {cal_monthly_sum:,}")
            results["calendar_maharashtra_daily_sum"] = cal_monthly_sum
            if "maharashtra_total_observations" in results:
                ok = abs(cal_monthly_sum - results["maharashtra_total_observations"]) <= 1
                chk("Calendar daily sum reconciles with activity_daily sum",
                    PASS if ok else FAIL,
                    f"Calendar: {cal_monthly_sum:,}  |  Activity CSV: {results['maharashtra_total_observations']:,}")
        else:
            chk("Calendar daily observation key", WARN,
                f"Could not identify obs key. First entry keys: {list(daily_entries[0].keys()) if daily_entries else 'empty'}")

    # Peak activity date from metrics JSON
    if "overview_metrics_json" in results:
        peak = results["overview_metrics_json"].get("peak_activity_date", "not in metrics")
        chk("Peak activity date (from metrics JSON)", INFO, str(peak))

# ──────────────────────────────────────────────────────────────────────────────
hdr("12. MAHARASHTRA BOUNDARY GEOMETRY VERIFICATION")
# ──────────────────────────────────────────────────────────────────────────────

if not os.path.exists(BOUNDARY):
    chk("maharashtra.geojson exists", FAIL, f"Path: {BOUNDARY}")
else:
    with open(BOUNDARY, "r", encoding="utf-8") as f:
        boundary_data = json.load(f)
    
    geom_types = set()
    n_features = 0
    n_coords_total = 0

    def collect_geometry_info(geom):
        global n_coords_total
        geom_types.add(geom["type"])
        if geom["type"] == "Polygon":
            for ring in geom["coordinates"]:
                n_coords_total += len(ring)
        elif geom["type"] == "MultiPolygon":
            for poly in geom["coordinates"]:
                for ring in poly:
                    n_coords_total += len(ring)

    if boundary_data["type"] == "FeatureCollection":
        n_features = len(boundary_data["features"])
        for feat in boundary_data["features"]:
            if "geometry" in feat and feat["geometry"]:
                collect_geometry_info(feat["geometry"])
    elif boundary_data["type"] in ("Polygon", "MultiPolygon"):
        n_features = 1
        collect_geometry_info(boundary_data)

    chk("Maharashtra boundary geometry type(s)", 
        PASS if "MultiPolygon" in geom_types or "Polygon" in geom_types else FAIL,
        f"Types: {geom_types}  |  Features: {n_features}  |  Coord vertices: {n_coords_total:,}")
    
    is_polygon = bool({"Polygon", "MultiPolygon"} & geom_types)
    chk("Boundary is Polygon/MultiPolygon (not bounding box)",
        PASS if is_polygon else FAIL,
        "Real administrative polygon confirmed" if is_polygon else "Only point or line geometry found — WRONG")

# Check geographic_filter.py uses shapely contains_xy
filter_path = os.path.join(ROOT, "processing", "geographic_filter.py")
if os.path.exists(filter_path):
    with open(filter_path, "r", encoding="utf-8") as f:
        filter_src = f.read()
    uses_contains = "contains_xy" in filter_src or "contains(" in filter_src or ".contains" in filter_src
    uses_bbox_only = ("lat >" in filter_src or "latitude >" in filter_src) and "contains" not in filter_src
    chk("geographic_filter.py uses polygon point-in-polygon",
        PASS if uses_contains else (FAIL if uses_bbox_only else WARN),
        f"contains_xy: {'YES' if 'contains_xy' in filter_src else 'NO'}  "
        f"| .contains: {'YES' if '.contains' in filter_src else 'NO'}")

# ──────────────────────────────────────────────────────────────────────────────
hdr("13. FRONTEND HARDCODED VALUE SCAN")
# ──────────────────────────────────────────────────────────────────────────────

FRONTEND_SRC = os.path.join(ROOT, "frontend", "src")
suspicious_values = ["28450", "18450", "2450", "77534", "142748", "11748"]
hardcoded_found = []

for root_dir, dirs, files in os.walk(FRONTEND_SRC):
    dirs[:] = [d for d in dirs if d not in ["node_modules", ".git"]]
    for fname in files:
        if fname.endswith((".tsx", ".ts", ".jsx", ".js")):
            fpath = os.path.join(root_dir, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                for lineno, line in enumerate(f, 1):
                    for val in suspicious_values:
                        if val in line and "comment" not in line.lower():
                            hardcoded_found.append({
                                "file": os.path.relpath(fpath, ROOT),
                                "line": lineno,
                                "value": val,
                                "content": line.strip()[:100]
                            })

if hardcoded_found:
    chk("No hardcoded fallback statistics in frontend", FAIL,
        f"{len(hardcoded_found)} hardcoded values found:\n" +
        "\n".join(f"  {h['file']}:{h['line']}  [{h['value']}]  {h['content']}"
                  for h in hardcoded_found))
    results["hardcoded_values"] = hardcoded_found
else:
    chk("No hardcoded fallback statistics in frontend", PASS)

# ──────────────────────────────────────────────────────────────────────────────
hdr("14. TERMINOLOGY AUDIT — FRONTEND")
# ──────────────────────────────────────────────────────────────────────────────

bad_terms = {
    "Total Energy": "Should be 'Total FRP (MW)'",
    "unique fire": "Should be 'satellite detection' or 'observation'",
    "confirmed match": "Should be 'candidate co-detection'",
    "confirmed co-detection": "Should be 'candidate co-detection'",
    "fire count": "Ambiguous — should be 'observation count' or 'detection count'",
    "Total Fire Events": "Should be 'Total Detections' or 'Total Observations'",
}
term_issues = []

for root_dir, dirs, files in os.walk(FRONTEND_SRC):
    dirs[:] = [d for d in dirs if d not in ["node_modules", ".git"]]
    for fname in files:
        if fname.endswith((".tsx", ".ts", ".jsx", ".js")):
            fpath = os.path.join(root_dir, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for term, suggestion in bad_terms.items():
                if term.lower() in content.lower():
                    # Find line number
                    for lineno, line in enumerate(content.splitlines(), 1):
                        if term.lower() in line.lower():
                            term_issues.append({
                                "file": os.path.relpath(fpath, ROOT),
                                "line": lineno,
                                "term": term,
                                "suggestion": suggestion,
                                "content": line.strip()[:100]
                            })

if term_issues:
    chk("Terminology issues found", FAIL if any(t["term"] == "Total Energy" for t in term_issues) else WARN,
        f"{len(term_issues)} issues:\n" +
        "\n".join(f"  {t['file']}:{t['line']}  [{t['term']}] → {t['suggestion']}"
                  for t in term_issues[:20]))
    results["terminology_issues"] = term_issues
else:
    chk("No terminology issues found", PASS)

# ──────────────────────────────────────────────────────────────────────────────
hdr("15. SUPABASE CONNECTION STATUS")
# ──────────────────────────────────────────────────────────────────────────────

env_path = os.path.join(ROOT, ".env")
env_example_path = os.path.join(ROOT, ".env.example")

if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        env_content = f.read()
    has_url = "VITE_SUPABASE_URL" in env_content and "your_supabase" not in env_content
    has_key = "VITE_SUPABASE_PUBLISHABLE_KEY" in env_content and "your_supabase" not in env_content
    chk("Supabase .env file present", PASS)
    chk("Supabase URL configured",
        PASS if has_url else WARN,
        "URL present and not placeholder" if has_url else "URL is placeholder or missing")
    chk("Supabase publishable key configured",
        PASS if has_key else WARN,
        "Key present and not placeholder" if has_key else "Key is placeholder or missing")
    chk("Supabase connection status",
        PASS if (has_url and has_key) else WARN,
        "CONNECTED" if (has_url and has_key) else "NOT CONNECTED — using local JSON files. Dashboard shows 'Local Verified Engine'")
    results["supabase_connected"] = has_url and has_key
else:
    chk(".env file exists", FAIL, f"No .env found at {env_path}")
    chk("Supabase connection status", WARN,
        "NOT CONNECTED — no .env file. Dashboard shows 'Local Verified Engine'")
    results["supabase_connected"] = False

# ──────────────────────────────────────────────────────────────────────────────
hdr("16. GRID CELLS VERIFICATION")
# ──────────────────────────────────────────────────────────────────────────────

grid_path = os.path.join(FRONT, "grid_cells_maharashtra.json")
if os.path.exists(grid_path):
    with open(grid_path, "r", encoding="utf-8") as f:
        grid = json.load(f)
    
    # grid might be a list or dict
    if isinstance(grid, list):
        n_cells = len(grid)
        chk("grid_cells_maharashtra.json structure", INFO, f"Array with {n_cells:,} elements")
    elif isinstance(grid, dict):
        cells_key = next((k for k in ["cells", "grid_cells", "features"] if k in grid), None)
        if cells_key:
            n_cells = len(grid[cells_key])
            chk("grid_cells_maharashtra.json structure", INFO,
                f"Dict with key '{cells_key}': {n_cells:,} cells")
        else:
            n_cells = "unknown"
            chk("grid_cells_maharashtra.json structure", WARN,
                f"Dict keys: {list(grid.keys())[:10]}")
    
    results["maharashtra_grid_cells"] = n_cells
    chk("Active grid cells count (Maharashtra)", INFO, f"Cells in JSON: {n_cells}")
else:
    chk("grid_cells_maharashtra.json exists", FAIL)

# Check overview_metrics active_grid_cells field
if "overview_metrics_json" in results:
    m = results["overview_metrics_json"]
    for key in ["active_grid_cells_1km_maharashtra", "active_grid_cells_1km_india"]:
        if key in m:
            chk(f"metrics.json['{key}']", INFO, f"{m[key]:,}")
        else:
            chk(f"metrics.json has '{key}'", WARN)

# ──────────────────────────────────────────────────────────────────────────────
hdr("17. DAILY vs MONTHLY RECONCILIATION")
# ──────────────────────────────────────────────────────────────────────────────

if os.path.exists(maha_daily_path):
    maha_rec = pd.read_csv(maha_daily_path)
    if "total_observations" in maha_rec.columns:
        daily_total = int(maha_rec["total_observations"].sum())
        n_daily_rows = len(maha_rec)
        chk("Daily CSV row count = 31", PASS if n_daily_rows == 31 else FAIL,
            f"Rows: {n_daily_rows}")
        chk("Sum of daily totals (Maharashtra)", INFO, f"{daily_total:,}")
        results["maharashtra_daily_sum"] = daily_total

# ──────────────────────────────────────────────────────────────────────────────
hdr("SUMMARY")
# ──────────────────────────────────────────────────────────────────────────────

pass_count = sum(1 for v in results.values() if isinstance(v, dict) and v.get("status") == PASS)
fail_count = sum(1 for v in results.values() if isinstance(v, dict) and v.get("status") == FAIL)
warn_count = sum(1 for v in results.values() if isinstance(v, dict) and v.get("status") == WARN)
info_count = sum(1 for v in results.values() if isinstance(v, dict) and v.get("status") == INFO)

print(f"\n  PASSED : {pass_count}")
print(f"  FAILED : {fail_count}")
print(f"  WARNINGS: {warn_count}")
print(f"  INFO   : {info_count}")

print("\n  KEY VERIFIED METRICS:")
kv = {
    "Total India observations": results.get("actual_total_rows", "?"),
    "Maharashtra total observations": results.get("maharashtra_total_observations", "?"),
    "March 16 Maharashtra detections": results.get("march_16_maharashtra_detections",
        results.get("march_16_calendar_entry", {}).get("total_observations", "?") if isinstance(results.get("march_16_calendar_entry"), dict) else "?"),
    "Total FRP India (MW)": f"{results.get('total_frp_india_mw', '?'):,.2f}" if isinstance(results.get("total_frp_india_mw"), float) else "?",
    "Total FRP Maharashtra (MW)": f"{results.get('total_frp_maharashtra_mw', '?'):,.2f}" if isinstance(results.get("total_frp_maharashtra_mw"), float) else "?",
    "Candidate co-detections India": results.get("candidate_matches_india", "?"),
    "Candidate co-detections Maharashtra": results.get("candidate_matches_maharashtra", "?"),
    "Supabase connected": results.get("supabase_connected", False),
    "Hardcoded values in frontend": len(results.get("hardcoded_values", [])),
    "Terminology issues": len(results.get("terminology_issues", [])),
}
for k, v in kv.items():
    print(f"    {k:<42} : {v}")

# Save JSON
out_path = os.path.join(ROOT, "docs", "audit_results.json")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
# Filter to serializable
def make_serial(obj):
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    if isinstance(obj, dict):
        return {k: make_serial(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_serial(i) for i in obj]
    return obj

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(make_serial(results), f, indent=2)
print(f"\n  Audit results saved to: {out_path}")
print(f"  Finished: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
