import { useCallback, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { getAdminAlerts, getAdminLogs, getAdminSensors, getAdminUsers } from "../api";
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
        getAdminSensors(token),
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
      {tab === "sensors" ? <AdminTable rows={sensors} columns={["id", "device_id", "type", "status", "plant_id", "last_seen_at", "last_error_message"]} t={t} formatDateTime={formatDateTime} label={label} /> : null}
      {tab === "alerts" ? <AdminTable rows={alerts} columns={["id", "plant_id", "status", "severity", "metric", "created_at"]} t={t} formatDateTime={formatDateTime} label={label} /> : null}
      {tab === "logs" ? <AdminTable rows={logs} columns={["id", "event_type", "user_id", "message", "created_at"]} t={t} formatDateTime={formatDateTime} label={label} /> : null}
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
