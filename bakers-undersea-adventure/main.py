"""Baker's Undersea Adventure. Run with:  python main.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from game.engine.asset_builder import ensure_placeholder_assets  # noqa: E402
from game.engine.game import Game  # noqa: E402


def main():
    ensure_placeholder_assets()
    Game().run()


if __name__ == "__main__":
    main()
