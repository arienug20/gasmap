// TypeScript types for GasMap

export interface Chemical {
  cas_number: string;
  name: string;
  synonyms: string | null;
  formula: string | null;
  molecular_weight: number;
  boiling_point: number | null;
  density_gas: number | null;
  is_heavier_than_air: boolean;
  gas_category: string | null;
  erpg_1: number | null;
  erpg_2: number | null;
  erpg_3: number | null;
  idlh: number | null;
  pel: number | null;
  tlv_twa: number | null;
}

export interface SimulationRequest {
  chemical_cas: string;
  model: 'gaussian_plume' | 'gaussian_puff' | 'heavy_gas';
  emission_rate?: number;
  total_mass?: number;
  release_height: number;
  wind_speed: number;
  stability_class: string;
  terrain: string;
  ambient_temp: number;
  grid_resolution: number;
  grid_size_x: number;
  grid_size_y: number;
  release_density?: number;
}

export interface SimulationResult {
  status: string;
  model: string;
  chemical: { cas: string; name: string; MW: number };
  max_concentration_ppm: number;
  thresholds: Record<string, number>;
  grid_resolution: number;
  grid_shape: [number, number];
  computation_time_ms: number;
}

export interface WeatherPreset {
  name: string;
  wind_speed: number;
  stability_class: string;
  temperature: number;
  humidity: number;
  is_daytime: boolean;
}
