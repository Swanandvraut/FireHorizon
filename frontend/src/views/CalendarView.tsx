import React, { useEffect, useState } from 'react';
import {
  Calendar as CalendarIcon,
  Flame,
  Layers,
  Sparkles,
  Info,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  AlertTriangle,
  Clock,
  HelpCircle
} from 'lucide-react';
import { dataService } from '../services/dataService';
import { CalendarBundle, CalendarDay } from '../types';

interface CalendarViewProps {
  region: 'india' | 'maharashtra';
}

export const CalendarView: React.FC<CalendarViewProps> = ({ region }) => {
  const [bundle, setBundle] = useState<CalendarBundle | null>(null);
  const [selectedDay, setSelectedDay] = useState<CalendarDay | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);

    dataService
      .getCalendarBundle(region)
      .then((data) => {
        if (mounted) {
          setBundle(data);
          // Default selected day to peak activity date or first day
          if (data.daily_records && data.daily_records.length > 0) {
            const peak = data.daily_records.find(
              (d) => d.activity_date === data.month_summary.peak_activity_date
            ) || data.daily_records[0];
            setSelectedDay(peak);
          }
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error('Failed to load calendar:', err);
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [region]);

  const getTierBadge = (tier: string) => {
    switch (tier) {
      case 'Extreme Activity':
        return 'bg-red-500/20 text-red-300 border-red-500/40';
      case 'High Activity':
        return 'bg-orange-500/20 text-orange-300 border-orange-500/40';
      case 'Elevated Activity':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'Moderate Activity':
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/40';
      default:
        return 'bg-sky-500/20 text-sky-300 border-sky-500/40';
    }
  };

  const getDayCellColor = (day: CalendarDay) => {
    const isSelected = selectedDay?.activity_date === day.activity_date;
    const tier = day.activity_tier;
    let base = 'bg-slate-900 border-slate-800 text-slate-300 hover:border-slate-700';

    if (tier === 'Extreme Activity') {
      base = 'bg-red-950/50 border-red-900/60 text-red-200 hover:border-red-500';
    } else if (tier === 'High Activity') {
      base = 'bg-orange-950/50 border-orange-900/60 text-orange-200 hover:border-orange-500';
    } else if (tier === 'Elevated Activity') {
      base = 'bg-amber-950/40 border-amber-900/50 text-amber-200 hover:border-amber-500';
    } else if (tier === 'Moderate Activity') {
      base = 'bg-yellow-950/30 border-yellow-900/40 text-yellow-200 hover:border-yellow-500';
    } else {
      base = 'bg-sky-950/30 border-sky-900/40 text-sky-200 hover:border-sky-500';
    }

    if (isSelected) {
      base += ' ring-2 ring-amber-400 border-amber-400 shadow-lg shadow-amber-500/20 scale-[1.02] z-10';
    }
    return base;
  };

  if (loading || !bundle) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] text-slate-400 gap-3">
        <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm">Generating burning activity calendar...</p>
      </div>
    );
  }

  // Days of March 2025 starts on Saturday (ISO day 6)
  const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  // March 1, 2025 is Saturday -> 6 empty padding cells before March 1
  const paddingBefore = Array(6).fill(null);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Month Header Summary */}
      <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <CalendarIcon className="w-5 h-5 text-amber-500" />
              March 2025 — Burning Activity Calendar
            </h2>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
              31 Days Tracked
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Spatial-temporally harmonized active burning calendar for{' '}
            <strong className="text-slate-200 capitalize">{region}</strong>. Click any date to examine granular sensor observations.
          </p>
        </div>

        <div className="flex items-center gap-3 font-mono text-xs text-slate-300">
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-center">
            <span className="text-[10px] uppercase text-slate-400 block font-sans">Monthly Detections</span>
            <strong className="text-amber-400 text-sm">{bundle.month_summary.total_detections.toLocaleString()}</strong>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-center">
            <span className="text-[10px] uppercase text-slate-400 block font-sans">Total FRP (MW)</span>
            <strong className="text-orange-400 text-sm">{(bundle.month_summary.total_frp_sum / 1000).toFixed(1)}k MW</strong>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-center">
            <span className="text-[10px] uppercase text-slate-400 block font-sans">Peak Burning Date</span>
            <strong className="text-red-400 text-sm">{bundle.month_summary.peak_activity_date}</strong>
          </div>
        </div>
      </div>

      {/* Main Grid: Calendar Heatmap + Selected Day Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Heatmap Calendar Matrix */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <span className="font-semibold text-sm text-slate-200">Activity Calendar Grid</span>
            <span className="text-xs text-slate-400">March 2025</span>
          </div>

          {/* Weekday Labels */}
          <div className="grid grid-cols-7 gap-2 text-center text-xs font-semibold text-slate-400">
            {weekdays.map((w) => (
              <div key={w} className="py-1">
                {w}
              </div>
            ))}
          </div>

          {/* Calendar Cells */}
          <div className="grid grid-cols-7 gap-2">
            {paddingBefore.map((_, i) => (
              <div key={`pad-${i}`} className="h-20 rounded-lg bg-slate-950/30 border border-slate-900 opacity-20"></div>
            ))}

            {bundle.daily_records.map((day) => (
              <button
                key={day.activity_date}
                onClick={() => setSelectedDay(day)}
                className={`h-20 p-2 rounded-lg border text-left transition-all duration-150 flex flex-col justify-between ${getDayCellColor(
                  day
                )}`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs">{day.day_num}</span>
                  <span className="text-[9px] font-mono opacity-80">{day.activity_tier.split(' ')[0]}</span>
                </div>
                <div>
                  <div className="text-[11px] font-bold font-mono text-amber-300">
                    {day.total_detections.toLocaleString()}
                  </div>
                  <div className="text-[9px] font-mono text-slate-400">
                    {(day.total_frp_sum / 1000).toFixed(1)}k MW
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* Heatmap Legend */}
          <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs">
            <span className="text-slate-400 font-medium">Activity Intensity:</span>
            <div className="flex flex-wrap items-center gap-2 text-[11px] font-mono">
              <span className="px-2 py-0.5 rounded bg-sky-950 border border-sky-800 text-sky-300">Low</span>
              <span className="px-2 py-0.5 rounded bg-yellow-950 border border-yellow-800 text-yellow-300">Moderate</span>
              <span className="px-2 py-0.5 rounded bg-amber-950 border border-amber-800 text-amber-300">Elevated</span>
              <span className="px-2 py-0.5 rounded bg-orange-950 border border-orange-800 text-orange-300">High</span>
              <span className="px-2 py-0.5 rounded bg-red-950 border border-red-800 text-red-300">Extreme</span>
            </div>
          </div>
        </div>

        {/* Selected Day Inspector */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
          <div className="border-b border-slate-800/80 pb-3 flex items-center justify-between">
            <div>
              <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block">
                Day Inspector
              </span>
              <h3 className="text-base font-bold text-slate-100 font-mono">
                {selectedDay ? selectedDay.activity_date : '---'}
              </h3>
            </div>
            {selectedDay && (
              <span
                className={`text-[11px] px-2.5 py-1 rounded-md font-mono border ${getTierBadge(
                  selectedDay.activity_tier
                )}`}
              >
                {selectedDay.activity_tier}
              </span>
            )}
          </div>

          {selectedDay ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-[11px] text-slate-400 block">Total Detections</span>
                  <span className="text-lg font-bold font-mono text-amber-300">
                    {selectedDay.total_detections.toLocaleString()}
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-[11px] text-slate-400 block">Fire Radiative Power</span>
                  <span className="text-lg font-bold font-mono text-orange-400">
                    {selectedDay.total_frp_sum.toFixed(1)} MW
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-[11px] text-slate-400 block">Active 1km Cells</span>
                  <span className="text-lg font-bold font-mono text-cyan-300">
                    {selectedDay.active_grid_cells.toLocaleString()}
                  </span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-[11px] text-slate-400 block">Co-Detection Overlap</span>
                  <span className="text-lg font-bold font-mono text-emerald-300">
                    {selectedDay.cross_sensor_overlap_cells.toLocaleString()}
                  </span>
                </div>
              </div>

              {/* Sensor Composition for Selected Day */}
              <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
                <h4 className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                  <span>Sensor Family Breakdown</span>
                  <span className="text-[10px] text-slate-500 font-normal">Observation Count</span>
                </h4>
                <div className="space-y-2 text-xs font-mono">
                  <div>
                    <div className="flex justify-between text-slate-400 text-[11px] mb-1">
                      <span>VIIRS (375m)</span>
                      <span className="text-orange-400">{selectedDay.viirs_total_detection_count.toLocaleString()}</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full bg-orange-500 rounded-full"
                        style={{
                          width: `${(selectedDay.viirs_total_detection_count / selectedDay.total_detections) * 100}%`,
                        }}
                      ></div>
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-400 text-[11px] mb-1">
                      <span>MODIS (1000m)</span>
                      <span className="text-cyan-400">{selectedDay.modis_detection_count.toLocaleString()}</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full bg-cyan-400 rounded-full"
                        style={{
                          width: `${(selectedDay.modis_detection_count / selectedDay.total_detections) * 100}%`,
                        }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Experimental Index Notice */}
              <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800/80 text-[11px] space-y-1">
                <div className="flex items-center gap-1.5 text-amber-400 font-semibold">
                  <Sparkles className="w-3.5 h-3.5" /> Experimental Activity Index
                </div>
                <p className="text-slate-300 font-mono text-xs">
                  Score: <strong>{selectedDay.experimental_activity_index} / 100</strong>
                </p>
                <p className="text-slate-500 text-[10px] leading-relaxed">
                  Calculated from resolution-normalized active footprint area weighted with logarithmic FRP factor.
                </p>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-500">Select a date from the calendar to inspect detailed statistics.</p>
          )}
        </div>
      </div>

      {/* Weekly Aggregation Rollup Table */}
      <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
        <h3 className="font-semibold text-sm text-slate-100 flex items-center gap-2">
          Weekly Burning Summaries
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300 font-mono">
            <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">ISO Week</th>
                <th className="py-2.5 px-3">Date Range</th>
                <th className="py-2.5 px-3">Total Observations</th>
                <th className="py-2.5 px-3">MODIS Detections</th>
                <th className="py-2.5 px-3">VIIRS Detections</th>
                <th className="py-2.5 px-3">Total FRP (MW)</th>
                <th className="py-2.5 px-3">Avg Active Cells / Day</th>
                <th className="py-2.5 px-3">Peak Activity Index</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {bundle.weekly_summaries.map((w) => (
                <tr key={w.week_num} className="hover:bg-slate-800/30 transition">
                  <td className="py-2.5 px-3 font-bold text-amber-400">Week {w.week_num}</td>
                  <td className="py-2.5 px-3 text-slate-400 font-sans">{w.start_date} → {w.end_date}</td>
                  <td className="py-2.5 px-3 font-bold">{w.total_detections.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-cyan-400">{w.modis_detections.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-orange-400">{w.viirs_detections.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-amber-300">{w.total_frp_sum.toLocaleString()} MW</td>
                  <td className="py-2.5 px-3">{w.mean_daily_active_cells}</td>
                  <td className="py-2.5 px-3 font-bold text-emerald-400">{w.max_daily_index}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
