import React from 'react';
import { Database, ShieldCheck, Clock, ExternalLink } from 'lucide-react';
import { isSupabaseConfigured } from '../services/supabase';

interface HeaderProps {
  region: 'india' | 'maharashtra';
}

export const Header: React.FC<HeaderProps> = ({ region }) => {
  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/60 backdrop-blur sticky top-0 z-20 px-6 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-300">
          Target: <strong className="text-amber-400 capitalize">{region}</strong>
        </span>
        <span className="hidden sm:flex items-center gap-1.5 text-xs text-slate-400 bg-slate-950/60 px-3 py-1 rounded-full border border-slate-800/80">
          <Clock className="w-3.5 h-3.5 text-amber-500" />
          <span>Archive Coverage: <strong>March 1–31, 2025 (UTC)</strong></span>
        </span>
      </div>

      <div className="flex items-center gap-3">
        {/* Cloud DB Connection Status Indicator */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-950 border border-slate-800 text-xs">
          <Database className={`w-3.5 h-3.5 ${isSupabaseConfigured ? 'text-emerald-400' : 'text-cyan-400'}`} />
          <span className="text-slate-300 hidden md:inline">Storage:</span>
          {isSupabaseConfigured ? (
            <span className="flex items-center gap-1 text-emerald-400 font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Supabase Connected
            </span>
          ) : (
            <span className="flex items-center gap-1 text-cyan-400 font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span> Local Verified Engine
            </span>
          )}
        </div>

        {/* NASA FIRMS Provenance Badge */}
        <a
          href="https://firms.modaps.eosdis.nasa.gov/"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 px-2.5 py-1 rounded-lg hover:bg-slate-800/60 transition"
        >
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span className="hidden sm:inline">NASA FIRMS Provenance</span>
          <ExternalLink className="w-3 h-3 text-slate-500" />
        </a>
      </div>
    </header>
  );
};
