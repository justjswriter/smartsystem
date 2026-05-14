from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class SensorType(str, Enum):
    SOIL_MOISTURE = "soil_moisture"
    TEMPERATURE = "temperature"
    AIR_HUMIDITY = "air_humidity"
    LIGHT = "light"
    MULTI = "multi"


class SensorStatus(str, Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    DISABLED = "disabled"


class AlertStatus(str, Enum):
    CREATED = "created"
    VIEWED = "viewed"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(str, Enum):
    PLANT_CONDITION = "plant_condition"
    CRITICAL_ALERT = "critical_alert"
    SENSOR_STALE = "sensor_stale"
    SENSOR_SUBSCRIPTION = "sensor_subscription"


class NotificationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
