import { Alerts } from "../components/Alerts";
import { useAppState } from "../context/AppStateContext";
import { getAlert } from "../api";
import { useI18n } from "../i18n";

export function AlertsPage() {
  const { t } = useI18n();
  const {
    alerts,
    token,
    isAlertsLoading,
    alertsError,
    loadAlerts,
    markAlertViewed,
    acknowledgeAlert,
    resolveAlert,
    closeAlert,
  } = useAppState();

  return (
    <div className="page-stack">
      <h1 className="page-title">{t("alerts.title")}</h1>
      <p className="muted page-lead">{t("alerts.subtitle")}</p>
      <Alerts
        alerts={alerts}
        isLoading={isAlertsLoading}
        error={alertsError}
        onRefresh={() => loadAlerts()}
        onLoadDetail={(alertId) => {
          if (!token) {
            throw new Error("Authentication required");
          }
          return getAlert(token, alertId);
        }}
        onMarkViewed={markAlertViewed}
        onAcknowledge={acknowledgeAlert}
        onResolve={resolveAlert}
        onClose={closeAlert}
      />
    </div>
  );
}
