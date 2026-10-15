// Flow palettes. Canonical brand colors: memory/profile/brand-colors.md
// Both brand lanes are NEUTRAL-FIRST (white, black, all grays shared).
// Contrast pairing law: dark bg -> LIGHT accent carries the design, deep
// brand shade is depth only. Light bg -> DEEP accent carries the design,
// light brand shade is highlights/tone-on-tone only.
// Routing: AI topic -> mentorship lane. Anything else -> echo lane.
// Default mode is dark (Payton prefers black backgrounds); use the
// '-light' variant when he asks for a white/light background.
// 'lab' is the legacy light Train Bloom look (demo + v0725 renders).
// Scenes MUST call setPalette('<name>') as the first line of the component.

export type PaletteName =
  | 'lab'
  | 'mentorship'
  | 'mentorship-light'
  | 'echo'
  | 'echo-light';

type Palette = {
  bg: string; ink: string; muted: string; dim: string; label: string;
  labelBg: string; axis: string;
  good: string; goodFill: string; goodDeep: string;
  bad: string; badFill: string; badDeep: string;
  ghost: string; card: string; cardEdge: string; tile: string;
  termBg: string; termEdge: string; termDim: string;
  flash: string; chip: string; shadow: string; grain: number;
};

export const PALETTES: Record<PaletteName, Palette> = {
  // Legacy light lab paper, blue accent (Train Bloom study)
  lab: {
    bg: '#F2F2F3', ink: '#3C3C3C', muted: '#8F939B', dim: '#B6B9BE',
    label: '#6E7278', labelBg: 'rgba(242,242,243,0.92)', axis: '#9FA3AA',
    good: '#22A9F5', goodFill: '#66BAFC', goodDeep: '#3D8FD1',
    bad: '#DE545A', badFill: '#F6A29C', badDeep: '#D97F79',
    ghost: '#D8D9DC', card: '#FFFFFF', cardEdge: '#E3E4E7', tile: '#FFFFFF',
    termBg: '#1B1C20', termEdge: '#2A2B30', termDim: '#8A8D93',
    flash: '#FFFFFF', chip: '#3C3C3C',
    shadow: '0 14px 34px rgba(60,60,60,0.12)', grain: 0.05,
  },
  // AI lane, black bg: Mint carries, Old Money Green is depth only
  mentorship: {
    bg: '#0A0B0B', ink: '#FBFEFF', muted: '#BEC3C6', dim: '#8A8E90',
    label: '#CDD1D4', labelBg: 'rgba(10,11,11,0.92)', axis: '#878B8E',
    good: '#72DFA5', goodFill: '#72DFA5', goodDeep: '#0F583D',
    bad: '#8F8D8B', badFill: '#3A3937', badDeep: '#BEC3C6',
    ghost: '#232626', card: '#161819', cardEdge: 'rgba(255,255,255,0.12)',
    tile: '#FFFFFF',
    termBg: '#101214', termEdge: '#2A2D2E', termDim: '#9AA0A2',
    flash: '#000000', chip: '#FBFEFF',
    shadow: '0 16px 40px rgba(0,0,0,0.55)', grain: 0.06,
  },
  // AI lane, off-white bg: Old Money Green carries, mint is highlight only
  'mentorship-light': {
    bg: '#F2F0EF', ink: '#252525', muted: '#868583', dim: '#A8A6A3',
    label: '#55534F', labelBg: 'rgba(242,240,239,0.92)', axis: '#8E8C89',
    good: '#0F583D', goodFill: '#0F583D', goodDeep: '#72DFA5',
    bad: '#9A9895', badFill: '#D8D6D3', badDeep: '#6B6966',
    ghost: '#DEDCD9', card: '#FFFFFF', cardEdge: '#E3E1DE', tile: '#FFFFFF',
    termBg: '#1B1C20', termEdge: '#2A2B30', termDim: '#8A8D93',
    flash: '#FFFFFF', chip: '#252525',
    shadow: '0 14px 34px rgba(60,60,60,0.12)', grain: 0.05,
  },
  // Echo lane, dark navy-black bg: Light Aqua carries, turquoise is depth
  echo: {
    bg: '#10141F', ink: '#F2F0EF', muted: '#BEC3C6', dim: '#8B90A0',
    label: '#CDD1D8', labelBg: 'rgba(16,20,31,0.92)', axis: '#7E8494',
    good: '#72C7DF', goodFill: '#72C7DF', goodDeep: '#1F6F78',
    bad: '#8E92A0', badFill: '#3B3F4D', badDeep: '#BEC3C6',
    ghost: '#242B3D', card: '#1B2232', cardEdge: 'rgba(255,255,255,0.12)',
    tile: '#FFFFFF',
    termBg: '#0D1119', termEdge: '#293042', termDim: '#9AA0AD',
    flash: '#000000', chip: '#F2F0EF',
    shadow: '0 16px 40px rgba(0,0,0,0.55)', grain: 0.06,
  },
  // Echo lane, off-white bg: Dark Turquoise/navy carry, aqua is highlight
  'echo-light': {
    bg: '#F2F0EF', ink: '#252525', muted: '#868583', dim: '#A8A6A3',
    label: '#50545E', labelBg: 'rgba(242,240,239,0.92)', axis: '#8E9099',
    good: '#1F6F78', goodFill: '#1F6F78', goodDeep: '#72C7DF',
    bad: '#9A9DA5', badFill: '#D9D9DC', badDeep: '#63666E',
    ghost: '#DEDEE0', card: '#FFFFFF', cardEdge: '#E2E2E4', tile: '#FFFFFF',
    termBg: '#171A22', termEdge: '#2A2E3A', termDim: '#8E93A0',
    flash: '#FFFFFF', chip: '#202A44',
    shadow: '0 14px 34px rgba(60,60,60,0.12)', grain: 0.05,
  },
};

let current: PaletteName = 'lab';
export const setPalette = (p: PaletteName): void => {
  current = p;
};

// Live token object: always reads from the active palette.
export const T = new Proxy({} as Palette, {
  get: (_t, k) => PALETTES[current][k as keyof Palette],
}) as Palette;

export type Tone = 'ink' | 'muted' | 'good' | 'bad';

export const tone = (t?: Tone): string =>
  t === 'good' ? T.good : t === 'bad' ? T.bad : t === 'muted' ? T.muted : T.ink;
