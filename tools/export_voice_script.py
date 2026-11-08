"""Write a recording script for voice-over: one line per dialogue line, with the
filename the game will look for. Usage: python tools/export_voice_script.py > VOICE_SCRIPT.md"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from game.engine.content import Content  # noqa: E402


def main():
    content = Content()
    by_speaker: dict[str, list] = {}
    for dialogue_id, entry in content.dialogue.items():
        for i, line in enumerate(entry.get("lines", []), start=1):
            speaker = line.get("speaker", "baker")
            filename = line.get("voice") or f"{dialogue_id}_{i:02d}"
            by_speaker.setdefault(speaker, []).append((filename, line["text"]))
    for item_id, item in content.items.items():
        if item.get("pickup"):
            by_speaker.setdefault("baker", []).append((f"pickup_{item_id}", item["pickup"]))
    for scene_id, scene in content.scenes.items():
        for hs in scene["hotspots"]:
            if hs.get("type") != "humor":
                continue
            texts = hs["text"] if isinstance(hs["text"], list) else [hs["text"]]
            for i, text in enumerate(texts, start=1):
                by_speaker.setdefault(hs.get("speaker", "baker"), []).append(
                    (f"humor_{scene_id}_{hs['id']}_{i:02d}", text))
    print("# Voice-over recording script\n")
    print("Save each take as `assets/audio/voice/<filename>.ogg` (or `.wav`). "
          "Missing files are fine; the line just shows as text.\n")
    total = 0
    for speaker in sorted(by_speaker):
        name = content.character(speaker).get("name", speaker)
        lines = by_speaker[speaker]
        total += len(lines)
        print(f"## {name} ({len(lines)} lines)\n")
        print("| File | Line |\n|---|---|")
        for filename, text in lines:
            print(f"| `{filename}` | {text} |")
        print()
    print(f"_{total} lines total._")


if __name__ == "__main__":
    main()
