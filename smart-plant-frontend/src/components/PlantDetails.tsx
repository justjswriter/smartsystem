import { useRef, type ChangeEvent } from "react";
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
import { localizeCareText } from "../careText";
import { useI18n } from "../i18n";
import { displayPlantSpecies } from "../plantKnowledge";
import type { DashboardResponse, Plant, Sensor } from "../types";

type PlantDetailsProps = {
  plant: Plant | null;
  dashboard: DashboardResponse | null;
  isLoading: boolean;
  error: string;
  plantId: number;
  sensors: Sensor[];
  onRefresh: () => Promise<void>;
  isRefreshing: boolean;
  onPhotoUpload: (file: File) => Promise<void>;
  isPhotoUploading: boolean;
};

export function PlantDetails({
  plant,
  dashboard,
  isLoading,
  error,
  plantId,
  sensors,
  onRefresh,
  isRefreshing,
  onPhotoUpload,
  isPhotoUploading,
}: PlantDetailsProps) {
  const { t, label, formatDateTime } = useI18n();
  const emptyValue = "--";
  const temperatureUnit = t("units.temperature");
  const lightUnit = t("units.light");
  const photoInputRef = useRef<HTMLInputElement | null>(null);
  const chartData =
    dashboard?.history.map((h, i) => ({
      label: i === dashboard.history.length - 1 ? "now" : `${i}`,
      recordedAt: h.recorded_at,
      moisture: h.moisture ?? 0,
      temp: h.temperature ?? 0,
      humidity: h.humidity ?? 0,
      light: h.light ?? 0,
      time: formatDateTime(h.recorded_at),
    })) ?? [];

  const current = dashboard?.current;
  const condition = dashboard?.condition;
  const recommendation = dashboard?.active_recommendation;
  const mlConfidenceText =
    condition?.ml_confidence != null
      ? t("plant.confidenceValue", { value: Math.round(condition.ml_confidence * 100) })
      : t("common.unavailable");
  const analysisMethodText = label("analysis", condition?.analysis_method ?? "rule_based");
  const conditionExplanation =
    condition?.condition_status === "insufficient_data"
      ? t("plant.insufficientDataExplanation")
      : condition?.explanation ?? t("plant.noCondition");

  if (isLoading) {
    return <p className="muted page-lead">{t("common.loading")}</p>;
  }

  if (error || !plant) {
    return (
      <div className="page-stack">
        <p className="error">{error || t("plant.notFound")}</p>
        <Link to="/" className="text-link">
          {t("plant.back")}
        </Link>
      </div>
    );
  }

  const health = condition?.health_score ?? plant.health ?? 0;

  async function handlePhotoChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    await onPhotoUpload(file);
    event.target.value = "";
  }

  return (
    <div className="plant-detail-page">
      <Link to="/" className="back-link">
        <ArrowLeft size={18} />
        {t("plant.back")}
      </Link>

      <div className="page-head plant-detail-head">
        <div>
          <h1 className="page-title">{plant.name}</h1>
          <p className="muted page-lead">{displayPlantSpecies(plant.species, t)}</p>
        </div>
        <div className="button-row">
          <button type="button" className="btn-secondary" onClick={onRefresh} disabled={isRefreshing}>
            <Activity size={18} />
            {isRefreshing ? t("plant.refreshing") : t("plant.refreshReadings")}
          </button>
          <input
            ref={photoInputRef}
            type="file"
            accept="image/png,image/jpeg,image/webp"
            className="visually-hidden"
            onChange={(event) => {
              void handlePhotoChange(event);
            }}
          />
          <button
            type="button"
            className="btn-primary"
            onClick={() => photoInputRef.current?.click()}
            disabled={isPhotoUploading}
          >
            <Camera size={18} />
            {isPhotoUploading ? t("plant.uploading") : t("plant.updatePhoto")}
          </button>
        </div>
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
            <h3 className="section-title">{t("plant.info")}</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-ico blue">
                  <MapPin size={18} />
                </span>
                <div>
                  <p className="muted small">{t("dashboard.location")}</p>
                  <p>{plant.location ?? emptyValue}</p>
                </div>
              </div>
              <div className="info-item">
                <span className="info-ico green">
                  <Calendar size={18} />
                </span>
                <div>
                  <p className="muted small">{t("plant.plantId")}</p>
                  <p>{plantId}</p>
                </div>
              </div>
              <div className="info-item">
                <span className="info-ico teal">
                  <Activity size={18} />
                </span>
                <div>
                  <p className="muted small">{t("plant.condition")}</p>
                  <p>{condition?.condition_status ? label("condition", condition.condition_status) : emptyValue}</p>
                </div>
              </div>
              <div className="info-item">
                <span className="info-ico purple">
                  <Activity size={18} />
                </span>
                <div>
                  <p className="muted small">{t("dashboard.description")}</p>
                  <p>{plant.description ?? emptyValue}</p>
                </div>
              </div>
              <div className="info-item">
                <span className={`info-ico ${health >= 80 ? "green" : "yellow"}`}>
                  <Activity size={18} />
                </span>
                <div>
                  <p className="muted small">{t("plant.healthScore")}</p>
                  <p className={health >= 80 ? "text-ok" : "text-warn"}>
                    {condition?.health_score != null ? `${condition.health_score}%` : emptyValue}
                  </p>
                </div>
              </div>
            </div>
            <div className="border-top">
              <p className="muted small">{t("plant.notes")}</p>
              <p>{plant.description ?? t("plant.noNotes")}</p>
            </div>
          </div>

          <div className="card">
            <h3 className="section-title">{t("plant.careSchedule")}</h3>
            <p className="muted small">{t("plant.careGuidance")}</p>
            <div className="care-rows">
              <div className="care-row">
                <span className="care-ico blue">
                  <Droplet size={20} />
                </span>
                <div>
                  <strong>{t("plant.watering")}</strong>
                  <p className="muted small">{t("plant.trackAlerts")}</p>
                </div>
              </div>
              <div className="care-row">
                <span className="care-ico green">
                  <Activity size={20} />
                </span>
                <div>
                  <strong>{t("plant.healthScore")}</strong>
                  <p className="muted small">{t("plant.sensorThresholds")}</p>
                </div>
              </div>
              <div className="care-row">
                <span className="care-ico amber">
                  <Clock size={20} />
                </span>
                <div>
                  <strong>{t("plant.history")}</strong>
                  <p className="muted small">{t("plant.dataPoints", { count: dashboard?.history.length ?? 0 })}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="detail-col">
          <div className="metric-grid">
            <div className="card metric">
              <Thermometer className="metric-ico orange" size={22} />
              <p className="muted small">{t("plant.temperature")}</p>
              <p className="metric-val">{current?.temperature != null ? `${current.temperature}${temperatureUnit}` : emptyValue}</p>
            </div>
            <div className="card metric">
              <Droplet className="metric-ico blue" size={22} />
              <p className="muted small">{t("plant.soilMoisture")}</p>
              <p className="metric-val">{current?.moisture != null ? `${current.moisture}%` : emptyValue}</p>
            </div>
            <div className="card metric">
              <Sun className="metric-ico yellow" size={22} />
              <p className="muted small">{t("dashboard.lightScore")}</p>
              <p className="metric-val">{current?.light != null ? `${current.light} ${lightUnit}` : emptyValue}</p>
            </div>
            <div className="card metric">
              <Wind className="metric-ico teal" size={22} />
              <p className="muted small">{t("plant.humidity")}</p>
              <p className="metric-val">{current?.humidity != null ? `${current.humidity}%` : emptyValue}</p>
            </div>
          </div>
          <p className="muted small">{t("dashboard.lightHint")}</p>

          <div className="card chart-card">
            <h3 className="section-title">{t("plant.sensorHistory")}</h3>
            {chartData.length === 0 ? (
              <p className="muted">{t("plant.noSamples")}</p>
            ) : (
              <div className="chart-wrap">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis
                      dataKey="recordedAt"
                      tick={{ fontSize: 11 }}
                      tickFormatter={(value) => formatDateTime(String(value))}
                    />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="temp" name={t("plant.temperatureLegend")} stroke="#f97316" strokeWidth={2} dot={false} />
                    <Line
                      type="monotone"
                      dataKey="moisture"
                      name={t("plant.moistureLegend")}
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={false}
                    />
                    <Line type="monotone" dataKey="humidity" name={t("plant.humidityLegend")} stroke="#14b8a6" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="light" name={t("plant.lightLegend")} stroke="#eab308" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          <div className="card ai-hint">
            <h3 className="section-title">{t("plant.currentCondition")}</h3>
            <p>{conditionExplanation}</p>
            {condition?.risk_factors.length ? (
              <p className="muted">{t("plant.riskFactors")}: {condition.risk_factors.map((risk) => label("issue", risk)).join(", ")}</p>
            ) : null}
            <p className="muted small">{t("plant.confidence")}: {condition ? condition.confidence : emptyValue}</p>
            <p className="muted small">
              {t("plant.aiPrediction")}:{" "}
              {condition?.ml_prediction
                ? `${label("condition", condition.ml_prediction)} (${mlConfidenceText})`
                : t("common.unavailable")}
            </p>
            <p className="muted small">{t("plant.analysisMethod")}: {analysisMethodText}</p>
          </div>

          <div className="card ai-hint">
            <h3 className="section-title">{t("plant.recommendation")}</h3>
            <p>{localizeCareText(recommendation?.text, t) ?? t("plant.noRecommendation")}</p>
            {recommendation?.reason ? <p className="muted">{localizeCareText(recommendation.reason, t)}</p> : null}
          </div>

          <div className="card">
            <h3 className="section-title">{t("plant.attachedSensors")}</h3>
            {sensors.length === 0 ? (
              <p className="muted">{t("plant.noSensors")}</p>
            ) : (
              <div className="care-rows">
                {sensors.map((sensor) => (
                  <div className="care-row" key={sensor.id}>
                    <span className="care-ico green">
                      <Activity size={20} />
                    </span>
                    <div>
                      <strong>{sensor.device_id}</strong>
                      <p className="muted small">
                        {label("sensorType", sensor.type)} | {label("sensorStatus", sensor.status)} |{" "}
                        {sensor.last_seen_at ? formatDateTime(sensor.last_seen_at) : t("common.neverSeen")} |{" "}
                        {sensor.last_ingest_source ?? t("sensors.noGateway")}
                      </p>
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
