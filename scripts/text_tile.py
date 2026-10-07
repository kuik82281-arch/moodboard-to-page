"""Seamless tiles of text used as texture: newspaper columns, a handwritten letter, a ledger.

    python text_tile.py OUT.webp --mode news [--size 640] [--font PATH] [--ink 3a2a1e] [--alpha 0.55] [--text FILE]
    python text_tile.py OUT.webp --mode news --cols 1 --width 300 --size 1200 --scale 2
        -> one column, drawn at double size: show it at background-size 150px auto; tiles side by side keep the gutter
    python text_tile.py OUT.webp --mode letter [--font "C:/Windows/Fonts/ITCEDSCR.TTF"]

news: justified columns of small serif text with a headline now and then, rules between columns.
letter: loose lines of script handwriting across the whole tile.
The tile is transparent; only the ink is drawn, so it lays over any paper. Lines sit on a grid that divides the tile
height and anything crossing an edge is drawn again on the opposite side, so the tile repeats without a seam. To
slant the writing, rotate the element that carries the tile (CSS), not the tile. The filler text is generic and
written for this; pass --text to use your own (public-domain or the project's own words). Needs Pillow.
"""
import argparse
import random

from PIL import Image, ImageDraw, ImageFont

FILLER = (
    "The evening post brought news of the harbour where the ships came in late with the tide and the lamps along "
    "the quay were lit one by one. In the market square the flower sellers folded their awnings while a band "
    "played in the gardens until the light was gone. Readers are reminded that the library will open on Sunday "
    "afternoons through the winter months. A letter from our correspondent describes the mountain road after the "
    "first snow, the inns full of travellers and the coaches waiting for the pass to clear. Notice is given that "
    "the bridge over the river will be closed for repairs. The theatre announces a new season of music and dance, "
    "with an orchestra of forty players and seats at moderate prices. Fine weather is expected for the regatta. "
    "Gardeners are advised to bring tender plants indoors before the frost. The observatory reports a clear sky "
    "and a bright comet low in the west an hour after sunset. Lost, a silver locket with a small portrait inside, "
    "a reward is offered on its return. The museum has received a gift of old maps and engravings of the coast."
)
HEADS = ["LATEST INTELLIGENCE", "THE WEATHER", "NOTICES", "ARRIVALS", "MUSIC & THE STAGE", "FROM ABROAD",
         "THE GARDEN", "CORRESPONDENCE"]
LETTER = (
    "My dearest, the days are growing short and the garden is full of late roses. I write by the window with the "
    "lamp lit early, and think of the evening we walked along the river. Do you remember the music from the open "
    "door of the little church, and how we stood until it ended. The clock in the hall has stopped again and no one "
    "minds. Write to me soon and tell me everything, the small things most of all. Ever yours, "
)


def font(path: str | None, size: int, fallbacks: list[str]) -> ImageFont.FreeTypeFont:
    for p in ([path] if path else []) + fallbacks:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


SERIFS = ["C:/Windows/Fonts/times.ttf", "/System/Library/Fonts/Times.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"]
SERIFS_BOLD = ["C:/Windows/Fonts/timesbd.ttf", "/System/Library/Fonts/Times.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"]
SCRIPTS = ["C:/Windows/Fonts/ITCEDSCR.TTF", "C:/Windows/Fonts/KUNSTLER.TTF", "C:/Windows/Fonts/segoesc.ttf", "/System/Library/Fonts/Supplemental/SnellRoundhand.ttc", "/System/Library/Fonts/Supplemental/Apple Chancery.ttf"]


def draw_wrapped(d: ImageDraw.ImageDraw, S: int, xy, text: str, f, fill, W: int | None = None) -> None:
    """Draw text, and again shifted by the tile size wherever it crosses an edge (W wide, S high)."""
    W = W or S
    x, y = xy
    l, t, r, b = d.textbbox((x, y), text, font=f)
    for dx in (0, -W, W):
        for dy in (0, -S, S):
            if r + dx > 0 and l + dx < W and b + dy > 0 and t + dy < S:
                d.text((x + dx, y + dy), text, font=f, fill=fill)


