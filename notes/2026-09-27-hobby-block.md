# Hobby Block — 2026-09-27

**Time:** 01:00–02:00 BST  
**Focus:** Build a static HTML gallery for the archaeology project — first step toward the public site  

## Objective

The parameter landscape plots from Sep 26 are visually compelling but buried in a local notes directory. This block surfaces them into a browsable page that could eventually be deployed (Render, GitHub Pages, or similar). Also include example dreams and a narrative summary of the escape energy model.

## What Was Built

`site/index.html` — a single-page dark-themed static gallery:

- **Header:** project title, subtitle, corpus stats
- **Stats grid:** 101 texts, 8,121 vocab, 48K vectors, 38,515 drift scores, 200 dreams, 19 archetypes
- **Corpus figure:** era coverage from the paper
- **Escape energy model:** concise explanation with the key twist (temperature effect reverses by drift stratum)
- **Three parameter landscape plots:** scatter, heatmap, confidence — each with captions
- **Example dreams:** three cards (`creating`, `storm`, `touchstone`) with excerpts, jump annotations, and archetype badges
- **Findings in brief:** bullet summary of the major results (gravity-well rejection, kinetic bias, IDF weighting, wilderness rename)
- **Status + next steps**

### Design choices

- Dark theme (`#0d0d0f` bg, `#c9a96e` accent) — matches the project's austere aesthetic
- No frameworks, no JS — pure HTML/CSS for zero maintenance
- Responsive grid for dream cards
- All images self-contained in `site/` directory

### Files changed/created

- `site/index.html` — new
- `site/parameter_landscape_scatter.png` — copied from notes
- `site/parameter_landscape_heatmap.png` — copied from notes
- `site/parameter_landscape_confidence.png` — copied from notes
- `site/figure_0_era_coverage.png` — copied from paper
- `site/figure_3_archetype_distribution.png` — copied from paper
- `README.md` — updated with site entry in status table + project structure
- `.gitignore` — added `.venv/`

## Next Steps

1. **Deploy** — push to a branch and host on Render or GitHub Pages. The page is entirely static; any static host works.
2. **Expand dream gallery** — add more dream cards, perhaps filterable by archetype or confidence tier
3. **Add drift explorer** — interactive (or at least browsable) drift scores for individual words
4. **Paper figure cleanup** — the three parameter plots need axis label font size increase for publication
