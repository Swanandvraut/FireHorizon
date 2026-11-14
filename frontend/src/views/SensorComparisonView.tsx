import React, { useEffect, useState } from 'react';
import {
  Layers,
  Scale,
  Activity,
  AlertCircle,
  HelpCircle,
  ArrowRight,
  Sparkles,
  BarChart2
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line,
  Legend
} from 'recharts';
import { dataService } from '../services/dataService';
import { SensorComparisonRecord, DailyActivityRecord } from '../types';

interface SensorComparisonViewProps {
  region: 'india' | 'maharashtra';
}

export const SensorComparisonView: React.FC<SensorComparisonViewProps> = ({ region }) => {
  const [comparisons, setComparisons] = useState<SensorComparisonRecord[]>([]);
  const [dailyData, setDailyData] = useState<DailyActivityRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);

    Promise.all([
      dataService.getSensorComparison(region),
      dataService.getDailyActivity(region),
    ])
      .then(([comp, daily]) => {
        if (mounted) {
          setComparisons(comp || []);
          setDailyData(daily || []);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error('Failed to load sensor comparison:', err);
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [region]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] text-slate-400 gap-3">
        <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm">Evaluating cross-sensor spatial-temporal matches...</p>
      </div>
    );
  }

  const totalModisObs = dailyData.reduce((acc, d) => acc + d.modis_detection_count, 0);
  const totalViirsObs = dailyData.reduce((acc, d) => acc + d.viirs_total_detection_count, 0);
  const ratio = totalModisObs > 0 ? (totalViirsObs / totalModisObs).toFixed(1) : '---';

  const totalCoDetections = comparisons.reduce((acc, c) => acc + c.candidate_match_count, 0);
  const totalOverlapCells = comparisons.reduce((acc, c) => acc + c.co_detected_grid_cells, 0);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Module Title Banner */}
      <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
        <div className="flex items-center gap-2">
          <Scale className="w-5 h-5 text-amber-500" />
          <h2 className="text-lg font-bold text-slate-100">
            Sensor Harmonization & Comparative Analysis
          </h2>
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
            MODIS vs VIIRS
          </span>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed max-w-4xl">
          Direct quantitative comparison between 1000m MODIS (Terra/Aqua) and 375m VIIRS (Suomi-NPP, NOAA-20, NOAA-21)
          over <strong>{region}</strong>. Demonstrates why observation counts diverge and how spatial-temporal concurrence is assessed.
        </p>
      </div>

      {/* Comparison Metrics Header */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/80 border border-cyan-500/20">
          <span className="text-xs text-slate-400 block font-medium uppercase">MODIS Total Detections</span>
          <p className="text-2xl font-bold font-mono text-cyan-400 mt-1">{totalModisObs.toLocaleString()}</p>
          <span className="text-[11px] text-slate-500 font-mono">1000m Nominal Nadir</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-orange-500/20">
          <span className="text-xs text-slate-400 block font-medium uppercase">VIIRS Total Detections</span>
          <p className="text-2xl font-bold font-mono text-orange-400 mt-1">{totalViirsObs.toLocaleString()}</p>
          <span className="text-[11px] text-slate-500 font-mono">375m I-Band (3 Satellites)</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-amber-500/20">
          <span className="text-xs text-slate-400 block font-medium uppercase">Detection Granularity Ratio</span>
          <p className="text-2xl font-bold font-mono text-amber-400 mt-1">{ratio} : 1</p>
          <span className="text-[11px] text-slate-500 font-mono">VIIRS to MODIS Granularity</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-emerald-500/20">
          <span className="text-xs text-slate-400 block font-medium uppercase">Candidate Co-Detections</span>
          <p className="text-2xl font-bold font-mono text-emerald-400 mt-1">{totalCoDetections.toLocaleString()}</p>
          <span className="text-[11px] text-slate-500 font-mono">Δd ≤ 1km & Δt ≤ 60min</span>
        </div>
      </div>

      {/* Side-by-Side Instrument Specification Table */}
      <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
        <h3 className="font-semibold text-sm text-slate-100 flex items-center gap-2">
          Physical Instrument Specifications & Discrepancy Drivers
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] border-b border-slate-800 font-mono">
              <tr>
                <th className="py-2.5 px-3">Physical Attribute</th>
                <th className="py-2.5 px-3 text-cyan-400">MODIS (Terra & Aqua)</th>
                <th className="py-2.5 px-3 text-orange-400">VIIRS (SNPP, NOAA-20, NOAA-21)</th>
                <th className="py-2.5 px-3 text-amber-400">Harmonization Impact</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans text-xs">
              <tr className="hover:bg-slate-800/30">
                <td className="py-2.5 px-3 font-semibold text-slate-200">Nominal Resolution</td>
                <td className="py-2.5 px-3 font-mono">1000 m (1.0 km² nadir)</td>
                <td className="py-2.5 px-3 font-mono">375 m (0.14 km² nadir)</td>
                <td className="py-2.5 px-3 text-slate-400 leading-relaxed">
                  VIIRS pixel area is ~7.1× smaller. Highly sensitive to small agricultural crop-waste burns.
                </td>
              </tr>
              <tr className="hover:bg-slate-800/30">
                <td className="py-2.5 px-3 font-semibold text-slate-200">Equatorial Overpass</td>
                <td className="py-2.5 px-3 font-mono">10:30 AM/PM (Terra), 01:30 AM/PM (Aqua)</td>
                <td className="py-2.5 px-3 font-mono">01:30 AM/PM (S-NPP, N20 ~50m offset, N21)</td>
                <td className="py-2.5 px-3 text-slate-400 leading-relaxed">
                  Three afternoon VIIRS overpasses provide triple afternoon sampling during peak burning hours.
                </td>
              </tr>
              <tr className="hover:bg-slate-800/30">
                <td className="py-2.5 px-3 font-semibold text-slate-200">Confidence Encoding</td>
                <td className="py-2.5 px-3 font-mono">Numeric probability (0 to 100%)</td>
                <td className="py-2.5 px-3 font-mono">Categorical classes ('l', 'n', 'h')</td>
                <td className="py-2.5 px-3 text-slate-400 leading-relaxed">
                  Scales are non-interchangeable. Merging without transformation creates false statistics.
                </td>
              </tr>
              <tr className="hover:bg-slate-800/30">
                <td className="py-2.5 px-3 font-semibold text-slate-200">Detection Threshold</td>
                <td className="py-2.5 px-3 font-mono">FRP threshold ~ 10–20 MW</td>
                <td className="py-2.5 px-3 font-mono">FRP threshold ~ 1–3 MW</td>
                <td className="py-2.5 px-3 text-slate-400 leading-relaxed">
                  VIIRS detects cooler, lower-intensity smoldering events invisible to MODIS.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Cross-Sensor Daily Time Series Chart */}
      <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
          <div>
            <h3 className="font-semibold text-sm text-slate-100">
              Daily Temporal Agreement & Spatial Co-Detection Trends
            </h3>
            <p className="text-xs text-slate-400">
              Co-detected 1km grid cells vs candidate observation matches over time
            </p>
          </div>
          <div className="flex items-center gap-4 text-xs font-mono text-slate-400">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-sm bg-emerald-400"></span> Candidate Matches
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-0.5 bg-amber-400"></span> Co-Detected Cells
            </span>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={comparisons} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis dataKey="activity_date" tick={{ fill: '#64748b', fontSize: 11 }} tickFormatter={(v) => v.slice(8)} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#334155',
                  borderRadius: '0.5rem',
                  fontSize: '12px',
                }}
                labelFormatter={(v) => `Date: ${v}`}
              />
              <Bar dataKey="candidate_match_count" name="Candidate Matches" fill="#10b981" opacity={0.8} />
              <Bar dataKey="co_detected_grid_cells" name="Co-Detected 1km Cells" fill="#f59e0b" opacity={0.8} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
