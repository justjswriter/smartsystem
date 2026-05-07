export type User = {
  id: number;
  email: string;
  full_name: string;
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
  id: number;
  text: string;
  reason: string | null;
  created_at: string;
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

export type AdminLog = {
  id: number;
  user_id: number | null;
  event_type: string;
  message: string;
  payload: Record<string, unknown> | null;
  created_at: string;
};
