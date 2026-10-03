"""Narration-driven scenes.

A scene speaks with

    with self.voice("One sentence of narration."):
        self.play(...)          # animations that go with that sentence

The block lasts as long as the sentence takes to say: the measured length of
audio/<id>.wav if tts.py has generated it, otherwise an estimate from the word
count. Each scene writes its timings to media/timing/<Scene>.json, which
tts.py uses to place the audio clips and build the subtitles.
"""
import hashlib
import json
from contextlib import contextmanager
from pathlib import Path

from manim import MovingCameraScene

HERE = Path(__file__).resolve().parent
DURATIONS = HERE / "audio" / "durations.json"
TIMING_DIR = HERE / "media" / "timing"

GAP = 0.5               # pause after each sentence, seconds
WORDS_PER_SECOND = 2.6  # used only when there is no audio yet


def text_hash(text):
    return hashlib.sha1(text.encode()).hexdigest()[:12]


def estimate(text):
    return max(1.5, len(text.split()) / WORDS_PER_SECOND + 0.4)


class Narrated(MovingCameraScene):
    def setup(self):
        super().setup()
        self._segments = []
        self._known = json.loads(DURATIONS.read_text()) if DURATIONS.exists() else {}

    @contextmanager
    def voice(self, text):
        sid = f"{type(self).__name__}_{len(self._segments):02d}"
        known = self._known.get(sid)
        duration = known["duration"] if known and known["hash"] == text_hash(text) else estimate(text)
        start = self.renderer.time
        self.add_subcaption(text, duration=duration)
        self._segments.append({"id": sid, "text": text, "start": round(start, 3), "duration": round(duration, 3)})
        yield duration
        remaining = start + duration + GAP - self.renderer.time
        if remaining > 1e-3:
            self.wait(remaining)

    def tear_down(self):
        TIMING_DIR.mkdir(parents=True, exist_ok=True)
        (TIMING_DIR / f"{type(self).__name__}.json").write_text(json.dumps(self._segments, indent=1))
        super().tear_down()
