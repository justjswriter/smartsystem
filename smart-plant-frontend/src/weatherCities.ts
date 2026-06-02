export const WEATHER_CITY_KEY = "smart-plant-weather-city";

export const DEFAULT_WEATHER_CITY = "astana";

export const WEATHER_CITIES = [
  { id: "astana", label: "Астана", latitude: 51.1694, longitude: 71.4491 },
  { id: "almaty", label: "Алматы", latitude: 43.2389, longitude: 76.8897 },
  { id: "shymkent", label: "Шымкент", latitude: 42.3417, longitude: 69.5901 },
  { id: "karaganda", label: "Караганда", latitude: 49.8047, longitude: 73.1094 },
  { id: "aktobe", label: "Актобе", latitude: 50.2839, longitude: 57.167 },
  { id: "atyrau", label: "Атырау", latitude: 47.1167, longitude: 51.8833 },
  { id: "aktau", label: "Актау", latitude: 43.65, longitude: 51.2 },
  { id: "kostanay", label: "Костанай", latitude: 53.2144, longitude: 63.6246 },
  { id: "pavlodar", label: "Павлодар", latitude: 52.2873, longitude: 76.9674 },
  { id: "oskemen", label: "Өскемен", latitude: 49.9483, longitude: 82.6275 },
  { id: "oral", label: "Орал", latitude: 51.2333, longitude: 51.3667 },
  { id: "kyzylorda", label: "Қызылорда", latitude: 44.8479, longitude: 65.4999 },
  { id: "taraz", label: "Тараз", latitude: 42.9, longitude: 71.3667 },
  { id: "petropavl", label: "Петропавл", latitude: 54.8667, longitude: 69.15 },
];

export function getWeatherCity(cityId: string | null | undefined) {
  return WEATHER_CITIES.find((city) => city.id === cityId) ?? WEATHER_CITIES[0];
}
