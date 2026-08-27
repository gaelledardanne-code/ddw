import type { TimeOfDay } from './timeOfDay'

export interface ShareState {
  longitude?: number
  latitude?: number
  zoom?: number
  pitch?: number
  bearing?: number
  timeOfDay?: TimeOfDay
  showOverlay?: boolean
  historicalYear?: number | null
  sunMode?: boolean
  sunDateTime?: string
}

const TIME_OF_DAY_VALUES: TimeOfDay[] = ['dawn', 'noon', 'dusk', 'night']

function parseNumber(value: string | null): number | undefined {
  if (value === null) return undefined
  const n = Number(value)
  return Number.isFinite(n) ? n : undefined
}

export function parseShareStateFromUrl(): ShareState {
  const params = new URLSearchParams(window.location.search)
  const timeOfDayParam = params.get('t')
  const historicalYearParam = params.get('hy')

  return {
    longitude: parseNumber(params.get('lng')),
    latitude: parseNumber(params.get('lat')),
    zoom: parseNumber(params.get('z')),
    pitch: parseNumber(params.get('p')),
    bearing: parseNumber(params.get('b')),
    timeOfDay:
      timeOfDayParam && TIME_OF_DAY_VALUES.includes(timeOfDayParam as TimeOfDay)
        ? (timeOfDayParam as TimeOfDay)
        : undefined,
    showOverlay: params.has('ov') ? params.get('ov') === '1' : undefined,
    historicalYear: historicalYearParam ? (parseNumber(historicalYearParam) ?? null) : undefined,
    sunMode: params.has('sun') ? params.get('sun') === '1' : undefined,
    sunDateTime: params.get('sdt') ?? undefined,
  }
}

export function buildShareUrl(state: ShareState): string {
  const params = new URLSearchParams()
  if (state.longitude !== undefined) params.set('lng', state.longitude.toFixed(6))
  if (state.latitude !== undefined) params.set('lat', state.latitude.toFixed(6))
  if (state.zoom !== undefined) params.set('z', state.zoom.toFixed(2))
  if (state.pitch !== undefined) params.set('p', state.pitch.toFixed(1))
  if (state.bearing !== undefined) params.set('b', state.bearing.toFixed(1))
  if (state.timeOfDay) params.set('t', state.timeOfDay)
  if (state.showOverlay !== undefined) params.set('ov', state.showOverlay ? '1' : '0')
  if (state.historicalYear !== undefined && state.historicalYear !== null) {
    params.set('hy', String(state.historicalYear))
  }
  if (state.sunMode !== undefined) params.set('sun', state.sunMode ? '1' : '0')
  if (state.sunDateTime) params.set('sdt', state.sunDateTime)

  return `${window.location.origin}${window.location.pathname}?${params.toString()}`
}
