import { useState } from "react";
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
  const [newDeviceId, setNewDeviceId] = useState("");
  const [newType, setNewType] = useState("multi");
  const [provisioned, setProvisioned] = useState<{ deviceId: string; token: string } | null>(null);

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    const token = await onCreate(newDeviceId, newType);
    if (token) {
      setProvisioned({ deviceId: newDeviceId, token });
    }
    setNewDeviceId("");
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
          Refresh
        </button>
      </div>

      <form className="card" onSubmit={handleCreate}>
        <h3>Register new sensor</h3>
        <label>
          Device ID
          <input
            type="text"
            value={newDeviceId}
            onChange={(e) => setNewDeviceId(e.target.value)}
            placeholder="arduino-001"
            minLength={3}
            required
          />
        </label>
        <label>
          Sensor type
          <select value={newType} onChange={(e) => setNewType(e.target.value)}>
            <option value="multi">Multi sensor</option>
            <option value="soil_moisture">Soil moisture</option>
            <option value="temperature">Temperature</option>
            <option value="air_humidity">Air humidity</option>
            <option value="light">Light</option>
          </select>
        </label>
        <button type="submit">Create sensor</button>
      </form>

      {provisioned ? (
        <div className="card">
          <h3>Device token</h3>
          <p className="muted">Shown once. Use it as the X-Device-Token header from the IoT device.</p>
          <pre className="token-box">{provisioned.deviceId} | {provisioned.token}</pre>
        </div>
      ) : null}

      {error ? <div className="error">{error}</div> : null}

      <div className="screen">
        {sensors.map((sensor) => (
          <article key={sensor.id} className="card">
            <h3>{sensor.device_id}</h3>
            <p className="muted">
              Status: {sensor.status} | Type: {sensor.type} | Plant: {sensor.plant_id ?? "not attached"}
            </p>
            <p className="muted">
              Last seen: {sensor.last_seen_at ?? "—"} | Source: {sensor.last_ingest_source ?? "—"}
            </p>
            {sensor.last_error_message ? <p className="error">{sensor.last_error_message}</p> : null}
            <p className="muted small">
              POST /api/v1/ingest/sensors/{sensor.device_id}/data with header X-Device-Token.
            </p>
            <div className="button-row">
              {plants.map((plant) => (
                <button key={plant.id} type="button" onClick={() => onAttach(sensor.id, plant.id)}>
                  Attach to {plant.name}
                </button>
              ))}
              <button type="button" onClick={() => onDetach(sensor.id)}>
                Detach
              </button>
              <button type="button" onClick={() => rotate(sensor)}>
                Rotate token
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
