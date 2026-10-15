#!/usr/bin/env python3
"""
Jump Cut Editor v2 - PARALLEL VERSION

Identical output to jump_cut_vad.py, but uses parallel segment encoding
for 4-6x faster processing on Apple Silicon.

Key difference: Encodes 4 segments simultaneously using ThreadPoolExecutor,
taking advantage of VideoToolbox's ability to handle multiple encodes.

See: directives/jump_cut_vad.md for full documentation.

Usage:
    # Basic silence removal (4-6x faster than original)
    python tools/jump_cut_vad_parallel.py input.mp4 output.mp4

    # With audio enhancement and color grading
    python tools/jump_cut_vad_parallel.py input.mp4 output.mp4 \
        --enhance-audio --apply-lut project/cinematic.cube

    # With "cut cut" restart detection
    python tools/jump_cut_vad_parallel.py input.mp4 output.mp4 --detect-restarts

    # Full editorial pass (matches Payton's manual FCP behavior):
    # unmarked retakes (last take wins), false starts, throat clears
    python tools/jump_cut_vad_parallel.py input.mp4 output.mp4 \
        --detect-restarts --detect-full-stop-restart --detect-retakes \
        --cut-nonspeech --enhance-audio
"""

import subprocess
import tempfile
import os
import argparse
import json
import re
import time
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional
from xml.dom import minidom

# Configurable parameters
MIN_SILENCE_DURATION = 0.5  # Minimum gap between speech to cut (seconds)
PADDING_MS = 50  # Padding around speech segments (milliseconds) - tighter cuts
MIN_SPEECH_DURATION = 0.25  # Minimum speech duration to keep (seconds)
RESTART_PHRASE = "cut cut"  # Phrase that triggers a restart/redo
RESTART_LOOKBACK = 10.0  # Max seconds of botched lead-in to remove before a 'cut cut' marker
RESTART_MAX_GAP = 0.8  # Max gap between the two 'cut' words to count as the marker (seconds)
RESTART_TAKE_GAP = 1.5  # Silence gap that marks a take boundary when trimming the botched lead-in
RESTART_MIN_KEEP = 0.20  # Drop sub-segments shorter than this after a restart cut (seconds)
FULL_STOP_RESTART_PHRASE = "full stop restart"  # Phrase that triggers a full video restart

# Filler word removal (opt-in via --remove-fillers)
# Conservative set: these tokens are never legitimate English words, so a
# transcribed standalone match is near-certain to be a filler. Deliberately
# excludes "like", "so", "well", "right" — real words that would destroy speech.
FILLER_WORDS = {"um", "uh", "uhm", "umm", "uhh", "erm", "ehm", "mm", "mmm", "hmm", "hm"}
FILLER_MIN_GAP = 0.15  # Pause (s) required on at least one side to cut a filler
FILLER_PAD = 0.05  # Padding (s) trimmed around a filler, clamped to neighbors
FILLER_MIN_KEEP = 0.20  # Drop sub-segments shorter than this after a filler cut (seconds)

# Unmarked retake detection (opt-in via --detect-retakes).
#
# NOT part of the default workflow as of 2026-07-27. Payton reviewed a batch of
# six Quick Wins edited with it on and found it had removed content that needed
# to stay, in more than one file. Teaching speech legitimately repeats sentence
# structure ("So now I'll show you how." / "So now I'm going to show you how to
# go from this image to this.") and the similarity matcher reads that as a
# duplicate take. The pipeline cannot tell a retake from a rephrase, so it no
# longer guesses. Marker-driven cuts ("cut cut", "full stop restart") only.
#
# The flag still exists for deliberate use on a recording known to be full of
# unmarked retakes. Check the report and expect to spot-check every cut.
RETAKE_SIMILARITY = 0.75  # SequenceMatcher ratio to call two sentences the same take
RETAKE_PRE_PAD = 0.05   # Padding (s) before a losing take's first word
RETAKE_POST_PAD = 0.10  # Padding (s) after a losing take's last word
RETAKE_MIN_KEEP = 0.20  # Drop sub-segments shorter than this after a retake cut (seconds)

# Non-speech vocal noise removal (opt-in via --cut-nonspeech).
# Throat clears, lip smacks, and stray noises pass Silero VAD as "speech" but
# produce zero transcribed words. A short VAD segment with no word overlap is
# near-certain noise. The duration cap protects laughter/music/intentional
# sound-only moments from being cut.
NONSPEECH_MAX_S = 1.5  # Only drop word-free segments shorter than this (seconds)

# On-screen media protection (opt-in via --protect-media).
# When Payton plays something on screen — an AI-generated video, AI music, a
# YouTube clip — that audio is music/effects/other voices, not his narration.
# Silero VAD marks the musical parts "not speech", so the silence cutter would
# shred them. Detection: sustained LOUD audio in the gaps between his speech
# (real silence is quiet; a playing clip is not). Detected spans are kept
# verbatim: no silence, restart, retake, filler, or nonspeech cuts inside.
MEDIA_RMS_WINDOW_S = 0.10    # RMS analysis window (seconds)
MEDIA_FLOOR_RATIO = 4.0      # "loud" = at least this multiple of the noise floor (+12 dB)
MEDIA_MIN_ABS_RMS = 0.0035   # ...and above ~-49 dBFS regardless of floor
MEDIA_FLOOR_CAP = 0.01       # Noise-floor estimate is clamped to this (media-heavy gaps)
MEDIA_BRIDGE_S = 1.0         # Bridge quiet dips inside a media region up to this long
MEDIA_MIN_S = 2.0            # Minimum sustained loud run to call it media
MEDIA_PAD_S = 0.25           # Keep this much extra on each side of a media span

# Parallel encoding settings
# VideoToolbox can handle 3+ simultaneous 4K encodes, 4 workers is safe
PARALLEL_WORKERS = 4

# Micro-fade at each cut boundary to prevent audio pops/clicks at jump cuts.
# Duration-neutral (afade never changes segment length), so A/V sync is safe.
MICRO_FADE_S = 0.015

# Smart rendering settings
SMART_RENDER_THRESHOLD = 5.0  # Only use smart render for segments > 5 seconds
SMART_RENDER_EDGE = 1.0  # Re-encode 1 second at each edge

# Audio enhancement settings
AUDIO_FILTERS = {
    "highpass": "highpass=f=80",  # Remove rumble below 80Hz
    "lowpass": "lowpass=f=12000",  # Remove harsh highs above 12kHz
    "presence": "equalizer=f=3000:t=q:w=1.5:g=2",  # Slight boost at 3kHz for clarity
    "warmth": "equalizer=f=200:t=q:w=1:g=-1",  # Slight cut at 200Hz to reduce muddiness
    "compression": "acompressor=threshold=-20dB:ratio=3:attack=5:release=50",  # Gentle compression
    "loudnorm": "loudnorm=I=-16:TP=-1.5:LRA=11",  # measurement pass ONLY, never the output stage
}

# Loudness targets. The output stage is a constant `volume` gain plus a true-peak
# limiter, never loudnorm — see build_constant_gain_chain for why.
TARGET_I_LUFS = -16.0          # Speech-led comparison target; delivery brief may differ
TARGET_TP_DB = -1.5            # True-peak ceiling
TARGET_TP_LINEAR = 10 ** (TARGET_TP_DB / 20)   # alimiter wants linear amplitude
LOUDNESS_TOLERANCE_LU = 0.2    # Re-trim if the first attempt misses by more than this
MAX_TRIM_DB = 4.0              # Sanity clamp on the corrective trim

# Supported LUT formats
SUPPORTED_LUT_FORMATS = [".cube", ".3dl", ".dat", ".m3d", ".csp"]

# Video encoding settings
HARDWARE_ENCODER = "h264_videotoolbox"
SOFTWARE_ENCODER = "libx264"
# Constant-quality mode (-q:v 0-100) lets VideoToolbox scale bitrate to content
# and resolution — a fixed 10M starved 4K footage and wasted bits on 1080p.
# 65 is visually transparent for talking-head content on Apple Silicon.
HARDWARE_QUALITY = "65"
HARDWARE_BITRATE = "10M"  # Fallback only, for VideoToolbox builds without -q:v support
SOFTWARE_CRF = "18"  # CRF 18 for software encoding (high quality)

# mlx-whisper model repos (Apple GPU transcription, ~6x faster than CPU whisper).
# Keyed by the openai-whisper model names used by --whisper-model.
MLX_WHISPER_REPOS = {
    "tiny": "mlx-community/whisper-tiny-mlx",
    "base": "mlx-community/whisper-base-mlx",
    "small": "mlx-community/whisper-small-mlx",
    "medium": "mlx-community/whisper-medium-mlx",
    "large-v3": "mlx-community/whisper-large-v3-mlx",
    "turbo": "mlx-community/whisper-large-v3-turbo",
    "large-v3-turbo": "mlx-community/whisper-large-v3-turbo",
}


