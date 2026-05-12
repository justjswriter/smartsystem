from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.application.schemas.notification_settings import (
    NotificationSettingsResponse,
    NotificationSettingsUpdate,
    TestEmailResponse,
)
from app.application.services import NotificationSettingsService
from app.core.database import get_db
from app.infrastructure.models import User

router = APIRouter(prefix="/notification-settings", tags=["notification-settings"])


@router.get("", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await NotificationSettingsService(db).get_for_user(user_id=current_user.id)


@router.patch("", response_model=NotificationSettingsResponse)
async def update_notification_settings(
    payload: NotificationSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await NotificationSettingsService(db).update_for_user(
        user_id=current_user.id,
        payload=payload,
    )


@router.post("/test-email", response_model=TestEmailResponse)
async def send_test_email(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await NotificationSettingsService(db).send_test_email(user_id=current_user.id)
