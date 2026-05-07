import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Activity, ChevronDown, Droplet, Plus, Search, Sun, Thermometer } from "lucide-react";
import type { DashboardPoint, Plant, PlantCondition } from "../types";

type DashboardStats = {
  totalPlants: number;
  avgHealth: number | null;
  avgTemp: number | null;
  activeSensors: number;
};

type DashboardProps = {
  plants: Plant[];
  readingsByPlant: Record<number, DashboardPoint | null | undefined>;
  conditionByPlant: Record<number, PlantCondition | null | undefined>;
  stats: DashboardStats;
  isLoading: boolean;
  error: string;
  onRefresh: () => void;
  onCreatePlant: (payload: {
    name: string;
    species?: string;
    location?: string;
    description?: string;
  }) => Promise<void>;
};

type SortKey = "health" | "name";

export function Dashboard({
  plants,
  readingsByPlant,
  conditionByPlant,
  stats,
  isLoading,
  error,
  onRefresh,
  onCreatePlant,
}: DashboardProps) {
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<SortKey>("health");
  const [modalOpen, setModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [species, setSpecies] = useState("");
  const [location, setLocation] = useState("");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);

  function formatConditionLabel(value: string | null | undefined) {
    if (!value) {
      return "Unavailable";
    }
    return value
      .split("_")
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(" ");
  }

  const visible = useMemo(() => {
    const q = search.trim().toLowerCase();
    const filtered = plants.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        (p.species ?? "").toLowerCase().includes(q) ||
        (p.location ?? "").toLowerCase().includes(q)
    );
    return [...filtered].sort((a, b) => {
      if (sortBy === "name") {
        return a.name.localeCompare(b.name);
      }
      return (b.health ?? 0) - (a.health ?? 0);
    });
  }, [plants, search, sortBy]);

  function healthClass(health: number | undefined) {
    if (health == null) {
      return "badge-health muted";
    }
    if (health >= 80) {
      return "badge-health ok";
    }
    if (health >= 60) {
      return "badge-health mid";
    }
    return "badge-health bad";
  }

  function statusLabel(health: number | undefined) {
    if (health == null) {
      return "—";
    }
    if (health >= 70) {
      return "Healthy";
    }
    if (health >= 50) {
      return "Needs attention";
    }
    return "At risk";
  }

  async function submitPlant(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await onCreatePlant({
        name: name.trim(),
        species: species.trim() || undefined,
        location: location.trim() || undefined,
        description: description.trim() || undefined,
      });
      setModalOpen(false);
      setName("");
      setSpecies("");
      setLocation("");
      setDescription("");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="dashboard-page">
      <div className="page-head dashboard-head">
        <div>
          <h1 className="page-title">Plant Dashboard</h1>
          <p className="muted page-lead">Monitor and manage all your plants in one place.</p>
        </div>
        <button type="button" className="btn-primary" onClick={() => setModalOpen(true)}>
          <Plus size={18} />
          Add New Plant
        </button>
      </div>

      <div className="stats-row four">
        <div className="card stat-tile">
          <div className="stat-tile-inner">
            <div className="stat-icon-wrap green">
              <Activity size={20} />
            </div>
            <div>
              <p className="muted small">Total Plants</p>
              <p className="stat-big">{stats.totalPlants}</p>
            </div>
          </div>
        </div>
        <div className="card stat-tile">
          <div className="stat-tile-inner">
            <div className="stat-icon-wrap blue">
              <Droplet size={20} />
            </div>
            <div>
              <p className="muted small">Avg Health</p>
              <p className="stat-big">{stats.avgHealth != null ? `${stats.avgHealth}%` : "—"}</p>
            </div>
          </div>
        </div>
        <div className="card stat-tile">
          <div className="stat-tile-inner">
            <div className="stat-icon-wrap orange">
              <Thermometer size={20} />
            </div>
            <div>
              <p className="muted small">Avg Temp</p>
              <p className="stat-big">{stats.avgTemp != null ? `${stats.avgTemp}°C` : "—"}</p>
            </div>
          </div>
        </div>
        <div className="card stat-tile">
          <div className="stat-tile-inner">
            <div className="stat-icon-wrap yellow">
              <Sun size={20} />
            </div>
            <div>
              <p className="muted small">Active Sensors</p>
              <p className="stat-big">{stats.activeSensors}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="toolbar dashboard-toolbar">
        <div className="search-wrap">
          <Search className="search-ico" size={18} />
          <input
            type="search"
            placeholder="Search plants by name, species, or location..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="sort-wrap">
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value as SortKey)}>
            <option value="health">Sort by: Health Status</option>
            <option value="name">Name (A–Z)</option>
          </select>
          <ChevronDown className="select-chevron" size={18} />
        </div>
        <button type="button" className="btn-secondary" onClick={onRefresh} disabled={isLoading}>
          Refresh
        </button>
      </div>

      {error ? <div className="error">{error}</div> : null}
      {isLoading ? <p className="muted">Loading plants...</p> : null}

      <div className="table-card">
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Plant</th>
                <th>Location</th>
                <th>Health</th>
                <th>Temp</th>
                <th>Moisture</th>
                <th>Light</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((plant) => {
                const r = readingsByPlant[plant.id];
                const c = conditionByPlant[plant.id];
                const health = c?.health_score ?? plant.health;
                return (
                  <tr key={plant.id}>
                    <td>
                      <div className="plant-cell">
                        <div className="plant-thumb">
                          {plant.image_url ? (
                            <img src={plant.image_url} alt="" />
                          ) : (
                            <span className="thumb-ph">{plant.name.charAt(0)}</span>
                          )}
                        </div>
                        <div>
                          <div className="plant-name">{plant.name}</div>
                          <div className="muted small">{plant.species ?? "—"}</div>
                        </div>
                      </div>
                    </td>
                    <td>{plant.location ?? "—"}</td>
                    <td>
                      <span className={healthClass(health)}>
                        {health != null ? `${health}%` : "—"}
                      </span>
                    </td>
                    <td>{r?.temperature != null ? `${r.temperature}°C` : "—"}</td>
                    <td>{r?.moisture != null ? `${r.moisture}%` : "—"}</td>
                    <td>{r?.light != null ? `${r.light} lux` : "—"}</td>
                    <td>
                      <span className="badge-status">{c?.condition_status ?? statusLabel(health)}</span>
                      {c?.ml_prediction ? (
                        <div className="muted small">
                          AI: {formatConditionLabel(c.ml_prediction)} ({Math.round((c.ml_confidence ?? 0) * 100)}%)
                        </div>
                      ) : null}
                      <div className="muted small">
                        {c?.analysis_method === "hybrid_rule_based_and_ml"
                          ? "Hybrid rule-based + machine learning"
                          : "Rule-based"}
                      </div>
                    </td>
                    <td>
                      <Link to={`/plants/${plant.id}`} className="text-link">
                        View details →
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="weather-banner">
        <div className="weather-inner">
          <div className="weather-icon">
            <Sun size={36} />
          </div>
          <div className="weather-copy">
            <h3>Perfect growing conditions today</h3>
            <p className="muted-light">Check sensor data per plant for precise indoor readings.</p>
          </div>
          <div className="weather-temp">
            <span className="temp-big">{stats.avgTemp != null ? `${stats.avgTemp}°C` : "—"}</span>
            <span className="muted-light small">Avg. from sensors</span>
          </div>
        </div>
      </div>

      {modalOpen ? (
        <div className="modal-root" role="dialog" aria-modal="true" aria-labelledby="add-plant-title">
          <button
            type="button"
            className="modal-backdrop"
            aria-label="Close"
            onClick={() => setModalOpen(false)}
          />
          <div className="modal-panel card">
            <h2 id="add-plant-title">Add plant</h2>
            <form className="modal-form" onSubmit={submitPlant}>
              <label>
                Name
                <input value={name} onChange={(e) => setName(e.target.value)} required />
              </label>
              <label>
                Species
                <input value={species} onChange={(e) => setSpecies(e.target.value)} />
              </label>
              <label>
                Location
                <input value={location} onChange={(e) => setLocation(e.target.value)} />
              </label>
              <label>
                Description
                <input value={description} onChange={(e) => setDescription(e.target.value)} />
              </label>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={saving}>
                  {saving ? "Saving..." : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </div>
  );
}