def check_hardware_encoder_available() -> bool:
    """Check if h264_videotoolbox hardware encoder is available."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-hide_banner", "-encoders"],
            capture_output=True, text=True, timeout=5
        )
        return "h264_videotoolbox" in result.stdout
    except Exception:
        return False


def check_quality_mode_available() -> bool:
    """Probe whether h264_videotoolbox accepts constant-quality mode (-q:v).

    Runs a 0.1s test encode once per process. Older ffmpeg/VideoToolbox builds
    reject -q:v; falling back to fixed bitrate keeps the pipeline working.
    """
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc2=size=320x240:rate=30:duration=0.1",
             "-c:v", HARDWARE_ENCODER, "-q:v", HARDWARE_QUALITY, "-f", "null", "-"],
            capture_output=True, timeout=15
        )
        return result.returncode == 0
    except Exception:
        return False


def get_video_encoder_args(use_hardware: bool = True) -> list[str]:
    """Get FFmpeg video encoder arguments."""
    if use_hardware and check_hardware_encoder_available():
        if check_quality_mode_available():
            return ["-c:v", HARDWARE_ENCODER, "-q:v", HARDWARE_QUALITY]
        return ["-c:v", HARDWARE_ENCODER, "-b:v", HARDWARE_BITRATE]
    else:
        return ["-c:v", SOFTWARE_ENCODER, "-preset", "fast", "-crf", SOFTWARE_CRF]


# Cache the encoder check result (only check once per run)
_hardware_encoder_available = None

# Cache keyframe data per video (only probe once per video)
_keyframe_cache: dict[str, list[float]] = {}


def get_keyframes(input_path: str) -> list[float]:
    """
    Get all keyframe timestamps from a video using ffprobe.
    Results are cached per video path.
    """
    if input_path in _keyframe_cache:
        return _keyframe_cache[input_path]

    import json
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "packet=pts_time,flags",
        "-of", "json",
        input_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    keyframes = []
    try:
        data = json.loads(result.stdout)
        for packet in data.get("packets", []):
            # Keyframes have 'K' in flags
            if "K" in packet.get("flags", ""):
                pts = packet.get("pts_time")
                if pts is not None:
                    keyframes.append(float(pts))
    except (json.JSONDecodeError, KeyError):
        pass

    keyframes.sort()
    _keyframe_cache[input_path] = keyframes
    return keyframes


def find_keyframe_at_or_after(keyframes: list[float], target: float) -> Optional[float]:
    """Find the first keyframe at or after the target time."""
    for kf in keyframes:
        if kf >= target - 0.001:  # Small tolerance for float comparison
            return kf
    return None


def find_keyframe_at_or_before(keyframes: list[float], target: float) -> Optional[float]:
    """Find the last keyframe at or before the target time."""
    result = None
    for kf in keyframes:
        if kf <= target + 0.001:  # Small tolerance
            result = kf
        else:
            break
    return result


def get_cached_encoder_args() -> list[str]:
    """Get encoder args with cached hardware availability check."""
    global _hardware_encoder_available
    if _hardware_encoder_available is None:
        _hardware_encoder_available = check_hardware_encoder_available()
        if _hardware_encoder_available:
            print(f"🚀 Hardware encoding enabled (h264_videotoolbox)")
        else:
            print(f"💻 Using software encoding (libx264)")
    return get_video_encoder_args(_hardware_encoder_available)


def extract_audio(input_path: str, output_path: str, sample_rate: int = 16000):
    """Extract audio from video as WAV for VAD processing."""
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vn", "-ar", str(sample_rate), "-ac", "1",
        "-acodec", "pcm_s16le",
        "-loglevel", "error", output_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def transcribe_with_whisper(audio_path: str, model_name: str = "base", *,
                            initial_prompt: Optional[str] = None) -> list[dict]:
    """Transcribe audio to word-level timestamps.

    Prefers mlx-whisper (Apple GPU, ~6x faster than CPU openai-whisper, identical
    word timestamps). Falls back to openai-whisper if mlx-whisper is missing or
    fails for any reason, so the pipeline never breaks on a backend problem.

    Language is pinned to English. Whisper auto-detects from the first 30s of
    audio, and a recording that opens with dead air (Payton walking back to the
    desk) gets detected as some other language — which returns a hallucinated
    junk transcript instead of an error. That silently poisons every downstream
    word-level feature. Never let the model guess.

    condition_on_previous_text is off for the same reason: it is what turns one
    bad window into a page of repeated garbage tokens.

    Leave ordinary transcription unprimed. Marker hints can hallucinate edit
    commands in short dialogue clips; callers must request any hint explicitly.
    """
    result = None

    try:
        import mlx_whisper
        repo = MLX_WHISPER_REPOS.get(model_name, f"mlx-community/whisper-{model_name}-mlx")
        print(f"🗣️  Transcribing with mlx-whisper ({model_name}, Apple GPU, language=en)...")
        result = mlx_whisper.transcribe(
            audio_path,
            path_or_hf_repo=repo,
            word_timestamps=True,
            initial_prompt=initial_prompt,
            language="en",
            condition_on_previous_text=False,
        )
    except Exception as e:
        print(f"   mlx-whisper unavailable ({type(e).__name__}: {e}) — falling back to openai-whisper (CPU)")
        result = None

    if result is None:
        import whisper
        print(f"🗣️  Transcribing with Whisper ({model_name}, CPU, language=en)...")
        model = whisper.load_model(model_name)
        result = model.transcribe(
            audio_path,
            word_timestamps=True,
            initial_prompt=initial_prompt,
            language="en",
            condition_on_previous_text=False,
        )

    words = []
    for segment in result.get("segments", []):
        for word_info in segment.get("words", []):
            words.append({
                "word": word_info["word"].strip().lower(),
                "start": float(word_info["start"]),
                "end": float(word_info["end"]),
                # Kept for take scoring in retake detection (transcript_analyzer)
                "confidence": float(word_info.get("probability", word_info.get("score", 0.8))),
            })

    print(f"   Transcribed {len(words)} words")
    return words


def transcript_looks_broken(words: list[dict]) -> str | None:
    """Return a reason string if the transcript is degenerate, else None.

    A hallucinating Whisper pass does not raise — it returns confident garbage
    (non-Latin filler glyphs, or one token repeated hundreds of times). Cutting
    video from that transcript deletes good footage, which is exactly what
    happened to QW1 on 2026-07-27. Detect it and refuse to cut instead.
    """
    if not words:
        return None

    tokens = [w["word"] for w in words if w["word"]]
    if not tokens:
        return "transcript contains no usable words"

    # 1. Junk glyphs: tokens with no ASCII letter at all (Georgian/IPA filler)
    junk = sum(1 for t in tokens if not any(c.isascii() and c.isalpha() for c in t))
    if junk / len(tokens) > 0.20:
        return f"{junk}/{len(tokens)} tokens contain no ASCII letters (hallucinated glyphs)"

    # 2. Degenerate repetition: one token dominating the whole transcript
    from collections import Counter
    top_token, top_count = Counter(tokens).most_common(1)[0]
    if len(tokens) >= 50 and top_count / len(tokens) > 0.25:
        return f"token {top_token!r} is {top_count}/{len(tokens)} of the transcript (repetition loop)"

    # 3. Long identical run — a stuck decoder emitting the same word back to back
    run = best_run = 1
    for prev, cur in zip(tokens, tokens[1:]):
        run = run + 1 if cur == prev else 1
        best_run = max(best_run, run)
    if best_run >= 25:
        return f"{best_run} identical tokens in a row (stuck decoder)"

    return None


def _is_cut_word(word: str) -> bool:
    """Check if a word is 'cut' or a common Whisper mishearing of 'cut'.

    Deliberately EXCLUDES common standalone English words (caught, cat, cot,
    gut) that occur in normal speech — including them caused false-positive
    'cut cut' matches mid-sentence that destroyed good footage.
    """
    clean = ''.join(c for c in word.strip().lower() if c.isalnum())
    # Excludes common standalone words (caught/cat/cot/gut AND cup/cud) — all of
    # them occur in normal speech and would re-introduce false-positive matches.
    return clean in {"cut", "cutt", "kut", "khut", "kud"}


def find_restart_phrases(words: list[dict], phrase: str = "cut cut") -> list[tuple[float, float]]:
    """Find 'cut cut' restart markers in the transcript.

    Returns a list of (start, end) spans for each marker — the caller needs the
    start so it can remove the spoken marker itself, not just everything before
    its end.

    Tightened for precision: the two 'cut'-like words must be (a) tightly
    adjacent (a deliberate quick repetition, not two distant uses of "cut") and
    (b) either very tight OR preceded by a short pause — the natural break at the
    end of a botched take — so the matcher does not fire on the word "cut" used
    in normal continuous speech.
    """
    spans: list[tuple[float, float]] = []

    for i in range(len(words) - 1):
        word1 = words[i]["word"].strip().lower()
        word2 = words[i + 1]["word"].strip().lower()

        if not (_is_cut_word(word1) and _is_cut_word(word2)):
            continue

        gap = words[i + 1]["start"] - words[i]["end"]
        if gap < 0 or gap > RESTART_MAX_GAP:
            continue

        # A genuine marker is either spoken as one fast "cut-cut" (very tight)
        # or set off by a brief pause from the preceding (botched) speech.
        # The first word of the recording has no predecessor, so treat its
        # gap_before as effectively infinite (a sentinel) — it qualifies.
        gap_before = (words[i]["start"] - words[i - 1]["end"]) if i > 0 else float("inf")
        if not (gap < 0.30 or gap_before >= 0.15):
            continue

        start, end = words[i]["start"], words[i + 1]["end"]
        # Avoid duplicate detections within 2s of each other
        if spans and (end - spans[-1][1]) <= 2.0:
            continue
        spans.append((start, end))
        actual = f"{words[i]['word'].strip()} {words[i+1]['word'].strip()}"
        print(f"   Found '{actual}' at {end:.2f}s")

    return spans


def apply_restart_cuts(speech_segments: list[tuple[float, float]],
                       restart_spans,
                       lookback: float = RESTART_LOOKBACK) -> list[tuple[float, float]]:
    """Remove botched takes marked by 'cut cut', keeping the redo that follows.

    Recording convention: ``[botched take] "cut cut" [redo take]``. For each
    marker we build a kill window ``[botched_start, phrase_end]`` and subtract it
    from the speech segments. Two properties make this safe where the old
    whole-segment deletion was not:

      * Everything AFTER the marker (the redo) is always preserved. If the marker
        fell inside a VAD segment that also holds the redo, the segment is SPLIT
        at the marker rather than deleted — so good footage merged into the same
        segment as the marker is never lost.
      * The botched lead-in is only removed back to the previous real pause
        (a silence gap larger than ``RESTART_TAKE_GAP``) and never further than
        ``lookback`` seconds. A long clean take sitting before the marker — but
        separated from it by a pause — is left intact.

    Accepts either (start, end) spans (preferred) or bare end timestamps for
    backward compatibility.
    """
    if not restart_spans:
        return speech_segments

    # Normalize input to (start, end) spans.
    spans: list[tuple[float, float]] = []
    for item in restart_spans:
        if isinstance(item, (tuple, list)):
            spans.append((float(item[0]), float(item[1])))
        else:
            spans.append((float(item), float(item)))
    spans.sort(key=lambda s: s[1])

    segs = sorted(speech_segments)

    # 1) Build a kill window per marker: [botched_start, phrase_end].
    kills: list[tuple[float, float]] = []
    for ph_start, ph_end in spans:
        floor = ph_end - lookback
        kill_start = ph_start
        # Right edge of the last segment we folded into the botched run; used to
        # measure the silence gap to the next-earlier segment.
        prev_run_left = ph_start
        for s, e in reversed(segs):
            if s > ph_end:
                continue  # segment is entirely after the marker — not the lead-in
            seg_right = min(e, ph_end)  # cap at the marker (the botched part only)
            if seg_right <= floor:
                break  # beyond the lookback horizon
            if (prev_run_left - seg_right) > RESTART_TAKE_GAP:
                break  # a real pause = take boundary; earlier speech is a separate take
            kill_start = max(s, floor)
            prev_run_left = s
        kills.append((kill_start, ph_end))

    # 2) Merge kill windows separated by less than a take boundary — clustered
    # retakes ("cut cut … cut cut") collapse so only the final redo survives.
    # (Reuses RESTART_TAKE_GAP: the same silence span that bounds a single take.)
    kills.sort()
    merged: list[tuple[float, float]] = []
    for ks, ke in kills:
        if merged and ks <= merged[-1][1] + RESTART_TAKE_GAP:
            merged[-1] = (merged[-1][0], max(merged[-1][1], ke))
        else:
            merged.append((ks, ke))

    # 3) Subtract kill windows from the speech segments, splitting as needed.
    result: list[tuple[float, float]] = []
    for s, e in segs:
        pieces = [(s, e)]
        for ks, ke in merged:
            nxt = []
            for cs, ce in pieces:
                if ke <= cs or ks >= ce:
                    nxt.append((cs, ce))  # no overlap
                    continue
                if cs < ks:
                    nxt.append((cs, ks))  # keep part before the kill window
                if ce > ke:
                    nxt.append((ke, ce))  # keep the redo after the kill window
            pieces = nxt
        for cs, ce in pieces:
            if ce - cs >= RESTART_MIN_KEEP:
                result.append((cs, ce))

    # Report exact removed footage (kill windows + sub-RESTART_MIN_KEEP remnants).
    removed_total = sum(e - s for s, e in segs) - sum(ce - cs for cs, ce in result)
    for ks, ke in merged:
        print(f"   Cut botched take {ks:.2f}s - {ke:.2f}s (kept everything after the marker)")
    print(f"   Removed ~{removed_total:.1f}s across {len(merged)} restart marker(s)")
    return result


def find_filler_words(words: list[dict]) -> list[tuple[float, float]]:
    """Find standalone filler words ("um", "uh", ...) safe to cut.

    Conservative by design:
      * Only tokens in FILLER_WORDS — sounds that are never legitimate English
        words, so a transcribed match is near-certain to be a filler.
      * Requires a pause of at least FILLER_MIN_GAP on at least one side, so a
        filler glued tightly into fluent speech is left alone (cutting it would
        sound abrupt and risks clipping neighboring words).

    Returns kill windows (start, end), padded by FILLER_PAD but clamped so they
    never overlap the neighboring words.
    """
    windows: list[tuple[float, float]] = []

    for i, w in enumerate(words):
        clean = ''.join(c for c in w["word"].strip().lower() if c.isalnum())
        if clean not in FILLER_WORDS:
            continue

        prev_end = words[i - 1]["end"] if i > 0 else 0.0
        next_start = words[i + 1]["start"] if i + 1 < len(words) else float("inf")
        gap_before = w["start"] - prev_end
        gap_after = next_start - w["end"]

        if gap_before < FILLER_MIN_GAP and gap_after < FILLER_MIN_GAP:
            continue  # embedded in fluent speech — too risky to cut

        # Pad the cut slightly, but never into the neighboring words.
        kill_start = max(w["start"] - FILLER_PAD, prev_end)
        kill_end = min(w["end"] + FILLER_PAD, next_start)
        windows.append((kill_start, kill_end))
        print(f"   Found filler '{clean}' at {w['start']:.2f}s")

    return windows


def apply_filler_cuts(speech_segments: list[tuple[float, float]],
                      filler_windows: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Subtract filler kill windows from speech segments, splitting as needed.

    Same subtract-and-split approach as apply_restart_cuts: speech around a
    filler is always preserved; only the filler itself is removed.
    """
    if not filler_windows:
        return speech_segments

    result: list[tuple[float, float]] = []
    for s, e in sorted(speech_segments):
        pieces = [(s, e)]
        for ks, ke in filler_windows:
            nxt = []
            for cs, ce in pieces:
                if ke <= cs or ks >= ce:
                    nxt.append((cs, ce))
                    continue
                if cs < ks:
                    nxt.append((cs, ks))
                if ce > ke:
                    nxt.append((ke, ce))
            pieces = nxt
        for cs, ce in pieces:
            if ce - cs >= FILLER_MIN_KEEP:
                result.append((cs, ce))

    removed = sum(e - s for s, e in speech_segments) - sum(e - s for s, e in result)
    print(f"   Removed {len(filler_windows)} filler(s), ~{removed:.1f}s total")
    return result


