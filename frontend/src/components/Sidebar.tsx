import React from 'react';
import {
  Flame,
  LayoutDashboard,
  Map,
  Calendar,
  Layers,
  BarChart3,
  BookOpen,
  Info,
  ExternalLink,
  Satellite
} from 'lucide-react';

export type ActiveTab =
  | 'overview'
  | 'map'
  | 'calendar'
  | 'comparison'
  | 'analytics'
  | 'methodology'
  | 'about';

interface SidebarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  region: 'india' | 'maharashtra';
  setRegion: (r: 'india' | 'maharashtra') => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  region,
  setRegion,
}) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'map', label: 'Fire Map', icon: Map },
    { id: 'calendar', label: 'Burning Calendar', icon: Calendar },
    { id: 'comparison', label: 'Sensor Comparison', icon: Layers },
    { id: 'analytics', label: 'Regional Analytics', icon: BarChart3 },
    { id: 'methodology', label: 'Methodology & Data', icon: BookOpen },
    { id: 'about', label: 'About FireHorizon', icon: Info },
  ];

  return (
    <aside className="w-64 bg-slate-900/95 border-r border-slate-800 flex flex-col h-screen fixed left-0 top-0 z-30 select-none backdrop-blur">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-tr from-amber-600 to-orange-500 text-slate-950 shadow-lg shadow-amber-500/20">
            <Flame className="w-6 h-6 stroke-[2.5]" />
          </div>
          <div>
            <h1 className="font-bold text-lg text-slate-100 tracking-tight flex items-center gap-1.5">
              FireHorizon
            </h1>
            <p className="text-[11px] text-amber-400 font-medium tracking-wide uppercase">
              NASA Space Apps 2026
            </p>
          </div>
        </div>
        <p className="mt-3 text-xs text-slate-400 leading-relaxed font-normal">
          Satellite Harmonization & Integrated Burning Activity Calendar
        </p>
      </div>

      {/* Region Selector */}
      <div className="px-4 py-3 border-b border-slate-800/60 bg-slate-950/40">
        <label className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase block mb-1.5">
          Area of Interest
        </label>
        <div className="grid grid-cols-2 gap-1.5 bg-slate-900 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setRegion('india')}
            className={`px-2.5 py-1.5 rounded-md text-xs font-medium transition-all ${
              region === 'india'
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            India
          </button>
          <button
            onClick={() => setRegion('maharashtra')}
            className={`px-2.5 py-1.5 rounded-md text-xs font-medium transition-all ${
              region === 'maharashtra'
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Maharashtra
          </button>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id as ActiveTab)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-gradient-to-r from-amber-500/15 to-transparent text-amber-400 border-l-2 border-amber-500 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-amber-400' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Sensor Legend / Footer */}
      <div className="p-3.5 border-t border-slate-800 bg-slate-950/70 text-xs">
        <div className="flex items-center justify-between text-[11px] text-slate-400 mb-2">
          <span className="flex items-center gap-1.5 font-medium text-slate-300">
            <Satellite className="w-3.5 h-3.5 text-cyan-400" /> Sensors Active
          </span>
          <span className="text-emerald-400 font-mono">4 Products</span>
        </div>
        <div className="grid grid-cols-2 gap-1 text-[10px] font-mono text-slate-400">
          <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span> MODIS
          </span>
          <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-orange-400"></span> VIIRS SNPP
          </span>
          <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span> NOAA-20
          </span>
          <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-yellow-400"></span> NOAA-21
          </span>
        </div>
      </div>
    </aside>
  );
};
