"""Generates the placeholder asset pack (images, audio, manifest) when it is
missing. Real art and sound replace these files one-for-one; the filenames to
use are listed in assets/manifest.json."""
import json
import math
import random
import struct
import wave

import pygame

from . import placeholders
from .config import ASSETS_DIR, IMAGES_DIR, AUDIO_DIR, WIDTH, PLAY_H
from .content import Content

SAMPLE_RATE = 22050


# Audio synthesis ---------------------------------------------------------------
def _write_wav(path, samples):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for s in samples:
            frames += struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32000))
        wf.writeframes(bytes(frames))


def _tone(freq, seconds, volume=0.5, shape="sine", attack=0.01, release=0.08):
    n = int(SAMPLE_RATE * seconds)
    out = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = min(1.0, t / attack) * min(1.0, (seconds - t) / release)
        phase = 2 * math.pi * freq * t
        if shape == "square":
            v = 1.0 if math.sin(phase) > 0 else -1.0
            v *= 0.4
        elif shape == "tri":
            v = 2 / math.pi * math.asin(math.sin(phase))
        else:
            v = math.sin(phase)
        out.append(v * env * volume)
    return out


def _mix(*tracks):
    length = max(len(t) for t in tracks)
    out = [0.0] * length
    for t in tracks:
        for i, s in enumerate(t):
            out[i] += s
    return out


def _underwater_loop(seconds=12.0):
    n = int(SAMPLE_RATE * seconds)
    out = []
    rng = random.Random(7)
    for i in range(n):
        t = i / SAMPLE_RATE
        lfo = 0.6 + 0.4 * math.sin(2 * math.pi * t / seconds * 2)
        v = 0.25 * math.sin(2 * math.pi * 110 * t) * lfo
        v += 0.18 * math.sin(2 * math.pi * 165 * t + 0.5) * (0.7 + 0.3 * math.sin(2 * math.pi * t / seconds * 3))
        v += 0.10 * math.sin(2 * math.pi * 220 * t) * (0.5 + 0.5 * math.sin(2 * math.pi * t / seconds))
        v += 0.03 * (rng.random() * 2 - 1)
        out.append(v)
    return out


def _festival_loop():
    notes = [262, 330, 392, 523, 392, 330, 294, 392, 440, 523, 440, 392, 330, 294, 262, 392]
    beat = 0.25
    melody = []
    for f in notes:
        melody += _tone(f, beat, 0.22, "square", 0.005, 0.06)
    bass = []
    for f in (131, 131, 165, 165, 196, 196, 147, 147):
        bass += _tone(f, beat * 2, 0.25, "tri", 0.01, 0.1)
    return _mix(melody, bass)


def _bubble():
    n = int(SAMPLE_RATE * 0.18)
    out = []
    for i in range(n):
        t = i / SAMPLE_RATE
        f = 300 + 1800 * (t / 0.18) ** 2
        env = math.sin(math.pi * t / 0.18)
        out.append(0.5 * env * math.sin(2 * math.pi * f * t))
    return out


def _click():
    rng = random.Random(3)
    n = int(SAMPLE_RATE * 0.04)
    return [0.4 * (rng.random() * 2 - 1) * (1 - i / n) for i in range(n)]


def _pickup():
    return _tone(660, 0.09, 0.5) + _tone(990, 0.14, 0.5)


def _success():
    a = _tone(523, 0.5, 0.35)
    b = [0.0] * int(SAMPLE_RATE * 0.12) + _tone(659, 0.45, 0.35)
    c = [0.0] * int(SAMPLE_RATE * 0.24) + _tone(784, 0.6, 0.35)
    d = [0.0] * int(SAMPLE_RATE * 0.36) + _tone(1046, 0.7, 0.3)
    return _mix(a, b, c, d)


AUDIO = {
    "underwater": _underwater_loop,
    "festival": _festival_loop,
    "bubble": _bubble,
    "click": _click,
    "pickup": _pickup,
    "success": _success,
}


def build_audio(force=False):
    written = []
    for name, fn in AUDIO.items():
        path = AUDIO_DIR / f"{name}.wav"
        if force or not path.is_file():
            _write_wav(path, fn())
            written.append(path.name)
    return written


# Images ----------------------------------------------------------------------------
def build_images(content: Content, force=False):
    if not pygame.get_init():
        pygame.init()
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    written = []

    def save(surf, filename):
        path = IMAGES_DIR / filename
        if force or not path.is_file():
            pygame.image.save(surf, str(path))
            written.append(filename)

    for scene_id, scene in content.scenes.items():
        data = dict(scene); data["id"] = scene_id
        if scene.get("background"):
            save(placeholders.background(data), scene["background"])
    # Character sprites are NOT written as files on purpose: the procedural
    # placeholders animate (blink, talk) and keep their proportions at any size.
    # Drop real PNGs named as in characters.json into assets/images to use them.
    for item_id, item in content.items.items():
        if item.get("icon"):
            save(placeholders.icon(item, 64), item["icon"])
    return written


def build_manifest(content: Content):
    manifest = {
        "_readme": "Drop real files with these names into assets/ to replace the placeholders. "
                   "Backgrounds are 1280x640 (the window is 1280x720; the bottom 80px is the inventory bar).",
        "backgrounds": {sid: s.get("background") for sid, s in content.scenes.items()},
        "characters": {cid: {"sprite": c.get("sprite"), "portrait": c.get("portrait")} for cid, c in content.characters.items()},
        "items": {iid: i.get("icon") for iid, i in content.items.items()},
        "audio": {name: f"audio/{name}.wav (or .ogg)" for name in AUDIO},
        "voice": "audio/voice/<dialogue_id>_<line number>.ogg  (see tools/export_voice_script.py)",
    }
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ASSETS_DIR / "manifest.json", "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    return manifest


def ensure_placeholder_assets(force=False):
    """Called from main.py: cheap when everything already exists."""
    content = Content()
    written = build_audio(force)
    if force or not (ASSETS_DIR / "manifest.json").is_file():
        build_manifest(content)
    return written
