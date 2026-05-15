import { useCallback, useEffect, useMemo, useState } from "react";
import { getPlantDashboard } from "../api";
import { Dashboard } from "../components/Dashboard";
import { useAppState } from "../context/AppStateContext";
import { DEFAULT_WEATHER_CITY, WEATHER_CITY_KEY, getWeatherCity } from "../weatherCities";
import type { DashboardResponse, PlantCondition } from "../types";

export function DashboardPage() {
  const {
    token,
    plants,
    sensors,
    isPlantsLoading,
    plantsError,
    loadPlants,
  } = useAppState();

  const [readingsByPlant, setReadingsByPlant] = useState<
    Record<number, DashboardResponse["current"] | null | undefined>
  >({});
  const [conditionByPlant, setConditionByPlant] = useState<
    Record<number, PlantCondition | null | undefined>
  >({});
  const [weatherTemp, setWeatherTemp] = useState<number | null>(null);
  const [weatherCityId] = useState(() => localStorage.getItem(WEATHER_CITY_KEY) ?? DEFAULT_WEATHER_CITY);
  const weatherCity = getWeatherCity(weatherCityId);

  const loadDashboardSnapshots = useCallback(
    async (plantList = plants) => {
      if (!token || plantList.length === 0) {
        setReadingsByPlant({});
        setConditionByPlant({});
        return;
      }

      const slice = plantList.slice(0, 20);
      const rows = await Promise.all(
        slice.map(async (p) => {
          try {
            const dash = await getPlantDashboard(token, p.id, 24);
            return { id: p.id, current: dash.current, condition: dash.condition };
          } catch {
            return { id: p.id, current: null, condition: null };
          }
        })
      );

      const next: Record<number, DashboardResponse["current"] | null | undefined> = {};
      const nextCondition: Record<number, PlantCondition | null | undefined> = {};
      for (const row of rows) {
        next[row.id] = row.current;
        nextCondition[row.id] = row.condition;
      }
      setReadingsByPlant(next);
      setConditionByPlant(nextCondition);
    },
    [token, plants]
  );

  useEffect(() => {
    let cancelled = false;
    void loadDashboardSnapshots().then(() => {
      if (cancelled) {
        return;
      }
    });
    return () => {
      cancelled = true;
    };
  }, [loadDashboardSnapshots]);

  useEffect(() => {
    let cancelled = false;
    async function loadWeather() {
      try {
        const response = await fetch(
          `https://api.open-meteo.com/v1/forecast?latitude=${weatherCity.latitude}&longitude=${weatherCity.longitude}&current=temperature_2m`
        );
        if (!response.ok) {
          throw new Error("Weather request failed");
        }
        const data = (await response.json()) as { current?: { temperature_2m?: number } };
        if (!cancelled && typeof data.current?.temperature_2m === "number") {
          setWeatherTemp(Math.round(data.current.temperature_2m * 10) / 10);
        }
      } catch {
        if (!cancelled) {
          setWeatherTemp(null);
        }
      }
    }
    void loadWeather();
    return () => {
      cancelled = true;
    };
  }, [weatherCity.latitude, weatherCity.longitude]);

  const stats = useMemo(() => {
    const total = plants.length;
    const healthValues = Object.values(conditionByPlant)
      .map((c) => c?.health_score)
      .filter((v): v is number => typeof v === "number");
    const avgHealth =
      healthValues.length > 0
        ? Math.round(healthValues.reduce((s, v) => s + v, 0) / healthValues.length)
        : null;
    const temps = Object.values(readingsByPlant)
      .map((c) => c?.temperature)
      .filter((v): v is number => typeof v === "number");
    const avgTemp =
      temps.length > 0
        ? Math.round((temps.reduce((a, b) => a + b, 0) / temps.length) * 10) / 10
        : null;
    return {
      totalPlants: total,
      avgHealth,
      avgTemp,
      activeSensors: sensors.filter((s) => s.plant_id != null).length,
    };
  }, [plants, readingsByPlant, conditionByPlant, sensors]);

  return (
    <Dashboard
      plants={plants}
      readingsByPlant={readingsByPlant}
      conditionByPlant={conditionByPlant}
      stats={stats}
      weatherTemp={weatherTemp}
      weatherCityName={weatherCity.label}
      isLoading={isPlantsLoading}
      error={plantsError}
      onRefresh={() => {
        void loadPlants();
        void loadDashboardSnapshots();
      }}
    />
  );
}
