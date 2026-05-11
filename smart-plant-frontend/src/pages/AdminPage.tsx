import { useCallback, useEffect, useState, type Dispatch, type FormEvent, type SetStateAction } from "react";
import { Navigate } from "react-router-dom";
import {
  assignSensor,
  attachSensor,
  createSensor,
  detachSensor,
  getAdminAlerts,
  getAdminLogs,
  getAdminUsers,
  getSensors,
  rotateSensorToken,
} from "../api";
import { useAppState } from "../context/AppStateContext";
import { useI18n } from "../i18n";
import type { AdminLog, Alert, Sensor, User } from "../types";

type Tab = "users" | "sensors" | "alerts" | "logs";

export function AdminPage() {
  const { token, user } = useAppState();
  const { t, label, formatDateTime } = useI18n();
  const [tab, setTab] = useState<Tab>("users");
  const [users, setUsers] = useState<User[]>([]);
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [logs, setLogs] = useState<AdminLog[]>([]);
  const [error, setError] = useState("");
  const [newDeviceId, setNewDeviceId] = useState("arduino-uno-001");
  const [newSensorType, setNewSensorType] = useState("multi");
  const [assignedUserBySensor, setAssignedUserBySensor] = useState<Record<number, string>>({});
  const [attachPlantBySensor, setAttachPlantBySensor] = useState<Record<number, string>>({});
  const [provisioned, setProvisioned] = useState<{ deviceId: string; token: string } | null>(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    if (!token) {
      return;
    }
    setLoading(true);
    setError("");
    try {
      const [u, s, a, l] = await Promise.all([
        getAdminUsers(token),
        getSensors(token),
        getAdminAlerts(token),
        getAdminLogs(token),
      ]);
      setUsers(u);
      setSensors(s);
      setAlerts(a);
      setLogs(l);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("admin.failed"));
    } finally {
      setLoading(false);
    }
  }, [token, t]);

  useEffect(() => {
    void load();
  }, [load]);

  if (user && user.role !== "admin") {
    return <Navigate to="/" replace />;
  }

  async function handleCreateSensor(event: FormEvent) {
    event.preventDefault();
    if (!token) {
      return;
    }
    setError("");
    try {
      const result = await createSensor(token, newDeviceId.trim(), newSensorType);
      setProvisioned({ deviceId: result.sensor.device_id, token: result.device_token });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : t("admin.sensorActionFailed"));
    }
  }

  async function handleAssign(sensor: Sensor) {
    if (!token) {
      return;
    }
    const userId = Number(assignedUserBySensor[sensor.id] || users.find((item) => item.role !== "admin")?.id || "");
    if (!userId) {
      return;
    }
    setError("");
    try {
      await assignSensor(token, sensor.id, userId);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : t("admin.sensorActionFailed"));
    }
  }

  async function handleAttach(sensor: Sensor) {
    if (!token) {
      return;
    }
    const plantId = Number(attachPlantBySensor[sensor.id]);
    if (!plantId) {
      return;
    }
    setError("");
    try {
      await attachSensor(token, sensor.id, plantId);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : t("admin.sensorActionFailed"));
    }
  }

  async function handleDetach(sensor: Sensor) {
    if (!token) {
      return;
    }
    setError("");
    try {
      await detachSensor(token, sensor.id);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : t("admin.sensorActionFailed"));
    }
  }

  async function handleRotate(sensor: Sensor) {
    if (!token) {
      return;
    }
    setError("");
    try {
      const result = await rotateSensorToken(token, sensor.id);
      setProvisioned({ deviceId: result.sensor.device_id, token: result.device_token });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : t("admin.sensorActionFailed"));
    }
  }

  return (
    <div className="page-stack">
      <div className="page-head">
        <div>
          <h1 className="page-title">{t("admin.title")}</h1>
          <p className="muted page-lead">{t("admin.subtitle")}</p>
        </div>
        <button className="btn-secondary" type="button" onClick={() => void load()} disabled={loading}>
          {t("common.refresh")}
        </button>
      </div>
      {error ? <div className="error">{error}</div> : null}
      <div className="toolbar">
        {(["users", "sensors", "alerts", "logs"] as Tab[]).map((item) => (
          <button key={item} type="button" className={tab === item ? "btn-primary" : "btn-secondary"} onClick={() => setTab(item)}>
            {t(`admin.${item}`)}
          </button>
        ))}
      </div>

      {tab === "users" ? <AdminTable rows={users} columns={["id", "email", "full_name", "role", "is_active"]} t={t} formatDateTime={formatDateTime} label={label} /> : null}
      {tab === "sensors" ? (
        <AdminSensorProvisioning
          sensors={sensors}
          users={users}
          loading={loading}
          newDeviceId={newDeviceId}
          newSensorType={newSensorType}
          assignedUserBySensor={assignedUserBySensor}
          attachPlantBySensor={attachPlantBySensor}
          provisioned={provisioned}
          setNewDeviceId={setNewDeviceId}
          setNewSensorType={setNewSensorType}
          setAssignedUserBySensor={setAssignedUserBySensor}
          setAttachPlantBySensor={setAttachPlantBySensor}
          onCreate={handleCreateSensor}
          onAssign={handleAssign}
          onAttach={handleAttach}
          onDetach={handleDetach}
          onRotate={handleRotate}
          t={t}
          formatDateTime={formatDateTime}
          label={label}
        />
      ) : null}
      {tab === "alerts" ? <AdminTable rows={alerts} columns={["id", "plant_id", "status", "severity", "metric", "created_at"]} t={t} formatDateTime={formatDateTime} label={label} /> : null}
      {tab === "logs" ? <AdminTable rows={logs} columns={["id", "event_type", "user_id", "message", "created_at"]} t={t} formatDateTime={formatDateTime} label={label} /> : null}
    </div>
  );
}

