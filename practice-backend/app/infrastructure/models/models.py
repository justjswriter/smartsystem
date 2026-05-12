from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import (
    AlertSeverity,
    AlertStatus,
    NotificationSeverity,
    NotificationType,
    SensorStatus,
    SensorType,
    UserRole,
)
from app.infrastructure.models.base import Base, TimestampMixin


def _enum_values(enum_cls):
    return [item.value for item in enum_cls]


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=_enum_values),
        default=UserRole.USER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    plants: Mapped[list[Plant]] = relationship(back_populates="owner")
    alerts: Mapped[list[Alert]] = relationship(back_populates="user")
    notifications: Mapped[list[Notification]] = relationship(back_populates="user")
    notification_settings: Mapped[UserNotificationSettings | None] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )


class Plant(Base, TimestampMixin):
    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    species: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    owner: Mapped[User] = relationship(back_populates="plants")
    sensors: Mapped[list[Sensor]] = relationship(back_populates="plant")
    alerts: Mapped[list[Alert]] = relationship(back_populates="plant")
    recommendations: Mapped[list[Recommendation]] = relationship(back_populates="plant")
    notifications: Mapped[list[Notification]] = relationship(back_populates="plant")


class Sensor(Base, TimestampMixin):
    __tablename__ = "sensors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    device_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    device_token_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    type: Mapped[SensorType] = mapped_column(
        Enum(SensorType, name="sensor_type", values_callable=_enum_values),
        default=SensorType.MULTI,
        nullable=False,
    )
    status: Mapped[SensorStatus] = mapped_column(
        Enum(SensorStatus, name="sensor_status", values_callable=_enum_values),
        default=SensorStatus.OFFLINE,
        nullable=False,
    )
    plant_id: Mapped[int | None] = mapped_column(ForeignKey("plants.id"), index=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_ingest_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_error_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    plant: Mapped[Plant | None] = relationship(back_populates="sensors")
    data_points: Mapped[list[SensorData]] = relationship(back_populates="sensor")
    alerts: Mapped[list[Alert]] = relationship(back_populates="sensor")
    notifications: Mapped[list[Notification]] = relationship(back_populates="sensor")


class SensorData(Base):
    __tablename__ = "sensor_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sensor_id: Mapped[int] = mapped_column(ForeignKey("sensors.id"), index=True, nullable=False)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), index=True, nullable=False)
    moisture: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    light: Mapped[float | None] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    sensor: Mapped[Sensor] = relationship(back_populates="data_points")

    __table_args__ = (Index("ix_sensor_data_sensor_recorded", "sensor_id", "recorded_at"),)


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), index=True, nullable=False)
    sensor_id: Mapped[int | None] = mapped_column(ForeignKey("sensors.id"), index=True, nullable=True)
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, name="alert_status", values_callable=_enum_values),
        default=AlertStatus.CREATED,
        nullable=False,
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity, name="alert_severity", values_callable=_enum_values),
        default=AlertSeverity.MEDIUM,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metric: Mapped[str | None] = mapped_column(String(50), nullable=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    threshold: Mapped[float | None] = mapped_column(Float, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="alerts")
    plant: Mapped[Plant] = relationship(back_populates="alerts")
    sensor: Mapped[Sensor | None] = relationship(back_populates="alerts")
    transitions: Mapped[list[AlertTransition]] = relationship(back_populates="alert")
    recommendations: Mapped[list[Recommendation]] = relationship(back_populates="alert")
    notifications: Mapped[list[Notification]] = relationship(back_populates="alert")

    __table_args__ = (Index("ix_alerts_user_status_created", "user_id", "status", "created_at"),)

    @property
    def recommendation(self) -> str | None:
        if not self.recommendations:
            return None
        active = [item for item in self.recommendations if item.is_active]
        item = active[0] if active else self.recommendations[0]
        return item.text


class AlertTransition(Base):
    __tablename__ = "alert_transitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id"), index=True, nullable=False)
    from_status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, name="alert_status_transition_from", values_callable=_enum_values),
        nullable=False,
    )
    to_status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, name="alert_status_transition_to", values_callable=_enum_values),
        nullable=False,
    )
    changed_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    alert: Mapped[Alert] = relationship(back_populates="transitions")


class Recommendation(Base, TimestampMixin):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), index=True, nullable=False)
    alert_id: Mapped[int | None] = mapped_column(ForeignKey("alerts.id"), index=True, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    plant: Mapped[Plant] = relationship(back_populates="recommendations")
    alert: Mapped[Alert | None] = relationship(back_populates="recommendations")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type", values_callable=_enum_values),
        nullable=False,
    )
    severity: Mapped[NotificationSeverity] = mapped_column(
        Enum(NotificationSeverity, name="notification_severity", values_callable=_enum_values),
        default=NotificationSeverity.INFO,
        nullable=False,
    )
    title_key: Mapped[str] = mapped_column(String(255), nullable=False)
    message_key: Mapped[str] = mapped_column(String(255), nullable=False)
    params: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_plant_id: Mapped[int | None] = mapped_column(ForeignKey("plants.id"), index=True, nullable=True)
    related_alert_id: Mapped[int | None] = mapped_column(ForeignKey("alerts.id"), index=True, nullable=True)
    related_sensor_id: Mapped[int | None] = mapped_column(ForeignKey("sensors.id"), index=True, nullable=True)
    dedupe_key: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()"), index=True
    )

    user: Mapped[User] = relationship(back_populates="notifications")
    plant: Mapped[Plant | None] = relationship(back_populates="notifications")
    alert: Mapped[Alert | None] = relationship(back_populates="notifications")
    sensor: Mapped[Sensor | None] = relationship(back_populates="notifications")

    __table_args__ = (
        Index("ix_notifications_user_read_created", "user_id", "read_at", "created_at"),
        Index("ix_notifications_user_dedupe_read", "user_id", "dedupe_key", "read_at"),
    )


class UserNotificationSettings(Base, TimestampMixin):
    __tablename__ = "user_notification_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    notification_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    critical_only: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="notification_settings")


class SystemLog(Base):
    __tablename__ = "system_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()"), index=True
    )
