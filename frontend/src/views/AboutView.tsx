import React from 'react';
import {
  Users,
  Award,
  Globe,
  Rocket,
  ShieldCheck,
  CheckCircle2,
  ExternalLink
} from 'lucide-react';

export const AboutView: React.FC = () => {
  const teamMembers = [
    { name: 'Swanand Raut', role: 'Full-Stack Software Engineer & Lead Architect' },
    { name: 'Swaral Dabhade', role: 'Geospatial Data Scientist & Remote Sensing Analyst' },
    { name: 'Raj Dakle', role: 'Database Architect & Cloud Infrastructure Engineer' },
    { name: 'Vishal Sable', role: 'UI/UX Designer & Frontend Geospatial Developer' },
  ];

  return (
    <div className="space-y-6 max-w-4xl mx-auto text-slate-300">
      {/* Hero Banner */}
      <div className="p-8 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-amber-950/30 border border-slate-800 space-y-3 relative overflow-hidden">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-mono">
          <Award className="w-3.5 h-3.5" /> NASA Space Apps Challenge 2026 — Kopargaon
        </div>
        <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-100 tracking-tight">
          FireHorizon
        </h2>
        <p className="text-amber-400 font-medium text-sm">
          Satellite Harmonization & Integrated Burning Activity Calendar
        </p>
        <p className="text-xs text-slate-400 leading-relaxed max-w-2xl pt-1">
          Developed to reconcile NASA MODIS (1km) and VIIRS (375m) thermal hot-spot observations into a unified,
          scientifically validated burning activity calendar for environmental researchers, emergency responders,
          and forest management agencies.
        </p>
      </div>

      {/* Team Roster */}
      <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
        <h3 className="text-base font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-3">
          <Users className="w-4 h-4 text-amber-500" />
          Challenge Team Members
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {teamMembers.map((member, i) => (
            <div
              key={member.name}
              className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 flex items-start gap-3"
            >
              <div className="w-8 h-8 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 flex items-center justify-center font-mono font-bold text-xs shrink-0">
                0{i + 1}
              </div>
              <div className="space-y-0.5">
                <h4 className="text-sm font-bold text-slate-100">{member.name}</h4>
                <p className="text-xs text-slate-400">{member.role}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Key Architectural Highlights */}
      <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
        <h3 className="text-base font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-3">
          <Rocket className="w-4 h-4 text-cyan-400" />
          Delivered Capabilities
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-200 block">652,025 Verified NASA Records</strong>
              <span className="text-slate-400">
                Full provenance preserved across MODIS C6.1, Suomi-NPP, NOAA-20, and NOAA-21.
              </span>
            </div>
          </div>

          <div className="flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-200 block">EPSG:6933 Equal-Area Grid</strong>
              <span className="text-slate-400">
                Eliminates latitudinal area distortions with 1km analytical cells.
              </span>
            </div>
          </div>

          <div className="flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-200 block">Official Administrative Boundary</strong>
              <span className="text-slate-400">
                Exact point-in-polygon filtering using verified Maharashtra GeoJSON.
              </span>
            </div>
          </div>

          <div className="flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-200 block">Interactive Burning Calendar</strong>
              <span className="text-slate-400">
                Daily, weekly, and monthly activity heatmaps with documented intensity tiering.
              </span>
            </div>
          </div>

          <div className="flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-200 block">Supabase PostgreSQL Integration</strong>
              <span className="text-slate-400">
                Secure Row Level Security (RLS) policies and idempotent bulk migration scripts.
              </span>
            </div>
          </div>

          <div className="flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-200 block">Full Scientific Transparency</strong>
              <span className="text-slate-400">
                Explicit limitation policies; no unvalidated early-warning or forecast claims.
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
