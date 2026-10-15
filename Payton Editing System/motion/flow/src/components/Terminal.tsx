import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {Check} from 'lucide-react';
import {fadeUp, popStyle} from '../lib/anim';
import {pixel} from '../fonts';
import {T} from '../theme';

export type TermLine = {text: string; tone?: 'ok' | 'dim'};

// Dark terminal window (the one dark object in the paper world).
// Typed command + staggered output lines. x,y = window center.
export const Terminal: React.FC<{
  y: number;
  delay: number;
  command: string;
  outputs?: TermLine[];
  x?: number;
  w?: number;
  cps?: number; // typed characters per second
  title?: string;
  outGap?: number; // frames between output lines
}> = ({
  y,
  delay,
  command,
  outputs = [],
  x = 540,
  w = 880,
  cps = 13,
  title = 'terminal',
  outGap = 12,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const typeStart = delay + 8;
  const chars = Math.max(
    0,
    Math.min(command.length, Math.floor(((frame - typeStart) * cps) / fps))
  );
  const typeDone = typeStart + Math.ceil((command.length * fps) / cps);
  const outStart = typeDone + 10;
  const cursorOn = frame % 20 < 11;

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: w,
        marginLeft: -w / 2,
        transform: 'translateY(-50%)',
        ...popStyle(frame, fps, delay),
      }}
    >
      <div
        style={{
          background: T.termBg,
          border: `2px solid ${T.termEdge}`,
          borderRadius: 18,
          boxShadow: '0 18px 44px rgba(60,60,60,0.28)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: 66,
            display: 'flex',
            alignItems: 'center',
            padding: '0 28px',
            gap: 13,
            background: 'rgba(255,255,255,0.05)',
            borderBottom: `1.5px solid ${T.termEdge}`,
          }}
        >
          {['#FF5F57', '#FEBC2E', '#28C840'].map((c) => (
            <div
              key={c}
              style={{width: 20, height: 20, borderRadius: 999, background: c}}
            />
          ))}
          <div
            style={{
              flex: 1,
              textAlign: 'center',
              fontFamily: pixel,
              fontSize: 24,
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              color: T.termDim,
              marginRight: 80,
            }}
          >
            {title}
          </div>
        </div>
        <div
          style={{
            padding: '34px 38px 40px',
            fontFamily: pixel,
            fontSize: 36,
            lineHeight: 1.9,
          }}
        >
          <div style={{color: '#ECEDEF'}}>
            <span style={{color: T.good}}>${' '}</span>
            {command.slice(0, chars)}
            {frame < outStart ? (
              <span
                style={{
                  display: 'inline-block',
                  width: 19,
                  height: 38,
                  marginLeft: 6,
                  verticalAlign: 'middle',
                  background: T.good,
                  opacity: cursorOn ? 0.95 : 0,
                }}
              />
            ) : null}
          </div>
          {outputs.map((line, i) => (
            <div
              key={i}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 16,
                color: line.tone === 'ok' ? T.good : T.termDim,
                ...fadeUp(frame, fps, outStart + i * outGap, 16),
              }}
            >
              {line.tone === 'ok' ? (
                <Check size={32} color={T.good} strokeWidth={3} />
              ) : null}
              <span>{line.text}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
