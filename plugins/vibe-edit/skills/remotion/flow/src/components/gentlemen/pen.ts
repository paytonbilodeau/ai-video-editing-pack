import raw from './reenie-glyphs.json';

export type Stroke = {d: string; length: number; width: number};
export type Glyph = {d: string; advance: number; strokes: Stroke[]};
export type PenEvent = Stroke & {from: number; to: number};
export type Letter = {glyph: Glyph; x: number; strokes: PenEvent[]};
const glyphs = raw.glyphs as Record<string, Glyph>;
const memo = new Map<string, {letters: Letter[]; width: number; events: PenEvent[]}>();

/** This schedule drives both SVG masks and the exported Foley track. */
export const penLayout = (text: string, start: number, duration: number) => {
  if (!(duration > 0) || !Number.isFinite(duration) || !Number.isFinite(start)) throw new Error('Invalid pen timing');
  const key = `${text}|${start}|${duration}`;
  const cached = memo.get(key);
  if (cached) return cached;
  const letters: Letter[] = [];
  let x = 0;
  let weight = 0;
  for (const c of text) {
    const glyph = glyphs[c];
    if (!glyph) throw new Error(`The Gentlemen Style has no pen glyph for ${JSON.stringify(c)}. Compile the font before rendering.`);
    const strokes = glyph.strokes.map((s) => {
      const from = weight;
      weight += Math.max(55, Math.pow(s.length, .88));
      const to = weight;
      weight += 9; // Small pen lift; detached dots do not make an audible click.
      return {...s, from, to};
    });
    letters.push({glyph, x, strokes});
    x += glyph.advance;
    weight += c === ' ' ? 85 : 12;
  }
  const total = Math.max(weight - 12, 1);
  letters.forEach((letter) => letter.strokes.forEach((s) => {
    s.from = start + (s.from / total) * duration;
    s.to = start + (s.to / total) * duration;
  }));
  const layout = {letters, width: x, events: letters.flatMap((l) => l.strokes)};
  memo.set(key, layout);
  return layout;
};

export const clamp = (x: number) => Math.max(0, Math.min(1, x));
export const progress = (t: number, start: number, duration: number) => clamp((t - start) / duration);
export const phase = (t: number, start: number, end = Infinity) => t < start ? 0 : clamp((end - t) / .16);
export const inkWidth = (text: string, size: number) => penLayout(text, 0, 1).width * size / 1000;
