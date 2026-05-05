import { useCallback, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { getAdminAlerts, getAdminLogs, getAdminSensors, getAdminUsers } from "../api";
import { useAppState } from "../context/AppStateContext";
import type { AdminLog, Alert, Sensor, User } from "../types";

type Tab = "users" | "sensors" | "alerts" | "logs";

export function AdminPage() {
  const { token, user } = useAppState();
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
      setError(e instanceof Error ? e.message : "Failed to load admin data");
    } finally {
      setLoading(false);
    }
  }, [token]);

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
          <h1 className="page-title">Admin monitoring</h1>
          <p className="muted page-lead">Read-only users, devices, alerts, and system logs.</p>
        </div>
        <button className="btn-secondary" type="button" onClick={() => void load()} disabled={loading}>
          Refresh
        </button>
      </div>
      {error ? <div className="error">{error}</div> : null}
      <div className="toolbar">
        {(["users", "sensors", "alerts", "logs"] as Tab[]).map((item) => (
          <button key={item} type="button" className={tab === item ? "btn-primary" : "btn-secondary"} onClick={() => setTab(item)}>
            {item}
          </button>
        ))}
      </div>

      {tab === "users" ? <AdminTable rows={users} columns={["id", "email", "full_name", "role", "is_active"]} /> : null}
      {tab === "sensors" ? <AdminTable rows={sensors} columns={["id", "device_id", "type", "status", "plant_id", "last_seen_at", "last_error_message"]} /> : null}
      {tab === "alerts" ? <AdminTable rows={alerts} columns={["id", "plant_id", "status", "severity", "metric", "created_at"]} /> : null}
      {tab === "logs" ? <AdminTable rows={logs} columns={["id", "event_type", "user_id", "message", "created_at"]} /> : null}
    </div>
  );
}

function AdminTable<T extends Record<string, unknown>>({ rows, columns }: { rows: T[]; columns: string[] }) {
  return (
    <div className="table-card">
      <div className="table-scroll">
        <table className="data-table">
          <thead>
            <tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={String(row.id ?? index)}>
                {columns.map((column) => (
                  <td key={column}>{String(row[column] ?? "—")}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
