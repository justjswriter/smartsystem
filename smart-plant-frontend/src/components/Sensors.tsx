import { useMemo, useState } from "react";
import { useI18n } from "../i18n";
import type { Plant, Sensor } from "../types";

type SensorsProps = {
  plants: Plant[];
  sensors: Sensor[];
  isLoading: boolean;
  error: string;
  onRefresh: () => Promise<void>;
  onCreate: (deviceId: string, type: string) => Promise<string | null>;
  onAttach: (sensorId: number, plantId: number) => Promise<void>;
  onDetach: (sensorId: number) => Promise<void>;
  onRotateToken: (sensorId: number) => Promise<string | null>;
  readOnly?: boolean;
};

const DEFAULT_DEVICE_ID = "arduino-uno-001";
const TOKEN_PLACEHOLDER = "<PASTE_ONE_TIME_DEVICE_TOKEN>";

function gatewayCommand(deviceId: string, token: string) {
  return `python serial_gateway.py --port COM3 --backend-url http://127.0.0.1:8000 --device-id ${deviceId} --device-token ${token}`;
}

export function Sensors({
  plants,
  sensors,
  isLoading,
  error,
  onRefresh,
  onCreate,
  onAttach,
  onDetach,
  onRotateToken,
  readOnly = false,
}: SensorsProps) {
  const { t, label, formatDateTime } = useI18n();
  const [newDeviceId, setNewDeviceId] = useState(DEFAULT_DEVICE_ID);
  const [newType, setNewType] = useState("multi");
  const [provisioned, setProvisioned] = useState<{ deviceId: string; token: string } | null>(null);
  const [attachPlantBySensor, setAttachPlantBySensor] = useState<Record<number, string>>({});

  const plantNameById = useMemo(() => {
    return new Map(plants.map((plant) => [plant.id, plant.name]));
  }, [plants]);

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    const deviceId = newDeviceId.trim();
    const token = await onCreate(deviceId, newType);
    if (token) {
      setProvisioned({ deviceId, token });
    }
  }

  async function attach(sensor: Sensor) {
    const selected = attachPlantBySensor[sensor.id];
    const plantId = selected ? Number(selected) : plants[0]?.id;
    if (!plantId) {
      return;
    }
    await onAttach(sensor.id, plantId);
  }

  async function rotate(sensor: Sensor) {
    const token = await onRotateToken(sensor.id);
    if (token) {
      setProvisioned({ deviceId: sensor.device_id, token });
    }
  }

  return (
    <section className="screen">
      <div className="row">
        <h2>{t("sensors.title")}</h2>
        <button type="button" onClick={onRefresh} disabled={isLoading}>
          {t("sensors.refresh")}
        </button>
      </div>

      <div className="card onboarding-card">
        <h3>{t("sensors.gatewaySetup")}</h3>
        <p className="muted">
          {readOnly ? t("sensors.readOnlyText") : t("sensors.gatewayText")}
        </p>
        {!readOnly ? (
          <div className="onboarding-steps">
            <span>{t("sensors.step1")}</span>
            <span>{t("sensors.step2")}</span>
            <span>{t("sensors.step3")}</span>
            <span>{t("sensors.step4")}</span>
          </div>
        ) : null}
      </div>

      {!readOnly ? (
        <form className="card sensor-form" onSubmit={handleCreate}>
          <h3>{t("sensors.createIdentity")}</h3>
          <label>
            {t("sensors.deviceId")}
            <input
              type="text"
              value={newDeviceId}
              onChange={(e) => setNewDeviceId(e.target.value)}
              placeholder={DEFAULT_DEVICE_ID}
              minLength={3}
              required
            />
          </label>
          <label>
            {t("sensors.sensorType")}
            <select value={newType} onChange={(e) => setNewType(e.target.value)}>
              <option value="multi">{t("sensors.multi")}</option>
              <option value="soil_moisture">{t("sensors.soil")}</option>
              <option value="temperature">{t("sensors.temperature")}</option>
              <option value="air_humidity">{t("sensors.airHumidity")}</option>
              <option value="light">{t("sensors.light")}</option>
            </select>
          </label>
          <button type="submit">{t("sensors.create")}</button>
        </form>
      ) : null}

      {!readOnly && provisioned ? (
        <div className="card token-card">
          <h3>{t("sensors.oneTimeToken")}</h3>
          <p className="muted">
            {t("sensors.saveToken")}
          </p>
          <pre className="token-box">{provisioned.deviceId} | {provisioned.token}</pre>
          <pre className="token-box">{gatewayCommand(provisioned.deviceId, provisioned.token)}</pre>
        </div>
      ) : null}

      {error ? <div className="error">{error}</div> : null}

      <div className="screen">
        {sensors.map((sensor) => {
          const attachedPlant = sensor.plant_id ? plantNameById.get(sensor.plant_id) : null;
          const selectedPlantId = attachPlantBySensor[sensor.id] ?? String(plants[0]?.id ?? "");

          return (
            <article key={sensor.id} className="card sensor-card">
              <div className="sensor-card-head">
                <div>
                  <h3>{sensor.device_id}</h3>
                  <p className="muted small">{label("sensorType", sensor.type)}</p>
                </div>
                <span className={`sensor-status ${sensor.status === "online" ? "online" : "offline"}`}>
                  {label("sensorStatus", sensor.status)}
                </span>
              </div>

              <div className="sensor-meta-grid">
                <div>
                  <p className="muted small">{t("sensors.attachedPlant")}</p>
                  <strong>{attachedPlant ?? t("sensors.notAttached")}</strong>
                </div>
                <div>
                  <p className="muted small">{t("sensors.lastSeen")}</p>
                  <strong>{sensor.last_seen_at ? formatDateTime(sensor.last_seen_at) : t("common.neverSeen")}</strong>
                </div>
                <div>
                  <p className="muted small">{t("sensors.source")}</p>
                  <strong>{sensor.last_ingest_source ?? t("sensors.noGateway")}</strong>
                </div>
              </div>

              {sensor.last_error_message ? <p className="error">{sensor.last_error_message}</p> : null}

              {!readOnly ? (
                <>
                  <div className="gateway-command">
                    <p className="muted small">{t("sensors.commandTemplate")}</p>
                    <pre className="token-box">{gatewayCommand(sensor.device_id, TOKEN_PLACEHOLDER)}</pre>
                  </div>

                  <div className="attach-panel">
                    <h4>{t("sensors.attachToPlant")}</h4>
                    <div className="attach-row">
                      <select
                        value={selectedPlantId}
                        onChange={(e) =>
                          setAttachPlantBySensor((current) => ({
                            ...current,
                            [sensor.id]: e.target.value,
                          }))
                        }
                        disabled={plants.length === 0}
                      >
                        {plants.length === 0 ? <option value="">{t("sensors.createPlantFirst")}</option> : null}
                        {plants.map((plant) => (
                          <option key={plant.id} value={plant.id}>
                            {plant.name}
                          </option>
                        ))}
                      </select>
                      <button type="button" onClick={() => attach(sensor)} disabled={plants.length === 0}>
                        {t("sensors.attach")}
                      </button>
                    </div>
                  </div>

                  <div className="button-row">
                    <button type="button" onClick={() => onDetach(sensor.id)} disabled={!sensor.plant_id}>
                      {t("sensors.detach")}
                    </button>
                    <button type="button" onClick={() => rotate(sensor)}>
                      {t("sensors.rotate")}
                    </button>
                  </div>
                </>
              ) : null}
            </article>
          );
        })}
      </div>
    </section>
  );
}
