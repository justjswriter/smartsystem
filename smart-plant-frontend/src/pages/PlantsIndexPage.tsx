import { Link } from "react-router-dom";
import { useAppState } from "../context/AppStateContext";
import { useI18n } from "../i18n";
import { displayPlantSpecies } from "../plantKnowledge";

export function PlantsIndexPage() {
  const { plants, isPlantsLoading } = useAppState();
  const { t } = useI18n();

  if (isPlantsLoading) {
    return <p className="muted page-lead">{t("plants.loading")}</p>;
  }

  if (plants.length === 0) {
    return (
      <div className="page-stack">
        <h1 className="page-title">{t("plants.title")}</h1>
        <p className="muted page-lead">{t("plants.empty")}</p>
        <Link to="/" className="text-link">
          {t("plants.goDashboard")}
        </Link>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <div className="page-head">
        <div>
          <h1 className="page-title">{t("plants.title")}</h1>
          <p className="muted page-lead">{t("plants.subtitle")}</p>
        </div>
      </div>
      <div className="plants-grid">
        {plants.map((plant) => (
          <Link key={plant.id} to={`/plants/${plant.id}`} className="plant-tile card">
            <h3>{plant.name}</h3>
            <p className="muted">{displayPlantSpecies(plant.species, t)}</p>
            <p className="muted">{plant.location ?? t("plants.locationNotSet")}</p>
            <span className="text-link">{t("dashboard.viewDetails")}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
