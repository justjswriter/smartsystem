import { useEffect, useState, type FormEvent } from "react";
import { Eye, EyeOff, Leaf, Radio } from "lucide-react";
import { getNotificationSettings, sendTestNotificationEmail, updateNotificationSettings, updatePassword } from "../api";
import { useAppState } from "../context/AppStateContext";
import { useI18n } from "../i18n";

export function ProfilePage() {
  const { token, user, plants, sensors, updateProfile, updateProfilePhoto } = useAppState();
  const { t } = useI18n();
  const [profileName, setProfileName] = useState("");
  const [profileEmail, setProfileEmail] = useState("");
  const [isProfileSaving, setIsProfileSaving] = useState(false);
  const [profileMessage, setProfileMessage] = useState("");
  const [profileError, setProfileError] = useState("");
  const [isPhotoUploading, setIsPhotoUploading] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newPasswordConfirm, setNewPasswordConfirm] = useState("");
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showNewPasswordConfirm, setShowNewPasswordConfirm] = useState(false);
  const [isPasswordFormOpen, setIsPasswordFormOpen] = useState(false);
  const [isPasswordSaving, setIsPasswordSaving] = useState(false);
  const [passwordMessage, setPasswordMessage] = useState("");
  const [passwordError, setPasswordError] = useState("");
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

  function notificationErrorMessage(error: unknown, fallbackKey: string) {
    if (error instanceof Error && /invalid authentication|authentication required/i.test(error.message)) {
      return t("profile.sessionExpired");
    }
    if (error instanceof Error && /current password is incorrect/i.test(error.message)) {
      return t("profile.currentPasswordIncorrect");
    }
    if (error instanceof Error && /passwords do not match/i.test(error.message)) {
      return t("profile.passwordMismatch");
    }
    if (error instanceof Error && /new password must be different/i.test(error.message)) {
      return t("profile.passwordMustBeDifferent");
    }
    return error instanceof Error ? error.message : t(fallbackKey);
  }

  useEffect(() => {
    setProfileName(user?.full_name ?? "");
    setProfileEmail(user?.email ?? "");
  }, [user]);

  async function saveProfile(event: FormEvent) {
    event.preventDefault();
    if (!profileName.trim() || !profileEmail.trim()) {
      return;
    }
    setIsProfileSaving(true);
    setProfileError("");
    setProfileMessage("");
    try {
      await updateProfile({
        full_name: profileName.trim(),
        email: profileEmail.trim(),
      });
      setProfileMessage(t("profile.saved"));
    } catch (error) {
      setProfileError(notificationErrorMessage(error, "profile.saveFailed"));
    } finally {
      setIsProfileSaving(false);
    }
  }

  async function uploadAvatar(file: File | undefined) {
    if (!file) {
      return;
    }
    setIsPhotoUploading(true);
    setProfileError("");
    setProfileMessage("");
    try {
      await updateProfilePhoto(file);
      setProfileMessage(t("profile.photoSaved"));
    } catch (error) {
      setProfileError(notificationErrorMessage(error, "profile.photoSaveFailed"));
    } finally {
      setIsPhotoUploading(false);
    }
  }

  async function savePassword() {
    if (!token) {
      return;
    }
    setPasswordError("");
    setPasswordMessage("");
    if (!currentPassword || !newPassword || !newPasswordConfirm) {
      setPasswordError(t("profile.passwordFieldsRequired"));
      return;
    }
    if (newPassword !== newPasswordConfirm) {
      setPasswordError(t("profile.passwordMismatch"));
      return;
    }
    setIsPasswordSaving(true);
    try {
      await updatePassword(token, {
        current_password: currentPassword,
        new_password: newPassword,
        new_password_confirm: newPasswordConfirm,
      });
      setCurrentPassword("");
      setNewPassword("");
      setNewPasswordConfirm("");
      setIsPasswordFormOpen(false);
      setPasswordMessage(t("profile.passwordSaved"));
    } catch (error) {
      setPasswordError(notificationErrorMessage(error, "profile.passwordSaveFailed"));
    } finally {
      setIsPasswordSaving(false);
    }
  }

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
          setSettingsError(notificationErrorMessage(error, "profile.notificationsLoadFailed"));
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
      setSettingsError(notificationErrorMessage(error, "profile.notificationsSaveFailed"));
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
      setSettingsError(notificationErrorMessage(error, "profile.testEmailFailed"));
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
          <div className="profile-photo-frame">
            {user?.avatar_url ? (
              <img src={user.avatar_url} alt={user.full_name} />
            ) : (
              <div className="profile-photo-placeholder" aria-hidden>
                {user?.full_name?.charAt(0) ?? "U"}
              </div>
            )}
            <label className="profile-photo-btn">
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                onChange={(event) => void uploadAvatar(event.target.files?.[0])}
                disabled={isPhotoUploading}
              />
              {isPhotoUploading ? t("plant.uploading") : t("profile.changePhoto")}
            </label>
          </div>
        </div>

        <form className="card profile-edit-card" onSubmit={(event) => void saveProfile(event)}>
          <h3 className="section-title">{t("profile.profileData")}</h3>
          <label>
            {t("auth.fullName")}
            <input value={profileName} onChange={(event) => setProfileName(event.target.value)} required />
          </label>
          <label>
            {t("auth.email")}
            <input
              type="email"
              value={profileEmail}
              onChange={(event) => setProfileEmail(event.target.value)}
              required
            />
          </label>
          {profileError ? <div className="error">{profileError}</div> : null}
          {profileMessage ? <div className="success">{profileMessage}</div> : null}
          <div className="button-row">
            <button type="submit" disabled={isProfileSaving}>
              {isProfileSaving ? t("common.saving") : t("profile.saveProfile")}
            </button>
            <button
              type="button"
              className="btn-secondary"
              onClick={() => {
                setIsPasswordFormOpen((current) => !current);
                setPasswordError("");
                setPasswordMessage("");
                setCurrentPassword("");
                setNewPassword("");
                setNewPasswordConfirm("");
                setShowCurrentPassword(false);
                setShowNewPassword(false);
                setShowNewPasswordConfirm(false);
              }}
            >
              {t("profile.changePassword")}
            </button>
          </div>
          {isPasswordFormOpen ? (
            <div className="profile-password-panel">
              <h4>{t("profile.changePassword")}</h4>
              <label>
                {t("profile.currentPassword")}
                <span className="password-field">
                  <input
                    type={showCurrentPassword ? "text" : "password"}
                    value={currentPassword}
                    onChange={(event) => setCurrentPassword(event.target.value)}
                    minLength={8}
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowCurrentPassword((current) => !current)}
                    aria-label={showCurrentPassword ? t("auth.hidePassword") : t("auth.showPassword")}
                    title={showCurrentPassword ? t("auth.hidePassword") : t("auth.showPassword")}
                  >
                    {showCurrentPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </span>
              </label>
              <label>
                {t("profile.newPassword")}
                <span className="password-field">
                  <input
                    type={showNewPassword ? "text" : "password"}
                    value={newPassword}
                    onChange={(event) => setNewPassword(event.target.value)}
                    minLength={8}
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowNewPassword((current) => !current)}
                    aria-label={showNewPassword ? t("auth.hidePassword") : t("auth.showPassword")}
                    title={showNewPassword ? t("auth.hidePassword") : t("auth.showPassword")}
                  >
                    {showNewPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </span>
              </label>
              <label>
                {t("profile.confirmNewPassword")}
                <span className="password-field">
                  <input
                    type={showNewPasswordConfirm ? "text" : "password"}
                    value={newPasswordConfirm}
                    onChange={(event) => setNewPasswordConfirm(event.target.value)}
                    minLength={8}
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowNewPasswordConfirm((current) => !current)}
                    aria-label={showNewPasswordConfirm ? t("auth.hidePassword") : t("auth.showPassword")}
                    title={showNewPasswordConfirm ? t("auth.hidePassword") : t("auth.showPassword")}
                  >
                    {showNewPasswordConfirm ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </span>
              </label>
              {passwordError ? <div className="error">{passwordError}</div> : null}
              {passwordMessage ? <div className="success">{passwordMessage}</div> : null}
              <div className="button-row">
                <button type="button" onClick={() => void savePassword()} disabled={isPasswordSaving}>
                  {isPasswordSaving ? t("common.saving") : t("profile.savePassword")}
                </button>
              </div>
            </div>
          ) : passwordMessage ? (
            <div className="success">{passwordMessage}</div>
          ) : null}
        </form>
      </div>

      <div className="stats-row two">
        <div className="card stat-card">
          <Leaf className="stat-ico" size={22} />
          <p className="stat-value">{plants.length}</p>
          <p className="muted small">{t("profile.monitoredPlants")}</p>
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

    </div>
  );
}