def apply_kill_windows(speech_segments: list[tuple[float, float]],
                       kill_windows: list[tuple[float, float]],
                       min_keep: float,
                       label: str) -> list[tuple[float, float]]:
    """Subtract kill windows from speech segments, splitting as needed.

    Generic version of the subtract-and-split used by restart/filler cuts:
    speech around a window is always preserved; only the window is removed.
    """
    if not kill_windows:
        return speech_segments

    result: list[tuple[float, float]] = []
    for s, e in sorted(speech_segments):
        pieces = [(s, e)]
        for ks, ke in kill_windows:
            nxt = []
            for cs, ce in pieces:
                if ke <= cs or ks >= ce:
                    nxt.append((cs, ce))
                    continue
                if cs < ks:
                    nxt.append((cs, ks))
                if ce > ke:
                    nxt.append((ke, ce))
            pieces = nxt
        for cs, ce in pieces:
            if ce - cs >= min_keep:
                result.append((cs, ce))

    removed = sum(e - s for s, e in speech_segments) - sum(e - s for s, e in result)
    print(f"   Removed {len(kill_windows)} {label} window(s), ~{removed:.1f}s total")
    return result


def find_retake_windows(words: list[dict],
                        similarity: float = RETAKE_SIMILARITY) -> list[tuple[float, float]]:
    """Detect unmarked retakes and false starts; return kill windows for losers.

    Two patterns from Payton's manual FCP pass (2026-07 demonstration):
      * Repeated take — the same line said 2+ times consecutively with no
        "cut cut" marker. The LAST repetition wins unless an earlier take
        scores clearly better (>0.15 margin in take scoring).
      * False start — a short fragment abandoned and restarted ("So what you
        — So what you really want to pay attention to is...").

    Detection, grouping, and scoring live in transcript_analyzer.py (shared
    with intelligent_edit.py). This wrapper adapts word formats, merges the
    resulting windows, and degrades gracefully if the analyzer is missing.
    """
    try:
        import sys as _sys
        _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from transcript_analyzer import (
            detect_repeated_phrases,
            group_and_select_retakes,
            detect_false_starts,
        )
    except Exception as e:
        print(f"   ⚠️ transcript_analyzer unavailable ({type(e).__name__}: {e}) — skipping retake detection")
        return []

    # Adapt this pipeline's word format to the analyzer's.
    awords = [
        {"text": w["word"], "start": w["start"], "end": w["end"],
         "confidence": w.get("confidence", 0.8)}
        for w in words
    ]

    windows: list[tuple[float, float]] = []

    repeated = detect_repeated_phrases(awords, similarity_threshold=similarity)
    retake_cuts = group_and_select_retakes(repeated, awords)
    for cut in retake_cuts:
        windows.append((max(0.0, cut["start"] - RETAKE_PRE_PAD), cut["end"] + RETAKE_POST_PAD))
        print(f"   Retake: cutting {cut['start']:.2f}s - {cut['end']:.2f}s ({cut.get('reason', 'earlier take')})")

    for fs in detect_false_starts(awords):
        windows.append((max(0.0, fs["start"] - RETAKE_PRE_PAD), fs["end"] + RETAKE_POST_PAD))
        print(f"   False start: cutting {fs['start']:.2f}s - {fs['end']:.2f}s ('{fs['text'][:40]}...')")

    # Merge overlapping windows (a false start inside a losing take, etc.)
    windows.sort()
    merged: list[tuple[float, float]] = []
    for ws, we in windows:
        if merged and ws <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], we))
        else:
            merged.append((ws, we))

    return merged


def drop_nonspeech_segments(speech_segments: list[tuple[float, float]],
                            words: list[dict],
                            max_duration: float = NONSPEECH_MAX_S
                            ) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """Drop short VAD segments containing no transcribed words.

    Silero VAD passes throat clears, lip smacks, and stray vocal noises as
    speech, but Whisper transcribes no words in them. Any segment with zero
    word overlap and duration <= max_duration is cut. Longer word-free
    segments are kept (could be intentional sound, laughter, demo audio).

    Returns (kept_segments, dropped_segments).
    """
    kept: list[tuple[float, float]] = []
    dropped: list[tuple[float, float]] = []
    for s, e in speech_segments:
        has_word = any(w["start"] < e and w["end"] > s for w in words)
        if not has_word and (e - s) <= max_duration:
            dropped.append((s, e))
            print(f"   Non-speech noise: cutting {s:.2f}s - {e:.2f}s ({e - s:.2f}s, no words transcribed)")
        else:
            kept.append((s, e))
    return kept, dropped


