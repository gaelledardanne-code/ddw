import { haversineDistanceMeters } from './geo'

export interface TrailPoint {
  lngLat: [number, number]
  elevation: number | null
}

export interface ProfilePoint {
  distanceMeters: number
  elevationMeters: number | null
}

export interface ElevationProfile {
  points: ProfilePoint[]
  totalDistanceMeters: number
  totalGainMeters: number
  totalLossMeters: number
}

export function computeElevationProfile(trailPoints: TrailPoint[]): ElevationProfile {
  let cumulative = 0
  let gain = 0
  let loss = 0

  const points: ProfilePoint[] = trailPoints.map((point, i) => {
    if (i > 0) {
      const prev = trailPoints[i - 1]
      cumulative += haversineDistanceMeters(prev.lngLat, point.lngLat)

      if (prev.elevation !== null && point.elevation !== null) {
        const delta = point.elevation - prev.elevation
        if (delta > 0) gain += delta
        else loss += -delta
      }
    }
    return { distanceMeters: cumulative, elevationMeters: point.elevation }
  })

  return { points, totalDistanceMeters: cumulative, totalGainMeters: gain, totalLossMeters: loss }
}
