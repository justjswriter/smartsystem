from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories import (
    AlertRepository,
    SensorRepository,
    SystemLogRepository,
    UserRepository,
)


class AdminService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.sensor_repo = SensorRepository(db)
        self.alert_repo = AlertRepository(db)
        self.log_repo = SystemLogRepository(db)

    async def users(self, *, limit: int, offset: int):
        return await self.user_repo.list(limit=limit, offset=offset)

    async def sensors(self, *, limit: int, offset: int):
        return await self.sensor_repo.list(limit=limit, offset=offset)

    async def alerts(self, *, limit: int, offset: int):
        return await self.alert_repo.list_all(limit=limit, offset=offset)

    async def system_logs(self, *, limit: int, offset: int):
        return await self.log_repo.list(limit=limit, offset=offset)
