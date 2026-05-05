import { Link } from "react-router-dom";
import { useAppState } from "../context/AppStateContext";

export function PlantsIndexPage() {
  const { plants, isPlantsLoading } = useAppState();

  if (isPlantsLoading) {
    return <p className="muted page-lead">Loading plants...</p>;
  }

  if (plants.length === 0) {
    return (
      <div className="page-stack">
        <h1 className="page-title">Plants</h1>
        <p className="muted page-lead">
          No plants yet. Add one from the Dashboard, then open a plant here for details.
        </p>
        <Link to="/" className="text-link">
          Go to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="page-stack">
      <div className="page-head">
        <div>
          <h1 className="page-title">Plants</h1>
          <p className="muted page-lead">Choose a plant to see metrics and care details.</p>
        </div>
      </div>
      <div className="plants-grid">
        {plants.map((plant) => (
          <Link key={plant.id} to={`/plants/${plant.id}`} className="plant-tile card">
            <h3>{plant.name}</h3>
            <p className="muted">{plant.species ?? "Species not set"}</p>
            <p className="muted">{plant.location ?? "Location not set"}</p>
            <span className="text-link">View details →</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
