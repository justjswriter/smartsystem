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
  deletePlant,
  detachSensor,
  getAlerts,
  getMe,
  getNotifications,
  getPlants,
  getSensors,
  login,
  markAllNotificationsRead,
  markNotificationRead,
  register,
  rotateSensorToken,
  transitionAlert,
  updateMe,
  updatePlant,
  uploadProfilePhoto,
} from "../api";
import type { Alert, Notification, Plant, Sensor, User } from "../types";

const TOKEN_KEY = "smart-plant-token";

type AppStateContextValue = {
  token: string | null;
  user: User | null;
  plants: Plant[];
  alerts: Alert[];
  notifications: Notification[];
  sensors: Sensor[];
  isAuthLoading: boolean;
  isPlantsLoading: boolean;
  isAlertsLoading: boolean;
  isNotificationsLoading: boolean;
  isSensorsLoading: boolean;
  authError: string;
  plantsError: string;
  alertsError: string;
  notificationsError: string;
  sensorsError: string;
  setAuthError: (message: string) => void;
  loadPlants: () => Promise<void>;
  loadAlerts: () => Promise<void>;
  loadNotifications: () => Promise<void>;
  loadSensors: () => Promise<void>;
  loginWithCredentials: (email: string, password: string) => Promise<void>;
  registerAccount: (
    fullName: string,
    email: string,
    password: string,
    passwordConfirm: string
  ) => Promise<boolean>;
  updateProfile: (payload: { full_name?: string; email?: string }) => Promise<void>;
  updateProfilePhoto: (file: File) => Promise<void>;
  logout: () => void;
  createPlantEntry: (payload: {
    name: string;
    species?: string;
    location?: string;
    description?: string;
  }) => Promise<void>;
  deletePlantEntry: (plantId: number) => Promise<void>;
  renamePlantEntry: (plantId: number, name: string) => Promise<void>;
  createSensorEntry: (deviceId: string, type: string) => Promise<string | null>;
  rotateSensorDeviceToken: (sensorId: number) => Promise<string | null>;
  attachSensorToPlant: (sensorId: number, plantId: number) => Promise<void>;
  detachSensorFromPlant: (sensorId: number) => Promise<void>;
  markAlertViewed: (alertId: number) => Promise<void>;
  acknowledgeAlert: (alertId: number) => Promise<void>;
  resolveAlert: (alertId: number) => Promise<void>;
  closeAlert: (alertId: number) => Promise<void>;
  markNotificationAsRead: (notificationId: number) => Promise<void>;
  markAllNotificationsAsRead: () => Promise<void>;
};

const AppStateContext = createContext<AppStateContextValue | null>(null);

