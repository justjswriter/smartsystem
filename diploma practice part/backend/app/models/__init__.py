# Import all models for Alembic and SQLAlchemy mapper configuration
from app.core.database import Base
from app.models.user import User, UserRole
from app.models.plant import Plant
from app.models.sensor import Sensor, SensorStatus, SensorType
from app.models.sensor_reading import SensorReading
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.models.recommendation import Recommendation

__all__ = [
    "Base",
    "User",
    "UserRole",
    "Plant",
    "Sensor",
    "SensorType",
    "SensorStatus",
    "SensorReading",
    "Alert",
    "AlertSeverity",
    "AlertStatus",
    "Recommendation",
]
