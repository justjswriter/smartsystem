import { useMemo, useState } from "react";
import { localizeCareText } from "../careText";
import { useI18n } from "../i18n";
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
  const { t, label, formatDateTime } = useI18n();
  const [status, setStatus] = useState("");
  const [severity, setSeverity] = useState("");
  const [selected, setSelected] = useState<Alert | null>(null);

  const localizeAlertText = (text: string | null | undefined) => localizeCareText(text, t);

  const sortedAlerts = useMemo(() => {
    return [...alerts]
      .filter((a) => !status || a.status === status)
      .filter((a) => !severity || a.severity === severity)
      .sort((a, b) => b.created_at.localeCompare(a.created_at));
  }, [alerts, status, severity]);

  return (
    <section className="screen">
      <div className="row">
        <h2>{t("alerts.title")}</h2>
        <button type="button" onClick={onRefresh} disabled={isLoading}>
          {t("common.refresh")}
        </button>
      </div>

      <div className="toolbar">
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">{t("alerts.allStatuses")}</option>
          <option value="created">{t("alerts.created")}</option>
          <option value="viewed">{t("alerts.viewed")}</option>
          <option value="acknowledged">{t("alerts.acknowledged")}</option>
          <option value="resolved">{t("alerts.resolved")}</option>
          <option value="closed">{t("alerts.closed")}</option>
        </select>
        <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
          <option value="">{t("alerts.allSeverities")}</option>
          <option value="low">{t("alerts.low")}</option>
          <option value="medium">{t("alerts.medium")}</option>
          <option value="high">{t("alerts.high")}</option>
          <option value="critical">{t("alerts.critical")}</option>
        </select>
      </div>

      {error ? <div className="error">{error}</div> : null}
      {isLoading ? <p className="muted">{t("alerts.loading")}</p> : null}

      <div className="screen">
        {sortedAlerts.map((alert) => (
          <article key={alert.id} className="card">
            <div className="row">
              <h3>{localizeAlertText(alert.title)}</h3>
              <span className="muted">{label("alertSeverity", alert.severity)}</span>
            </div>
            <p>{localizeAlertText(alert.message)}</p>
            {alert.recommendation ? <p><strong>{t("alerts.recommendation")}:</strong> {localizeAlertText(alert.recommendation)}</p> : null}
            <p className="muted">
              {t("alerts.plant")} #{alert.plant_id} | {t("dashboard.status")}: {label("alertStatus", alert.status)} |{" "}
              {t("alerts.metric")}: {label("metric", alert.metric)}
            </p>
            <div className="button-row">
              <button type="button" onClick={() => void onLoadDetail(alert.id).then(setSelected)}>{t("alerts.details")}</button>
              <button type="button" onClick={() => onMarkViewed(alert.id)}>{t("alerts.viewed")}</button>
              <button type="button" onClick={() => onAcknowledge(alert.id)}>{t("alerts.ack")}</button>
              <button type="button" onClick={() => onResolve(alert.id)}>{t("alerts.resolve")}</button>
              <button type="button" onClick={() => onClose(alert.id)}>{t("common.close")}</button>
            </div>
          </article>
        ))}
      </div>

      {selected ? (
        <div className="modal-root" role="dialog" aria-modal="true" aria-labelledby="alert-detail-title">
          <button className="modal-backdrop" type="button" aria-label={t("common.close")} onClick={() => setSelected(null)} />
          <div className="modal-panel card">
            <h2 id="alert-detail-title">{localizeAlertText(selected.title)}</h2>
            <p>{localizeAlertText(selected.message)}</p>
            <p className="muted">{t("alerts.value")}: {selected.value ?? "--"} | {t("alerts.threshold")}: {selected.threshold ?? "--"}</p>
            <h3>{t("alerts.recommendation")}</h3>
            <p>{localizeAlertText(selected.recommendation) ?? t("alerts.noRecommendation")}</p>
            <h3>{t("alerts.transitionHistory")}</h3>
            {selected.transitions?.length ? (
              <div className="screen">
                {selected.transitions.map((transition) => (
                  <p className="muted" key={transition.id}>
                    {label("alertStatus", transition.from_status)} -&gt; {label("alertStatus", transition.to_status)} |{" "}
                    {formatDateTime(transition.changed_at)}
                  </p>
                ))}
              </div>
            ) : (
              <p className="muted">{t("alerts.openDetail")}</p>
            )}
          </div>
        </div>
      ) : null}
    </section>
  );
}
