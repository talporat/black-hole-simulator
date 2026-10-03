"""Shared building blocks for the episodes (ep1.py, ep2.py, ep3.py).

Narration lives next to the animation it describes, as self.voice("...")
blocks (see narration.py). Build with ./make.sh, or preview one scene with
    manim -ql ep1.py E1_06_CodePhysics
"""
import subprocess
from pathlib import Path

import numpy as np
from manim import *
from PIL import Image

import geodesics as geo
from narration import Narrated

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ASSETS = HERE / "assets"
FOOTAGE = HERE / "footage"

BG = "#0c0f16"
PANEL = "#151a24"
INK = "#e6e9ef"
MUTED = "#8a93a6"
ACCENT = "#ffb454"
COOL = "#5cc8ff"
HOT = "#ff5f6d"
GOOD = "#7ee787"
GOLD = "#ffe066"

config.background_color = BG
Text.set_default(font="Avenir Next", color=INK)
MathTex.set_default(color=INK)


# ---------------------------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------------------------

def T(text, size=28, color=INK, weight=NORMAL, **kw):
    return Text(text, font_size=size, color=color, weight=weight, **kw)


def excerpt(path, *ranges, skip=()):
    """Lines of a source file, dedented. Each range is (first, last): substrings
    identifying its first and last line (a bare closing brace must match the
    whole line). Several ranges are joined by an elision comment."""
    src = (ROOT / path).read_text().split("\n")

    def matches(line, marker):
        return line == marker if marker.strip() == "}" else marker in line

    out = []
    for k, (first, last) in enumerate(ranges):
        a = next(i for i, l in enumerate(src) if first in l)
        b = next(i for i in range(a, len(src)) if matches(src[i], last))
        chunk = [l for l in src[a:b + 1] if not any(m in l for m in skip)]
        if k:
            out.append(" " * (len(chunk[0]) - len(chunk[0].lstrip())) + "// ...")
        out += chunk
    indent = min(len(l) - len(l.lstrip()) for l in out if l.strip())
    return "\n".join(l[indent:] for l in out)


class CodePanel(VGroup):
    """A source listing with a file tab and a movable highlight."""

    def __init__(self, text, filename, language="glsl", font_size=20, max_width=8.0, max_height=6.2):
        super().__init__()
        self.text = text.split("\n")
        self.code = Code(
            code_string=text, language=language, formatter_style="one-dark", add_line_numbers=False,
            background="rectangle",
            background_config={"fill_color": PANEL, "stroke_color": "#2b3345", "stroke_width": 1.5,
                               "buff": 0.3, "corner_radius": 0.12},
            paragraph_config={"font": "Menlo", "font_size": font_size},
        )
        # Size by character width so short snippets are not blown up and long ones still fit.
        longest = max(len(l) for l in self.text)
        self.code.scale_to_fit_width(min(max_width, 0.6 + 0.125 * longest))
        if self.code.height > max_height:
            self.code.scale_to_fit_height(max_height)
        self.lines = self.code.code_lines
        self.tab = Text(filename, font="Menlo", font_size=17, color=MUTED)
        self.tab.next_to(self.code, UP, buff=0.12, aligned_edge=LEFT).shift(RIGHT * 0.1)
        self.bar = None
        self.add(self.code, self.tab)

    def find(self, needle, after=1):
        return next(i + 1 for i, l in enumerate(self.text) if i + 1 >= after and needle in l)

    def _row_y(self, i):
        filled = [k for k, l in enumerate(self.lines) if len(l)]
        a, b = filled[0], filled[-1]
        ya, yb = self.lines[a].get_center()[1], self.lines[b].get_center()[1]
        pitch = (ya - yb) / max(b - a, 1)
        return ya - (i - 1 - a) * pitch, pitch

    def focus(self, first, last=None):
        """Animations that light up lines first..last (1-based, or substrings) and dim the rest."""
        a = self.find(first) if isinstance(first, str) else first
        b = a if last is None else (self.find(last, after=a) if isinstance(last, str) else last)
        ya, pitch = self._row_y(a)
        yb, _ = self._row_y(b)
        bg = self.code.submobjects[0]
        bar = RoundedRectangle(width=bg.width - 0.16, height=abs(pitch) * (b - a + 1) + 0.06, corner_radius=0.06,
                               fill_color=ACCENT, fill_opacity=0.14, stroke_color=ACCENT, stroke_width=1.2)
        bar.move_to([bg.get_center()[0], (ya + yb) / 2, 0])
        anims = [l.animate.set_opacity(1.0 if a <= i + 1 <= b else 0.45) for i, l in enumerate(self.lines) if len(l)]
        if self.bar is None:
            anims.append(FadeIn(bar))
            self.add(bar)
        else:
            anims.append(Transform(self.bar, bar))
            bar = self.bar
        self.bar = bar
        return AnimationGroup(*anims)

    def rows(self, first, last=None):
        a = self.find(first) if isinstance(first, str) else first
        b = a if last is None else (self.find(last, after=a) if isinstance(last, str) else last)
        return VGroup(*[self.lines[i] for i in range(a - 1, b)])

    def unfocus(self):
        anims = [l.animate.set_opacity(1.0) for l in self.lines if len(l)]
        if self.bar is not None:
            anims.append(FadeOut(self.bar))
            self.remove(self.bar)
            self.bar = None
        return AnimationGroup(*anims)


