"""Regenerate the full placeholder asset pack: python tools/make_placeholder_assets.py [--force]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from game.engine.asset_builder import build_audio, build_images, build_manifest  # noqa: E402
from game.engine.content import Content  # noqa: E402

if __name__ == "__main__":
    force = "--force" in sys.argv
    content = Content()
    print("audio:", build_audio(force))
    print("images:", build_images(content, force))
    build_manifest(content)
    print("manifest written to assets/manifest.json")
