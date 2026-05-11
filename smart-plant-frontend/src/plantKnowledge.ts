import type { useI18n } from "./i18n";

export const SUPPORTED_PLANT_SPECIES = "Epipremnum aureum";

type Translator = ReturnType<typeof useI18n>["t"];

export function supportedPlantTypeName(t: Translator) {
  return t("plantType.epipremnum_aureum");
}

export function displayPlantSpecies(species: string | undefined, t: Translator) {
  if (!species || species.toLowerCase() === SUPPORTED_PLANT_SPECIES.toLowerCase()) {
    return supportedPlantTypeName(t);
  }
  return supportedPlantTypeName(t);
}
