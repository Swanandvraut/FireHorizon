import React, { useEffect, useState } from 'react';
import {
  Flame,
  Satellite,
  Activity,
  Layers,
  Sun,
  Moon,
  Clock,
  Sparkles,
  Info,
  CalendarDays,
  ShieldAlert
} from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { MetricCard } from '../components/MetricCard';
import { dataService } from '../services/dataService';
import { OverviewMetrics, DailyActivityRecord } from '../types';

interface OverviewViewProps {
  region: 'india' | 'maharashtra';
  onNavigateToTab: (tab: any) => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({ region, onNavigateToTab }) => {
  const [metrics, setMetrics] = useState<OverviewMetrics | null>(null);
  const [dailyData, setDailyData] = useState<DailyActivityRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);

    Promise.all([
      dataService.getOverviewMetrics(),
      dataService.getDailyActivity(region),
    ])
      .then(([m, d]) => {
        if (mounted) {
          setMetrics(m);
          setDailyData(d);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error('Overview load error:', err);
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
        <p className="text-sm">Loading verified satellite observations...</p>
      </div>
    );
  }

  const isMh = region === 'maharashtra';
  // Fallback to 0 — never use hardcoded fake statistics.
  // All values come from frontend/public/data/overview_metrics.json (computed by pipeline).
  const obsCount = isMh
    ? (metrics?.maharashtra_observations ?? 0)
    : (metrics?.total_observations ?? 0);

  const activeCells = isMh
    ? (metrics?.active_grid_cells_1km_maharashtra ?? 0)
    : (metrics?.active_grid_cells_1km_india ?? 0);

  const candidateMatches = isMh
    ? (metrics?.candidate_matches_maharashtra ?? 0)
    : (metrics?.candidate_matches_india ?? 0);

  const pieData = metrics ? [
    { name: 'MODIS (Terra & Aqua)', value: metrics.modis_observations, color: '#38bdf8' },
    { name: 'VIIRS Suomi-NPP', value: metrics.viirs_snpp, color: '#f97316' },
    { name: 'VIIRS NOAA-20', value: metrics.viirs_noaa20, color: '#f59e0b' },
    { name: 'VIIRS NOAA-21', value: metrics.viirs_noaa21, color: '#eab308' },
  ] : [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Banner / Archival Status Notice */}
      <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 shrink-0">
            <CalendarDays className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              Archived NASA FIRMS Dataset — March 1–31, 2025
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30">
                Verified Research Benchmark
              </span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Harmonizing MODIS C6.1 (1km) and VIIRS C2 (375m) observations over{' '}
              <strong className="text-slate-200 capitalize">{region}</strong>. Notice: Detections represent satellite observation events, not unique physical fires.
            </p>
          </div>
        </div>

        <button
          onClick={() => onNavigateToTab('calendar')}
          className="self-start md:self-auto px-3.5 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold text-xs transition flex items-center gap-1.5 shadow-sm"
        >
          View Burning Calendar &rarr;
        </button>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Satellite Detections"
          value={obsCount.toLocaleString()}
          subtitle={`${isMh ? 'Maharashtra subset' : 'India-wide total'}`}
          icon={Flame}
          badge="NASA Verified Observations"
          variant="amber"
        />
        <MetricCard
          title="Active 1km Equal-Area Cells"
          value={activeCells.toLocaleString()}
          subtitle="EPSG:6933 Binned Grid"
          icon={Layers}
          badge="1 km × 1 km Resolution"
          variant="cyan"
        />
        <MetricCard
          title="Candidate Co-Detections"
          value={candidateMatches.toLocaleString()}
          subtitle="MODIS & VIIRS concurrence"
          icon={Activity}
          badge="Δd ≤ 1km, Δt ≤ 60min"
          variant="emerald"
        />
        <MetricCard
          title="Total Fire Radiative Power"
          value={metrics ? `${(metrics.total_frp_mw / 1000).toFixed(1)}k MW` : '---'}
          subtitle="Radiative heat emission"
          icon={Sparkles}
          badge="Combined Sensors (MW)"
          variant="orange"
        />
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Daily Burning Trend Chart */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
            <div>
              <h3 className="font-semibold text-sm text-slate-100 flex items-center gap-2">
                Daily Detection Observations & Energy Profile
              </h3>
              <p className="text-xs text-slate-400">
                Comparing MODIS vs VIIRS daily temporal trends (March 1–31, 2025)
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-orange-500"></span> VIIRS
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-cyan-400"></span> MODIS
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-0.5 bg-amber-400"></span> FRP (MW)
              </span>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={dailyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis
                  dataKey="activity_date"
                  tick={{ fill: '#64748b', fontSize: 11 }}
                  tickFormatter={(v) => v.slice(8)} // Show day number
                />
                <YAxis
                  yAxisId="left"
                  tick={{ fill: '#64748b', fontSize: 11 }}
                  tickFormatter={(v) => (v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v)}
                />
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  tick={{ fill: '#64748b', fontSize: 11 }}
                  tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '0.5rem',
                    fontSize: '12px',
                  }}
                  labelFormatter={(v) => `Date: ${v}`}
                />
                <Bar
                  yAxisId="left"
                  dataKey="viirs_total_detection_count"
                  name="VIIRS Observations"
                  fill="#f97316"
                  opacity={0.85}
                  stackId="a"
                />
                <Bar
                  yAxisId="left"
                  dataKey="modis_detection_count"
                  name="MODIS Observations"
                  fill="#38bdf8"
                  opacity={0.85}
                  stackId="a"
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="total_frp_sum"
                  name="Total FRP (MW)"
                  stroke="#fbbf24"
                  strokeWidth={2}
                  dot={false}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sensor Share Breakdown */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="font-semibold text-sm text-slate-100 flex items-center gap-2">
              Sensor Family Contribution
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Distribution of raw observations across satellite platforms
            </p>
          </div>

