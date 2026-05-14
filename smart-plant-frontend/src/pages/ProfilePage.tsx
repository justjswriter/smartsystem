import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { Activity, Calendar, Leaf, Radio, Settings } from "lucide-react";
import { getNotificationSettings, sendTestNotificationEmail, updateNotificationSettings } from "../api";
import { useAppState } from "../context/AppStateContext";
import { useI18n } from "../i18n";

export function ProfilePage() {
  const { token, user, plants, sensors } = useAppState();
  const { t } = useI18n();
  const [notificationEmail, setNotificationEmail] = useState("");
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [criticalOnly, setCriticalOnly] = useState(true);
  const [emailCriticalAlerts, setEmailCriticalAlerts] = useState(true);
  const [emailMoistureAlerts, setEmailMoistureAlerts] = useState(true);
  const [emailTemperatureAlerts, setEmailTemperatureAlerts] = useState(true);
  const [emailHumidityAlerts, setEmailHumidityAlerts] = useState(true);
  const [emailLightAlerts, setEmailLightAlerts] = useState(true);
  const [isSettingsLoading, setIsSettingsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [settingsMessage, setSettingsMessage] = useState("");
  const [settingsError, setSettingsError] = useState("");

  const avgHealth =
    plants.filter((p) => p.health != null).length > 0
      ? Math.round(
          plants.reduce((s, p) => s + (p.health ?? 0), 0) /
            plants.filter((p) => p.health != null).length
        )
      : "--";

  useEffect(() => {
    if (!token) {
      return;
    }
    const authToken = token;
    let cancelled = false;
    async function loadSettings() {
      setIsSettingsLoading(true);
      setSettingsError("");
      try {
        const settings = await getNotificationSettings(authToken);
        if (!cancelled) {
          setNotificationEmail(settings.notification_email ?? "");
          setEmailEnabled(settings.email_enabled);
          setCriticalOnly(settings.critical_only);
          setEmailCriticalAlerts(settings.email_critical_alerts);
          setEmailMoistureAlerts(settings.email_moisture_alerts);
          setEmailTemperatureAlerts(settings.email_temperature_alerts);
          setEmailHumidityAlerts(settings.email_humidity_alerts);
          setEmailLightAlerts(settings.email_light_alerts);
        }
      } catch (error) {
        if (!cancelled) {
          setSettingsError(error instanceof Error ? error.message : t("profile.notificationsLoadFailed"));
        }
      } finally {
        if (!cancelled) {
          setIsSettingsLoading(false);
        }
      }
    }
    void loadSettings();
    return () => {
      cancelled = true;
    };
  }, [token, t]);

  async function saveNotificationSettings(event: FormEvent) {
    event.preventDefault();
    if (!token) {
      return;
    }
    setIsSaving(true);
    setSettingsError("");
    setSettingsMessage("");
    try {
      const settings = await updateNotificationSettings(token, {
        notification_email: notificationEmail.trim() || null,
        email_enabled: emailEnabled,
        critical_only: criticalOnly,
        email_critical_alerts: emailCriticalAlerts,
        email_moisture_alerts: emailMoistureAlerts,
        email_temperature_alerts: emailTemperatureAlerts,
        email_humidity_alerts: emailHumidityAlerts,
        email_light_alerts: emailLightAlerts,
      });
      setNotificationEmail(settings.notification_email ?? "");
      setEmailEnabled(settings.email_enabled);
      setCriticalOnly(settings.critical_only);
      setEmailCriticalAlerts(settings.email_critical_alerts);
      setEmailMoistureAlerts(settings.email_moisture_alerts);
      setEmailTemperatureAlerts(settings.email_temperature_alerts);
      setEmailHumidityAlerts(settings.email_humidity_alerts);
      setEmailLightAlerts(settings.email_light_alerts);
      setSettingsMessage(t("profile.notificationsSaved"));
    } catch (error) {
      setSettingsError(error instanceof Error ? error.message : t("profile.notificationsSaveFailed"));
    } finally {
      setIsSaving(false);
    }
  }

  async function sendTestEmail() {
    if (!token) {
      return;
    }
    setIsTesting(true);
    setSettingsError("");
    setSettingsMessage("");
    try {
      const result = await sendTestNotificationEmail(token);
      const statusMessageKey = `profile.emailStatusMessage.${result.status}`;
      const statusMessage = t(statusMessageKey);
      setSettingsMessage(
        statusMessage === statusMessageKey
          ? `${t(`profile.emailStatus.${result.status}`)} ${result.detail}`
          : statusMessage
      );
    } catch (error) {
      setSettingsError(error instanceof Error ? error.message : t("profile.testEmailFailed"));
    } finally {
      setIsTesting(false);
    }
  }

  return (
    <div className="page-stack profile-page">
      <div>
        <h1 className="page-title">{t("profile.title")}</h1>
        <p className="muted page-lead">{t("profile.subtitle")}</p>
      </div>

      <div className="profile-grid">
        <div className="profile-card-hero card">
          <div className="profile-avatar">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
            </svg>
          </div>
          <h2>{user?.full_name ?? t("profile.user")}</h2>
          <p className="profile-role">{t("profile.role")}</p>
          <p className="muted small">{user?.email}</p>
        </div>

        <div className="card">
          <h3 className="section-title">{t("profile.quickActions")}</h3>
          <Link to="/settings" className="quick-action">
            <span className="qa-icon">
              <Settings size={18} />
            </span>
            <span>
              <strong>{t("profile.iot")}</strong>
              <span className="quick-action-subtitle">{t("profile.configureDevices")}</span>
            </span>
          </Link>
        </div>
      </div>

      <div className="stats-row three">
        <div className="card stat-card">
          <Leaf className="stat-ico" size={22} />
          <p className="stat-value">{plants.length}</p>
          <p className="muted small">{t("profile.monitoredPlants")}</p>
        </div>
        <div className="card stat-card">
          <Activity className="stat-ico" size={22} />
          <p className="stat-value">{avgHealth}%</p>
          <p className="muted small">{t("profile.avgHealth")}</p>
        </div>
        <div className="card stat-card">
          <Radio className="stat-ico" size={22} />
          <p className="stat-value">{sensors.length}</p>
          <p className="muted small">{t("profile.sensorsRegistered")}</p>
        </div>
      </div>

      <form className="card notification-settings-card" onSubmit={(event) => void saveNotificationSettings(event)}>
        <h3 className="section-title">{t("profile.notificationContacts")}</h3>
        <p className="muted">{t("profile.notificationContactsText")}</p>
        <label>
          {t("profile.notificationEmail")}
          <input
            type="email"
            value={notificationEmail}
            onChange={(event) => setNotificationEmail(event.target.value)}
            placeholder="name@example.com"
            disabled={isSettingsLoading}
          />
        </label>
        <label className="toggle-row">
          <input
            type="checkbox"
            checked={emailEnabled}
            onChange={(event) => setEmailEnabled(event.target.checked)}
            disabled={isSettingsLoading}
          />
          <span>{t("profile.emailEnabled")}</span>
        </label>
        <label className="toggle-row">
          <input
            type="checkbox"
            checked={criticalOnly}
            onChange={(event) => setCriticalOnly(event.target.checked)}
            disabled={isSettingsLoading}
          />
          <span>{t("profile.criticalOnly")}</span>
        </label>
        <div className="notification-preferences">
          <p className="muted small">{t("profile.emailCategories")}</p>
          <label className="toggle-row">
            <input
              type="checkbox"
              checked={emailCriticalAlerts}
              onChange={(event) => setEmailCriticalAlerts(event.target.checked)}
              disabled={isSettingsLoading}
            />
            <span>{t("profile.emailCriticalAlerts")}</span>
          </label>
          <label className="toggle-row">
            <input
              type="checkbox"
              checked={emailMoistureAlerts}
              onChange={(event) => setEmailMoistureAlerts(event.target.checked)}
              disabled={isSettingsLoading}
            />
            <span>{t("profile.emailMoistureAlerts")}</span>
          </label>
          <label className="toggle-row">
            <input
              type="checkbox"
              checked={emailLightAlerts}
              onChange={(event) => setEmailLightAlerts(event.target.checked)}
              disabled={isSettingsLoading}
            />
            <span>{t("profile.emailLightAlerts")}</span>
          </label>
          <label className="toggle-row">
            <input
              type="checkbox"
              checked={emailTemperatureAlerts}
              onChange={(event) => setEmailTemperatureAlerts(event.target.checked)}
              disabled={isSettingsLoading}
            />
            <span>{t("profile.emailTemperatureAlerts")}</span>
          </label>
          <label className="toggle-row">
            <input
              type="checkbox"
              checked={emailHumidityAlerts}
              onChange={(event) => setEmailHumidityAlerts(event.target.checked)}
              disabled={isSettingsLoading}
            />
            <span>{t("profile.emailHumidityAlerts")}</span>
          </label>
        </div>
        {settingsError ? <div className="error">{settingsError}</div> : null}
        {settingsMessage ? <div className="success">{settingsMessage}</div> : null}
        <div className="button-row">
          <button type="submit" disabled={isSaving || isSettingsLoading}>
            {isSaving ? t("common.saving") : t("profile.saveNotifications")}
          </button>
          <button type="button" onClick={() => void sendTestEmail()} disabled={isTesting || isSettingsLoading}>
            {isTesting ? t("profile.sendingTestEmail") : t("profile.sendTestEmail")}
          </button>
        </div>
      </form>

      <div className="card">
        <h3 className="section-title">{t("profile.recentFocus")}</h3>
        <p className="muted">{t("profile.focusText")}</p>
        <div className="activity-row">
          <Calendar size={18} />
          <span>{t("profile.openAnalytics")}</span>
        </div>
      </div>
    </div>
  );
}
