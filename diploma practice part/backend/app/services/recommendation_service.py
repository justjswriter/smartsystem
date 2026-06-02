from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.recommendation_repository import RecommendationRepository
from app.schemas.recommendation import RecommendationItemOut, RecommendationListOut
from app.services import plant_service


def list_recent_recommendations(
    db: Session, user: User, plant_id: int, limit: int = 10
) -> RecommendationListOut:
    plant_service.get_plant_entity_for_user(db, user, plant_id, allow_inactive=False)
    rows = RecommendationRepository(db).list_recent_for_plant(plant_id, limit=limit)
    return RecommendationListOut(
        items=[RecommendationItemOut.model_validate(r) for r in rows]
    )