          <div className="h-52 w-full relative flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {pieData.map((entry, idx) => (
                    <Cell key={`cell-${idx}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '0.5rem',
                    fontSize: '12px',
                  }}
                  formatter={(val: any) => [Number(val).toLocaleString(), 'Observations']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-1.5 text-xs border-t border-slate-800/80 pt-3 font-mono">
            {pieData.map((p) => (
              <div key={p.name} className="flex items-center justify-between text-slate-300">
                <span className="flex items-center gap-2 text-slate-400 font-sans">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: p.color }}></span>
                  {p.name}
                </span>
                <span>{p.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Diurnal Breakdown and Scientific Cautions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Day / Night Distribution */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Diurnal Overpass Distribution
          </h4>
          <div className="grid grid-cols-2 gap-3 pt-1">
            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <div className="flex items-center gap-1.5 text-amber-400 text-xs font-medium">
                <Sun className="w-4 h-4" /> Daytime
              </div>
              <p className="text-xl font-bold font-mono text-slate-100">
                {metrics ? `${((metrics.day_observations / metrics.total_observations) * 100).toFixed(1)}%` : '---'}
              </p>
              <p className="text-[11px] text-slate-500 font-mono">
                {metrics?.day_observations.toLocaleString()} obs
              </p>
            </div>

            <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <div className="flex items-center gap-1.5 text-indigo-400 text-xs font-medium">
                <Moon className="w-4 h-4" /> Nighttime
              </div>
              <p className="text-xl font-bold font-mono text-slate-100">
                {metrics ? `${((metrics.night_observations / metrics.total_observations) * 100).toFixed(1)}%` : '---'}
              </p>
              <p className="text-[11px] text-slate-500 font-mono">
                {metrics?.night_observations.toLocaleString()} obs
              </p>
            </div>
          </div>
          <p className="text-[11px] text-slate-500 pt-1 leading-relaxed">
            Daytime burning is driven by peak agricultural residue clearing and highest solar surface heating.
          </p>
        </div>

        {/* Scientific Ground Rule Alert */}
        <div className="md:col-span-2 p-5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs uppercase tracking-wider">
            <ShieldAlert className="w-4 h-4" /> Scientific Integrity Guidelines Maintained
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-slate-300">
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 space-y-1">
              <span className="font-semibold text-amber-300">1. Observation Count ≠ Fire Count</span>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                Raw detection counts reflect satellite scan points, which may capture the same fire across successive orbits.
              </p>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 space-y-1">
              <span className="font-semibold text-cyan-300">2. Incomparable Confidences</span>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                MODIS numeric (0–100%) and VIIRS categorical (low/nominal/high) confidences are strictly segregated.
              </p>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 space-y-1">
              <span className="font-semibold text-emerald-300">3. Accurate Geometry</span>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                Maharashtra filtering utilizes verified administrative boundaries from geoBoundaries (no rough bounding boxes).
              </p>
            </div>
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 space-y-1">
              <span className="font-semibold text-orange-300">4. Baseline Caution</span>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                Single-month data (March 2025) cannot establish multi-year seasonal anomalies. Climatological forecasting is restricted.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
