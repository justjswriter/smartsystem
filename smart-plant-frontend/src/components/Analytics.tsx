import { useEffect, useMemo, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Activity, Download, Filter } from "lucide-react";
import type { DashboardResponse, Plant } from "../types";

type AnalyticsProps = {
  plants: Plant[];
  dashboard: DashboardResponse | null;
  isLoading: boolean;
  error: string;
  onLoad: (plantId: number, hours: number) => Promise<void>;
};

export function Analytics({ plants, dashboard, isLoading, error, onLoad }: AnalyticsProps) {
  const [selectedPlantId, setSelectedPlantId] = useState<number | null>(plants[0]?.id ?? null);
  const [hours, setHours] = useState(168);

  useEffect(() => {
    if (plants.length === 0) {
      return;
    }
    if (selectedPlantId == null || !plants.some((p) => p.id === selectedPlantId)) {
      setSelectedPlantId(plants[0].id);
    }
  }, [plants, selectedPlantId]);

  const lineData = useMemo(() => {
    if (!dashboard?.history.length) {
      return [];
    }
    return dashboard.history.map((h, i) => ({
      i,
      t: new Date(h.recorded_at).toLocaleString(undefined, { month: "short", day: "numeric" }),
      temp: h.temperature ?? 0,
      moisture: h.moisture ?? 0,
      light: h.light ?? 0,
    }));
  }, [dashboard]);

  const currentMetrics = useMemo(() => {
    if (!dashboard?.current) {
      return [];
    }
    return [
      { label: "Moisture", value: dashboard.current.moisture, unit: "%" },
      { label: "Temperature", value: dashboard.current.temperature, unit: "°C" },
      { label: "Humidity", value: dashboard.current.humidity, unit: "%" },
      { label: "Light", value: dashboard.current.light, unit: "lux" },
    ];
  }, [dashboard]);

  return (
    <div className="analytics-page">
      <div className="page-head dashboard-head">
        <div>
          <h1 className="page-title">Analytics</h1>
          <p className="muted page-lead">Historical sensor data for the selected plant.</p>
        </div>
        <div className="analytics-actions">
          <button type="button" className="btn-secondary" disabled title="Disabled in this prototype">
            <Filter size={18} />
            Filters
          </button>
          <button type="button" className="btn-primary" disabled title="Disabled in this prototype">
            <Download size={18} />
            Export
          </button>
        </div>
      </div>

      <div className="toolbar dashboard-toolbar">
        <select
          value={selectedPlantId ?? ""}
          onChange={(e) => setSelectedPlantId(Number(e.target.value))}
          disabled={plants.length === 0}
        >
          {plants.length === 0 ? <option value="">No plants</option> : null}
          {plants.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        <select value={hours} onChange={(e) => setHours(Number(e.target.value))}>
          <option value={24}>Last 24h</option>
          <option value={72}>Last 3 days</option>
          <option value={168}>Last 7 days</option>
        </select>
        <button
          type="button"
          className="btn-primary"
          onClick={() => selectedPlantId && onLoad(selectedPlantId, hours)}
          disabled={!selectedPlantId || isLoading}
        >
          {isLoading ? "Loading..." : "Load"}
        </button>
      </div>

      {error ? <div className="error">{error}</div> : null}

      <div className="stats-row four">
        {currentMetrics.map((m) => (
          <div key={m.label} className="card stat-tile">
            <p className="muted small">{m.label}</p>
            <p className="stat-big">{m.value ?? "—"}</p>
            <p className="muted small">{m.unit}</p>
          </div>
        ))}
      </div>

      <div className="analytics-charts">
        <div className="card chart-card">
          <div className="chart-head">
            <Activity size={18} color="#ea580c" />
            <h3>Temperature</h3>
          </div>
          {lineData.length === 0 ? (
            <p className="muted">No history for this range.</p>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={lineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="t" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="temp" name="°C" stroke="#f97316" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
        <div className="card chart-card">
          <div className="chart-head">
            <Activity size={18} color="#2563eb" />
            <h3>Soil moisture</h3>
          </div>
          {lineData.length === 0 ? (
            <p className="muted">No history for this range.</p>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={lineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="t" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Area type="monotone" dataKey="moisture" name="%" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.25} />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="card">
        <h3 className="section-title">History points</h3>
        <p className="muted">Samples in range: {dashboard?.history.length ?? 0}</p>
        <p className="muted">Last update: {dashboard?.last_updated_at ?? "—"}</p>
      </div>
    </div>
  );
}
