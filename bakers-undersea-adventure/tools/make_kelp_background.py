"""Turn the Coral reference painting into a Kelp Forest background by removing
Coral (inpaint + soft-focus blend) and cropping to 1280x640.
    python tools/make_kelp_background.py
"""
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import keyout  # noqa: E402

SRC = ROOT / "art" / "reference" / "coral_kelp.jpg"
OUT = ROOT / "web" / "assets" / "images" / "backgrounds" / "kelp_forest.jpg"


def main():
    img = cv2.imread(str(SRC))
    job = next(j for j in keyout.JOBS if j[0] == "coral")
    _, rect, seeds, extra, _, _, ffg, fbg = job[0:1] and (job[0], job[2], job[3], job[4], job[5], job[6], job[7], job[8])
    crop, fg = keyout.segment(Image.open(SRC), rect, seeds, extra, force_fg=ffg, force_bg=fbg)
    fg = keyout.dilate(fg, 10)
    mask = np.zeros(img.shape[:2], np.uint8)
    x0, y0, w, h = rect
    mask[y0:y0 + h, x0:x0 + w] = fg.astype(np.uint8) * 255
    filled = cv2.inpaint(img, mask, 16, cv2.INPAINT_NS)
    # the inpaint leaves a faint ghost; melt it into the bokeh with a wide blur inside a feathered mask
    soft = cv2.GaussianBlur(filled, (0, 0), 28)
    feather = cv2.GaussianBlur(cv2.dilate(mask, np.ones((25, 25), np.uint8)), (0, 0), 18).astype(np.float32) / 255.0
    out = (filled * (1 - feather[..., None]) + soft * feather[..., None]).astype(np.uint8)
    out = cv2.GaussianBlur(out, (0, 0), 0.8)
    hh, ww = out.shape[:2]
    out = cv2.resize(out, (1280, int(hh * 1280 / ww)), interpolation=cv2.INTER_AREA)
    top = (out.shape[0] - 640) // 2
    OUT.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUT), out[top:top + 640], [cv2.IMWRITE_JPEG_QUALITY, 88])
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
