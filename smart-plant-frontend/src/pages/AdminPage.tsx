import { useCallback, useEffect, useState, type Dispatch, type FormEvent, type SetStateAction } from "react";
import { Navigate } from "react-router-dom";
import {
  assignSensor,
  attachSensor,
  createSensor,
  detachSensor,
  getAdminAlerts,
  getAdminLogs,
  getAdminPlants,
  getAdminUsers,
  getSensors,
  rotateSensorToken,
} from "../api";
import { CustomSelect } from "../components/CustomSelect";
import { useAppState } from "../context/AppStateContext";
import { useI18n } from "../i18n";
import type { AdminLog, AdminPlant, Alert, Sensor, User } from "../types";

type Tab = "users" | "sensors" | "alerts" | "logs";

export function AdminPage() {
  const { token, user } = useAppState();
  const { t, label, formatDateTime } = useI18n();
  const [tab, setTab] = useState<Tab>("sensors");
  const [users, setUsers] = useState<User[]>([]);
  const [plants, setPlants] = useState<AdminPlant[]>([]);
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
      const [u, p, s, a, l] = await Promise.all([
        getAdminUsers(token),
        getAdminPlants(token),
        getSensors(token),
        getAdminAlerts(token),
        getAdminLogs(token),
      ]);
      setUsers(u);
      setPlants(p);
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
    return <Navigate to="/dashboard" replace />;
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

  async function handleAssignAndAttach(sensor: Sensor) {
    if (!token) {
      return;
    }
    const userId = Number(assignedUserBySensor[sensor.id] || sensor.user_id || users.find((item) => item.role !== "admin")?.id || "");
    const ownedPlants = plants.filter((plant) => plant.user_id === userId);
    const plantId = Number(attachPlantBySensor[sensor.id] || sensor.plant_id || ownedPlants[0]?.id || "");
    if (!userId || !plantId) {
      setError(t("admin.selectUserAndPlant"));
      return;
    }
    setError("");
    try {
      if (sensor.user_id !== userId) {
        await assignSensor(token, sensor.id, userId);
      }
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
          plants={plants}
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
          onAssignAndAttach={handleAssignAndAttach}
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
  return `python serial_gateway.py --port COM3 --backend-url http://127.0.0.1:8000 --device-id ${deviceId} --device-token ${token} --source-label serial:COM3`;
}

function AdminSensorProvisioning({
  sensors,
  users,
  plants,
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
  onAssignAndAttach,
  onDetach,
  onRotate,
  t,
  formatDateTime,
  label,
}: {
  sensors: Sensor[];
  users: User[];
  plants: AdminPlant[];
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
  onAssignAndAttach: (sensor: Sensor) => Promise<void>;
  onDetach: (sensor: Sensor) => Promise<void>;
  onRotate: (sensor: Sensor) => Promise<void>;
  t: (key: string, params?: Record<string, string | number | null | undefined>) => string;
  formatDateTime: (value: string | Date | null | undefined) => string;
  label: (prefix: string, value: string | null | undefined) => string;
}) {
  const [selectedSensorId, setSelectedSensorId] = useState("");
  const assignableUsers = users.filter((item) => item.role !== "admin");
  const userNameById = new Map(users.map((item) => [item.id, `${item.full_name} (${item.email})`]));
  const plantNameById = new Map(plants.map((item) => [item.id, `${item.name}${item.location ? ` - ${item.location}` : ""}`]));
  const selectedSensor = sensors.find((sensor) => String(sensor.id) === selectedSensorId) ?? null;

  function formatUser(userId: number | null) {
    return userId ? userNameById.get(userId) ?? `#${userId}` : t("admin.notAssigned");
  }

  function formatPlant(plantId: number | null) {
    return plantId ? plantNameById.get(plantId) ?? `#${plantId}` : t("sensors.notAttached");
  }

  function sensorOptionLabel(sensor: Sensor) {
    return `${sensor.device_id} | ${label("sensorStatus", sensor.status)} | ${formatUser(sensor.user_id)} | ${formatPlant(sensor.plant_id)}`;
  }

  function selectSensor(sensor: Sensor) {
    setSelectedSensorId(String(sensor.id));
    setAssignedUserBySensor((current) => ({ ...current, [sensor.id]: String(sensor.user_id ?? "") }));
    setAttachPlantBySensor((current) => ({ ...current, [sensor.id]: String(sensor.plant_id ?? "") }));
  }

  return (
    <div className="page-stack">
      <div className="admin-help-grid">
        <div className="card admin-help-card">
          <h3>{t("admin.reconnectTitle")}</h3>
          <p className="muted">{t("admin.reconnectText")}</p>
        </div>
        <div className="card admin-help-card">
          <h3>{t("admin.newSensorTitle")}</h3>
          <p className="muted">{t("admin.newSensorText")}</p>
        </div>
      </div>

      <form className="card sensor-form" onSubmit={onCreate}>
        <div>
          <h3>{t("admin.registerNewArduinoSensor")}</h3>
          <p className="muted">{t("admin.registerNewArduinoSensorHint")}</p>
        </div>
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
          <CustomSelect
            value={newSensorType}
            onChange={setNewSensorType}
            options={[
              { value: "multi", label: t("sensors.multi") },
              { value: "soil_moisture", label: t("sensors.soil") },
              { value: "temperature", label: t("sensors.temperature") },
              { value: "air_humidity", label: t("sensors.airHumidity") },
              { value: "light", label: t("sensors.light") },
            ]}
          />
        </label>
        <button type="submit" disabled={loading}>{t("admin.createNewSensor")}</button>
      </form>

      {provisioned ? (
        <div className="card token-card">
          <h3>{t("sensors.oneTimeToken")}</h3>
          <p className="muted">{t("sensors.saveToken")}</p>
          <pre className="token-box">{provisioned.deviceId} | {provisioned.token}</pre>
          <pre className="token-box">{adminGatewayCommand(provisioned.deviceId, provisioned.token)}</pre>
        </div>
      ) : null}

      <section className="card provision-card">
        <div>
          <h3>{t("admin.provisionExistingSensor")}</h3>
          <p className="muted">{t("admin.provisionExistingSensorHint")}</p>
        </div>
        <label>
          {t("admin.selectSensor")}
          <CustomSelect
            value={selectedSensorId}
            onChange={(value) => {
              const sensor = sensors.find((item) => String(item.id) === value);
              if (sensor) {
                selectSensor(sensor);
              } else {
                setSelectedSensorId("");
              }
            }}
            options={[
              { value: "", label: t("admin.selectSensorPlaceholder") },
              ...sensors.map((sensor) => ({ value: String(sensor.id), label: sensorOptionLabel(sensor) })),
            ]}
          />
        </label>

        {!selectedSensor ? <p className="empty-state">{t("admin.selectSensorEmptyHint")}</p> : null}

        {selectedSensor ? (
          <SelectedSensorCard
            sensor={selectedSensor}
            assignableUsers={assignableUsers}
            plants={plants}
            assignedUserBySensor={assignedUserBySensor}
            attachPlantBySensor={attachPlantBySensor}
            setAssignedUserBySensor={setAssignedUserBySensor}
            setAttachPlantBySensor={setAttachPlantBySensor}
            onAssignAndAttach={onAssignAndAttach}
            onDetach={onDetach}
            onRotate={onRotate}
            t={t}
            formatDateTime={formatDateTime}
            label={label}
            formatUser={formatUser}
            formatPlant={formatPlant}
          />
        ) : null}
      </section>

      <section className="table-card">
        <div className="table-card-head">
          <div>
            <h3>{t("admin.existingSensorsOverview")}</h3>
            <p className="muted">{t("admin.existingSensorsOverviewHint")}</p>
          </div>
        </div>
        <div className="table-scroll">
          <table className="data-table compact-sensor-table">
            <thead>
              <tr>
                <th>{t("admin.column.device_id")}</th>
                <th>{t("admin.column.status")}</th>
                <th>{t("admin.assignedUser")}</th>
                <th>{t("sensors.attachedPlant")}</th>
                <th>{t("sensors.lastSeen")}</th>
              </tr>
            </thead>
            <tbody>
              {sensors.map((sensor) => (
                <tr
                  key={sensor.id}
                  className={selectedSensor?.id === sensor.id ? "selected-row" : ""}
                  onClick={() => selectSensor(sensor)}
                >
                  <td>{sensor.device_id}</td>
                  <td>
                    <span className={`sensor-status ${sensor.status === "online" ? "online" : "offline"}`}>
                      {label("sensorStatus", sensor.status)}
                    </span>
                  </td>
                  <td>{formatUser(sensor.user_id)}</td>
                  <td>{formatPlant(sensor.plant_id)}</td>
                  <td>{sensor.last_seen_at ? formatDateTime(sensor.last_seen_at) : t("common.neverSeen")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function SelectedSensorCard({
  sensor,
  assignableUsers,
  plants,
  assignedUserBySensor,
  attachPlantBySensor,
  setAssignedUserBySensor,
  setAttachPlantBySensor,
  onAssignAndAttach,
  onDetach,
  onRotate,
  t,
  formatDateTime,
  label,
  formatUser,
  formatPlant,
}: {
  sensor: Sensor;
  assignableUsers: User[];
  plants: AdminPlant[];
  assignedUserBySensor: Record<number, string>;
  attachPlantBySensor: Record<number, string>;
  setAssignedUserBySensor: Dispatch<SetStateAction<Record<number, string>>>;
  setAttachPlantBySensor: Dispatch<SetStateAction<Record<number, string>>>;
  onAssignAndAttach: (sensor: Sensor) => Promise<void>;
  onDetach: (sensor: Sensor) => Promise<void>;
  onRotate: (sensor: Sensor) => Promise<void>;
  t: (key: string, params?: Record<string, string | number | null | undefined>) => string;
  formatDateTime: (value: string | Date | null | undefined) => string;
  label: (prefix: string, value: string | null | undefined) => string;
  formatUser: (userId: number | null) => string;
  formatPlant: (plantId: number | null) => string;
}) {
  const selectedUserId = assignedUserBySensor[sensor.id] ?? String(sensor.user_id ?? "");
  const selectedUserNumber = Number(selectedUserId);
  const userPlants = selectedUserNumber ? plants.filter((plant) => plant.user_id === selectedUserNumber) : [];
  const selectedPlantId = attachPlantBySensor[sensor.id] ?? String(sensor.plant_id ?? "");

  return (
    <article className="selected-sensor-card">
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
          <p className="muted small">{t("admin.assignedUser")}</p>
          <strong>{formatUser(sensor.user_id)}</strong>
        </div>
        <div>
          <p className="muted small">{t("sensors.attachedPlant")}</p>
          <strong>{formatPlant(sensor.plant_id)}</strong>
        </div>
        <div>
          <p className="muted small">{t("sensors.lastSeen")}</p>
          <strong>{sensor.last_seen_at ? formatDateTime(sensor.last_seen_at) : t("common.neverSeen")}</strong>
        </div>
        <div>
          <p className="muted small">{t("admin.source")}</p>
          <strong>{sensor.last_ingest_source ?? t("common.none")}</strong>
        </div>
      </div>

      {sensor.last_error_message ? <p className="error">{sensor.last_error_message}</p> : null}

      <div className="attach-panel">
        <h4>{t("admin.assignAndAttach")}</h4>
        <div className="attach-row">
          <label>
            {t("admin.assignedUser")}
            <CustomSelect
              value={selectedUserId}
              onChange={(value) => {
                const nextUserId = value;
                const nextPlant = plants.find((plant) => plant.user_id === Number(nextUserId));
                setAssignedUserBySensor((current) => ({ ...current, [sensor.id]: nextUserId }));
                setAttachPlantBySensor((current) => ({ ...current, [sensor.id]: nextPlant ? String(nextPlant.id) : "" }));
              }}
              disabled={assignableUsers.length === 0}
              options={[
                { value: "", label: assignableUsers.length === 0 ? t("admin.noUsers") : t("admin.selectUser") },
                ...assignableUsers.map((item) => ({
                  value: String(item.id),
                  label: `${item.full_name} (${item.email})`,
                })),
              ]}
            />
          </label>
          <label>
            {t("sensors.attachedPlant")}
            <CustomSelect
              value={selectedPlantId}
              onChange={(value) => setAttachPlantBySensor((current) => ({ ...current, [sensor.id]: value }))}
              disabled={!selectedUserId || userPlants.length === 0}
              options={[
                { value: "", label: userPlants.length === 0 ? t("admin.noPlantsForUser") : t("admin.selectPlant") },
                ...userPlants.map((plant) => ({
                  value: String(plant.id),
                  label: `${plant.name}${plant.location ? ` - ${plant.location}` : ""} #${plant.id}`,
                })),
              ]}
            />
          </label>
        </div>
        <button
          type="button"
          className="btn-primary"
          onClick={() => onAssignAndAttach(sensor)}
          disabled={!selectedUserId || !selectedPlantId || userPlants.length === 0}
        >
          {t("admin.assignAndAttachButton")}
        </button>
      </div>

      <div className="gateway-command">
        <p className="muted small">{t("admin.reconnectCommand")}</p>
        <pre className="token-box">{adminGatewayCommand(sensor.device_id, "<SAVED_DEVICE_TOKEN>")}</pre>
      </div>

      <div className="button-row">
        <button type="button" onClick={() => onDetach(sensor)} disabled={!sensor.plant_id}>
          {t("sensors.detach")}
        </button>
        <button type="button" onClick={() => onRotate(sensor)}>
          {t("admin.rotateLostToken")}
        </button>
      </div>
    </article>
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
