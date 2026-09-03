import type { Map as MLMap } from 'maplibre-gl'
import { lerp, lerpHexColor } from './colorUtil'

export interface SkyPaint {
  'sky-color': string
  'horizon-color': string
  'fog-color': string
  'fog-ground-blend': number
  'horizon-fog-blend': number
  'sky-horizon-blend': number
  'atmosphere-blend': number
}

export interface LightState {
  color: string
  intensity: number
  position: [number, number, number]
}

export interface MoodState {
  light: LightState
  sky: SkyPaint
}

const ANIMATION_DURATION_MS = 600

const lastState = new WeakMap<MLMap, MoodState>()
const activeFrame = new WeakMap<MLMap, number>()

function easeInOutQuad(t: number): number {
  return t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2
}

/** Interpolates a compass angle (degrees) along its shortest path. */
function lerpAngleDeg(a: number, b: number, t: number): number {
  const diff = ((b - a + 540) % 360) - 180
  return (a + diff * t + 360) % 360
}

function lerpSky(a: SkyPaint, b: SkyPaint, t: number): SkyPaint {
  return {
    'sky-color': lerpHexColor(a['sky-color'], b['sky-color'], t),
    'horizon-color': lerpHexColor(a['horizon-color'], b['horizon-color'], t),
    'fog-color': lerpHexColor(a['fog-color'], b['fog-color'], t),
    'fog-ground-blend': lerp(a['fog-ground-blend'], b['fog-ground-blend'], t),
    'horizon-fog-blend': lerp(a['horizon-fog-blend'], b['horizon-fog-blend'], t),
    'sky-horizon-blend': lerp(a['sky-horizon-blend'], b['sky-horizon-blend'], t),
    'atmosphere-blend': lerp(a['atmosphere-blend'], b['atmosphere-blend'], t),
  }
}

function lerpLight(a: LightState, b: LightState, t: number): LightState {
  return {
    color: lerpHexColor(a.color, b.color, t),
    intensity: lerp(a.intensity, b.intensity, t),
    position: [
      lerp(a.position[0], b.position[0], t),
      lerpAngleDeg(a.position[1], b.position[1], t),
      lerp(a.position[2], b.position[2], t),
    ],
  }
}

/**
 * Applies a light+sky mood to the map, animating from whatever mood was last
 * applied (via this function) instead of snapping instantly. The very first
 * call for a given map applies immediately, since there's nothing to
 * transition from.
 */
export function applyMoodAnimated(map: MLMap, target: MoodState) {
  const existing = activeFrame.get(map)
  if (existing !== undefined) cancelAnimationFrame(existing)

  const from = lastState.get(map) ?? target
  const start = performance.now()

  const tick = (now: number) => {
    const t = Math.min(1, (now - start) / ANIMATION_DURATION_MS)
    const eased = easeInOutQuad(t)
    map.setLight({ anchor: 'viewport', ...lerpLight(from.light, target.light, eased) })
    map.setSky(lerpSky(from.sky, target.sky, eased))

    if (t < 1) {
      activeFrame.set(map, requestAnimationFrame(tick))
    } else {
      activeFrame.delete(map)
      lastState.set(map, target)
    }
  }

  activeFrame.set(map, requestAnimationFrame(tick))
}