def words_forever(text: str, rnd: random.Random):
    words = text.split()
    i = rnd.randrange(len(words))
    while True:
        yield words[i % len(words)]
        i += 1


def news(a, rnd) -> Image.Image:
    S, ink, k = a.size, a.ink, a.scale
    W = a.width or S
    img = Image.new('RGBA', (W, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lh = 10 * k
    while S % lh:
        lh += 1
    body = font(a.font, lh - 2 * k, SERIFS)
    head = font(None, lh * 2 - 4 * k, SERIFS_BOLD)
    cols, gutter = a.cols, 12 * k
    margin = gutter / 2  # so tiles laid side by side keep the same gutter
    cw = (W - 2 * margin - (cols - 1) * gutter) / cols
    stream = words_forever(a.text or FILLER, rnd)
    put = lambda xy, t, f: draw_wrapped(d, S, xy, t, f, ink + (255,), W)
    for c in range(cols):
        x0 = margin + c * (cw + gutter)
        if a.rules:
            d.line([(x0 - gutter / 2, 0), (x0 - gutter / 2, S)], fill=ink + (90,), width=k)
        y = rnd.randrange(0, 8) * lh
        rows = S // lh
        row = 0
        while row < rows:
            if rnd.random() < 0.05 and row < rows - 4:
                t = rnd.choice(HEADS)
                hf = head
                while d.textlength(t, font=hf) > cw and hf.size > 8 * k:
                    hf = font(None, hf.size - 1, SERIFS_BOLD)
                put((x0 + (cw - d.textlength(t, font=hf)) / 2, (row * lh + y) % S), t, hf)
                row += 3
                continue
            words = []
            while True:
                w = next(stream)
                if d.textlength(' '.join(words + [w]), font=body) > cw:
                    break
                words.append(w)
            if not words:
                words = [next(stream)]
            gap = (cw - sum(d.textlength(w, font=body) for w in words)) / max(1, len(words) - 1)
            xx, yy = x0, (row * lh + y) % S
            for w in words:
                put((xx, yy), w, body)
                xx += d.textlength(w, font=body) + gap
            row += 1
    return img


def letter(a, rnd) -> Image.Image:
    S, ink = a.size, a.ink
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font(a.font, 30, SCRIPTS)
    lh = 40
    while S % lh:
        lh += 1
    stream = words_forever(a.text or LETTER, rnd)
    for row in range(S // lh):
        x = rnd.randrange(0, S)
        end = x + S - d.textlength('  ', font=f)
        while True:
            w = next(stream)
            wl = d.textlength(w + ' ', font=f)
            if x + wl > end:
                break
            draw_wrapped(d, S, (x % S, row * lh), w, f, ink + (255,))
            x += wl
    return img


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--mode', choices=['news', 'letter'], default='news')
    ap.add_argument('--size', type=int, default=640)
    ap.add_argument('--font', default=None)
    ap.add_argument('--width', type=int, default=None, help='news: tile width (default = --size, square)')
    ap.add_argument('--cols', type=int, default=4, help='news: columns per tile')
    ap.add_argument('--scale', type=int, default=1, help='news: 2 renders at double size for sharp text on phones')
    ap.add_argument('--no-rules', dest='rules', action='store_false', help='news: no rules between columns')
    ap.add_argument('--ink', default='3a2a1e')
    ap.add_argument('--alpha', type=float, default=0.55, help='overall ink opacity')
    ap.add_argument('--text', default=None, help='a text file to use instead of the filler')
    ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_intermixed_args()
    a.ink = tuple(int(a.ink[i:i + 2], 16) for i in (0, 2, 4))
    if a.text:
        a.text = open(a.text, encoding='utf-8').read()
    img = (news if a.mode == 'news' else letter)(a, random.Random(a.seed))
    r, g, b, al = img.split()
    img.putalpha(al.point(lambda v: int(v * a.alpha)))
    img.save(a.out, 'WEBP', quality=80, method=6) if a.out.endswith('.webp') else img.save(a.out)
    print(a.out, img.size)


if __name__ == '__main__':
    main()
