import { useCallback, useEffect, useState } from "react";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { Link, useLocation, useParams } from "react-router-dom";
import { API_BASE_URL, getPlant, getPlantDashboard, updatePlant, uploadPlantPhoto } from "../api";
import { PlantDetails } from "../components/PlantDetails";
import { useAppState } from "../context/AppStateContext";
import { useI18n } from "../i18n";
import type { DashboardPoint, DashboardResponse, Plant } from "../types";

const DASHBOARD_POLL_INTERVAL_MS = 5000;

export function PlantDetailsPage() {
  const { t } = useI18n();
  const { plantId } = useParams();
  const location = useLocation();
  const { token, sensors, loadPlants } = useAppState();
  const [plant, setPlant] = useState<Plant | null>(null);
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [photoUploading, setPhotoUploading] = useState(false);
  const [notesSaving, setNotesSaving] = useState(false);

  const id = plantId ? Number(plantId) : NaN;
  const routeState = location.state as { backTo?: string; backLabelKey?: string } | null;
  const backTo = routeState?.backTo ?? "/plants";
  const backLabel = t(routeState?.backLabelKey ?? "common.backToPlants");

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

  const refreshDashboard = useCallback(async (showIndicator = true) => {
    if (!token || !Number.isFinite(id)) {
      return;
    }
    if (showIndicator) {
      setRefreshing(true);
    }
    setError("");
    try {
      const d = await getPlantDashboard(token, id, 72);
      setDashboard(d);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("common.failedRefreshReadings"));
    } finally {
      if (showIndicator) {
        setRefreshing(false);
      }
    }
  }, [token, id, t]);

  const applySensorDataEvent = useCallback(
    (eventData: string) => {
      try {
        const payload = JSON.parse(eventData) as {
          plant_id?: number;
          data?: Partial<DashboardPoint>;
        };
        if (payload.plant_id !== id || !payload.data?.recorded_at) {
          void refreshDashboard();
          return;
        }
        const point: DashboardPoint = {
          recorded_at: payload.data.recorded_at,
          moisture: payload.data.moisture ?? null,
          temperature: payload.data.temperature ?? null,
          humidity: payload.data.humidity ?? null,
          light: payload.data.light ?? null,
        };
        setDashboard((currentDashboard) => {
          if (!currentDashboard) {
            return currentDashboard;
          }
          const history = [...currentDashboard.history, point].slice(-500);
          return {
            ...currentDashboard,
            current: point,
            history,
            last_updated_at: point.recorded_at,
          };
        });
        void refreshDashboard(false);
      } catch {
        void refreshDashboard(false);
      }
    },
    [id, refreshDashboard]
  );

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

  const saveNotes = useCallback(
    async (notes: string) => {
      if (!token || !Number.isFinite(id)) {
        return;
      }
      setNotesSaving(true);
      setError("");
      try {
        const updated = await updatePlant(token, id, { description: notes.trim() || null });
        setPlant(updated);
        await loadPlants();
      } catch (e) {
        setError(e instanceof Error ? e.message : t("common.failedSaveNotes"));
      } finally {
        setNotesSaving(false);
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
        applySensorDataEvent(event.data);
      },
      onerror() {
        // fetch-event-source retries automatically.
      },
    });
    return () => abortController.abort();
  }, [token, id, applySensorDataEvent]);

  useEffect(() => {
    if (!token || !Number.isFinite(id)) {
      return;
    }
    const intervalId = window.setInterval(() => {
      if (document.hidden) {
        return;
      }
      void refreshDashboard(false);
    }, DASHBOARD_POLL_INTERVAL_MS);
    return () => window.clearInterval(intervalId);
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
      onNotesSave={saveNotes}
      isNotesSaving={notesSaving}
      backTo={backTo}
      backLabel={backLabel}
    />
  );
}
