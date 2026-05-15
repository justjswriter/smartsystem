import { useEffect, useRef, useState, type ChangeEvent } from "react";
import { Link } from "react-router-dom";
import {
  Activity,
  ArrowLeft,
  BookOpen,
  Calendar,
  Camera,
  Droplet,
  MapPin,
  Sun,
  Thermometer,
  Wind,
  X,
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
import { basicCareItems, displayPlantSpecies } from "../plantKnowledge";
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
  onNotesSave: (notes: string) => Promise<void>;
  isNotesSaving: boolean;
  backTo: string;
  backLabel: string;
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
  onNotesSave,
  isNotesSaving,
  backTo,
  backLabel,
}: PlantDetailsProps) {
  const { t, label, formatDateTime } = useI18n();
  const emptyValue = "--";
  const temperatureUnit = t("units.temperature");
  const photoInputRef = useRef<HTMLInputElement | null>(null);
  const [isEditingNotes, setIsEditingNotes] = useState(false);
  const [isCareGuideOpen, setIsCareGuideOpen] = useState(false);
  const [notesDraft, setNotesDraft] = useState("");
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
  const careItems = dashboard?.care_profile?.basic_care ?? basicCareItems(plant?.species, t);
  const mlConfidenceText =
    condition?.ml_confidence != null
      ? t("plant.confidenceValue", { value: Math.round(condition.ml_confidence * 100) })
      : t("common.unavailable");
  const riskLabels = condition?.risk_factors.map((risk) => label("issue", risk)) ?? [];
  const primaryRisk = riskLabels[0];
  const conditionExplanation = buildHumanConditionSummary();
  const gardenerAdvice = dashboard?.today_care?.length ? dashboard.today_care : buildGardenerAdvice();

  useEffect(() => {
    setNotesDraft(plant?.description ?? "");
    setIsEditingNotes(false);
  }, [plant?.id, plant?.description]);

  useEffect(() => {
    if (!isCareGuideOpen) {
      return;
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsCareGuideOpen(false);
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isCareGuideOpen]);

  if (isLoading) {
    return <p className="muted page-lead">{t("common.loading")}</p>;
  }

  if (error || !plant) {
    return (
      <div className="page-stack">
        <p className="error">{error || t("plant.notFound")}</p>
        <Link to={backTo} className="text-link">
          {backLabel}
        </Link>
      </div>
    );
  }

  const health = condition?.health_score ?? plant.health ?? 0;
  const healthStatusText = buildHealthStatusText();

  function buildHumanConditionSummary() {
    if (!condition || condition.condition_status === "insufficient_data") {
      return t("plant.insufficientDataExplanation");
    }
    if (condition.condition_status === "normal") {
      return t("plant.conditionSummary.normal");
    }
    if (primaryRisk) {
      return t(`plant.conditionSummary.${condition.condition_status}`, { issue: primaryRisk });
    }
    return t(`plant.conditionSummary.${condition.condition_status}`, { issue: t("plant.conditionIssueFallback") });
  }

  function buildHealthStatusText() {
    if (condition?.health_score == null) {
      return t("plant.healthStatus.unavailable");
    }
    if (riskLabels.length > 0 && condition.health_score >= 80) {
      return t("plant.healthStatus.goodWithIssue", { issue: primaryRisk ?? t("plant.conditionIssueFallback") });
    }
    if (condition.health_score >= 80) {
      return t("plant.healthStatus.good");
    }
    if (condition.health_score >= 60) {
      return t("plant.healthStatus.watch");
    }
    return t("plant.healthStatus.bad");
  }

  function buildGardenerAdvice() {
    const moisture = current?.moisture;
    const light = current?.light;
    const humidity = current?.humidity;
    const temperature = current?.temperature;

    return [
      {
        icon: "water",
        color: "blue",
        title: t("plant.gardener.waterTitle"),
        action:
          moisture == null
            ? t("plant.gardener.waterUnknown")
            : moisture < 35
              ? t("plant.gardener.waterDry")
              : moisture < 45
                ? t("plant.gardener.waterSoon")
                : moisture > 75
                  ? t("plant.gardener.waterWet")
                  : t("plant.gardener.waterOk"),
        detail:
          moisture == null
            ? t("plant.gardener.sensorNeeded")
            : t("plant.gardener.currentMoisture", { value: moisture }),
      },
      {
        icon: "light",
        color: "amber",
        title: t("plant.gardener.lightTitle"),
        action:
          light == null
            ? t("plant.gardener.lightUnknown")
            : light < 40
              ? t("plant.gardener.lightLow")
              : light > 180
                ? t("plant.gardener.lightHigh")
                : t("plant.gardener.lightOk"),
        detail:
          light == null
            ? t("plant.gardener.sensorNeeded")
            : t("plant.gardener.currentLight", { value: light }),
      },
      {
        icon: "humidity",
        color: "green",
        title: t("plant.gardener.humidityTitle"),
        action:
          humidity == null
            ? t("plant.gardener.humidityUnknown")
            : humidity < 40
              ? t("plant.gardener.humidityLow")
              : humidity > 75
                ? t("plant.gardener.humidityHigh")
                : t("plant.gardener.humidityOk"),
        detail:
          humidity == null
            ? t("plant.gardener.sensorNeeded")
            : t("plant.gardener.currentHumidity", { value: humidity }),
      },
      {
        icon: "temperature",
        color: "orange",
        title: t("plant.gardener.placeTitle"),
        action:
          temperature == null
            ? t("plant.gardener.placeUnknown")
            : temperature < 18
              ? t("plant.gardener.placeCold")
              : temperature > 30
                ? t("plant.gardener.placeHot")
                : t("plant.gardener.placeOk"),
        detail:
          temperature == null
            ? t("plant.gardener.sensorNeeded")
            : t("plant.gardener.currentTemperature", { value: temperature }),
      },
    ];
  }

  function metricState(metric: "temperature" | "moisture" | "light" | "humidity", value: number | null | undefined) {
    if (value == null) {
      return "unknown";
    }
    if (metric === "temperature") {
      if (value < 16 || value > 34) return "critical";
      if (value < 18 || value > 30) return "warning";
      if (value < 20 || value > 27) return "attention";
      return "normal";
    }
    if (metric === "moisture") {
      const backendStatus = dashboard?.today_care?.find((item) => item.icon === "water")?.status;
      if (
        backendStatus === "normal" ||
        backendStatus === "attention" ||
        backendStatus === "warning" ||
        backendStatus === "critical" ||
        backendStatus === "unknown"
      ) {
        return backendStatus;
      }
      if (value < 20) return "critical";
      if (value < 35 || value > 75) return "warning";
      if (value < 45 || value > 65) return "attention";
      return "normal";
    }
    if (metric === "light") {
      if (value < 20 || value > 260) return "critical";
      if (value < 40 || value > 180) return "warning";
      if (value < 45) return "attention";
      return "normal";
    }
    if (value < 25 || value > 85) return "critical";
    if (value < 40 || value > 75) return "warning";
    if (value < 50 || value > 70) return "attention";
    return "normal";
  }

  async function handlePhotoChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    await onPhotoUpload(file);
    event.target.value = "";
  }

  async function saveNotes() {
    await onNotesSave(notesDraft);
    setIsEditingNotes(false);
  }

  return (
    <div className="plant-detail-page">
      <Link to={backTo} className="back-link">
        <ArrowLeft size={18} />
        {backLabel}
      </Link>

      <div className="page-head plant-detail-head">
        <div>
          <h1 className="page-title">{plant.name}</h1>
          <p className="muted page-lead">{displayPlantSpecies(plant.species, t)}</p>
        </div>
        <div className="button-row">
          <button
            type="button"
            className="btn-secondary icon-label-btn"
            title={t("plant.basicCare")}
            aria-label={t("plant.basicCare")}
            onClick={() => setIsCareGuideOpen(true)}
          >
            <BookOpen size={18} />
          </button>
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

      {isCareGuideOpen ? (
        <div className="care-guide-backdrop" role="presentation" onClick={() => setIsCareGuideOpen(false)}>
          <div
            className="care-guide-dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="care-guide-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="care-guide-head">
              <div className="species-care-head">
                <span className="species-care-mark">
                  <Droplet size={20} />
                  <Sun size={18} />
                </span>
                <div>
                  <h3 className="section-title" id="care-guide-title">{t("plant.basicCare")}</h3>
                  <p className="muted small">{t("plant.basicCareIntro", { species: displayPlantSpecies(plant.species, t) })}</p>
                </div>
              </div>
              <button
                type="button"
                className="icon-btn"
                title={t("common.close")}
                aria-label={t("common.close")}
                onClick={() => setIsCareGuideOpen(false)}
              >
                <X size={18} />
              </button>
            </div>
            <div className="species-care-copy">
              {careItems.map((item) => (
                <p key={item.title}>
                  <strong>{item.title}.</strong> {item.text}
                </p>
              ))}
            </div>
          </div>
        </div>
      ) : null}

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
                <span className={`info-ico ${health >= 80 ? "green" : "yellow"}`}>
                  <Activity size={18} />
                </span>
                <div>
                  <p className="muted small">{t("plant.healthScore")}</p>
                  <p className={health >= 80 ? "text-ok" : "text-warn"}>
                    {condition?.health_score != null ? `${condition.health_score}%` : emptyValue}
                  </p>
                  <p className="muted small">{healthStatusText}</p>
                </div>
              </div>
            </div>
            <div className="border-top">
              <div className="notes-head">
                <p className="muted small">{t("plant.notes")}</p>
                <button type="button" className="text-button" onClick={() => setIsEditingNotes((current) => !current)}>
                  {isEditingNotes ? t("common.cancel") : t("plant.editNotes")}
                </button>
              </div>
              {isEditingNotes ? (
                <div className="notes-editor">
                  <textarea
                    value={notesDraft}
                    onChange={(event) => setNotesDraft(event.target.value)}
                    placeholder={t("plant.notesPlaceholder")}
                    rows={4}
                  />
                  <button type="button" onClick={() => void saveNotes()} disabled={isNotesSaving}>
                    {isNotesSaving ? t("common.saving") : t("plant.saveNotes")}
                  </button>
                </div>
              ) : (
                <p>{plant.description?.trim() ? plant.description : t("plant.noNotes")}</p>
              )}
            </div>
          </div>

          <div className="card gardener-card">
            <h3 className="section-title">{t("plant.careSchedule")}</h3>
            <p className="muted small">{t("plant.careGuidance")}</p>
            <div className="gardener-plan">
              {gardenerAdvice.map((item) => (
                <div className="gardener-step" key={item.title}>
                  <span className={`care-ico ${item.color}`}>
                    {item.icon === "water" ? (
                      <Droplet size={20} />
                    ) : item.icon === "light" ? (
                      <Sun size={20} />
                    ) : item.icon === "humidity" ? (
                      <Wind size={20} />
                    ) : (
                      <Thermometer size={20} />
                    )}
                  </span>
                  <div>
                    <strong>{item.title}</strong>
                    <p>{"action" in item ? item.action : item.text}</p>
                    <span className="gardener-detail">{item.detail}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="detail-col">
          <div className="metric-grid">
            <div className={`card metric metric-state-${metricState("temperature", current?.temperature)}`}>
              <Thermometer className="metric-ico orange" size={22} />
              <p className="muted small">{t("plant.temperature")}</p>
              <p className="metric-val">{current?.temperature != null ? `${current.temperature}${temperatureUnit}` : emptyValue}</p>
            </div>
            <div className={`card metric metric-state-${metricState("moisture", current?.moisture)}`}>
              <Droplet className="metric-ico blue" size={22} />
              <p className="muted small">{t("plant.soilMoisture")}</p>
              <p className="metric-val">{current?.moisture != null ? `${current.moisture}%` : emptyValue}</p>
            </div>
            <div className={`card metric metric-state-${metricState("light", current?.light)}`}>
              <Sun className="metric-ico yellow" size={22} />
              <p className="muted small">{t("dashboard.lightScore")}</p>
              <p className="metric-val">{current?.light != null ? current.light : emptyValue}</p>
            </div>
            <div className={`card metric metric-state-${metricState("humidity", current?.humidity)}`}>
              <Wind className="metric-ico teal" size={22} />
              <p className="muted small">{t("plant.humidity")}</p>
              <p className="metric-val">{current?.humidity != null ? `${current.humidity}%` : emptyValue}</p>
            </div>
          </div>

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

          <div className="card action-card">
            <h3 className="section-title">{t("plant.currentCondition")}</h3>
            <p>{conditionExplanation}</p>
            {condition?.ml_prediction ? (
              <p className="muted">
                {label("condition", condition.ml_prediction)} ({mlConfidenceText})
              </p>
            ) : null}
            {riskLabels.length ? (
              <p className="muted">{t("plant.riskFactors")}: {riskLabels.join(", ")}</p>
            ) : null}
          </div>

          <div className="card action-card">
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
