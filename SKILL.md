---
name: moodboard-to-page
description: Restyle an existing web page or app in the style of reference images (a moodboard) - any style, e.g. vintage ephemera, punk zine, Korean soft, Chinese classical, business 商务, Hong Kong 港风, Western 欧美, French romantic 法式, sweetheart 甜心少女, Y2K, cottagecore. Use when the user shares one or more style reference images (or names a style) and asks to make a page look like that, "做成这种风格", "照着这个风格改", "装修一下"; also when a restyle came out generic ("像插件", "千篇一律", "流水线") and needs the style's real design language.
---

# Moodboard to Page

Read the **design language** of the reference images, not their surface texture, and rebuild the page in it. The usual
failure is copying one obvious trait (a paper texture, a gradient, a font) and laying it evenly over every box; the page
then looks like a theme plugin. A style is a set of decisions - material, edges, layering, text as decoration, type
personality, colour, motifs, and above all **where it breaks and where it stays whole** - and those decisions differ
completely between styles. Vintage tears and burns; Korean soft never breaks; punk breaks everything; Chinese classical
keeps symmetry and wholeness.

## Workflow

Work through these in order. Show the user the brief (step 1) before building.

### 1. Read the references → a style brief

Look at every reference image and fill in the twelve dimensions in [references/dimensions.md](references/dimensions.md)
(material, edges, layering, density, text-as-texture, typography, colour, motifs, light & depth, motion, **breakage**, **integration**).
For each, write what you *see* (concrete: "torn edges with a darker scorched rim on one corner", not "vintage feel")
and what it means for UI. End the brief with **Never** (what this style must not do - the generic moves that would
betray it) and **Signature** (the two or three moves that make it unmistakable).

**The user's references lead.** The worked briefs in [references/styles/](references/styles/) (vintage ephemera,
punk zine, Korean soft, Chinese classical, business, Hong Kong, Western editorial, French romantic, sweetheart girly)
show how the same dimensions give opposite answers for different styles; use them to know what to look for and as a
fallback when the user only names a style - never to overrule what their images show. If the references are thin,
ask for one or two more, or name what you are guessing.

Keep the brief short (one screen) and in the user's language. Wait for their go-ahead or corrections.

### 2. Map the page

List the page's parts (header, title, navigation, cards, lists, grid cells, buttons, inputs, empty space, background)
and decide for each what it *becomes* in this style - not "a card with the style's texture" but an object of the style's
world: a calendar grid in vintage can be newspaper scraps pinned together; in punk, a photocopied flyer with stamped
dates; in Korean soft, a sticker sheet; in Chinese classical, a lattice window. Write the map as a table.

Rules: keep every control working and readable (tap targets, contrast, focus); keep the DOM and logic; restyle with the
page's own classes and a new stylesheet of the page's own prefix. Decorative layers get `pointer-events: none`.

**Several pages in one style: vary by function, not by copy-paste.** Ask what each page is *for* (keeping time,
holding feelings, playing music, reading) and pick the style's sub-world that fits it - punk is a stencilled gym wall
for a timer, a riot grrrl notebook for feelings, a wheatpasted gig wall for music. Share the bones (a token sheet, the
breakage rule, the crisp controls) and change per page the ground, the accent colours, the title treatment and the
motifs. If two pages would look alike in a screenshot with the text blurred, they are not varied enough. Many briefs
list "Kinds by function" to start from; invent new kinds from the references when none fit.

### 3. Material and assets

- **Cut from the references** what can be reused (stickers, ornaments, textures): `scripts/cut_stickers.py` (background
  removal by flood fill from the border, split into pieces, trim, WebP).
- **Generate** what cannot be cut - torn / burnt / scissor-cut / scalloped edges, halftone, grain, paper fibres, rice
  paper, lattice: `scripts/edge_shapes.py` makes clip-path polygons and edge masks; the rest is CSS or a small canvas
  (see [references/techniques.md](references/techniques.md)).
- **Fonts**: choose by personality from the style's examples. Prefer fonts the device already has (iOS ships Didot,
  Bodoni 72, Baskerville, Snell Roundhand, Savoye LET, Songti SC, Kaiti SC ...) and fonts the project already bundles;
  ask before downloading new ones.
- Keep images small (stickers ~420 px, textures tileable ~512 px, WebP) and avoid heavy filters, blend modes and
  backdrop blur on large areas - phones run out of memory.

### 4. Build with variation

Apply the map. Vary within the style so nothing repeats mechanically: rotate scraps by different small angles, use
several edge shapes in turn, let some elements break the grid and some stay calm. The style's breakage rule decides how
much: follow the brief, not habit. Make the most important information the calmest.

