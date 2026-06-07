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
import { CustomSelect } from "./CustomSelect";
import { useI18n } from "../i18n";
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
  recordedAt: string;
  temp: number;
  moisture: number;
  humidity: number;
  light: number;
};

const MAX_CHART_POINTS = 500;

function downsamplePoints<T>(items: T[], maxPoints = MAX_CHART_POINTS): T[] {
  if (items.length <= maxPoints) {
    return items;
  }
  const step = (items.length - 1) / (maxPoints - 1);
  return Array.from({ length: maxPoints }, (_, index) => items[Math.round(index * step)]);
}

function escapeHtml(value: string | number | null | undefined) {
  if (value == null) {
    return "";
  }
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function pad(value: number) {
  return String(value).padStart(2, "0");
}

function exportDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function metricClass(metric: "temperature" | "moisture" | "humidity" | "light", value: number | null | undefined) {
  if (value == null) {
    return "empty";
  }
  if (metric === "temperature") {
    if (value < 16 || value > 34) return "bad";
    if (value < 18 || value > 30) return "warn";
    return "ok";
  }
  if (metric === "moisture") {
    if (value < 20 || value > 85) return "bad";
    if (value < 35 || value > 75) return "warn";
    return "ok";
  }
  if (metric === "humidity") {
    if (value < 25 || value > 85) return "bad";
    if (value < 40 || value > 75) return "warn";
    return "ok";
  }
  if (value < 20 || value > 260) return "bad";
  if (value < 40 || value > 180) return "warn";
  return "ok";
}

function metricCell(metric: "temperature" | "moisture" | "humidity" | "light", value: number | null | undefined) {
  return `<td class="${metricClass(metric, value)}">${escapeHtml(value ?? "")}</td>`;
}

export function Analytics({ plants, dashboard, isLoading, error, onLoad }: AnalyticsProps) {
  const { t, formatDate, formatDateTime } = useI18n();
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
    return downsamplePoints(dashboard.history).map((h, i) => ({
      i,
      t: formatDate(h.recorded_at),
      recordedAt: h.recorded_at,
      temp: h.temperature ?? 0,
      moisture: h.moisture ?? 0,
      humidity: h.humidity ?? 0,
      light: h.light ?? 0,
    }));
  }, [dashboard, formatDate]);

  const currentMetrics = useMemo(() => {
    if (!dashboard?.current) {
      return [];
    }
    return [
      { label: t("dashboard.moisture"), value: dashboard.current.moisture, unit: "%" },
      { label: t("plant.temperature"), value: dashboard.current.temperature, unit: t("units.temperature") },
      { label: t("plant.humidity"), value: dashboard.current.humidity, unit: "%" },
      { label: t("dashboard.lightScore"), value: dashboard.current.light, unit: t("units.light") },
    ];
  }, [dashboard, t]);

  const hasHistory = Boolean(dashboard?.history.length);

  function exportCsv() {
    if (!dashboard?.history.length || selectedPlantId == null) {
      return;
    }
    const rows = dashboard.history
      .map(
        (point) => `
          <tr>
            <td>${escapeHtml(exportDate(point.recorded_at))}</td>
            ${metricCell("temperature", point.temperature)}
            ${metricCell("moisture", point.moisture)}
            ${metricCell("humidity", point.humidity)}
            ${metricCell("light", point.light)}
          </tr>`
      )
      .join("");
    const html = `<!doctype html>
      <html>
        <head>
          <meta charset="utf-8" />
          <style>
            table { border-collapse: collapse; font-family: Arial, sans-serif; }
            th, td { border: 1px solid #999; padding: 6px 8px; white-space: nowrap; }
            th { background: #d9ead3; font-weight: 700; }
            .ok { background: #d9ead3; }
            .warn { background: #fff2cc; }
            .bad { background: #f4cccc; }
            .empty { background: #eeeeee; }
          </style>
        </head>
        <body>
          <table>
            <thead>
              <tr>
                <th>Recorded at</th>
                <th>Temperature (C)<br />Normal: 18-30</th>
                <th>Soil moisture (%)<br />Normal: 35-75</th>
                <th>Air humidity (%)<br />Normal: 40-75</th>
                <th>Light level<br />Normal: 40-180</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </body>
      </html>`;

    const blob = new Blob(["\ufeff", html], { type: "application/vnd.ms-excel;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `analytics-plant-${selectedPlantId}-${hours}h.xls`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="analytics-page">
      <div className="page-head dashboard-head">
        <div>
          <h1 className="page-title">{t("analytics.title")}</h1>
          <p className="muted page-lead">{t("analytics.subtitle")}</p>
        </div>
        <div className="analytics-actions">
          <button
            type="button"
            className="btn-primary"
            onClick={exportCsv}
            disabled={!hasHistory || selectedPlantId == null}
            title={hasHistory ? t("analytics.exportTitle") : t("analytics.exportDisabled")}
          >
            <Download size={18} />
            {t("common.export")}
          </button>
        </div>
      </div>

      <div className="toolbar dashboard-toolbar">
        <CustomSelect
          value={String(selectedPlantId ?? "")}
          onChange={(value) => setSelectedPlantId(Number(value))}
          disabled={plants.length === 0}
          options={
            plants.length === 0
              ? [{ value: "", label: t("plants.title") }]
              : plants.map((p) => ({ value: String(p.id), label: p.name }))
          }
        />
        <CustomSelect
          value={String(hours)}
          onChange={(value) => setHours(Number(value))}
          options={[
            { value: "24", label: t("analytics.last24h") },
            { value: "72", label: t("analytics.last3d") },
            { value: "168", label: t("analytics.last7d") },
            { value: "720", label: t("analytics.last30d") },
          ]}
        />
        <button
          type="button"
          className="btn-primary"
          onClick={() => selectedPlantId && onLoad(selectedPlantId, hours)}
          disabled={!selectedPlantId || isLoading}
        >
          {isLoading ? t("common.loading") : t("common.load")}
        </button>
      </div>
      {error ? <div className="error">{error}</div> : null}

      {plants.length === 0 ? (
        <div className="card">
          <p className="muted">{t("analytics.noPlants")}</p>
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
          <p className="muted">{t("analytics.noLatest")}</p>
        </div>
      )}

      <div className="analytics-charts">
        <MetricLineChart
          color="#f97316"
          data={lineData}
          dataKey="temp"
          name={t("units.temperature")}
          title={t("plant.temperature")}
        />
        <MetricAreaChart
          color="#3b82f6"
          data={lineData}
          dataKey="moisture"
          name="%"
          title={t("plant.soilMoisture")}
        />
        <MetricAreaChart
          color="#14b8a6"
          data={lineData}
          dataKey="humidity"
          name="%"
          title={t("plant.humidity")}
        />
        <MetricLineChart
          color="#eab308"
          data={lineData}
          dataKey="light"
          name={t("units.light")}
          title={t("dashboard.lightScore")}
        />
      </div>

      <div className="card">
        <h3 className="section-title">{t("analytics.historyPoints")}</h3>
        <p className="muted">{t("analytics.samplesInRange", { count: dashboard?.history.length ?? 0 })}</p>
        <p className="muted">{t("analytics.lastUpdate")}: {dashboard?.last_updated_at ? formatDateTime(dashboard.last_updated_at) : "--"}</p>
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
  const { t, formatDate } = useI18n();
  return (
    <div className="card chart-card">
      <div className="chart-head">
        <Activity size={18} color={color} />
        <h3>{title}</h3>
      </div>
      {data.length === 0 ? (
        <p className="muted">{t("analytics.noHistory")}</p>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="recordedAt" tick={{ fontSize: 10 }} tickFormatter={(value) => formatDate(String(value))} />
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
  const { t, formatDate } = useI18n();
  return (
    <div className="card chart-card">
      <div className="chart-head">
        <Activity size={18} color={color} />
        <h3>{title}</h3>
      </div>
      {data.length === 0 ? (
        <p className="muted">{t("analytics.noHistory")}</p>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="recordedAt" tick={{ fontSize: 10 }} tickFormatter={(value) => formatDate(String(value))} />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip />
            <Area type="monotone" dataKey={dataKey} name={name} stroke={color} fill={color} fillOpacity={0.25} />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
