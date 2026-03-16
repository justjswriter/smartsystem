import asyncio
from datetime import datetime, timezone
from pathlib import Path
import sys

from sqlalchemy import select

# Ensure project root is importable when script is run directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.domain.enums import AlertSeverity, AlertStatus, SensorStatus, SensorType, UserRole
from app.infrastructure.models import Alert, Plant, Sensor, User


async def get_or_create_user(session, *, full_name: str, email: str, password: str, role: UserRole) -> User:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        return user
    user = User(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_or_create_plant(session, *, user_id: int) -> Plant:
    result = await session.execute(
        select(Plant).where(Plant.user_id == user_id, Plant.name == "Demo Monstera", Plant.is_active.is_(True))
    )
    plant = result.scalar_one_or_none()
    if plant:
        return plant
    plant = Plant(
        user_id=user_id,
        name="Demo Monstera",
        species="Monstera Deliciosa",
        location="Living room",
        description="Seeded demo plant",
        is_active=True,
    )
    session.add(plant)
    await session.commit()
    await session.refresh(plant)
    return plant


async def get_or_create_sensor(session, *, plant_id: int) -> Sensor:
    device_id = "demo-sensor-001"
    result = await session.execute(select(Sensor).where(Sensor.device_id == device_id))
    sensor = result.scalar_one_or_none()
    if sensor:
        if sensor.plant_id != plant_id:
            sensor.plant_id = plant_id
            sensor.status = SensorStatus.ONLINE
            sensor.last_seen_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(sensor)
        return sensor
    sensor = Sensor(
        device_id=device_id,
        type=SensorType.SOIL_MOISTURE,
        status=SensorStatus.ONLINE,
        plant_id=plant_id,
        is_active=True,
        last_seen_at=datetime.now(timezone.utc),
    )
    session.add(sensor)
    await session.commit()
    await session.refresh(sensor)
    return sensor


async def get_or_create_alert(session, *, user_id: int, plant_id: int, sensor_id: int) -> Alert:
    result = await session.execute(
        select(Alert).where(
            Alert.user_id == user_id,
            Alert.plant_id == plant_id,
            Alert.title == "Demo low moisture alert",
            Alert.status == AlertStatus.CREATED,
        )
    )
    alert = result.scalar_one_or_none()
    if alert:
        return alert
    alert = Alert(
        user_id=user_id,
        plant_id=plant_id,
        sensor_id=sensor_id,
        status=AlertStatus.CREATED,
        severity=AlertSeverity.MEDIUM,
        title="Demo low moisture alert",
        message="Seeded demo alert for presentation",
        metric="moisture",
        value=18.0,
        threshold=30.0,
    )
    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    return alert


async def main() -> None:
    async with AsyncSessionLocal() as session:
        demo_user = await get_or_create_user(
            session,
            full_name="Demo User",
            email="demo@example.com",
            password="DemoPass123!",
            role=UserRole.USER,
        )
        admin_user = await get_or_create_user(
            session,
            full_name="Demo Admin",
            email="admin@example.com",
            password="AdminPass123!",
            role=UserRole.ADMIN,
        )
        demo_plant = await get_or_create_plant(session, user_id=demo_user.id)
        demo_sensor = await get_or_create_sensor(session, plant_id=demo_plant.id)
        demo_alert = await get_or_create_alert(
            session,
            user_id=demo_user.id,
            plant_id=demo_plant.id,
            sensor_id=demo_sensor.id,
        )

        print("Demo seed ready:")
        print(f"- demo user: {demo_user.email} / DemoPass123!")
        print(f"- admin user: {admin_user.email} / AdminPass123!")
        print(f"- demo plant id: {demo_plant.id}")
        print(f"- demo sensor id: {demo_sensor.id} (device_id={demo_sensor.device_id})")
        print(f"- demo alert id: {demo_alert.id} (status={demo_alert.status.value})")


if __name__ == "__main__":
    asyncio.run(main())