**Rich, with a focus - not simple, not stacked.** A restyle is decoration, so it may and should be detailed, unless the
user asks for minimal. But richness is not more icons: a little balloon, a bow and a sprig scattered round a page look
cheap however many there are, and the same landmark used five times is stacking. Instead:

- **One hero per page**, large and worked in depth - the style's most evocative image of the page's subject (French →
  the Eiffel Tower over the Seine at dusk; Hong Kong → a neon street; Chinese classical → a mountain landscape scroll).
  Draw it with real detail: structure (lattice, windows, roofs, ripples), tone (hatching, washes, light), depth (near,
  middle, far). It should stop the eye. Generate it (procedural SVG, see techniques: "Illustration") when it cannot be
  cut from the references.
- **Supporting details carry meaning** and stay small: a stamp, a postmark, a lamp, string lights - each a real object
  from the style's world, not a generic shape.
- **Lines and frames become objects of the world.** A plain straight line or a box can be drawn without any skill, so it
  wastes the chance. Turn every line into something: a progress bar into a musical staff whose notes run as far as the
  value, a divider into overhead wires or a bridge's balustrade or a wrought-iron balcony, a separator into strung café
  lights; a box into a letter, a postcard, a ticket, a sign. Keep a plain line only where the style itself is plain
  (business).
- **A poster, not boxes on a background.** Aim for the look of a poster, where the text lives inside the picture: let
  the hero fill the whole page (enlarged, scrolling with it) and set the content into the scene. No rectangle may stay
  a plain card - each becomes an object that would lie in that world: a folded letter, a sticky note, a bill or
  receipt, a ticket, a luggage tag, a sticking plaster, a bandage, a label, a menu. Where text must sit on busy art,
  give it the scene's own atmosphere behind it (mist, light, a glow), never a box. Vary the objects; don't repeat one.

### 5. Look, compare, fix

Render the page (phone width first), screenshot it, and put it beside the references. Check each dimension of the brief
against what you see; check **Never** and **Signature**. Fix and repeat until it would pass as the same world as the
references. Then check it still works: every control reachable and legible, nothing decorative blocking taps.

## Pitfalls learned the hard way

- **Make the UI in the medium, don't lay boxes over it.** A translucent panel over a textured ground always reads as a
  plugin, however good the texture - and it gives itself away where it overhangs the paper under it. Ask of every
  block: how would this exist in the reference's world? In a newspaper style the calendar is *printed on the page*: a
  double rule round a boxed feature, ink type and hairlines straight on the same paper, no fill; only the hand-made
  marks (a red-pencil circle) sit on top. Pasted things (scraps, strips, clippings) are the *other* layer, and there are
  only these two.
- **Breathing room = rhythm plus loose placement.** Printed blocks keep a calm column rhythm with white space between
  them; added things are placed loosely - different sizes, angles from 2° to 9°, crossing the edges of blocks, a strip
  turned on its side - like someone pasted them by hand. Even, centred, equally spaced decoration looks generated.
  Never cover a tap target or a number with a pasted piece.
- **Print moves with its paper.** No fixed background textures or collages under printed UI - when the page scrolls the
  print slides over them and the illusion breaks. Scroll the ground with the content (`background-attachment: local`,
  or put it in the scrolling content) and keep fixed layers for things that really float.

- One texture over every box = plugin look. Material should vary by object, damage should be local.
- A decorative pseudo-element inside a stacking context (`position: fixed; z-index: -1` background layers) can never be
  lifted above content by its own z-index; give "above everything" ornaments their own element or layer.
- `border-image` needs a non-zero border width to paint; 9-slice textures seam - use the texture as background and an
  edge-only rim.
- Big blend modes / filters / backdrop blur / turbulence on phones crash Safari; prefer pre-baked images.
- Fonts must have a fallback stack that still fits the style.
- A cut-out whose subject runs off the image edge (a torn corner, a photo bleeding out) can lose half of itself if its
  colour is taken for background. `cut_stickers.py` ignores textured border colours, but always look at the cut-outs on
  a contrasting ground, and pass `--bg ffffff` when the subject is flat too.

## Files

- [references/dimensions.md](references/dimensions.md) - the eleven dimensions, the brief template
- [references/techniques.md](references/techniques.md) - how to build edges, textures, text-as-texture, layering, fonts
- [references/styles/](references/styles/) - worked briefs: vintage ephemera, punk zine (with kinds), Korean soft, Chinese classical, business, Hong Kong, Western editorial, French romantic, sweetheart girly
- `scripts/cut_stickers.py` - cut stickers out of reference images
- `scripts/edge_shapes.py` - torn / burnt / scissor / deckle edges as CSS clip-paths and PNG masks
- `scripts/examples/paris_etching.py` - a worked procedural hero illustration (etching + watercolour) and line objects