def find_media_regions(audio_path: str,
                       speech_segments: list[tuple[float, float]],
                       duration: float) -> list[tuple[float, float]]:
    """Find spans of loud NON-speech audio: music or a played clip's soundtrack.

    Works on the same 16 kHz mono WAV used by VAD. RMS is measured in short
    windows; windows outside every speech segment that sit well above the
    recording's noise floor are coalesced (bridging brief dips) into media
    regions. Only sustained runs count — a chair squeak is not a song.
    """
    import wave
    import array

    with wave.open(audio_path, "rb") as wf:
        sr = wf.getframerate()
        raw = wf.readframes(wf.getnframes())
    samples = array.array("h", raw)

    win = max(1, int(MEDIA_RMS_WINDOW_S * sr))
    n_win = len(samples) // win
    if n_win == 0:
        return []

    rms = []
    for i in range(n_win):
        chunk = samples[i * win:(i + 1) * win]
        acc = 0
        for v in chunk:
            acc += v * v
        rms.append((acc / len(chunk)) ** 0.5 / 32768.0)

    def in_speech(t: float) -> bool:
        return any(s <= t <= e for s, e in speech_segments)

    win_s = win / sr
    gap_rms = [r for i, r in enumerate(rms)
               if not in_speech((i + 0.5) * win_s)]
    if not gap_rms:
        return []

    # Noise floor: a low percentile of the non-speech windows, clamped so a
    # media-heavy recording (little true silence) can't inflate it.
    floor = min(sorted(gap_rms)[len(gap_rms) // 5], MEDIA_FLOOR_CAP)
    threshold = max(floor * MEDIA_FLOOR_RATIO, MEDIA_MIN_ABS_RMS)

    # Coalesce loud non-speech windows, bridging brief quiet dips
    regions: list[tuple[float, float]] = []
    run_start = None
    last_loud_end = None
    for i, r in enumerate(rms):
        t0, t1 = i * win_s, (i + 1) * win_s
        loud = r >= threshold and not in_speech((t0 + t1) / 2)
        if loud:
            if run_start is None:
                run_start = t0
            last_loud_end = t1
        elif run_start is not None and t1 - last_loud_end > MEDIA_BRIDGE_S:
            regions.append((run_start, last_loud_end))
            run_start = None
    if run_start is not None:
        regions.append((run_start, last_loud_end))

    # Keep sustained runs only, pad, clamp, merge
    padded = [(max(0.0, s - MEDIA_PAD_S), min(duration, e + MEDIA_PAD_S))
              for s, e in regions if e - s >= MEDIA_MIN_S]
    merged: list[tuple[float, float]] = []
    for s, e in padded:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def apply_media_protection(speech_segments: list[tuple[float, float]],
                           media_regions: list[tuple[float, float]],
                           duration: float) -> list[tuple[float, float]]:
    """Union protected media spans into the kept timeline, verbatim."""
    if not media_regions:
        return speech_segments
    clamped = [(max(0.0, s), min(duration, e)) for s, e in media_regions]
    merged = sorted(speech_segments + clamped)
    out = [merged[0]]
    for s, e in merged[1:]:
        ps, pe = out[-1]
        if s <= pe + 1e-6:
            out[-1] = (ps, max(pe, e))
        else:
            out.append((s, e))
    return out


def filter_windows_outside_media(windows: list[tuple[float, float]],
                                 media_regions: list[tuple[float, float]],
                                 label: str) -> list[tuple[float, float]]:
    """Drop cut windows that touch a protected media span.

    A repeated line, an "um", or even a spoken "cut cut" heard INSIDE a
    played clip belongs to the clip, not to Payton — cutting there would
    slice the media he explicitly wants kept whole.
    """
    if not media_regions or not windows:
        return windows
    kept = []
    for w in windows:
        ws, we = w[0], w[1]
        if any(ws < me and we > ms for ms, me in media_regions):
            print(f"   🎼 Skipping {label} cut at {ws:.2f}s - {we:.2f}s (inside protected media)")
        else:
            kept.append(w)
    return kept


def _is_full_stop_word(word: str) -> bool:
    """Check if a word is 'full' or a common Whisper mishearing."""
    clean = ''.join(c for c in word.strip().lower() if c.isalnum())
    return clean in {"full", "ful", "fol", "fool", "foul", "fll", "fall"}


def _is_stop_word(word: str) -> bool:
    """Check if a word is 'stop' or a common Whisper mishearing."""
    clean = ''.join(c for c in word.strip().lower() if c.isalnum())
    return clean in {"stop", "stob", "stopp", "sob", "stock", "stoop", "stup", "stub", "shop"}


def _is_restart_word(word: str) -> bool:
    """Check if a word is 'restart' or a common Whisper mishearing."""
    clean = ''.join(c for c in word.strip().lower() if c.isalnum())
    return clean in {
        "restart", "restartt", "reestart",
        # Common Whisper mishearings (kept conservative to avoid false positives)
        "reset", "restore", "resort",
        "reasart", "reastart",
        "restard", "restarg", "restort", "resart",
    }


def find_full_stop_restarts(words: list[dict]) -> list[float]:
    """Find occurrences of 'full stop restart' in the transcript.

    Uses fuzzy matching to catch common Whisper mishearings.
    Returns list of phrase-end timestamps for each occurrence.
    """
    restart_times = []

    # Sliding window of 3 consecutive words
    for i in range(len(words) - 2):
        w1 = words[i]
        w2 = words[i + 1]
        w3 = words[i + 2]

        if _is_full_stop_word(w1["word"]) and _is_stop_word(w2["word"]) and _is_restart_word(w3["word"]):
            # Ensure all three words are close together (within 3s total span)
            span = w3["end"] - w1["start"]
            if span < 3.0:
                phrase_end = w3["end"]
                # Avoid duplicate detections within 3s
                if not restart_times or (phrase_end - restart_times[-1]) > 3.0:
                    restart_times.append(phrase_end)
                    actual = f"{w1['word'].strip()} {w2['word'].strip()} {w3['word'].strip()}"
                    print(f"   Found '{actual}' at {phrase_end:.2f}s")

    return restart_times


def apply_full_stop_restart(speech_segments: list[tuple[float, float]],
                            restart_times: list[float]) -> list[tuple[float, float]]:
    """Discard source time through the last recording-restart phrase.

    Restart times are phrase-end timestamps. A VAD segment can contain both
    the marker and the clean take, so trim that segment instead of dropping it.
    """
    if not restart_times:
        return speech_segments

    # Only the last occurrence matters
    last_restart = max(restart_times)
    print(f"   Using last 'full stop restart' at {last_restart:.2f}s — discarding everything before")

    kept = [(max(s, last_restart), e) for s, e in speech_segments
            if e > last_restart]
    removed_count = len(speech_segments) - len(kept)
    print(f"   Removed {removed_count} segment(s), keeping {len(kept)} segment(s)")
    return kept


def get_speech_timestamps_silero(audio_path: str, min_speech_duration: float = 0.25, min_silence_duration: float = 0.5):
    """Use Silero VAD to detect speech segments."""
    import torch

    model, utils = torch.hub.load(
        repo_or_dir='snakers4/silero-vad',
        model='silero_vad',
        force_reload=False,
        trust_repo=True
    )

    (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

    SAMPLE_RATE = 16000
    wav = read_audio(audio_path, sampling_rate=SAMPLE_RATE)

    speech_timestamps = get_speech_timestamps(
        wav,
        model,
        sampling_rate=SAMPLE_RATE,
        threshold=0.5,
        min_speech_duration_ms=int(min_speech_duration * 1000),
        min_silence_duration_ms=int(min_silence_duration * 1000),
        speech_pad_ms=100,
    )

    segments = []
    for ts in speech_timestamps:
        start_sec = ts['start'] / SAMPLE_RATE
        end_sec = ts['end'] / SAMPLE_RATE
        segments.append((start_sec, end_sec))

    return segments


def merge_close_segments(segments: list[tuple[float, float]], max_gap: float) -> list[tuple[float, float]]:
    """Merge segments that are very close together."""
    if not segments:
        return []

    merged = [segments[0]]
    for start, end in segments[1:]:
        prev_start, prev_end = merged[-1]

        if start - prev_end <= max_gap:
            merged[-1] = (prev_start, end)
        else:
            merged.append((start, end))

    return merged


def add_padding(segments: list[tuple[float, float]], padding_s: float, duration: float) -> list[tuple[float, float]]:
    """Add padding around segments and merge any overlaps."""
    if not segments:
        return []

    padded = []
    for start, end in segments:
        new_start = max(0, start - padding_s)
        new_end = min(duration, end + padding_s)
        padded.append((new_start, new_end))

    merged = [padded[0]]
    for start, end in padded[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))

    return merged


def build_audio_filter_chain(enhance: bool = False) -> str:
    """Build FFmpeg audio filter chain for voice enhancement."""
    if not enhance:
        return ""

    filters = [
        AUDIO_FILTERS["highpass"],
        AUDIO_FILTERS["lowpass"],
        AUDIO_FILTERS["warmth"],
        AUDIO_FILTERS["presence"],
        AUDIO_FILTERS["compression"],
        AUDIO_FILTERS["loudnorm"],
    ]
    return ",".join(filters)


def build_pre_loudnorm_chain() -> str:
    """Enhancement chain up to (but not including) loudnorm."""
    return ",".join([
        AUDIO_FILTERS["highpass"],
        AUDIO_FILTERS["lowpass"],
        AUDIO_FILTERS["warmth"],
        AUDIO_FILTERS["presence"],
        AUDIO_FILTERS["compression"],
    ])


def measure_loudness(input_path: str, pre_filter: str) -> Optional[dict]:
    """First loudnorm pass: measure loudness through the same pre-loudnorm chain.

    Returns the measured stats dict, or None if measurement failed (caller
    falls back to single-pass dynamic loudnorm — the old behavior).
    """
    filt = (pre_filter + "," if pre_filter else "") + AUDIO_FILTERS["loudnorm"] + ":print_format=json"
    cmd = [
        "ffmpeg", "-hide_banner", "-nostats", "-i", input_path,
        "-vn", "-af", filt, "-f", "null", "-"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # loudnorm prints its JSON block to stderr after a "[Parsed_loudnorm..." tag,
    # followed by more log lines — locate the block and raw_decode just the JSON.
    stderr = result.stderr or ""
    marker = stderr.rfind("[Parsed_loudnorm")
    start = stderr.find("{", marker if marker != -1 else 0)
    if start == -1:
        return None
    try:
        stats, _ = json.JSONDecoder().raw_decode(stderr[start:])
        required = ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")
        if all(k in stats for k in required):
            return stats
    except json.JSONDecodeError:
        pass
    return None


def build_two_pass_loudnorm(stats: dict) -> str:
    """DEPRECATED second-pass loudnorm (see build_constant_gain_chain).

    Kept only so an old call site fails loudly rather than silently ramping.
    `linear=true` is a REQUEST, not a guarantee: when the gain needed to reach
    the target would push true peak past TP, ffmpeg silently falls back to
    dynamic mode, which rides its gain upward over the first ~30-60s. That is
    the "intro fades up" artifact Payton reported 2026-07-29.
    """
    raise RuntimeError(
        "build_two_pass_loudnorm is deprecated: it silently falls back to "
        "dynamic loudnorm and ramps the intro. Use build_constant_gain_chain()."
    )


def build_constant_gain_chain(stats: dict, trim_db: float = 0.0) -> str:
    """Constant gain to the loudness target, plus a true-peak limiter.

    Replaces two-pass loudnorm (Payton, 2026-07-29: every edit faded up over the
    first 30-60 seconds). Root cause: reaching -16 LUFS on his quiet source
    (~-34 LUFS, peaks ~-15 dBTP) needs ~+18 dB, which would put true peak at
    ~+3.5 dBTP. With a -1.5 ceiling, loudnorm CANNOT do that with one constant
    gain, so `linear=true` is ignored and it runs dynamic, ramping the gain in.

    A fixed `volume` gain cannot ramp by construction. The limiter then holds the
    peaks, acting only on transients in milliseconds rather than riding the whole
    programme level. `level=disabled` stops alimiter renormalising back to 0 dB;
    `latency=true` compensates its lookahead so A/V sync is untouched.
    """
    gain_db = TARGET_I_LUFS - float(stats["input_i"]) + trim_db
    return (
        f"volume={gain_db:.2f}dB,"
        f"alimiter=limit={TARGET_TP_LINEAR:.4f}:attack=5:release=50"
        f":level=disabled:latency=true"
    )


def measure_integrated(input_path: str, filter_chain: str) -> Optional[float]:
    """Integrated LUFS of input_path after filter_chain. None if unmeasurable."""
    cmd = [
        "ffmpeg", "-hide_banner", "-nostats", "-i", input_path, "-vn",
        "-af", (filter_chain + "," if filter_chain else "") + "ebur128",
        "-f", "null", "-",
    ]
    stderr = subprocess.run(cmd, capture_output=True, text=True).stderr or ""
    m = re.findall(r"I:\s*(-?\d+\.?\d*)\s*LUFS", stderr)
    return float(m[-1]) if m else None


def build_video_filter_chain(lut_path: str = None) -> str:
    """Build FFmpeg video filter chain for color grading."""
    filters = []

    if lut_path:
        filters.append(f"lut3d='{lut_path}':interp=trilinear")

    return ",".join(filters) if filters else ""


def encode_single_segment(args: tuple) -> tuple[int, str]:
    """
    Encode a single segment. Used by ThreadPoolExecutor.

    Args: tuple of (index, input_path, start, end, output_path, encoder_args, audio_filter, video_filter, smart_render, keyframes)
    Returns: tuple of (index, output_path) for ordering
    """
    idx, input_path, start, end, seg_path, encoder_args, audio_filter, video_filter, smart_render, keyframes = args

    duration = end - start

    # Smart rendering: only re-encode edges for long segments
    if smart_render and duration > SMART_RENDER_THRESHOLD and not video_filter:
        return encode_segment_smart(idx, input_path, start, end, seg_path, encoder_args, audio_filter, keyframes)

    # Full re-encode for short segments or when filters are needed
    # Use -ss BEFORE -i for fast seeking, then use -accurate_seek for precision
    # This maintains perfect A/V sync
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", input_path,
        "-t", str(duration),  # Duration from start point
    ]

    if video_filter:
        cmd.extend(["-vf", video_filter])

    cmd.extend(encoder_args)

    # Micro-fade the segment edges so concatenated jump cuts never pop/click.
    if MICRO_FADE_S > 0 and duration > MICRO_FADE_S * 4:
        fade = (f"afade=t=in:st=0:d={MICRO_FADE_S},"
                f"afade=t=out:st={max(0.0, duration - MICRO_FADE_S):.4f}:d={MICRO_FADE_S}")
        audio_filter = f"{audio_filter},{fade}" if audio_filter else fade

    if audio_filter:
        cmd.extend(["-af", audio_filter, "-c:a", "aac", "-b:a", "192k"])
    else:
        cmd.extend(["-c:a", "aac", "-b:a", "192k"])

    # Lock audio sample rate to 48kHz (source rate) and reset timestamps
    cmd.extend(["-ar", "48000", "-avoid_negative_ts", "make_zero",
                "-muxdelay", "0", "-muxpreload", "0",
                "-loglevel", "error", seg_path])
    subprocess.run(cmd, capture_output=True)

    return (idx, seg_path)


def encode_segment_smart(idx: int, input_path: str, start: float, end: float,
                          seg_path: str, encoder_args: list[str], audio_filter: str,
                          keyframes: list[float] = None) -> tuple[int, str]:
    """
    Smart render a segment: re-encode only edges, stream-copy middle.
    Uses keyframe-aligned boundaries to avoid duplicate frames.

    For a 30-second segment:
    - Part 1: Re-encode from start to first keyframe after (start + edge)
    - Part 2: Stream-copy from that keyframe to last keyframe before (end - edge)
    - Part 3: Re-encode from that keyframe to end
    - Concat all three parts

    This is 10-20x faster than full re-encoding for long segments.
    """
    duration = end - start
    edge = SMART_RENDER_EDGE

    # Get keyframes if not provided
    if keyframes is None:
        keyframes = get_keyframes(input_path)

    # Find keyframe-aligned boundaries
    # Part 1 ends at the first keyframe at or after (start + edge)
    ideal_part1_end = start + edge
    part1_end_kf = find_keyframe_at_or_after(keyframes, ideal_part1_end)

    # Part 3 starts at the last keyframe at or before (end - edge)
    ideal_part3_start = end - edge
    part3_start_kf = find_keyframe_at_or_before(keyframes, ideal_part3_start)

    # Validate: part1_end must be before part3_start (need room for middle)
    # Also check we found valid keyframes
    if (part1_end_kf is None or part3_start_kf is None or
        part1_end_kf >= part3_start_kf or
        part1_end_kf <= start or part3_start_kf >= end):
        # Fall back to full re-encode if keyframe alignment fails
        return encode_single_segment((idx, input_path, start, end, seg_path, encoder_args, audio_filter, None, False, keyframes))

    # Create temp directory for parts
    import tempfile as tf
    with tf.TemporaryDirectory() as tmpdir:
        parts = []

        # Part 1: Re-encode from start UP TO (but not including) keyframe
        # Use -ss BEFORE -i for proper sync
        part1 = os.path.join(tmpdir, "part1.mp4")
        part1_duration = part1_end_kf - start
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", input_path,
            "-t", str(part1_duration),
        ] + encoder_args

        if audio_filter:
            cmd.extend(["-af", audio_filter, "-c:a", "aac", "-b:a", "192k"])
        else:
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])

        cmd.extend(["-ar", "48000", "-avoid_negative_ts", "make_zero",
                    "-muxdelay", "0", "-muxpreload", "0",
                    "-loglevel", "error", part1])
        subprocess.run(cmd, capture_output=True)
        parts.append(part1)

        # Part 2: Stream-copy VIDEO from keyframe to keyframe
        # NOTE: Stream-copy has GOP boundary issues - may have ~1 frame glitch
        # This is a known limitation of mixing stream-copy with frame-accurate cuts
        middle_duration = part3_start_kf - part1_end_kf

        if middle_duration > 0:
            part2 = os.path.join(tmpdir, "part2.mp4")
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(part1_end_kf),
                "-i", input_path,
                "-t", str(middle_duration),
                "-c:v", "copy",
            ]
            # Re-encode audio to match other parts
            if audio_filter:
                cmd.extend(["-af", audio_filter, "-c:a", "aac", "-b:a", "192k"])
            else:
                cmd.extend(["-c:a", "aac", "-b:a", "192k"])
            cmd.extend(["-ar", "48000", "-avoid_negative_ts", "make_zero",
                        "-muxdelay", "0", "-muxpreload", "0",
                        "-loglevel", "error", part2])
            subprocess.run(cmd, capture_output=True)
            parts.append(part2)

        # Part 3: Re-encode from keyframe to segment end
        # Use -ss BEFORE -i for proper sync
        part3 = os.path.join(tmpdir, "part3.mp4")
        part3_duration = end - part3_start_kf
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(part3_start_kf),
            "-i", input_path,
            "-t", str(part3_duration),
        ] + encoder_args

        if audio_filter:
            cmd.extend(["-af", audio_filter, "-c:a", "aac", "-b:a", "192k"])
        else:
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])

        cmd.extend(["-ar", "48000", "-avoid_negative_ts", "make_zero",
                    "-muxdelay", "0", "-muxpreload", "0",
                    "-loglevel", "error", part3])
        subprocess.run(cmd, capture_output=True)
        parts.append(part3)

        # Concat all parts
        concat_file = os.path.join(tmpdir, "concat.txt")
        with open(concat_file, "w") as f:
            for part in parts:
                f.write(f"file '{part}'\n")

        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
            "-c", "copy", "-loglevel", "error", seg_path
        ]
        subprocess.run(cmd, capture_output=True)

    return (idx, seg_path)


