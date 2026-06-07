import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  BarChart3,
  Home,
  Leaf,
  LogOut,
  Radio,
  Shield,
  User,
} from "lucide-react";
import { NotificationsPanel } from "../components/NotificationsPanel";
import { CustomSelect } from "../components/CustomSelect";
import { useAppState } from "../context/AppStateContext";
import { useI18n, type Language } from "../i18n";

export function MainLayout() {
  const { user, logout, plants, notifications, markNotificationAsRead, markAllNotificationsAsRead } = useAppState();
  const { language, setLanguage, t } = useI18n();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/", { replace: true });
  }

  return (
    <div className="web-layout">
      <header className="top-header">
        <div className="top-header-inner">
          <Link to="/" className="brand-block" aria-label="Smart Plant Monitor information">
            <div className="brand-icon" aria-hidden>
              <Leaf size={22} strokeWidth={2} />
            </div>
            <div>
              <div className="brand-title">Smart Plant Monitor</div>
              <div className="brand-sub">IoT &amp; AI-Powered System</div>
            </div>
          </Link>

          <nav className="top-nav" aria-label={t("nav.main")}>
            <NavLink
              to="/dashboard"
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
            <NavLink
              to="/sensors"
              className={({ isActive }) => (isActive ? "top-nav-link active" : "top-nav-link")}
            >
              <Radio size={18} />
              {t("nav.sensors")}
            </NavLink>
          </nav>

          <div className="top-actions">
            <label className="language-select">
              <span className="visually-hidden">{t("language.label")}</span>
              <CustomSelect
                value={language}
                ariaLabel={t("language.label")}
                onChange={(value) => setLanguage(value as Language)}
                options={[
                  { value: "kk", label: "KK" },
                  { value: "ru", label: "RU" },
                  { value: "en", label: "EN" },
                ]}
              />
            </label>
            <NotificationsPanel
              notifications={notifications}
              plants={plants}
              onMarkRead={markNotificationAsRead}
              onMarkAllRead={markAllNotificationsAsRead}
            />
            <span className="top-divider" aria-hidden />
            <NavLink
              to="/profile"
              className={({ isActive }) =>
                isActive ? "profile-pill active" : "profile-pill"
              }
            >
              <span className="avatar-circle">
                {user?.avatar_url ? <img src={user.avatar_url} alt={user.full_name} /> : <User size={18} />}
              </span>
              <span className="profile-name">{user?.full_name ?? t("nav.profile")}</span>
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
      <footer className="app-footer">
        <p>© 2026 Smart Plant Monitor. All rights reserved.</p>
        <p>
          Copyright certificate No. 73639: Smart System with IoT Integration and
          Artificial Intelligence Technologies for Plant Condition Monitoring.
        </p>
      </footer>
    </div>
  );
}
