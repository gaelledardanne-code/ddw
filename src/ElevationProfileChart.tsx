import type { ElevationProfile } from './elevationProfile'

interface Props {
  profile: ElevationProfile
}

const WIDTH = 180
const HEIGHT = 60
const PADDING = 4

export default function ElevationProfileChart({ profile }: Props) {
  const validPoints = profile.points.filter(
    (p): p is { distanceMeters: number; elevationMeters: number } => p.elevationMeters !== null,
  )

  if (validPoints.length < 2) {
    return <span className="hint">Add at least two points with terrain data</span>
  }

  const elevations = validPoints.map((p) => p.elevationMeters)
  const minElevation = Math.min(...elevations)
  const maxElevation = Math.max(...elevations)
  const elevationRange = maxElevation - minElevation || 1
  const maxDistance = profile.totalDistanceMeters || 1

  const toX = (d: number) => PADDING + (d / maxDistance) * (WIDTH - PADDING * 2)
  const toY = (e: number) => HEIGHT - PADDING - ((e - minElevation) / elevationRange) * (HEIGHT - PADDING * 2)

  const linePoints = validPoints.map((p) => `${toX(p.distanceMeters)},${toY(p.elevationMeters)}`).join(' ')

  return (
    <svg width={WIDTH} height={HEIGHT} viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="elevation-chart">
      <polyline points={linePoints} fill="none" stroke="#ffdd57" strokeWidth={1.5} />
    </svg>
  )
}
