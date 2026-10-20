#!/usr/bin/env python3
"""Flow SFX engine: procedural UI sound effects, frame-synced to Flow
motion graphics. Zero cost, deterministic, ElevenLabs-free.

Usage:
  python3.11 execution/flow_sfx.py timeline.json out.wav [--duration 123.0]

timeline.json: [{"t": 1.45, "s": "pop"}, {"t": 2.6, "s": "draw",
                "pitch": 2, "gain": -3}, ...]
  t     seconds in the final video
  s     sound name (below)
  pitch semitone offset (default 0; auto-jitter is added for variety)
  gain  dB offset from the sound's base level (default 0)

Palette (subtle UI-grade, tuned to sit under -16 LUFS voice):
  pop     card/chip/tile pops in
  tick    small cascade items, slots, bricks
  key     single soft keystroke (terminal/answer typing)
  draw    connector/line draws on
  whoosh  lockup or scene mutation
  air     beat fade-in breath (very quiet)
  ting    highlight/annotation
  chime   affirmative two-note (chosen, success)
  check   single low ting for checklist rows
  step    signature two-tone step-rail advance
  shimmer chips flip to numbers / sparkle transform
  thump   black-flash hard cut
The final track is peak-normalized to -20 dBFS: drop it on the timeline
at 0:00 under the Auphonic -16 LUFS voice and it sits subtle by default.
"""
import hashlib, json, sys, wave
from pathlib import Path
import numpy as np

SR = 48000


def env_exp(n, attack=0.003, decay=6.0):
    t = np.arange(n) / SR
    e = np.exp(-t * decay / max(t[-1], 1e-6) * 5)
    a = int(attack * SR)
    if a > 0:
        e[:a] *= np.linspace(0, 1, a)
    return e


def hann(n):
    return np.hanning(n)


def bandnoise(n, lo, hi):
    x = np.random.randn(n)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, n)


def st(semitones):
    return 2 ** (semitones / 12)


def s_pop(p=0):
    n = int(0.10 * SR)
    t = np.arange(n) / SR
    f0 = 520 * st(p)
    freq = f0 * (1 + 0.65 * np.exp(-t * 55))
    x = np.sin(2 * np.pi * np.cumsum(freq) / SR) * env_exp(n, decay=7)
    x += 0.12 * bandnoise(n, 1500, 6000) * env_exp(n, 0.001, 30)
    return x * 0.9


def s_tick(p=0):
    n = int(0.035 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 1250 * st(p) * t) * env_exp(n, 0.001, 18)
    return x * 0.5


def s_key(p=0):
    n = int(0.02 * SR)
    x = bandnoise(n, 1800, 5200) * env_exp(n, 0.0005, 25)
    return x * 0.32


def s_draw(p=0):
    n = int(0.16 * SR)
    e = hann(n) ** 0.7
    x = bandnoise(n, 900 * st(p), 4200 * st(p)) * e
    return x * 0.4


def s_whoosh(p=0):
    n = int(0.36 * SR)
    e = hann(n) ** 1.4
    x = bandnoise(n, 400, 2600) * e
    return x * 0.5


def s_air(p=0):
    n = int(0.5 * SR)
    x = bandnoise(n, 300, 1500) * hann(n) ** 2
    return x * 0.22


def s_ting(p=0):
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    f = 1700 * st(p)
    x = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.6 * t))
    return x * env_exp(n, 0.001, 9) * 0.34


def s_check(p=0):
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    f = 660 * st(p)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 2 * t)
    return x * env_exp(n, 0.002, 10) * 0.4


def s_chime(p=0):
    a, b = s_check(p), s_ting(p + 7)
    off = int(0.07 * SR)
    n = max(len(a), off + len(b))
    x = np.zeros(n)
    x[:len(a)] += a
    x[off:off + len(b)] += b * 0.8
    return x


def s_step(p=0):
    n1, n2 = int(0.07 * SR), int(0.09 * SR)
    t1, t2 = np.arange(n1) / SR, np.arange(n2) / SR
    f1, f2 = 480 * st(p), 640 * st(p)
    a = (np.sin(2 * np.pi * f1 * t1) + 0.25 * np.sin(2 * np.pi * 3 * f1 * t1)) * env_exp(n1, 0.002, 6)
    b = (np.sin(2 * np.pi * f2 * t2) + 0.25 * np.sin(2 * np.pi * 3 * f2 * t2)) * env_exp(n2, 0.002, 6)
    return np.concatenate([a, b * 1.05]) * 0.42


def s_shimmer(p=0):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    rng = np.random.default_rng(7)
    for f in rng.uniform(1200, 2800, 5):
        g = f * st(p) * (1 + 0.04 * t / t[-1])
        x += np.sin(2 * np.pi * np.cumsum(g) / SR)
    return x / 5 * hann(n) * 0.3


def s_thump(p=0):
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    f = 120 * st(p) * np.exp(-t * 9) + 55
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.002, 7)
    x += 0.25 * bandnoise(n, 60, 500) * env_exp(n, 0.001, 12)
    return x * 0.8


SOUNDS = {"pop": s_pop, "tick": s_tick, "key": s_key, "draw": s_draw,
          "whoosh": s_whoosh, "air": s_air, "ting": s_ting,
          "check": s_check, "chime": s_chime, "step": s_step,
          "shimmer": s_shimmer, "thump": s_thump}
BASE_DB = {"pop": -2, "tick": -5, "key": -10, "draw": -5, "whoosh": -4,
           "air": -9, "ting": -6, "check": -4, "chime": -3, "step": -2,
           "shimmer": -6, "thump": -2}


def main():
    tl_path, out_path = sys.argv[1], sys.argv[2]
    if Path(out_path).exists(): raise SystemExit("Refusing existing output; use a new file.")
    # Procedural noise is part of several sounds. Reset it for every render so
    # the same timeline produces byte-identical audio across processes.
    np.random.seed(0)
    dur = None
    if "--duration" in sys.argv:
        dur = float(sys.argv[sys.argv.index("--duration") + 1])
    events = json.load(open(tl_path))
    end = max((e["t"] for e in events), default=0) + 1.5
    total = int((dur or end) * SR)
    track = np.zeros(total)
    for i, e in enumerate(events):
        fn = SOUNDS[e["s"]]
        # Deterministic per-event micro-variation (pitch +-0.6 st). Python's
        # built-in string hash changes between processes, so derive the jitter
        # from stable bytes instead.
        digest = hashlib.sha256(f'{i}:{e["s"]}'.encode()).digest()
        jitter = (int.from_bytes(digest[:4], "big") % 1000 / 1000 - 0.5) * 1.2
        x = fn(e.get("pitch", 0) + jitter)
        g = 10 ** ((BASE_DB[e["s"]] + e.get("gain", 0)) / 20)
        start = int(e["t"] * SR)
        seg = x[: max(0, total - start)] * g
        track[start:start + len(seg)] += seg
    peak = np.max(np.abs(track)) or 1.0
    track = track / peak * 10 ** (-20 / 20)   # peak -20 dBFS
    stereo = np.repeat(track[:, None], 2, axis=1)
    pcm = (stereo * 32767).astype(np.int16)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"wrote {out_path}: {len(events)} events, "
          f"{total / SR:.2f}s, peak -20 dBFS")


if __name__ == "__main__":
    main()
