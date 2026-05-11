import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  BarChart3,
  Bell,
  Home,
  Leaf,
  LogOut,
  Settings as SettingsIcon,
  Shield,
  User,
} from "lucide-react";
import { useAppState } from "../context/AppStateContext";
import { useI18n, type Language } from "../i18n";

export function MainLayout() {
  const { user, logout, alerts } = useAppState();
  const { language, setLanguage, t } = useI18n();
  const navigate = useNavigate();

  const openAlerts = alerts.filter((a) => a.status === "created" || a.status === "viewed").length;

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="web-layout">
      <header className="top-header">
        <div className="top-header-inner">
          <div className="brand-block">
            <div className="brand-icon" aria-hidden>
              <Leaf size={22} strokeWidth={2} />
            </div>
            <div>
              <div className="brand-title">Smart Plant Monitor</div>
              <div className="brand-sub">IoT &amp; AI-Powered System</div>
            </div>
          </div>

          <nav className="top-nav" aria-label={t("nav.main")}>
            <NavLink
              to="/"
              end
              className={({ isActive }) => (isActive ? "top-nav-link active" : "top-nav-link")}
            >
              <Home size={18} />
              {t("nav.dashboard")}
            </NavLink>
            <NavLink
              to="/plants"
              className={({ isActive }) => (isActive ? "top-nav-link active" : "top-nav-link")}
            >
              <Leaf size={18} />
              {t("nav.plants")}
            </NavLink>
            <NavLink
              to="/analytics"
              className={({ isActive }) => (isActive ? "top-nav-link active" : "top-nav-link")}
            >
              <BarChart3 size={18} />
              {t("nav.analytics")}
            </NavLink>
          </nav>

          <div className="top-actions">
            <label className="language-select">
              <span className="visually-hidden">{t("language.label")}</span>
              <select value={language} onChange={(e) => setLanguage(e.target.value as Language)}>
                <option value="kk">KK</option>
                <option value="ru">RU</option>
                <option value="en">EN</option>
              </select>
            </label>
            <NavLink to="/alerts" className="icon-btn" title={t("nav.alerts")} aria-label={t("nav.alerts")}>
              <Bell size={20} />
              {openAlerts > 0 ? <span className="alert-dot" /> : null}
            </NavLink>
            <span className="top-divider" aria-hidden />
            <NavLink
              to="/profile"
              className={({ isActive }) =>
                isActive ? "profile-pill active" : "profile-pill"
              }
            >
              <span className="avatar-circle">
                <User size={18} />
              </span>
              <span className="profile-name">{user?.full_name ?? t("nav.profile")}</span>
            </NavLink>
            <NavLink to="/settings" className="icon-btn" title={t("nav.settings")} aria-label={t("nav.settings")}>
              <SettingsIcon size={20} />
            </NavLink>
            {user?.role === "admin" ? (
              <NavLink to="/admin" className="icon-btn" title={t("nav.admin")} aria-label={t("nav.admin")}>
                <Shield size={20} />
              </NavLink>
            ) : null}
            <button type="button" className="icon-btn danger-hover" onClick={handleLogout} title={t("nav.logout")}>
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </header>

      <main className="web-main">
        <Outlet />
      </main>
    </div>
  );
}
