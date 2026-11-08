from .bubble_catch import BubbleCatch
from .shell_puzzle import ShellPuzzle
from .crab_dance import CrabDance
from .dj_beat import DJBeat

REGISTRY = {cls.id: cls for cls in (BubbleCatch, ShellPuzzle, CrabDance, DJBeat)}
