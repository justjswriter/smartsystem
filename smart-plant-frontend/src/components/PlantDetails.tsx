import { Link } from "react-router-dom";
import {
  Activity,
  ArrowLeft,
  Calendar,
  Camera,
  Clock,
  Droplet,
  MapPin,
  Sun,
  Thermometer,
  Wind,
} from "lucide-react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { DashboardResponse, Plant, Sensor } from "../types";

type PlantDetailsProps = {
  plant: Plant | null;
  dashboard: DashboardResponse | null;
  isLoading: boolean;
  error: string;
  plantId: number;
  sensors: Sensor[];
};

export function PlantDetails({ plant, dashboard, isLoading, error, plantId, sensors }: PlantDetailsProps) {
  const chartData =
    dashboard?.history.map((h, i) => ({
      label: i === dashboard.history.length - 1 ? "now" : `${i}`,
      moisture: h.moisture ?? 0,
      temp: h.temperature ?? 0,
      humidity: h.humidity ?? 0,
      light: h.light ?? 0,
      time: new Date(h.recorded_at).toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit" }),
    })) ?? [];

  const current = dashboard?.current;
  const condition = dashboard?.condition;
  const recommendation = dashboard?.active_recommendation;

  if (isLoading) {
    return <p className="muted page-lead">Loading plant...</p>;
  }

  if (error || !plant) {
    return (
      <div className="page-stack">
        <p className="error">{error || "Plant not found."}</p>
        <Link to="/" className="text-link">
          Back to Dashboard
        </Link>
      </div>
    );
  }

  const health = condition?.health_score ?? plant.health ?? 0;

  return (
    <div className="plant-detail-page">
      <Link to="/" className="back-link">
        <ArrowLeft size={18} />
        Back to Dashboard
      </Link>

      <div className="page-head plant-detail-head">
        <div>
          <h1 className="page-title">{plant.name}</h1>
          <p className="muted page-lead">{plant.species ?? "Species not set"}</p>
        </div>
        <button type="button" className="btn-primary" disabled title="Photo upload is disabled in this prototype">
          <Camera size={18} />
          Update Photo
        </button>
      </div>

      <div className="detail-two-col">
        <div className="detail-col">
          <div className="card plant-hero-img">
            {plant.image_url ? (
              <img src={plant.image_url} alt={plant.name} />
            ) : (
              <div className="plant-hero-fallback">{plant.name.charAt(0)}</div>
            )}
          </div>

          <div className="card">
            <h3 className="section-title">Plant information</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-ico blue">
                  <MapPin size={18} />
                </span>
                <div>
                  <p className="muted small">Location</p>
                  <p>{plant.location ?? "—"}</p>
                </div>
              </div>
              <div className="info-item">
                <span className="info-ico green">
                  <Calendar size={18} />
                </span>
                <div>
                  <p className="muted small">Plant ID</p>
                  <p>{plantId}</p>
                </div>
              </div>
              <div className="info-item">
                <span className="info-ico teal">
                  <Activity size={18} />
                </span>
                <div>
                  <p className="muted small">Condition</p>
                  <p>{condition?.condition_status ?? "—"}</p>
                </div>
              </div>
              <div className="info-item">
                <span className="info-ico purple">
                  <Activity size={18} />
                </span>
                <div>
                  <p className="muted small">Description</p>
                  <p>{plant.description ?? "—"}</p>
                </div>
              </div>
              <div className="info-item">
                <span className={`info-ico ${health >= 80 ? "green" : "yellow"}`}>
                  <Activity size={18} />
                </span>
                <div>
                  <p className="muted small">Health score</p>
                  <p className={health >= 80 ? "text-ok" : "text-warn"}>
                    {condition?.health_score != null ? `${condition.health_score}%` : "—"}
                  </p>
                </div>
              </div>
            </div>
            <div className="border-top">
              <p className="muted small">Notes</p>
              <p>{plant.description ?? "No notes yet."}</p>
            </div>
          </div>

          <div className="card">
            <h3 className="section-title">Care schedule</h3>
            <p className="muted small">
              Care guidance is currently based on live sensor alerts and recommendation output.
            </p>
            <div className="care-rows">
              <div className="care-row">
                <span className="care-ico blue">
                  <Droplet size={20} />
                </span>
                <div>
                  <strong>Watering</strong>
                  <p className="muted small">Track via dashboard alerts</p>
                </div>
              </div>
              <div className="care-row">
                <span className="care-ico green">
                  <Activity size={20} />
                </span>
                <div>
                  <strong>Health</strong>
                  <p className="muted small">Based on sensor thresholds</p>
                </div>
              </div>
              <div className="care-row">
                <span className="care-ico amber">
                  <Clock size={20} />
                </span>
                <div>
                  <strong>History</strong>
                  <p className="muted small">{dashboard?.history.length ?? 0} data points</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="detail-col">
          <div className="metric-grid">
            <div className="card metric">
              <Thermometer className="metric-ico orange" size={22} />
              <p className="muted small">Temperature</p>
              <p className="metric-val">{current?.temperature != null ? `${current.temperature}°C` : "—"}</p>
            </div>
            <div className="card metric">
              <Droplet className="metric-ico blue" size={22} />
              <p className="muted small">Soil moisture</p>
              <p className="metric-val">{current?.moisture != null ? `${current.moisture}%` : "—"}</p>
            </div>
            <div className="card metric">
              <Sun className="metric-ico yellow" size={22} />
              <p className="muted small">Light</p>
              <p className="metric-val">{current?.light != null ? `${current.light} lux` : "—"}</p>
            </div>
            <div className="card metric">
              <Wind className="metric-ico teal" size={22} />
              <p className="muted small">Humidity</p>
              <p className="metric-val">{current?.humidity != null ? `${current.humidity}%` : "—"}</p>
            </div>
          </div>

          <div className="card chart-card">
            <h3 className="section-title">Sensor history</h3>
            {chartData.length === 0 ? (
              <p className="muted">No sensor samples yet. Ingest data to see history.</p>
            ) : (
              <div className="chart-wrap">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="time" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="temp" name="Temp (°C)" stroke="#f97316" strokeWidth={2} dot={false} />
                    <Line
                      type="monotone"
                      dataKey="moisture"
                      name="Moisture (%)"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={false}
                    />
                    <Line type="monotone" dataKey="humidity" name="Humidity (%)" stroke="#14b8a6" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="light" name="Light (lux)" stroke="#eab308" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          <div className="card ai-hint">
            <h3 className="section-title">Current condition</h3>
            <p>{condition?.explanation ?? "No plant condition has been calculated yet."}</p>
            {condition?.risk_factors.length ? (
              <p className="muted">Risk factors: {condition.risk_factors.join(", ")}</p>
            ) : null}
            <p className="muted small">Confidence: {condition ? condition.confidence : "—"}</p>
          </div>

          <div className="card ai-hint">
            <h3 className="section-title">Recommendation</h3>
            <p>{recommendation?.text ?? "No active recommendation. The system will generate one when a risk is detected."}</p>
            {recommendation?.reason ? <p className="muted">{recommendation.reason}</p> : null}
          </div>

          <div className="card">
            <h3 className="section-title">Attached sensors</h3>
            {sensors.length === 0 ? (
              <p className="muted">No sensors attached yet.</p>
            ) : (
              <div className="care-rows">
                {sensors.map((sensor) => (
                  <div className="care-row" key={sensor.id}>
                    <span className="care-ico green">
                      <Activity size={20} />
                    </span>
                    <div>
                      <strong>{sensor.device_id}</strong>
                      <p className="muted small">{sensor.type} | {sensor.status} | {sensor.last_seen_at ?? "never seen"}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
