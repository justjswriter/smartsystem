import { useMemo, useState } from "react";
import type { Alert } from "../types";

type AlertsProps = {
  alerts: Alert[];
  isLoading: boolean;
  error: string;
  onRefresh: () => Promise<void>;
  onLoadDetail: (alertId: number) => Promise<Alert>;
  onMarkViewed: (alertId: number) => Promise<void>;
  onAcknowledge: (alertId: number) => Promise<void>;
  onResolve: (alertId: number) => Promise<void>;
  onClose: (alertId: number) => Promise<void>;
};

export function Alerts({
  alerts,
  isLoading,
  error,
  onRefresh,
  onLoadDetail,
  onMarkViewed,
  onAcknowledge,
  onResolve,
  onClose,
}: AlertsProps) {
  const [status, setStatus] = useState("");
  const [severity, setSeverity] = useState("");
  const [selected, setSelected] = useState<Alert | null>(null);

  const sortedAlerts = useMemo(() => {
    return [...alerts]
      .filter((a) => !status || a.status === status)
      .filter((a) => !severity || a.severity === severity)
      .sort((a, b) => b.created_at.localeCompare(a.created_at));
  }, [alerts, status, severity]);

  return (
    <section className="screen">
      <div className="row">
        <h2>Alerts</h2>
        <button type="button" onClick={onRefresh} disabled={isLoading}>
          Refresh
        </button>
      </div>

      <div className="toolbar">
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All statuses</option>
          <option value="created">Created</option>
          <option value="viewed">Viewed</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
        </select>
        <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
          <option value="">All severities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>

      {error ? <div className="error">{error}</div> : null}
      {isLoading ? <p className="muted">Loading alerts...</p> : null}

      <div className="screen">
        {sortedAlerts.map((alert) => (
          <article key={alert.id} className="card">
            <div className="row">
              <h3>{alert.title}</h3>
              <span className="muted">{alert.severity}</span>
            </div>
            <p>{alert.message}</p>
            {alert.recommendation ? <p><strong>Recommendation:</strong> {alert.recommendation}</p> : null}
            <p className="muted">
              Plant #{alert.plant_id} | Status: {alert.status} | Metric: {alert.metric ?? "—"}
            </p>
            <div className="button-row">
              <button type="button" onClick={() => void onLoadDetail(alert.id).then(setSelected)}>
                Details
              </button>
              <button type="button" onClick={() => onMarkViewed(alert.id)}>
                Viewed
              </button>
              <button type="button" onClick={() => onAcknowledge(alert.id)}>
                Ack
              </button>
              <button type="button" onClick={() => onResolve(alert.id)}>
                Resolve
              </button>
              <button type="button" onClick={() => onClose(alert.id)}>
                Close
              </button>
            </div>
          </article>
        ))}
      </div>

      {selected ? (
        <div className="modal-root" role="dialog" aria-modal="true" aria-labelledby="alert-detail-title">
          <button className="modal-backdrop" type="button" aria-label="Close" onClick={() => setSelected(null)} />
          <div className="modal-panel card">
            <h2 id="alert-detail-title">{selected.title}</h2>
            <p>{selected.message}</p>
            <p className="muted">Value: {selected.value ?? "—"} | Threshold: {selected.threshold ?? "—"}</p>
            <h3>Recommendation</h3>
            <p>{selected.recommendation ?? "No recommendation returned yet."}</p>
            <h3>Transition history</h3>
            {selected.transitions?.length ? (
              <div className="screen">
                {selected.transitions.map((t) => (
                  <p className="muted" key={t.id}>
                    {t.from_status} → {t.to_status} at {t.changed_at}
                  </p>
                ))}
              </div>
            ) : (
              <p className="muted">Open this alert from backend detail endpoint to load transition history.</p>
            )}
          </div>
        </div>
      ) : null}
    </section>
  );
}