function adminGatewayCommand(deviceId: string, token: string) {
  return `python serial_gateway.py --port COM3 --backend-url http://127.0.0.1:8000 --device-id ${deviceId} --device-token ${token}`;
}

function AdminSensorProvisioning({
  sensors,
  users,
  loading,
  newDeviceId,
  newSensorType,
  assignedUserBySensor,
  attachPlantBySensor,
  provisioned,
  setNewDeviceId,
  setNewSensorType,
  setAssignedUserBySensor,
  setAttachPlantBySensor,
  onCreate,
  onAssign,
  onAttach,
  onDetach,
  onRotate,
  t,
  formatDateTime,
  label,
}: {
  sensors: Sensor[];
  users: User[];
  loading: boolean;
  newDeviceId: string;
  newSensorType: string;
  assignedUserBySensor: Record<number, string>;
  attachPlantBySensor: Record<number, string>;
  provisioned: { deviceId: string; token: string } | null;
  setNewDeviceId: (value: string) => void;
  setNewSensorType: (value: string) => void;
  setAssignedUserBySensor: Dispatch<SetStateAction<Record<number, string>>>;
  setAttachPlantBySensor: Dispatch<SetStateAction<Record<number, string>>>;
  onCreate: (event: FormEvent) => Promise<void>;
  onAssign: (sensor: Sensor) => Promise<void>;
  onAttach: (sensor: Sensor) => Promise<void>;
  onDetach: (sensor: Sensor) => Promise<void>;
  onRotate: (sensor: Sensor) => Promise<void>;
  t: (key: string, params?: Record<string, string | number | null | undefined>) => string;
  formatDateTime: (value: string | Date | null | undefined) => string;
  label: (prefix: string, value: string | null | undefined) => string;
}) {
  const assignableUsers = users.filter((item) => item.role !== "admin");

  return (
    <div className="page-stack">
      <form className="card sensor-form" onSubmit={onCreate}>
        <h3>{t("admin.provisionSensor")}</h3>
        <label>
          {t("sensors.deviceId")}
          <input
            type="text"
            value={newDeviceId}
            onChange={(event) => setNewDeviceId(event.target.value)}
            minLength={3}
            required
          />
        </label>
        <label>
          {t("sensors.sensorType")}
          <select value={newSensorType} onChange={(event) => setNewSensorType(event.target.value)}>
            <option value="multi">{t("sensors.multi")}</option>
            <option value="soil_moisture">{t("sensors.soil")}</option>
            <option value="temperature">{t("sensors.temperature")}</option>
            <option value="air_humidity">{t("sensors.airHumidity")}</option>
            <option value="light">{t("sensors.light")}</option>
          </select>
        </label>
        <button type="submit" disabled={loading}>{t("sensors.create")}</button>
      </form>

      {provisioned ? (
        <div className="card token-card">
          <h3>{t("sensors.oneTimeToken")}</h3>
          <p className="muted">{t("sensors.saveToken")}</p>
          <pre className="token-box">{provisioned.deviceId} | {provisioned.token}</pre>
          <pre className="token-box">{adminGatewayCommand(provisioned.deviceId, provisioned.token)}</pre>
        </div>
      ) : null}

      <div className="screen">
        {sensors.map((sensor) => {
          const selectedUserId = assignedUserBySensor[sensor.id] ?? String(sensor.user_id ?? assignableUsers[0]?.id ?? "");
          const selectedPlantId = attachPlantBySensor[sensor.id] ?? String(sensor.plant_id ?? "");

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
                  <p className="muted small">{t("admin.column.user_id")}</p>
                  <strong>{sensor.user_id ?? t("common.none")}</strong>
                </div>
                <div>
                  <p className="muted small">{t("admin.column.plant_id")}</p>
                  <strong>{sensor.plant_id ?? t("sensors.notAttached")}</strong>
                </div>
                <div>
                  <p className="muted small">{t("sensors.lastSeen")}</p>
                  <strong>{sensor.last_seen_at ? formatDateTime(sensor.last_seen_at) : t("common.neverSeen")}</strong>
                </div>
              </div>

              {sensor.last_error_message ? <p className="error">{sensor.last_error_message}</p> : null}

              <div className="attach-panel">
                <h4>{t("admin.assignUser")}</h4>
                <div className="attach-row">
                  <select
                    value={selectedUserId}
                    onChange={(event) =>
                      setAssignedUserBySensor((current) => ({ ...current, [sensor.id]: event.target.value }))
                    }
                    disabled={assignableUsers.length === 0}
                  >
                    {assignableUsers.length === 0 ? <option value="">{t("admin.noUsers")}</option> : null}
                    {assignableUsers.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.full_name} ({item.email})
                      </option>
                    ))}
                  </select>
                  <button type="button" onClick={() => onAssign(sensor)} disabled={assignableUsers.length === 0}>
                    {t("admin.assign")}
                  </button>
                </div>
              </div>

              <div className="attach-panel">
                <h4>{t("sensors.attachToPlant")}</h4>
                <div className="attach-row">
                  <input
                    type="number"
                    min={1}
                    value={selectedPlantId}
                    placeholder={t("admin.plantIdPlaceholder")}
                    onChange={(event) =>
                      setAttachPlantBySensor((current) => ({ ...current, [sensor.id]: event.target.value }))
                    }
                  />
                  <button type="button" onClick={() => onAttach(sensor)} disabled={!selectedPlantId}>
                    {t("sensors.attach")}
                  </button>
                </div>
              </div>

              <div className="button-row">
                <button type="button" onClick={() => onDetach(sensor)} disabled={!sensor.plant_id}>
                  {t("sensors.detach")}
                </button>
                <button type="button" onClick={() => onRotate(sensor)}>
                  {t("sensors.rotate")}
                </button>
              </div>
            </article>
          );
        })}
      </div>
    </div>
  );
}

