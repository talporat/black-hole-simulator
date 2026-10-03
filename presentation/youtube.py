#!/usr/bin/env python3
"""Writes everything needed to upload the series, into youtube/:

    epN_description.txt   title, description with chapters, tags
    epN_thumbnail.jpg     1280x720 thumbnail
    epN_captions.srt      copy of blackhole_epN.srt

Chapter times are read from the rendered episodes, so run this after ./make.sh.
Put the code's URL in REPO_URL before uploading.
"""
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "youtube"
REPO_URL = "https://github.com/talporat/black-hole-simulator"
SERIES = "Building a Black Hole Simulator"
FONT = "/System/Library/Fonts/Avenir Next.ttc"
HEAVY, DEMI = 8, 2

CREDITS = """Credits
- Narration: AI-generated voice (Chatterbox, open source).
- Music: synthesised in code for this series.
- Animations: Manim Community Edition. Black hole renders: the C++/OpenGL simulator built in this series.
- Portraits (public domain, Wikimedia Commons): Isaac Newton (Godfrey Kneller, 1689), Albert Einstein \
(Ferdinand Schmutzer, 1921), Karl Schwarzschild, William Rowan Hamilton, Leonhard Euler (Jakob Emanuel \
Handmann, 1753), Christian Doppler."""

TAGS = ("black hole, ray tracing, general relativity, OpenGL, C++, GLSL, shaders, physics simulation, "
        "gravitational lensing, Schwarzschild, Einstein, programming tutorial, computer graphics, physics explained")

