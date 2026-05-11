import { useMemo, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { Activity, ChevronDown, Droplet, Plus, Search, Sun, Thermometer } from "lucide-react";
import { useI18n } from "../i18n";
import { displayPlantSpecies, SUPPORTED_PLANT_SPECIES, supportedPlantTypeName } from "../plantKnowledge";
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
  const { t, label } = useI18n();
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<SortKey>("health");
  const [modalOpen, setModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [location, setLocation] = useState("");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);
  const temperatureUnit = t("units.temperature");
  const lightUnit = t("units.light");

  function formatConditionLabel(value: string | null | undefined) {
    if (!value) {
      return t("common.unavailable");
    }
    return label("condition", value);
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
      return "--";
    }
    if (health >= 70) {
      return t("dashboard.healthy");
    }
    if (health >= 50) {
      return t("dashboard.needsAttention");
    }
    return t("dashboard.atRisk");
  }

  function analysisLabel(value: string | null | undefined) {
    if (value === "hybrid_rule_based_and_ml") {
      return t("dashboard.hybridShort");
    }
    if (value === "rule_based") {
      return t("dashboard.ruleBasedShort");
    }
    return label("analysis", value ?? "rule_based");
  }

  async function submitPlant(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await onCreatePlant({
        name: name.trim(),
        species: SUPPORTED_PLANT_SPECIES,
        location: location.trim() || undefined,
        description: description.trim() || undefined,
      });
      setModalOpen(false);
      setName("");
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
          <h1 className="page-title">{t("dashboard.title")}</h1>
          <p className="muted page-lead">{t("dashboard.subtitle")}</p>
        </div>
        <button type="button" className="btn-primary" onClick={() => setModalOpen(true)}>
          <Plus size={18} />
          {t("dashboard.addPlant")}
        </button>
      </div>

      <div className="stats-row four">
        <StatTile icon={<Activity size={20} />} color="green" label={t("dashboard.totalPlants")} value={stats.totalPlants} />
        <StatTile icon={<Droplet size={20} />} color="blue" label={t("dashboard.avgHealth")} value={stats.avgHealth != null ? `${stats.avgHealth}%` : "--"} />
        <StatTile icon={<Thermometer size={20} />} color="orange" label={t("dashboard.avgTemp")} value={stats.avgTemp != null ? `${stats.avgTemp}${temperatureUnit}` : "--"} />
        <StatTile icon={<Sun size={20} />} color="yellow" label={t("dashboard.activeSensors")} value={stats.activeSensors} />
      </div>

      <div className="toolbar dashboard-toolbar">
        <div className="search-wrap">
          <Search className="search-ico" size={18} />
          <input
            type="search"
            placeholder={t("dashboard.search")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="sort-wrap">
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value as SortKey)}>
            <option value="health">{t("dashboard.sortHealth")}</option>
            <option value="name">{t("dashboard.sortName")}</option>
          </select>
          <ChevronDown className="select-chevron" size={18} />
        </div>
        <button type="button" className="btn-secondary" onClick={onRefresh} disabled={isLoading}>
          {t("common.refresh")}
        </button>
      </div>
      <p className="muted small">{t("dashboard.lightHint")}</p>

      {error ? <div className="error">{error}</div> : null}
      {isLoading ? <p className="muted">{t("dashboard.loadingPlants")}</p> : null}

      <div className="table-card">
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>{t("dashboard.plant")}</th>
                <th>{t("dashboard.location")}</th>
                <th>{t("dashboard.health")}</th>
                <th>{t("dashboard.temp")}</th>
                <th>{t("dashboard.moisture")}</th>
                <th>{t("dashboard.lightScore")}</th>
                <th>{t("dashboard.status")}</th>
                <th>{t("dashboard.actions")}</th>
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
                          {plant.image_url ? <img src={plant.image_url} alt="" /> : <span className="thumb-ph">{plant.name.charAt(0)}</span>}
                        </div>
                        <div>
                          <div className="plant-name">{plant.name}</div>
                          <div className="muted small">{displayPlantSpecies(plant.species, t)}</div>
                        </div>
                      </div>
                    </td>
                    <td>{plant.location ?? "--"}</td>
                    <td><span className={healthClass(health)}>{health != null ? `${health}%` : "--"}</span></td>
                    <td>{r?.temperature != null ? `${r.temperature}${temperatureUnit}` : "--"}</td>
                    <td>{r?.moisture != null ? `${r.moisture}%` : "--"}</td>
                    <td>{r?.light != null ? `${r.light} ${lightUnit}` : "--"}</td>
                    <td>
                      <span className="badge-status">
                        {c?.condition_status ? label("condition", c.condition_status) : statusLabel(health)}
                      </span>
                      {c?.ml_prediction ? (
                        <div className="muted small">
                          {t("dashboard.ai")}: {formatConditionLabel(c.ml_prediction)} ({Math.round((c.ml_confidence ?? 0) * 100)}%)
                        </div>
                      ) : null}
                      <div className="muted small">
                        {analysisLabel(c?.analysis_method)}
                      </div>
                    </td>
                    <td>
                      <Link to={`/plants/${plant.id}`} className="text-link">{t("dashboard.viewDetails")}</Link>
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
          <div className="weather-icon"><Sun size={36} /></div>
          <div className="weather-copy">
            <h3>{t("dashboard.weatherTitle")}</h3>
            <p className="muted-light">{t("dashboard.weatherText")}</p>
          </div>
          <div className="weather-temp">
            <span className="temp-big">{stats.avgTemp != null ? `${stats.avgTemp}${temperatureUnit}` : "--"}</span>
            <span className="muted-light small">{t("dashboard.avgFromSensors")}</span>
          </div>
        </div>
      </div>

      {modalOpen ? (
        <div className="modal-root" role="dialog" aria-modal="true" aria-labelledby="add-plant-title">
          <button type="button" className="modal-backdrop" aria-label={t("common.close")} onClick={() => setModalOpen(false)} />
          <div className="modal-panel card">
            <h2 id="add-plant-title">{t("dashboard.addPlantTitle")}</h2>
            <form className="modal-form" onSubmit={submitPlant}>
              <label>{t("dashboard.name")}<input value={name} onChange={(e) => setName(e.target.value)} required /></label>
              <label>{t("dashboard.species")}<input value={supportedPlantTypeName(t)} readOnly /></label>
              <label>{t("dashboard.location")}<input value={location} onChange={(e) => setLocation(e.target.value)} /></label>
              <label>{t("dashboard.description")}<input value={description} onChange={(e) => setDescription(e.target.value)} /></label>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setModalOpen(false)}>{t("common.cancel")}</button>
                <button type="submit" className="btn-primary" disabled={saving}>{saving ? t("common.saving") : t("common.create")}</button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function StatTile({ icon, color, label, value }: { icon: ReactNode; color: string; label: string; value: ReactNode }) {
  return (
    <div className="card stat-tile">
      <div className="stat-tile-inner">
        <div className={`stat-icon-wrap ${color}`}>{icon}</div>
        <div>
          <p className="muted small">{label}</p>
          <p className="stat-big">{value}</p>
        </div>
      </div>
    </div>
  );
}
