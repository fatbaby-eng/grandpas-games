"""Cut characters out of painted reference images with numpy only (no OpenCV).

Colour-model segmentation: k-means clusters of foreground samples (around seed
points) versus background samples (the crop border plus optional extra colours),
then region growing from the seeds, hole filling and a feathered edge.

    python tools/keyout.py              # runs the job list at the bottom
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "web" / "assets" / "images" / "characters"


def kmeans(samples, k, iters=20, seed=0):
    rng = np.random.default_rng(seed)
    centers = samples[rng.choice(len(samples), min(k, len(samples)), replace=False)].astype(np.float64)
    for _ in range(iters):
        d = ((samples[:, None, :] - centers[None, :, :]) ** 2).sum(-1)
        lab = d.argmin(1)
        for i in range(len(centers)):
            pts = samples[lab == i]
            if len(pts):
                centers[i] = pts.mean(0)
    return centers


def grow(mask, seeds):
    """Region-grow inside `mask` (bool HxW) from seed points (x, y)."""
    region = np.zeros_like(mask)
    for x, y in seeds:
        if 0 <= y < mask.shape[0] and 0 <= x < mask.shape[1]:
            region[y, x] = mask[y, x]
    if not region.any():
        return region
    while True:
        d = region.copy()
        d[1:, :] |= region[:-1, :]; d[:-1, :] |= region[1:, :]
        d[:, 1:] |= region[:, :-1]; d[:, :-1] |= region[:, 1:]
        d &= mask
        if (d == region).all():
            return region
        region = d


def fill_holes(fg, max_area=6000):
    """Fill enclosed background pockets smaller than max_area (eyes, highlights),
    but leave big enclosed areas alone (the inside of a curled tail)."""
    bg = ~fg
    border = [(x, 0) for x in range(fg.shape[1])] + [(x, fg.shape[0] - 1) for x in range(fg.shape[1])] + \
             [(0, y) for y in range(fg.shape[0])] + [(fg.shape[1] - 1, y) for y in range(fg.shape[0])]
    outside = grow(bg, border)
    holes = bg & ~outside
    out = fg.copy()
    remaining = holes.copy()
    while remaining.any():
        ys, xs = np.where(remaining)
        comp = grow(remaining, [(xs[0], ys[0])])
        if comp.sum() <= max_area:
            out |= comp
        remaining &= ~comp
    return out


def erode(m, n=1):
    for _ in range(n):
        e = m.copy()
        e[1:, :] &= m[:-1, :]; e[:-1, :] &= m[1:, :]; e[:, 1:] &= m[:, :-1]; e[:, :-1] &= m[:, 1:]
        m = e
    return m


def dilate(m, n=1):
    for _ in range(n):
        d = m.copy()
        d[1:, :] |= m[:-1, :]; d[:-1, :] |= m[1:, :]; d[:, 1:] |= m[:, :-1]; d[:, :-1] |= m[:, 1:]
        m = d
    return m


def to_features(rgb):
    """RGB + a chroma emphasis so hue separates better than brightness."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return np.stack([r, g, b, (r - b) * 1.2, (g - b) * 0.8], -1)


def poly_mask(w, h, polys, offset):
    m = Image.new("L", (w, h), 0); d = ImageDraw.Draw(m)
    for poly in polys or []:
        d.polygon([(x - offset[0], y - offset[1]) for x, y in poly], fill=255)
    return np.asarray(m) > 0


def segment(img, rect, seeds, extra_bg=(), fg_box=12, border=6, k_fg=6, k_bg=8, bias=0.0, force_fg=None, force_bg=None):
    x0, y0, w, h = rect
    crop = np.asarray(img.convert("RGB"), dtype=np.float64)[y0:y0 + h, x0:x0 + w]
    feat = to_features(crop)
    local_seeds = [(sx - x0, sy - y0) for sx, sy in seeds]
    fg_samples = np.concatenate([feat[max(0, sy - fg_box):sy + fg_box, max(0, sx - fg_box):sx + fg_box].reshape(-1, 5) for sx, sy in local_seeds])
    ring = np.zeros((h, w), bool); ring[:border, :] = ring[-border:, :] = True; ring[:, :border] = ring[:, -border:] = True
    bg_samples = feat[ring].reshape(-1, 5)
    if len(bg_samples) > 6000:
        bg_samples = bg_samples[np.random.default_rng(0).choice(len(bg_samples), 6000, replace=False)]
    cf = kmeans(fg_samples, k_fg)
    cb = kmeans(bg_samples, k_bg)
    if extra_bg:
        extra = to_features(np.array(extra_bg, dtype=np.float64).reshape(-1, 1, 3)).reshape(-1, 5)
        cb = np.concatenate([cb, extra])
    px = feat.reshape(-1, 5)
    dfg = np.sqrt(((px[:, None, :] - cf[None]) ** 2).sum(-1)).min(1)
    dbg = np.sqrt(((px[:, None, :] - cb[None]) ** 2).sum(-1)).min(1)
    fg = (dfg + bias < dbg).reshape(h, w)
    fg = dilate(erode(fg, 1), 1)                   # drop specks
    fg |= poly_mask(w, h, force_fg, (x0, y0))       # hand-marked "definitely character" areas
    fg = grow(fg, local_seeds)                      # keep what touches the seeds
    fg = fill_holes(fg)
    fg = erode(dilate(fg, 2), 2)                    # close small gaps
    fg &= ~poly_mask(w, h, force_bg, (x0, y0))      # hand-marked "definitely background" areas
    return crop, fg


