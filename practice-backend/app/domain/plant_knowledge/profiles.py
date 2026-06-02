from __future__ import annotations

from app.domain.plant_knowledge.types import (
    IssueDefinition,
    LocalizedText,
    MetricRange,
    PlantAdvice,
    PlantProfile,
)

DEFAULT_PLANT_PROFILE_SLUG = "common_tropical_aroid_vines"
CANONICAL_SPECIES = "Epipremnum aureum"
SUPPORTED_SPECIES = {
    "epipremnum aureum": "Epipremnum aureum",
    "golden pothos": "Epipremnum aureum",
    "philodendron hederaceum": "Philodendron hederaceum",
    "heartleaf philodendron": "Philodendron hederaceum",
    "scindapsus pictus": "Scindapsus pictus",
    "satin pothos": "Scindapsus pictus",
    "syngonium podophyllum": "Syngonium podophyllum",
    "arrowhead vine": "Syngonium podophyllum",
}


def _text(*, kk: str, ru: str, en: str) -> LocalizedText:
    return LocalizedText(kk=kk, ru=ru, en=en)


def _advice(*, text: LocalizedText, reason: LocalizedText) -> PlantAdvice:
    return PlantAdvice(text=text, reason=reason)


BASE_GOLDEN_POTHOS_PROFILE = PlantProfile(
    slug=DEFAULT_PLANT_PROFILE_SLUG,
    canonical_species=CANONICAL_SPECIES,
    names=_text(
        kk="Алтын потос / Эпипремнум",
        ru="Золотой потос / Эпипремнум",
            en="Common tropical aroid vine profile",
    ),
    thresholds={
        "moisture": MetricRange(min=35.0, max=75.0, optimal_min=45.0, optimal_max=65.0),
        "temperature": MetricRange(min=18.0, max=30.0, optimal_min=20.0, optimal_max=27.0),
        "humidity": MetricRange(min=40.0, max=80.0, optimal_min=50.0, optimal_max=70.0),
        "light": MetricRange(min=40.0, max=320.0, optimal_min=45.0, optimal_max=180.0),
    },
    issues={},
    stable_advice=_advice(
        text=_text(
            kk="Жағдай тұрақты. Қазіргі күтім режимін сақтап, сенсор трендтерін бақылауды жалғастырыңыз.",
            ru="Условия стабильны. Сохраните текущий режим ухода и продолжайте следить за трендами сенсоров.",
            en="Conditions are stable. Keep the current care routine and continue monitoring sensor trends.",
        ),
        reason=_text(
            kk="Соңғы сенсор мәндері Алтын потос үшін ұсынылған диапазонда.",
            ru="Последние сенсорные значения находятся в рекомендуемом диапазоне для золотого потоса.",
            en="Latest sensor values are within the shared tropical aroid care ranges.",
        ),
    ),
)


def _issue(
    *,
    code: str,
    metric: str,
    direction: str,
    threshold: float,
    title: LocalizedText,
    message: LocalizedText,
    advice_text: LocalizedText,
    advice_reason: LocalizedText,
) -> IssueDefinition:
    return IssueDefinition(
        code=code,
        metric=metric,
        direction=direction,
        threshold=threshold,
        title=title,
        message=message,
        advice=_advice(text=advice_text, reason=advice_reason),
    )


