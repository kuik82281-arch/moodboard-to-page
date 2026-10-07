"""Irregular edges for boxes: torn, burnt, scissor-cut, deckled - as CSS clip-paths or PNG masks / rims.

    python edge_shapes.py clip --kind torn --seed 3 [--sides trbl] [--depth 2.2] [--points 28]
        -> a `clip-path: polygon(...)` in percentages, for any box size
    python edge_shapes.py clip --kind torn --sides tr --burn bl --burn-size 16
        -> torn top and right, and a burnt bite out of the bottom-left corner (lay a dark radial-gradient of about the
           same size over that corner for the scorch: radial-gradient(ellipse 22% 22% at 0 100%, #2a1608 40%, ...))
    python edge_shapes.py mask --kind burnt --seed 3 --size 512x512 OUT.png
        -> an alpha mask PNG (white = keep) for `mask-image`
    python edge_shapes.py rim --kind burnt --seed 3 --size 512x512 OUT.png
        -> a scorch rim PNG (dark brown fading inward, transparent centre) to lay over a box

kinds: torn (soft ragged, fibrous), burnt (wavy, deeper bites), scissor (straight segments, sharp angles),
deckle (small even ripples). --sides chooses which sides are irregular (t r b l); the others stay straight.
Use several seeds in turn so no two boxes share an edge. Needs Pillow, numpy, scipy (mask / rim only).
"""
import argparse
import math
import random

KINDS = {
    #          depth %, points / side, roughness, smooth
    'torn': (2.4, 60, 0.7, 0),
    'burnt': (4.5, 22, 1.4, 2),
    'scissor': (2.6, 9, 1.0, 0),
    'deckle': (1.0, 46, 0.6, 1),
}


def side_offsets(n: int, depth: float, rough: float, smooth: int, rnd: random.Random) -> list[float]:
    """Inward offsets (percent) along one side: random walk, smoothed, kept within [0, depth]."""
    vals, v = [], rnd.uniform(0, depth)
    for _ in range(n + 1):
        v += rnd.uniform(-depth, depth) * 0.6 * rough
        v = min(depth, max(0.0, v))
        vals.append(v)
    for _ in range(smooth):
        vals = [vals[0]] + [(vals[i - 1] + 2 * vals[i] + vals[i + 1]) / 4 for i in range(1, len(vals) - 1)] + [vals[-1]]
    return vals


CORNERS = {'tl': (0, 0), 'tr': (100, 0), 'br': (100, 100), 'bl': (0, 100)}


def burn_corner(pts, corner: str, size: float, rnd: random.Random) -> list[tuple[float, float]]:
    """Replace the outline near a corner with a ragged, roughly circular bite (a corner burnt away)."""
    cx, cy = CORNERS[corner]
    waves = [(rnd.uniform(0.04, 0.1), rnd.uniform(2, 7), rnd.uniform(0, 6.3)) for _ in range(3)]

    def radius(t: float) -> float:
        return size * (1 + sum(a * math.sin(f * t + p) for a, f, p in waves))

    inside = [math.hypot(x - cx, y - cy) < radius(math.atan2(y - cy, x - cx)) for x, y in pts]
    if not any(inside):
        return pts
    k = inside.index(True)
    while inside[k - 1]:  # back up to where the bite starts, cyclically
        k -= 1
    k %= len(pts)
    pts, inside = pts[k:] + pts[:k], inside[k:] + inside[:k]
    j = inside.index(False)  # first point after the bite
    a0 = math.atan2(pts[-1][1] - cy, pts[-1][0] - cx)
    a1 = math.atan2(pts[j][1] - cy, pts[j][0] - cx)
    if a1 - a0 > math.pi: a1 -= 2 * math.pi
    if a0 - a1 > math.pi: a1 += 2 * math.pi
    n = 30
    arc = []
    for i in range(1, n):
        t = a0 + (a1 - a0) * i / n
        r = radius(t) + rnd.uniform(-0.35, 0.35)
        arc.append((min(100, max(0, cx + r * math.cos(t))), min(100, max(0, cy + r * math.sin(t)))))
    return arc + pts[j:]


