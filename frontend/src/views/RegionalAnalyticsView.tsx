import React, { useEffect, useState } from 'react';
import {
  BarChart3,
  Download,
  MapPin,
  Flame,
  Layers,
  Sparkles,
  ArrowUpDown,
  Filter
} from 'lucide-react';
import { dataService } from '../services/dataService';
import { DailyActivityRecord, GridCellFeature } from '../types';

interface RegionalAnalyticsViewProps {
  region: 'india' | 'maharashtra';
}

export const RegionalAnalyticsView: React.FC<RegionalAnalyticsViewProps> = ({ region }) => {
  const [dailyData, setDailyData] = useState<DailyActivityRecord[]>([]);
  const [gridCells, setGridCells] = useState<GridCellFeature[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);

    Promise.all([
      dataService.getDailyActivity(region),
      dataService.getGridCells(region),
    ])
      .then(([daily, cells]) => {
        if (mounted) {
          setDailyData(daily);
          setGridCells(cells);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error('Failed to load regional analytics:', err);
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [region]);

  const handleExportCSV = () => {
    if (dailyData.length === 0) return;
    const headers = Object.keys(dailyData[0]).join(',');
    const rows = dailyData.map((d) => Object.values(d).map((v) => `"${v}"`).join(','));
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers, ...rows].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `firehorizon_daily_activity_${region}_march2025.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] text-slate-400 gap-3">
        <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm">Compiling regional burning analytics...</p>
      </div>
    );
  }

  const topCells = gridCells.slice(0, 15);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Banner & Export Action */}
      <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-amber-500" />
            Regional Analytics & Spatial Hotspot Ranking
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Spatial distribution, peak radiating cells, and downloadable open data for{' '}
            <strong className="text-slate-200 capitalize">{region}</strong>.
          </p>
        </div>

        <button
          onClick={handleExportCSV}
          className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 font-medium text-xs transition flex items-center gap-2 shadow-sm self-start sm:self-auto"
        >
          <Download className="w-4 h-4 text-amber-400" />
          Export Regional CSV
        </button>
      </div>

      {/* Top Active 1km Equal-Area Grid Cells Table */}
      <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <div>
            <h3 className="font-semibold text-sm text-slate-100 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-amber-500" />
              Top Active 1 km² Equal-Area Grid Cells
            </h3>
            <p className="text-xs text-slate-400">
              Ranked by cumulative Fire Radiative Power (MW) across March 2025
            </p>
          </div>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
            Top 15 Hotspots
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300 font-mono">
            <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Rank</th>
                <th className="py-2.5 px-3">Grid Cell ID</th>
                <th className="py-2.5 px-3">Center Coordinates</th>
                <th className="py-2.5 px-3">Detection Count</th>
                <th className="py-2.5 px-3">Cumulative FRP (MW)</th>
                <th className="py-2.5 px-3">Mean Brightness (K)</th>
                <th className="py-2.5 px-3">Active Days</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {topCells.map((cell, idx) => (
                <tr key={cell.grid_id} className="hover:bg-slate-800/30 transition">
                  <td className="py-2.5 px-3 font-bold text-amber-400 font-mono">#{idx + 1}</td>
                  <td className="py-2.5 px-3 font-mono text-slate-200">{cell.grid_id}</td>
                  <td className="py-2.5 px-3 font-mono text-slate-400">
                    {cell.center_latitude.toFixed(3)}°N, {cell.center_longitude.toFixed(3)}°E
                  </td>
                  <td className="py-2.5 px-3 font-bold font-mono text-amber-300">
                    {cell.detection_count.toLocaleString()}
                  </td>
                  <td className="py-2.5 px-3 font-mono text-orange-400 font-bold">
                    {cell.frp_sum.toFixed(1)} MW
                  </td>
                  <td className="py-2.5 px-3 font-mono">{cell.brightness_mean.toFixed(1)} K</td>
                  <td className="py-2.5 px-3 font-mono text-emerald-400 font-semibold">{cell.active_dates} days</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Daily Anomaly & Statistical Variance Status Table */}
      <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
        <div>
          <h3 className="font-semibold text-sm text-slate-100 flex items-center gap-2">
            Intra-Sample Statistical Deviation & Climatological Status
          </h3>
          <p className="text-xs text-slate-400">
            Robust z-scores calculated against the March 2025 median (MAD normalized). Climatological early warning is held unvalidated.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300 font-mono">
            <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Date</th>
                <th className="py-2.5 px-3">Total Detections</th>
                <th className="py-2.5 px-3">Total FRP (MW)</th>
                <th className="py-2.5 px-3">Robust Z-Score (Detections)</th>
                <th className="py-2.5 px-3">Robust Z-Score (FRP)</th>
                <th className="py-2.5 px-3">Climatological Baseline Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {dailyData.slice(0, 10).map((d) => (
                <tr key={d.activity_date} className="hover:bg-slate-800/30 transition">
                  <td className="py-2.5 px-3 font-semibold text-slate-200">{d.activity_date}</td>
                  <td className="py-2.5 px-3 text-amber-300">{d.total_detections.toLocaleString()}</td>
                  <td className="py-2.5 px-3 text-orange-400">{d.total_frp_sum.toFixed(1)} MW</td>
                  <td className="py-2.5 px-3">
                    <span className={Number(d.intra_month_detection_zscore) > 1.5 ? 'text-amber-400 font-bold' : 'text-slate-400'}>
                      {d.intra_month_detection_zscore}σ
                    </span>
                  </td>
                  <td className="py-2.5 px-3">
                    <span className={Number(d.intra_month_frp_zscore) > 1.5 ? 'text-orange-400 font-bold' : 'text-slate-400'}>
                      {d.intra_month_frp_zscore}σ
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-sans text-[11px] text-slate-400">
                    <span className="px-2 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-slate-700">
                      Baseline Insufficient (1-month archive)
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
