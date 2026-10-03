#!/usr/bin/env python3
"""Narration tooling for the video.

    tts.py extract            ep*.py -> narration.json (every sentence, in order)
    tts.py setup              download the Kokoro voice model (about 350 MB) into tts_models/
    tts.py speak [options]    one audio clip per sentence -> audio/<id>.wav + audio/durations.json
    tts.py mux ep1            place the clips on the rendered episode -> blackhole_ep1.mp4, .srt, script_ep1.md

speak has two built-in engines: "kokoro", a neural voice that runs locally
(the default once `setup` has been run), and "say", the macOS system voice.
To use any other TTS, pass a command template; it is run once per sentence
and must write an audio file:

    tts.py speak --cmd 'my-tts --text {text} --out {out}' --ext mp3

Sentences whose text has not changed are not regenerated. After speak, render
again (./make.sh does this) so every scene is timed to the real audio.
"""
import argparse
import ast
import json
import re
import shlex
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

from narration import GAP, estimate, text_hash

HERE = Path(__file__).resolve().parent
AUDIO = HERE / "audio"
MODELS = HERE / "tts_models"
KOKORO_FILES = ("kokoro-v1.0.onnx", "voices-v1.0.bin")
KOKORO_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
RATE = 44100


def setup():
    import urllib.request
    MODELS.mkdir(exist_ok=True)
    for name in KOKORO_FILES:
        if not (MODELS / name).exists():
            print("downloading", name)
            urllib.request.urlretrieve(KOKORO_URL + name, MODELS / name)
    print("Kokoro model ready in", MODELS)


def chatterbox_ready():
    return (HERE / ".venv-tts" / "bin" / "python").exists() and (HERE / "voice_ref" / "fable.wav").exists()


def kokoro_ready():
    return all((MODELS / name).exists() for name in KOKORO_FILES)


def episodes():
    return sorted(p.stem for p in HERE.glob("ep[0-9]*.py"))


def extract():
    """Every self.voice("...") in the episode files, in order, with the ids narration.py assigns."""
    segments = []
    for episode in episodes():
        tree = ast.parse((HERE / f"{episode}.py").read_text())
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            calls = [n for n in ast.walk(cls)
                     if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "voice"]
            calls.sort(key=lambda n: (n.lineno, n.col_offset))
            for i, call in enumerate(calls):
                arg = call.args[0]
                if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
                    sys.exit(f"{episode}.py:{call.lineno}: self.voice() needs a plain string")
                segments.append({"id": f"{cls.name}_{i:02d}", "episode": episode, "scene": cls.name, "text": arg.value})
    (HERE / "narration.json").write_text(json.dumps(segments, indent=1))
    return segments


