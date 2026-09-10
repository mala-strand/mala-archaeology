# Archaeology Hobby Block — September 9, 2026

## Work Completed

### 1. Built `expand_archetypes.py` — data-driven keyword expansion

Wrote a script that uses semantic neighbors from the vector database to propose new keywords for each archetype. For each existing keyword in the v2 taxonomy, it finds the top 15 semantic neighbors in the 1850-1900 era. A candidate is proposed if it appears as a neighbor to at least 3 existing keywords within that archetype.

This is exactly the kind of thing the archaeology project was built for — using semantic vectors to discover related words, rather than guessing manually.

### 2. Curated and applied keyword expansion to v2 taxonomy

From the script's proposals, manually filtered out generic action/position words ("down", "stood", "came", "went", "looked", etc.) that are neighbors to everything by frequency, not by semantic affinity. Added 43 curated keywords across 10 archetypes:

| Archetype | Added | Notable |
|---|---|---|
| bodily | +5 | hands, arm, arms, bones, eyes |
| domestic | +7 | corner, floor, sat, sitting, chair, children, sister |
| conflict | +4 | army, campaign, fought, retreat |
| knowledge | +4 | reading, writing, written, note |
| natural | +10 | rain, cloud, clouds, mist, snow, trees, island, shadows, shining, shore |
| power_divine | +3 | faith, bless, prayers |
| religious_devotion | +1 | forgive |
| religious_moral | +2 | faith, spirit |
| commerce | +6 | bought, buying, goods, sold, paid, worth |
| urban | +1 | corner |

**Before:** 224 keywords across 19 archetypes  
**After:** 267 keywords (+43)

### 3. Reclassified all 53 existing dreams + generated 3 new ones

Ran v2 backfill on all existing reflections. **Unclassifiable rate dropped from 57% to 47%** — a 10 percentage point improvement from keyword expansion alone.

Generated 3 new dreams with high-drift seeds:
- **Dream 74** (touchstone, T=1.3): classified as **natural** — hills, streams, oak, rain
- **Dream 75** (gospel, T=1.0): classified as **chaos** — tumult, barbarous, desolate, wreck (unexpected for a gospel seed, but the dream cut loose)
- **Dream 76** (valiant, T=1.5): classified as **power_political** — king, empire, highness, reign, commanded (perfect fit)

## Key Insights

1. **Semantic neighbor expansion works.** The proposals were surprisingly good — most candidate words genuinely belonged to their archetype. The noise was mostly high-frequency generic verbs, which are easy to filter.

2. **The 47% unclassifiable rate is still high, but it's moving.** To push it lower, the scoring method itself may need to change — keyword counting is binary and brittle. A semantic-similarity approach (cosine distance between dream words and archetype centroids) would be more robust.

3. **Seed decontamination continues to work well.** Dreams like "plus" and "love" no longer self-fulfill their categories because the seed word is removed from scoring.

## What Needs Doing Next

- **Semantic-similarity scoring** — instead of keyword counting, compute average cosine similarity between dream words and archetype keyword vectors. This would catch related words that aren't exact keyword matches.
- **More keyword expansion** — run the script at lower thresholds and manually curate further.
- **Public site** — still waiting for paper to be "truly solid" before building the Render site.

## Files Changed

- `worker/expand_archetypes.py` — new
- `worker/archetype_taxonomy_v2.py` — +43 keywords across 10 archetypes
- `data/archaeology_phase1_clean.db` — 3 new dreams (74-76), updated v2 classifications for all 53 reflections
