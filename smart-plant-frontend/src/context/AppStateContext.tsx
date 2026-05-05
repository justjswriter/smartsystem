import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import {
  API_BASE_URL,
  attachSensor,
  createPlant,
  createSensor,
  detachSensor,
  getAlerts,
  getMe,
  getPlants,
  getSensors,
  login,
  register,
  rotateSensorToken,
  transitionAlert,
} from "../api";
import type { Alert, Plant, Sensor, User } from "../types";

const TOKEN_KEY = "smart-plant-token";

type AppStateContextValue = {
  token: string | null;
  user: User | null;
  plants: Plant[];
  alerts: Alert[];
  sensors: Sensor[];
  isAuthLoading: boolean;
  isPlantsLoading: boolean;
  isAlertsLoading: boolean;
  isSensorsLoading: boolean;
  authError: string;
  plantsError: string;
  alertsError: string;
  sensorsError: string;
  setAuthError: (message: string) => void;
  loadPlants: () => Promise<void>;
  loadAlerts: () => Promise<void>;
  loadSensors: () => Promise<void>;
  loginWithCredentials: (email: string, password: string) => Promise<void>;
  registerAccount: (
    fullName: string,
    email: string,
    password: string,
    passwordConfirm: string
  ) => Promise<boolean>;
  logout: () => void;
  createPlantEntry: (payload: {
    name: string;
    species?: string;
    location?: string;
    description?: string;
  }) => Promise<void>;
  createSensorEntry: (deviceId: string, type: string) => Promise<string | null>;
  rotateSensorDeviceToken: (sensorId: number) => Promise<string | null>;
  attachSensorToPlant: (sensorId: number, plantId: number) => Promise<void>;
  detachSensorFromPlant: (sensorId: number) => Promise<void>;
  markAlertViewed: (alertId: number) => Promise<void>;
  acknowledgeAlert: (alertId: number) => Promise<void>;
  resolveAlert: (alertId: number) => Promise<void>;
  closeAlert: (alertId: number) => Promise<void>;
};

