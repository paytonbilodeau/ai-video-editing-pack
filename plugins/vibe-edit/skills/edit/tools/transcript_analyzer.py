#!/usr/bin/env python3
"""
Transcript Analyzer — Shared utilities for intelligent video editing.

Provides all transcript-based analysis functions:
- Sentence splitting from word-level timestamps
- Retake detection (explicit "cut cut" + implicit repeated phrases)
- False start detection
- Filler word detection (core + contextual)
- Take scoring and selection
- Cut placement refinement (word boundary snapping, tail-pause rule)
- Pacing validation
- Intro hook finder (for swivel placement)
- Edit manifest builder
- Cut list ↔ keep list conversion

All functions operate on a standardized word list:
    [{"text": str, "start": float, "end": float, "confidence": float}, ...]
"""

import json
from difflib import SequenceMatcher
from typing import Optional

# ============================================================
# CONFIGURATION
# ============================================================

CONFIG = {
    # Silence detection
    "silence_threshold": 0.75,      # Gaps longer than this → candidate for removal
    "min_preserved_gap": 0.15,      # Always keep at least this much silence between sentences
    "max_gap_within_topic": 0.40,   # Max gap between sentences in same topic
    "topic_transition_gap": 0.60,   # Gap at major topic changes

    # Filler words
    "filler_removal_rate": 0.90,
    "min_padding_for_filler_cut": 0.05,   # 50ms silence around filler to cut it
    "filler_replacement_silence_ratio": 0.35,

    # Take selection
    "similarity_threshold": 0.60,
    "min_phrase_length": 5,

    # Cut placement
    "micro_fade_duration": 0.04,    # 40ms (2 frames at 24fps)
    "pre_word_margin": 0.025,       # 25ms before word start for transient capture
    "post_word_margin": 0.25,       # 250ms after word end — preserves final syllable tail + room for Whisper timing error

    # Pacing validation
    "min_gap_between_sentences": 0.08,
    "max_gap_between_sentences": 0.50,
    "energy_jump_threshold_db": 8.0,

    # Quality
    "min_compression_ratio": 0.35,
    "max_compression_ratio": 0.75,

    # Restart detection
    "restart_phrase": "cut cut",
    "restart_lookback": 10.0,
}

# Filler word lists
CORE_FILLERS = {"um", "uh", "umm", "uhh", "er", "err", "hmm"}

CONTEXTUAL_FILLERS = {
    "like", "you know", "so", "basically", "actually",
    "literally", "right", "i mean", "well", "kind of", "sort of",
}

MULTI_WORD_FILLERS = {
    "you know what i mean",
    "if that makes sense",
    "or whatever",
    "and stuff like that",
    "so basically",
    "so as i was saying",
    "as i mentioned",
}

# Intro hook phrases for swivel placement
INTRO_HOOK_PHRASES = [
    "in this video",
    "today we're going to",
    "today we're covering",
    "what we'll be",
    "we're going to talk about",
    "we're going to be talking about",
    "let me show you",
    "i'm going to show you",
    "in today's video",
    "what we're going to do",
    "i want to show you",
    "let me walk you through",
    "i'm going to walk you through",
    "here's what we'll cover",
    "we're going to be looking at",
]


# ============================================================
# WORD LIST PARSING
# ============================================================

def parse_whisper_output(whisper_result: dict) -> list[dict]:
    """
    Normalize Whisper output into a flat word list with timestamps.

    Args:
        whisper_result: Raw Whisper transcribe() output

    Returns:
        [{"text": str, "start": float, "end": float, "confidence": float}, ...]
    """
    words = []
    for segment in whisper_result.get("segments", []):
        for word_info in segment.get("words", []):
            words.append({
                "text": word_info.get("word", "").strip(),
                "start": word_info["start"],
                "end": word_info["end"],
                "confidence": word_info.get("probability", word_info.get("score", 0.8)),
            })
    return words


# ============================================================
# SENTENCE SPLITTING
# ============================================================

