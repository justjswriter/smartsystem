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

export function MainLayout() {
  const { user, logout, alerts } = useAppState();
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

          <nav className="top-nav" aria-label="Main">
            <NavLink
              to="/"
              end
              className={({ isActive }) => (isActive ? "top-nav-link active" : "top-nav-link")}
            >
              <Home size={18} />
              Dashboard
            </NavLink>
            <NavLink
              to="/plants"
              className={({ isActive }) => (isActive ? "top-nav-link active" : "top-nav-link")}
            >
              <Leaf size={18} />
              Plants
            </NavLink>
            <NavLink
              to="/analytics"
              className={({ isActive }) => (isActive ? "top-nav-link active" : "top-nav-link")}
            >
              <BarChart3 size={18} />
              Analytics
            </NavLink>
          </nav>

          <div className="top-actions">
            <NavLink to="/alerts" className="icon-btn" title="Alerts" aria-label="Alerts">
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
              <span className="profile-name">{user?.full_name ?? "Profile"}</span>
            </NavLink>
            <NavLink to="/settings" className="icon-btn" title="Settings" aria-label="Settings">
              <SettingsIcon size={20} />
            </NavLink>
            {user?.role === "admin" ? (
              <NavLink to="/admin" className="icon-btn" title="Admin" aria-label="Admin">
                <Shield size={20} />
              </NavLink>
            ) : null}
            <button type="button" className="icon-btn danger-hover" onClick={handleLogout} title="Logout">
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
