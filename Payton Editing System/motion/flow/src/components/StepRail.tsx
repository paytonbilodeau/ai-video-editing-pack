import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {ease, fadeUp, pop, popStyle} from '../lib/anim';
import {pixel} from '../fonts';
import {T} from '../theme';

// Safe zone at 1080x1920 is x 90..940 (right rail!), so the visual
// center of every composition in this video is x=515, not 540.
export const CX = 540;

// Seconds (beat-relative) -> frames at 30fps.
export const S = (sec: number, fps = 30): number => Math.round(sec * fps);

// Phase opacity window: fades in at `enter`, starts fading out at `exit`.
export const phaseO = (
  frame: number,
  enter: number,
  exit: number,
  f = 9
): number => Math.min(ease(frame, enter, f), 1 - ease(frame, exit, f));

// Keycap chip: the pill/keycap used for step numbers, tokens, candidates.
export type ChipState = 'todo' | 'active' | 'done';

export const chipColors = (
  state: ChipState
): {bg: string; edge: string; text: string} =>
  state === 'active'
    ? {bg: T.goodFill, edge: T.goodFill, text: T.bg}
    : state === 'done'
      ? {bg: T.goodDeep, edge: T.goodDeep, text: T.good}
      : {bg: 'transparent', edge: T.cardEdge, text: T.muted};

// Persistent 5-chip step rail with a mutating step-name label beneath.
// steps[i].at = frame this step becomes the active one.
export const StepRail: React.FC<{
  delay: number;
  steps: {name: string; at: number}[];
  y?: number;
}> = ({delay, steps, y = 290}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const xs = steps.map((_, i) => 540 + (i - (steps.length - 1) / 2) * Math.min(170, 680 / Math.max(1, steps.length - 1)));
  let active = -1;
  steps.forEach((s, i) => {
    if (frame >= s.at) {
      active = i;
    }
  });
  return (
    <>
      {xs.map((x, i) => {
        const state: ChipState =
          i === active ? 'active' : i < active ? 'done' : 'todo';
        const c = chipColors(state);
        const settle = pop(frame, fps, i <= active ? steps[i].at : 0);
        const bump = i === active ? 1 + 0.06 * (1 - Math.min(1, settle)) : 1;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x - 42,
              top: y - 42,
              ...popStyle(frame, fps, delay + i * 6),
            }}
          >
            <div
              style={{
                width: 84,
                height: 84,
                borderRadius: 16,
                background: c.bg,
                border: `2.5px solid ${c.edge}`,
                boxShadow: state === 'active' ? T.shadow : 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontFamily: pixel,
                fontSize: 40,
                color: c.text,
                transform: `scale(${bump})`,
              }}
            >
              {i + 1}
            </div>
          </div>
        );
      })}
      {active >= 0 ? (
        <div
          key={active}
          style={{
            position: 'absolute',
            top: y + 66,
            left: 0,
            right: 0,
            textAlign: 'center',
            fontFamily: pixel,
            fontSize: 38,
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            color: T.ink,
            ...fadeUp(frame, fps, steps[active].at, 16),
          }}
        >
          {steps[active].name}
        </div>
      ) : null}
    </>
  );
};

// Small centered pixel-caps line (kickers, captions) with fadeUp entry.
export const Kicker: React.FC<{
  y: number;
  text: string;
  delay: number;
  size?: number;
  color?: string;
  spacing?: string;
}> = ({y, text, delay, size = 38, color, spacing = '0.18em'}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <div
      style={{
        position: 'absolute',
        top: y,
        left: 0,
        right: 0,
        textAlign: 'center',
        fontFamily: pixel,
        fontSize: size,
        letterSpacing: spacing,
        textTransform: 'uppercase',
        color: color ?? T.muted,
        ...fadeUp(frame, fps, delay, 18),
      }}
    >
      {text}
    </div>
  );
};