def split_into_sentences(words: list[dict], pause_threshold: float = 0.5) -> list[dict]:
    """
    Split word list into sentence-level chunks based on pauses and punctuation.

    Returns:
        [{"words": [...], "start": float, "end": float, "text": str}, ...]
    """
    if not words:
        return []

    sentences = []
    current = {"words": [], "start": None, "end": None}

    for i, word in enumerate(words):
        if current["start"] is None:
            current["start"] = word["start"]
        current["words"].append(word)
        current["end"] = word["end"]

        # Sentence break indicators
        is_break = False
        if i < len(words) - 1:
            gap = words[i + 1]["start"] - word["end"]
            if gap > pause_threshold:
                is_break = True
        else:
            is_break = True  # last word

        if word["text"].rstrip().endswith((".", "!", "?")):
            is_break = True

        if is_break and len(current["words"]) >= 2:
            current["text"] = " ".join(w["text"] for w in current["words"])
            sentences.append(current)
            current = {"words": [], "start": None, "end": None}

    # Don't lose trailing words
    if current["words"]:
        current["text"] = " ".join(w["text"] for w in current["words"])
        sentences.append(current)

    return sentences


# ============================================================
# SPEAKER CADENCE LEARNING
# ============================================================

def learn_speaker_cadence(words: list[dict], sample_duration: float = 120.0) -> dict:
    """
    Analyze the first N seconds to learn the speaker's natural rhythm.

    Returns:
        {"median_gap": float, "p25_gap": float, "p75_gap": float, "mean_gap": float}
    """
    sample_words = [w for w in words if w["start"] < sample_duration]
    gaps = []

    for i in range(1, len(sample_words)):
        gap = sample_words[i]["start"] - sample_words[i - 1]["end"]
        if 0.05 < gap < 2.0:
            gaps.append(gap)

    if not gaps:
        return {"median_gap": 0.2, "p25_gap": 0.12, "p75_gap": 0.35, "mean_gap": 0.2}

    gaps.sort()
    n = len(gaps)
    return {
        "median_gap": gaps[n // 2],
        "p25_gap": gaps[n // 4] if n >= 4 else gaps[0],
        "p75_gap": gaps[3 * n // 4] if n >= 4 else gaps[-1],
        "mean_gap": sum(gaps) / n,
    }


# ============================================================
# SILENCE DETECTION
# ============================================================

def detect_silence_from_transcript(
    words: list[dict],
    threshold: float = None,
    min_preserved_gap: float = None,
) -> list[dict]:
    """
    Detect silence/dead air gaps from transcript word timestamps.

    Returns list of cut candidates:
        [{"start": float, "end": float, "reason": str, "type": "silence",
          "original_gap": float, "confidence": float, "action": "remove"}, ...]
    """
    threshold = CONFIG["silence_threshold"] if threshold is None else threshold
    min_gap = CONFIG["min_preserved_gap"] if min_preserved_gap is None else min_preserved_gap

    silence_segments = []
    for i in range(1, len(words)):
        gap = words[i]["start"] - words[i - 1]["end"]
        if gap > threshold:
            # Preserve min_gap at the tail of the outgoing word
            cut_start = words[i - 1]["end"] + min_gap
            cut_end = words[i]["start"]
            if cut_end > cut_start:
                silence_segments.append({
                    "start": cut_start,
                    "end": cut_end,
                    "reason": f"silence ({gap:.2f}s gap, trimmed to {min_gap:.2f}s)",
                    "type": "silence",
                    "original_gap": gap,
                    "confidence": 0.95,
                    "action": "remove",
                })

    return silence_segments


# ============================================================
# FILLER WORD DETECTION
# ============================================================

def _is_filler_in_context(words: list[dict], index: int, filler_text: str) -> bool:
    """Determine if a contextual filler word is being used as filler vs. meaningfully."""
    word = words[index]

    # Sentence-initial filler after a long pause
    if index > 0:
        gap_before = word["start"] - words[index - 1]["end"]
        if gap_before > 0.5 and filler_text in {"so", "well", "like", "basically", "right"}:
            return True

    # Low confidence = more likely filler
    if word.get("confidence", 1.0) < 0.6:
        return True

    # "like" after "was/were/is/am" = almost certainly filler
    if filler_text == "like" and index > 0:
        prev_word = words[index - 1]["text"].lower().strip(".,!?")
        if prev_word in {"was", "were", "is", "am"}:
            return True

    # Surrounded by other fillers → definitely filler
    context_range = 3
    nearby_fillers = 0
    for offset in range(-context_range, context_range + 1):
        if offset == 0:
            continue
        j = index + offset
        if 0 <= j < len(words):
            w = words[j]["text"].lower().strip(".,!?")
            if w in CORE_FILLERS or w in CONTEXTUAL_FILLERS:
                nearby_fillers += 1
    if nearby_fillers >= 2:
        return True

    return False


def detect_fillers(words: list[dict]) -> list[dict]:
    """
    Detect filler words in the transcript.

    Returns:
        [{"start": float, "end": float, "word": str, "reason": str,
          "type": "filler", "confidence": float, "removable": bool,
          "action": "remove"|"keep"}, ...]
    """
    filler_cuts = []

    # Check multi-word fillers first
    multi_word_found = set()
    for phrase in MULTI_WORD_FILLERS:
        phrase_words = phrase.split()
        for i in range(len(words) - len(phrase_words) + 1):
            candidate = " ".join(
                words[i + j]["text"].lower().strip(".,!?")
                for j in range(len(phrase_words))
            )
            if candidate == phrase:
                start = words[i]["start"]
                end = words[i + len(phrase_words) - 1]["end"]
                for idx in range(i, i + len(phrase_words)):
                    multi_word_found.add(idx)
                filler_cuts.append({
                    "start": start,
                    "end": end,
                    "word": phrase,
                    "reason": "multi_word_filler",
                    "type": "filler",
                    "confidence": 0.85,
                    "removable": True,
                    "action": "remove",
                })

    # Check single-word fillers
    for i, word in enumerate(words):
        if i in multi_word_found:
            continue

        text = word["text"].lower().strip(".,!?")

        if text in CORE_FILLERS:
            filler_cuts.append({
                "start": word["start"],
                "end": word["end"],
                "word": text,
                "reason": "core_filler",
                "type": "filler",
                "confidence": 0.95,
                "removable": True,
                "action": "remove",
            })
        elif text in CONTEXTUAL_FILLERS:
            removable = _is_filler_in_context(words, i, text)
            filler_cuts.append({
                "start": word["start"],
                "end": word["end"],
                "word": text,
                "reason": "contextual_filler",
                "type": "filler",
                "confidence": 0.7 if removable else 0.3,
                "removable": removable,
                "action": "remove" if removable else "keep",
            })

    return filler_cuts


def plan_filler_removal(filler: dict, words: list[dict]) -> Optional[dict]:
    """
    Decide whether and how to remove a detected filler word.

    Returns the cut specification or None if it should be kept.
    """
    if not filler.get("removable", False):
        return None

    start = filler["start"]
    end = filler["end"]
    duration = end - start

    # Find adjacent words
    prev_end = None
    next_start = None
    for w in words:
        if w["end"] <= start and (prev_end is None or w["end"] > prev_end):
            prev_end = w["end"]
        if w["start"] >= end and (next_start is None or w["start"] < next_start):
            next_start = w["start"]

    silence_before = (start - prev_end) if prev_end is not None else float("inf")
    silence_after = (next_start - end) if next_start is not None else float("inf")

    # Filler fused to next word — removing would clip
    if silence_after < CONFIG["min_padding_for_filler_cut"]:
        return None

    # Filler fused to previous word
    if silence_before < 0.03:
        return None

    # Calculate replacement silence (keep 35% of filler duration for rhythm)
    replacement_silence = duration * CONFIG["filler_replacement_silence_ratio"]

    return {
        "start": max(0, start - 0.02),  # Include tiny pre-gap, clamp to 0
        "end": end,
        "action": "remove",
        "type": "filler",
        "preserve_silence": replacement_silence,
        "reason": f"filler_word_{filler['word']}",
        "confidence": filler["confidence"],
    }


# ============================================================
# RESTART / RETAKE DETECTION
# ============================================================

def find_explicit_restarts(words: list[dict], phrase: str = None) -> list[dict]:
    """
    Find explicit restart markers ("cut cut") in the transcript.

    Returns:
        [{"type": "explicit_restart", "phrase_start": float, "phrase_end": float,
          "cut_from": float, "cut_to": float, "confidence": float}, ...]
    """
    phrase = phrase or CONFIG["restart_phrase"]
    phrase_words = phrase.lower().split()
    phrase_len = len(phrase_words)
    restarts = []

    for i in range(len(words) - phrase_len + 1):
        match = True
        for j, target_word in enumerate(phrase_words):
            actual = "".join(c for c in words[i + j]["text"].lower() if c.isalnum())
            if actual != target_word:
                match = False
                break

        if match:
            phrase_end = words[i + phrase_len - 1]["end"]
            restarts.append({
                "type": "explicit_restart",
                "phrase_start": words[i]["start"],
                "phrase_end": phrase_end,
                "confidence": 0.95,
            })

    return restarts


def detect_repeated_phrases(
    words: list[dict],
    min_phrase_length: int = None,
    similarity_threshold: float = None,
) -> list[dict]:
    """
    Detect when the speaker says the same thing twice consecutively.

    Uses sliding window text similarity (SequenceMatcher).

    Returns:
        [{"take_a": {"start", "end", "text", "words"}, "take_b": {...},
          "similarity": float, "type": "implicit_retake"}, ...]
    """
    min_len = CONFIG["min_phrase_length"] if min_phrase_length is None else min_phrase_length
    threshold = CONFIG["similarity_threshold"] if similarity_threshold is None else similarity_threshold

    sentences = split_into_sentences(words)
    repeated_sections = []

    for i in range(len(sentences) - 1):
        for j in range(i + 1, min(i + 4, len(sentences))):
            text_a = sentences[i]["text"].lower()
            text_b = sentences[j]["text"].lower()

            if len(text_a.split()) < min_len or len(text_b.split()) < min_len:
                continue

            similarity = SequenceMatcher(None, text_a, text_b).ratio()

            if similarity > threshold:
                repeated_sections.append({
                    "take_a": {
                        "start": sentences[i]["start"],
                        "end": sentences[i]["end"],
                        "text": sentences[i]["text"],
                        "words": sentences[i]["words"],
                    },
                    "take_b": {
                        "start": sentences[j]["start"],
                        "end": sentences[j]["end"],
                        "text": sentences[j]["text"],
                        "words": sentences[j]["words"],
                    },
                    "similarity": similarity,
                    "type": "implicit_retake",
                })

    return repeated_sections


def detect_false_starts(words: list[dict]) -> list[dict]:
    """
    Detect when the speaker starts a sentence, stops, and restarts.
    Pattern: 2-6 words → pause > 0.5s → same first 2-3 words again.

    Returns:
        [{"start": float, "end": float, "text": str,
          "replacement_start": float, "replacement_text": str,
          "type": "false_start", "confidence": float}, ...]
    """
    sentences = split_into_sentences(words)
    false_starts = []

    for i in range(len(sentences) - 1):
        sent_a_words = [w["text"].lower().strip(".,!?") for w in sentences[i]["words"]]
        sent_b_words = [w["text"].lower().strip(".,!?") for w in sentences[i + 1]["words"]]

        # Short fragment followed by a longer version starting with similar words
        if 2 <= len(sent_a_words) < 8 and len(sent_b_words) > len(sent_a_words):
            overlap = 0
            for k in range(min(3, len(sent_a_words), len(sent_b_words))):
                if sent_a_words[k] == sent_b_words[k]:
                    overlap += 1

            if overlap >= 2:
                false_starts.append({
                    "start": sentences[i]["start"],
                    "end": sentences[i]["end"],
                    "text": " ".join(sent_a_words),
                    "replacement_start": sentences[i + 1]["start"],
                    "replacement_text": " ".join(sent_b_words),
                    "type": "false_start",
                    "confidence": 0.85,
                    "action": "remove",
                    "reason": f"false start (restart: '{' '.join(sent_b_words[:4])}...')",
                })

    return false_starts


# ============================================================
# TAKE SELECTION / SCORING
# ============================================================

def score_take(take: dict, words_in_take: list[dict]) -> dict:
    """
    Score a take for quality. Higher = better.

    Scores completeness, fluency, and confidence.
    Recency is NOT part of the score — the caller uses it as a tiebreaker.
    """
    text = " ".join(w["text"] for w in words_in_take)
    word_count = len(words_in_take)

    # 1. Completeness: Does it end with sentence-ending punctuation?
    ends_complete = text.rstrip().endswith((".", "!", "?"))
    completeness_score = 1.0 if ends_complete else 0.4

    # 2. Fluency: Count fillers and long pauses within the take
    filler_count = sum(
        1 for w in words_in_take
        if w["text"].lower().strip(".,!?") in CORE_FILLERS
    )
    filler_rate = filler_count / max(word_count, 1)
    fluency_score = max(0, 1.0 - (filler_rate * 10))

    # Count internal pauses > 0.5s
    long_pauses = 0
    for i in range(1, len(words_in_take)):
        if words_in_take[i]["start"] - words_in_take[i - 1]["end"] > 0.5:
            long_pauses += 1
    fluency_score = max(0, fluency_score - long_pauses * 0.15)

    # 3. Confidence: Average Whisper probability
    avg_confidence = sum(w.get("confidence", 0.8) for w in words_in_take) / max(word_count, 1)

    total = (
        completeness_score * 0.40
        + fluency_score * 0.35
        + avg_confidence * 0.25
    )

    return {
        "score": total,
        "completeness": completeness_score,
        "fluency": fluency_score,
        "confidence": avg_confidence,
        "filler_count": filler_count,
        "long_pauses": long_pauses,
    }


def select_best_take(repeated: dict, words: list[dict]) -> dict:
    """
    Given a repeated_phrases detection, score both takes and pick the best.

    STRONG recency bias: the later take wins UNLESS the earlier take scores
    significantly higher (>0.15 margin). This matches the real-world pattern
    where speakers re-record because they weren't happy with the first take.

    Returns:
        {"keep": take_dict, "cut": take_dict, "scores": {...}}
    """
    take_a = repeated["take_a"]
    take_b = repeated["take_b"]

    words_a = [w for w in words if take_a["start"] <= w["start"] <= take_a["end"]]
    words_b = [w for w in words if take_b["start"] <= w["start"] <= take_b["end"]]

    score_a = score_take(take_a, words_a)
    score_b = score_take(take_b, words_b)

    # Later take (b) wins unless earlier take (a) is CLEARLY better
    # Threshold: earlier must beat later by >0.15 to override recency
    if score_a["score"] > score_b["score"] + 0.15:
        return {"keep": take_a, "cut": take_b, "scores": {"a": score_a, "b": score_b}}
    else:
        return {"keep": take_b, "cut": take_a, "scores": {"a": score_a, "b": score_b}}


def group_and_select_retakes(
    repeated_pairs: list[dict],
    words: list[dict],
) -> list[dict]:
    """
    Group overlapping retake detections and select ONE winner per group.

    When the speaker says the same thing 3+ times, detect_repeated_phrases
    produces multiple pairwise entries (A vs B, A vs C, B vs C). This function
    groups them by overlapping time ranges, finds ALL takes in each group,
    and picks the LATEST take as the winner (unless an earlier take is
    clearly better).

    Returns a flat list of cut segments (the losing takes to remove).
    """
    if not repeated_pairs:
        return []

    # Group takes by the PAIR relationship (union-find), NOT by time overlap.
    #
    # Bug fixed 2026-07: the old code grouped takes by overlapping time
    # ranges — but separate takes of the same line are sequential and never
    # overlap in time, so every take landed in its own group and NO cuts were
    # produced in exactly the common case (a line repeated with a pause
    # between takes). Similarity pairs already tell us which takes belong
    # together; connectivity across pairs is the correct grouping.
    takes_by_key: dict = {}
    parent: dict = {}

    def _key(take: dict) -> float:
        # Round to 10ms to handle float noise in duplicate detections
        return round(take["start"], 2)

    def _find(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    def _union(a, b):
        ra, rb = _find(a), _find(b)
        if ra != rb:
            parent[ra] = rb

    for pair in repeated_pairs:
        for side in ("take_a", "take_b"):
            take = pair[side]
            k = _key(take)
            if k not in takes_by_key or take["end"] > takes_by_key[k]["end"]:
                takes_by_key[k] = take
            if k not in parent:
                parent[k] = k
        _union(_key(pair["take_a"]), _key(pair["take_b"]))

    groups_by_root: dict = {}
    for k, take in takes_by_key.items():
        groups_by_root.setdefault(_find(k), []).append(take)

    # For each connected group, pick the latest take (unless an earlier one
    # is clearly better) and cut the rest.
    cut_segments = []
    for members in groups_by_root.values():
        unique_takes = sorted(members, key=lambda t: t["start"])

        if len(unique_takes) < 2:
            continue

        # Score each take
        scored = []
        for take in unique_takes:
            take_words = [w for w in words if take["start"] <= w["start"] <= take["end"]]
            score = score_take(take, take_words)
            scored.append((take, score))

        # Latest take is the default winner
        latest = scored[-1]

        # Check if any earlier take is CLEARLY better (>0.15 margin)
        best_earlier = max(scored[:-1], key=lambda x: x[1]["score"])
        if best_earlier[1]["score"] > latest[1]["score"] + 0.15:
            winner = best_earlier[0]
        else:
            winner = latest[0]

        # Cut everything except the winner
        for take, score in scored:
            if take["start"] == winner["start"] and take["end"] == winner["end"]:
                continue
            # Never cut a take whose range overlaps the winner (imperfect
            # sentence splits can yield near-duplicate ranges of one take)
            if take["start"] < winner["end"] and take["end"] > winner["start"]:
                continue
            cut_segments.append({
                "start": take["start"],
                "end": take["end"],
                "type": "implicit_retake",
                "reason": f"retake (keeping {'latest' if take != winner else 'best'} version)",
                "confidence": 0.85,
                "action": "remove",
            })

    # Deduplicate cuts by (start, end)
    seen_cuts = set()
    deduped = []
    for cut in cut_segments:
        key = (round(cut["start"], 2), round(cut["end"], 2))
        if key not in seen_cuts:
            seen_cuts.add(key)
            deduped.append(cut)

    return sorted(deduped, key=lambda c: c["start"])


# ============================================================
# CUT PLACEMENT REFINEMENT
# ============================================================

def snap_cut_to_word_boundary(cut_time: float, words: list[dict]) -> float:
    """
    Ensure a cut point doesn't fall inside any word's time range.
    If it does, shift to the nearest word boundary.
    Uses post_word_margin to preserve the tail of the last syllable.
    """
    margin = CONFIG["post_word_margin"]
    for word in words:
        if word["start"] <= cut_time <= word["end"]:
            dist_to_start = cut_time - word["start"]
            dist_to_end = word["end"] - cut_time
            if dist_to_start < dist_to_end:
                return word["start"] - 0.01
            else:
                return word["end"] + margin
    return cut_time


def snap_incoming_to_word_start(time: float, words: list[dict]) -> float:
    """
    Find the next word after a time point and set the incoming clip's
    start to just before that word's transient.
    """
    for word in words:
        if word["start"] >= time:
            return word["start"] - CONFIG["pre_word_margin"]
    return time


def refine_keep_segments(keep_segments: list[dict], words: list[dict]) -> list[dict]:
    """
    Refine cut placement on keep_segments:
    1. Snap segment starts to word transients (25ms pre-roll)
    2. Add tail padding after last word (100ms post_word_margin)
    3. Ensure no word is partially clipped
    4. Validate no segment is too short

    Returns refined keep_segments.
    """
    margin = CONFIG["post_word_margin"]
    refined = []
    for seg in keep_segments:
        start = snap_incoming_to_word_start(seg["start"], words)
        end = snap_cut_to_word_boundary(seg["end"], words)

        # Also ensure the last word in this segment gets tail padding
        # even if the cut didn't land inside a word
        for word in reversed(words):
            if word["end"] <= end and word["end"] > end - 0.30:
                # Last word ends near segment end — ensure margin after it
                end = max(end, word["end"] + margin)
                break

        # Ensure segment is at least 100ms
        if end - start < 0.1:
            continue

        refined.append({
            "start": max(0, start),
            "end": end,
            "reason": seg.get("reason", "content"),
        })

    return refined


# ============================================================
# PACING VALIDATION
# ============================================================

def is_emphasis_moment(words: list[dict], index: int) -> bool:
    """
    Detect if a word is being emphasized based on an unusual pre-pause.
    """
    if index == 0 or index >= len(words):
        return False

    word = words[index]
    prev_word = words[index - 1]
    gap_before = word["start"] - prev_word["end"]

    # Calculate local average gap
    window = 10
    start_idx = max(1, index - window)
    end_idx = min(len(words), index + window)
    local_gaps = []
    for i in range(start_idx, end_idx):
        g = words[i]["start"] - words[i - 1]["end"]
        if 0.01 < g < 2.0:
            local_gaps.append(g)

    avg_gap = sum(local_gaps) / len(local_gaps) if local_gaps else 0.2

    # Pause before this word is 2x+ the local average and > 0.3s
    return gap_before > avg_gap * 2 and gap_before > 0.3


def validate_pacing(keep_segments: list[dict], words: list[dict]) -> list[dict]:
    """
    Check gaps between kept segments and flag issues.

    Returns list of issues:
        [{"type": str, "position": float, "gap": float, "recommendation": str}, ...]
    """
    issues = []
    min_gap = CONFIG["min_gap_between_sentences"]
    max_gap = CONFIG["max_gap_between_sentences"]

    for i in range(1, len(keep_segments)):
        source_gap = keep_segments[i]["start"] - keep_segments[i - 1]["end"]

        if source_gap < 0:
            issues.append({
                "type": "overlapping_segments",
                "position": keep_segments[i]["start"],
                "gap": source_gap,
                "recommendation": "Fix overlapping segment boundaries",
            })
        elif source_gap < min_gap and source_gap >= 0:
            issues.append({
                "type": "too_tight",
                "position": keep_segments[i]["start"],
                "gap": source_gap,
                "recommendation": f"Gap ({source_gap:.3f}s) is below minimum ({min_gap}s)",
            })
        elif source_gap > max_gap:
            issues.append({
                "type": "too_loose",
                "position": keep_segments[i]["start"],
                "gap": source_gap,
                "recommendation": f"Gap ({source_gap:.3f}s) exceeds maximum ({max_gap}s)",
            })

    return issues


def verify_no_clipped_words(keep_segments: list[dict], words: list[dict]) -> list[dict]:
    """
    Verify that no word is partially inside a kept segment.
    Every word should be either fully inside or fully outside.
    """
    issues = []
    for word in words:
        for seg in keep_segments:
            # Word starts before segment but ends inside it
            if word["start"] < seg["start"] < word["end"] <= seg["end"]:
                issues.append({
                    "type": "word_clipped_at_start",
                    "word": word["text"],
                    "time": word["start"],
                    "segment_start": seg["start"],
                })
            # Word starts inside segment but ends after it
            if seg["start"] <= word["start"] < seg["end"] < word["end"]:
                issues.append({
                    "type": "word_clipped_at_end",
                    "word": word["text"],
                    "time": word["start"],
                    "segment_end": seg["end"],
                })
    return issues


def verify_duration_sanity(
    keep_segments: list[dict], original_duration: float
) -> dict:
    """Check that edited duration is in the 35-75% range of original."""
    edited_duration = sum(s["end"] - s["start"] for s in keep_segments)
    ratio = edited_duration / original_duration if original_duration > 0 else 1.0

    if ratio < CONFIG["min_compression_ratio"]:
        return {
            "warning": f"OVER-CUT: Edited video is {ratio:.1%} of original (< {CONFIG['min_compression_ratio']:.0%}). Review cuts for false positives.",
            "ratio": ratio,
        }
    elif ratio > CONFIG["max_compression_ratio"]:
        return {
            "warning": f"UNDER-CUT: Edited video is {ratio:.1%} of original (> {CONFIG['max_compression_ratio']:.0%}). Review for missed cuts.",
            "ratio": ratio,
        }
    else:
        return {"ok": True, "ratio": ratio}


# ============================================================
# INTRO HOOK FINDER
# ============================================================

def find_intro_hook(words: list[dict], max_search_seconds: float = 120.0) -> Optional[float]:
    """
    Find the optimal swivel insertion point by detecting intro hook phrases.

    Returns timestamp (end of the matching phrase) or None if no clear hook found.
    """
    # Build text from first N seconds
    early_words = [w for w in words if w["start"] < max_search_seconds]
    if not early_words:
        return None

    full_text = " ".join(w["text"].lower() for w in early_words)

    for phrase in INTRO_HOOK_PHRASES:
        idx = full_text.find(phrase)
        if idx >= 0:
            # Find the word that corresponds to the end of this phrase
            char_count = 0
            for i, w in enumerate(early_words):
                if i > 0:
                    char_count += 1  # space before this word (not before first word)
                char_count += len(w["text"])
                if char_count >= idx + len(phrase):
                    return w["end"]

    # Fallback: first major pause (>0.5s) after 10 seconds
    for i in range(1, len(early_words)):
        if early_words[i]["start"] > 10.0:
            gap = early_words[i]["start"] - early_words[i - 1]["end"]
            if gap > 0.5:
                return early_words[i - 1]["end"]

    return None


# ============================================================
# CUT LIST ↔ KEEP LIST CONVERSION
# ============================================================

def combine_cuts(*cut_lists: list[dict]) -> list[dict]:
    """Combine multiple cut lists, sorted by start time."""
    all_cuts = []
    for cut_list in cut_lists:
        all_cuts.extend(cut_list)
    return sorted(all_cuts, key=lambda c: c["start"])


def invert_cuts_to_keep_list(cuts: list[dict], total_duration: float) -> list[dict]:
    """
    Convert a list of cut segments into a list of keep segments.
    Only inverts "remove" actions — "silence" and "reduce_volume" actions
    don't remove time and are handled separately.
    """
    # Filter to only time-removing cuts
    removal_cuts = [c for c in cuts if c.get("action") == "remove"]
    sorted_cuts = sorted(removal_cuts, key=lambda c: c["start"])

    # Merge overlapping cuts
    merged = []
    for cut in sorted_cuts:
        if merged and cut["start"] <= merged[-1]["end"]:
            merged[-1]["end"] = max(merged[-1]["end"], cut["end"])
        else:
            merged.append({"start": cut["start"], "end": cut["end"]})

    # Build keep segments (inverse of merged cuts)
    keeps = []
    current_start = 0.0

    for cut in merged:
        if cut["start"] > current_start:
            keeps.append({
                "start": current_start,
                "end": cut["start"],
                "reason": "content",
            })
        current_start = cut["end"]

    # Don't forget the last segment
    if current_start < total_duration:
        keeps.append({
            "start": current_start,
            "end": total_duration,
            "reason": "content",
        })

    return keeps


def extract_audio_modifications(cuts: list[dict]) -> list[dict]:
    """
    Extract audio modification actions (silence, reduce_volume) from the cut list.
    These modify audio in-place WITHOUT removing time.
    """
    return [
        c for c in cuts
        if c.get("action") in ("silence", "reduce_volume")
    ]


# ============================================================
# MANIFEST BUILDER
# ============================================================

def build_edit_manifest(
    source_video: str,
    source_duration: float,
    keep_segments: list[dict],
    cut_segments: list[dict],
    audio_modifications: list[dict],
    speaker_cadence: dict,
    swivel_insert_at: Optional[float] = None,
) -> dict:
    """Build the standardized edit manifest JSON structure (v2.0)."""
    # Compute metadata
    estimated_output = sum(s["end"] - s["start"] for s in keep_segments)
    compression_ratio = estimated_output / source_duration if source_duration > 0 else 1.0

    retakes = sum(1 for c in cut_segments if c.get("type") in ("retake", "implicit_retake", "explicit_restart"))
    fillers = sum(1 for c in cut_segments if c.get("type") == "filler")
    false_starts = sum(1 for c in cut_segments if c.get("type") == "false_start")
    wispr = sum(1 for c in cut_segments if c.get("type") == "wispr_flow")
    breaths_silenced = sum(1 for m in audio_modifications if m.get("action") == "silence")
    breaths_reduced = sum(1 for m in audio_modifications if m.get("action") == "reduce_volume")
    silence_removed = sum(c["end"] - c["start"] for c in cut_segments if c.get("type") == "silence")

    return {
        "version": "2.0",
        "source_video": source_video,
        "source_duration": source_duration,
        "speaker_cadence": speaker_cadence,
        "keep_segments": keep_segments,
        "cut_segments": cut_segments,
        "audio_modifications": audio_modifications,
        "micro_fades": True,
        "micro_fade_duration": CONFIG["micro_fade_duration"],
        "swivel_insert_at": swivel_insert_at,
        "metadata": {
            "total_cuts": len(cut_segments),
            "retakes_removed": retakes,
            "fillers_removed": fillers,
            "false_starts_removed": false_starts,
            "breaths_silenced": breaths_silenced,
            "breaths_reduced": breaths_reduced,
            "wispr_zones_cut": wispr,
            "silence_removed_seconds": round(silence_removed, 1),
            "estimated_output_duration": round(estimated_output, 1),
            "compression_ratio": round(compression_ratio, 3),
        },
    }


def save_manifest(manifest: dict, output_path: str) -> None:
    """Save manifest to JSON file."""
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"   Manifest saved to {output_path}")


def load_manifest(manifest_path: str) -> dict:
    """Load and return manifest from JSON file."""
    with open(manifest_path, "r") as f:
        return json.load(f)
