export interface WeatherData {
  temperatureC: number
  windSpeedKmh: number
  windDirectionDeg: number
  precipitationMm: number
  weatherCode: number
  description: string
}

const WEATHER_CODE_DESCRIPTIONS: Record<number, string> = {
  0: 'Clear sky',
  1: 'Mainly clear',
  2: 'Partly cloudy',
  3: 'Overcast',
  45: 'Fog',
  48: 'Depositing rime fog',
  51: 'Light drizzle',
  53: 'Moderate drizzle',
  55: 'Dense drizzle',
  61: 'Slight rain',
  63: 'Moderate rain',
  65: 'Heavy rain',
  71: 'Slight snow',
  73: 'Moderate snow',
  75: 'Heavy snow',
  80: 'Slight rain showers',
  81: 'Moderate rain showers',
  82: 'Violent rain showers',
  95: 'Thunderstorm',
  96: 'Thunderstorm with slight hail',
  99: 'Thunderstorm with heavy hail',
}

export function weatherDescriptionFor(code: number): string {
  return WEATHER_CODE_DESCRIPTIONS[code] ?? 'Unknown conditions'
}

export async function fetchCurrentWeather(lat: number, lon: number): Promise<WeatherData> {
  const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,wind_speed_10m,wind_direction_10m,precipitation,weather_code&timezone=auto`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`Open-Meteo request failed: ${res.status}`)
  const data = await res.json()
  const current = data.current

  return {
    temperatureC: current.temperature_2m,
    windSpeedKmh: current.wind_speed_10m,
    windDirectionDeg: current.wind_direction_10m,
    precipitationMm: current.precipitation,
    weatherCode: current.weather_code,
    description: weatherDescriptionFor(current.weather_code),
  }
}
