/**
 * Curated stops into the Esri World Imagery Wayback archive — a free,
 * keyless archive of dated satellite imagery snapshots. Release numbers
 * verified to return real (non-empty) tiles over the estate.
 * https://livingatlas.arcgis.com/wayback/
 */
export interface HistoricalYear {
  year: number
  releaseNum: number
}

export const historicalYears: HistoricalYear[] = [
  { year: 2014, releaseNum: 10 },
  { year: 2016, releaseNum: 3515 },
  { year: 2018, releaseNum: 13161 },
  { year: 2020, releaseNum: 23001 },
  { year: 2022, releaseNum: 42663 },
  { year: 2024, releaseNum: 41468 },
]

export function waybackTileUrl(releaseNum: number): string {
  return `https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/MapServer/tile/${releaseNum}/{z}/{y}/{x}`
}
