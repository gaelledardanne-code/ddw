import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import Map, {
  Marker,
  Popup,
  NavigationControl,
  FullscreenControl,
  Source,
  Layer,
  type MapRef,
  type MapLayerMouseEvent,
} from 'react-map-gl/maplibre'
import 'maplibre-gl/dist/maplibre-gl.css'
import { pois, type Poi } from './poi'
import { mapStyle } from './mapStyle'
import { applyTimeOfDay, overlayColorFor, type TimeOfDay } from './timeOfDay'
import { runTour } from './tour'
import { haversineDistanceMeters } from './geo'
import { estateBoundary } from './boundary'
import { terrainZones, terrainTypeColors, type TerrainZone } from './terrainZones'
import { historicalYears, waybackTileUrl } from './historicalImagery'
import { sampleElevation, type ElevationSample } from './elevation'
import { applySunLight, mauritiusLocalToUtcDate, utcDateToMauritiusLocalInputValue } from './sunPosition'
import { fetchCurrentWeather, type WeatherData } from './weather'
import { buildShareUrl, parseShareStateFromUrl } from './shareState'
import { computeElevationProfile } from './elevationProfile'
import ControlsPanel from './ControlsPanel'
import './App.css'

interface MeasurePoint {
  lngLat: [number, number]
  elevation: number | null
}

const terrainZoneCollection: GeoJSON.FeatureCollection = {
  type: 'FeatureCollection',
  features: terrainZones.map((zone) => ({
    type: 'Feature',
    properties: { id: zone.id, type: zone.type },
    geometry: { type: 'Polygon', coordinates: [zone.coordinates] },
  })),
}

const boundaryGeometry: GeoJSON.Feature = {
  type: 'Feature',
  properties: {},
  geometry: { type: 'LineString', coordinates: estateBoundary },
}

const HOVER_THROTTLE_MS = 100
const ESTATE_CENTER = { longitude: 57.368, latitude: -20.302 }