def outline(kind: str, seed: int, sides: str, depth: float | None, points: int | None,
            burn: str | None = None, burn_size: float = 14) -> list[tuple[float, float]]:
    d0, n0, rough, smooth = KINDS[kind]
    depth = depth or d0
    n = points or n0
    rnd = random.Random(seed)
    pts: list[tuple[float, float]] = []
    # top: left -> right
    off = side_offsets(n, depth, rough, smooth, rnd) if 't' in sides else [0] * (n + 1)
    pts += [(i / n * 100, off[i]) for i in range(n + 1)]
    off = side_offsets(n, depth, rough, smooth, rnd) if 'r' in sides else [0] * (n + 1)
    pts += [(100 - off[i], i / n * 100) for i in range(1, n + 1)]
    off = side_offsets(n, depth, rough, smooth, rnd) if 'b' in sides else [0] * (n + 1)
    pts += [(100 - i / n * 100, 100 - off[i]) for i in range(1, n + 1)]
    off = side_offsets(n, depth, rough, smooth, rnd) if 'l' in sides else [0] * (n + 1)
    pts += [(off[i], 100 - i / n * 100) for i in range(1, n)]
    if burn:
        pts = burn_corner(pts, burn, burn_size, rnd)
    if kind == 'burnt':  # a couple of deeper bites
        for _ in range(2):
            k = rnd.randrange(len(pts))
            x, y = pts[k]
            cx, cy = 50, 50
            pts[k] = (x + (cx - x) * 0.06, y + (cy - y) * 0.06)
    return pts


def clip(args) -> None:
    pts = outline(args.kind, args.seed, args.sides, args.depth, args.points, args.burn, args.burn_size)
    print('clip-path: polygon(' + ', '.join(f'{x:.1f}% {y:.1f}%' for x, y in pts) + ');')


def raster(args, rim: bool) -> None:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter
    from scipy import ndimage

    w, h = (int(v) for v in args.size.split('x'))
    pts = outline(args.kind, args.seed, args.sides, args.depth, args.points, args.burn, args.burn_size)
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).polygon([(x / 100 * w, y / 100 * h) for x, y in pts], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(0.8))
    if not rim:
        m.save(args.out)
        return
    inside = np.asarray(m) > 127
    dist = ndimage.distance_transform_edt(inside)
    width = max(6, min(w, h) * 0.05)
    rng = np.random.default_rng(args.seed)
    noise = ndimage.gaussian_filter(rng.random((h, w)), 6)
    noise = (noise - noise.min()) / (noise.max() - noise.min() + 1e-9)
    a = np.clip(1 - dist / (width * (0.6 + noise)), 0, 1) * inside
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = 58, 34, 18  # scorched brown
    rgba[..., 3] = (a ** 1.6 * 235).astype(np.uint8)
    Image.fromarray(rgba).save(args.out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['clip', 'mask', 'rim'])
    ap.add_argument('out', nargs='?')
    ap.add_argument('--kind', choices=list(KINDS), default='torn')
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--sides', default='trbl')
    ap.add_argument('--depth', type=float, default=None)
    ap.add_argument('--points', type=int, default=None)
    ap.add_argument('--size', default='512x512')
    ap.add_argument('--burn', choices=list(CORNERS), default=None, help='burn a ragged bite out of this corner')
    ap.add_argument('--burn-size', type=float, default=14, help='bite radius, percent of the box')
    a = ap.parse_intermixed_args()
    if a.mode == 'clip':
        clip(a)
    else:
        if not a.out:
            ap.error('OUT.png is required for mask / rim')
        raster(a, rim=a.mode == 'rim')


if __name__ == '__main__':
    main()
