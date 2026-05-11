import { useCallback, useEffect, useState } from "react";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { Link, useParams } from "react-router-dom";
import { API_BASE_URL, getPlant, getPlantDashboard, uploadPlantPhoto } from "../api";
import { PlantDetails } from "../components/PlantDetails";
import { useAppState } from "../context/AppStateContext";
import { useI18n } from "../i18n";
import type { DashboardResponse, Plant } from "../types";

export function PlantDetailsPage() {
  const { t } = useI18n();
  const { plantId } = useParams();
  const { token, sensors, loadPlants } = useAppState();
  const [plant, setPlant] = useState<Plant | null>(null);
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [photoUploading, setPhotoUploading] = useState(false);

  const id = plantId ? Number(plantId) : NaN;

  const loadPlantDetails = useCallback(async () => {
    if (!token || !Number.isFinite(id)) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError("");
    try {
      const [p, d] = await Promise.all([getPlant(token, id), getPlantDashboard(token, id, 72)]);
      setPlant(p);
      setDashboard(d);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("common.failedLoadPlantDetails"));
    } finally {
      setLoading(false);
    }
  }, [token, id, t]);

  const refreshDashboard = useCallback(async () => {
    if (!token || !Number.isFinite(id)) {
      return;
    }
    setRefreshing(true);
    setError("");
    try {
      const d = await getPlantDashboard(token, id, 72);
      setDashboard(d);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("common.failedRefreshReadings"));
    } finally {
      setRefreshing(false);
    }
  }, [token, id, t]);

  const updatePhoto = useCallback(
    async (file: File) => {
      if (!token || !Number.isFinite(id)) {
        return;
      }
      setPhotoUploading(true);
      setError("");
      try {
        const updated = await uploadPlantPhoto(token, id, file);
        setPlant(updated);
        await loadPlants();
      } catch (e) {
        setError(e instanceof Error ? e.message : t("common.failedUploadPhoto"));
      } finally {
        setPhotoUploading(false);
      }
    },
    [token, id, loadPlants, t]
  );

  useEffect(() => {
    void loadPlantDetails();
  }, [loadPlantDetails]);

  useEffect(() => {
    if (!token || !Number.isFinite(id)) {
      return;
    }
    const abortController = new AbortController();
    void fetchEventSource(`${API_BASE_URL}/stream/dashboard/${id}`, {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
      signal: abortController.signal,
      onmessage(event) {
        if (event.event === "heartbeat") {
          return;
        }
        void refreshDashboard();
      },
      onerror() {
        // fetch-event-source retries automatically.
      },
    });
    return () => abortController.abort();
  }, [token, id, refreshDashboard]);

  if (!Number.isFinite(id)) {
    return (
      <p className="error">
        {t("common.invalidPlantId")} <Link to="/plants">{t("common.backToPlants")}</Link>
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
      onRefresh={refreshDashboard}
      isRefreshing={refreshing}
      onPhotoUpload={updatePhoto}
      isPhotoUploading={photoUploading}
    />
  );
}
