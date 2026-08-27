export function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value))
}

export function hexToRgb(hex: string): [number, number, number] {
  const clean = hex.replace('#', '')
  const r = parseInt(clean.slice(0, 2), 16)
  const g = parseInt(clean.slice(2, 4), 16)
  const b = parseInt(clean.slice(4, 6), 16)
  return [r, g, b]
}

export function rgbToHex([r, g, b]: [number, number, number]): string {
  const toHex = (v: number) => clamp(Math.round(v), 0, 255).toString(16).padStart(2, '0')
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`
}

export function lerpHexColor(a: string, b: string, t: number): string {
  const [ar, ag, ab] = hexToRgb(a)
  const [br, bg, bb] = hexToRgb(b)
  return rgbToHex([lerp(ar, br, t), lerp(ag, bg, t), lerp(ab, bb, t)])
}

export function parseRgba(value: string): [number, number, number, number] {
  const match = value.match(/rgba?\(([^)]+)\)/)
  if (!match) return [0, 0, 0, 0]
  const parts = match[1].split(',').map((p) => parseFloat(p.trim()))
  return [parts[0] ?? 0, parts[1] ?? 0, parts[2] ?? 0, parts[3] ?? 1]
}

export function lerpRgba(a: string, b: string, t: number): string {
  const [ar, ag, ab, aa] = parseRgba(a)
  const [br, bg, bb, ba] = parseRgba(b)
  const r = Math.round(lerp(ar, br, t))
  const g = Math.round(lerp(ag, bg, t))
  const bl = Math.round(lerp(ab, bb, t))
  const alpha = lerp(aa, ba, t)
  return `rgba(${r}, ${g}, ${bl}, ${alpha.toFixed(3)})`
}