GOLDEN_POTHOS_ISSUES = {
    "low_moisture": _issue(
        code="low_moisture",
        metric="moisture",
        direction="below",
        threshold=BASE_GOLDEN_POTHOS_PROFILE.thresholds["moisture"].min or 0.0,
        title=_text(kk="Топырақ ылғалы төмен", ru="Низкая влажность почвы", en="Moisture threshold below"),
        message=_text(
            kk="Топырақ ылғалы Алтын потос үшін ұсынылған шектен төмен.",
            ru="Влажность почвы ниже рекомендуемого порога для золотого потоса.",
            en="Soil moisture is below the shared care threshold.",
        ),
        advice_text=_text(
            kk="Суару жиілігін арттырып, топырақты 2-4 сағаттан кейін қайта тексеріңіз.",
            ru="Увеличьте частоту полива и проверьте почву через 2-4 часа.",
            en="Water gradually until the top soil is evenly moist, then re-check soil moisture in 2-4 hours.",
        ),
        advice_reason=_text(
            kk="Алтын потос топырағы сәл ылғалды болғанын қалайды.",
            ru="Золотой потос предпочитает слегка влажную почву.",
            en="These indoor aroid vines prefer lightly moist, well-drained soil.",
        ),
    ),
    "high_moisture": _issue(
        code="high_moisture",
        metric="moisture",
        direction="above",
        threshold=BASE_GOLDEN_POTHOS_PROFILE.thresholds["moisture"].max or 100.0,
        title=_text(kk="Топырақ тым ылғалды", ru="Почва слишком влажная", en="Moisture threshold above"),
        message=_text(
            kk="Топырақ ылғалы Алтын потос үшін ұсынылған жоғарғы шектен жоғары.",
            ru="Влажность почвы выше верхнего порога для золотого потоса.",
            en="Soil moisture is above the shared care threshold.",
        ),
        advice_text=_text(
            kk="Суаруды уақытша тоқтатып, келесі суаруға дейін топырақтың кебуін күтіңіз.",
            ru="Временно остановите полив и дайте почве подсохнуть перед следующим поливом.",
            en="Pause watering and let the top layer of soil dry before the next watering.",
        ),
        advice_reason=_text(
            kk="Артық ылғал Алтын потос тамырына зиян келтіруі мүмкін.",
            ru="Избыточная влажность может навредить корням золотого потоса.",
            en="Excess moisture can stress roots and increase the risk of rot.",
        ),
    ),
    "low_temperature": _issue(
        code="low_temperature",
        metric="temperature",
        direction="below",
        threshold=BASE_GOLDEN_POTHOS_PROFILE.thresholds["temperature"].min or 0.0,
        title=_text(kk="Температура төмен", ru="Низкая температура", en="Temperature threshold below"),
        message=_text(
            kk="Температура Алтын потос үшін ұсынылған шектен төмен.",
            ru="Температура ниже рекомендуемого порога для золотого потоса.",
            en="Temperature is below the shared care threshold.",
        ),
        advice_text=_text(
            kk="Өсімдікті жылырақ жерге қойып, суық ауа ағынынан қорғаңыз.",
            ru="Переставьте растение в более тёплое место и защитите от сквозняков.",
            en="Move the plant to a warmer area and keep it away from cold drafts.",
        ),
        advice_reason=_text(
            kk="Алтын потос тұрақты жылы ортада жақсы өседі.",
            ru="Золотой потос лучше растёт в стабильной тёплой среде.",
            en="These indoor aroid vines grow best in a stable warm environment.",
        ),
    ),
    "high_temperature": _issue(
        code="high_temperature",
        metric="temperature",
        direction="above",
        threshold=BASE_GOLDEN_POTHOS_PROFILE.thresholds["temperature"].max or 0.0,
        title=_text(kk="Температура жоғары", ru="Высокая температура", en="Temperature threshold above"),
        message=_text(
            kk="Температура Алтын потос үшін ұсынылған жоғарғы шектен жоғары.",
            ru="Температура выше верхнего порога для золотого потоса.",
            en="Temperature is above the shared care threshold.",
        ),
        advice_text=_text(
            kk="Өсімдікті салқындау жерге қойып, тікелей жылу көздерінен алыстатыңыз.",
            ru="Переставьте растение в более прохладное место и уберите от источников тепла.",
            en="Move the plant to a cooler area and reduce direct heat exposure.",
        ),
        advice_reason=_text(
            kk="Жоғары температура жапырақ пен топырақтың тез кебуіне әкеледі.",
            ru="Высокая температура ускоряет высыхание листьев и почвы.",
            en="High temperature can dry leaves and soil too quickly.",
        ),
    ),
    "low_humidity": _issue(
        code="low_humidity",
        metric="humidity",
        direction="below",
        threshold=BASE_GOLDEN_POTHOS_PROFILE.thresholds["humidity"].min or 0.0,
        title=_text(kk="Ауа ылғалдылығы төмен", ru="Низкая влажность воздуха", en="Humidity threshold below"),
        message=_text(
            kk="Ауа ылғалдылығы Алтын потос үшін ұсынылған шектен төмен.",
            ru="Влажность воздуха ниже рекомендуемого порога для золотого потоса.",
            en="Air humidity is below the shared care threshold.",
        ),
        advice_text=_text(
            kk="Ауа ылғалдылығын су науасы, ылғалдатқыш немесе өсімдіктерді бірге қою арқылы арттырыңыз.",
            ru="Повысьте влажность с помощью поддона с водой, увлажнителя или группировки растений.",
            en="Move the plant away from dry heat sources and increase ambient humidity with a humidifier, water tray, or grouped plants.",
        ),
        advice_reason=_text(
            kk="Алтын потос орташа ылғалды ауаны жақсы қабылдайды.",
            ru="Золотой потос хорошо переносит умеренно влажный воздух.",
            en="These indoor aroid vines benefit from moderate ambient humidity.",
        ),
    ),
    "low_light": _issue(
        code="low_light",
        metric="light",
        direction="below",
        threshold=BASE_GOLDEN_POTHOS_PROFILE.thresholds["light"].min or 0.0,
        title=_text(kk="Жарық төмен", ru="Недостаточно света", en="Light threshold below"),
        message=_text(
            kk="Жарық көрсеткіші Алтын потос үшін ұсынылған шектен төмен.",
            ru="Показатель света ниже рекомендуемого порога для золотого потоса.",
            en="Light is below the shared care threshold.",
        ),
        advice_text=_text(
            kk="Өсімдікті жарығырақ жерге қойыңыз немесе қосымша жарық қолданыңыз.",
            ru="Переставьте растение в более светлое место или добавьте дополнительную подсветку.",
            en="Move the plant closer to bright indirect light or add supplemental light; avoid harsh direct sun.",
        ),
        advice_reason=_text(
            kk="Алтын потос төмен жарыққа шыдайды, бірақ тұрақты өсу үшін жанама жарық қажет.",
            ru="Золотой потос переносит слабый свет, но для стабильного роста нужен рассеянный свет.",
            en="These indoor aroid vines tolerate lower light but grow better with bright indirect light.",
        ),
    ),
}

GOLDEN_POTHOS_PROFILE = PlantProfile(
    **{
        **BASE_GOLDEN_POTHOS_PROFILE.__dict__,
        "issues": GOLDEN_POTHOS_ISSUES,
    }
)

PLANT_PROFILES = {
    DEFAULT_PLANT_PROFILE_SLUG: GOLDEN_POTHOS_PROFILE,
    **{species.lower(): GOLDEN_POTHOS_PROFILE for species in SUPPORTED_SPECIES.values()},
}


def normalize_species(value: str | None = None) -> str:
    if not value:
        return CANONICAL_SPECIES
    return SUPPORTED_SPECIES.get(value.strip().lower(), CANONICAL_SPECIES)


def resolve_plant_profile(species: str | None = None) -> PlantProfile:
    if not species:
        return GOLDEN_POTHOS_PROFILE
    return PLANT_PROFILES.get(species.strip().lower(), GOLDEN_POTHOS_PROFILE)
