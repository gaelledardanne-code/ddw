import type { Map as MLMap } from 'maplibre-gl'

export interface Waypoint {
  center: [number, number]
  zoom: number
  pitch: number
  bearing: number
  duration: number
}

/** Scripted camera path over the estate. Coordinates are placeholders pending verified site data. */
export const tourWaypoints: Waypoint[] = [
  { center: [57.372, -20.298], zoom: 13.5, pitch: 45, bearing: 0, duration: 0 },
  { center: [57.368, -20.302], zoom: 15.5, pitch: 70, bearing: -30, duration: 4000 },
  { center: [57.3695, -20.3005], zoom: 16.5, pitch: 75, bearing: 40, duration: 4500 },
  { center: [57.365, -20.305], zoom: 14.5, pitch: 55, bearing: 120, duration: 5000 },
  { center: [57.368, -20.302], zoom: 15, pitch: 60, bearing: -20, duration: 4000 },
]

function flyToAsync(map: MLMap, wp: Waypoint, cancelled: { current: boolean }) {
  return new Promise<void>((resolve) => {
    if (cancelled.current) {
      resolve()
      return
    }
    const onEnd = () => {
      map.off('moveend', onEnd)
      resolve()
    }
    map.on('moveend', onEnd)
    map.flyTo({
      center: wp.center,
      zoom: wp.zoom,
      pitch: wp.pitch,
      bearing: wp.bearing,
      duration: wp.duration,
      essential: true,
    })
  })
}

export async function runTour(map: MLMap, cancelled: { current: boolean }) {
  for (const wp of tourWaypoints) {
    if (cancelled.current) return
    await flyToAsync(map, wp, cancelled)
  }
}
