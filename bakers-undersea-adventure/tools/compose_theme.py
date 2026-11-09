"""Compose and render the opening theme of Baker's Undersea Adventure.

Everything is synthesised from scratch with numpy: a small chamber-orchestra
palette (strings, harp, flute, celesta, cello, timpani, shaker, bell) playing a
written score, mixed in stereo with a convolution reverb.

Outputs (in bakers-undersea-adventure/music/):
    opening_theme_instrumental.wav     full 72 s arrangement, music only
    opening_theme_with_narration.wav   music ducked under the narrator
    opening_narration_voice_only.wav   the narration stem, same timeline
    underwater_loop.wav                16-bar seamless loop for in-game use
plus .mp3 / .ogg versions via ffmpeg when it is installed.

Usage:
    python tools/compose_theme.py [--voice-dir DIR_WITH_NARRATION_WAVS]
The narration clips are 4 sentence files named narr_1.wav .. narr_4.wav; see
music/NARRATION_SCRIPT.md. Without --voice-dir only the instrumental and loop
are rendered.
"""
import argparse
import math
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "music"
rng = np.random.default_rng(1998)

# ----------------------------------------------------------------------------
# Timing: 6/8 at dotted-quarter = 80 bpm  ->  one eighth note = 0.25 s
EIGHTH = 0.25
BAR = 6 * EIGHTH          # 1.5 s
N_BARS = 48
TOTAL = N_BARS * BAR + 6.0   # reverb tail / fade room


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def note(name):
    """'F4' -> midi number."""
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    base = names[name[0]]
    rest = name[1:]
    if rest.startswith("b"):
        base -= 1; rest = rest[1:]
    elif rest.startswith("#"):
        base += 1; rest = rest[1:]
    return 12 * (int(rest) + 1) + base


# ----------------------------------------------------------------------------
# Instruments. Each returns a mono float array for (midi pitch, duration s, velocity).
def adsr(n, a, d, s, r, total_len=None):
    total_len = total_len or n
    env = np.zeros(total_len)
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    sus_n = max(0, n - a_n - d_n)
    idx = 0
    env[idx:idx + a_n] = np.linspace(0, 1, a_n, endpoint=False); idx += a_n
    env[idx:idx + d_n] = np.linspace(1, s, d_n, endpoint=False); idx += d_n
    env[idx:idx + sus_n] = s; idx += sus_n
    r_n = min(r_n, total_len - idx)
    if r_n > 0:
        env[idx:idx + r_n] = s * np.linspace(1, 0, r_n)
    return env


