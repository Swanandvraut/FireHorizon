import pandas as pd, json, os, sys

mdf = pd.read_csv('data/processed/activity_daily_maharashtra.csv')
print('=== MAHARASHTRA DAILY COLUMNS ===')
print(list(mdf.columns))
print()

tot = int(mdf['total_detections'].sum())
modis = int(mdf['modis_detection_count'].sum())
snpp = int(mdf['viirs_snpp_detection_count'].sum())
n20 = int(mdf['viirs_noaa20_detection_count'].sum())
n21 = int(mdf['viirs_noaa21_detection_count'].sum())
frp_maha = float(mdf['total_frp_sum'].sum())
print(f'Maharashtra total_detections: {tot:,}')
print(f'Maharashtra MODIS_C61: {modis:,}')
print(f'Maharashtra VIIRS_SNPP: {snpp:,}')
print(f'Maharashtra VIIRS_NOAA20: {n20:,}')
print(f'Maharashtra VIIRS_NOAA21: {n21:,}')
print(f'Maharashtra total_frp_sum MW: {frp_maha:,.2f}')
print()

mdf['activity_date'] = pd.to_datetime(mdf['activity_date'])
m16 = mdf[mdf['activity_date'].dt.strftime('%Y-%m-%d') == '2025-03-16']
march16_count = int(m16['total_detections'].sum())
print(f'March 16 Maharashtra detections: {march16_count:,}')
print()

peak_row = mdf.loc[mdf['total_detections'].idxmax()]
print(f'Peak date: {peak_row["activity_date"].strftime("%Y-%m-%d")}  count: {int(peak_row["total_detections"]):,}')
print()
print('=== ALL 31 DAYS ===')
for _, row in mdf.sort_values('activity_date').iterrows():
    print(f'  {row["activity_date"].strftime("%Y-%m-%d")}  {int(row["total_detections"]):>6,}  FRP: {row["total_frp_sum"]:>12,.2f}')
print()

sc = pd.read_csv('data/processed/sensor_comparison_daily_maharashtra.csv')
print('=== SENSOR COMPARISON MAHARASHTRA ===')
print(list(sc.columns))
match_cols = [c for c in sc.columns if any(x in c.lower() for x in ['match','overlap','candidate'])]
print(f'Match cols: {match_cols}')
for col in match_cols:
    print(f'  {col}: {sc[col].sum():,}')
print()

sci = pd.read_csv('data/processed/sensor_comparison_daily_india.csv')
print('=== SENSOR COMPARISON INDIA ===')
match_cols_i = [c for c in sci.columns if any(x in c.lower() for x in ['match','overlap','candidate'])]
print(f'Match cols: {match_cols_i}')
for col in match_cols_i:
    print(f'  India {col}: {sci[col].sum():,}')
print()

with open('frontend/public/data/calendar_maharashtra.json') as f:
    cal = json.load(f)
print('=== CALENDAR STRUCTURE ===')
print(list(cal.keys()))
recs = cal.get('daily_records', [])
print(f'daily_records count: {len(recs)}')
if recs:
    print(f'First record keys: {list(recs[0].keys())}')
    total_cal = sum(r.get('total_detections', r.get('total_observations', 0)) for r in recs)
    print(f'Calendar daily sum total_detections: {total_cal:,}')
    for r in recs:
        d = str(r.get('date', r.get('acq_date', '')))
        if '2025-03-16' in d or d.endswith('16'):
            print(f'March 16 calendar entry: {r}')
            break
    peak_cal = max(recs, key=lambda r: r.get('total_detections', 0))
    print(f'Calendar peak entry: {peak_cal}')
print()
ms = cal.get('month_summary', {})
print(f'month_summary: {ms}')
print()

# active grid cells discrepancy
with open('frontend/public/data/overview_metrics.json') as f:
    om = json.load(f)
print('=== OVERVIEW METRICS JSON ===')
for k, v in om.items():
    print(f'  {k}: {v}')
