import React, { useState, useEffect, useCallback } from 'react';
import { Chemical, SimulationResult, WeatherPreset } from '../types';
import { chemicalsApi, weatherApi, simulationsApi } from '../api/client';

const STABILITY_CLASSES = ['A', 'B', 'C', 'D', 'E', 'F'];
const MODELS = [
  { value: 'gaussian_plume', label: 'Gaussian Plume (Continuous)' },
  { value: 'gaussian_puff', label: 'Gaussian Puff (Instantaneous)' },
  { value: 'heavy_gas', label: 'Heavy Gas (Britter-McQuaid)' },
];

export default function App() {
  const [chemicals, setChemicals] = useState<Chemical[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedChemical, setSelectedChemical] = useState<Chemical | null>(null);
  const [presets, setPresets] = useState<WeatherPreset[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<string>('');
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [model, setModel] = useState('gaussian_plume');
  const [emissionRate, setEmissionRate] = useState(10);
  const [totalMass, setTotalMass] = useState(1000);
  const [releaseHeight, setReleaseHeight] = useState(0);
  const [windSpeed, setWindSpeed] = useState(5);
  const [stabilityClass, setStabilityClass] = useState('D');
  const [terrain, setTerrain] = useState('rural');
  const [gridSize, setGridSize] = useState(5000);

  useEffect(() => {
    chemicalsApi.list().then(r => setChemicals(r.data.chemicals)).catch(() => {});
    weatherApi.presets().then(r => setPresets(r.data.presets)).catch(() => {});
  }, []);

  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) {
      const r = await chemicalsApi.list();
      setChemicals(r.data.chemicals);
      return;
    }
    const r = await chemicalsApi.search(searchQuery);
    setChemicals(r.data.chemicals);
  }, [searchQuery]);

  const handlePreset = (name: string) => {
    setSelectedPreset(name);
    const preset = presets.find(p => p.name === name);
    if (preset) {
      setWindSpeed(preset.wind_speed);
      setStabilityClass(preset.stability_class);
    }
  };

  const handleRun = async () => {
    if (!selectedChemical) { setError('Select a chemical first'); return; }
    setLoading(true);
    setError(null);
    try {
      const payload: Record<string, unknown> = {
        chemical_cas: selectedChemical.cas_number,
        model,
        emission_rate: emissionRate,
        release_height: releaseHeight,
        wind_speed: windSpeed,
        stability_class: stabilityClass,
        terrain,
        grid_resolution: 100,
        grid_size_x: gridSize,
        grid_size_y: gridSize * 0.4,
      };
      if (model === 'gaussian_puff') payload.total_mass = totalMass;
      if (model === 'heavy_gas' && selectedChemical.density_gas) {
        payload.release_density = selectedChemical.density_gas;
      }
      const r = await simulationsApi.run(payload);
      setResult(r.data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Simulation failed');
    } finally {
      setLoading(false);
    }
  };

  const formatConcentration = (val: number) => {
    if (val >= 1e6) return `${(val / 1e6).toFixed(1)}M`;
    if (val >= 1e3) return `${(val / 1e3).toFixed(1)}K`;
    return val.toFixed(2);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-blue-700 text-white px-6 py-4 shadow">
        <h1 className="text-2xl font-bold">GasMap — Gas Dispersion Visualizer</h1>
        <p className="text-blue-200 text-sm">Process Safety Engineering Tool</p>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel: Scenario Builder */}
        <div className="lg:col-span-1 space-y-4">
          {/* Chemical Selector */}
          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="font-semibold text-lg mb-3">🧪 Chemical</h2>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                placeholder="Search chemicals..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSearch()}
                className="flex-1 border rounded px-3 py-2 text-sm"
              />
              <button onClick={handleSearch} className="bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700">
                Search
              </button>
            </div>
            <select
              value={selectedChemical?.cas_number || ''}
              onChange={e => {
                const c = chemicals.find(ch => ch.cas_number === e.target.value);
                setSelectedChemical(c || null);
              }}
              className="w-full border rounded px-3 py-2 text-sm"
            >
              <option value="">-- Select Chemical --</option>
              {chemicals.map(c => (
                <option key={c.cas_number} value={c.cas_number}>
                  {c.name} ({c.formula || c.cas_number})
                </option>
              ))}
            </select>
            {selectedChemical && (
              <div className="mt-2 text-xs text-gray-600 space-y-1">
                <p>MW: {selectedChemical.molecular_weight} g/mol</p>
                <p>Category: {selectedChemical.gas_category || 'N/A'}</p>
                <p>Heavier than air: {selectedChemical.is_heavier_than_air ? 'Yes' : 'No'}</p>
              </div>
            )}
          </div>

          {/* Release Parameters */}
          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="font-semibold text-lg mb-3">💨 Release Parameters</h2>
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium">Dispersion Model</label>
                <select value={model} onChange={e => setModel(e.target.value)} className="w-full border rounded px-3 py-2 text-sm mt-1">
                  {MODELS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
                </select>
              </div>
              {model === 'gaussian_puff' ? (
                <div>
                  <label className="text-sm font-medium">Total Mass (kg)</label>
                  <input type="number" value={totalMass} onChange={e => setTotalMass(+e.target.value)}
                    className="w-full border rounded px-3 py-2 text-sm mt-1" />
                </div>
              ) : (
                <div>
                  <label className="text-sm font-medium">Emission Rate (kg/s)</label>
                  <input type="number" value={emissionRate} onChange={e => setEmissionRate(+e.target.value)}
                    className="w-full border rounded px-3 py-2 text-sm mt-1" />
                </div>
              )}
              <div>
                <label className="text-sm font-medium">Release Height (m)</label>
                <input type="number" value={releaseHeight} onChange={e => setReleaseHeight(+e.target.value)}
                  className="w-full border rounded px-3 py-2 text-sm mt-1" />
              </div>
            </div>
          </div>

          {/* Weather */}
          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="font-semibold text-lg mb-3">🌤️ Weather</h2>
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium">Weather Preset</label>
                <select value={selectedPreset} onChange={e => handlePreset(e.target.value)} className="w-full border rounded px-3 py-2 text-sm mt-1">
                  <option value="">-- Custom --</option>
                  {presets.map(p => <option key={p.name} value={p.name}>{p.name}</option>)}
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">Wind Speed (m/s)</label>
                <input type="number" step="0.1" value={windSpeed} onChange={e => setWindSpeed(+e.target.value)}
                  className="w-full border rounded px-3 py-2 text-sm mt-1" />
              </div>
              <div>
                <label className="text-sm font-medium">Stability Class</label>
                <select value={stabilityClass} onChange={e => setStabilityClass(e.target.value)} className="w-full border rounded px-3 py-2 text-sm mt-1">
                  {STABILITY_CLASSES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">Terrain</label>
                <select value={terrain} onChange={e => setTerrain(e.target.value)} className="w-full border rounded px-3 py-2 text-sm mt-1">
                  <option value="rural">Rural</option>
                  <option value="urban">Urban</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">Grid Size (m)</label>
                <input type="number" value={gridSize} onChange={e => setGridSize(+e.target.value)}
                  className="w-full border rounded px-3 py-2 text-sm mt-1" />
              </div>
            </div>
          </div>

          {/* Run Button */}
          <button
            onClick={handleRun}
            disabled={loading}
            className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 text-lg"
          >
            {loading ? '⏳ Computing...' : '▶ Run Simulation'}
          </button>
        </div>

        {/* Right Panel: Results */}
        <div className="lg:col-span-2 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">{error}</div>
          )}

          {result && (
            <>
              {/* Summary Card */}
              <div className="bg-white rounded-lg shadow p-4">
                <h2 className="font-semibold text-lg mb-3">📊 Results Summary</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-blue-50 rounded p-3">
                    <p className="text-xs text-gray-500">Chemical</p>
                    <p className="font-semibold">{result.chemical.name}</p>
                  </div>
                  <div className="bg-blue-50 rounded p-3">
                    <p className="text-xs text-gray-500">Model</p>
                    <p className="font-semibold">{result.model}</p>
                  </div>
                  <div className="bg-orange-50 rounded p-3">
                    <p className="text-xs text-gray-500">Max Concentration</p>
                    <p className="font-semibold text-orange-700">{formatConcentration(result.max_concentration_ppm)} ppm</p>
                  </div>
                  <div className="bg-green-50 rounded p-3">
                    <p className="text-xs text-gray-500">Computation Time</p>
                    <p className="font-semibold text-green-700">{result.computation_time_ms} ms</p>
                  </div>
                </div>
              </div>

              {/* Thresholds Table */}
              <div className="bg-white rounded-lg shadow p-4">
                <h2 className="font-semibold text-lg mb-3">🚨 Emergency Thresholds</h2>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="text-left px-3 py-2">Threshold</th>
                      <th className="text-right px-3 py-2">Value (ppm)</th>
                      <th className="text-center px-3 py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(result.thresholds).map(([key, value]) => {
                      const exceeded = result.max_concentration_ppm >= value;
                      return (
                        <tr key={key} className="border-t">
                          <td className="px-3 py-2 font-medium">{key.replace(/_/g, ' ').toUpperCase()}</td>
                          <td className="text-right px-3 py-2">{formatConcentration(value)}</td>
                          <td className="text-center px-3 py-2">
                            <span className={`px-2 py-1 rounded text-xs font-bold ${
                              exceeded ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                            }`}>
                              {exceeded ? 'EXCEEDED' : 'SAFE'}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Chemical Info */}
              {selectedChemical && (
                <div className="bg-white rounded-lg shadow p-4">
                  <h2 className="font-semibold text-lg mb-3">📋 Chemical Properties</h2>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                    <div><span className="text-gray-500">CAS:</span> {selectedChemical.cas_number}</div>
                    <div><span className="text-gray-500">Formula:</span> {selectedChemical.formula || 'N/A'}</div>
                    <div><span className="text-gray-500">MW:</span> {selectedChemical.molecular_weight} g/mol</div>
                    <div><span className="text-gray-500">Boiling Pt:</span> {selectedChemical.boiling_point ?? 'N/A'} °C</div>
                    <div><span className="text-gray-500">Gas Density:</span> {selectedChemical.density_gas ?? 'N/A'} kg/m³</div>
                    <div><span className="text-gray-500">Category:</span> {selectedChemical.gas_category || 'N/A'}</div>
                  </div>
                </div>
              )}

              {/* Simulation Parameters */}
              <div className="bg-white rounded-lg shadow p-4">
                <h2 className="font-semibold text-lg mb-3">⚙️ Simulation Parameters</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                  <div><span className="text-gray-500">Grid:</span> {result.grid_resolution}×{result.grid_resolution}</div>
                  <div><span className="text-gray-500">Wind:</span> {windSpeed} m/s</div>
                  <div><span className="text-gray-500">Stability:</span> {stabilityClass}</div>
                  <div><span className="text-gray-500">Terrain:</span> {terrain}</div>
                </div>
              </div>
            </>
          )}

          {!result && !error && (
            <div className="bg-white rounded-lg shadow p-12 text-center text-gray-400">
              <p className="text-5xl mb-4">🧪</p>
              <p className="text-lg font-medium">Configure your scenario and run a simulation</p>
              <p className="text-sm mt-2">Select a chemical, set release parameters and weather, then click Run</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
