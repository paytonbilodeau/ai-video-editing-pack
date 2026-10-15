#!/usr/bin/env python3
"""Restore authorized demonstration audio after enhancement without moving time.

Protected frame ranges are half-open and refer to the locked output timeline.
The output is a 32-bit float WAV. Original decoded float samples are copied
exactly inside protected ranges; fades occur only outside those ranges.
This does not run Auphonic, normalize the mix, or alter video.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf


def frame_sample(frame, fps, rate):
    return round(Fraction(frame) * rate / Fraction(str(fps)))


def normalize_ranges(ranges, fps, rate, total):
    spans = []
    for row in ranges:
        a, b = row['start_frame'], row['end_frame']
        if isinstance(a, bool) or isinstance(b, bool) or not isinstance(a, int) or not isinstance(b, int):
            raise ValueError('Frame boundaries must be integers')
        if not 0 <= a < b:
            raise ValueError('Protected ranges must have positive length')
        a, b = frame_sample(a, fps, rate), frame_sample(b, fps, rate)
        if not 0 <= a < b <= total:
            raise ValueError('Protected range exceeds the locked timeline')
        spans.append((a, b))
    merged = []
    for a, b in sorted(spans):
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else:
            merged.append((a, b))
    return merged


def weights(start, count, spans, fade_samples):
    x = np.arange(start, start + count, dtype=np.int64)
    weight = np.zeros(count, dtype=np.float64)
    for a, b in spans:
        weight[(x >= a) & (x < b)] = 1.0
        if fade_samples:
            pre = (x >= a - fade_samples) & (x < a)
            post = (x >= b) & (x < b + fade_samples)
            weight[pre] = np.maximum(weight[pre], (x[pre] - a + fade_samples) / fade_samples)
            weight[post] = np.maximum(weight[post], (b + fade_samples - x[post]) / fade_samples)
    return weight


def sample_hash(path, spans):
    digest = hashlib.sha256()
    with sf.SoundFile(path) as handle:
        for a, b in spans:
            handle.seek(a)
            remaining = b - a
            while remaining:
                block = handle.read(min(65536, remaining), dtype='float32', always_2d=True)
                if not len(block):
                    raise ValueError('Audio ended within a protected range')
                digest.update(np.asarray(block, dtype='<f4').tobytes())
                remaining -= len(block)
    return digest.hexdigest()


def restore(original, processed, manifest, output, fade_ms=40.0):
    original, processed, output = map(Path, (original, processed, output))
    if output.resolve() in (original.resolve(), processed.resolve()):
        raise ValueError('Output must not overwrite an input')
    if output.exists():
        raise ValueError('Output already exists; use a fresh filename')
    if not 0 <= fade_ms <= 250:
        raise ValueError('Transition duration must be between 0 and 250 milliseconds')
    fps = Fraction(str(manifest['fps']))
    frames = manifest['frames']
    if fps <= 0 or isinstance(frames, bool) or not isinstance(frames, int) or frames <= 0:
        raise ValueError('Invalid locked timeline')
    with sf.SoundFile(original) as source, sf.SoundFile(processed) as enhanced:
        if (source.samplerate, source.channels) != (enhanced.samplerate, enhanced.channels):
            raise ValueError('Inputs must have matching sample rate and channel count')
        rate, channels = source.samplerate, source.channels
        total = frame_sample(frames, fps, rate)
        if abs(len(source) - total) > rate / 10 or abs(len(enhanced) - total) > rate / 10:
            raise ValueError('Input duration differs by more than 100ms; align and investigate before restoration')
        spans = normalize_ranges(manifest['ranges'], fps, rate, total)
        if not spans:
            raise ValueError('No protected ranges supplied')
        if spans[-1][1] > len(source):
            raise ValueError('Original source does not cover every protected sample')
        original_frames, processed_frames = len(source), len(enhanced)
        fade = round(rate * fade_ms / 1000)
        with sf.SoundFile(output, 'w', samplerate=rate, channels=channels, format='WAV', subtype='FLOAT') as target:
            for start in range(0, total, 65536):
                count = min(65536, total - start)
                a = source.read(count, dtype='float32', always_2d=True)
                b = enhanced.read(count, dtype='float32', always_2d=True)
                a = np.pad(a, ((0, count - len(a)), (0, 0)))
                b = np.pad(b, ((0, count - len(b)), (0, 0)))
                w = weights(start, count, spans, fade)
                mixed = (b.astype(np.float64) * (1 - w[:, None]) + a.astype(np.float64) * w[:, None]).astype(np.float32)
                # Exact assignments avoid arithmetic changing protected samples.
                mixed[w == 1] = a[w == 1]
                mixed[w == 0] = b[w == 0]
                target.write(mixed)
    expected, actual = sample_hash(original, spans), sample_hash(output, spans)
    if expected != actual:
        raise ValueError('Protected sample verification failed')
    info = sf.info(output)
    return {
        'ok': True, 'original': str(original.resolve()), 'processed': str(processed.resolve()),
        'output': str(output.resolve()), 'fps': str(fps), 'timeline_frames': frames,
        'sample_rate': rate, 'channels': channels, 'output_samples': info.frames,
        'expected_samples': total, 'original_input_samples': original_frames,
        'processed_input_samples': processed_frames, 'fade_ms': fade_ms,
        'protected_sample_ranges': spans, 'protected_original_float32_sha256': expected,
        'protected_output_float32_sha256': actual, 'protected_samples_identical': expected == actual,
        'scope': 'Exact decoded float32 WAV samples inside protected ranges. Final lossy delivery encoding requires separate correlation and level checks.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-wav', required=True)
    parser.add_argument('--processed-wav', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--output-wav', required=True)
    parser.add_argument('--report', required=True)
    parser.add_argument('--fade-ms', type=float, default=40)
    args = parser.parse_args()
    report = restore(args.original_wav, args.processed_wav,
                     json.loads(Path(args.manifest).read_text()), args.output_wav, args.fade_ms)
    Path(args.report).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
