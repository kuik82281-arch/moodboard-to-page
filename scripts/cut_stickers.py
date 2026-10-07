"""Cut stickers out of reference images: remove the background, split into separate pieces, trim, save small WebPs.

    python cut_stickers.py INPUT OUTDIR [--name base] [--max 420] [--min-area 1500] [--tol 26] [--bg ffffff] [--close 6] [--clear-holes 400] [--no-split]

Background detection: if the image already has transparency it is used as is. Otherwise the colours along the border
are clustered and only the flat clusters are kept (this catches plain white, plain dark, and the two greys of a fake "transparent" checkerboard), pixels
close to those colours become background candidates, and only candidates connected to the border are removed - so a
white flower inside a white-background picture keeps its petals. If the subject itself is flat and touches the edge,
name the background with --bg. Pieces smaller than --min-area pixels are dropped.
Needs Pillow, numpy, scipy.
"""
import argparse
import pathlib
import sys

import numpy as np
from PIL import Image
from scipy import ndimage


def border_colours(rgb: np.ndarray, k: int = 3) -> np.ndarray:
    """The flat colours of the border (k-means on the outermost pixels). A cluster whose pixels vary a lot is a
    textured subject running off the edge (old paper, a photo), not a background, so it is dropped."""
    edge = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]]).astype(float)
    centres = edge[np.linspace(0, len(edge) - 1, k).astype(int)]
    for _ in range(12):
        d = ((edge[:, None, :] - centres[None]) ** 2).sum(-1)
        lab = d.argmin(1)
        for i in range(k):
            if (lab == i).any():
                centres[i] = edge[lab == i].mean(0)
    flat = [c for i, c in enumerate(centres) if (lab == i).sum() > len(edge) * 0.03
            and edge[lab == i].std(0).max() < 14]
    return np.array(flat) if flat else centres[np.bincount(lab, minlength=k).argmax()][None]


def foreground_mask(img: Image.Image, tol: float, bg: str | None = None, close: int = 0, clear_holes: int = 0) -> np.ndarray:
    rgba = np.asarray(img.convert('RGBA'))
    alpha = rgba[..., 3]
    if (alpha < 250).mean() > 0.02:  # already cut out
        return alpha > 24
    rgb = rgba[..., :3].astype(float)
    if bg:
        centres = np.array([[int(c.strip('#')[i:i + 2], 16) for i in (0, 2, 4)] for c in bg.split(',')], float)
    else:
        centres = border_colours(rgb)
    dist = np.sqrt(((rgb[:, :, None, :] - centres[None, None]) ** 2).sum(-1)).min(-1)
    candidate = dist < tol
    labels, _ = ndimage.label(candidate)
    touching = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    background = np.isin(labels, touching[touching > 0])
    if clear_holes:  # background showing through gaps enclosed by the picture (between branches, inside a garland)
        tight = dist < tol * 0.6
        hl, n = ndimage.label(tight & ~background)
        sizes = ndimage.sum(np.ones_like(hl), hl, range(1, n + 1))
        big = np.flatnonzero(sizes >= clear_holes) + 1
        background |= np.isin(hl, big)
    fg = ~background
    fg = ndimage.binary_opening(fg, iterations=1)
    if close:  # halftone dots, stippling: the white between the dots belongs to the picture
        pad = close + 2
        fg = ndimage.binary_closing(np.pad(fg, pad), iterations=close)[pad:-pad, pad:-pad]
    if not clear_holes:
        fg = ndimage.binary_fill_holes(fg)
    return fg


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('outdir')
    ap.add_argument('--name', default=None)
    ap.add_argument('--max', type=int, default=420, help='longest side of each saved sticker')
    ap.add_argument('--min-area', type=int, default=1500)
    ap.add_argument('--tol', type=float, default=26, help='colour distance counted as background')
    ap.add_argument('--bg', default=None, help='background colour(s) as hex, e.g. ffffff or "ffffff,cccccc"')
    ap.add_argument('--close', type=int, default=0, help='bridge gaps up to about 2x this many px (halftone, stippling)')
    ap.add_argument('--clear-holes', type=int, default=0, metavar='PX',
                    help='also clear enclosed patches of plain background at least PX pixels big')
    ap.add_argument('--no-split', action='store_true', help='keep everything as one sticker')
    a = ap.parse_args()

    src = pathlib.Path(a.input)
    out = pathlib.Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    base = a.name or src.stem
    img = Image.open(src).convert('RGBA')
    fg = foreground_mask(img, a.tol, a.bg, a.close, a.clear_holes)
    # a soft 1px edge
    soft = ndimage.gaussian_filter(fg.astype(float), 0.7)
    rgba = np.asarray(img).copy()
    rgba[..., 3] = (np.clip(soft, 0, 1) * np.asarray(img)[..., 3]).astype(np.uint8)

    if a.no_split:
        pieces = [fg]
    else:
        labels, n = ndimage.label(ndimage.binary_dilation(fg, iterations=3))
        pieces = [(labels == i) & fg for i in range(1, n + 1)]
    pieces = [p for p in pieces if p.sum() >= a.min_area]
    pieces.sort(key=lambda p: (np.argwhere(p)[:, 0].min() // 80, np.argwhere(p)[:, 1].min()))
    if not pieces:
        sys.exit('nothing left after removing the background - try a smaller --tol or --no-split')

    for i, piece in enumerate(pieces, 1):
        ys, xs = np.where(piece)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        crop = rgba[y0:y1, x0:x1].copy()
        crop[..., 3] = np.where(piece[y0:y1, x0:x1] | (crop[..., 3] > 0), crop[..., 3], 0)
        crop[~ndimage.binary_dilation(piece[y0:y1, x0:x1], iterations=2), 3] = 0
        im = Image.fromarray(crop)
        scale = a.max / max(im.size)
        if scale < 1:
            im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
        name = base if len(pieces) == 1 else f'{base}-{i}'
        im.save(out / f'{name}.webp', 'WEBP', quality=86, method=6)
        print(f'{name}.webp  {im.width}x{im.height}')


if __name__ == '__main__':
    main()
