"""Cut a character out of a painted reference image with GrabCut.

    python tools/cutout.py SRC.jpg OUT.png x y w h [--iters 8] [--feather 2] [--shrink 0.06]

The rectangle is a generous box around the character. The result is a PNG
with alpha, cropped to the character's bounds, with a slightly softened edge.
"""
import argparse
import cv2
import numpy as np


def cutout(src, rect, iters=8, feather=2, shrink=0.06):
    img = cv2.imread(src)
    h, w = img.shape[:2]
    x, y, rw, rh = rect
    mask = np.zeros((h, w), np.uint8)
    bgd = np.zeros((1, 65), np.float64); fgd = np.zeros((1, 65), np.float64)
    cv2.grabCut(img, mask, (x, y, rw, rh), bgd, fgd, iters, cv2.GC_INIT_WITH_RECT)
    # a centred inner box is almost certainly foreground; nudge GrabCut with it
    sx, sy = int(rw * shrink * 3), int(rh * shrink * 3)
    mask[y + sy:y + rh - sy, x + sx:x + rw - sx][mask[y + sy:y + rh - sy, x + sx:x + rw - sx] == cv2.GC_PR_BGD] = cv2.GC_PR_FGD
    cv2.grabCut(img, mask, None, bgd, fgd, 3, cv2.GC_INIT_WITH_MASK)
    alpha = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    # keep the biggest blob only
    n, labels, stats, _ = cv2.connectedComponentsWithStats(alpha)
    if n > 1:
        biggest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        alpha = np.where(labels == biggest, 255, 0).astype(np.uint8)
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    if feather:
        alpha = cv2.GaussianBlur(alpha, (feather * 2 + 1, feather * 2 + 1), 0)
    ys, xs = np.where(alpha > 10)
    if len(xs) == 0:
        raise SystemExit("nothing found")
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = alpha
    return rgba[y0:y1, x0:x1], (x0, y0, x1 - x0, y1 - y0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("rect", nargs=4, type=int)
    ap.add_argument("--iters", type=int, default=8); ap.add_argument("--feather", type=int, default=2)
    ap.add_argument("--shrink", type=float, default=0.06)
    a = ap.parse_args()
    out, box = cutout(a.src, a.rect, a.iters, a.feather, a.shrink)
    cv2.imwrite(a.out, out)
    print(a.out, "bounds", box, "size", out.shape[1], "x", out.shape[0])


if __name__ == "__main__":
    main()
