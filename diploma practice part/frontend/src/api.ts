/**
 * API client: central base URL and JSON helpers. Token is read from localStorage.
 * - In dev, leave VITE_API_URL empty to use the Vite proxy to the backend.
 * - Or set VITE_API_URL to the full API root, e.g. http://127.0.0.1:8001/api
 */
const API_BASE = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') ?? '';

function apiUrl(path: string): string {
  if (!API_BASE) {
    return path;
  }
  if (path.startsWith('/api/') && API_BASE.replace(/\/$/, '').endsWith('/api')) {
    return `${API_BASE.replace(/\/$/, '')}${path.slice(4)}`;
  }
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE.replace(/\/$/, '')}${p}`;
}

function authHeaders(): HeadersInit {
  const t = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(t ? { Authorization: `Bearer ${t}` } : {}),
  };
}

export async function apiGet<T>(path: string): Promise<T> {
  const r = await fetch(apiUrl(path), { headers: authHeaders() });
  if (r.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    throw new Error('UNAUTHORIZED');
  }
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    throw new Error((err as { detail?: string })?.detail || r.statusText);
  }
  return r.json() as Promise<T>;
}

export async function apiPost<T, B = unknown>(path: string, body: B): Promise<T> {
  const r = await fetch(apiUrl(path), {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify(body),
  });
  if (r.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    throw new Error('UNAUTHORIZED');
  }
  if (!r.ok) {
    const err = await r.json().catch(() => ({}));
    const d = (err as { detail?: string | { msg?: string }[] })?.detail;
    const msg = typeof d === 'string' ? d : r.statusText;
    throw new Error(msg);
  }
  return r.json() as Promise<T>;
}

export type User = {
  id: number;
  name: string;
  email: string;
  role: string;
};

export type Plant = {
  id: number;
  name: string;
  species: string | null;
  location: string | null;
  is_active: boolean;
};

export type Reading = {
  id: number;
  recorded_at: string;
  soil_moisture_percent: number | null;
  temperature: number | null;
  humidity: number | null;
  light_percent: number | null;
};

export type PlantDashboard = {
  plant_id: number;
  plant_name: string;
  latest: {
    soil_moisture_percent: number | null;
    temperature: number | null;
    humidity: number | null;
    light_percent: number | null;
    health_status: string;
    recorded_at: string | null;
    abnormal_codes: string[];
  } | null;
  recent_readings_count: number;
  open_alerts: number;
};

export type AlertRow = {
  id: number;
  plant_id: number;
  severity: string;
  message: string;
  status: string;
  created_at: string;
};

export type RecItem = { id: number; text: string; explanation: string | null; created_at: string };