class Footage(ImageMobject):
    """Plays a numbered JPEG sequence (footage/<name>/NNNN.jpg), back and forth unless loop=False."""

    def __init__(self, name, fps=30, loop=True, span=None, **kw):
        self.paths = sorted((FOOTAGE / name).glob("*.jpg"))
        self.fps = fps
        self.loop = loop  # False: play once and hold the last frame
        self.span = span  # seconds: play the whole clip once over exactly this long
        self.clock = 0.0
        super().__init__(self._frame(0), **kw)
        self.add_updater(self._tick)

    def _frame(self, i):
        return np.array(Image.open(self.paths[i]).convert("RGBA"))

    def _tick(self, mob, dt):
        self.clock += dt
        n = len(self.paths)
        if self.span:
            k = min(int(self.clock / self.span * (n - 1)), n - 1)
        else:
            k = int(self.clock * self.fps)
            k = k % (2 * n - 2) if self.loop else min(k, n - 1)
        self.pixel_array = self._frame(k if k < n else 2 * n - 2 - k)


def to_scene(points, scale, origin):
    return np.array([origin + scale * np.array([q[0], q[1], 0.0]) for q in points])


def ray_path(points, scale, origin, color=INK, width=3, box=None):
    """Polyline through geodesic points (units of M) mapped into the scene.
    box = (xmin, xmax, ymin, ymax) keeps only the first stretch inside it."""
    pts = to_scene(points, scale, origin)
    if box is not None:
        inside = (pts[:, 0] > box[0]) & (pts[:, 0] < box[1]) & (pts[:, 1] > box[2]) & (pts[:, 1] < box[3])
        first = int(np.argmax(inside))
        rest = inside[first:]
        last = first + (int(np.argmin(rest)) if not rest.all() else len(rest))
        pts = pts[first:max(last, first + 2)]
    return VMobject(stroke_color=color, stroke_width=width).set_points_as_corners(pts)


def glow(path, strength=1.0):
    """The path with two soft, wider copies behind it."""
    w = path.get_stroke_width()
    return VGroup(path.copy().set_stroke(width=w * 5, opacity=0.10 * strength),
                  path.copy().set_stroke(width=w * 2.5, opacity=0.22 * strength), path)


def black_hole(scale, origin):
    return VGroup(
        Circle(radius=2 * scale * 1.35, stroke_width=0, fill_color=ACCENT, fill_opacity=0.10),
        Circle(radius=2 * scale, stroke_color=ACCENT, stroke_width=2, fill_color=BLACK, fill_opacity=1),
    ).move_to(origin)


def note(tex, color=INK, size=34):
    return MathTex(tex, font_size=size, color=color)


class Video(Narrated):
    def tag(self, text):
        dot = Dot(radius=0.06, color=ACCENT)
        label = T(text, 20, MUTED, weight=MEDIUM)
        group = VGroup(dot, label).arrange(RIGHT, buff=0.15).to_corner(UL, buff=0.35)
        self.play(FadeIn(group, shift=RIGHT * 0.2), run_time=0.5)
        return group

    def chapter(self, part, title):
        num = T(part, 26, ACCENT, weight=BOLD)
        name = T(title, 60, weight=BOLD)
        line = Line(LEFT * 1.2, RIGHT * 1.2, color=ACCENT, stroke_width=3)
        card = VGroup(num, name, line).arrange(DOWN, buff=0.35)
        self.play(FadeIn(num, shift=UP * 0.2), Write(name), GrowFromCenter(line), run_time=1.0)
        self.wait(1.0)
        self.play(FadeOut(card, shift=UP * 0.3), run_time=0.5)

    def clear(self, run_time=0.6):
        mobs = [m for m in self.mobjects if m is not self.camera.frame]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)


def card(text, color=INK, size=24):
    """A labelled box for flow diagrams."""
    label = T(text, size, color, weight=SEMIBOLD, line_spacing=0.8)
    frame = RoundedRectangle(width=label.width + 0.6, height=label.height + 0.5, corner_radius=0.14,
                             stroke_color=color, stroke_width=2.5, fill_color=PANEL, fill_opacity=1)
    return VGroup(frame, label)


def flow(*cards, buff=0.7):
    """Cards in a row with arrows between them. Returns (row, arrows)."""
    row = VGroup(*cards).arrange(RIGHT, buff=buff)
    arrows = VGroup(*[Arrow(a.get_right(), b.get_left(), buff=0.08, color=MUTED, stroke_width=4,
                            max_tip_length_to_length_ratio=0.35) for a, b in zip(cards, cards[1:])])
    return row, arrows


def step_dots(points, scale, origin, color, box=None, radius=0.05):
    """A geodesic as a polyline plus one dot per integration step."""
    pts = to_scene(points, scale, origin)
    if box is not None:
        pts = np.array([q for q in pts if box[0] < q[0] < box[1] and box[2] < q[1] < box[3]])
    line = VMobject(stroke_color=color, stroke_width=2.5).set_points_as_corners(pts)
    return line, VGroup(*[Dot(q, radius=radius, color=color) for q in pts])


def portrait(key, name, years, height=2.0, label_side=DOWN):
    """A framed picture of a scientist (assets/people/<key>.jpg, all public domain) with name and dates."""
    img = ImageMobject(str(ASSETS / "people" / f"{key}.jpg")).scale_to_fit_height(height)
    frame = SurroundingRectangle(img, color=ACCENT, buff=0, stroke_width=2.5)
    label = VGroup(T(name, 20, weight=SEMIBOLD), T(years, 16, MUTED))
    label.arrange(DOWN, buff=0.06, aligned_edge=LEFT if label_side is RIGHT else ORIGIN).next_to(img, label_side, buff=0.15)
    back = BackgroundRectangle(label, color=BG, fill_opacity=0.85, buff=0.08)
    return Group(img, frame, back, label)
