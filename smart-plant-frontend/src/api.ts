import type {
  Alert,
  AuthResponse,
  DashboardResponse,
  LoginPayload,
  Plant,
  RegisterPayload,
  Sensor,
  SensorProvisionResponse,
  User,
  AdminLog,
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

const jsonHeaders = {
  "Content-Type": "application/json",
};

async function apiFetch<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers: Record<string, string> = {
    ...jsonHeaders,
    ...((options.headers as Record<string, string> | undefined) ?? {}),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string | Array<{ msg?: string }> };
      if (typeof payload.detail === "string") {
        message = payload.detail;
      } else if (Array.isArray(payload.detail) && payload.detail[0]?.msg) {
        message = payload.detail[0].msg;
      }
    } catch {
      // Ignore non-JSON error payloads.
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}

async function uploadFetch<T>(path: string, formData: FormData, token: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string | Array<{ msg?: string }> };
      if (typeof payload.detail === "string") {
        message = payload.detail;
      } else if (Array.isArray(payload.detail) && payload.detail[0]?.msg) {
        message = payload.detail[0].msg;
      }
    } catch {
      // Ignore non-JSON error payloads.
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}

export async function register(payload: RegisterPayload): Promise<void> {
  await apiFetch("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function login(payload: LoginPayload): Promise<AuthResponse> {
  return apiFetch<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getMe(token: string) {
  return apiFetch("/auth/me", { method: "GET" }, token);
}

function mapPlant(raw: Record<string, unknown>): Plant {
  const healthCandidate = raw.health ?? raw.health_score ?? raw.healthScore ?? raw.score;
  const numericHealth =
    typeof healthCandidate === "number"
      ? healthCandidate
      : typeof healthCandidate === "string"
      ? Number(healthCandidate)
      : undefined;

  const rawImageUrl = typeof raw.image_url === "string" ? raw.image_url : undefined;

  return {
    id: Number(raw.id),
    name: String(raw.name ?? "Unnamed plant"),
    species: typeof raw.species === "string" ? raw.species : undefined,
    location: typeof raw.location === "string" ? raw.location : undefined,
    description: typeof raw.description === "string" ? raw.description : undefined,
    image_url: resolveImageUrl(rawImageUrl),
    health: Number.isFinite(numericHealth) ? numericHealth : undefined,
    notes: typeof raw.notes === "string" ? raw.notes : undefined,
  };
}

function resolveImageUrl(value: string | undefined) {
  if (!value) {
    return undefined;
  }
  if (/^(https?:|data:|blob:)/.test(value)) {
    return value;
  }
  if (value.startsWith("/")) {
    return `${new URL(API_BASE_URL).origin}${value}`;
  }
  return value;
}

export async function getPlant(token: string, plantId: number): Promise<Plant> {
  const raw = await apiFetch<Record<string, unknown>>(`/plants/${plantId}`, { method: "GET" }, token);
  return mapPlant(raw);
}

export async function getPlants(token: string): Promise<Plant[]> {
  const items = await apiFetch<Record<string, unknown>[]>(
    "/plants",
    { method: "GET" },
    token
  );
  return items.map(mapPlant);
}

export async function createPlant(
  token: string,
  payload: { name: string; species?: string; location?: string; description?: string }
): Promise<Plant> {
  const created = await apiFetch<Record<string, unknown>>(
    "/plants",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    token
  );
  return mapPlant(created);
}

export async function uploadPlantPhoto(token: string, plantId: number, file: File): Promise<Plant> {
  const formData = new FormData();
  formData.append("file", file);
  const updated = await uploadFetch<Record<string, unknown>>(`/plants/${plantId}/photo`, formData, token);
  return mapPlant(updated);
}

export async function getPlantDashboard(
  token: string,
  plantId: number,
  hours = 24
): Promise<DashboardResponse> {
  return apiFetch<DashboardResponse>(
    `/dashboard/plants/${plantId}?hours=${hours}`,
    { method: "GET" },
    token
  );
}

export async function getAlerts(token: string): Promise<Alert[]> {
  return apiFetch<Alert[]>("/alerts", { method: "GET" }, token);
}

export async function getAlert(token: string, alertId: number): Promise<Alert> {
  return apiFetch<Alert>(`/alerts/${alertId}`, { method: "GET" }, token);
}

export async function transitionAlert(
  token: string,
  alertId: number,
  toStatus: "viewed" | "acknowledged" | "resolved" | "closed",
  note?: string
): Promise<void> {
  await apiFetch(`/alerts/${alertId}/transition`, {
    method: "POST",
    body: JSON.stringify({ to_status: toStatus, note: note ?? null }),
  }, token);
}

export async function getSensors(token: string): Promise<Sensor[]> {
  return apiFetch<Sensor[]>("/sensors", { method: "GET" }, token);
}

export async function createSensor(token: string, deviceId: string, type = "multi"): Promise<SensorProvisionResponse> {
  return apiFetch<SensorProvisionResponse>(
    "/sensors",
    {
      method: "POST",
      body: JSON.stringify({ device_id: deviceId, type }),
    },
    token
  );
}

export async function attachSensor(token: string, sensorId: number, plantId: number): Promise<Sensor> {
  return apiFetch<Sensor>(
    `/sensors/${sensorId}/attach`,
    {
      method: "POST",
      body: JSON.stringify({ plant_id: plantId }),
    },
    token
  );
}

export async function assignSensor(token: string, sensorId: number, userId: number): Promise<Sensor> {
  return apiFetch<Sensor>(
    `/sensors/${sensorId}/assign`,
    {
      method: "POST",
      body: JSON.stringify({ user_id: userId }),
    },
    token
  );
}

export async function detachSensor(token: string, sensorId: number): Promise<Sensor> {
  return apiFetch<Sensor>(`/sensors/${sensorId}/detach`, { method: "POST" }, token);
}

export async function rotateSensorToken(token: string, sensorId: number): Promise<SensorProvisionResponse> {
  return apiFetch<SensorProvisionResponse>(`/sensors/${sensorId}/rotate-token`, { method: "POST" }, token);
}

export async function getAdminUsers(token: string): Promise<User[]> {
  return apiFetch<User[]>("/admin/users", { method: "GET" }, token);
}

export async function getAdminSensors(token: string): Promise<Sensor[]> {
  return apiFetch<Sensor[]>("/admin/sensors", { method: "GET" }, token);
}

export async function getAdminAlerts(token: string): Promise<Alert[]> {
  return apiFetch<Alert[]>("/admin/alerts", { method: "GET" }, token);
}

export async function getAdminLogs(token: string): Promise<AdminLog[]> {
  return apiFetch<AdminLog[]>("/admin/logs", { method: "GET" }, token);
}

export { API_BASE_URL };