export function AppStateProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState<User | null>(null);
  const [plants, setPlants] = useState<Plant[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [sensors, setSensors] = useState<Sensor[]>([]);
  const [isAuthLoading, setIsAuthLoading] = useState(() => Boolean(localStorage.getItem(TOKEN_KEY)));
  const [isPlantsLoading, setIsPlantsLoading] = useState(false);
  const [isAlertsLoading, setIsAlertsLoading] = useState(false);
  const [isNotificationsLoading, setIsNotificationsLoading] = useState(false);
  const [isSensorsLoading, setIsSensorsLoading] = useState(false);
  const [authError, setAuthError] = useState("");
  const [plantsError, setPlantsError] = useState("");
  const [alertsError, setAlertsError] = useState("");
  const [notificationsError, setNotificationsError] = useState("");
  const [sensorsError, setSensorsError] = useState("");

  useEffect(() => {
    async function bootstrap() {
      if (!token) {
        setIsAuthLoading(false);
        return;
      }
      setIsAuthLoading(true);
      try {
        const me = (await getMe(token)) as User;
        setUser(me);
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        setToken(null);
        setUser(null);
      } finally {
        setIsAuthLoading(false);
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

  const loadNotifications = useCallback(async () => {
    if (!token) {
      return;
    }
    setIsNotificationsLoading(true);
    setNotificationsError("");
    try {
      const data = await getNotifications(token, true);
      setNotifications(data);
    } catch (error) {
      setNotificationsError(error instanceof Error ? error.message : "Failed to load notifications");
    } finally {
      setIsNotificationsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (!token) {
      return;
    }
    void loadPlants();
    void loadAlerts();
    void loadNotifications();
    void loadSensors();
  }, [token, loadPlants, loadAlerts, loadNotifications, loadSensors]);

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

  useEffect(() => {
    if (!token) {
      return;
    }
    const abortController = new AbortController();
    void fetchEventSource(`${API_BASE_URL}/stream/notifications`, {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` },
      signal: abortController.signal,
      onmessage(event) {
        if (event.event === "heartbeat") {
          return;
        }
        void loadNotifications();
      },
      onerror() {
        // fetch-event-source retries
      },
    });
    return () => abortController.abort();
  }, [token, loadNotifications]);

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

  const updateProfile = useCallback(
    async (payload: { full_name?: string; email?: string }) => {
      if (!token) {
        return;
      }
      setAuthError("");
      try {
        const updated = await updateMe(token, payload);
        setUser(updated);
      } catch (error) {
        setAuthError(error instanceof Error ? error.message : "Failed to update profile");
        throw error;
      }
    },
    [token]
  );

  const updateProfilePhoto = useCallback(
    async (file: File) => {
      if (!token) {
        return;
      }
      setAuthError("");
      try {
        const updated = await uploadProfilePhoto(token, file);
        setUser(updated);
      } catch (error) {
        setAuthError(error instanceof Error ? error.message : "Failed to update profile photo");
        throw error;
      }
    },
    [token]
  );

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
    setPlants([]);
    setAlerts([]);
    setNotifications([]);
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

  const deletePlantEntry = useCallback(
    async (plantId: number) => {
      if (!token) {
        return;
      }
      setPlantsError("");
      try {
        await deletePlant(token, plantId);
        await loadPlants();
        await loadSensors();
      } catch (error) {
        setPlantsError(error instanceof Error ? error.message : "Failed to delete plant");
        throw error;
      }
    },
    [token, loadPlants, loadSensors]
  );

  const renamePlantEntry = useCallback(
    async (plantId: number, name: string) => {
      if (!token) {
        return;
      }
      setPlantsError("");
      try {
        await updatePlant(token, plantId, { name });
        await loadPlants();
      } catch (error) {
        setPlantsError(error instanceof Error ? error.message : "Failed to rename plant");
        throw error;
      }
    },
    [token, loadPlants]
  );

  const markNotificationAsRead = useCallback(
    async (notificationId: number) => {
      if (!token) {
        return;
      }
      await markNotificationRead(token, notificationId);
      await loadNotifications();
    },
    [token, loadNotifications]
  );

  const markAllNotificationsAsRead = useCallback(async () => {
    if (!token) {
      return;
    }
    await markAllNotificationsRead(token);
    await loadNotifications();
  }, [token, loadNotifications]);

  const value = useMemo<AppStateContextValue>(
    () => ({
      token,
      user,
      plants,
      alerts,
      notifications,
      sensors,
      isAuthLoading,
      isPlantsLoading,
      isAlertsLoading,
      isNotificationsLoading,
      isSensorsLoading,
      authError,
      plantsError,
      alertsError,
      notificationsError,
      sensorsError,
      setAuthError,
      loadPlants,
      loadAlerts,
      loadNotifications,
      loadSensors,
      loginWithCredentials,
      registerAccount,
      updateProfile,
      updateProfilePhoto,
      logout,
      createPlantEntry,
      deletePlantEntry,
      renamePlantEntry,
      createSensorEntry,
      rotateSensorDeviceToken,
      attachSensorToPlant,
      detachSensorFromPlant,
      markAlertViewed,
      acknowledgeAlert,
      resolveAlert,
      closeAlert,
      markNotificationAsRead,
      markAllNotificationsAsRead,
    }),
    [
      token,
      user,
      plants,
      alerts,
      notifications,
      sensors,
      isAuthLoading,
      isPlantsLoading,
      isAlertsLoading,
      isNotificationsLoading,
      isSensorsLoading,
      authError,
      plantsError,
      alertsError,
      notificationsError,
      sensorsError,
      loadPlants,
      loadAlerts,
      loadNotifications,
      loadSensors,
      loginWithCredentials,
      registerAccount,
      updateProfile,
      updateProfilePhoto,
      logout,
      createPlantEntry,
      deletePlantEntry,
      renamePlantEntry,
      createSensorEntry,
      rotateSensorDeviceToken,
      attachSensorToPlant,
      detachSensorFromPlant,
      markAlertViewed,
      acknowledgeAlert,
      resolveAlert,
      closeAlert,
      markNotificationAsRead,
      markAllNotificationsAsRead,
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