def get_video_start_offset(input_path: str) -> float:
    """
    Get the video stream's start_time offset in seconds.
    h264_videotoolbox introduces encoder priming delay that shifts video PTS
    forward relative to audio, causing audio-ahead lip sync drift.
    """
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=start_time", "-of", "csv=p=0", input_path],
        capture_output=True, text=True
    )
    try:
        return float(result.stdout.strip())
    except (ValueError, AttributeError):
        return 0.0


def apply_audio_enhancement(input_path: str, output_path: str, audio_filter: str):
    """
    Apply audio enhancement to a video file.
    Re-encodes audio only, copies video stream to preserve perfect sync.
    Also compensates for h264_videotoolbox encoder priming delay by
    delaying audio to match the video start_time offset.

    Uses two-pass loudnorm (measure, then apply with linear gain) so output
    lands exactly on -16 LUFS; falls back to the provided single-pass chain
    if measurement fails.
    """
    # Measure, then apply a CONSTANT gain plus a true-peak limiter. Never
    # loudnorm on the output: it silently falls back to dynamic mode when the
    # required gain would clip, which ramps the first 30-60s of the video.
    pre_chain = build_pre_loudnorm_chain()
    if AUDIO_FILTERS["loudnorm"] in audio_filter:
        print(f"🎧 Measuring loudness...")
        stats = measure_loudness(input_path, pre_chain)
        if stats:
            candidate = build_constant_gain_chain(stats)
            gain = TARGET_I_LUFS - float(stats["input_i"])
            headroom = float(stats["input_tp"]) + gain
            print(f"   Measured {stats['input_i']} LUFS, peaks {stats['input_tp']} dBTP")
            print(f"   Constant gain {gain:+.2f} dB → {TARGET_I_LUFS} LUFS "
                  f"(would peak {headroom:+.2f} dBTP, limiter holds {TARGET_TP_DB})")

            # Peak limiting removes some energy, so verify and trim once.
            achieved = measure_integrated(input_path, pre_chain + "," + candidate)
            if achieved is not None:
                miss = TARGET_I_LUFS - achieved
                if abs(miss) > LOUDNESS_TOLERANCE_LU:
                    trim = max(-MAX_TRIM_DB, min(MAX_TRIM_DB, miss))
                    candidate = build_constant_gain_chain(stats, trim_db=trim)
                    print(f"   Limiter cost {-miss:+.2f} LU → trimming {trim:+.2f} dB")
                else:
                    print(f"   Verified {achieved:.1f} LUFS, within tolerance")
            else:
                print(f"   ⚠️ Could not verify output loudness — shipping untrimmed gain")
            audio_filter = pre_chain + "," + candidate
        else:
            print(f"   ⚠️ Loudness measurement failed — enhancement without normalization")
            print(f"      (skipping loudnorm entirely: single-pass would ramp the intro)")
            audio_filter = pre_chain

    # Measure video encoder priming delay and delay audio to match
    video_offset = get_video_start_offset(input_path)
    delay_ms = max(0, round(video_offset * 1000))

    if delay_ms > 0:
        # Prepend adelay to shift audio forward to match video start_time
        sync_filter = f"adelay={delay_ms}|{delay_ms}"
        combined_filter = f"{sync_filter},{audio_filter}"
        print(f"🎧 Applying audio enhancement + sync fix (adelay={delay_ms}ms)...")
    else:
        combined_filter = audio_filter
        print(f"🎧 Applying audio enhancement...")

    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-c:v", "copy",
        "-af", combined_filter,
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-loglevel", "error",
        output_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    print(f"   ✅ Audio enhancement complete")


