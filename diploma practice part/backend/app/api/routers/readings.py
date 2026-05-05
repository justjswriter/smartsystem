from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.schemas.reading import IngestRequest, IngestResponse
from app.services import reading_service

router = APIRouter(prefix="/readings", tags=["readings"])


@router.post("/ingest", response_model=IngestResponse)
def ingest(
    data: IngestRequest,
    db: Session = Depends(get_db),
    x_api_key: Optional[str] = Header(default=None, alias="x-api-key"),
) -> IngestResponse:
    """
    ESP32 / device ingest. Secured with shared DEVICE_API_KEY in header x-api-key
    (not JWT; devices do not have user accounts).
    """
    key = (x_api_key or "").strip()
    if not key or key != get_settings().DEVICE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing x-api-key",
        )
    return reading_service.ingest_reading(db, data)
