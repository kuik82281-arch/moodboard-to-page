"""Copperplate-etching Paris for a French romantic page: the Eiffel Tower (four lattice legs, the great arch, platforms
with railings, the shaft X-braced to the spire), the far quai with plane trees, Pont Alexandre III across the front
(arch, ribbed spandrels, balustrade, candelabra), the Seine hatched with ripples and the tower's broken reflection,
a hatched sky with birds. Plus: guinguette lights, a wrought-iron balcony tile, a Paris street lamp."""
import math, random, pathlib, sys

OUT = pathlib.Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
random.seed(7)
INK = '#3b3433'
f = lambda v: f'{v:.1f}'.rstrip('0').rstrip('.')


def line(x1, y1, x2, y2, w=.6, o=1, c=INK):
    return f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{c}" stroke-width="{w}" opacity="{o}"/>'


def path(d, w=.7, o=1, fill='none', c=INK):
    return f'<path d="{d}" fill="{fill}" stroke="{c}" stroke-width="{w}" opacity="{o}" stroke-linecap="round" stroke-linejoin="round"/>'


# ---------------------------------------------------------------- the hero
W, H = 400, 560
CX, BASE, TOP = 282, 452, 14
HT = BASE - TOP
y_of = lambda t: BASE - t * HT
hw = lambda t: 4.5 + 95 * (1 - t) ** 3.1       # half width of the tower at height t
parts = []
P = parts.append

# watercolour washes under the etching: a rose dusk at the horizon, a pale sun, the Seine in French blue
P(f'<rect width="{W}" height="{BASE}" fill="url(#dusk)"/>')
P('<circle cx="96" cy="300" r="46" fill="url(#sun)"/>')
P(f'<rect y="{BASE}" width="{W}" height="{H - BASE}" fill="url(#seine)"/>')
# sky: horizontal etched hatching, denser toward the top, broken here and there
for i, y in enumerate(range(6, 330, 4)):
    dens = max(0, 1 - y / 330)
    x = random.uniform(-10, 30)
    while x < W:
        seg = random.uniform(30, 120)
        if random.random() < .35 + dens * .6:
            # leave the tower's silhouette clear
            P(line(x, y, min(W, x + seg), y + random.uniform(-.4, .4), .45, .16 + dens * .22))
        x += seg + random.uniform(6, 30)
# birds
for bx, by, s in [(60, 200, 1), (84, 186, .8), (104, 206, .6), (40, 230, .7), (200, 90, .6)]:
    P(path(f'M{f(bx - 6 * s)} {f(by)}q{f(3 * s)} {f(-4 * s)} {f(6 * s)} 0q{f(3 * s)} {f(-4 * s)} {f(6 * s)} 0', .9, .7))

# white ground under the tower so sky hatching does not cross it
pts = [(CX - hw(t / 50), y_of(t / 50)) for t in range(0, 51)] + [(CX + hw(t / 50), y_of(t / 50)) for t in range(50, -1, -1)]
P('<path d="M' + ' L'.join(f'{f(x)} {f(y)}' for x, y in pts) + 'Z" fill="#fbf1ea" stroke="none" opacity=".55"/>')


def leg(side, t0, t1, lw0, lw1, n):
    """One leg between heights t0..t1: outer and inner edges, X bracing, a midline."""
    sgn = -1 if side == 'L' else 1
    ts = [t0 + (t1 - t0) * k / n for k in range(n + 1)]
    out = [(CX + sgn * hw(t), y_of(t)) for t in ts]
    inn = [(CX + sgn * (hw(t) - (lw0 + (lw1 - lw0) * (t - t0) / (t1 - t0))), y_of(t)) for t in ts]
    P(path('M' + ' L'.join(f'{f(x)} {f(y)}' for x, y in out), 1.2))
    P(path('M' + ' L'.join(f'{f(x)} {f(y)}' for x, y in inn), 1))
    for k in range(n):
        (ax, ay), (bx, by) = out[k], out[k + 1]
        (cx_, cy_), (dx, dy) = inn[k], inn[k + 1]
        P(line(ax, ay, dx, dy, .55, .9))
        P(line(cx_, cy_, bx, by, .55, .9))
        P(line(ax, ay, cx_, cy_, .5, .8))
        # shading on the right-hand leg: fine vertical hatching
        if side == 'R':
            for j in range(1, 4):
                u = j / 4
                P(line(ax + (cx_ - ax) * u, ay, bx + (dx - bx) * u, by, .3, .5))


