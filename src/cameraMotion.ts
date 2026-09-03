import type { Map as MLMap } from 'maplibre-gl'

export interface CameraTarget {
  center: [number, number]
  zoom: number
  pitch: number
  bearing: number
}

/** Eases the camera to a target view. Wraps flyTo with house defaults so every programmatic move feels consistent. */
export function flyToEstate(map: MLMap, target: CameraTarget, durationMs = 2200) {
  map.flyTo({
    center: target.center,
    zoom: target.zoom,
    pitch: target.pitch,
    bearing: target.bearing,
    duration: durationMs,
    curve: 1.4,
    essential: true,
  })
}
