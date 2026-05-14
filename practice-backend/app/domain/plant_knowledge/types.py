from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LocalizedText:
    kk: str
    ru: str
    en: str

    def text(self, locale: str = "en") -> str:
        if locale == "kk":
            return self.kk
        if locale == "ru":
            return self.ru
        return self.en


@dataclass(frozen=True)
class MetricRange:
    min: float | None = None
    max: float | None = None
    optimal_min: float | None = None
    optimal_max: float | None = None


@dataclass(frozen=True)
class PlantAdvice:
    text: LocalizedText
    reason: LocalizedText


@dataclass(frozen=True)
class IssueDefinition:
    code: str
    metric: str
    direction: str
    threshold: float
    title: LocalizedText
    message: LocalizedText
    advice: PlantAdvice


@dataclass(frozen=True)
class PlantProfile:
    slug: str
    canonical_species: str
    names: LocalizedText
    thresholds: dict[str, MetricRange]
    issues: dict[str, IssueDefinition]
    stable_advice: PlantAdvice

