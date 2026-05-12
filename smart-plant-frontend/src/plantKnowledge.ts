import type { useI18n } from "./i18n";

export const SUPPORTED_PLANT_SPECIES = "Epipremnum aureum";
export const SUPPORTED_PLANT_OPTIONS = [
  "Epipremnum aureum",
  "Philodendron hederaceum",
  "Scindapsus pictus",
  "Syngonium podophyllum",
] as const;

export type SupportedPlantSpecies = (typeof SUPPORTED_PLANT_OPTIONS)[number];

type Translator = ReturnType<typeof useI18n>["t"];

export function plantTypeKey(species: string | undefined) {
  const normalized = (species || SUPPORTED_PLANT_SPECIES).toLowerCase();
  if (normalized === "philodendron hederaceum") {
    return "plantType.philodendron_hederaceum";
  }
  if (normalized === "scindapsus pictus") {
    return "plantType.scindapsus_pictus";
  }
  if (normalized === "syngonium podophyllum") {
    return "plantType.syngonium_podophyllum";
  }
  return "plantType.epipremnum_aureum";
}

export function supportedPlantTypeName(t: Translator) {
  return t("plantType.common_aroid_vines");
}

export function displayPlantSpecies(species: string | undefined, t: Translator) {
  return t(plantTypeKey(species));
}
