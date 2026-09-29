# Hobby Block — 2026-09-29

**Time:** 01:00–02:00 BST  
**Focus:** Build a filterable dream gallery for the public site  

## Objective

The site had index.html (landing) and drift.html (drift explorer) but only 3 hardcoded example dreams. This block builds a complete gallery of all 200 generated dreams, filterable by archetype and confidence tier, with seed-word search.

## What Was Built

### `worker/generate_dream_gallery.py`

A zero-token Python script that:
- Queries `dreams` + `dream_reflections` tables from the clean DB
- Parses dream text to strip headers and format era-jump markers
- Generates per-archetype hue-based badge colors (deterministic from archetype name)
- Truncates very long dreams to ~600 chars for card density
- Outputs a single static `site/dreams.html` (246KB, 200 cards)

### `site/dreams.html`

- **Stats bar:** total dreams, archetype count, confidence distribution
- **Archetype filters:** 20 archetype buttons with counts, "All" default
- **Confidence filters:** HIGH / MEDIUM / LOW / TENTATIVE buttons
- **Search:** live client-side filter by seed word
- **Card layout:** seed, era/temp/jumps/unique tags, excerpt with styled jump markers, archetype badge, confidence badge, margin score
- **Responsive:** stacks to single column on mobile
- **Zero dependencies:** pure HTML/CSS/JS, dark theme matching index.html and drift.html

### Cross-links updated

- `index.html` → linked to dreams.html in header meta + status paragraph
- `drift.html` → linked to dreams.html in header meta

### README updates

- Added Phase 2 Dream Gallery as ✅ BUILT
- Updated project structure to list all three site files
- Listed `generate_dream_gallery.py` in worker directory

## Design decisions

- **Static HTML over dynamic:** The site is meant to be hostable anywhere (GitHub Pages, Render, NAS static serve). No backend needed.
- **Client-side filtering:** All 200 cards are in the DOM; JS toggles `hidden` class. Fast enough at this scale, simpler than a data layer.
- **Truncate, don’t paginate:** For a browsable gallery, truncation keeps density high while still showing the dream’s texture. The full text is in the DB if anyone wants it.
- **HSL badge colors:** Each archetype gets a deterministic hue from `hash(name) % 360`. Visually distinguishes 20 archetypes without a manual color map.

## Next Steps

1. **Logistic regression** — formal model of drift × temperature interaction (still the open statistical question)
2. **Deploy** — the site now has substantial content across 3 pages; worth hosting
3. **Per-dream deep-dive pages** — if the gallery gets use, individual dream pages with full text, reflection, and neighbor analysis
