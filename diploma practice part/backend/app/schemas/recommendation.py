from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class RecommendationItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    explanation: Optional[str] = None
    created_at: Optional[datetime] = None


class RecommendationListOut(BaseModel):
    items: List[RecommendationItemOut]
