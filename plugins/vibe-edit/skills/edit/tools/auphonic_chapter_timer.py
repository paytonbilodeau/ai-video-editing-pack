#!/usr/bin/env python3
"""Re-time scripted chapter titles against an Auphonic word-level transcript.

Auphonic's HTML transcript is a Vue app and its auto-chapters can collapse to a
single marker on long talking-head videos, so for scripted videos we take the
script's chapter titles and locate each one by the first sentence actually
spoken at that point. Word timings come from the production's ``speech`` JSON
output (``extracted.json``), fetched via the API or given as a local file.

Usage:
  python3 tools/auphonic_chapter_timer.py --production <uuid> --anchors anchors.json \
      --out project/<stem>_chapters
  python3 tools/auphonic_chapter_timer.py --speech-json extracted.json --anchors anchors.json

anchors.json: [{"title": "Part 1: ...", "phrases": ["first sentence spoken", "alt phrasing"]}, ...]
A chapter with no phrases (or "time": 0) is pinned to 0:00. Chapters are searched in
order, each after the previous hit, so repeated wording later in the video is ignored.
Exit code 1 if any chapter matches below --min-match (default 0.85).
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from urllib.parse import urlsplit
from difflib import SequenceMatcher

API = "https://auphonic.com/api"


def _download_headers(url, key):
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Auphonic downloads require an HTTPS URL without embedded credentials")
    return {"Authorization": f"Bearer {key}"} if parsed.hostname == "auphonic.com" and parsed.port in (None, 443) else {}


class _SafeDownloadRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        allowed_headers = _download_headers(newurl, "unused")
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None and not allowed_headers:
            redirected.remove_header("Authorization")
        return redirected


def fetch_speech_json(uuid: str) -> list:
    if not isinstance(uuid, str) or len(uuid) > 128 or not re.fullmatch(r"[A-Za-z0-9_-]+", uuid):
        raise ValueError("Invalid Auphonic production identifier")
    key = os.getenv("AUPHONIC_API_KEY")
    if not key:
        sys.exit("AUPHONIC_API_KEY not set (source .env first)")
    opener = urllib.request.build_opener(_SafeDownloadRedirect())
    url = f"{API}/production/{uuid}.json"
    with opener.open(urllib.request.Request(url, headers=_download_headers(url, key)), timeout=60) as response:
        data = json.load(response)["data"]
    url = next((f["download_url"] for f in data.get("output_files", [])
                if f.get("format") == "speech" and f.get("download_url")), None)
    if not url:
        sys.exit("production has no 'speech' JSON output (preset needs speech recognition)")
    with opener.open(urllib.request.Request(url, headers=_download_headers(url, key)), timeout=60) as response:
        return json.load(response)


def word_stream(segments: list) -> list:
    words = []
    for seg in segments:
        for item in seg.get("timestamps") or []:
            for tok in re.findall(r"[a-z0-9'$%]+", str(item[0]).lower()):
                words.append((float(item[1]), tok))
    return words


def norm(s: str) -> list:
    return re.findall(r"[a-z0-9'$%]+", s.lower())


def find(words, phrase, after=0.0):
    pw = norm(phrase); n = len(pw); best = (0.0, None, "")
    for i in range(len(words) - n + 1):
        if words[i][0] < after:
            continue
        win = [w for _, w in words[i:i + n]]
        r = SequenceMatcher(None, pw, win).ratio()
        if r > best[0]:
            best = (r, words[i][0], " ".join(win))
            if r == 1.0:
                break
    return best


def fmt(sec: int) -> str:
    return f"{sec // 60}:{sec % 60:02d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--production", help="Auphonic production uuid")
    src.add_argument("--speech-json", help="local extracted.json from Auphonic")
    ap.add_argument("--anchors", required=True, help="JSON list of {title, phrases}")
    ap.add_argument("--out", help="output path stem (writes <stem>.json and <stem>.txt)")
    ap.add_argument("--lead", type=int, default=1, help="seconds before the first word (default 1)")
    ap.add_argument("--min-match", type=float, default=0.85)
    a = ap.parse_args()

    segments = fetch_speech_json(a.production) if a.production else json.load(open(a.speech_json))
    words = word_stream(segments)
    anchors = json.load(open(a.anchors))
    out, last, weak = [], 0.0, False
    for ch in anchors:
        phrases = ch.get("phrases") or []
        if not phrases or ch.get("time") == 0:
            out.append({"title": ch["title"], "time": 0}); print(f"{ch['title']:<46} 0:00"); continue
        hits = sorted((find(words, ph, after=last) for ph in phrases), key=lambda h: -h[0])
        r, t, spoken = hits[0]
        if t is None:
            weak = True; print(f"{ch['title']:<46}   ??   NO MATCH"); continue
        sec = max(0, int(t) - a.lead)
        flag = "" if r >= a.min_match else "   <-- weak, verify"
        if flag: weak = True
        print(f"{ch['title']:<46} {fmt(sec):>6}  match={r:.2f}  spoken='{spoken[:55]}'{flag}")
        out.append({"title": ch["title"], "time": sec}); last = t
    if a.out:
        json.dump(out, open(f"{a.out}.json", "w"), indent=1)
        with open(f"{a.out}.txt", "w") as fh:
            fh.writelines(f"{fmt(c['time'])} {c['title']}\n" for c in out)
        print(f"saved {a.out}.json / .txt")
    sys.exit(1 if weak else 0)


if __name__ == "__main__":
    main()
