import { supabase, isSupabaseConfigured } from './supabase';
import {
  OverviewMetrics,
  DailyActivityRecord,
  SensorComparisonRecord,
  CalendarBundle,
  GridCellFeature
} from '../types';

export const dataService = {
  async getOverviewMetrics(): Promise<OverviewMetrics> {
    try {
      const res = await fetch('/data/overview_metrics.json');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.warn('Failed to fetch overview metrics:', err);
      throw err;
    }
  },

  async getDailyActivity(regionId: 'india' | 'maharashtra' = 'india'): Promise<DailyActivityRecord[]> {
    if (isSupabaseConfigured && supabase) {
      try {
        const { data, error } = await supabase
          .from('activity_daily')
          .select('*')
          .eq('region_id', regionId)
          .order('activity_date', { ascending: true });

        if (!error && data && data.length > 0) {
          return data as DailyActivityRecord[];
        }
      } catch (e) {
        console.warn('Supabase query failed, falling back to local bundle:', e);
      }
    }

    const filename = regionId === 'maharashtra'
      ? '/data/daily_activity_maharashtra.json'
      : '/data/daily_activity_india.json';
    const res = await fetch(filename);
    return await res.json();
  },

  async getSensorComparison(regionId: 'india' | 'maharashtra' = 'india'): Promise<SensorComparisonRecord[]> {
    if (isSupabaseConfigured && supabase) {
      try {
        const { data, error } = await supabase
          .from('sensor_comparison_daily')
          .select('*')
          .eq('region_id', regionId)
          .order('activity_date', { ascending: true });

        if (!error && data && data.length > 0) {
          return data as SensorComparisonRecord[];
        }
      } catch (e) {
        console.warn('Supabase query failed, falling back to local bundle:', e);
      }
    }

    const res = await fetch('/data/sensor_comparison.json');
    return await res.json();
  },

  async getCalendarBundle(regionId: 'india' | 'maharashtra' = 'india'): Promise<CalendarBundle> {
    const filename = regionId === 'maharashtra'
      ? '/data/calendar_maharashtra.json'
      : '/data/calendar_india.json';
    const res = await fetch(filename);
    return await res.json();
  },

  async getGridCells(regionId: 'india' | 'maharashtra' = 'india'): Promise<GridCellFeature[]> {
    const filename = regionId === 'maharashtra'
      ? '/data/grid_cells_maharashtra.json'
      : '/data/grid_cells_india.json';
    const res = await fetch(filename);
    return await res.json();
  },

  async getMaharashtraDisplayBoundary(): Promise<any> {
    const res = await fetch('/data/maharashtra_display.geojson');
    if (!res.ok) {
      // Fallback: try fetching from raw boundaries if hosted
      const alt = await fetch('/data/boundaries/maharashtra.geojson');
      return await alt.json();
    }
    return await res.json();
  }
};
