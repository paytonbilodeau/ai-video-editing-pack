#!/usr/bin/env python3
"""Optional historical MusicGen research adapter. Model weights are CC-BY-NC-4.0,
not included. Read OPTIONAL PROVIDERS.md and current model terms before choosing it.
No speed, output license or commercial-use assurance. Existing output is preserved.
"""
import argparse, os, subprocess, tempfile
import numpy as np
import wave

DEFAULT_PROMPT = (
    "minimal ambient electronic background music, soft warm analog synth "
    "pads, gentle subtle tech pulse, light clean arpeggio, calm focused "
    "educational mood, modern, understated, smooth consistent energy, "
    "no vocals, no loud drums"
)


def save_wav(path, audio, sr):
    a = np.clip(audio, -1, 1)
    pcm = (a * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(a.shape[1] if a.ndim > 1 else 1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prompt", default=DEFAULT_PROMPT)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--lufs", type=float, default=-32.0)
    ap.add_argument("--accept-model-terms", action="store_true", help="Confirm noncommercial model terms and authorize the optional download")
    args = ap.parse_args()
    if not args.accept_model_terms: ap.error("Read the MusicGen noncommercial model terms; this route is not enabled by setup")
    if args.duration <= 0: ap.error("duration must be positive")
    if os.path.exists(args.out): ap.error("Output exists; choose a new path")
    import torch

    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    model_id = "facebook/musicgen-stereo-small"
    print(f"loading {model_id}...")
    proc = AutoProcessor.from_pretrained(model_id)
    model = MusicgenForConditionalGeneration.from_pretrained(
        model_id, torch_dtype=torch.float32)
    model = model.float()
    model.eval()
    torch.manual_seed(args.seed)
    sr = model.config.audio_encoder.sampling_rate

    # window 1: 30s from text
    print("chunk 1/… generating 30s seed…")
    inputs = proc(text=[args.prompt], padding=True, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=1500, do_sample=True,
                             guidance_scale=3.0)
    audio = out[0].cpu().numpy().T  # (samples, channels)

    # continuation windows: prompt with the last 10s, keep the new ~20s
    hold = int(10 * sr)
    chunk = 0
    while audio.shape[0] / sr < args.duration + 2:
        chunk += 1
        print(f"continuation {chunk}: have {audio.shape[0] / sr:.0f}s…")
        tail = audio[-hold:].T.astype(np.float32)  # (channels, samples)
        inputs = proc(audio=[tail], sampling_rate=sr, text=[args.prompt],
                      padding=True, return_tensors="pt")
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=1500,
                                 do_sample=True, guidance_scale=3.0)
        new = out[0].cpu().numpy().T
        # crossfade the overlap region (50ms) and append only new audio
        add = new[hold:]
        xf = int(0.05 * sr)
        if xf > 0 and add.shape[0] > xf:
            ramp = np.linspace(0, 1, xf)[:, None]
            audio[-xf:] = audio[-xf:] * (1 - ramp) + add[:xf] * ramp
            add = add[xf:]
        audio = np.concatenate([audio, add])

    # exact length + gentle fades
    n = int(args.duration * sr)
    audio = audio[:n]
    fade = min(int(1.5 * sr), n // 2)
    audio[:fade] *= np.linspace(0, 1, fade)[:, None]
    audio[-fade:] *= np.linspace(1, 0, fade)[:, None]

    tmp = tempfile.mktemp(suffix=".wav")
    save_wav(tmp, audio, sr)
    # loudness-normalize to bed level, resample to 48k
    subprocess.run([
        "ffmpeg", "-n", "-v", "error", "-i", tmp,
        "-af", f"loudnorm=I={args.lufs}:TP=-3:LRA=9",
        "-ar", "48000", args.out], check=True)
    os.remove(tmp)
    print(f"wrote {args.out}: {args.duration:.2f}s at ~{args.lufs} LUFS")


if __name__ == "__main__":
    main()
