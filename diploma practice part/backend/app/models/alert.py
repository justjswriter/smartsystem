import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AlertSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"  # one abnormal metric (treat as "warning" severity in product copy)
    high = "high"
    critical = "critical"


class AlertStatus(str, enum.Enum):
    created = "created"
    viewed = "viewed"
    acknowledged = "acknowledged"
    resolved = "resolved"
    closed = "closed"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("plants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(64), default="threshold_breach", index=True)
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity, name="alertseverity", native_enum=True),
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, name="alertstatus", native_enum=True),
        default=AlertStatus.created,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    plant: Mapped["Plant"] = relationship("Plant", back_populates="alerts")
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation", back_populates="alert"
    )
