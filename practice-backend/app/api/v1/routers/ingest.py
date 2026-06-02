from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.schemas.sensor import SensorDataIngest
from app.application.services import AlertService
from app.core.database import get_db

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/sensors/{device_id}/data")
async def ingest_sensor_data(
    device_id: str,
    payload: SensorDataIngest,
    request: Request,
    x_device_token: str | None = Header(default=None, alias="X-Device-Token"),
    x_ingest_source: str | None = Header(default=None, alias="X-Ingest-Source"),
    db: AsyncSession = Depends(get_db),
):
    service = AlertService(db)
    try:
        data = await service.ingest_sensor_data(
            device_id=device_id,
            device_token=x_device_token,
            source=x_ingest_source or (request.client.host if request.client else None),
            payload=payload.model_dump(),
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return {"status": "accepted", "sensor_data_id": data.id}