ONES = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
        "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def two_digits(n):
    return ONES[n] if n < 20 else (TENS[n // 10] + (" " + ONES[n % 10] if n % 10 else ""))


def year_words(match):
    """1919 -> nineteen nineteen, 1905 -> nineteen oh five, 2000 -> two thousand, 2015 -> twenty fifteen."""
    year = int(match.group())
    high, low = divmod(year, 100)
    if 2000 <= year <= 2009:
        return "two thousand" + (" and " + ONES[low] if low else "")
    if low == 0:
        return two_digits(high) + " hundred"
    return two_digits(high) + (" oh " + ONES[low] if low < 10 else " " + two_digits(low))


def spoken(text):
    """The text as the voice should say it. Subtitles and the script keep the original."""
    return re.sub(r"\b(1[0-9]{3}|20[0-9]{2})\b", year_words, text).replace("3D", "three D")


def clip_seconds(path):
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


def chatterbox_batch(segments, table, speaker, voice, args):
    """Generate every out-of-date clip with Chatterbox in one run of chatterbox_worker.py
    (the model takes a while to load, so all sentences go through a single process)."""
    python = HERE / ".venv-tts" / "bin" / "python"
    reference = HERE / "voice_ref" / f"{voice}.wav"
    if not python.exists() or not reference.exists():
        sys.exit("chatterbox needs .venv-tts (pip install chatterbox-tts) and voice_ref/<voice>.wav")
    todo = []
    for seg in segments:
        old = table.get(seg["id"], {})
        fresh = old.get("hash") == text_hash(seg["text"]) and old.get("speaker") == speaker
        if not ((AUDIO / f"{seg['id']}.wav").exists() and fresh) or args.force:
            todo.append(seg)
    if not todo:
        return
    job = HERE / "media" / "chatterbox_job.json"
    job.parent.mkdir(exist_ok=True)
    job.write_text(json.dumps({"reference": str(reference), "exaggeration": args.exaggeration, "cfg_weight": args.cfg_weight,
                               "items": [{"id": s["id"], "text": spoken(s["text"]), "out": str(AUDIO / f"{s['id']}.cb.wav")}
                                         for s in todo]}))
    subprocess.run([str(python), str(HERE / "chatterbox_worker.py"), str(job)], check=True)
    checks = json.loads(Path(str(job) + ".result.json").read_text())
    for seg in todo:
        raw, out = AUDIO / f"{seg['id']}.cb.wav", AUDIO / f"{seg['id']}.wav"
        before = table.get(seg["id"], {}).get("duration")
        # atempo slows the speech slightly without changing its pitch.
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"atempo={args.tempo}", "-ac", "1",
                        "-ar", str(RATE), "-sample_fmt", "s16", str(out)], check=True)
        raw.unlink()
        seconds = round(clip_seconds(out), 3)
        table[seg["id"]] = {"hash": text_hash(seg["text"]), "speaker": speaker, "spoken": spoken(seg["text"]), "duration": seconds}
        # This model can occasionally skip or repeat words; a clip much shorter or longer than
        # the words suggest is worth listening to.
        match = checks.get(seg["id"], {}).get("match", 0)
        table[seg["id"]]["match"] = match
        flag = "  <-- listen to this one" if match < 0.88 else ""
        print(f"{seg['id']}: {seconds:.1f}s (was {before}s), words matched {match:.2f}{flag}")
        table_path = AUDIO / "durations.json"
        table_path.write_text(json.dumps(table, indent=1))


def speak(args):
    segments = extract()
    AUDIO.mkdir(exist_ok=True)
    table_path = AUDIO / "durations.json"
    table = json.loads(table_path.read_text()) if table_path.exists() else {}

    default = "chatterbox" if chatterbox_ready() else ("kokoro" if kokoro_ready() else "say")
    engine = "cmd" if args.cmd else (args.engine or default)
    voice = args.voice or {"kokoro": "bm_fable", "say": "Daniel", "chatterbox": "fable", "cmd": ""}[engine]
    if args.only:
        segments = [s for s in segments if s["id"].startswith(args.only)]
    speaker = f"{engine}:{voice}:{args.speed}" if engine != "cmd" else f"cmd:{args.cmd}"
    kokoro = None
    if engine == "kokoro":
        if not kokoro_ready():
            sys.exit("Kokoro model missing: run `tts.py setup` first")
        import soundfile
        from kokoro_onnx import Kokoro
        kokoro = Kokoro(str(MODELS / KOKORO_FILES[0]), str(MODELS / KOKORO_FILES[1]))

    if engine == "chatterbox":
        speaker = f"chatterbox:{voice}:{args.exaggeration}:{args.cfg_weight}:{args.tempo}"
        chatterbox_batch(segments, table, speaker, voice, args)

    made = 0
    for seg in segments:
        out = AUDIO / f"{seg['id']}.wav"
        h = text_hash(seg["text"])
        say = spoken(seg["text"])
        old = table.get(seg["id"], {})
        same = old.get("hash") == h and old.get("speaker") == speaker and old.get("spoken", seg["text"]) == say
        if out.exists() and same and not args.force:
            old["duration"] = round(clip_seconds(out), 3)  # in case the file was replaced by hand
            continue
        raw = AUDIO / f"{seg['id']}.raw.{args.ext}"
        if engine == "cmd":
            cmd = args.cmd.format(text=shlex.quote(say), out=shlex.quote(str(raw)))
            subprocess.run(cmd, shell=True, check=True)
        elif engine == "kokoro":
            accent = "en-gb" if voice.startswith("b") else "en-us"
            samples, rate = kokoro.create(say, voice=voice, speed=args.speed, lang=accent)
            soundfile.write(str(raw), samples, rate)
        else:
            subprocess.run(["say", "-v", voice, "-r", str(int(175 * args.speed)), "-o", str(raw),
                            "--data-format=LEI16@44100", say], check=True)
        # Normalise every engine's output to mono 16-bit 44.1 kHz.
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-ac", "1", "-ar", str(RATE),
                        "-sample_fmt", "s16", str(out)], check=True)
        raw.unlink()
        table[seg["id"]] = {"hash": h, "speaker": speaker, "spoken": say, "duration": round(clip_seconds(out), 3)}
        made += 1
    ids = {s["id"] for s in extract()}
    for stale in [k for k in table if k not in ids]:
        del table[stale]
        (AUDIO / f"{stale}.wav").unlink(missing_ok=True)
    table_path.write_text(json.dumps(table, indent=1))
    total = sum(v["duration"] + GAP for v in table.values())
    print(f"{engine} voice {voice or '(custom)'}: {made} clips generated, {len(table)} total, "
          f"about {total / 60:.1f} min of narration")


