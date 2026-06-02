from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.alert import AlertSeverity, AlertStatus


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: int
    plant_id: int
    type: str
    severity: str
    message: str
    status: str
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class AlertListResponse(BaseModel):
    total: int
    items: List[AlertOut]
