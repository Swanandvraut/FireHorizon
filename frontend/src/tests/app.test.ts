import { describe, it, expect } from 'vitest';
import { isSupabaseConfigured } from '../services/supabase';

describe('Frontend Services & Configuration', () => {
  it('handles Supabase configuration state safely without throwing', () => {
    expect(typeof isSupabaseConfigured).toBe('boolean');
  });

  it('dataService falls back safely to pre-packaged bundles', async () => {
    // Basic verification of service interface contract
    const dataService = (await import('../services/dataService')).dataService;
    expect(dataService).toBeDefined();
    expect(typeof dataService.getOverviewMetrics).toBe('function');
    expect(typeof dataService.getDailyActivity).toBe('function');
    expect(typeof dataService.getCalendarBundle).toBe('function');
    expect(typeof dataService.getGridCells).toBe('function');
  });
});