function AdminTable<T extends Record<string, unknown>>({
  rows,
  columns,
  t,
  formatDateTime,
  label,
}: {
  rows: T[];
  columns: string[];
  t: (key: string, params?: Record<string, string | number | null | undefined>) => string;
  formatDateTime: (value: string | Date | null | undefined) => string;
  label: (prefix: string, value: string | null | undefined) => string;
}) {
  function headerLabel(column: string) {
    const key = `admin.column.${column}`;
    const translated = t(key);
    return translated === key ? column : translated;
  }

  function renderCell(column: string, value: unknown) {
    if (value == null) {
      return "--";
    }
    if (column.endsWith("_at")) {
      return formatDateTime(String(value));
    }
    if (column === "status") {
      return label("alertStatus", String(value)) !== String(value) ? label("alertStatus", String(value)) : label("sensorStatus", String(value));
    }
    if (column === "severity") {
      return label("alertSeverity", String(value));
    }
    if (column === "metric") {
      return label("metric", String(value));
    }
    if (column === "type") {
      return label("sensorType", String(value));
    }
    return String(value);
  }

  return (
    <div className="table-card">
      <div className="table-scroll">
        <table className="data-table">
          <thead>
            <tr>{columns.map((column) => <th key={column}>{headerLabel(column)}</th>)}</tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={String(row.id ?? index)}>
                {columns.map((column) => (
                  <td key={column}>{renderCell(column, row[column])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
