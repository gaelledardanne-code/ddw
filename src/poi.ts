export interface Poi {
  id: string
  name: string
  description: string
  longitude: number
  latitude: number
}

/**
 * PLACEHOLDER coordinates around Flic-en-Flac / Wolmar, Mauritius.
 * Not verified against the actual estate boundary — replace with
 * real pins once confirmed (e.g. from the venue or a site visit).
 */
export const pois: Poi[] = [
  {
    id: 'estate-center',
    name: 'Domaine de Wolmar',
    description: 'Approximate center of the hunting estate / nature reserve.',
    longitude: 57.368,
    latitude: -20.302,
  },
  {
    id: 'reception-hall',
    name: 'Salle de réception',
    description: 'Wedding / reception venue on the estate (placeholder location).',
    longitude: 57.3695,
    latitude: -20.3005,
  },
]