MUSIC_LEVEL = 0.16   # music loudness when nobody is speaking (1 = full scale)
MUSIC_DUCK = 0.4     # multiplied in while the narrator speaks


def music_bed(n):
    """Stereo music [n, 2]: music/<anything>.mp3|wav|m4a if you supply one (looped), otherwise synthesised."""
    own = sorted(p for p in (HERE / "music").glob("*") if p.suffix.lower() in (".mp3", ".wav", ".m4a", ".flac", ".ogg"))
    if own:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(own[0]), "-f", "s16le", "-ac", "2", "-ar", str(RATE), "-"],
                             capture_output=True, check=True).stdout
        track = np.frombuffer(raw, dtype=np.int16).reshape(-1, 2) / 32768.0
        track = track / max(np.max(np.abs(track)), 1e-6)
        return np.tile(track, (n // len(track) + 1, 1))[:n]
    import music
    return music.bed(n / RATE)[:n]


def stamp(t, sep=","):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}{sep}{ms % 1000:03d}"


def mux(args):
    ep = args.episode
    video = HERE / "media" / f"silent_{ep}.mp4"
    if not video.exists():
        sys.exit(f"{video} not found: run ./make.sh first")
    timeline, offset = [], 0.0
    for line in (HERE / "media" / f"concat_{ep}.txt").read_text().splitlines():
        if not line.strip():
            continue
        clip = HERE / "media" / line.split("'")[1]
        for seg in json.loads((HERE / "media" / "timing" / f"{clip.stem}.json").read_text()):
            timeline.append({**seg, "scene": clip.stem, "start": offset + seg["start"]})
        offset += float(subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(clip)]))

    srt = HERE / f"blackhole_{ep}.srt"
    srt.write_text("".join(
        f"{i + 1}\n{stamp(s['start'])} --> {stamp(s['start'] + s['duration'])}\n{s['text']}\n\n"
        for i, s in enumerate(timeline)))

    lines, scene = [f"# Voiceover script: {ep}\n", f"Generated by `tts.py`; edit the text in `{ep}.py`.\n"], None
    for s in timeline:
        if s["scene"] != scene:
            scene = s["scene"]
            lines.append(f"\n## {scene}\n")
        lines.append(f"- `{stamp(s['start'], '.')[3:-4]}` {s['text']}")
    (HERE / f"script_{ep}.md").write_text("\n".join(lines) + "\n")

    # Chapter list in the format YouTube reads from a video description.
    chapters, seen = [], set()
    for s in timeline:
        if s["scene"] not in seen:
            seen.add(s["scene"])
            title = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s["scene"].split("_", 2)[2]).replace("Open GL", "OpenGL")
            t = 0 if not chapters else int(s["start"])
            chapters.append(f"{t // 60}:{t % 60:02d} {title.capitalize() if not title.isupper() else title}")
    (HERE / f"chapters_{ep}.txt").write_text("\n".join(chapters) + "\n")

    n = int(offset * RATE)
    voice = np.zeros(n)
    voiced, late = 0, []
    for seg in timeline:
        clip = AUDIO / f"{seg['id']}.wav"
        if not clip.exists():
            continue
        with wave.open(str(clip)) as w:
            data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16) / 32768.0
        if len(data) / RATE > seg["duration"] + GAP:
            late.append(seg["id"])
        a = int(seg["start"] * RATE)
        voice[a:a + len(data)] += data[:n - a]
        voiced += 1

    mix = np.repeat(voice[:, None], 2, axis=1)
    music = None if args.no_music else music_bed(n)
    if music is not None:
        # Duck the music while someone is speaking: follow the voice's loudness,
        # smoothed over about half a second.
        window = int(0.5 * RATE)
        loud = np.convolve(np.abs(voice), np.ones(window) / window, mode="same")
        speaking = np.clip(loud / 0.02, 0, 1)
        gain = MUSIC_LEVEL * (1.0 - (1.0 - MUSIC_DUCK) * speaking)
        fade = np.clip(np.minimum(np.arange(n), n - np.arange(n)) / (2.0 * RATE), 0, 1)
        mix += music * (gain * fade)[:, None]
    mix = np.clip(mix, -1.0, 1.0)

    out = HERE / f"blackhole_{ep}.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(video)]
    has_audio = voiced or music is not None
    if has_audio:
        wav = HERE / "media" / f"audio_{ep}.wav"
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes((mix * 32767).astype(np.int16).tobytes())
        cmd += ["-i", str(wav)]
    # Subtitles stay in the separate .srt file (upload it as captions); they are not put in the video.
    cmd += ["-map", "0:v"] + (["-map", "1:a", "-c:a", "aac", "-b:a", "192k"] if has_audio else [])
    cmd += ["-c:v", "copy", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    kind = "no music" if music is None else "music"
    print(f"wrote {out.name} ({offset / 60:.1f} min, {voiced}/{len(timeline)} sentences voiced, {kind}), "
          f"{srt.name}, script_{ep}.md")
    if late:
        print("audio longer than its slot (re-render to fix):", ", ".join(late))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("extract")
    sp = sub.add_parser("speak")
    sp.add_argument("--engine", choices=["kokoro", "say", "chatterbox"], help="default: kokoro if its model is installed")
    sp.add_argument("--only", help="only (re)generate sentences whose id starts with this, e.g. E1_01_Hook")
    sp.add_argument("--exaggeration", type=float, default=0.6, help="chatterbox: how animated the delivery is")
    sp.add_argument("--cfg-weight", type=float, default=0.2, help="chatterbox: lower = looser pacing")
    sp.add_argument("--tempo", type=float, default=0.94, help="chatterbox: playback speed, below 1 = slower")
    sp.add_argument("--voice", help="kokoro: af_heart, af_bella, am_michael, bm_george, ...; say: see `say -v '?'`")
    sp.add_argument("--speed", type=float, default=1.0, help="speaking speed multiplier")
    sp.add_argument("--cmd", help="custom TTS command with {text} and {out} placeholders")
    sp.add_argument("--ext", default="wav", help="file type the custom command writes")
    sp.add_argument("--force", action="store_true", help="regenerate every clip")
    mx = sub.add_parser("mux")
    mx.add_argument("episode", help="ep1, ep2, ...")
    mx.add_argument("--no-music", action="store_true")
    sub.add_parser("setup")
    args = ap.parse_args()
    if args.command == "setup":
        setup()
    elif args.command == "extract":
        segs = extract()
        est = sum(estimate(s["text"]) + GAP for s in segs)
        print(f"{len(segs)} sentences, {sum(len(s['text'].split()) for s in segs)} words, about {est / 60:.1f} min")
    elif args.command == "speak":
        speak(args)
    else:
        mux(args)


if __name__ == "__main__":
    main()
