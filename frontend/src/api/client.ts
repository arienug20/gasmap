import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({ baseURL: API_BASE });

export const chemicalsApi = {
  list: (page = 1, perPage = 50) =>
    api.get('/chemicals', { params: { page, per_page: perPage } }),
  search: (q: string) =>
    api.get('/chemicals/search', { params: { q } }),
  get: (cas: string) =>
    api.get(`/chemicals/${cas}`),
  thresholds: (cas: string) =>
    api.get(`/chemicals/${cas}/thresholds`),
  categories: () =>
    api.get('/chemicals/categories'),
};

export const weatherApi = {
  presets: () => api.get('/weather/presets'),
  stabilityClass: (params: { wind_speed: number; is_daytime: boolean; solar_radiation?: string; cloud_cover?: number }) =>
    api.get('/weather/stability-class', { params }),
};

export const simulationsApi = {
  run: (data: Record<string, unknown>) => api.post('/simulations/run', data),
};

export default api;
