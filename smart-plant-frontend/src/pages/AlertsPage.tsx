import { Alerts } from "../components/Alerts";
import { useAppState } from "../context/AppStateContext";
import { getAlert } from "../api";

export function AlertsPage() {
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
      <h1 className="page-title">Alerts</h1>
      <p className="muted page-lead">Threshold and system alerts for your plants.</p>
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
