import { useMemo, useState } from "react";
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
};

const DEFAULT_DEVICE_ID = "arduino-uno-001";
const TOKEN_PLACEHOLDER = "<PASTE_ONE_TIME_DEVICE_TOKEN>";

function gatewayCommand(deviceId: string, token: string) {
  return `python serial_gateway.py --port COM3 --backend-url http://127.0.0.1:8000 --device-id ${deviceId} --device-token ${token}`;
}

function formatDateTime(value: string | null) {
  if (!value) {
    return "never seen";
  }
  return new Date(value).toLocaleString();
}

function sensorTypeLabel(value: string) {
  if (value === "multi") {
    return "Arduino Uno multi sensor";
  }
  return value.replace(/_/g, " ");
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
}: SensorsProps) {
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
        <h2>Sensors</h2>
        <button type="button" onClick={onRefresh} disabled={isLoading}>
          Refresh sensors
        </button>
      </div>

      <div className="card onboarding-card">
        <h3>Arduino Uno USB Serial Gateway setup</h3>
        <p className="muted">
          This page creates the backend sensor identity. Real readings come from Arduino Uno through
          the Python Serial Gateway, not from this form.
        </p>
        <div className="onboarding-steps">
          <span>1. Create sensor</span>
          <span>2. Copy one-time device token</span>
          <span>3. Attach sensor to plant</span>
          <span>4. Run Python gateway with COM port and token</span>
        </div>
      </div>

      <form className="card sensor-form" onSubmit={handleCreate}>
        <h3>Create backend sensor identity</h3>
        <label>
          Device ID
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
          Sensor type
          <select value={newType} onChange={(e) => setNewType(e.target.value)}>
            <option value="multi">Arduino Uno multi sensor (soil, temp, humidity, light)</option>
            <option value="soil_moisture">Soil moisture</option>
            <option value="temperature">Temperature</option>
            <option value="air_humidity">Air humidity</option>
            <option value="light">Light</option>
          </select>
        </label>
        <button type="submit">Create sensor identity</button>
      </form>

      {provisioned ? (
        <div className="card token-card">
          <h3>One-time device token</h3>
          <p className="muted">
            Save this token now. It is required by the Python Serial Gateway and will not be shown again.
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
                  <p className="muted small">{sensorTypeLabel(sensor.type)}</p>
                </div>
                <span className={`sensor-status ${sensor.status === "online" ? "online" : "offline"}`}>
                  {sensor.status}
                </span>
              </div>

              <div className="sensor-meta-grid">
                <div>
                  <p className="muted small">Attached plant</p>
                  <strong>{attachedPlant ?? "Not attached"}</strong>
                </div>
                <div>
                  <p className="muted small">Last seen</p>
                  <strong>{formatDateTime(sensor.last_seen_at)}</strong>
                </div>
                <div>
                  <p className="muted small">Source</p>
                  <strong>{sensor.last_ingest_source ?? "No gateway data yet"}</strong>
                </div>
              </div>

              {sensor.last_error_message ? <p className="error">{sensor.last_error_message}</p> : null}

              <div className="gateway-command">
                <p className="muted small">Gateway command template</p>
                <pre className="token-box">{gatewayCommand(sensor.device_id, TOKEN_PLACEHOLDER)}</pre>
              </div>

              <div className="attach-panel">
                <h4>Attach to plant</h4>
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
                    {plants.length === 0 ? <option value="">Create a plant first</option> : null}
                    {plants.map((plant) => (
                      <option key={plant.id} value={plant.id}>
                        {plant.name}
                      </option>
                    ))}
                  </select>
                  <button type="button" onClick={() => attach(sensor)} disabled={plants.length === 0}>
                    Attach
                  </button>
                </div>
              </div>

              <div className="button-row">
                <button type="button" onClick={() => onDetach(sensor.id)} disabled={!sensor.plant_id}>
                  Detach
                </button>
                <button type="button" onClick={() => rotate(sensor)}>
                  Rotate token
                </button>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
