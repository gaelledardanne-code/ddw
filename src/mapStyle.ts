import type { StyleSpecification } from 'maplibre-gl'

/**
 * Free, keyless tile sources — no account or billing required.
 * - Satellite imagery: Esri World Imagery
 * - Terrain elevation: AWS Terrain Tiles (Terrarium encoding)
 */
export const mapStyle: StyleSpecification = {
  version: 8,
  sources: {
    'esri-satellite': {
      type: 'raster',
      tiles: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      ],
      tileSize: 256,
      attribution: 'Esri, Maxar, Earthstar Geographics, and the GIS User Community',
    },
    'terrain-dem': {
      type: 'raster-dem',
      tiles: ['https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'],
      tileSize: 256,
      encoding: 'terrarium',
      maxzoom: 15,
    },
  },
  layers: [
    {
      id: 'satellite',
      type: 'raster',
      source: 'esri-satellite',
    },
    {
      id: 'hillshade',
      type: 'hillshade',
      source: 'terrain-dem',
      paint: {
        'hillshade-exaggeration': 0.5,
        'hillshade-illumination-direction': 200,
        'hillshade-shadow-color': '#3b2f2f',
        'hillshade-highlight-color': '#fff8e7',
      },
    },
    {
      id: 'hillshade-contrast',
      type: 'hillshade',
      source: 'terrain-dem',
      layout: { visibility: 'none' },
      paint: {
        'hillshade-exaggeration': 1,
        'hillshade-illumination-direction': 200,
        'hillshade-shadow-color': '#8b1a1a',
        'hillshade-highlight-color': '#ffe98a',
        'hillshade-accent-color': '#1b4332',
      },
    },
  ],
  terrain: {
    source: 'terrain-dem',
    exaggeration: 1.3,
  },
  light: {
    anchor: 'viewport',
    color: '#ffffff',
    intensity: 0.6,
    position: [1.15, 200, 30],
  },
  sky: {
    'sky-color': '#88c9f9',
    'horizon-color': '#d6ecff',
    'fog-color': '#ffffff',
    'fog-ground-blend': 0.5,
    'horizon-fog-blend': 0.5,
    'sky-horizon-blend': 0.5,
    'atmosphere-blend': 0.8,
  },
}