def lp_fft(x, cutoff, order=2):
    """Butterworth-ish low-pass done in the frequency domain (fast, zero phase)."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    H = 1 / np.sqrt(1 + (f / cutoff) ** (2 * order))
    return np.fft.irfft(X * H, n)


def strings(p, dur, vel=1.0):
    n = int((dur + 1.2) * SR)
    t = np.arange(n) / SR
    f = midi(p)
    out = np.zeros(n)
    for det in (-0.004, 0.0, 0.0045, -0.0025, 0.003):
        ph = 2 * np.pi * f * (1 + det) * t + rng.uniform(0, 6.28)
        vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t + rng.uniform(0, 6.28)) * np.clip(t / 0.8, 0, 1)
        for h in range(1, 9):
            out += np.sin(h * ph * vib) / (h ** 1.3)
    out = lp_fft(out, 1800 + f * 2)
    env = adsr(int(dur * SR), 0.45, 0.2, 0.85, 1.1, n)
    return out * env * vel * 0.16


def cello(p, dur, vel=1.0):
    n = int((dur + 0.8) * SR)
    t = np.arange(n) / SR
    f = midi(p)
    out = np.zeros(n)
    for det in (-0.003, 0.0, 0.003):
        ph = 2 * np.pi * f * (1 + det) * t
        for h in range(1, 7):
            out += np.sin(h * ph) / h
    out = lp_fft(out, 900)
    env = adsr(int(dur * SR), 0.12, 0.15, 0.8, 0.7, n)
    return out * env * vel * 0.3


def harp(p, dur, vel=1.0):
    n = int(max(dur, 0.1) * SR + 2.5 * SR)
    t = np.arange(n) / SR
    f = midi(p)
    out = np.zeros(n)
    for h, amp in ((1, 1.0), (2, 0.5), (3, 0.3), (4, 0.18), (5, 0.1), (6, 0.06)):
        decay = np.exp(-t * (1.6 + h * 0.9))
        out += amp * np.sin(2 * np.pi * f * h * (1 + 0.0003 * h * h) * t) * decay
    attack = np.minimum(1, t / 0.004)
    return out * attack * vel * 0.32


def flute(p, dur, vel=1.0):
    n = int((dur + 0.5) * SR)
    t = np.arange(n) / SR
    f = midi(p)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.15) / 0.5, 0, 1)
    ph = 2 * np.pi * f * vib * t
    tone = np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.07 * np.sin(3 * ph) + 0.03 * np.sin(4 * ph)
    breath = lp_fft(rng.normal(0, 1, n), 3000) * 0.012
    env = adsr(int(dur * SR), 0.09, 0.1, 0.9, 0.35, n)
    return (tone + breath) * env * vel * 0.42


def celesta(p, dur, vel=1.0):
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    f = midi(p)
    out = np.sin(2 * np.pi * f * t) * np.exp(-t * 3.2) + 0.35 * np.sin(2 * np.pi * f * 4.0 * t) * np.exp(-t * 7) \
        + 0.15 * np.sin(2 * np.pi * f * 9.7 * t) * np.exp(-t * 12)
    return out * np.minimum(1, t / 0.002) * vel * 0.3


def bell(p, dur, vel=1.0):
    n = int(5 * SR)
    t = np.arange(n) / SR
    f = midi(p)
    out = np.zeros(n)
    for ratio, amp, dec in ((1, 1, 0.9), (2.0, 0.5, 1.4), (2.76, 0.35, 1.9), (5.4, 0.2, 3.0), (8.9, 0.1, 4.5)):
        out += amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t * dec)
    return out * vel * 0.25


def timpani(p, dur, vel=1.0):
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    f = midi(p)
    sweep = f * (1 + 0.35 * np.exp(-t * 18))
    ph = 2 * np.pi * np.cumsum(sweep) / SR
    body = np.sin(ph) * np.exp(-t * 3.5) + 0.3 * np.sin(1.5 * ph) * np.exp(-t * 6)
    thump = lp_fft(rng.normal(0, 1, n), 300) * np.exp(-t * 40) * 1.5
    return (body + thump) * vel * 0.9


def shaker(p, dur, vel=1.0):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    band = lp_fft(noise, 8000) - lp_fft(noise, 2500)      # soft, band-limited shaker
    return band * np.exp(-t * 45) * vel * 0.1


INSTRUMENTS = {
    "strings": strings, "cello": cello, "harp": harp, "flute": flute,
    "celesta": celesta, "bell": bell, "timpani": timpani, "shaker": shaker,
}
PAN = {"strings": 0.0, "cello": -0.35, "harp": 0.4, "flute": -0.25, "celesta": 0.5, "bell": 0.2,
       "timpani": -0.1, "shaker": 0.6}
LEVEL = {"strings": 0.9, "cello": 0.8, "harp": 0.85, "flute": 1.0, "celesta": 0.55, "bell": 0.6,
         "timpani": 0.55, "shaker": 0.22}


# ----------------------------------------------------------------------------
# Score
CHORDS = {
    "F":  ["F", "A", "C"], "Bb": ["Bb", "D", "F"], "C": ["C", "E", "G"], "Dm": ["D", "F", "A"],
    "Gm": ["G", "Bb", "D"], "Am": ["A", "C", "E"], "C7": ["C", "E", "G", "Bb"],
}
PROG_A = ["F", "F", "Bb", "C", "F", "Dm", "Bb", "C"]
PROG_BRIDGE = ["Dm", "Bb", "Gm", "C", "Dm", "Bb", "C", "C7"]
PROG_END = ["F", "Dm", "Bb", "C", "F", "Bb", "C", "F"]

# melody: list of bars; each bar a list of (note, eighths). None = rest
THEME = [
    [("A4", 3), ("C5", 2), ("A4", 1)],
    [("G4", 3), ("F4", 3)],
    [("D5", 2), ("C5", 1), ("Bb4", 3)],
    [("C5", 4), ("A4", 2)],
    [("A4", 3), ("C5", 2), ("F5", 1)],
    [("E5", 3), ("D5", 3)],
    [("C5", 2), ("Bb4", 1), ("A4", 2), ("G4", 1)],
    [("F4", 6)],
]
BRIDGE = [
    [("D5", 3), ("F5", 3)],
    [("E5", 2), ("D5", 1), ("C5", 3)],
    [("Bb4", 3), ("D5", 3)],
    [("C5", 6)],
    [("D5", 3), ("F5", 2), ("G5", 1)],
    [("A5", 3), ("G5", 3)],
    [("F5", 2), ("E5", 1), ("D5", 3)],
    [("E5", 4), ("G5", 2)],
]
COUNTER = [   # celesta answers in section C and E
    [(None, 3), ("F5", 1), ("A5", 1), ("C6", 1)],
    [(None, 6)],
    [(None, 3), ("D6", 1), ("C6", 1), ("Bb5", 1)],
    [(None, 6)],
    [(None, 3), ("F5", 1), ("A5", 1), ("C6", 1)],
    [(None, 6)],
    [(None, 2), ("C6", 1), (None, 1), ("A5", 1), (None, 1)],
    [("F5", 1), ("A5", 1), ("C6", 1), ("F6", 3)],
]


def harmony_third(bars):
    """Diatonic third below each melody note (F major), bar by bar."""
    scale = ["F", "G", "A", "Bb", "C", "D", "E"]
    result = []
    for bar in bars:
        out = []
        for n, d in bar:
            if n is None:
                out.append((None, d)); continue
            name, octv = n[:-1], int(n[-1])
            i = scale.index(name)
            j = (i - 2) % 7
            if j > i:
                octv -= 1
            out.append((scale[j] + str(octv), d))
        result.append(out)
    return result


class Mix:
    def __init__(self, seconds):
        self.n = int(seconds * SR)
        self.L = np.zeros(self.n)
        self.R = np.zeros(self.n)

    def play(self, inst, pitch, start, dur, vel=1.0, pan=None):
        if pitch is None:
            return
        p = note(pitch) if isinstance(pitch, str) else pitch
        start += rng.normal(0, 0.006)              # human timing
        vel *= rng.uniform(0.92, 1.0)
        sig = INSTRUMENTS[inst](p, dur, vel) * LEVEL[inst]
        pan = PAN[inst] if pan is None else pan
        i = max(0, int(start * SR))
        seg = sig[: self.n - i]
        if len(seg) <= 0:
            return
        gl, gr = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        self.L[i:i + len(seg)] += seg * gl
        self.R[i:i + len(seg)] += seg * gr


def bar_time(b):
    return b * BAR


def write_melody(mix, inst, bars, start_bar, vel=1.0, octave=0, pan=None, legato=0.98):
    for bi, bar in enumerate(bars):
        t = bar_time(start_bar + bi)
        for n, d in bar:
            if n is not None:
                p = note(n) + 12 * octave
                mix.play(inst, p, t, d * EIGHTH * legato, vel, pan)
            t += d * EIGHTH


def write_harp(mix, prog, start_bar, vel=1.0, pattern=(0, 1, 2, 3, 2, 1)):
    for bi, ch in enumerate(prog):
        tones = CHORDS[ch]
        base = [note(tones[0] + "3"), note(tones[1] + "3"), note(tones[2] + "3") if note(tones[2] + "3") > note(tones[0] + "3") else note(tones[2] + "4"),
                note(tones[0] + "4")]
        base = sorted(base)
        t = bar_time(start_bar + bi)
        for k in pattern:
            mix.play("harp", base[k], t, EIGHTH * 2, vel * (1.0 if k == 0 else 0.8))
            t += EIGHTH


def write_pad(mix, prog, start_bar, vel=1.0, octave=0):
    for bi, ch in enumerate(prog):
        tones = CHORDS[ch]
        t = bar_time(start_bar + bi)
        for k, tn in enumerate(tones):
            p = note(tn + "3") + 12 * octave
            if k and p < note(tones[0] + "3") + 12 * octave:
                p += 12
            mix.play("strings", p, t, BAR * 1.02, vel * 0.8)
            mix.play("strings", p + 12, t, BAR * 1.02, vel * 0.45)


def write_bass(mix, prog, start_bar, vel=1.0):
    for bi, ch in enumerate(prog):
        root = note(CHORDS[ch][0] + "2")
        t = bar_time(start_bar + bi)
        mix.play("cello", root, t, EIGHTH * 3, vel)
        mix.play("cello", root + (7 if ch != "C7" else 5), t + EIGHTH * 3, EIGHTH * 3, vel * 0.7)


def write_percussion(mix, start_bar, n_bars, timp=True, vel=1.0):
    for b in range(n_bars):
        t = bar_time(start_bar + b)
        if timp and b % 2 == 0:
            mix.play("timpani", note("F2"), t, 1.0, vel * 0.8)
        for k in range(6):
            mix.play("shaker", 60, t + k * EIGHTH, 0.1, vel * (0.9 if k in (0, 3) else 0.35))


def compose():
    mix = Mix(TOTAL)
    # A: bars 0-7  harp alone, pad creeps in at bar 4
    write_harp(mix, PROG_A, 0, vel=0.9)
    write_pad(mix, PROG_A[4:], 4, vel=0.55)
    mix.play("bell", note("F5"), 0.0, 1, 0.5)
    # B: bars 8-15  theme on flute
    write_harp(mix, PROG_A, 8, vel=0.85)
    write_pad(mix, PROG_A, 8, vel=0.7)
    write_bass(mix, PROG_A, 8, vel=0.7)
    write_melody(mix, "flute", THEME, 8, vel=0.9)
    # C: bars 16-23  theme again with celesta + light percussion
    write_harp(mix, PROG_A, 16, vel=0.9)
    write_pad(mix, PROG_A, 16, vel=0.8)
    write_bass(mix, PROG_A, 16, vel=0.85)
    write_melody(mix, "flute", THEME, 16, vel=1.0)
    write_melody(mix, "celesta", COUNTER, 16, vel=0.8)
    write_percussion(mix, 16, 8, timp=False, vel=0.7)
    # D: bars 24-31  bridge, strings carry the tune, flute answers an octave up
    write_harp(mix, PROG_BRIDGE, 24, vel=0.8, pattern=(0, 2, 1, 3, 1, 2))
    write_pad(mix, PROG_BRIDGE, 24, vel=0.75)
    write_bass(mix, PROG_BRIDGE, 24, vel=0.9)
    write_melody(mix, "strings", BRIDGE, 24, vel=1.1, legato=1.0)
    write_melody(mix, "flute", BRIDGE[4:], 28, vel=0.75, octave=1)
    write_percussion(mix, 24, 8, timp=True, vel=0.8)
    # E: bars 32-39  full theme: flute + strings in thirds, timpani, bells on downbeats
    write_harp(mix, PROG_A, 32, vel=1.0)
    write_pad(mix, PROG_A, 32, vel=0.95)
    write_bass(mix, PROG_A, 32, vel=1.0)
    write_melody(mix, "flute", THEME, 32, vel=1.05)
    write_melody(mix, "strings", harmony_third(THEME), 32, vel=0.8, legato=1.0)
    write_melody(mix, "celesta", COUNTER, 32, vel=0.9)
    write_percussion(mix, 32, 8, timp=True, vel=1.0)
    for b in (32, 34, 36):
        mix.play("bell", note("F5"), bar_time(b), 1, 0.45)
    # F: bars 40-47  outro, thinning out to harp and a last chord
    write_harp(mix, PROG_END, 40, vel=0.85)
    write_pad(mix, PROG_END, 40, vel=0.7)
    write_bass(mix, PROG_END[:7], 40, vel=0.7)
    closing = [THEME[4], THEME[5], THEME[6], [("F4", 6)],
               [("A4", 3), ("G4", 3)], [("F4", 2), ("G4", 1), ("A4", 3)], [("G4", 6)]]
    write_melody(mix, "flute", closing, 40, vel=0.85)
    write_melody(mix, "celesta", [[(None, 3), ("C6", 1), ("A5", 1), ("F5", 1)]], 46, vel=0.7)
    final = bar_time(47)
    for p in ("F2", "C3", "F3", "A3", "C4", "F4"):
        mix.play("strings", note(p), final, BAR * 2.5, 0.9)
    mix.play("cello", note("F2"), final, BAR * 2.2, 0.9)
    mix.play("harp", note("F4"), final, 2, 1.0); mix.play("harp", note("A4"), final + 0.12, 2, 0.9)
    mix.play("harp", note("C5"), final + 0.24, 2, 0.9); mix.play("harp", note("F5"), final + 0.36, 2, 1.0)
    mix.play("bell", note("F5"), final + 0.4, 1, 0.7)
    mix.play("timpani", note("F2"), final, 1, 0.9)
    return mix


# ----------------------------------------------------------------------------
# Effects / mastering
def reverb_ir(seconds=2.2, decay=3.2):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    env = np.exp(-t * decay)
    l = rng.normal(0, 1, n) * env
    r = rng.normal(0, 1, n) * env
    # early reflections
    for d, g in ((0.011, 0.6), (0.019, 0.45), (0.027, 0.35), (0.041, 0.25)):
        i = int(d * SR)
        l[i] += g; r[i + 7] += g
    l[0] = r[0] = 0
    l = lp_fft(l, 5000); r = lp_fft(r, 5000)
    norm = max(np.abs(l).sum(), np.abs(r).sum()) / 12
    return l / norm, r / norm


def convolve(x, h):
    n = len(x) + len(h) - 1
    N = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(h, N), N)[: len(x)]


def master(L, R, wet=0.32):
    irl, irr = reverb_ir()
    wl, wr = convolve(L, irl), convolve(R, irr)
    L = L * (1 - wet) + wl * wet * 1.4 + wr * wet * 0.25
    R = R * (1 - wet) + wr * wet * 1.4 + wl * wet * 0.25
    peak = max(np.abs(L).max(), np.abs(R).max(), 1e-9)
    L, R = L / peak * 0.9, R / peak * 0.9
    # gentle soft clip
    L, R = np.tanh(L * 1.15) / np.tanh(1.15), np.tanh(R * 1.15) / np.tanh(1.15)
    return L, R


def fade(L, R, out_seconds=4.0):
    n = int(out_seconds * SR)
    ramp = np.linspace(1, 0, n)
    L[-n:] *= ramp; R[-n:] *= ramp
    return L, R


def write_wav(path, L, R):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = np.stack([L, R], axis=1)
    pcm = (np.clip(data, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


def read_wav_mono(path):
    with wave.open(str(path), "rb") as wf:
        sr, ch, sw, n = wf.getframerate(), wf.getnchannels(), wf.getsampwidth(), wf.getnframes()
        raw = wf.readframes(n)
    data = np.frombuffer(raw, dtype="<i2" if sw == 2 else "<i4").astype(np.float64)
    data /= 32768.0 if sw == 2 else 2147483648.0
    if ch > 1:
        data = data.reshape(-1, ch).mean(axis=1)
    if sr != SR:
        x_old = np.linspace(0, 1, len(data)); x_new = np.linspace(0, 1, int(len(data) * SR / sr))
        data = np.interp(x_new, x_old, data)
    return data


def encode(path_wav):
    if not shutil.which("ffmpeg"):
        return
    for ext, args in ((".mp3", ["-codec:a", "libmp3lame", "-q:a", "2"]), (".ogg", ["-codec:a", "libvorbis", "-q:a", "6"])):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(path_wav), *args, str(path_wav.with_suffix(ext))], check=False)


# ----------------------------------------------------------------------------
# Narration: four sentences placed over the quiet opening sections.
NARRATION = [
    (1.5,  "Far below the waves, where the water is warm and the coral glows, there is a little town called the Coral Reef."),
    (8.5,  "Today is Founder's Day, the happiest day of the whole year."),
    (12.5, "But this morning, the Great Conch Shell has gone missing!"),
    (16.5, "Somebody has to find it before the festival begins. And that somebody... is Baker."),
]


def place_narration(voice_dir: Path, n):
    voice = np.zeros(n)
    for i, (start, _) in enumerate(NARRATION, start=1):
        clip_path = voice_dir / f"narr_{i}.wav"
        if not clip_path.is_file():
            print(f"  missing {clip_path.name}, skipped")
            continue
        clip = read_wav_mono(clip_path)
        clip = clip / (np.abs(clip).max() + 1e-9) * 0.8
        s = int(start * SR)
        seg = clip[: n - s]
        voice[s:s + len(seg)] += seg
    return voice


def duck(L, R, voice, depth=0.6):
    """Lower the music while the narrator speaks (sidechain-style)."""
    win = int(0.05 * SR)
    env = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, mode="same"))
    env = env / (env.max() + 1e-9)
    env = np.clip(env * 3, 0, 1)
    # attack fast, release slow
    out = np.empty_like(env)
    g = 0.0
    att, rel = math.exp(-1 / (0.02 * SR)), math.exp(-1 / (0.6 * SR))
    for i, v in enumerate(env):
        coef = att if v > g else rel
        g = coef * g + (1 - coef) * v
        out[i] = g
    gain = 1 - depth * out
    return L * gain, R * gain


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-dir", type=Path, default=None)
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    print("composing...")
    mix = compose()
    print("mastering...")
    L, R = master(mix.L, mix.R)
    L, R = fade(L, R)
    write_wav(OUT / "opening_theme_instrumental.wav", L, R)
    encode(OUT / "opening_theme_instrumental.wav")
    print("  opening_theme_instrumental")

    # In-game loop: bars 8-23 (theme twice) with the reverb tail folded back to the start.
    s, e = int(bar_time(8) * SR), int(bar_time(24) * SR)
    tail = int(2.5 * SR)
    lL, lR = master(mix.L[s:e + tail], mix.R[s:e + tail], wet=0.3)
    body_L, body_R = lL[: e - s].copy(), lR[: e - s].copy()
    body_L[:tail] += lL[e - s:e - s + tail]; body_R[:tail] += lR[e - s:e - s + tail]
    peak = max(np.abs(body_L).max(), np.abs(body_R).max())
    write_wav(OUT / "underwater_loop.wav", body_L / peak * 0.85, body_R / peak * 0.85)
    encode(OUT / "underwater_loop.wav")
    print("  underwater_loop")

    if args.voice_dir:
        print("narration...")
        voice = place_narration(args.voice_dir, len(L))
        voice = lp_fft(voice, 9000)
        write_wav(OUT / "opening_narration_voice_only.wav", voice, voice)
        encode(OUT / "opening_narration_voice_only.wav")
        dL, dR = duck(L, R, voice)
        mL, mR = dL + voice * 0.95, dR + voice * 0.95
        peak = max(np.abs(mL).max(), np.abs(mR).max())
        write_wav(OUT / "opening_theme_with_narration.wav", mL / peak * 0.95, mR / peak * 0.95)
        encode(OUT / "opening_theme_with_narration.wav")
        print("  opening_theme_with_narration, opening_narration_voice_only")
    print("done ->", OUT)


if __name__ == "__main__":
    main()
