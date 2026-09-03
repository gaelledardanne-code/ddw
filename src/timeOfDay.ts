import type { Map as MLMap } from 'maplibre-gl'
import { applyMoodAnimated } from './mapMood'

export type TimeOfDay = 'dawn' | 'noon' | 'dusk' | 'night'

interface Preset {
  light: { color: string; intensity: number; position: [number, number, number] }
  sky: {
    'sky-color': string
    'horizon-color': string
    'fog-color': string
    'fog-ground-blend': number
    'horizon-fog-blend': number
    'sky-horizon-blend': number
    'atmosphere-blend': number
  }
  /** CSS color applied as a mood-lighting overlay above the map canvas. */
  overlayColor: string
}

const PRESETS: Record<TimeOfDay, Preset> = {
  dawn: {
    light: { color: '#ffb066', intensity: 0.45, position: [1.15, 80, 75] },
    sky: {
      'sky-color': '#ffcf9c',
      'horizon-color': '#ffdca8',
      'fog-color': '#ffe4b5',
      'fog-ground-blend': 0.6,
      'horizon-fog-blend': 0.6,
      'sky-horizon-blend': 0.6,
      'atmosphere-blend': 0.7,
    },
    overlayColor: 'rgba(255, 176, 102, 0.16)',
  },
  noon: {
    light: { color: '#ffffff', intensity: 0.6, position: [1.15, 200, 30] },
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
  },
  dusk: {
    light: { color: '#ff7b54', intensity: 0.4, position: [1.15, 260, 80] },
    sky: {
      'sky-color': '#ff9d6c',
      'horizon-color': '#c1446e',
      'fog-color': '#ff8a65',
      'fog-ground-blend': 0.6,
      'horizon-fog-blend': 0.55,
      'sky-horizon-blend': 0.55,
      'atmosphere-blend': 0.75,
    },
    overlayColor: 'rgba(255, 90, 60, 0.22)',
  },
  night: {
    light: { color: '#2b3a67', intensity: 0.15, position: [1.15, 0, 120] },
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
  },
}

export const timeOfDayOptions: { value: TimeOfDay; label: string }[] = [
  { value: 'dawn', label: 'Dawn' },
  { value: 'noon', label: 'Noon' },
  { value: 'dusk', label: 'Dusk' },
  { value: 'night', label: 'Night' },
]

export function overlayColorFor(time: TimeOfDay): string {
  return PRESETS[time].overlayColor
}

export function applyTimeOfDay(map: MLMap, time: TimeOfDay) {
  const preset = PRESETS[time]
  applyMoodAnimated(map, { light: preset.light, sky: preset.sky })
}
