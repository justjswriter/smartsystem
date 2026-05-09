import { Link } from "react-router-dom";
import { Activity, Calendar, Leaf, Radio, Settings } from "lucide-react";
import { useAppState } from "../context/AppStateContext";

export function ProfilePage() {
  const { user, plants, sensors } = useAppState();

  const avgHealth =
    plants.filter((p) => p.health != null).length > 0
      ? Math.round(
          plants.reduce((s, p) => s + (p.health ?? 0), 0) /
            plants.filter((p) => p.health != null).length
        )
      : "—";

  return (
    <div className="page-stack profile-page">
      <div>
        <h1 className="page-title">My Profile</h1>
        <p className="muted page-lead">Account overview and plant care snapshot.</p>
      </div>

      <div className="profile-grid">
        <div className="profile-card-hero card">
          <div className="profile-avatar">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
            </svg>
          </div>
          <h2>{user?.full_name ?? "User"}</h2>
          <p className="profile-role">Plant enthusiast</p>
          <p className="muted small">{user?.email}</p>
        </div>

        <div className="card">
          <h3 className="section-title">Quick actions</h3>
          <Link to="/settings" className="quick-action">
            <span className="qa-icon">
              <Settings size={18} />
            </span>
            <span>
              <strong>IoT &amp; sensors</strong>
              <span className="quick-action-subtitle">Configure devices</span>
            </span>
          </Link>
        </div>
      </div>

      <div className="stats-row three">
        <div className="card stat-card">
          <Leaf className="stat-ico" size={22} />
          <p className="stat-value">{plants.length}</p>
          <p className="muted small">Monitored plants</p>
        </div>
        <div className="card stat-card">
          <Activity className="stat-ico" size={22} />
          <p className="stat-value">{avgHealth}%</p>
          <p className="muted small">Avg health (if available)</p>
        </div>
        <div className="card stat-card">
          <Radio className="stat-ico" size={22} />
          <p className="stat-value">{sensors.length}</p>
          <p className="muted small">Sensors registered</p>
        </div>
      </div>

      <div className="card">
        <h3 className="section-title">Recent focus</h3>
        <p className="muted">
          Use the Dashboard for the full table, Analytics for charts, and Settings for sensor pairing.
        </p>
        <div className="activity-row">
          <Calendar size={18} />
          <span>Open Analytics for historical sensor trends.</span>
        </div>
      </div>
    </div>
  );
}
