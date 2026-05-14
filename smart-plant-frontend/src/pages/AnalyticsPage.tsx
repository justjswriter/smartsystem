import { useEffect, useState } from "react";
import { getPlantDashboard } from "../api";
import { Analytics } from "../components/Analytics";
import { useAppState } from "../context/AppStateContext";
import { useI18n } from "../i18n";
import type { DashboardResponse } from "../types";

export function AnalyticsPage() {
  const { token, plants } = useAppState();
  const { t } = useI18n();
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const defaultPlantId = plants[0]?.id;

  useEffect(() => {
    if (!token || !defaultPlantId) {
      setDashboard(null);
      return;
    }
    void load(defaultPlantId, 168);
  }, [token, defaultPlantId]);

  async function load(plantId: number, hours: number) {
    if (!token) {
      return;
    }
    setIsLoading(true);
    setError("");
    try {
      const data = await getPlantDashboard(token, plantId, hours);
      setDashboard(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("common.failedLoadAnalytics"));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Analytics
      plants={plants}
      dashboard={dashboard}
      isLoading={isLoading}
      error={error}
      onLoad={load}
    />
  );
}