def apply_av_sync_fix(input_path: str, output_path: str):
    """
    Fix A/V sync when audio enhancement is not being applied.
    Measures the video encoder priming delay and delays audio to match.
    """
    video_offset = get_video_start_offset(input_path)
    delay_ms = max(0, round(video_offset * 1000))

    if delay_ms > 0:
        print(f"🔧 Fixing A/V sync (adelay={delay_ms}ms to match encoder priming delay)...")
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c:v", "copy",
            "-af", f"adelay={delay_ms}|{delay_ms}",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-loglevel", "error",
            output_path
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"   ✅ A/V sync fixed")
    else:
        # No offset detected, just copy
        import shutil
        shutil.copy2(input_path, output_path)
        print(f"   ✅ No A/V sync fix needed")


def concatenate_segments_parallel(input_path: str, segments: list[tuple[float, float]], output_path: str,
                                   enhance_audio: bool = False, lut_path: str = None,
                                   workers: int = PARALLEL_WORKERS, smart_render: bool = True):
    """
    Extract and concatenate video segments using PARALLEL encoding with SMART RENDERING.

    Uses ThreadPoolExecutor to encode multiple segments simultaneously,
    taking advantage of VideoToolbox's ability to handle multiple encodes.

    Smart rendering (default on): Only re-encodes 1s at each cut point, stream-copies
    the middle of long segments. 10-20x faster for long segments.

    IMPORTANT: Audio enhancement is applied AFTER concatenation in a single pass
    to prevent cumulative timing drift across segments.

    Output is identical to full re-encoding.
    """

    mode = "smart render" if smart_render else "full re-encode"
    print(f"✂️  Concatenating {len(segments)} segments (parallel {workers}x, {mode})...")
    if enhance_audio:
        print(f"🎧 Audio enhancement enabled (will apply after concatenation)")
    if lut_path:
        print(f"🎨 Color grading with LUT: {os.path.basename(lut_path)}")

    start_time = time.time()

    # Get encoder args (checks hardware availability once, caches result)
    encoder_args = get_cached_encoder_args()

    # NOTE: Audio filter is NO LONGER applied per-segment to prevent timing drift
    # It will be applied in a single pass after concatenation
    video_filter = build_video_filter_chain(lut_path)

    # Pre-fetch keyframes for smart rendering (do this once, not per-segment)
    keyframes = None
    if smart_render and not video_filter:
        smart_count = sum(1 for s, e in segments if (e - s) > SMART_RENDER_THRESHOLD)
        if smart_count > 0:
            print(f"   📐 Pre-fetching keyframes for smart rendering...")
            keyframes = get_keyframes(input_path)
            print(f"   ⚡ Smart rendering {smart_count}/{len(segments)} long segments ({len(keyframes)} keyframes found)")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Prepare all encoding tasks - NO audio filter per segment
        tasks = []
        for i, (start, end) in enumerate(segments):
            seg_path = os.path.join(tmpdir, f"seg_{i:04d}.mp4")
            # Pass empty string for audio_filter to preserve original audio timing
            tasks.append((i, input_path, start, end, seg_path, encoder_args, "", video_filter, smart_render, keyframes))

        # Encode segments in parallel
        segment_files = [None] * len(segments)  # Pre-allocate to maintain order
        completed = 0

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(encode_single_segment, task): task[0] for task in tasks}

            for future in as_completed(futures):
                idx, seg_path = future.result()
                segment_files[idx] = seg_path
                completed += 1

                # Progress update every 10 segments or at completion
                if completed % 10 == 0 or completed == len(segments):
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    remaining = (len(segments) - completed) / rate if rate > 0 else 0
                    print(f"   ⏳ Encoded {completed}/{len(segments)} segments ({elapsed:.1f}s elapsed, ~{remaining:.0f}s remaining)")

        encode_time = time.time() - start_time
        print(f"   ✅ Parallel encoding complete in {encode_time:.1f}s ({len(segments)/encode_time:.1f} seg/s)")

        # Create concat file (order is preserved via indexed list)
        concat_path = os.path.join(tmpdir, "concat.txt")
        with open(concat_path, "w") as f:
            for seg_path in segment_files:
                f.write(f"file '{seg_path}'\n")

        # Always concat to temp file so we can do a sync-fix pass after
        concat_output = os.path.join(tmpdir, "concat_output.mp4")

        # Concatenate (stream copy - fast)
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", concat_path,
            "-c", "copy",
            "-loglevel", "error", concat_output
        ]
        subprocess.run(cmd, capture_output=True)

        # Apply audio enhancement + A/V sync fix (adelay compensates for encoder priming delay)
        if enhance_audio:
            audio_filter = build_audio_filter_chain(enhance=True)
            apply_audio_enhancement(concat_output, output_path, audio_filter)
        else:
            # No enhancement, but still fix A/V sync from encoder priming delay
            apply_av_sync_fix(concat_output, output_path)

    total_time = time.time() - start_time
    print(f"✅ Output saved to {output_path} (total: {total_time:.1f}s)")


