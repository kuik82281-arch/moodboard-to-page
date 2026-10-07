# Moodboard to Page

A [Claude Code](https://claude.com/claude-code) skill that restyles an existing web page in the style of your
reference images: vintage ephemera, punk zine, Korean soft, Chinese classical, business, Hong Kong, Western
editorial, French romantic, sweetheart girly, or anything else you show it.

It reads the **design language** of the references instead of copying a texture. Material, edges, layering, density,
text as texture, typography, colour, motifs, light, motion, where things break and how content belongs to its medium
are twelve dimensions in all. It then rebuilds the page from them, without touching its logic.

## What it insists on

- **Your references lead.** The bundled style briefs are only examples and a fallback when you just name a style.
- **Vary by function.** When several pages share one style, each gets its own sub-world based on what the page is for.
  For punk, a timer becomes a stencilled gym wall, a diary a riot grrrl notebook, a music page a wheatpasted gig wall.
  Pages are never one kit copied over and over.
- **Rich, with a focus.** Each page gets one large, finely worked hero image, such as an etched Eiffel Tower over the
  Seine at dusk. Small icons stacked up do not count as richness.
- **Lines and boxes become objects.** A progress bar becomes a musical staff. A divider becomes overhead wires, string
  lights or a wrought-iron balcony. A card becomes a folded letter, a sticky note, a café bill or a ticket.
- **A poster, not boxes on a background.** The scene fills the page and text is set into it.
- **Controls stay usable.** Tap targets, contrast and focus all keep working.

## Install

```bash
git clone https://github.com/kuik82281-arch/moodboard-to-page ~/.claude/skills/moodboard-to-page
```

Or put it in a project's `.claude/skills/`. Then share a few reference images with Claude Code and ask it to restyle a
page ("make this page look like these", "做成这种风格").

The helper scripts need Python 3 with `numpy`, `Pillow` and `scipy`:

```bash
pip install numpy pillow scipy
```

## Contents

| Path | What |
|---|---|
| `SKILL.md` | The workflow: brief → page map → material → build → compare, plus pitfalls learned the hard way |
| `references/dimensions.md` | The twelve dimensions and the brief template |
| `references/techniques.md` | Edges, textures, text as texture, layering, fonts, procedural illustration, lines and containers as objects |
| `references/styles/` | Worked briefs, each with kinds by function and hero/line ideas |
| `scripts/cut_stickers.py` | Cut stickers out of reference images (background removal, split, trim, WebP) |
| `scripts/edge_shapes.py` | Torn / burnt / scissor / deckle edges as CSS `clip-path` and PNG masks |
| `scripts/text_tile.py` | Newsprint and handwriting tiles for text-as-texture |
| `scripts/examples/paris_etching.py` | A worked procedural hero: copperplate-etched Paris tinted in watercolour, with string lights, a balcony rail and a street lamp |

---

一个 Claude Code skill：照着你给的参考图（复古做旧、朋克、韩系、中式古典、商务、港风、欧美、法式浪漫、甜心少女……）
重新装修已有的网页。它读的是风格的设计语言，不是照搬某个纹理。它坚持几条原则：以你的参考图为准；同一种风格放到不同页面，
按页面的用途变化；要有一个放大、画细的主画面；线条和方框都要变成那个世界里的东西；整页要有海报的感觉。

## License

MIT
