export type User = {
  id: number;
  email: string;
  full_name: string;
  avatar_url?: string | null;
  role: string;
  is_active?: boolean;
  created_at?: string;
};

export type AuthResponse = {
  access_token: string;
  user: User;
};

export type RegisterPayload = {
  full_name: string;
  email: string;
  password: string;
  password_confirm: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type UserUpdatePayload = {
  full_name?: string;
  email?: string;
};

export type PasswordUpdatePayload = {
  current_password: string;
  new_password: string;
  new_password_confirm: string;
};

export type Plant = {
  id: number;
  name: string;
  species?: string;
  location?: string;
  description?: string;
  image_url?: string;
  health?: number;
  notes?: string;
};

export type DashboardPoint = {
  recorded_at: string;
  moisture: number | null;
  temperature: number | null;
  humidity: number | null;
  light: number | null;
};

export type DashboardResponse = {
  plant_id: number;
  last_updated_at: string | null;
  current: DashboardPoint | null;
  history: DashboardPoint[];
  condition: PlantCondition;
  active_recommendation: RecommendationSummary | null;
  care_profile?: CareProfile | null;
  today_care?: CareActionItem[];
};

export type CareTextItem = {
  icon: "water" | "light" | "humidity" | "temperature" | string;
  color: "blue" | "amber" | "green" | "orange" | string;
  title: string;
  text: string;
};

export type CareActionItem = CareTextItem & {
  detail?: string | null;
  status?: "normal" | "attention" | "warning" | "critical" | "unknown" | string | null;
};

export type CareProfile = {
  slug: string;
  canonical_species: string;
  display_names: Record<string, string>;
  thresholds: Record<string, unknown>;
  basic_care: CareTextItem[];
  gardener_advice: CareTextItem[];
};

export type PlantCondition = {
  condition_status: "normal" | "attention" | "critical" | "insufficient_data" | string;
  health_score: number | null;
  risk_factors: string[];
  confidence: number;
  explanation: string;
  ml_prediction: "normal" | "attention" | "critical" | string | null;
  ml_confidence: number | null;
  class_probabilities: Record<string, number>;
  analysis_method: "hybrid_rule_based_and_ml" | "rule_based" | string;
};

export type RecommendationSummary = {
  id: number | null;
  text: string;
  reason: string | null;
  created_at: string | null;
  metric?: string | null;
  severity?: string | null;
  source?: "current_condition" | "historical_alert" | string;
};

export type AlertStatus = "created" | "viewed" | "acknowledged" | "resolved" | "closed";

export type Alert = {
  id: number;
  plant_id: number;
  sensor_id: number | null;
  status: AlertStatus;
  severity: string;
  title: string;
  message: string;
  metric: string | null;
  value: number | null;
  threshold: number | null;
  recommendation?: string | null;
  transitions?: AlertTransition[];
  created_at: string;
  updated_at: string;
};

export type AlertTransition = {
  id: number;
  alert_id: number;
  from_status: AlertStatus;
  to_status: AlertStatus;
  changed_by: number;
  note: string | null;
  changed_at: string;
};

export type Sensor = {
  id: number;
  user_id: number | null;
  device_id: string;
  type: string;
  status: string;
  plant_id: number | null;
  is_active: boolean;
  last_seen_at: string | null;
  last_ingest_source: string | null;
  last_error_at: string | null;
  last_error_message: string | null;
  created_at?: string;
  updated_at?: string;
};

export type SensorProvisionResponse = {
  sensor: Sensor;
  device_token: string;
};

export type Notification = {
  id: number;
  user_id: number;
  type: string;
  severity: "info" | "warning" | "critical" | string;
  title_key: string;
  message_key: string;
  params: Record<string, string | number | null | undefined> | null;
  title: string | null;
  message: string | null;
  related_plant_id: number | null;
  related_alert_id: number | null;
  related_sensor_id: number | null;
  dedupe_key: string | null;
  read_at: string | null;
  created_at: string;
};

export type NotificationSettings = {
  id: number;
  user_id: number;
  notification_email: string | null;
  email_enabled: boolean;
  critical_only: boolean;
  email_critical_alerts: boolean;
  email_moisture_alerts: boolean;
  email_temperature_alerts: boolean;
  email_humidity_alerts: boolean;
  email_light_alerts: boolean;
  verified_at: string | null;
  created_at: string;
  updated_at: string;
};

export type NotificationSettingsUpdate = {
  notification_email?: string | null;
  email_enabled?: boolean;
  critical_only?: boolean;
  email_critical_alerts?: boolean;
  email_moisture_alerts?: boolean;
  email_temperature_alerts?: boolean;
  email_humidity_alerts?: boolean;
  email_light_alerts?: boolean;
};

export type TestEmailResponse = {
  status: string;
  detail: string;
};

export type AdminLog = {
  id: number;
  user_id: number | null;
  event_type: string;
  message: string;
  payload: Record<string, unknown> | null;
  created_at: string;
};

export type AdminPlant = {
  id: number;
  user_id: number;
  name: string;
  species: string | null;
  location: string | null;
  created_at: string;
};
