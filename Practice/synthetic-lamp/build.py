#!/usr/bin/env python3
"""Rebuild the synthetic lamp exercise using prepared cards and the public exporter.

Requires Python 3.11+, FFmpeg, ffprobe, and the current pack's exporter.
Never uses a speech service or changes the supplied illustration originals.
"""
from __future__ import annotations

import argparse
import array
import hashlib
import importlib.util
import json
import math
import shutil
import subprocess
import sys
import wave
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
FPS = 24
RATE = 48000


def run(args: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise RuntimeError('\n'.join((result.stderr or result.stdout).splitlines()[-20:]))
    return result


def ff(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return run(['ffmpeg', '-nostdin', '-hide_banner', '-nostats', '-n', *args], cwd=cwd)


def wav(path: Path, samples: list[float]) -> None:
    data = array.array('h', (round(max(-1, min(1, x)) * 32767) for x in samples))
    if sys.byteorder != 'little':
        data.byteswap()
    with wave.open(str(path), 'wb') as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(RATE)
        file.writeframes(data.tobytes())


def loudness(path: Path) -> dict:
    result = ff('-i', str(path), '-af', 'loudnorm=I=-23:TP=-3:LRA=7:print_format=json',
                '-f', 'null', '-')
    return json.JSONDecoder().raw_decode(result.stderr[result.stderr.rfind('{'):])[0]


def normalize(source: Path, output: Path) -> dict:
    measured = loudness(source)
    params = ('loudnorm=I=-23:TP=-3:LRA=7:linear=true:'
              f'measured_I={measured["input_i"]}:measured_TP={measured["input_tp"]}:'
              f'measured_LRA={measured["input_lra"]}:measured_thresh={measured["input_thresh"]}:'
              f'offset={measured["target_offset"]}')
    ff('-i', str(source), '-af', params, '-ar', str(RATE), '-ac', '1',
       '-c:a', 'pcm_s16le', str(output))
    return loudness(output)


def probe(path: Path) -> dict:
    return json.loads(run(['ffprobe', '-v', 'error', '-count_frames', '-show_entries',
                          'stream=index,codec_type,codec_name,width,height,avg_frame_rate,nb_read_frames,sample_rate,channels,duration:format=duration',
                          '-of', 'json', str(path)]).stdout)


def portable_interchange(path: Path) -> None:
    tree = ET.parse(path)
    for node in tree.findall('.//media-rep'):
        node.set('src', 'file://localhost/source.mp4')
    for node in tree.findall('.//file/pathurl'):
        node.text = 'file://localhost/source.mp4'
    tree.write(path, encoding='utf-8', xml_declaration=True)


def build(output: Path, exporter_path: Path) -> None:
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise RuntimeError('FFmpeg and ffprobe must already be installed.')
    output = output.expanduser().resolve()
    if output.exists():
        raise RuntimeError('Choose a new output folder; existing files are preserved.')
    cards = ['01-wait.png', '02-ready.png', '03-on.png', '04-result.png', '05-tail.png',
             'header-corrected.png', 'header-too-short.png']
    for name in cards:
        if not (ROOT / 'assets' / name).is_file():
            raise RuntimeError(f'Missing prepared card: assets/{name}')
    if not exporter_path.is_file():
        raise RuntimeError('Supply the current pack tools/cut_list_to_timeline.py with --exporter.')
    spec = importlib.util.spec_from_file_location('lamp_exporter', exporter_path)
    exporter = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = exporter
    spec.loader.exec_module(exporter)
    output.mkdir(parents=True)
    (output / 'assets').mkdir()
    for name in cards:
        shutil.copyfile(ROOT / 'assets' / name, output / 'assets' / name)
    for name in ['START HERE.md', 'BRIEF.md', 'ACCEPTED PREFERENCE.md', 'RIGHTS AND LIMITS.md', 'relink.py', 'build.py']:
        shutil.copyfile(ROOT / name, output / name)

    click = [0.0] * (10 * RATE)
    for i in range(round(.045 * RATE)):
        t = i / RATE
        attack = min(1.0, t / .0004)
        click[4 * RATE + i] = .23 * attack * math.exp(-t * 170) * (
            math.sin(2 * math.pi * 2200 * t) + .35 * math.sin(2 * math.pi * 3400 * t))
    wav(output / 'source-audio.wav', click)
    wav(output / 'corrected-audio.wav', click[2 * RATE:9 * RATE])
    wav(output / 'too-short-audio.wav', click[96000:190000] + click[238000:432000])
    lines = ['ffconcat version 1.0']
    for name, duration in zip(cards[:5], [2, 2, 3, 2, 1]):
        lines.extend([f"file 'assets/{name}'", f'duration {duration}'])
    lines.append("file 'assets/05-tail.png'")
    (output / 'scenes.ffconcat').write_text('\n'.join(lines) + '\n')
    encode = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-g', '24',
              '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', str(RATE),
              '-ac', '1', '-movflags', '+faststart']
    ff('-f', 'concat', '-safe', '0', '-i', 'scenes.ffconcat', '-i', 'source-audio.wav',
       '-vf', 'fps=24', '-frames:v', '240', '-t', '10', *encode, 'source.mp4', cwd=output)
    ff('-i', 'source.mp4', '-loop', '1', '-i', 'assets/header-corrected.png',
       '-filter_complex',
       '[0:v]trim=start_frame=48:end_frame=216,setpts=PTS-STARTPTS[v];'
       '[v][1:v]overlay=0:0:shortest=1[outv];'
       '[0:a]atrim=start_sample=96000:end_sample=432000,asetpts=PTS-STARTPTS[outa]',
       '-map', '[outv]', '-map', '[outa]', '-r', '24', '-frames:v', '168', '-t', '7',
       *encode, 'corrected.mp4', cwd=output)
    ff('-i', 'source.mp4', '-loop', '1', '-i', 'assets/header-too-short.png',
       '-filter_complex',
       '[0:v]split=2[v1][v2];[v1]trim=start_frame=48:end_frame=95,setpts=PTS-STARTPTS[a];'
       '[v2]trim=start_frame=119:end_frame=216,setpts=PTS-STARTPTS[b];'
       '[a][b]concat=n=2:v=1:a=0[v];[v][1:v]overlay=0:0:shortest=1[outv];'
       '[0:a]asplit=2[x1][x2];[x1]atrim=start_sample=96000:end_sample=190000,asetpts=PTS-STARTPTS[x];'
       '[x2]atrim=start_sample=238000:end_sample=432000,asetpts=PTS-STARTPTS[y];'
       '[x][y]concat=n=2:v=0:a=1[outa]',
       '-map', '[outv]', '-map', '[outa]', '-r', '24', '-frames:v', '144', '-t', '6',
       *encode, 'too-short.mp4', cwd=output)

    base = {'source': 'source.mp4', 'fps': 24, 'width': 1280, 'height': 720,
            'duration': 10, 'audio_channels': 1, 'audio_rate': RATE,
            'markers': [{'time': 4, 'name': 'Synthetic switch click',
                         'note': 'Keep the click and the following result hold.'}]}
    correct = {**base, 'name': 'lamp-practice-corrected',
               'keep': [{'start': 2, 'end': 9, 'note': 'Remove only the opening and closing wait.'}]}
    wrong = {**base, 'name': 'lamp-practice-too-short',
             'keep': [{'start': 2, 'end': '00:00:03:23', 'note': 'Before click'},
                      {'start': '00:00:04:23', 'end': 9, 'note': 'Intentional error: one-second window containing click removed.'}]}
    for name, data in [('cut-list.json', correct), ('too-short-cut-list.json', wrong)]:
        (output / name).write_text(json.dumps(data, indent=2) + '\n')
    cut = exporter.build_cut_list(correct, base_dir=output, probe=True)
    written = exporter.export(cut, output, ('fcpxml', 'xmeml', 'edl', 'sheet'), False, '1.11')
    for kind in ('fcpxml', 'xmeml'):
        portable_interchange(written[kind])
    summary = json.loads(written['summary'].read_text())
    summary['source'] = 'source.mp4'
    summary['files'] = {k: p.name for k, p in written.items() if k != 'summary'}
    summary['sha256'] = {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in written.items() if k != 'summary'}
    summary['mediaPathNote'] = 'Privacy-safe placeholder. Run relink.py here or relink source.mp4 in the editor.'
    written['summary'].write_text(json.dumps(summary, indent=2) + '\n')
    (output / 'source.srt').write_text('1\n00:00:04,000 --> 00:00:04,650\n[synthetic switch click]\n')
    (output / 'corrected.srt').write_text('1\n00:00:02,000 --> 00:00:02,650\n[synthetic switch click]\n')

    clean, noisy = [], []
    for i in range(8 * RATE):
        t = i / RATE
        fade = min(1.0, t / .5, (8 - t) / .5)
        tone = .07 * math.sin(2 * math.pi * 660 * t)
        # Keep hum audible but modest so matching total loudness does not make
        # the wanted tone substantially louder after filtering.
        hum = .018 * math.sin(2 * math.pi * 60 * t) + .007 * math.sin(2 * math.pi * 120 * t)
        clean.append(tone * fade)
        noisy.append((tone + hum) * fade)
    wav(output / 'tone-reference-unmatched.wav', clean)
    wav(output / 'tone-with-hum-unmatched.wav', noisy)
    ff('-i', str(output / 'tone-with-hum-unmatched.wav'),
       '-af', 'bandreject=f=60:t=q:w=15,bandreject=f=120:t=q:w=15',
       '-c:a', 'pcm_s16le', str(output / 'tone-filtered-unmatched.wav'))
    measurements = {}
    for key, raw, final in [
        ('a', 'tone-with-hum-unmatched.wav', 'audio-a-hum.wav'),
        ('b', 'tone-filtered-unmatched.wav', 'audio-b-notched.wav'),
        ('reference', 'tone-reference-unmatched.wav', 'audio-reference-tone.wav')]:
        measurements[key] = normalize(output / raw, output / final)
    (output / 'audio-measurements.json').write_text(json.dumps(measurements, indent=2) + '\n')
    media = ['source.mp4', 'corrected.mp4', 'too-short.mp4', 'source-audio.wav',
             'corrected-audio.wav', 'too-short-audio.wav', 'audio-a-hum.wav',
             'audio-b-notched.wav', 'audio-reference-tone.wav']
    probes = {name: probe(output / name) for name in media}
    (output / 'media-probe.json').write_text(json.dumps(probes, indent=2) + '\n')
    hashes = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in output.rglob('*') if p.is_file()}
    (output / 'SHA256.json').write_text(json.dumps(hashes, indent=2) + '\n')
    print(f'Created {output.name}: source 240 frames; corrected 168; intentional error 144.')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--exporter', required=True, type=Path)
    args = parser.parse_args()
    build(args.out, args.exporter.expanduser().resolve())


if __name__ == '__main__':
    main()
