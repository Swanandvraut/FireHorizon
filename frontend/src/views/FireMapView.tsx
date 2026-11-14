import React, { useEffect, useState, useMemo } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, GeoJSON } from 'react-leaflet';
import {
  Flame,
  Filter,
  Layers,
  Calendar,
  Eye,
  Sliders,
  MapPin,
  Info,
  Maximize2
} from 'lucide-react';
import { dataService } from '../services/dataService';
import { GridCellFeature } from '../types';

interface FireMapViewProps {
  region: 'india' | 'maharashtra';
}

export const FireMapView: React.FC<FireMapViewProps> = ({ region }) => {
  const [gridCells, setGridCells] = useState<GridCellFeature[]>([]);
  const [boundaryGeoJson, setBoundaryGeoJson] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  // Filters
  const [selectedSensor, setSelectedSensor] = useState<string>('all');
  const [minFrp, setMinFrp] = useState<number>(0);
  const [activeDate, setActiveDate] = useState<string>('all');

  useEffect(() => {
    let mounted = true;
    setLoading(true);

    Promise.all([
      dataService.getGridCells(region),
      region === 'maharashtra' ? dataService.getMaharashtraDisplayBoundary() : Promise.resolve(null),
    ])
      .then(([cells, boundary]) => {
        if (mounted) {
          setGridCells(cells || []);
          setBoundaryGeoJson(boundary);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error('Failed to load map data:', err);
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [region]);

  const mapCenter: [number, number] = region === 'maharashtra' ? [19.2, 76.5] : [22.5, 82.0];
  const mapZoom = region === 'maharashtra' ? 7 : 5;

  const filteredCells = useMemo(() => {
    return gridCells.filter((cell) => {
      if (minFrp > 0 && cell.frp_sum < minFrp) return false;
      return true;
    });
  }, [gridCells, minFrp]);

  const getColor = (frp: number) => {
    if (frp > 500) return '#ef4444'; // Red (Extreme)
    if (frp > 200) return '#f97316'; // Orange-Red (High)
    if (frp > 80) return '#f59e0b';  // Amber (Elevated)
    if (frp > 30) return '#eab308';  // Yellow (Moderate)
    return '#38bdf8';                 // Cyan/Blue (Low)
  };

  return (
    <div className="space-y-4 max-w-7xl mx-auto h-[calc(100vh-6rem)] flex flex-col">
      {/* Map Control Bar */}
      <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <span className="font-semibold text-slate-200 flex items-center gap-1.5">
            <Filter className="w-4 h-4 text-amber-500" /> Layer Filters:
          </span>

          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">Sensor:</span>
            <select
              value={selectedSensor}
              onChange={(e) => setSelectedSensor(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-200 focus:outline-none focus:border-amber-500"
            >
              <option value="all">All Harmonized Sensors</option>
              <option value="MODIS">MODIS C6.1 (1km)</option>
              <option value="VIIRS_SNPP">VIIRS Suomi-NPP (375m)</option>
              <option value="VIIRS_NOAA20">VIIRS NOAA-20 (375m)</option>
              <option value="VIIRS_NOAA21">VIIRS NOAA-21 (375m)</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-slate-400">Min FRP:</span>
            <input
              type="range"
              min="0"
              max="500"
              step="25"
              value={minFrp}
              onChange={(e) => setMinFrp(Number(e.target.value))}
              className="w-24 accent-amber-500 cursor-pointer"
            />
            <span className="font-mono text-amber-400 min-w-12">{minFrp} MW</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-slate-400 font-mono text-[11px]">
            Rendering {filteredCells.length.toLocaleString()} of top active 1km grid cells (highest-density sample)
          </span>
          <span className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-[11px]">
            EPSG:6933 Equal-Area
          </span>
        </div>
      </div>

      {/* Main Map Canvas */}
      <div className="flex-1 rounded-xl overflow-hidden border border-slate-800 relative shadow-2xl bg-slate-950 min-h-[450px]">
        {loading ? (
          <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-slate-950/80 backdrop-blur text-slate-400 gap-2">
            <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-xs">Loading spatial grid layers and administrative boundaries...</p>
          </div>
        ) : null}

        <MapContainer
          key={`${region}-${mapZoom}`}
          center={mapCenter}
          zoom={mapZoom}
          style={{ height: '100%', width: '100%' }}
          zoomControl={true}
        >
          {/* Dark CartoDB Matter Base Map */}
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://openstreetmap.org">OSM</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />

          {/* Maharashtra Administrative Boundary Overlay */}
          {boundaryGeoJson && (
            <GeoJSON
              data={boundaryGeoJson}
              style={{
                color: '#f59e0b',
                weight: 2,
                fillOpacity: 0.05,
                fillColor: '#f59e0b',
                dashArray: '4, 4',
              }}
            />
          )}

          {/* Grid Cell Point Clusters */}
          {filteredCells.map((cell) => {
            const color = getColor(cell.frp_sum);
            return (
              <CircleMarker
                key={cell.grid_id}
                center={[cell.center_latitude, cell.center_longitude]}
                radius={Math.min(10, Math.max(3, Math.sqrt(cell.detection_count) * 2))}
                pathOptions={{
                  fillColor: color,
                  fillOpacity: 0.8,
                  color: color,
                  weight: 1,
                }}
              >
                <Popup>
                  <div className="p-2 space-y-2 text-xs font-sans">
                    <div className="flex items-center justify-between border-b border-slate-700 pb-1.5 gap-3">
                      <span className="font-bold text-amber-400 font-mono flex items-center gap-1">
                        <MapPin className="w-3.5 h-3.5" /> {cell.grid_id}
                      </span>
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                        1km Cell
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 font-mono text-[11px] pt-1">
                      <div>
                        <span className="text-slate-400 text-[10px] block font-sans">Coordinates</span>
                        {cell.center_latitude.toFixed(3)}°N, {cell.center_longitude.toFixed(3)}°E
                      </div>
                      <div>
                        <span className="text-slate-400 text-[10px] block font-sans">Detections</span>
                        <strong className="text-amber-300">{cell.detection_count}</strong> observations
                      </div>
                      <div>
                        <span className="text-slate-400 text-[10px] block font-sans">Total FRP</span>
                        <strong className="text-orange-400">{cell.frp_sum.toFixed(1)} MW</strong>
                      </div>
                      <div>
                        <span className="text-slate-400 text-[10px] block font-sans">Mean Brightness</span>
                        {cell.brightness_mean.toFixed(1)} K
                      </div>
                    </div>

                    <div className="pt-2 border-t border-slate-800 text-[10px] text-slate-400 flex items-center justify-between font-sans">
                      <span>Active Days: {cell.active_dates}</span>
                      <span className="text-emerald-400">NASA FIRMS Provenance</span>
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}
        </MapContainer>

        {/* Map Legend Overlay */}
        <div className="absolute bottom-5 right-5 z-[1000] p-3 rounded-lg bg-slate-900/90 border border-slate-800 shadow-xl backdrop-blur text-xs space-y-2">
          <p className="font-semibold text-slate-200 text-[11px] uppercase tracking-wider">
            Fire Radiative Power (MW)
          </p>
          <div className="space-y-1 font-mono text-[10px] text-slate-300">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500"></span> &gt; 500 MW (Extreme)
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-orange-500"></span> 200 - 500 MW (High)
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-amber-500"></span> 80 - 200 MW (Elevated)
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-yellow-500"></span> 30 - 80 MW (Moderate)
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-sky-400"></span> &lt; 30 MW (Low)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
