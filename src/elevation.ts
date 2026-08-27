import type { Map as MLMap } from 'maplibre-gl'

export interface ElevationSample {
  elevationMeters: number | null
  slopePercent: number | null
}

const OFFSET_METERS = 15

export function sampleElevation(map: MLMap, lngLat: { lng: number; lat: number }): ElevationSample {
  const elevationMeters = map.queryTerrainElevation(lngLat)
  if (elevationMeters === null) return { elevationMeters: null, slopePercent: null }

  const metersPerDegLat = 111320
  const metersPerDegLon = 111320 * Math.cos((lngLat.lat * Math.PI) / 180)
  const dLat = OFFSET_METERS / metersPerDegLat
  const dLon = OFFSET_METERS / metersPerDegLon

  const north = map.queryTerrainElevation({ lng: lngLat.lng, lat: lngLat.lat + dLat })
  const east = map.queryTerrainElevation({ lng: lngLat.lng + dLon, lat: lngLat.lat })

  if (north === null || east === null) return { elevationMeters, slopePercent: null }

  const dzNorth = north - elevationMeters
  const dzEast = east - elevationMeters
  const slopePercent = (Math.sqrt(dzNorth ** 2 + dzEast ** 2) / OFFSET_METERS) * 100

  return { elevationMeters, slopePercent }
}
