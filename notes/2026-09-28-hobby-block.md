# Hobby Block — 2026-09-28

**Time:** 01:00–02:00 BST  
**Focus:** Build a semantic drift explorer page for the public site  

## Objective

Yesterday's block built the site skeleton. Today's block adds the first substantial content beyond the landing page: a browsable drift explorer that surfaces the actual Phase 1 findings in a readable, narrative form.

## What Was Built

`site/drift.html` — a companion page to the main gallery:

- **Era navigation:** jump links to each of the 5 era transitions
- **Curated drift tables:** top words per transition with drift scores and interpretations
- **Pattern boxes:** narrative summaries for each period (Great Secularization revised, Political Secularization, Professionalization of Virtue)
- **Neighbor deep-dives:** side-by-side neighbor comparison for `immortal` and `crowded` — the two most interpretively rich cases from FINDINGS.md
- **Methodology section:** concise explanation of how drift scores are computed
- **Cross-links:** linked from index.html header and status section

### Design choices

- Same dark theme as index.html (`#0d0d0f` bg, `#c9a96e` accent) for consistency
- Tables for drift data — dense but scannable
- Neighbor boxes use pill-style tags for visual distinction
- No JS, no frameworks — pure static HTML/CSS

### Content sourcing

The raw DB drift queries return many artifacts (French words, proper nouns, OCR noise). Rather than surface uncleaned data, I used the curated findings from `FINDINGS.md` (which were already interpreted and verified) and supplemented with a handful of clean entries from the DB. The neighbor data for `lord`, `immortal`, and `crowded` comes from the Phase 1 deep-dive analysis.

### Files changed/created

- `site/drift.html` — new
- `site/index.html` — linked to drift.html in header + status section

## Next Steps

1. **Expanded dream gallery** — more than 3 cards, perhaps filterable by archetype or confidence tier
2. **Logistic regression** — formal model of drift × temperature interaction
3. **Deploy** — the site is now substantial enough to host; Render or GitHub Pages
