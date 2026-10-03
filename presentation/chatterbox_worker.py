"""Generates speech with Chatterbox and checks every clip. Run by tts.py inside .venv-tts
(it needs PyTorch, which the video environment does not have).

    .venv-tts/bin/python chatterbox_worker.py job.json

job.json: {"reference": "voice_ref/fable.wav", "exaggeration": 0.6, "cfg_weight": 0.2,
           "items": [{"id": "...", "text": "...", "out": "audio/x.cb.wav"}, ...]}

This kind of model occasionally skips or repeats words. So each clip is transcribed with
Whisper and compared with its text; a poor match is retried with a different random seed
and the best take is kept. The match score of every clip is written to <job>.result.json.
"""
import difflib
import json
import re
import sys

import torch
import torchaudio
import whisper

from chatterbox.tts import ChatterboxTTS

GOOD_ENOUGH = 0.88
SEEDS = [1234, 7, 99, 2024]
NUMBERS = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "20": "twenty",
           "60": "sixty", "200": "two hundred", "4.1": "four point one", "5.2": "five point two", "16": "sixteen"}


def words(text):
    text = text.lower().replace("-", " ").replace("disc", "disk").replace("color", "colour").replace("center", "centre")
    text = re.sub(r"\d+(\.\d+)?", lambda m: NUMBERS.get(m.group(), m.group()), text)
    return re.sub(r"[^a-z0-9 ]", "", text).split()


job = json.load(open(sys.argv[1]))
device = "mps" if torch.backends.mps.is_available() else "cpu"
model = ChatterboxTTS.from_pretrained(device=device)
listener = whisper.load_model("base.en")
results = {}
for n, item in enumerate(job["items"]):
    best = (-1.0, None, None)
    for seed in SEEDS:
        torch.manual_seed(seed)
        wav = model.generate(item["text"], audio_prompt_path=job["reference"],
                             exaggeration=job["exaggeration"], cfg_weight=job["cfg_weight"]).cpu()
        torchaudio.save(item["out"], wav, model.sr)
        heard = listener.transcribe(item["out"], fp16=False)["text"]
        score = difflib.SequenceMatcher(None, words(item["text"]), words(heard)).ratio()
        if score > best[0]:
            best = (score, wav, heard)
        if score >= GOOD_ENOUGH:
            break
    torchaudio.save(item["out"], best[1], model.sr)
    results[item["id"]] = {"match": round(best[0], 3), "heard": best[2].strip()}
    json.dump(results, open(sys.argv[1] + ".result.json", "w"), indent=1)
    print(f"[{n + 1}/{len(job['items'])}] {item['id']} match {best[0]:.2f}", flush=True)
