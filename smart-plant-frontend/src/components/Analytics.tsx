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
import { Activity, Download } from "lucide-react";
import type { DashboardResponse, Plant } from "../types";

type AnalyticsProps = {
  plants: Plant[];
  dashboard: DashboardResponse | null;
  isLoading: boolean;
  error: string;
  onLoad: (plantId: number, hours: number) => Promise<void>;
};

type ChartPoint = {
  i: number;
  t: string;
  temp: number;
  moisture: number;
  humidity: number;
  light: number;
};

function csvValue(value: string | number | null | undefined) {
  if (value == null) {
    return "";
  }
  const text = String(value);
  if (/[",\n\r]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
}

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

  const lineData = useMemo<ChartPoint[]>(() => {
    if (!dashboard?.history.length) {
      return [];
    }
    return dashboard.history.map((h, i) => ({
      i,
      t: new Date(h.recorded_at).toLocaleString(undefined, { month: "short", day: "numeric" }),
      temp: h.temperature ?? 0,
      moisture: h.moisture ?? 0,
      humidity: h.humidity ?? 0,
      light: h.light ?? 0,
    }));
  }, [dashboard]);

  const currentMetrics = useMemo(() => {
    if (!dashboard?.current) {
      return [];
    }
    return [
      { label: "Moisture", value: dashboard.current.moisture, unit: "%" },
      { label: "Temperature", value: dashboard.current.temperature, unit: "C" },
      { label: "Humidity", value: dashboard.current.humidity, unit: "%" },
      { label: "Light score", value: dashboard.current.light, unit: "score" },
    ];
  }, [dashboard]);

  const selectedPlant = plants.find((plant) => plant.id === selectedPlantId);
  const hasHistory = Boolean(dashboard?.history.length);

  function exportCsv() {
    if (!dashboard?.history.length || selectedPlantId == null) {
      return;
    }
    const csv = [
      ["recorded_at", "temperature", "moisture", "humidity", "light_score"],
      ...dashboard.history.map((point) => [
        point.recorded_at,
        point.temperature,
        point.moisture,
        point.humidity,
        point.light,
      ]),
    ]
      .map((row) => row.map(csvValue).join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `analytics-plant-${selectedPlantId}-${hours}h.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="analytics-page">
      <div className="page-head dashboard-head">
        <div>
          <h1 className="page-title">Analytics</h1>
          <p className="muted page-lead">Historical sensor data for the selected plant.</p>
        </div>
        <div className="analytics-actions">
          <button
            type="button"
            className="btn-primary"
            onClick={exportCsv}
            disabled={!hasHistory || selectedPlantId == null}
            title={hasHistory ? "Export loaded history as CSV" : "Load history before exporting"}
          >
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
          <option value={720}>Last 30 days</option>
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
      <p className="muted small">
        Showing {selectedPlant?.name ?? "the selected plant"} for the selected range. Light score is normalized from the
        Arduino LDR reading; it is not lux.
      </p>

      {error ? <div className="error">{error}</div> : null}

      {plants.length === 0 ? (
        <div className="card">
          <p className="muted">Create a plant and attach a sensor to see analytics.</p>
        </div>
      ) : null}

      {currentMetrics.length > 0 ? (
        <div className="stats-row four">
          {currentMetrics.map((m) => (
            <div key={m.label} className="card stat-tile">
              <p className="muted small">{m.label}</p>
              <p className="stat-big">{m.value ?? "--"}</p>
              <p className="muted small">{m.unit}</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="card">
          <p className="muted">No latest sensor values for this plant yet.</p>
        </div>
      )}

      <div className="analytics-charts">
        <MetricLineChart
          color="#f97316"
          data={lineData}
          dataKey="temp"
          name="C"
          title="Temperature"
        />
        <MetricAreaChart
          color="#3b82f6"
          data={lineData}
          dataKey="moisture"
          name="%"
          title="Soil moisture"
        />
        <MetricAreaChart
          color="#14b8a6"
          data={lineData}
          dataKey="humidity"
          name="%"
          title="Humidity"
        />
        <MetricLineChart
          color="#eab308"
          data={lineData}
          dataKey="light"
          name="score"
          title="Light score"
        />
      </div>

      <div className="card">
        <h3 className="section-title">History points</h3>
        <p className="muted">Samples in range: {dashboard?.history.length ?? 0}</p>
        <p className="muted">Last update: {dashboard?.last_updated_at ?? "--"}</p>
      </div>
    </div>
  );
}

type MetricChartProps = {
  color: string;
  data: ChartPoint[];
  dataKey: keyof Pick<ChartPoint, "temp" | "moisture" | "humidity" | "light">;
  name: string;
  title: string;
};

function MetricLineChart({ color, data, dataKey, name, title }: MetricChartProps) {
  return (
    <div className="card chart-card">
      <div className="chart-head">
        <Activity size={18} color={color} />
        <h3>{title}</h3>
      </div>
      {data.length === 0 ? (
        <p className="muted">No history for this range.</p>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="t" tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey={dataKey} name={name} stroke={color} strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

function MetricAreaChart({ color, data, dataKey, name, title }: MetricChartProps) {
  return (
    <div className="card chart-card">
      <div className="chart-head">
        <Activity size={18} color={color} />
        <h3>{title}</h3>
      </div>
      {data.length === 0 ? (
        <p className="muted">No history for this range.</p>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="t" tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip />
            <Area type="monotone" dataKey={dataKey} name={name} stroke={color} fill={color} fillOpacity={0.25} />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
