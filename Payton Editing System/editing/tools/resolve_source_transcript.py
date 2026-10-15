#!/usr/bin/env python3
"""Prepare a source-timed ASR draft for Resolve review. Never edit the media.

Run with the your configured Python 3.11+ runtime. Reuses the maintained local Whisper
helper; its timestamps and wording still require source verification.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

import jump_cut_vad_parallel as speech


def timestamp(seconds):
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"


def validate_words(words, duration):
    """Reject unsafe intervals, while preserving genuine overlapping word timing."""
    previous = -1.0
    for index, word in enumerate(words):
        start, end = float(word['start']), float(word['end'])
        if (not math.isfinite(start) or not math.isfinite(end)
                or start < 0 or end < start or end > duration + 0.1
                or start < previous or not str(word['word']).strip()):
            raise ValueError(f"Invalid source word interval at index {index}")
        previous = start


def write_draft(destination, source, words):
    validate_words(words, source['duration_seconds'])
    rejection = speech.transcript_looks_broken(words)
    if not words:
        rejection = 'No recognized words; inspect the original audio.'
    (destination / 'source-words.auto.json').write_text(
        json.dumps(words, ensure_ascii=False, indent=2) + '\n')
    manifest = dict(source, word_count=len(words),
                    state='rejected_asr_draft' if rejection else 'unverified_asr_draft',
                    source_verified=False, rejection_reason=rejection)
    (destination / 'source-transcript-manifest.json').write_text(
        json.dumps(manifest, indent=2) + '\n')
    lines = ['# Original recording: timestamped ASR draft', '',
             'Not yet verified against the recording. Automatic recognition can omit',
             'stutters, repeated syllables, abandoned takes and complete spoken phrases.',
             'These are source-relative word times, not exact phoneme boundaries.', '',
             f"Source: {source['source']}",
             f"Source SHA256: {source['source_sha256']}",
             f"Duration: {source['duration_seconds']:.3f} seconds", '',
             '| Word index | Source start | Source end | Recognized wording |',
             '| --- | --- | --- | --- |']
    for index, word in enumerate(words):
        text = str(word['word']).replace('|', '\\|').replace('\n', ' ')
        lines.append(f"| {index} | {timestamp(word['start'])} | "
                     f"{timestamp(word['end'])} | {text} |")
    (destination / 'source-transcript.auto.md').write_text('\n'.join(lines) + '\n')
    (destination / 'source-review.md').write_text(
        '# Source verification and take decisions\n\n'
        'State: pending. Preserve the automatic files and record corrections here.\n\n'
        '## Coverage\n\n'
        '| Source start/end | Review evidence | Missing or uncertain speech | Resolution |\n'
        '| --- | --- | --- | --- |\n\n'
        '## Verbatim corrections and utterances\n\n'
        '| Source start/end | Words actually spoken, including false starts | Evidence |\n'
        '| --- | --- | --- |\n\n'
        '## Take decisions\n\n'
        '| Candidate source ranges | Complete take kept | Reason | Protected meaning/UI |\n'
        '| --- | --- | --- | --- |\n\n'
        'Use source-transcript-review.md in the Resolve skill. A filled table or\n'
        'successful ASR run alone does not establish an accurate transcript.\n')
    return manifest


def prepare(media, destination, model):
    media = media.expanduser().resolve(strict=True)
    destination = destination.expanduser().resolve()
    if not media.is_file():
        raise ValueError('Input must be a media file.')
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError('Use a new transcript directory; existing work is preserved.')
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(media)]))
    if not any(s['codec_type'] == 'audio' for s in probe['streams']):
        raise ValueError('The recording has no audio stream.')
    duration = float(probe['format']['duration'])
    with media.open('rb') as handle:
        digest = hashlib.file_digest(handle, 'sha256').hexdigest()
    video = next((s for s in probe['streams'] if s['codec_type'] == 'video'), {})
    destination.mkdir(parents=True, exist_ok=True)
    audio = destination / 'source-analysis.wav'
    speech.extract_audio(str(media), str(audio))
    words = speech.transcribe_with_whisper(str(audio), model)
    with media.open('rb') as handle:
        if hashlib.file_digest(handle, 'sha256').hexdigest() != digest:
            raise RuntimeError('Source changed during transcription; do not use this draft.')
    return write_draft(destination, {
        'source': str(media), 'source_sha256': digest, 'duration_seconds': duration,
        'source_fps': video.get('avg_frame_rate'), 'timestamp_origin': 'source beginning, seconds',
        'requested_model': model, 'language': 'en',
        'recognizer': 'jump_cut_vad_parallel.transcribe_with_whisper; local MLX/CPU fallback',
    }, words)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output_dir', type=Path)
    parser.add_argument('--model', default='medium')
    args = parser.parse_args()
    result = prepare(args.input, args.output_dir, args.model)
    print(json.dumps(result, indent=2))
    return 1 if result['rejection_reason'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
