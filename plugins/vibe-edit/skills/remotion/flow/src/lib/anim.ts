import React from 'react';
import {Easing, interpolate, spring} from 'remotion';

// Springy pop, slight overshoot. Returns 0..~1.04..1
export const pop = (frame: number, fps: number, delay = 0) =>
  spring({
    frame: frame - delay,
    fps,
    config: {damping: 13, stiffness: 140, mass: 0.9},
  });

// Smooth ease between two values over [delay, delay+dur] frames
export const ease = (
  frame: number,
  delay: number,
  dur: number,
  from = 0,
  to = 1
) =>
  interpolate(frame, [delay, delay + dur], [from, to], {
    easing: Easing.inOut(Easing.cubic),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

export const easeOut = (
  frame: number,
  delay: number,
  dur: number,
  from = 0,
  to = 1
) =>
  interpolate(frame, [delay, delay + dur], [from, to], {
    easing: Easing.out(Easing.poly(5)),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

// Fade + slide up, spring-settled. Spread into a style object.
export const fadeUp = (
  frame: number,
  fps: number,
  delay: number,
  dist = 30
): React.CSSProperties => {
  const p = spring({
    frame: frame - delay,
    fps,
    config: {damping: 16, stiffness: 120, mass: 0.9},
  });
  return {
    opacity: Math.min(1, p * 1.5),
    transform: `translateY(${(1 - p) * dist}px)`,
  };
};

// Pop-in scale style for cards/chips
export const popStyle = (
  frame: number,
  fps: number,
  delay: number
): React.CSSProperties => {
  const p = pop(frame, fps, delay);
  return {
    opacity: Math.min(1, p * 1.7),
    transform: `scale(${0.88 + p * 0.12})`,
  };
};
