from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.models.plant import Plant


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, alert_id: int) -> Optional[Alert]:
        return self.db.get(Alert, alert_id)

    def get_for_plant(
        self, alert_id: int, plant_id: int
    ) -> Optional[Alert]:
        return self.db.execute(
            select(Alert).where(Alert.id == alert_id, Alert.plant_id == plant_id)
        ).scalar_one_or_none()

    def get_for_user(
        self, alert_id: int, user_id: int
    ) -> Optional[Alert]:
        q = (
            select(Alert)
            .join(Plant, Plant.id == Alert.plant_id)
            .where(Alert.id == alert_id, Plant.user_id == user_id)
        )
        return self.db.execute(q).scalar_one_or_none()

    def list_for_user(
        self, user_id: int, status_filter: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> tuple[List[Alert], int]:
        j = (Alert.plant_id == Plant.id) & (Plant.user_id == user_id)
        count_q = select(func.count()).select_from(Alert).join(Plant, j)
        list_q = select(Alert).join(Plant, j)
        if status_filter and status_filter in {e.name for e in AlertStatus}:
            st = AlertStatus[status_filter]
            count_q = count_q.where(Alert.status == st)
            list_q = list_q.where(Alert.status == st)
        total = int(self.db.execute(count_q).scalar() or 0)
        list_q = list_q.order_by(desc(Alert.created_at)).offset(offset).limit(limit)
        items = list(self.db.execute(list_q).scalars().all())
        return items, total

    def list_open_for_plant(self, plant_id: int) -> List[Alert]:
        q = (
            select(Alert)
            .where(Alert.plant_id == plant_id, Alert.status != AlertStatus.closed)
        )
        return list(self.db.execute(q).scalars().all())

    def count_open_for_user(self, user_id: int) -> int:
        c = self.db.execute(
            select(func.count())
            .select_from(Alert)
            .join(Plant, Plant.id == Alert.plant_id)
            .where(Plant.user_id == user_id, Alert.status != AlertStatus.closed)
        ).scalar()
        return int(c or 0)

    def create(
        self,
        plant_id: int,
        alert_type: str,
        severity: AlertSeverity,
        message: str,
        status: AlertStatus = AlertStatus.created,
        commit: bool = True,
    ) -> Alert:
        a = Alert(
            plant_id=plant_id,
            type=alert_type,
            severity=severity,
            message=message,
            status=status,
        )
        self.db.add(a)
        if commit:
            self.db.commit()
            self.db.refresh(a)
        else:
            self.db.flush()
            self.db.refresh(a)
        return a

    def save(self, alert: Alert) -> Alert:
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert
