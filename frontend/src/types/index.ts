export interface OverviewMetrics {
  dataset_name: string;
  coverage_period: string;
  archive_status: string;
  total_observations: number;
  modis_observations: number;
  viirs_observations: number;
  viirs_snpp: number;
  viirs_noaa20: number;
  viirs_noaa21: number;
  total_frp_mw: number;
  mean_frp_mw: number;
  active_grid_cells_1km_india: number;
  active_grid_cells_1km_maharashtra: number;
  maharashtra_observations: number;
  candidate_matches_india: number;
  candidate_matches_maharashtra: number;
  day_observations: number;
  night_observations: number;
  pipeline_execution_time_seconds: number;
}

export interface DailyActivityRecord {
  activity_date: string;
  region_id: string;
  modis_detection_count: number;
  viirs_snpp_detection_count: number;
  viirs_noaa20_detection_count: number;
  viirs_noaa21_detection_count: number;
  viirs_total_detection_count: number;
  total_detections: number;
  modis_frp_sum: number;
  viirs_frp_sum: number;
  total_frp_sum: number;
  active_grid_cells: number;
  cross_sensor_overlap_cells: number;
  experimental_activity_index: number;
  index_method: string;
  baseline_status: string;
  uncertainty_status: string;
  processing_version: string;
  intra_month_detection_zscore?: number;
  intra_month_frp_zscore?: number;
  climatological_anomaly_status?: string;
  early_warning_claim_allowed?: boolean;
}

export interface SensorComparisonRecord {
  activity_date: string;
  region_id: string;
  sensor_a: string;
  sensor_b: string;
  sensor_a_count: number;
  sensor_b_count: number;
  sensor_a_frp_sum: number;
  sensor_b_frp_sum: number;
  candidate_match_count: number;
  co_detected_grid_cells: number;
  distance_threshold_meters: number;
  time_threshold_minutes: number;
  methodology_version: string;
}

export interface CalendarDay {
  activity_date: string;
  day_num: number;
  day_of_week: string;
  week_num: number;
  activity_tier: string;
  total_detections: number;
  modis_detection_count: number;
  viirs_total_detection_count: number;
  total_frp_sum: number;
  experimental_activity_index: number;
  active_grid_cells: number;
  cross_sensor_overlap_cells: number;
}

export interface CalendarSummary {
  region_id: string;
  month: string;
  days_in_month: number;
  days_with_data: number;
  total_detections: number;
  modis_detections: number;
  viirs_detections: number;
  total_frp_sum: number;
  peak_activity_date: string;
  peak_activity_detections: number;
  peak_frp_date: string;
  peak_frp_mw: number;
  tier_distribution: Record<string, number>;
  baseline_note: string;
}

export interface WeeklySummary {
  week_num: number;
  start_date: string;
  end_date: string;
  total_detections: number;
  modis_detections: number;
  viirs_detections: number;
  total_frp_sum: number;
  mean_daily_active_cells: number;
  max_daily_index: number;
  mean_daily_index: number;
}

export interface CalendarBundle {
  region_id: string;
  month_summary: CalendarSummary;
  weekly_summaries: WeeklySummary[];
  daily_records: CalendarDay[];
}

export interface GridCellFeature {
  grid_id: string;
  center_latitude: number;
  center_longitude: number;
  detection_count: number;
  frp_sum: number;
  brightness_mean: number;
  active_dates: number;
}