EPISODES = {
    "ep1": {
        "title": f"Why Light Bends Around a Black Hole | {SERIES}, Part 1",
        "pitch": "Light has no mass, so why does gravity bend it? In this first part we go from Newton and "
                 "Pythagoras to the two equations that tell light how to move near a black hole. Those two "
                 "equations are all our simulator will need.",
        "learn": ["Why massless light still bends, and what Einstein changed",
                  "What a metric is, built up from Pythagoras",
                  "The event horizon, the photon sphere and the innermost stable orbit",
                  "Hamilton's equations, explained with a thrown ball",
                  "A form of the equations a computer can use without dividing by zero"],
        "chapters": [("E1_01_Hook", 0, "Intro"), ("E1_02_WhyLightBends", 0, "Why does light bend?"),
                     ("E1_02_WhyLightBends", 6, "From Pythagoras to the metric"),
                     ("E1_02_WhyLightBends", 13, "Three distances that matter"),
                     ("E1_03_TwoRules", 0, "How light moves: two rules"),
                     ("E1_04_Formula", 0, "A formula a computer can use"),
                     ("E1_05_Next", 0, "Recap and what's next")],
        "background": ("footage", "hook_3", 110), "words": ["WHY LIGHT", "BENDS"],
        "code": None,
    },
    "ep2": {
        "title": f"Bending Light in 200 Lines of C++ and OpenGL | {SERIES}, Part 2",
        "pitch": "We turn the two equations from part 1 into a real program: light rays traced step by step "
                 "around a black hole, and drawn with OpenGL from scratch. Every line of code is shown next to "
                 "the maths it comes from.",
        "learn": ["Writing the equations of motion for light in C++",
                  "Solving H = 0 with the quadratic formula",
                  "Why Runge-Kutta 4 beats Euler's method",
                  "OpenGL from zero: a window, two shaders, vertex buffers and draw calls",
                  "Finding the black hole's shadow at 5.2 M"],
        "chapters": [("E2_01_Recap", 0, "Recap"), ("E2_02_Plan", 0, "The plan: physics plus OpenGL"),
                     ("E2_03_CodePhysics", 0, "Code: vectors and the two rules"),
                     ("E2_03_CodePhysics", 9, "Solving H = 0 with the quadratic formula"),
                     ("E2_03_CodePhysics", 12, "Euler vs Runge-Kutta 4"),
                     ("E2_03_CodePhysics", 17, "Following a ray"),
                     ("E2_04_CodeOpenGL", 0, "OpenGL: opening a window"),
                     ("E2_04_CodeOpenGL", 3, "Vertex and fragment shaders"),
                     ("E2_04_CodeOpenGL", 10, "Compiling shaders"),
                     ("E2_04_CodeOpenGL", 13, "Vertex buffers"),
                     ("E2_04_CodeOpenGL", 15, "Drawing lines and shapes"),
                     ("E2_04_CodeOpenGL", 19, "The main loop"),
                     ("E2_05_Result", 0, "The program running"),
                     ("E2_05_Result", 4, "The black hole's shadow")],
        "background": ("asset", "stage1.jpg", None), "words": ["200 LINES", "OF C++"],
        "code": "stages/01_rays_2d",
    },
    "ep3": {
        "title": f"Ray Tracing a Black Hole on the GPU | {SERIES}, Part 3",
        "pitch": "One ray of light for every pixel, a few hundred steps each, sixty times a second. We move "
                 "the physics into a GLSL fragment shader and fly a camera around the black hole in real time.",
        "learn": ["How a ray tracer makes a picture, and why a black hole breaks it",
                  "Why this needs the graphics card",
                  "Covering the screen with a single triangle",
                  "Porting the physics from C++ to GLSL",
                  "Building a camera from two angles and cross products",
                  "Reading the result: the shadow and the lensed sky"],
        "chapters": [("E3_01_Recap", 0, "Recap"), ("E3_02_RayTracing", 0, "How a ray tracer works"),
                     ("E3_03_WhyGPU", 0, "Why the graphics card?"),
                     ("E3_04_Triangle", 0, "One triangle to cover the screen"),
                     ("E3_05_Port", 0, "Moving the physics into a shader"),
                     ("E3_06_Camera", 0, "The camera"), ("E3_06_Camera", 7, "One ray per pixel"),
                     ("E3_07_Loop", 0, "The tracing loop"), ("E3_07_Loop", 5, "Painting the sky"),
                     ("E3_08_Result", 0, "The result")],
        "background": ("asset", "stage2.jpg", None), "words": ["RAY TRACING", "ON THE GPU"],
        "code": "stages/02_raytracer_3d",
    },
    "ep4": {
        "title": f"The Glowing Disk: Doppler, Redshift and Tone Mapping | {SERIES}, Part 4",
        "pitch": "We give the black hole a disk of hot gas orbiting at half the speed of light, and explain "
                 "the two most famous features of a black hole image: the halo, and the lopsided glow.",
        "learn": ["Why one flat disk shows up three times",
                  "Finding where a ray crosses the disk",
                  "Orbital speed from centripetal force and gravity",
                  "Doppler shift and gravitational redshift in one number",
                  "Floating-point textures, framebuffers and tone mapping in OpenGL"],
        "chapters": [("E4_01_Recap", 0, "Recap"), ("E4_02_ThreeImages", 0, "One disk, three images"),
                     ("E4_03_CodeCrossing", 0, "Did the ray hit the disk?"),
                     ("E4_04_Rotation", 0, "How fast does the gas orbit?"),
                     ("E4_04_Rotation", 5, "The spinning disk in the shader"),
                     ("E4_05_Doppler", 0, "Doppler shift and redshift"),
                     ("E4_05_Doppler", 4, "Colour in the shader"), ("E4_05_Doppler", 8, "Why hot gas glows"),
                     ("E4_06_Brightness", 0, "Too bright for the screen"),
                     ("E4_06_Brightness", 2, "Textures and framebuffers"),
                     ("E4_06_Brightness", 6, "Tone mapping"), ("E4_07_Result", 0, "The final result")],
        "background": ("footage", "hook_1", 200), "words": ["THE GLOWING", "DISK"],
        "code": "stages/03_disk",
    },
}


def scene_offsets(ep):
    """Start time of every scene in the finished episode."""
    offsets, t = {}, 0.0
    for line in (HERE / "media" / f"concat_{ep}.txt").read_text().splitlines():
        clip = HERE / "media" / line.split("'")[1]
        offsets[clip.stem] = t
        t += float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                            "-of", "csv=p=0", str(clip)]))
    return offsets, t


