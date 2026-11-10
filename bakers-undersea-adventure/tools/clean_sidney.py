"""Sidney's GrabCut cut-out keeps a patch of sand between his legs. Inside a
generous polygon under his body, drop every pixel that is not crab-red.
    python tools/clean_sidney.py SRC_SPRITE.png OUT.png
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

src, out = sys.argv[1], sys.argv[2]
OFF = (471 - 4, 147 - 4)                 # sprite bounds + padding, from cutout.py's output
im = Image.open(src).convert("RGBA"); a = np.asarray(im).astype(np.int32)
poly = [(600, 515), (925, 515), (965, 700), (555, 700)]
m = Image.new("L", im.size, 0); ImageDraw.Draw(m).polygon([(x - OFF[0], y - OFF[1]) for x, y in poly], fill=255)
zone = np.asarray(m) > 0
r, g, b = a[..., 0], a[..., 1], a[..., 2]
crab = (r - g > 40) & (r > 120)
alpha = a[..., 3].copy()
alpha[zone & ~crab] = 0
al = Image.fromarray(alpha.astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1))
rgba = np.dstack([a[..., :3].astype(np.uint8), np.asarray(al)])
Image.fromarray(rgba, "RGBA").save(out); print("cleaned", out)
