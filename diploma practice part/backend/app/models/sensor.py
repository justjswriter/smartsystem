import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.plant import Plant
    from app.models.sensor_reading import SensorReading


class SensorType(str, enum.Enum):
    soil_moisture = "soil_moisture"
    temperature = "temperature"
    humidity = "humidity"
    light = "light"
    multi = "multi"


class SensorStatus(str, enum.Enum):
    online = "online"
    offline = "offline"
    disabled = "disabled"


class Sensor(Base):
    __tablename__ = "sensors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plant_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("plants.id", ondelete="SET NULL"), nullable=True, index=True
    )
    device_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    sensor_type: Mapped[SensorType] = mapped_column(
        Enum(SensorType, name="sensortype", native_enum=True), default=SensorType.multi
    )
    status: Mapped[SensorStatus] = mapped_column(
        Enum(SensorStatus, name="sensorstatus", native_enum=True),
        default=SensorStatus.offline,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    plant: Mapped[Optional["Plant"]] = relationship("Plant", back_populates="sensors")
    readings: Mapped[List["SensorReading"]] = relationship(
        "SensorReading", back_populates="sensor"
    )
