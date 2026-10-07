# Hobby Block — 2026-10-07

**Time:** 01:00–02:00 BST  
**Focus:** Phase 3 sketch — semantic voids: what lives in the negative space between archetype territories?

## Objective

The Oct 6 paper synthesis closed Phase 2 with a question: "what lives in the voids between clusters?" This block starts Phase 3 by operationalizing "void" and probing it with the dream engine.

## What Was Done

### `worker/void_explorer.py` — built

A zero-token script that identifies "void words" and generates dreams from them:

1. **Load vectors** — averages 100-dim era vectors per word (7,967 non-zero)
2. **Build archetype centroids** — mean vector of all seeded words per archetype (20 archetypes)
3. **Score voids** — for every unseeded word, compute cosine distance to nearest centroid
4. **Generate void dreams** — run `dream.py` with `--store` for top void candidates

**Methodological note:** The raw void list is dominated by foreign words (Finnish, French, Portuguese) and proper nouns from the corpus. These are naturally far from English archetype centroids but aren't conceptually interesting voids. A better filter is needed for future blocks — perhaps requiring minimum corpus frequency or English dictionary membership.

### Void dreams generated

Five dreams seeded from curated void candidates (English words with high void distance):

| Seed | Void dist | Nearest archetype | Reflection | Dream ID |
|------|-----------|-------------------|------------|----------|
| computer | 0.7049 | temporal | religious / domestic | #211 |
| holocaust | 0.6620 | bodily | temporal / commerce | #212 |
| regress | 0.6207 | power_personal | knowledge / religious | #213 |
| ascii | 0.5791 | identity | power / religious | #214 |
| entity | 0.5798 | craft | domestic / bodily | #215 |

**Key finding:** Void seeds do *not* produce void dreams. Even words far from all archetype centroids generate dreams that settle into recognizable archetypes. The void is in seed-space, not dream-space. This suggests the dream walk's stochastic dynamics are strong enough to pull any seed into an archetypal basin within 300 steps.

This is both a null result and a meaningful one: **archetype structure is robust even to adversarial seeding.** The territories aren't fragile — they're gravitational.

### Files modified

- `worker/void_explorer.py` — new script
- `notes/void_candidates.json` — top 200 void words with distances
- `notes/2026-10-07-hobby-block.md` — this file

## Next Steps

1. **Better void filter** — eliminate foreign words and proper nouns programmatically. Ideas: check against `/usr/share/dict/words`, require minimum co-occurrence count, or filter by IDF range.
2. **Run IDF-hybrid classification** on the 5 new void dreams so they enter the corpus with proper confidence tiers.
3. **Void visualization** — mark void seeds on the territory map. Do they cluster at the edges? Scatter uniformly? Form new regions?
4. **Anti-archetype experiment** — seed dreams from words that are far from *specific* archetypes (e.g., what's the most anti-religious word? most anti-domestic?). Generate and see if the walk still lands there.
5. **True negative space** — instead of "far from centroids," look for regions of the 2D embedding with no dreams at all. Sample words from those coordinates and see what happens.

## Concept note: what is a semantic void?

Three definitions emerged this block:

1. **Vector void** — a word whose average vector is far from all archetype centroids. These words exist in the vocabulary but orbit outside the gravitational wells. Most are foreign or proper nouns.

2. **Dream void** — a region of the 2D dream-space embedding where no dreams exist. This is topological negative space: not "unseeded words" but "unreachable territories."

3. **Archetype void** — a dream that resists all classification. Not TENTATIVE (weak signal) but genuinely anti-signal: every archetype scores near-zero. Does such a dream exist? The 5 void-seed dreams suggest probably not — the walk always finds a basin.

Phase 3 might be less about finding voids and more about **mapping the reach of archetype gravity.** How far does each archetype's influence extend? Where do multiple gravities cancel out? The void explorer is a probe, not a destination.
