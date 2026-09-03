import type { StyleSpecification } from 'maplibre-gl'

/**
 * Free, keyless tile sources — no account or billing required.
 * - Basemap: OpenFreeMap "openmaptiles" vector tiles, restyled with an estate
 *   palette (lagoon water, tropical greens, sandy paths) instead of their
 *   default colors.
 * - Terrain elevation: AWS Terrain Tiles (Terrarium encoding). Two separate
 *   sources point at the same tiles — one dedicated to 3D terrain (applied
 *   imperatively via the Map component's `terrain` prop), one dedicated to
 *   hillshade — so MapLibre doesn't warn about sharing a single source
 *   between a hillshade layer and 3D terrain.
 */

const TERRARIUM_TILES = ['https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png']

const WATER = '#3fb6c9'
const WATERWAY = '#54c2d1'
const WOOD = '#4f7942'
const GRASS = '#8fb96a'
const PARK = '#79ad63'
const SAND = '#f2e6c9'
const BACKGROUND = '#ece2c9'
const PATH = '#d9c48f'
const MINOR_ROAD = '#cdb27f'
const MAJOR_ROAD = '#e0a458'
const BUILDING = '#c9a98c'

export const mapStyle: StyleSpecification = {
  version: 8,
  sources: {
    openmaptiles: {
      type: 'vector',
      url: 'https://tiles.openfreemap.org/planet',
    },
    'terrain-dem': {
      type: 'raster-dem',
      tiles: TERRARIUM_TILES,
      tileSize: 256,
      encoding: 'terrarium',
      maxzoom: 15,
    },
    'hillshade-dem': {
      type: 'raster-dem',
      tiles: TERRARIUM_TILES,
      tileSize: 256,
      encoding: 'terrarium',
      maxzoom: 15,
    },
  },
  layers: [
    {
      id: 'background',
      type: 'background',
      paint: { 'background-color': BACKGROUND },
    },
    {
      id: 'landcover-wood',
      type: 'fill',
      source: 'openmaptiles',
      'source-layer': 'landcover',
      filter: ['==', ['get', 'class'], 'wood'],
      paint: { 'fill-color': WOOD, 'fill-opacity': 0.55 },
    },
    {
      id: 'landcover-grass',
      type: 'fill',
      source: 'openmaptiles',
      'source-layer': 'landcover',
      filter: ['==', ['get', 'class'], 'grass'],
      paint: { 'fill-color': GRASS, 'fill-opacity': 0.45 },
    },
    {
      id: 'landcover-sand',
      type: 'fill',
      source: 'openmaptiles',
      'source-layer': 'landcover',
      filter: ['==', ['get', 'class'], 'sand'],
      paint: { 'fill-color': SAND, 'fill-opacity': 0.6 },
    },
    {
      id: 'park',
      type: 'fill',
      source: 'openmaptiles',
      'source-layer': 'park',
      paint: { 'fill-color': PARK, 'fill-opacity': 0.4 },
    },
    {
      id: 'hillshade',
      type: 'hillshade',
      source: 'hillshade-dem',
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
      source: 'hillshade-dem',
      layout: { visibility: 'none' },
      paint: {
        'hillshade-exaggeration': 1,
        'hillshade-illumination-direction': 200,
        'hillshade-shadow-color': '#8b1a1a',
        'hillshade-highlight-color': '#ffe98a',
        'hillshade-accent-color': '#1b4332',
      },
    },
    {
      id: 'waterway',
      type: 'line',
      source: 'openmaptiles',
      'source-layer': 'waterway',
      paint: { 'line-color': WATERWAY, 'line-width': ['interpolate', ['linear'], ['zoom'], 11, 0.5, 18, 4] },
    },
    {
      id: 'water',
      type: 'fill',
      source: 'openmaptiles',
      'source-layer': 'water',
      paint: { 'fill-color': WATER },
    },
    {
      id: 'road-path',
      type: 'line',
      source: 'openmaptiles',
      'source-layer': 'transportation',
      filter: ['match', ['get', 'class'], ['path', 'track'], true, false],
      layout: { 'line-cap': 'round', 'line-join': 'round' },
      paint: {
        'line-color': PATH,
        'line-width': ['interpolate', ['linear'], ['zoom'], 13, 0.75, 18, 3],
        'line-dasharray': [2, 1.5],
      },
    },
    {
      id: 'road-minor',
      type: 'line',
      source: 'openmaptiles',
      'source-layer': 'transportation',
      filter: ['match', ['get', 'class'], ['minor', 'service', 'tertiary'], true, false],
      layout: { 'line-cap': 'round', 'line-join': 'round' },
      paint: {
        'line-color': MINOR_ROAD,
        'line-width': ['interpolate', ['linear'], ['zoom'], 12, 0.5, 18, 5],
      },
    },
    {
      id: 'road-major',
      type: 'line',
      source: 'openmaptiles',
      'source-layer': 'transportation',
      filter: ['match', ['get', 'class'], ['motorway', 'trunk', 'primary', 'secondary'], true, false],
      layout: { 'line-cap': 'round', 'line-join': 'round' },
      paint: {
        'line-color': MAJOR_ROAD,
        'line-width': ['interpolate', ['linear'], ['zoom'], 10, 1, 18, 8],
      },
    },
    {
      id: 'building',
      type: 'fill',
      source: 'openmaptiles',
      'source-layer': 'building',
      maxzoom: 15,
      paint: { 'fill-color': BUILDING, 'fill-opacity': 0.85 },
    },
    {
      id: 'building-3d',
      type: 'fill-extrusion',
      source: 'openmaptiles',
      'source-layer': 'building',
      minzoom: 15,
      paint: {
        'fill-extrusion-color': BUILDING,
        'fill-extrusion-base': ['coalesce', ['get', 'render_min_height'], 0],
        'fill-extrusion-height': ['coalesce', ['get', 'render_height'], 6],
        'fill-extrusion-opacity': 0.9,
      },
    },
  ],
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
    'atmosphere-blend': 0.85,
  },
}