def platform(t, h, inset=0):
    y = y_of(t)
    x0, x1 = CX - hw(t) - 6 + inset, CX + hw(t) + 6 - inset
    P(path(f'M{f(x0)} {f(y)}H{f(x1)}M{f(x0)} {f(y - h)}H{f(x1)}M{f(x0)} {f(y)}V{f(y - h)}M{f(x1)} {f(y)}V{f(y - h)}', 1))
    # a row of little arches under the platform and a railing over it
    n = int((x1 - x0) / 4)
    for k in range(n):
        xa = x0 + k * (x1 - x0) / n
        P(path(f'M{f(xa)} {f(y)}q{f((x1 - x0) / n / 2)} {f(-h * .7)} {f((x1 - x0) / n)} 0', .4, .8))
        P(line(xa, y - h, xa, y - h - 4, .35, .8))
    P(line(x0, y - h - 4, x1, y - h - 4, .6))


# lower legs and the great arch
leg('L', 0, .135, 30, 19, 9)
leg('R', 0, .135, 30, 19, 9)
ya = y_of(.02)
xl, xr = CX - hw(.02) + 29, CX + hw(.02) - 29
for k, o in enumerate([0, 4, 7]):
    P(path(f'M{f(xl + o * .4)} {f(ya)}Q{f(CX)} {f(y_of(.2) + o * 1.4)} {f(xr - o * .4)} {f(ya)}', 1 - k * .25))
for k in range(1, 18):  # voussoir rays along the arch
    u = k / 18
    x = (1 - u) ** 2 * xl + 2 * u * (1 - u) * CX + u * u * xr
    y = (1 - u) ** 2 * ya + 2 * u * (1 - u) * y_of(.2) + u * u * ya
    P(line(x, y, x, y + 4, .4, .7))
platform(.135, 9)
# middle legs, and the cross bracing between them
leg('L', .14, .27, 19, 13, 8)
leg('R', .14, .27, 19, 13, 8)
for k in range(8):
    t, t2 = .14 + .13 * k / 8, .14 + .13 * (k + 1) / 8
    a, b = CX - hw(t) + 19 - 6 * (k / 8), CX + hw(t) - 19 + 6 * (k / 8)
    a2, b2 = CX - hw(t2) + 19 - 6 * ((k + 1) / 8), CX + hw(t2) - 19 + 6 * ((k + 1) / 8)
    P(line(a, y_of(t), b2, y_of(t2), .35, .55))
    P(line(b, y_of(t), a2, y_of(t2), .35, .55))
platform(.27, 7, 2)
# the shaft: edges, inner leg lines, dense X bracing, finer toward the top
k, t = 0, .275
while t < .86:
    dt = .014 + .02 * (1 - t)
    t2 = min(.86, t + dt)
    for s in (-1, 1):
        P(line(CX + s * hw(t), y_of(t), CX + s * hw(t2), y_of(t2), 1.1))
        P(line(CX + s * hw(t) * .45, y_of(t), CX + s * hw(t2) * .45, y_of(t2), .55, .8))
        P(line(CX + s * hw(t), y_of(t), CX + s * hw(t2) * .45, y_of(t2), .4, .8))
        P(line(CX + s * hw(t) * .45, y_of(t), CX + s * hw(t2), y_of(t2), .4, .8))
    P(line(CX - hw(t2), y_of(t2), CX + hw(t2), y_of(t2), .4, .7))
    if k % 2:
        P(line(CX + hw(t) * .1, y_of(t), CX + hw(t2) * .4, y_of(t2), .3, .5))
    t, k = t2, k + 1
# the cabin, the lantern, the spire
yt = y_of(.86)
P(path(f'M{f(CX - 10)} {f(yt)}h20v-9h-20zM{f(CX - 7)} {f(yt - 9)}h14v-7h-14zM{f(CX - 12)} {f(yt)}h24', .9))
for xx in range(-9, 10, 3):
    P(line(CX + xx, yt, CX + xx, yt - 9, .35, .7))
P(path(f'M{f(CX - 4)} {f(yt - 16)}l4 -10l4 10z', .8))
P(line(CX, yt - 26, CX, TOP - 6, 1))
P(line(CX - 3, TOP + 6, CX + 3, TOP + 6, .6))

