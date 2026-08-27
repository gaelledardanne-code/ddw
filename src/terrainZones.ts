export type TerrainType = 'forest' | 'field' | 'water' | 'trail'

export interface TerrainZone {
  id: string
  name: string
  type: TerrainType
  description: string
  /** Closed polygon ring [lng, lat][]. */
  coordinates: [number, number][]
}

export const terrainTypeLabels: Record<TerrainType, string> = {
  forest: 'Forest',
  field: 'Open field',
  water: 'Water',
  trail: 'Trail corridor',
}

export const terrainTypeColors: Record<TerrainType, string> = {
  forest: '#2d6a4f',
  field: '#c9e4a3',
  water: '#4a90d9',
  trail: '#e0a458',
}

/**
 * Hand-placed against satellite imagery to approximate visible tree cover,
 * clearings, and trails — not a surveyed land-cover dataset. Replace with
 * real vector data when available.
 */
export const terrainZones: TerrainZone[] = [
  {
    id: 'forest-core',
    name: 'Wooded hunting ground',
    type: 'forest',
    description: 'Dense tree cover forming the bulk of the estate, used for deer hunting June–September.',
    coordinates: [
      [57.364, -20.298],
      [57.371, -20.293],
      [57.376, -20.297],
      [57.3745, -20.3025],
      [57.369, -20.3055],
      [57.3635, -20.3015],
      [57.364, -20.298],
    ],
  },
  {
    id: 'main-clearing',
    name: 'Main clearing',
    type: 'field',
    description: 'Open grassy area used off-season for weddings and events.',
    coordinates: [
      [57.3665, -20.2995],
      [57.371, -20.2985],
      [57.371, -20.3025],
      [57.3665, -20.3035],
      [57.3665, -20.2995],
    ],
  },
  {
    id: 'watering-hole',
    name: 'Watering hole',
    type: 'water',
    description: 'Illustrative placeholder for a small pond — not confirmed from imagery.',
    coordinates: [
      [57.3715, -20.2965],
      [57.3725, -20.2965],
      [57.3725, -20.2975],
      [57.3715, -20.2975],
      [57.3715, -20.2965],
    ],
  },
  {
    id: 'north-trail-corridor',
    name: 'North trail corridor',
    type: 'trail',
    description: 'Cleared path network cutting through the northern forest block.',
    coordinates: [
      [57.369, -20.2955],
      [57.3735, -20.294],
      [57.3745, -20.2955],
      [57.37, -20.297],
      [57.369, -20.2955],
    ],
  },
]
