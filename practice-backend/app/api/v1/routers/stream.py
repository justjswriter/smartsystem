import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.domain.enums import UserRole
from app.infrastructure.models import User
from app.infrastructure.repositories import PlantRepository
from app.infrastructure.services.event_bus import event_bus

router = APIRouter(prefix="/stream", tags=["stream"])


def _event_payload(event: dict) -> dict:
    return {"event": event.get("event", "message"), "data": json.dumps(event)}


@router.get("/alerts")
async def stream_alerts(current_user: User = Depends(get_current_user)):
    queue = event_bus.subscribe(f"alerts:{current_user.id}")

    async def event_generator():
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=settings.SSE_HEARTBEAT_SECONDS)
                    yield _event_payload(event)
                except TimeoutError:
                    yield {"event": "heartbeat", "data": "keepalive"}
        finally:
            event_bus.unsubscribe(f"alerts:{current_user.id}", queue)

    return EventSourceResponse(event_generator())


@router.get("/dashboard/{plant_id}")
async def stream_dashboard(
    plant_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != UserRole.ADMIN:
        plant = await PlantRepository(db).get_for_user(plant_id, current_user.id)
        if not plant:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Plant stream access denied")
    queue = event_bus.subscribe(f"dashboard:{plant_id}")

    async def event_generator():
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=settings.SSE_HEARTBEAT_SECONDS)
                    yield _event_payload(event)
                except TimeoutError:
                    yield {"event": "heartbeat", "data": "keepalive"}
        finally:
            event_bus.unsubscribe(f"dashboard:{plant_id}", queue)

    return EventSourceResponse(event_generator())
