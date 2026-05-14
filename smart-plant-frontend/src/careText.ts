type Translator = (key: string, params?: Record<string, string | number | null | undefined>) => string;

export function localizeCareText(text: string | null | undefined, t: Translator) {
  if (!text) {
    return text;
  }
  const exact: Record<string, string> = {
    "Light threshold below": t("alertText.lightBelowTitle"),
    "Light is below threshold": t("alertText.lightBelowMessage"),
    "Light is below the Golden pothos profile threshold.": t("alertText.lightBelowMessage"),
    "Light is below the shared care threshold.": t("alertText.lightBelowMessage"),
    "Move the plant to a brighter location or add supplemental light.": t("alertText.lightBelowRecommendation"),
    "Move the plant closer to bright indirect light or add supplemental light; avoid harsh direct sun.": t("alertText.lightBelowRecommendation"),

    "Moisture threshold below": t("alertText.moistureBelowTitle"),
    "Moisture is below threshold": t("alertText.moistureBelowMessage"),
    "Moisture is below the Golden pothos profile threshold.": t("alertText.moistureBelowMessage"),
    "Soil moisture is below the shared care threshold.": t("alertText.moistureBelowMessage"),
    "Increase watering schedule and re-check soil in 2-4 hours.": t("alertText.moistureBelowRecommendation"),
    "Water gradually until the top soil is evenly moist, then re-check soil moisture in 2-4 hours.": t("alertText.moistureBelowRecommendation"),

    "Moisture threshold above": t("alertText.moistureAboveTitle"),
    "Moisture is above the Golden pothos profile threshold.": t("alertText.moistureAboveMessage"),
    "Soil moisture is above the shared care threshold.": t("alertText.moistureAboveMessage"),
    "Pause watering and let the soil dry down before the next watering.": t("alertText.moistureAboveRecommendation"),
    "Pause watering and let the top layer of soil dry before the next watering.": t("alertText.moistureAboveRecommendation"),

    "Temperature threshold below": t("alertText.temperatureBelowTitle"),
    "Temperature is below the Golden pothos profile threshold.": t("alertText.temperatureBelowMessage"),
    "Temperature is below the shared care threshold.": t("alertText.temperatureBelowMessage"),
    "Move the plant to a warmer area and keep it away from cold drafts.": t("alertText.temperatureBelowRecommendation"),

    "Temperature threshold above": t("alertText.temperatureAboveTitle"),
    "Temperature is above threshold": t("alertText.temperatureAboveMessage"),
    "Temperature is above the Golden pothos profile threshold.": t("alertText.temperatureAboveMessage"),
    "Temperature is above the shared care threshold.": t("alertText.temperatureAboveMessage"),
    "Move the plant to a cooler location and avoid direct heat sources.": t("alertText.temperatureAboveRecommendation"),
    "Move the plant to a cooler area and reduce direct heat exposure.": t("alertText.temperatureAboveRecommendation"),

    "Humidity threshold below": t("alertText.humidityBelowTitle"),
    "Humidity is below threshold": t("alertText.humidityBelowMessage"),
    "Humidity is below the Golden pothos profile threshold.": t("alertText.humidityBelowMessage"),
    "Air humidity is below the shared care threshold.": t("alertText.humidityBelowMessage"),
    "Increase ambient humidity with a tray, humidifier, or grouped plants.": t("alertText.humidityBelowRecommendation"),
    "Move the plant away from dry heat sources and increase ambient humidity with a humidifier, water tray, or grouped plants.": t("alertText.humidityBelowRecommendation"),

    "Conditions are stable. Keep the current care routine and continue monitoring sensor trends.": t("alertText.stableRecommendation"),
    "Latest sensor values are within the shared tropical aroid care ranges.": t("alertText.stableReason"),
  };
  if (exact[text]) {
    return exact[text];
  }
  return text.replace(/\s*\(severity=(low|medium|high|critical)\)\.?$/i, "");
}