# the far quai: Haussmann blocks with mansard roofs, dormers, chimney pots and windows; plane trees in scribble
P(line(0, BASE + 2, W, BASE + 2, .9))
x0 = -6
while x0 < 196:
    bw, bh = random.uniform(24, 38), random.uniform(28, 46)
    top = BASE - bh
    P(path(f'M{f(x0)} {BASE}V{f(top)}H{f(x0 + bw)}V{BASE}', .6, .75))
    P(path(f'M{f(x0 - 1)} {f(top)}l3 -9H{f(x0 + bw - 2)}l3 9', .6, .75))
    for dx in range(4, int(bw) - 3, 7):
        P(path(f'M{f(x0 + dx)} {f(top - 1)}v-5h3v5', .4, .7))
    for cx1 in (x0 + 5, x0 + bw - 7):
        P(path(f'M{f(cx1)} {f(top - 9)}v-5h3v5M{f(cx1 - .5)} {f(top - 14)}h4', .45, .7))
    for wy in range(int(top) + 5, BASE - 6, 7):
        for dx in range(4, int(bw) - 3, 7):
            P(f'<rect x="{f(x0 + dx)}" y="{wy}" width="2.6" height="4" fill="{INK}" opacity=".35"/>')
    for wy in range(int(top) + 3, BASE, 7):
        P(line(x0, wy, x0 + bw, wy, .3, .25))
    x0 += bw + random.uniform(0, 2)
for tx in [10, 40, 74, 108, 142, 176, 214, 352, 384]:
    r = random.uniform(12, 17)
    for j in range(46):
        a_ = random.uniform(0, math.tau); d = r * math.sqrt(random.random())
        x = tx + math.cos(a_) * d * 1.1; y = BASE - 22 + math.sin(a_) * d * .7
        P(path(f'M{f(x)} {f(y)}q1.5 -2.5 3 0', .5, .65))
    for j in range(7):
        P(line(tx - r * .2 + j * r * .25, BASE - 18, tx - r * .6 + j * r * .25, BASE - 6, .3, .4))
    P(line(tx, BASE - 10, tx, BASE, .8, .7))

# the Seine: ripples, the tower's broken reflection
for y in range(BASE + 6, H, 3):
    x = random.uniform(-20, 10)
    while x < W:
        seg = random.uniform(8, 40)
        P(line(x, y, x + seg, y, .45, .25 + .35 * (y - BASE) / (H - BASE)))
        x += seg + random.uniform(4, 14)
for y in range(BASE + 8, BASE + 70, 4):
    spread = hw((y - BASE) / HT * .9) * .8
    P(line(CX - spread * random.uniform(.6, 1), y, CX + spread * random.uniform(.6, 1), y, .9, .28))

# Pont Alexandre III in front: deck, balustrade, a shallow arch, ribbed spandrels, candelabra
DY, AY = 488, 528
P(path(f'M-4 {DY}H{W + 4}M-4 {DY + 5}H{W + 4}', 1.2))
for x in range(0, W, 4):
    P(path(f'M{x} {DY - 2}q1.2 -3 0 -6q-1.2 -3 0 -4', .45, .85))
P(path(f'M-4 {DY - 12}H{W + 4}', 1))
P(path(f'M-10 {AY + 20}Q{W / 2} {DY + 2} {W + 10} {AY + 20}', 1.3))
P(path(f'M-10 {AY + 26}Q{W / 2} {DY + 10} {W + 10} {AY + 26}', .8))
for k in range(1, 40):
    u = k / 40
    x = -10 + u * (W + 20)
    y = (1 - u) ** 2 * (AY + 20) + 2 * u * (1 - u) * (DY + 2) + u * u * (AY + 20)
    if y > DY + 7:
        P(line(x, DY + 6, x, y, .5, .8))
        if k % 4 == 0:
            P(f'<circle cx="{f(x)}" cy="{f((DY + 6 + y) / 2)}" r="1.6" fill="none" stroke="{INK}" stroke-width=".5"/>')
for lx in [36, 140, 252, 366]:
    P(path(f'M{lx - 3} {DY - 12}h6v-4h-6zM{lx} {DY - 16}v-30M{lx - 9} {DY - 40}q9 -6 18 0M{lx} {DY - 44}v-6', .8))
    for gx, gy in [(lx - 9, DY - 42), (lx + 9, DY - 42), (lx, DY - 52)]:
        P(f'<circle cx="{gx}" cy="{gy}" r="2.6" fill="#fbf6ee" stroke="{INK}" stroke-width=".7"/>')
# shadow under the deck: crosshatching
for x in range(-4, W, 3):
    P(line(x, DY + 7, x + 6, DY + 15, .35, .45))
for x in range(-4, W, 5):
    P(line(x + 6, DY + 7, x, DY + 13, .3, .35))
