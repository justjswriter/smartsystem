from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.schemas.dashboard import CareActionItem, CareProfileResponse, DashboardPoint, DashboardResponse
from app.application.services.plant_condition_service import PlantConditionService
from app.application.services.recommendation_service import RecommendationService
from app.domain.plant_knowledge import resolve_plant_profile
from app.infrastructure.repositories import PlantCareProfileRepository, PlantRepository, SensorDataRepository


class MonitoringService:
    def __init__(self, db: AsyncSession):
        self.plant_repo = PlantRepository(db)
        self.sensor_data_repo = SensorDataRepository(db)
        self.care_profile_repo = PlantCareProfileRepository(db)
        self.condition_service = PlantConditionService()
        self.recommendation_service = RecommendationService(db)

    async def get_dashboard(self, *, user_id: int, plant_id: int, hours: int) -> DashboardResponse:
        plant = await self.plant_repo.get_for_user(plant_id, user_id)
        if not plant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")

        current_data = await self.sensor_data_repo.latest_for_plant(plant_id)
        history_data = await self.sensor_data_repo.history_for_plant(plant_id, hours)

        current = (
            DashboardPoint(
                recorded_at=current_data.recorded_at,
                moisture=current_data.moisture,
                temperature=current_data.temperature,
                humidity=current_data.humidity,
                light=current_data.light,
            )
            if current_data
            else None
        )
        history = [
            DashboardPoint(
                recorded_at=item.recorded_at,
                moisture=item.moisture,
                temperature=item.temperature,
                humidity=item.humidity,
                light=item.light,
            )
            for item in history_data
        ]
        plant_profile = resolve_plant_profile(getattr(plant, "species", None))
        care_profile_repo = getattr(self, "care_profile_repo", None)
        db_care_profile = (
            await care_profile_repo.get_by_species(getattr(plant, "species", None))
            if care_profile_repo
            else None
        )
        condition = self.condition_service.evaluate(current=current, history=history, plant_profile=plant_profile)
        active_recommendation = self.recommendation_service.build_current_recommendation(
            current=current,
            condition=condition,
            plant_profile=plant_profile,
        )
        return DashboardResponse(
            plant_id=plant_id,
            last_updated_at=current_data.recorded_at if current_data else None,
            current=current,
            history=history,
            condition=condition,
            active_recommendation=active_recommendation,
            care_profile=CareProfileResponse.model_validate(
                {
                    "slug": db_care_profile.slug,
                    "canonical_species": db_care_profile.canonical_species,
                    "display_names": db_care_profile.display_names,
                    "thresholds": db_care_profile.thresholds,
                    "basic_care": db_care_profile.basic_care,
                    "gardener_advice": db_care_profile.gardener_advice,
                }
            )
            if db_care_profile
            else None,
            today_care=self._build_today_care(current=current, history=history, condition=condition),
        )

    @staticmethod
    def _build_today_care(
        *,
        current: DashboardPoint | None,
        history: list[DashboardPoint],
        condition,
    ) -> list[CareActionItem]:
        if not current:
            return [
                CareActionItem(
                    icon="water",
                    color="blue",
                    title="Полив",
                    text="Пока нет свежих показаний. Проверьте почву пальцем: поливайте только если верхние 2 см сухие.",
                    detail="Совет рассчитан без сенсорных данных.",
                    status="unknown",
                ),
                CareActionItem(
                    icon="light",
                    color="amber",
                    title="Свет",
                    text="Держите растение рядом со светлым восточным или западным окном, без прямого полуденного солнца.",
                    detail="Совет рассчитан без сенсорных данных.",
                    status="unknown",
                ),
            ]

        moisture = current.moisture
        moisture_status = "unknown"
        if moisture is None:
            water_text = "Проверьте землю пальцем: поливайте только если верхние 2 см почвы сухие."
            water_detail = "Точного значения влажности почвы нет."
            moisture_status = "unknown"
        elif moisture < 35:
            water_text = "Сегодня полейте 150-250 мл отстоянной воды. Лейте небольшими порциями и не оставляйте воду в поддоне."
            water_detail = f"Сейчас влажность почвы: {moisture:g}%."
            moisture_status = "critical" if moisture < 20 else "warning"
        elif moisture < 45:
            water_text = "В ближайшие 24 часа слегка полейте или проверьте, подсох ли верхний слой почвы."
            water_detail = f"Сейчас влажность почвы: {moisture:g}%."
            moisture_status = "attention"
        elif moisture > 75:
            is_sustained = MonitoringService._is_sustained_high_moisture_in_history(
                history=history,
                threshold=75.0,
                current_time=current.recorded_at,
            )
            if is_sustained:
                water_text = "Почва слишком долго остаётся мокрой. Не поливайте 3-5 дней, слейте воду из поддона и проверьте дренаж."
                moisture_status = "critical"
            else:
                water_text = "Похоже, почва ещё влажная после недавнего полива. Сейчас не поливайте и просто проверьте позже."
                moisture_status = "attention"
            water_detail = f"Сейчас влажность почвы: {moisture:g}%."
        else:
            water_text = "Сейчас полив не нужен. Обычно поливайте 1-2 раза в неделю, когда верхние 2 см почвы подсохли."
            water_detail = f"Сейчас влажность почвы: {moisture:g}%."
            moisture_status = "attention" if moisture > 65 else "normal"

        light = current.light
        light_status = "unknown"
        if light is None:
            light_text = "Поставьте растение в светлое место без жёсткого прямого солнца."
            light_detail = "Точного показателя света нет."
        elif light < 40:
            light_text = "Подвиньте растение ближе к окну: лучше восточное или западное, но без прямого полуденного солнца."
            light_detail = f"Сейчас показатель света: {light:g}."
            light_status = "critical" if light < 20 else "warning"
        elif light > 180:
            light_text = "Если солнце жёсткое, отодвиньте горшок на 1-2 м от окна или закройте окно лёгкой шторой."
            light_detail = f"Сейчас показатель света: {light:g}."
            light_status = "critical" if light > 260 else "warning"
        else:
            light_text = "Место подходит. Оставьте растение здесь, если свет яркий и рассеянный."
            light_detail = f"Сейчас показатель света: {light:g}."
            light_status = "normal" if light >= 45 else "attention"

        humidity = current.humidity
        humidity_status = "unknown"
        if humidity is None:
            humidity_text = "Держите листья подальше от батареи, сухого потока воздуха и сквозняка."
            humidity_detail = "Точного значения влажности воздуха нет."
        elif humidity < 40:
            humidity_text = "Повысьте влажность: поставьте рядом поддон с водой, включите увлажнитель или сгруппируйте растения."
            humidity_detail = f"Сейчас влажность воздуха: {humidity:g}%."
            humidity_status = "critical" if humidity < 25 else "warning"
        elif humidity > 75:
            humidity_text = "Проветривайте комнату и следите, чтобы вода не стояла на листьях слишком долго."
            humidity_detail = f"Сейчас влажность воздуха: {humidity:g}%."
            humidity_status = "critical" if humidity > 85 else "warning"
        else:
            humidity_text = "Влажность воздуха подходит. Достаточно периодически протирать листья от пыли."
            humidity_detail = f"Сейчас влажность воздуха: {humidity:g}%."
            humidity_status = "normal" if 50 <= humidity <= 70 else "attention"

        temperature = current.temperature
        temperature_status = "unknown"
        if temperature is None:
            place_text = "Держите горшок в тёплом стабильном месте: подальше от батареи и холодного сквозняка."
            place_detail = "Точного значения температуры нет."
        elif temperature < 18:
            place_text = "Переставьте растение в более тёплое место и уберите от холодного окна или сквозняка."
            place_detail = f"Сейчас температура: {temperature:g}°C."
            temperature_status = "critical" if temperature < 16 else "warning"
        elif temperature > 30:
            place_text = "Переставьте растение в более прохладное место, дальше от батареи и прямого солнца."
            place_detail = f"Сейчас температура: {temperature:g}°C."
            temperature_status = "critical" if temperature > 34 else "warning"
        else:
            place_text = "Место комфортное. Держите горшок вдали от батареи, кондиционера и холодного сквозняка."
            place_detail = f"Сейчас температура: {temperature:g}°C."
            temperature_status = "normal" if 20 <= temperature <= 27 else "attention"

        return [
            CareActionItem(icon="water", color="blue", title="Полив", text=water_text, detail=water_detail, status=moisture_status),
            CareActionItem(icon="light", color="amber", title="Свет", text=light_text, detail=light_detail, status=light_status),
            CareActionItem(icon="humidity", color="green", title="Воздух", text=humidity_text, detail=humidity_detail, status=humidity_status),
            CareActionItem(icon="temperature", color="orange", title="Где держать", text=place_text, detail=place_detail, status=temperature_status),
        ]

    @staticmethod
    def _is_sustained_high_moisture_in_history(
        *,
        history: list[DashboardPoint],
        threshold: float,
        current_time,
    ) -> bool:
        points = [point for point in history if point.moisture is not None]
        if len(points) < 3:
            return False

        last_normal_at = None
        for point in points:
            if point.moisture is not None and point.moisture <= threshold:
                last_normal_at = point.recorded_at

        high_after_normal = [
            point
            for point in points
            if point.moisture is not None
            and point.moisture > threshold
            and (last_normal_at is None or point.recorded_at > last_normal_at)
        ]
        if len(high_after_normal) < 3:
            return False
        first_high_at = min(point.recorded_at for point in high_after_normal)
        return current_time - first_high_at >= timedelta(hours=48)
