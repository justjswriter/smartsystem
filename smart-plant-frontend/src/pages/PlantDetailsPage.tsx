import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getPlant, getPlantDashboard } from "../api";
import { PlantDetails } from "../components/PlantDetails";
import { useAppState } from "../context/AppStateContext";
import type { DashboardResponse, Plant } from "../types";

export function PlantDetailsPage() {
  const { plantId } = useParams();
  const { token, sensors } = useAppState();
  const [plant, setPlant] = useState<Plant | null>(null);
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const id = plantId ? Number(plantId) : NaN;

  useEffect(() => {
    if (!token || !Number.isFinite(id)) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError("");
    void Promise.all([getPlant(token, id), getPlantDashboard(token, id, 72)])
      .then(([p, d]) => {
        if (!cancelled) {
          setPlant(p);
          setDashboard(d);
        }
      })
      .catch((e: Error) => {
        if (!cancelled) {
          setError(e.message);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [token, id]);

  if (!Number.isFinite(id)) {
    return (
      <p className="error">
        Invalid plant id. <Link to="/plants">Back to plants</Link>
      </p>
    );
  }

  return (
    <PlantDetails
      plant={plant}
      dashboard={dashboard}
      isLoading={loading}
      error={error}
      plantId={id}
      sensors={sensors.filter((sensor) => sensor.plant_id === id)}
    />
  );
}