# a fade into the paper at the bottom
hero = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" stroke-linecap="round">'
        f'<defs><linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset=".86" stop-color="#fff"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        '<linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c9d3e6" stop-opacity=".35"/><stop offset=".55" stop-color="#f3d9d3" stop-opacity=".25"/><stop offset="1" stop-color="#eeb9b0" stop-opacity=".75"/></linearGradient>'
        '<radialGradient id="sun"><stop offset="0" stop-color="#fbe3b8" stop-opacity=".95"/><stop offset=".55" stop-color="#f6c9b0" stop-opacity=".5"/><stop offset="1" stop-color="#f6c9b0" stop-opacity="0"/></radialGradient>'
        '<linearGradient id="seine" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9fb3d4" stop-opacity=".55"/><stop offset="1" stop-color="#6f87b0" stop-opacity=".45"/></linearGradient>'
        f'<mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask></defs>'
        '<style>line,path,circle{vector-effect:non-scaling-stroke}</style>'
        f'<g mask="url(#m)">' + ''.join(parts) + '</g></svg>')
(OUT / 'paris-etching.svg').write_text(hero, encoding='utf-8')

# ---------------------------------------------------------------- guinguette lights: a sagging wire with bulbs
GW, GH = 400, 64
g = [path(f'M-4 6Q{GW / 2} 52 {GW + 4} 6', .9), path(f'M-4 9Q{GW / 2} 44 {GW + 4} 10', .5, .5)]
for k in range(1, 14):
    u = k / 14
    x = -4 + u * (GW + 8)
    y = (1 - u) ** 2 * 6 + 2 * u * (1 - u) * 52 + u * u * 6
    g.append(line(x, y, x, y + 5, .6))
    g.append(f'<circle cx="{f(x)}" cy="{f(y + 11)}" r="9" fill="url(#glow)"/>')
    g.append(f'<path d="M{f(x - 2.4)} {f(y + 5)}h4.8l1 3a4 4 0 1 1-6.8 0z" fill="#f6e3b0" stroke="{INK}" stroke-width=".6"/>')
(OUT / 'guinguette.svg').write_text(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {GW} {GH}"><defs><radialGradient id="glow">'
    f'<stop offset="0" stop-color="#ffd98a" stop-opacity=".7"/><stop offset="1" stop-color="#ffd98a" stop-opacity="0"/>'
    f'</radialGradient></defs>' + ''.join(g) + '</svg>', encoding='utf-8')

# ---------------------------------------------------------------- a wrought-iron balcony (repeat-x tile)
B = [path('M0 2H80M0 5H80M0 44H80M0 47H80', 1.1)]
for x in (0, 40):
    B.append(line(x + .5, 5, x + .5, 44, 1.1))
    # a lyre of C-scrolls round a rosette
    c = x + 20
    B.append(path(f'M{c} 8c-12 2-14 14-6 16s8-6 3-7M{c} 8c12 2 14 14 6 16s-8-6-3-7', .9))
    B.append(path(f'M{c} 41c-12-2-14-12-6-14s8 5 3 6M{c} 41c12-2 14-12 6-14s-8 5-3 6', .9))
    B.append(f'<circle cx="{c}" cy="25" r="3.4" fill="none" stroke="{INK}" stroke-width=".9"/>')
    B.append(f'<circle cx="{c}" cy="25" r="1.1" fill="{INK}"/>')
    for s in (-1, 1):
        B.append(path(f'M{x + 20 + s * 16} 8v33', .7))
        B.append(path(f'M{x + 20 + s * 16} 24.5c{s * -3} -3 {s * -6} -1 {s * -9} 0', .6))
    B.append(path(f'M{x + 2} 5q2 -4 4 0M{x + 34} 5q2 -4 4 0', .6))
(OUT / 'balcony.svg').write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 49" stroke-linecap="round">' + ''.join(B) + '</svg>',
    encoding='utf-8')

# ---------------------------------------------------------------- a Paris street lamp (candélabre)
L = [path('M20 238h40v-8h-40zM24 230h32l-4-16h-24zM28 214c0-8 24-8 24 0', 1),
     path('M34 206h12v-130h-12z', 1)]
for x in (37, 40, 43):
    L.append(line(x, 200, x, 82, .45, .8))
L += [path('M30 76h20M32 70h16l-2 6h-12zM40 70v-12', 1),
      path('M26 58h28l-4-34h-20zM30 24l10-12 10 12M40 12v-6', 1),
      path('M40 58V24M33 58l2-34M47 58l-2-34', .5),
      path('M14 120c8-14 18-4 26-10M66 120c-8-14-18-4-26-10', .8),
      f'<rect x="31" y="27" width="18" height="29" fill="#ffe6a8" opacity=".55"/>',
      path('M34 214c-10 0-14-6-12-12M46 214c10 0 14-6 12-12', .7)]
(OUT / 'lamp.svg').write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 240" stroke-linecap="round" stroke-linejoin="round">'
    + ''.join(L) + '</svg>', encoding='utf-8')
for p in sorted(OUT.iterdir()):
    print(p.name, p.stat().st_size)