export default function App() {
  const mapRef = useRef<MapRef>(null)
  const cancelledRef = useRef(false)

  const lastHoverRef = useRef(0)

  const shared = useMemo(() => parseShareStateFromUrl(), [])

  const [selected, setSelected] = useState<Poi | null>(null)
  const [timeOfDay, setTimeOfDay] = useState<TimeOfDay>(shared.timeOfDay ?? 'noon')
  const [tourRunning, setTourRunning] = useState(false)
  const [measureActive, setMeasureActive] = useState(false)
  const [measurePoints, setMeasurePoints] = useState<MeasurePoint[]>([])
  const [showOverlay, setShowOverlay] = useState(shared.showOverlay ?? true)
  const [selectedZone, setSelectedZone] = useState<TerrainZone | null>(null)
  const [historicalYear, setHistoricalYear] = useState<number | null>(shared.historicalYear ?? null)
  const [hoverElevation, setHoverElevation] = useState<ElevationSample | null>(null)
  const [mapReady, setMapReady] = useState(false)
  const [sunMode, setSunMode] = useState(shared.sunMode ?? false)
  const [sunDateTime, setSunDateTime] = useState<Date>(() => (shared.sunDateTime ? new Date(shared.sunDateTime) : new Date()))
  const [sunOverlayColor, setSunOverlayColor] = useState<string | null>(null)
  const [sunInfo, setSunInfo] = useState<{ altitudeDeg: number; compassAzimuthDeg: number } | null>(null)
  const [weather, setWeather] = useState<WeatherData | null>(null)
  const [weatherError, setWeatherError] = useState<string | null>(null)
  const [shareUrl, setShareUrl] = useState<string | null>(null)
  const [shareCopied, setShareCopied] = useState(false)
  const [trailActive, setTrailActive] = useState(false)
  const [trailPoints, setTrailPoints] = useState<MeasurePoint[]>([])
  const [slopeContrast, setSlopeContrast] = useState(false)

  const handleTimeOfDayChange = useCallback((t: TimeOfDay) => {
    setTimeOfDay(t)
    const map = mapRef.current?.getMap()
    if (map) applyTimeOfDay(map, t)
  }, [])

  const handleToggleTour = useCallback(() => {
    const map = mapRef.current?.getMap()
    if (!map) return

    if (tourRunning) {
      cancelledRef.current = true
      setTourRunning(false)
      return
    }

    setSelected(null)
    setSelectedZone(null)
    setMeasureActive(false)
    setTrailActive(false)
    cancelledRef.current = false
    setTourRunning(true)
    runTour(map, cancelledRef).finally(() => setTourRunning(false))
  }, [tourRunning])

  const handleToggleMeasure = useCallback(() => {
    setMeasureActive((active) => !active)
    setMeasurePoints([])
    setTrailActive(false)
  }, [])

  const handleClearMeasure = useCallback(() => {
    setMeasurePoints([])
  }, [])

  const handleToggleTrail = useCallback(() => {
    setTrailActive((active) => {
      const next = !active
      if (next) {
        setTrailPoints([])
        setMeasureActive(false)
        setMeasurePoints([])
      }
      return next
    })
  }, [])

  const handleClearTrail = useCallback(() => {
    setTrailPoints([])
  }, [])

  const handleToggleSlopeContrast = useCallback(() => {
    setSlopeContrast((active) => !active)
  }, [])

  const handleMapClick = useCallback(
    (e: MapLayerMouseEvent) => {
      if (measureActive) {
        const map = e.target
        const elevation = map.queryTerrainElevation(e.lngLat)
        const point: MeasurePoint = { lngLat: [e.lngLat.lng, e.lngLat.lat], elevation }
        setMeasurePoints((prev) => (prev.length >= 2 ? [point] : [...prev, point]))
        return
      }

      if (trailActive) {
        const map = e.target
        const elevation = map.queryTerrainElevation(e.lngLat)
        const point: MeasurePoint = { lngLat: [e.lngLat.lng, e.lngLat.lat], elevation }
        setTrailPoints((prev) => [...prev, point])
        return
      }

      const zoneId = e.features?.[0]?.properties?.id as string | undefined
      const zone = zoneId ? terrainZones.find((z) => z.id === zoneId) : undefined
      setSelectedZone(zone ?? null)
    },
    [measureActive, trailActive],
  )

  const handleMapMouseMove = useCallback((e: MapLayerMouseEvent) => {
    const now = performance.now()
    if (now - lastHoverRef.current < HOVER_THROTTLE_MS) return
    lastHoverRef.current = now
    setHoverElevation(sampleElevation(e.target, e.lngLat))
  }, [])

  const handleMapMouseLeave = useCallback(() => {
    setHoverElevation(null)
  }, [])

  const handleToggleOverlay = useCallback(() => {
    setShowOverlay((v) => !v)
    setSelectedZone(null)
  }, [])

  const handleHistoricalYearChange = useCallback((year: number | null) => {
    setHistoricalYear(year)
  }, [])

  const handleToggleSunMode = useCallback(() => {
    setSunMode((v) => !v)
  }, [])

  const handleSunDateTimeInputChange = useCallback((value: string) => {
    setSunDateTime(mauritiusLocalToUtcDate(value))
  }, [])

  const handleSunNow = useCallback(() => {
    setSunDateTime(new Date())
  }, [])

  useEffect(() => {
    const map = mapRef.current?.getMap()
    if (!map || !mapReady) return

    if (sunMode) {
      const result = applySunLight(map, ESTATE_CENTER.latitude, ESTATE_CENTER.longitude, sunDateTime)
      setSunOverlayColor(result.overlayColor)
      setSunInfo({ altitudeDeg: result.altitudeDeg, compassAzimuthDeg: result.compassAzimuthDeg })
    } else {
      applyTimeOfDay(map, timeOfDay)
      setSunOverlayColor(null)
      setSunInfo(null)
    }
  }, [sunMode, sunDateTime, timeOfDay, mapReady])

  useEffect(() => {
    const map = mapRef.current?.getMap()
    if (!map || !mapReady) return

    map.setLayoutProperty('hillshade', 'visibility', slopeContrast ? 'none' : 'visible')
    map.setLayoutProperty('hillshade-contrast', 'visibility', slopeContrast ? 'visible' : 'none')
  }, [slopeContrast, mapReady])

  useEffect(() => {
    let cancelled = false

    const load = () => {
      fetchCurrentWeather(ESTATE_CENTER.latitude, ESTATE_CENTER.longitude)
        .then((data) => {
          if (!cancelled) {
            setWeather(data)
            setWeatherError(null)
          }
        })
        .catch(() => {
          if (!cancelled) setWeatherError('Weather unavailable')
        })
    }

    load()
    const interval = setInterval(load, 10 * 60 * 1000)
    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [])

  const handleCaptureView = useCallback(() => {
    const map = mapRef.current?.getMap()
    if (!map) return
    const canvas = map.getCanvas()
    const link = document.createElement('a')
    link.download = `wolmar-estate-${Date.now()}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  }, [])

  const handleGenerateShareLink = useCallback(() => {
    const map = mapRef.current?.getMap()
    const center = map ? map.getCenter() : { lng: ESTATE_CENTER.longitude, lat: ESTATE_CENTER.latitude }

    const url = buildShareUrl({
      longitude: center.lng,
      latitude: center.lat,
      zoom: map?.getZoom(),
      pitch: map?.getPitch(),
      bearing: map?.getBearing(),
      timeOfDay,
      showOverlay,
      historicalYear,
      sunMode,
      sunDateTime: sunDateTime.toISOString(),
    })

    setShareUrl(url)
    setShareCopied(false)
    navigator.clipboard
      ?.writeText(url)
      .then(() => setShareCopied(true))
      .catch(() => {})
  }, [timeOfDay, showOverlay, historicalYear, sunMode, sunDateTime])

  const trailProfile = useMemo(() => computeElevationProfile(trailPoints), [trailPoints])

  const measureResult =
    measurePoints.length === 2
      ? {
          distanceMeters: haversineDistanceMeters(
            measurePoints[0].lngLat,
            measurePoints[1].lngLat,
          ),
          elevationDeltaMeters:
            measurePoints[0].elevation !== null && measurePoints[1].elevation !== null
              ? measurePoints[1].elevation - measurePoints[0].elevation
              : null,
        }
      : null

  return (
    <Map
      ref={mapRef}
      initialViewState={{
        longitude: shared.longitude ?? ESTATE_CENTER.longitude,
        latitude: shared.latitude ?? ESTATE_CENTER.latitude,
        zoom: shared.zoom ?? 15,
        pitch: shared.pitch ?? 65,
        bearing: shared.bearing ?? -20,
      }}
      style={{ width: '100%', height: '100%' }}
      mapStyle={mapStyle}
      preserveDrawingBuffer
      onClick={handleMapClick}
      onMouseMove={handleMapMouseMove}
      onMouseOut={handleMapMouseLeave}
      onLoad={() => setMapReady(true)}
      interactiveLayerIds={showOverlay ? ['terrain-zones-fill'] : []}
      cursor={measureActive || trailActive ? 'crosshair' : 'grab'}
    >
      <div
        className="time-overlay"
        style={{ backgroundColor: sunMode && sunOverlayColor !== null ? sunOverlayColor : overlayColorFor(timeOfDay) }}
      />

      <NavigationControl position="top-right" visualizePitch />
      <FullscreenControl position="top-right" />

      {historicalYear !== null && (
        <Source
          id="historical-imagery"
          type="raster"
          tiles={[waybackTileUrl(historicalYears.find((y) => y.year === historicalYear)!.releaseNum)]}
          tileSize={256}
        >
          <Layer id="historical-imagery-layer" type="raster" beforeId="hillshade" />
        </Source>
      )}

      {showOverlay && (
        <>
          <Source id="terrain-zones" type="geojson" data={terrainZoneCollection}>
            <Layer
              id="terrain-zones-fill"
              type="fill"
              paint={{
                'fill-color': [
                  'match',
                  ['get', 'type'],
                  'forest',
                  terrainTypeColors.forest,
                  'field',
                  terrainTypeColors.field,
                  'water',
                  terrainTypeColors.water,
                  'trail',
                  terrainTypeColors.trail,
                  '#888888',
                ],
                'fill-opacity': 0.35,
              }}
            />
            <Layer
              id="terrain-zones-outline"
              type="line"
              paint={{
                'line-color': [
                  'match',
                  ['get', 'type'],
                  'forest',
                  terrainTypeColors.forest,
                  'field',
                  terrainTypeColors.field,
                  'water',
                  terrainTypeColors.water,
                  'trail',
                  terrainTypeColors.trail,
                  '#888888',
                ],
                'line-width': 1.5,
              }}
            />
          </Source>

          <Source id="estate-boundary" type="geojson" data={boundaryGeometry}>
            <Layer
              id="estate-boundary-line"
              type="line"
              paint={{
                'line-color': '#ff4d4d',
                'line-width': 3,
                'line-dasharray': [3, 2],
              }}
            />
          </Source>
        </>
      )}

      {selectedZone && (
        <Popup
          longitude={
            selectedZone.coordinates.reduce((sum, c) => sum + c[0], 0) /
            selectedZone.coordinates.length
          }
          latitude={
            selectedZone.coordinates.reduce((sum, c) => sum + c[1], 0) /
            selectedZone.coordinates.length
          }
          anchor="bottom"
          onClose={() => setSelectedZone(null)}
          closeOnClick={false}
        >
          <strong>{selectedZone.name}</strong>
          <p>{selectedZone.description}</p>
        </Popup>
      )}

      {pois.map((poi) => (
        <Marker
          key={poi.id}
          longitude={poi.longitude}
          latitude={poi.latitude}
          anchor="bottom"
          onClick={(e) => {
            e.originalEvent.stopPropagation()
            setSelected(poi)
          }}
        >
          <div className="marker-pin" title={poi.name} />
        </Marker>
      ))}

      {selected && (
        <Popup
          longitude={selected.longitude}
          latitude={selected.latitude}
          anchor="top"
          onClose={() => setSelected(null)}
          closeOnClick={false}
        >
          <strong>{selected.name}</strong>
          <p>{selected.description}</p>
        </Popup>
      )}

      {measurePoints.map((p, i) => (
        <Marker key={i} longitude={p.lngLat[0]} latitude={p.lngLat[1]} anchor="center">
          <div className="measure-pin" />
        </Marker>
      ))}

      {measurePoints.length === 2 && (
        <Source
          id="measure-line"
          type="geojson"
          data={{
            type: 'Feature',
            properties: {},
            geometry: {
              type: 'LineString',
              coordinates: measurePoints.map((p) => p.lngLat),
            },
          }}
        >
          <Layer
            id="measure-line-layer"
            type="line"
            paint={{
              'line-color': '#ffdd57',
              'line-width': 3,
              'line-dasharray': [2, 1],
            }}
          />
        </Source>
      )}

      {trailPoints.map((p, i) => (
        <Marker key={i} longitude={p.lngLat[0]} latitude={p.lngLat[1]} anchor="center">
          <div className="trail-pin" />
        </Marker>
      ))}

      {trailPoints.length >= 2 && (
        <Source
          id="trail-line"
          type="geojson"
          data={{
            type: 'Feature',
            properties: {},
            geometry: {
              type: 'LineString',
              coordinates: trailPoints.map((p) => p.lngLat),
            },
          }}
        >
          <Layer
            id="trail-line-layer"
            type="line"
            paint={{
              'line-color': '#4ade80',
              'line-width': 3,
            }}
          />
        </Source>
      )}

      <ControlsPanel
        timeOfDay={timeOfDay}
        onTimeOfDayChange={handleTimeOfDayChange}
        tourRunning={tourRunning}
        onToggleTour={handleToggleTour}
        measureActive={measureActive}
        onToggleMeasure={handleToggleMeasure}
        measureResult={measureResult}
        onClearMeasure={handleClearMeasure}
        showOverlay={showOverlay}
        onToggleOverlay={handleToggleOverlay}
        hoverElevation={hoverElevation}
        historicalYear={historicalYear}
        onHistoricalYearChange={handleHistoricalYearChange}
        sunMode={sunMode}
        onToggleSunMode={handleToggleSunMode}
        sunDateTimeValue={utcDateToMauritiusLocalInputValue(sunDateTime)}
        onSunDateTimeChange={handleSunDateTimeInputChange}
        onSunNow={handleSunNow}
        sunInfo={sunInfo}
        weather={weather}
        weatherError={weatherError}
        onCaptureView={handleCaptureView}
        onGenerateShareLink={handleGenerateShareLink}
        shareUrl={shareUrl}
        shareCopied={shareCopied}
        trailActive={trailActive}
        onToggleTrail={handleToggleTrail}
        trailPointCount={trailPoints.length}
        trailProfile={trailProfile}
        onClearTrail={handleClearTrail}
        slopeContrast={slopeContrast}
        onToggleSlopeContrast={handleToggleSlopeContrast}
      />
    </Map>
  )
}
