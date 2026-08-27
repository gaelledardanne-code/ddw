import * as SunCalc from 'suncalc'
import type { Map as MLMap } from 'maplibre-gl'
import { clamp, lerp, lerpHexColor, lerpRgba } from './colorUtil'

interface SkyPaint {
  'sky-color': string
  'horizon-color': string
  'fog-color': string
  'fog-ground-blend': number
  'horizon-fog-blend': number
  'sky-horizon-blend': number
  'atmosphere-blend': number
}

interface Mood {
  lightColor: string
  intensity: number
  sky: SkyPaint
  overlayColor: string
}

const NIGHT: Mood = {
  lightColor: '#2b3a67',
  intensity: 0.15,
  sky: {
    'sky-color': '#0b1026',
    'horizon-color': '#1a2140',
    'fog-color': '#05060f',
    'fog-ground-blend': 0.3,
    'horizon-fog-blend': 0.3,
    'sky-horizon-blend': 0.3,
    'atmosphere-blend': 0.9,
  },
  overlayColor: 'rgba(8, 12, 38, 0.6)',
}

const HORIZON: Mood = {
  lightColor: '#ff8c5a',
  intensity: 0.42,
  sky: {
    'sky-color': '#ffb37a',
    'horizon-color': '#c1547a',
    'fog-color': '#ff9a6e',
    'fog-ground-blend': 0.6,
    'horizon-fog-blend': 0.58,
    'sky-horizon-blend': 0.58,
    'atmosphere-blend': 0.75,
  },
  overlayColor: 'rgba(255, 120, 70, 0.2)',
}

const DAY: Mood = {
  lightColor: '#ffffff',
  intensity: 0.6,
  sky: {
    'sky-color': '#88c9f9',
    'horizon-color': '#d6ecff',
    'fog-color': '#ffffff',
    'fog-ground-blend': 0.5,
    'horizon-fog-blend': 0.5,
    'sky-horizon-blend': 0.5,
    'atmosphere-blend': 0.8,
  },
  overlayColor: 'rgba(0, 0, 0, 0)',
}

function blendPair(a: Mood, b: Mood, t: number): Mood {
  return {
    lightColor: lerpHexColor(a.lightColor, b.lightColor, t),
    intensity: lerp(a.intensity, b.intensity, t),
    sky: {
      'sky-color': lerpHexColor(a.sky['sky-color'], b.sky['sky-color'], t),
      'horizon-color': lerpHexColor(a.sky['horizon-color'], b.sky['horizon-color'], t),
      'fog-color': lerpHexColor(a.sky['fog-color'], b.sky['fog-color'], t),
      'fog-ground-blend': lerp(a.sky['fog-ground-blend'], b.sky['fog-ground-blend'], t),
      'horizon-fog-blend': lerp(a.sky['horizon-fog-blend'], b.sky['horizon-fog-blend'], t),
      'sky-horizon-blend': lerp(a.sky['sky-horizon-blend'], b.sky['sky-horizon-blend'], t),
      'atmosphere-blend': lerp(a.sky['atmosphere-blend'], b.sky['atmosphere-blend'], t),
    },
    overlayColor: lerpRgba(a.overlayColor, b.overlayColor, t),
  }
}

/** Maps solar altitude (degrees) to a blend position: 0 = night, 0.5 = horizon, 1 = full day. */
function altitudeToT(altitudeDeg: number): number {
  if (altitudeDeg <= -8) return 0
  if (altitudeDeg >= 40) return 1
  if (altitudeDeg <= 0) return lerp(0, 0.5, (altitudeDeg + 8) / 8)
  return lerp(0.5, 1, altitudeDeg / 40)
}

function blend(t: number): Mood {
  return t <= 0.5 ? blendPair(NIGHT, HORIZON, t / 0.5) : blendPair(HORIZON, DAY, (t - 0.5) / 0.5)
}

export interface SunLightResult {
  light: { color: string; intensity: number; position: [number, number, number] }
  sky: SkyPaint
  overlayColor: string
  altitudeDeg: number
  compassAzimuthDeg: number
}

export function computeSunLight(lat: number, lon: number, date: Date): SunLightResult {
  // suncalc v2 returns altitude/azimuth already in degrees, with azimuth as a
  // compass bearing (0 = north, clockwise) — no radian conversion needed.
  const pos = SunCalc.getPosition(date, lat, lon)
  const altitudeDeg = pos.altitude
  const compassAzimuthDeg = ((pos.azimuth % 360) + 360) % 360
  const polar = clamp(90 - altitudeDeg, 0, 180)

  const mood = blend(altitudeToT(altitudeDeg))

  return {
    light: { color: mood.lightColor, intensity: mood.intensity, position: [1.15, compassAzimuthDeg, polar] },
    sky: mood.sky,
    overlayColor: mood.overlayColor,
    altitudeDeg,
    compassAzimuthDeg,
  }
}

export function applySunLight(map: MLMap, lat: number, lon: number, date: Date): SunLightResult {
  const result = computeSunLight(lat, lon, date)
  map.setLight({ anchor: 'viewport', color: result.light.color, intensity: result.light.intensity, position: result.light.position })
  map.setSky(result.sky)
  return result
}

const MAURITIUS_UTC_OFFSET_HOURS = 4

/** Parses a `datetime-local` input value as Mauritius local time (fixed UTC+4, no DST). */
export function mauritiusLocalToUtcDate(localDateTimeValue: string): Date {
  const [datePart, timePart] = localDateTimeValue.split('T')
  const [year, month, day] = datePart.split('-').map(Number)
  const [hour, minute] = (timePart ?? '00:00').split(':').map(Number)
  return new Date(Date.UTC(year, month - 1, day, hour - MAURITIUS_UTC_OFFSET_HOURS, minute))
}

/** Formats a Date as a `datetime-local` input value representing Mauritius local time. */
export function utcDateToMauritiusLocalInputValue(date: Date): string {
  const local = new Date(date.getTime() + MAURITIUS_UTC_OFFSET_HOURS * 60 * 60 * 1000)
  const pad = (n: number) => String(n).padStart(2, '0')
  const year = local.getUTCFullYear()
  const month = pad(local.getUTCMonth() + 1)
  const day = pad(local.getUTCDate())
  const hour = pad(local.getUTCHours())
  const minute = pad(local.getUTCMinutes())
  return `${year}-${month}-${day}T${hour}:${minute}`
}
