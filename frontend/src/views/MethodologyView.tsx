import React from 'react';
import {
  BookOpen,
  ExternalLink,
  ShieldCheck,
  Cpu,
  Layers,
  Sparkles,
  AlertTriangle,
  FileText
} from 'lucide-react';

export const MethodologyView: React.FC = () => {
  return (
    <div className="space-y-6 max-w-5xl mx-auto text-slate-300">
      {/* Title Header */}
      <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
        <div className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-amber-500" />
          <h2 className="text-xl font-bold text-slate-100">
            Scientific Methodology, Provenance & Mathematical Formulation
          </h2>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          Open documentation explaining the physics, sensor discrepancies, mathematical harmonization, and uncertainties
          implemented within the FireHorizon platform.
        </p>
      </div>

      {/* Sensor Resolution & Optics */}
      <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
        <h3 className="text-base font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-3">
          <Cpu className="w-4 h-4 text-cyan-400" />
          1. Satellite Sensor Resolution & Optics Discrepancies
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
            <span className="font-semibold text-cyan-400 block text-sm">MODIS (Terra & Aqua)</span>
            <p className="text-slate-400 leading-relaxed">
              MODIS Collection 6.1 active fire algorithms detect hot spots using 4 µm (channels 21 and 22) and 11 µm (channel 31)
              radiances at a nominal nadir spatial resolution of <strong>1000 m (1.0 km²)</strong>. Because of the broad pixel footprint,
              sub-pixel fires must attain sufficient energy output (typically &gt; 10–20 MW FRP) to trigger detection against solar reflective background.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
            <span className="font-semibold text-orange-400 block text-sm">VIIRS (Suomi-NPP, NOAA-20, NOAA-21)</span>
            <p className="text-slate-400 leading-relaxed">
              VIIRS Collection 2 fire product incorporates 375 m imagery channels (I4 at 3.74 µm and I5 at 11.45 µm) providing a nominal
              ground pixel area of <strong>0.14 km² (~7.1× finer spatial resolution)</strong>. This significantly reduces background contamination,
              permitting detection of small, low-intensity flaming and smoldering agricultural burns down to ~1–3 MW FRP.
            </p>
          </div>
        </div>
      </div>

      {/* Mathematical Harmonization Formula */}
      <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
        <h3 className="text-base font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-3">
          <Sparkles className="w-4 h-4 text-amber-500" />
          2. Experimental Activity Index (EAI) Formulation
        </h3>

        <p className="text-xs text-slate-400 leading-relaxed">
          Rather than naively adding MODIS and VIIRS observation counts, FireHorizon calculates a normalized composite activity
          indicator that normalizes for footprint area differences and logarithmic fire energy:
        </p>

        <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 font-mono text-center text-xs text-amber-300 overflow-x-auto">
          EAI = min(100, [(w_M · A_M + w_V · A_V · κ) · (1 + log10(1 + FRP_total / FRP_ref))] / Σ_norm)
        </div>

        <div className="space-y-1.5 text-xs text-slate-400">
          <p><strong className="text-slate-200">Where:</strong></p>
          <ul className="list-disc pl-5 space-y-1 text-slate-400">
            <li><strong className="text-slate-300">A_M:</strong> Active grid cell area detected by MODIS (km²).</li>
            <li><strong className="text-slate-300">A_V:</strong> Active grid cell area detected by VIIRS (km²).</li>
            <li><strong className="text-slate-300">w_M = 1.0, w_V = 0.6:</strong> Weighting factors adjusting for orbital overpass redundancy (3 VIIRS afternoon passes vs 1 MODIS Aqua pass).</li>
            <li><strong className="text-slate-300">κ = 2.5:</strong> Spatial resolution compensation scaling factor.</li>
            <li><strong className="text-slate-300">FRP_ref = 100 MW:</strong> Reference normalization constant.</li>
            <li><strong className="text-slate-300">Σ_norm = 500.0:</strong> Regional scaling denominator normalizing score to a 0–100 scale.</li>
          </ul>
        </div>
      </div>

      {/* Spatial Grid & Projection */}
      <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 space-y-4">
        <h3 className="text-base font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-3">
          <Layers className="w-4 h-4 text-emerald-400" />
          3. Common Spatial Grid: EPSG:6933 (World Cylindrical Equal Area)
        </h3>

        <p className="text-xs text-slate-400 leading-relaxed">
          Comparing hot spots across India without spatial distortion requires an equal-area coordinate reference system.
          Standard latitude/longitude (WGS84 degrees) distorts cell area between southern Kerala (~8°N) and northern Kashmir (~35°N).
          FireHorizon projects all raw coordinates into <strong>EPSG:6933</strong>, establishing regular 1 km × 1 km spatial bins
          (<code className="text-amber-400">GRID_1000M_R{`{row}`}_C{`{col}`}</code>).
        </p>
      </div>

      {/* Climatological Limitations Alert */}
      <div className="p-6 rounded-xl bg-slate-900/80 border border-amber-500/30 space-y-3">
        <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
          <AlertTriangle className="w-5 h-5" />
          4. Climatological Baseline & Early Warning Restraint
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          The supplied archive strictly covers <strong>March 1–31, 2025 (31 days)</strong>.
          Under scientific standards, declaring a fire anomaly or operational early-warning forecast requires a verified
          5-to-10-year climatological baseline (e.g., 2015–2024 historical reference period).
          Therefore, FireHorizon restricts calculations to intra-month statistical variance (Median Absolute Deviation robust z-score)
          and marks multi-year climatological baseline as <em>"Insufficient (requires 5+ years)"</em>.
        </p>
      </div>

      {/* Official References */}
      <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
        <h3 className="text-base font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-3">
          <FileText className="w-4 h-4 text-cyan-400" />
          5. Official NASA References & Data Citations
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <a
            href="https://firms.modaps.eosdis.nasa.gov/"
            target="_blank"
            rel="noreferrer"
            className="p-3 rounded-lg bg-slate-950 border border-slate-800 hover:border-slate-700 transition flex items-center justify-between"
          >
            <span>NASA FIRMS Fire Information for Resource Management System</span>
            <ExternalLink className="w-3.5 h-3.5 text-amber-400" />
          </a>

          <a
            href="https://firms.modaps.eosdis.nasa.gov/content/active_fire/"
            target="_blank"
            rel="noreferrer"
            className="p-3 rounded-lg bg-slate-950 border border-slate-800 hover:border-slate-700 transition flex items-center justify-between"
          >
            <span>NASA Active Fire Data Products</span>
            <ExternalLink className="w-3.5 h-3.5 text-amber-400" />
          </a>

          <a
            href="https://firms2.modaps.eosdis.nasa.gov/descriptions/FIRMS_MODIS_Firehotspots.html"
            target="_blank"
            rel="noreferrer"
            className="p-3 rounded-lg bg-slate-950 border border-slate-800 hover:border-slate-700 transition flex items-center justify-between"
          >
            <span>MODIS Collection 6.1 Active Fire Product Guide</span>
            <ExternalLink className="w-3.5 h-3.5 text-amber-400" />
          </a>

          <a
            href="https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html"
            target="_blank"
            rel="noreferrer"
            className="p-3 rounded-lg bg-slate-950 border border-slate-800 hover:border-slate-700 transition flex items-center justify-between"
          >
            <span>VIIRS 375m Active Fire Product Guide</span>
            <ExternalLink className="w-3.5 h-3.5 text-amber-400" />
          </a>

          <a
            href="https://www.earthdata.nasa.gov/"
            target="_blank"
            rel="noreferrer"
            className="p-3 rounded-lg bg-slate-950 border border-slate-800 hover:border-slate-700 transition flex items-center justify-between"
          >
            <span>NASA Earthdata Open Science</span>
            <ExternalLink className="w-3.5 h-3.5 text-amber-400" />
          </a>

          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex items-center justify-between">
            <span>Maharashtra Boundary: geoBoundaries gbOpen ADM1 (CC BY 2.5 IN)</span>
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          </div>
        </div>
      </div>
    </div>
  );
};