def get_duration(input_path: str) -> float:
    """Get video duration in seconds."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", input_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


# ============================================================
# FCPXML EXPORT
# ============================================================

def seconds_to_fcpxml_time(seconds: float, fps: int = 30) -> str:
    """Convert seconds to FCPXML rational time format."""
    frames = round(seconds * fps)
    return f"{frames}/{fps}s"


def generate_fcpxml(
    segments: list[tuple[float, float]],
    input_video_path: str,
    output_path: str,
    fps: int = 30,
) -> str:
    """
    Generate a Final Cut Pro FCPXML file from keep segments.

    Each segment becomes an asset-clip referencing the original video,
    so the user can extend clips in FCP to recover trimmed frames.

    Returns the output path.
    """
    # Get video properties
    duration = get_duration(input_video_path)
    probe_cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "json", input_video_path,
    ]
    probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
    try:
        stream_info = json.loads(probe_result.stdout)["streams"][0]
        width = int(stream_info["width"])
        height = int(stream_info["height"])
    except (json.JSONDecodeError, KeyError, IndexError):
        print(f"   WARNING: Could not probe video dimensions, defaulting to 3840x2160")
        width, height = 3840, 2160

    # Create XML
    root = ET.Element("fcpxml", version="1.11")

    # Resources
    resources = ET.SubElement(root, "resources")

    # Format
    format_name = f"FFVideoFormat{height}p{fps}"
    frame_dur = seconds_to_fcpxml_time(1.0 / fps, fps)
    ET.SubElement(resources, "format",
        id="r1", name=format_name,
        frameDuration=frame_dur,
        width=str(width), height=str(height))

    # Asset
    asset_uid = str(uuid.uuid4())
    asset_duration = seconds_to_fcpxml_time(duration, fps)
    asset = ET.SubElement(resources, "asset",
        id="r2",
        name=os.path.splitext(os.path.basename(input_video_path))[0],
        uid=asset_uid,
        start="0s",
        duration=asset_duration,
        hasVideo="1", format="r1",
        hasAudio="1", audioSources="1", audioChannels="2", audioRate="48000")

    ET.SubElement(asset, "media-rep",
        kind="original-media",
        src=f"file://{os.path.abspath(input_video_path)}")

    # Project
    project_uid = str(uuid.uuid4())
    seq_duration = sum(end - start for start, end in segments)

    project = ET.SubElement(root, "project", name="Edited Video", uid=project_uid)
    sequence = ET.SubElement(project, "sequence",
        format="r1",
        duration=seconds_to_fcpxml_time(seq_duration, fps),
        tcStart="0s", tcFormat="NDF")

    spine = ET.SubElement(sequence, "spine")

    # Add clips
    timeline_offset = 0.0
    for start, end in segments:
        clip_duration = end - start
        ET.SubElement(spine, "asset-clip",
            ref="r2",
            offset=seconds_to_fcpxml_time(timeline_offset, fps),
            start=seconds_to_fcpxml_time(start, fps),
            duration=seconds_to_fcpxml_time(clip_duration, fps))
        timeline_offset += clip_duration

    # Write to file with DOCTYPE
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    lines = xml_str.split("\n")
    lines.insert(1, "<!DOCTYPE fcpxml>")
    xml_str = "\n".join(lines)

    with open(output_path, "w") as f:
        f.write(xml_str)

    return output_path


def write_edit_report(report_path: str, input_path: str, duration: float,
                      kept_duration: float, segments: list[tuple[float, float]],
                      report: dict, elapsed: float):
    """Write a markdown summary of every edit decision for quick review."""
    def ts(seconds: float) -> str:
        m, s = divmod(int(seconds), 60)
        return f"{m}:{s:02d}"

    removed = duration - kept_duration
    lines = [
        f"# Edit Report — {os.path.basename(input_path)}",
        "",
        f"- Original: {duration:.1f}s ({ts(duration)}) → Edited: {kept_duration:.1f}s ({ts(kept_duration)})",
        f"- Removed: {removed:.1f}s ({100*removed/duration:.1f}%)",
        f"- Kept segments: {len(segments)} (from {report['silence_segments']} VAD speech segments)",
        f"- Processing time: {elapsed:.1f}s",
        "",
    ]

    if report.get("transcript_rejected"):
        lines += ["## ⚠️ Transcript rejected — silence-only edit", "",
                  f"Reason: {report['transcript_rejected']}",
                  "",
                  "Whisper returned a degenerate transcript, so every word-level cut "
                  "(restarts, retakes, fillers, throat clears) was skipped. This edit is "
                  "silence removal and audio enhancement only. Any 'cut cut' markers in "
                  "the recording are still in the video and need a manual pass.",
                  ""]

    if report.get("full_stop_restart") is not None:
        t = report["full_stop_restart"]
        lines += [f"## Full stop restart", "",
                  f"- Discarded everything before {t:.1f}s ({ts(t)}) in the original recording", ""]

    if report.get("restarts"):
        lines += ["## 'Cut cut' retakes removed", ""]
        for s, e in report["restarts"]:
            lines.append(f"- Marker at {s:.1f}s ({ts(s)}) in original — botched take before it cut, redo kept")
        lines.append("")

    if report.get("retakes"):
        lines += [f"## Unmarked retakes / false starts removed ({len(report['retakes'])})", ""]
        for s, e in report["retakes"]:
            lines.append(f"- {s:.1f}s - {e:.1f}s ({ts(s)} - {ts(e)}) in original — earlier take cut, last take kept")
        lines.append("")

    if report.get("fillers"):
        lines += [f"## Fillers removed ({len(report['fillers'])})", ""]
        for s, e in report["fillers"]:
            lines.append(f"- {s:.1f}s ({ts(s)}) in original")
        lines.append("")

    if report.get("nonspeech"):
        lines += [f"## Non-speech noise removed ({len(report['nonspeech'])})", ""]
        for s, e in report["nonspeech"]:
            lines.append(f"- {s:.1f}s - {e:.1f}s ({ts(s)}) in original — no words transcribed (throat clear / stray sound)")
        lines.append("")

    if report.get("media"):
        lines += [f"## Protected media spans — kept verbatim ({len(report['media'])})", ""]
        for s, e in report["media"]:
            lines.append(f"- {s:.1f}s - {e:.1f}s ({ts(s)} - {ts(e)}) in original — sustained non-speech audio (played clip / music); no cuts applied inside")
        lines.append("")

    lines += ["## Notes", "",
              "All timestamps refer to the ORIGINAL recording, not the edited output.",
              "Spot-check tip: if a cut looks wrong, the FCPXML export lets you extend clips to recover trimmed frames.",
              ""]

    with open(report_path, "w") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Jump cut editor using Silero VAD (PARALLEL version)")
    parser.add_argument("input", help="Input video file")
    parser.add_argument("output", nargs="?", default=None, help="Output video/fcpxml file (auto-generated if omitted)")
    parser.add_argument("--min-silence", type=float, default=MIN_SILENCE_DURATION,
                        help=f"Minimum silence duration to cut (default: {MIN_SILENCE_DURATION}s)")
    parser.add_argument("--min-speech", type=float, default=MIN_SPEECH_DURATION,
                        help=f"Minimum speech duration to keep (default: {MIN_SPEECH_DURATION}s)")
    parser.add_argument("--padding", type=int, default=PADDING_MS,
                        help=f"Padding around speech in ms (default: {PADDING_MS})")
    parser.add_argument("--merge-gap", type=float, default=0.3,
                        help="Merge segments closer than this (default: 0.3s)")
    parser.add_argument("--keep-start", action="store_true", default=True,
                        help="Always start from 0:00 (preserve intro, default: True)")
    parser.add_argument("--no-keep-start", action="store_false", dest="keep_start",
                        help="Allow cutting silence at the very beginning")
    parser.add_argument("--enhance-audio", action="store_true", default=False,
                        help="Apply audio enhancement (EQ, compression, loudness normalization)")
    parser.add_argument("--detect-restarts", action="store_true", default=False,
                        help=f"Detect '{RESTART_PHRASE}' markers; remove the botched take before each marker and keep the redo that follows")
    parser.add_argument("--detect-full-stop-restart", action="store_true", default=False,
                        help=f"Detect '{FULL_STOP_RESTART_PHRASE}' and restart video from that point")
    parser.add_argument("--remove-fillers", action="store_true", default=False,
                        help="Remove standalone filler words (um, uh, ...) detected via transcription")
    parser.add_argument("--detect-retakes", action="store_true", default=False,
                        help="Detect unmarked retakes (same line said twice, no 'cut cut') and false starts; keep the last take unless an earlier one scores clearly better")
    parser.add_argument("--retake-similarity", type=float, default=RETAKE_SIMILARITY,
                        help=f"Sentence similarity ratio to call two lines the same take (default: {RETAKE_SIMILARITY})")
    parser.add_argument("--cut-nonspeech", action="store_true", default=False,
                        help=f"Cut short VAD segments with no transcribed words (throat clears, stray noises, <= {NONSPEECH_MAX_S}s)")
    parser.add_argument("--tight", action="store_true", default=False,
                        help="Optional candidate thresholds: min-silence 0.35s, padding 40ms; review every boundary")
    parser.add_argument("--protect-media", action="store_true", default=False,
                        help="Detect on-screen media audio (played clips, AI video/music) and keep those spans verbatim — no cuts of any kind inside them")
    parser.add_argument("--restart-phrase", type=str, default=RESTART_PHRASE,
                        help=f"Phrase to trigger restart (default: '{RESTART_PHRASE}')")
    parser.add_argument("--restart-after", type=float, default=0.0,
                        help="Only apply restart cuts after this timestamp in seconds (default: 0.0)")
    parser.add_argument("--whisper-model", type=str, default="small",
                        help="Whisper model size for restart detection (default: small)")
    parser.add_argument("--apply-lut", type=str, default=None,
                        help="Path to LUT file for color grading (.cube, .3dl, .dat, .m3d, .csp)")
    parser.add_argument("--workers", type=int, default=PARALLEL_WORKERS,
                        help=f"Number of parallel encoding workers (default: {PARALLEL_WORKERS})")
    parser.add_argument("--smart-render", action="store_true", default=False,
                        help="Optional smart rendering; may have a one-frame glitch at internal boundaries, inspect every join")
    parser.add_argument("--no-smart-render", action="store_false", dest="smart_render",
                        help="Full re-encode all segments; avoids smart-render keyframe shortcuts (default)")
    parser.add_argument("--export", type=str, default="mp4", choices=["mp4", "fcpxml", "both"],
                        help="Output format: mp4 (default), fcpxml (Final Cut Pro), or both")

    args = parser.parse_args()

    # Validate LUT file if provided
    if args.apply_lut:
        lut_path = Path(args.apply_lut)
        if not lut_path.exists():
            print(f"❌ LUT file not found: {args.apply_lut}")
            return
        if lut_path.suffix.lower() not in SUPPORTED_LUT_FORMATS:
            print(f"❌ Unsupported LUT format: {lut_path.suffix}")
            print(f"   Supported: {', '.join(SUPPORTED_LUT_FORMATS)}")
            return

    # Tight preset: only tighten values the user didn't explicitly loosen.
    if args.tight:
        args.min_silence = min(args.min_silence, 0.35)
        args.padding = min(args.padding, 40)
        print("🔧 Tight pacing preset: min-silence "
              f"{args.min_silence}s, padding {args.padding}ms")

    input_path = args.input
    export_mode = args.export

    # Derive output paths based on export mode
    input_stem = os.path.splitext(input_path)[0]
    if args.output:
        output_path = args.output
    else:
        # Auto-generate output path based on export mode
        if export_mode == "fcpxml":
            output_path = f"{input_stem}_edited.fcpxml"
        else:
            output_path = f"{input_stem}_edited.mp4"

    mp4_path = output_path if output_path.endswith(".mp4") else f"{input_stem}_edited.mp4"
    fcpxml_path = output_path if output_path.endswith(".fcpxml") else f"{input_stem}_edited.fcpxml"

    protected_outputs = []
    if export_mode in ("mp4", "both"):
        protected_outputs.append(Path(mp4_path))
    if export_mode in ("fcpxml", "both"):
        protected_outputs.append(Path(fcpxml_path))
    for target in protected_outputs:
        if target.resolve() == Path(input_path).resolve() or target.exists() or target.is_symlink():
            raise FileExistsError("Use fresh output paths; original media and previous exports are preserved")

    print(f"🎬 Jump Cut Editor (Silero VAD) - PARALLEL VERSION")
    print(f"   Input: {input_path}")
    if export_mode in ("mp4", "both"):
        print(f"   Output MP4: {mp4_path}")
    if export_mode in ("fcpxml", "both"):
        print(f"   Output FCPXML: {fcpxml_path}")
    print(f"   Parallel workers: {args.workers}")
    print()

    overall_start = time.time()

    # Get video duration
    duration = get_duration(input_path)
    print(f"📏 Video duration: {duration:.2f}s")

    # Extract audio ONCE — reused for both VAD and Whisper (both need 16kHz mono)
    print(f"🎵 Extracting audio...")
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio_path = tmp.name

    # Edit report data (written next to the output at the end)
    report = {
        "restarts": [],
        "full_stop_restart": None,
        "fillers": [],
        "retakes": [],
        "nonspeech": [],
        "media": [],
        "silence_segments": 0,
    }
    media_regions: list[tuple[float, float]] = []

    needs_transcription = (args.detect_restarts or args.detect_full_stop_restart
                           or args.remove_fillers or args.detect_retakes
                           or args.cut_nonspeech)

    try:
        extract_audio(input_path, audio_path)

        # Run Silero VAD
        print(f"🎯 Running Silero VAD (min_silence={args.min_silence}s, min_speech={args.min_speech}s)...")
        speech_segments = get_speech_timestamps_silero(
            audio_path,
            min_speech_duration=args.min_speech,
            min_silence_duration=args.min_silence
        )
        print(f"   Found {len(speech_segments)} speech segments")
        report["silence_segments"] = len(speech_segments)

        # Debug: show first few segments
        for i, (start, end) in enumerate(speech_segments[:5]):
            print(f"     {i+1}. {start:.2f}s - {end:.2f}s ({end-start:.2f}s)")
        if len(speech_segments) > 5:
            print(f"     ... and {len(speech_segments) - 5} more")

        if not speech_segments:
            print("⚠️  No speech detected!")
            return

        # Merge close segments
        speech_segments = merge_close_segments(speech_segments, args.merge_gap)
        print(f"📎 After merging close segments: {len(speech_segments)} segments")

        # Add padding
        padding_s = args.padding / 1000
        speech_segments = add_padding(speech_segments, padding_s, duration)
        print(f"🔲 After adding {args.padding}ms padding: {len(speech_segments)} segments")

        # Remember where speech originally began. If restart detection later drops
        # leading segments (a flubbed take before a "cut cut" / "full stop restart"),
        # the first kept segment will start LATER than this — the signal that the
        # intro was deliberately cut and must NOT be re-added by --keep-start.
        original_first_start = speech_segments[0][0] if speech_segments else 0.0

        # Protect on-screen media BEFORE any cut logic runs: loud non-speech
        # audio between his speech segments is a playing clip, not silence
        if args.protect_media:
            print(f"\n🎼 Scanning for on-screen media audio (played clips, AI video/music)...")
            media_regions = find_media_regions(audio_path, speech_segments, duration)
            if media_regions:
                for ms, me in media_regions:
                    print(f"   Protected media: {ms:.2f}s - {me:.2f}s ({me - ms:.1f}s, kept verbatim)")
                report["media"] = media_regions
            else:
                print(f"   No media audio detected")

        # Transcribe once for all word-level features (restarts, fillers)
        if needs_transcription:
            words = transcribe_with_whisper(audio_path, model_name=args.whisper_model)

            # A hallucinated transcript must never drive a cut. Fall back to a
            # silence-only edit and say so loudly rather than deleting footage.
            broken = transcript_looks_broken(words)
            if broken:
                print(f"\n⚠️  TRANSCRIPT REJECTED: {broken}")
                print("   Skipping all word-level cuts (restarts, retakes, fillers, noise).")
                print("   Falling back to silence removal + audio enhancement only.")
                report["transcript_rejected"] = broken
                words = []
                args.detect_full_stop_restart = False
                args.detect_restarts = False
                args.detect_retakes = False
                args.remove_fillers = False
                args.cut_nonspeech = False

            # Full stop restart runs first — discards everything before the last
            # occurrence, so any "cut cut" phrases in discarded footage are ignored
            if args.detect_full_stop_restart:
                print(f"\n🔁 Detecting '{FULL_STOP_RESTART_PHRASE}'...")
                fsr_times = find_full_stop_restarts(words)
                if media_regions:
                    # a phrase heard inside a played clip is the clip talking
                    fsr_times = [t for t in fsr_times
                                 if not any(ms <= t <= me for ms, me in media_regions)]

                if fsr_times:
                    print(f"   Found {len(fsr_times)} full stop restart(s)")
                    speech_segments = apply_full_stop_restart(speech_segments, fsr_times)
                    # Protection applies within the retained recording, not to
                    # played media from an opening deliberately abandoned.
                    media_regions = apply_full_stop_restart(media_regions, fsr_times)
                    report["media"] = media_regions
                    report["full_stop_restart"] = max(fsr_times)
                    if not speech_segments:
                        print("⚠️  No speech segments remain after full stop restart — nothing to export")
                        return
                else:
                    print(f"   No full stop restarts found")

            # Cut cut: remove mistake + trigger segment pairs
            if args.detect_restarts:
                print(f"\n🔄 Detecting restart phrases ('{args.restart_phrase}')...")
                restart_spans = find_restart_phrases(words, phrase=args.restart_phrase)
                if args.restart_after > 0 and restart_spans:
                    before = len(restart_spans)
                    restart_spans = [s for s in restart_spans if s[1] >= args.restart_after]
                    skipped = before - len(restart_spans)
                    if skipped:
                        print(f"   Skipped {skipped} restart(s) before {args.restart_after:.1f}s (--restart-after)")
                restart_spans = filter_windows_outside_media(restart_spans, media_regions, "restart")

                if restart_spans:
                    print(f"   Found {len(restart_spans)} restart phrase(s)")
                    speech_segments = apply_restart_cuts(speech_segments, restart_spans, RESTART_LOOKBACK)
                    print(f"   After restart cuts: {len(speech_segments)} segments")
                    report["restarts"] = restart_spans
                else:
                    print(f"   No restart phrases found")

            # Unmarked retakes + false starts: last take wins
            if args.detect_retakes:
                print(f"\n🔁 Detecting unmarked retakes and false starts...")
                print(f"   ⚠️  Off by default since 2026-07-27 — it removes rephrased lines.")
                print(f"   ⚠️  Spot-check every cut listed in the report before using this edit.")
                retake_windows = find_retake_windows(words, similarity=args.retake_similarity)
                retake_windows = filter_windows_outside_media(retake_windows, media_regions, "retake")
                if retake_windows:
                    speech_segments = apply_kill_windows(
                        speech_segments, retake_windows, RETAKE_MIN_KEEP, "retake")
                    report["retakes"] = retake_windows
                else:
                    print(f"   No unmarked retakes found")

            # Filler removal: cut standalone "um"/"uh" bounded by pauses
            if args.remove_fillers:
                print(f"\n🧹 Detecting filler words...")
                filler_windows = find_filler_words(words)
                filler_windows = filter_windows_outside_media(filler_windows, media_regions, "filler")
                if filler_windows:
                    speech_segments = apply_filler_cuts(speech_segments, filler_windows)
                    report["fillers"] = filler_windows
                else:
                    print(f"   No fillers found")

            # Non-speech noise: drop short word-free VAD segments
            if args.cut_nonspeech:
                print(f"\n🤫 Detecting non-speech vocal noise (throat clears, stray sounds)...")
                speech_segments, nonspeech = drop_nonspeech_segments(speech_segments, words)
                if media_regions and nonspeech:
                    # word-free segments inside protected media are the media
                    restore = [seg for seg in nonspeech
                               if any(seg[0] < me and seg[1] > ms
                                      for ms, me in media_regions)]
                    for seg in restore:
                        print(f"   🎼 Restored {seg[0]:.2f}s - {seg[1]:.2f}s (inside protected media)")
                        nonspeech.remove(seg)
                    speech_segments = sorted(speech_segments + restore)
                if nonspeech:
                    report["nonspeech"] = nonspeech
                else:
                    print(f"   No non-speech noise segments found")
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)

    # Union protected media spans back into the kept timeline, verbatim.
    # Runs AFTER all cut logic so nothing can shrink or split a media span.
    if media_regions:
        speech_segments = apply_media_protection(speech_segments, media_regions, duration)
        kept_media = sum(e - s for s, e in media_regions)
        print(f"\n🎼 Kept {len(media_regions)} media span(s) verbatim (~{kept_media:.1f}s)")

    # Keep start: force first segment to start at 0:00 — but ONLY if restart
    # detection did not deliberately drop the opening footage. If the first kept
    # segment now starts later than speech originally did, a flubbed intro take
    # was cut; extending back to 0:00 would re-add the very content (mistake +
    # "cut cut") we just removed, so leave the clean take's start untouched.
    intro_was_cut = bool(speech_segments) and speech_segments[0][0] > original_first_start + 0.01
    if args.keep_start and speech_segments and speech_segments[0][0] > 0:
        if intro_was_cut:
            print(f"📌 Intro take was cut by restart detection — starting at the clean take "
                  f"({speech_segments[0][0]:.2f}s), not 0:00")
        else:
            first_start, first_end = speech_segments[0]
            speech_segments[0] = (0.0, first_end)
            print(f"📌 Preserving intro: extended first segment to start at 0:00")

    # Generate FCPXML if requested
    if export_mode in ("fcpxml", "both"):
        print(f"\n📄 Generating FCPXML for Final Cut Pro...")
        generate_fcpxml(speech_segments, input_path, fcpxml_path)
        print(f"   ✅ FCPXML saved to {fcpxml_path}")

    # Render MP4 if requested
    if export_mode in ("mp4", "both"):
        concatenate_segments_parallel(input_path, speech_segments, mp4_path,
                                       enhance_audio=args.enhance_audio, lut_path=args.apply_lut,
                                       workers=args.workers, smart_render=args.smart_render)

    # Stats
    overall_time = time.time() - overall_start
    kept_duration = sum(end - start for start, end in speech_segments)
    removed = duration - kept_duration

    print()
    print(f"📊 Stats:")
    print(f"   Original: {duration:.2f}s")
    print(f"   Kept: {kept_duration:.2f}s")
    print(f"   Removed: {removed:.2f}s ({100*removed/duration:.1f}%)")
    if export_mode in ("mp4", "both"):
        print(f"   MP4: {mp4_path}")
    if export_mode in ("fcpxml", "both"):
        print(f"   FCPXML: {fcpxml_path}")
    print(f"   ⚡ Total processing time: {overall_time:.1f}s")

    # Write edit report — a human-readable record of every cut decision so the
    # edit can be spot-checked without scrubbing the whole video.
    report_path = os.path.splitext(mp4_path if export_mode in ("mp4", "both") else fcpxml_path)[0] + "_report.md"
    try:
        write_edit_report(report_path, input_path, duration, kept_duration,
                          speech_segments, report, overall_time)
        print(f"   📝 Edit report: {report_path}")
    except Exception as e:
        print(f"   ⚠️ Could not write edit report: {e}")


if __name__ == "__main__":
    main()
