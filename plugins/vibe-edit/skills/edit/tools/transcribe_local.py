#!/usr/bin/env python3
"""Transcribe through an installed local faster-whisper model after FFmpeg decoding.

No model download, account access, media upload or editor mutation. Word times
remain estimates until checked against the source. Existing output is preserved.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--language', default='en')
    parser.add_argument('--model', default='small', help='Already cached model name or local model directory')
    parser.add_argument('--ffmpeg', help='Existing FFmpeg executable; otherwise use PATH')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output exists; choose a new path to preserve previous work.')
    if not args.source.is_file():
        parser.error('Source is not a readable file.')
    ffmpeg = args.ffmpeg or shutil.which('ffmpeg')
    if not ffmpeg:
        parser.error('FFmpeg is not available. Select an existing executable with --ffmpeg.')
    try:
        import numpy as np
        from faster_whisper import WhisperModel
    except ImportError:
        parser.error('Use an existing Python environment with numpy and faster-whisper. No package was installed.')
    try:
        model = WhisperModel(args.model, device='cpu', compute_type='int8',
                             cpu_threads=4, local_files_only=True)
    except Exception as error:
        parser.error('The selected local model could not be loaded. No download was requested. ' + type(error).__name__)
    pcm = subprocess.run([ffmpeg, '-v', 'error', '-i', str(args.source), '-vn',
                          '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'],
                         check=True, capture_output=True).stdout
    segments, info = model.transcribe(np.frombuffer(pcm, dtype=np.float32),
                                      language=args.language, word_timestamps=True, beam_size=5)
    rows = [{'start': s.start, 'end': s.end, 'text': s.text,
             'words': [{'word': w.word, 'start': w.start, 'end': w.end,
                        'probability': w.probability} for w in (s.words or [])]}
            for s in segments]
    digest = hashlib.sha256()
    with args.source.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    result = {'source': args.source.name, 'source_sha256': digest.hexdigest(),
              'model': args.model, 'runtime': 'faster-whisper',
              'audio_decode': 'ffmpeg f32le mono 16kHz',
              'alignment': 'ASR word estimates; verify against source before editing',
              'segments': rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as output:
        output.write(json.dumps(result, indent=2) + '\n')
    print('Saved', len(rows), 'segments to', args.output)


if __name__ == '__main__':
    main()