def save_sprite(crop, fg, path, flip=False, feather=1.5, pad=4):
    alpha = (fg.astype(np.uint8) * 255)
    a = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(feather))
    ys, xs = np.where(np.asarray(a) > 8)
    if len(xs) == 0:
        print("  (empty mask, skipped)"); return None
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    rgba = np.dstack([crop.astype(np.uint8), np.asarray(a)])[y0:y1, x0:x1]
    im = Image.fromarray(rgba, "RGBA")
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    canvas = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    canvas.paste(im, (pad, pad))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)
    return canvas


JOBS = [
    # name, source, rect(x,y,w,h), seeds, extra_bg colours, flip-to-face-right, also-apply-mask-to, force_fg polys, force_bg polys
    ("baker", "baker_reef_closed.jpg", (430, 90, 640, 505),
     [(700, 300), (760, 440), (650, 455), (760, 380), (940, 230), (470, 350), (760, 520), (820, 505), (700, 500), (1000, 300)],
     [], True, ("baker_talk", "baker_reef_open.jpg"),
     [[(612, 450), (640, 520), (700, 573), (760, 588), (840, 573), (900, 538), (938, 490), (928, 440), (860, 455), (760, 470), (680, 470)]], None),
    ("coral", "coral_kelp.jpg", (420, 90, 490, 590),
     [(760, 250), (770, 430), (505, 480), (545, 435), (690, 620), (560, 560)],
     [(100, 180, 190), (150, 210, 210), (120, 195, 200)], False, None,
     # the translucent pectoral fin is water-coloured: keep it by hand
     [[(612, 372), (640, 365), (672, 368), (690, 395), (686, 440), (668, 470), (640, 470), (618, 445), (610, 410)]],
     # and keep the inside of the tail hook clear
     [[(536, 452), (552, 440), (572, 446), (582, 464), (576, 484), (558, 494), (538, 486), (528, 468)],
      [(556, 452), (590, 446), (616, 474), (640, 502), (634, 546), (600, 566), (570, 546), (550, 502)]]),
]


def main():
    sheet = []
    for name, src, rect, seeds, extra, flip, also, ffg, fbg in JOBS:
        img = Image.open(ROOT / "art" / "reference" / src)
        crop, fg = segment(img, rect, seeds, extra, force_fg=ffg, force_bg=fbg)
        out = save_sprite(crop, fg, OUT_DIR / f"{name}.png", flip)
        if out is None:
            continue
        sheet.append((name, out))
        print(name, out.size, f"{fg.mean():.0%} of crop")
        if also:
            other = Image.open(ROOT / "art" / "reference" / also[1])
            x0, y0, w, h = rect
            crop2 = np.asarray(other.convert("RGB"), dtype=np.float64)[y0:y0 + h, x0:x0 + w]
            out2 = save_sprite(crop2, fg, OUT_DIR / f"{also[0]}.png", flip)
            sheet.append((also[0], out2))
    # contact sheet on a checkerboard so edges are visible
    W = sum(min(300, im.width) + 20 for _, im in sheet); H = 340
    cs = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    for yy in range(0, H, 20):
        for xx in range(0, W, 20):
            if (xx // 20 + yy // 20) % 2 == 0:
                cs.paste((200, 200, 200, 255), (xx, yy, xx + 20, yy + 20))
    x = 10
    for name, im in sheet:
        s = min(300 / im.width, 300 / im.height, 1.0); t = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        cs.alpha_composite(t, (x, 10)); x += t.width + 20
    cs.save(sys.argv[1] if len(sys.argv) > 1 else "/tmp/contact.png")


if __name__ == "__main__":
    main()
