from pydantic import BaseModel

from app.application.schemas.dashboard import CareTextItem


class PlantCareProfileResponse(BaseModel):
    slug: str
    canonical_species: str
    display_names: dict[str, str]
    thresholds: dict
    basic_care: list[CareTextItem]
    gardener_advice: list[CareTextItem]
