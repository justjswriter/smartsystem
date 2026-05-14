from app.application.schemas.plant_care_profile import PlantCareProfileResponse
from app.infrastructure.repositories import PlantCareProfileRepository


class PlantCareProfileService:
    def __init__(self, db) -> None:
        self.repo = PlantCareProfileRepository(db)

    async def list_profiles(self) -> list[PlantCareProfileResponse]:
        profiles = await self.repo.list_active()
        return [self._to_response(profile) for profile in profiles]

    async def get_by_species(self, species: str | None) -> PlantCareProfileResponse | None:
        profile = await self.repo.get_by_species(species)
        return self._to_response(profile) if profile else None

    @staticmethod
    def _to_response(profile) -> PlantCareProfileResponse:
        return PlantCareProfileResponse.model_validate(
            {
                "slug": profile.slug,
                "canonical_species": profile.canonical_species,
                "display_names": profile.display_names,
                "thresholds": profile.thresholds,
                "basic_care": profile.basic_care,
                "gardener_advice": profile.gardener_advice,
            }
        )
