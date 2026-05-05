from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plant_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("plants.id", ondelete="CASCADE"), nullable=True, index=True
    )
    sensor_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sensors.id", ondelete="SET NULL"), nullable=True, index=True
    )
    device_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    soil_moisture_raw: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    soil_moisture_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    humidity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    light_raw: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    light_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    plant: Mapped[Optional["Plant"]] = relationship("Plant", back_populates="readings")
    sensor: Mapped[Optional["Sensor"]] = relationship("Sensor", back_populates="readings")