def chapters(ep, spec):
    offsets, total = scene_offsets(ep)
    lines, last = [], -999
    for scene, index, title in spec:
        start = 0 if not lines else offsets[scene] + json.loads(
            (HERE / "media" / "timing" / f"{scene}.json").read_text())[index]["start"]
        assert start - last >= 10, f"{ep}: chapter '{title}' is under 10 s after the previous one"
        last = start
        s = int(start)
        lines.append(f"{s // 60}:{s % 60:02d} {title}")
    return lines, total


def thumbnail(ep, info):
    kind, name, frame = info["background"]
    path = HERE / "footage" / name / f"{frame:04d}.jpg" if kind == "footage" else HERE / "assets" / name
    src = Image.open(path).convert("RGB").resize((1280, 720), Image.LANCZOS)
    # Move the black hole to the right third, clear of the words; mirror the left edge to fill the gap.
    shift = 320
    img = Image.new("RGB", (1280, 720))
    img.paste(src, (shift, 0))
    img.paste(src.crop((0, 0, shift, 720)).transpose(Image.FLIP_LEFT_RIGHT), (0, 0))
    img = ImageEnhance.Contrast(ImageEnhance.Brightness(img).enhance(0.95)).enhance(1.1)
    # Darken the left side so the words read clearly.
    shade = Image.new("L", (1280, 720))
    ImageDraw.Draw(shade).rectangle([0, 0, 1280, 720], fill=0)
    for x in range(1280):
        ImageDraw.Draw(shade).line([(x, 0), (x, 720)], fill=int(205 * max(0.0, 1 - x / 820) ** 1.4))
    img = Image.composite(Image.new("RGB", img.size, (0, 0, 0)), img, shade)

    draw = ImageDraw.Draw(img)
    big = ImageFont.truetype(FONT, 118, index=HEAVY)
    small = ImageFont.truetype(FONT, 40, index=DEMI)
    y = 360 - 75 * len(info["words"])
    for word in info["words"]:
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((64, y + 6), word, font=big, fill=(0, 0, 0, 200))
        img.paste(layer.filter(ImageFilter.GaussianBlur(8)), (0, 0), layer.filter(ImageFilter.GaussianBlur(8)))
        draw = ImageDraw.Draw(img)
        draw.text((60, y), word, font=big, fill=(255, 255, 255))
        y += 140
    badge = f"PART {ep[-1]}"
    w = draw.textlength(badge, font=small)
    draw.rounded_rectangle([60, 62, 60 + w + 44, 62 + 64], radius=14, fill=(255, 180, 84))
    draw.text((82, 68), badge, font=small, fill=(12, 15, 22))
    draw.text((60, 630), "C++  ·  OpenGL  ·  general relativity", font=ImageFont.truetype(FONT, 34, index=DEMI),
              fill=(255, 224, 102))
    out = OUT / f"{ep}_thumbnail.jpg"
    img.save(out, quality=90)
    return out


def description(ep, info, chapter_lines):
    others = [f"Part {e[-1]}: {EPISODES[e]['title'].split(' | ')[0]}" for e in EPISODES if e != ep]
    code = (f"The code for this part: {REPO_URL} (folder {info['code']}).\n"
            if info["code"] else f"All the code for the series: {REPO_URL}\n")
    return "\n".join([
        info["title"], "", "-" * 60, "",
        info["pitch"], "",
        "In this video:", *[f"- {item}" for item in info["learn"]], "",
        code.rstrip(), "",
        "Chapters", *chapter_lines, "",
        f"The series ({SERIES}):", *[f"- {o}" for o in others], "",
        CREDITS, "",
        "Tags: " + TAGS, "",
    ])


def main():
    OUT.mkdir(exist_ok=True)
    for ep, info in EPISODES.items():
        lines, total = chapters(ep, info["chapters"])
        text = description(ep, info, lines)
        (OUT / f"{ep}_description.txt").write_text(text)
        thumbnail(ep, info)
        shutil.copy(HERE / f"blackhole_{ep}.srt", OUT / f"{ep}_captions.srt")
        print(f"{ep}: {len(lines)} chapters, {total / 60:.1f} min, title {len(info['title'])} chars")


if __name__ == "__main__":
    main()