const AppStateContext = createContext<AppStateContextValue | null>(null);

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState<User | null>(null);
  const [plants, setPlants] = useState<Plant[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [isAuthLoading, setIsAuthLoading] = useState(false);
  const [isPlantsLoading, setIsPlantsLoading] = useState(false);
  const [isAlertsLoading, setIsAlertsLoading] = useState(false);
  const [isSensorsLoading, setIsSensorsLoading] = useState(false);
  const [authError, setAuthError] = useState("");
  const [plantsError, setPlantsError] = useState("");
  const [alertsError, setAlertsError] = useState("");
  const [sensorsError, setSensorsError] = useState("");

  useEffect(() => {
    async function bootstrap() {
      if (!token) {
        return;
      }
      try {
        const me = (await getMe(token)) as User;
        setUser(me);
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        setToken(null);
        setUser(null);
      }
    }
    void bootstrap();
  }, [token]);

  const loadPlants = useCallback(async () => {
    if (!token) {
      return;
    }
    setIsPlantsLoading(true);
    setPlantsError("");
    try {
      const data = await getPlants(token);
      setPlants(data);
    } catch (error) {
      setPlantsError(error instanceof Error ? error.message : "Failed to load plants");
    } finally {
      setIsPlantsLoading(false);
    }
  }, [token]);

  const loadAlerts = useCallback(async () => {
    if (!token) {
      return;
    }
    setIsAlertsLoading(true);
    setAlertsError("");
    try {
      const data = await getAlerts(token);
      setAlerts(data);
    } catch (error) {
      setAlertsError(error instanceof Error ? error.message : "Failed to load alerts");
    } finally {
      setIsAlertsLoading(false);
    }
  }, [token]);

  const loadSensors = useCallback(async () => {
    if (!token) {
      return;
    }
    setIsSensorsLoading(true);
    setSensorsError("");
    try {
      const data = await getSensors(token);
      setSensors(data);
    } catch (error) {
      setSensorsError(error instanceof Error ? error.message : "Failed to load sensors");
    } finally {
      setIsSensorsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (!token) {
      return;
    }
    void loadPlants();
    void loadAlerts();
    void loadSensors();
  }, [token, loadPlants, loadAlerts, loadSensors]);

  useEffect(() => {
    if (!token) {
      return;
    }
    const abortController = new AbortController();
    void fetchEventSource(`${API_BASE_URL}/stream/alerts`, {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
      signal: abortController.signal,
      onmessage(event) {
        if (event.event === "heartbeat") {
          return;
        }
        void loadAlerts();
      },
      onerror() {
        // fetch-event-source retries
      },
    });
    return () => abortController.abort();
  }, [token, loadAlerts]);

  const loginWithCredentials = useCallback(async (email: string, password: string) => {
    setIsAuthLoading(true);
    setAuthError("");
    try {
      const result = await login({ email, password });
      localStorage.setItem(TOKEN_KEY, result.access_token);
      setToken(result.access_token);
      setUser(result.user);
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : "Login failed");
      throw error;
    } finally {
      setIsAuthLoading(false);
    }
  }, []);

  const registerAccount = useCallback(
    async (
      fullName: string,
      email: string,
      password: string,
      passwordConfirm: string
    ): Promise<boolean> => {
      setIsAuthLoading(true);
      setAuthError("");
      if (password !== passwordConfirm) {
        setAuthError("Passwords do not match");
        setIsAuthLoading(false);
        return false;
      }
      try {
        await register({
          full_name: fullName,
          email,
          password,
          password_confirm: passwordConfirm,
        });
        setAuthError("");
        return true;
      } catch (error) {
        setAuthError(error instanceof Error ? error.message : "Registration failed");
        return false;
      } finally {
        setIsAuthLoading(false);
      }
    },
    []
  );

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
    setPlants([]);
    setAlerts([]);
    setSensors([]);
  }, []);

  const createPlantEntry = useCallback(
    async (payload: {
      name: string;
      species?: string;
      location?: string;
      description?: string;
    }) => {
      if (!token) {
        return;
      }
      setPlantsError("");
      try {
        await createPlant(token, payload);
        await loadPlants();
      } catch (error) {
        setPlantsError(error instanceof Error ? error.message : "Failed to create plant");
        throw error;
      }
    },
    [token, loadPlants]
  );

  const createSensorEntry = useCallback(
    async (deviceId: string, type: string) => {
      if (!token) {
        return null;
      }
      setSensorsError("");
      try {
        const result = await createSensor(token, deviceId, type);
        await loadSensors();
        return result.device_token;
      } catch (error) {
        setSensorsError(error instanceof Error ? error.message : "Failed to create sensor");
        throw error;
      }
    },
    [token, loadSensors]
  );

  const rotateSensorDeviceToken = useCallback(
    async (sensorId: number) => {
      if (!token) {
        return null;
      }
      setSensorsError("");
      try {
        const result = await rotateSensorToken(token, sensorId);
        await loadSensors();
        return result.device_token;
      } catch (error) {
        setSensorsError(error instanceof Error ? error.message : "Failed to rotate sensor token");
        throw error;
      }
    },
    [token, loadSensors]
  );

  const attachSensorToPlant = useCallback(
    async (sensorId: number, plantId: number) => {
      if (!token) {
        return;
      }
      setSensorsError("");
      try {
        await attachSensor(token, sensorId, plantId);
        await loadSensors();
      } catch (error) {
        setSensorsError(error instanceof Error ? error.message : "Failed to attach sensor");
        throw error;
      }
    },
    [token, loadSensors]
  );

  const detachSensorFromPlant = useCallback(
    async (sensorId: number) => {
      if (!token) {
        return;
      }
      setSensorsError("");
      try {
        await detachSensor(token, sensorId);
        await loadSensors();
      } catch (error) {
        setSensorsError(error instanceof Error ? error.message : "Failed to detach sensor");
        throw error;
      }
    },
    [token, loadSensors]
  );

  const markAlertViewed = useCallback(
    async (alertId: number) => {
      if (!token) {
        return;
      }
      await transitionAlert(token, alertId, "viewed");
      await loadAlerts();
    },
    [token, loadAlerts]
  );

  const acknowledgeAlert = useCallback(
    async (alertId: number) => {
      if (!token) {
        return;
      }
      await transitionAlert(token, alertId, "acknowledged");
      await loadAlerts();
    },
    [token, loadAlerts]
  );

  const resolveAlert = useCallback(
    async (alertId: number) => {
      if (!token) {
        return;
      }
      await transitionAlert(token, alertId, "resolved");
      await loadAlerts();
    },
    [token, loadAlerts]
  );

  const closeAlert = useCallback(
    async (alertId: number) => {
      if (!token) {
        return;
      }
      await transitionAlert(token, alertId, "closed");
      await loadAlerts();
    },
    [token, loadAlerts]
  );

  const value = useMemo<AppStateContextValue>(
    () => ({
      token,
      user,
      plants,
      alerts,
      sensors,
      isAuthLoading,
      isPlantsLoading,
      isAlertsLoading,
      isSensorsLoading,
      authError,
      plantsError,
      alertsError,
      sensorsError,
      setAuthError,
      loadPlants,
      loadAlerts,
      loadSensors,
      loginWithCredentials,
      registerAccount,
      logout,
      createPlantEntry,
      createSensorEntry,
      rotateSensorDeviceToken,
      attachSensorToPlant,
      detachSensorFromPlant,
      markAlertViewed,
      acknowledgeAlert,
      resolveAlert,
      closeAlert,
    }),
    [
      token,
      user,
      plants,
      alerts,
      sensors,
      isAuthLoading,
      isPlantsLoading,
      isAlertsLoading,
      isSensorsLoading,
      authError,
      plantsError,
      alertsError,
      sensorsError,
      loadPlants,
      loadAlerts,
      loadSensors,
      loginWithCredentials,
      registerAccount,
      logout,
      createPlantEntry,
      createSensorEntry,
      rotateSensorDeviceToken,
      attachSensorToPlant,
      detachSensorFromPlant,
      markAlertViewed,
      acknowledgeAlert,
      resolveAlert,
      closeAlert,
    ]
  );

  return <AppStateContext.Provider value={value}>{children}</AppStateContext.Provider>;
}

export function useAppState() {
  const ctx = useContext(AppStateContext);
  if (!ctx) {
    throw new Error("useAppState must be used within AppStateProvider");
  }
  return ctx;
}
