from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import AlertSeverity, AlertStatus
from app.infrastructure.repositories import (
    AlertRepository,
    PlantRepository,
    SensorRepository,
    SystemLogRepository,
    UserRepository,
)


class AdminService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.sensor_repo = SensorRepository(db)
        self.plant_repo = PlantRepository(db)
        self.alert_repo = AlertRepository(db)
        self.log_repo = SystemLogRepository(db)

    async def users(self, *, limit: int, offset: int):
        return await self.user_repo.list(limit=limit, offset=offset)

    async def sensors(self, *, limit: int, offset: int):
        return await self.sensor_repo.list(limit=limit, offset=offset)

    async def plants(self, *, limit: int, offset: int):
        return await self.plant_repo.list_all(limit=limit, offset=offset)

    async def alerts(self, *, limit: int, offset: int, status: AlertStatus | None, severity: AlertSeverity | None):
        return await self.alert_repo.list_all(limit=limit, offset=offset, status=status, severity=severity)

    async def system_logs(self, *, limit: int, offset: int, event_type=None, user_id=None, date_from=None, date_to=None):
        return await self.log_repo.list(
            limit=limit,
            offset=offset,
            event_type=event_type,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        )
