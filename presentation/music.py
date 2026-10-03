"""A soft ambient music bed, synthesised from scratch (so there is nothing to license).

Slow pad chords in D minor with a little shimmer and a long reverb tail.
tts.py calls bed(seconds); run this file directly to write music_preview.wav.
"""
import numpy as np
from scipy.signal import fftconvolve

RATE = 44100
# D minor 9, B flat major 7, F major 9, A minor 7 (MIDI note numbers).
CHORDS = [(38, 57, 60, 64, 65), (34, 53, 57, 62, 65), (41, 55, 57, 60, 64), (33, 55, 57, 60, 64)]
CHORD_SECONDS = 9.0
FADE = 3.0


def tone(freq, t, detune):
    """One pad voice: a few soft harmonics, slightly detuned, with slow vibrato."""
    f = freq * (1 + detune)
    phase = 2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * 0.11 * t + freq)
    return np.sin(phase) + 0.28 * np.sin(2 * phase) + 0.08 * np.sin(3 * phase)


def bed(seconds, seed=7):
    """Stereo float array [n, 2], peak about 1."""
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    t = np.arange(n) / RATE
    out = np.zeros((n, 2))
    period = CHORD_SECONDS * len(CHORDS)
    for k, chord in enumerate(CHORDS):
        # Each chord swells in and out; neighbours overlap by FADE seconds.
        local = (t - k * CHORD_SECONDS) % period
        env = np.clip(local / FADE, 0, 1) * np.clip((CHORD_SECONDS + FADE - local) / FADE, 0, 1)
        env = np.sin(0.5 * np.pi * env) ** 2
        for i, note in enumerate(chord):
            freq = 440.0 * 2 ** ((note - 69) / 12)
            gain = 0.45 if i == 0 else 0.5 / (1 + 0.3 * i)
            swell = 0.75 + 0.25 * np.sin(2 * np.pi * (0.05 + 0.013 * i) * t + i)
            out[:, 0] += env * gain * swell * tone(freq, t, -0.0015)
            out[:, 1] += env * gain * swell * tone(freq, t, +0.0015)
    # Reverb: convolve with a few seconds of decaying noise, different per ear.
    tail = int(3.5 * RATE)
    decay = np.exp(-np.arange(tail) / (0.9 * RATE))
    for ch in range(2):
        impulse = rng.standard_normal(tail) * decay
        wet = fftconvolve(out[:, ch], impulse)[:n]
        out[:, ch] = 0.55 * out[:, ch] + 0.45 * wet / np.max(np.abs(wet)) * np.max(np.abs(out[:, ch]))
    return out / np.max(np.abs(out))


if __name__ == "__main__":
    import wave
    audio = (bed(40) * 0.5 * 32767).astype(np.int16)
    with wave.open("music_preview.wav", "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(audio.tobytes())
    print("wrote music_preview.wav")
