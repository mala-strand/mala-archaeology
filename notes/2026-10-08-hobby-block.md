# Hobby Block — 2026-10-08

**Time:** 01:00–02:00 BST  
**Focus:** Phase 3 true negative space — do dreams from the sparsest regions of seed-space resist archetype capture?

## Context

Oct 7's void exploration found that words far from all archetype centroids still produce archetypal dreams. The question became: is there *any* region of semantic space that the dream walk cannot pull into a basin? The "true negative space" hypothesis: words that are far from ALL seed words (not just centroids) and surrounded by diverse archetypes might resist capture.

## What Was Done

### 1. Classified all pending dreams (236–240 + older unclassified)

Ran the three backfill scripts on the full 240-dream corpus:
- `backfill_idf_hybrid.py` — 235 updated, 5 inserted
- `backfill_confidence.py` — confidence tiers for all 240
- `backfill_bodily_penalty.py` — penalized_primary for all 240

Corpus is now fully classified. Distribution: 16.7% HIGH, 25.8% MEDIUM, 29.2% LOW, 28.3% TENTATIVE.

### 2. Built `negative_space_sampler.py`

A density-based sampler that finds words in the sparsest regions of the seed-word manifold:
- For every qualified vocabulary word, compute average cosine distance to its K=20 nearest seed words
- Compute archetype diversity among those K nearest seeds (how many different archetypes surround it)
- Density score = avg_dist + 0.3 × diversity
- High score = far from seeds AND surrounded by mixed archetypes (not just on the edge of one territory)

**Top 5 negative space words:**
| Rank | Word | AvgDist | Diversity | Score | Nearest Archetypes |
|------|------|---------|-----------|-------|-------------------|
| 1 | manasses | 0.6324 | 0.55 | 0.7974 | power_political(4), abstract(3), power_divine(3) |
| 2 | galaad | 0.5988 | 0.60 | 0.7788 | abstract(3), power_political(2), domestic(2) |
| 3 | thinges | 0.6266 | 0.50 | 0.7766 | abstract(3), power_divine(3), legacy(3) |
| 4 | sonnes | 0.5870 | 0.60 | 0.7670 | conflict(2), craft(2), legacy(2) |
| 5 | juda | 0.5853 | 0.60 | 0.7653 | abstract(3), power_political(3), legacy(3) |

All are English words (archaic spellings, biblical names, Early Modern forms) with moderate corpus frequency.

### 3. Generated dreams from top 5 negative space seeds

| Dream ID | Seed | Archetype | Confidence | Nearest archetypes (seed-space) |
|----------|------|-----------|------------|--------------------------------|
| 236 | manasses | power_institutional | MEDIUM | power_political, abstract, power_divine |
| 237 | galaad | conflict | HIGH | abstract, power_political, domestic |
| 238 | thinges | temporal | TENTATIVE | abstract, power_divine, legacy |
| 239 | sonnes | power_divine | MEDIUM | conflict, craft, legacy |
| 240 | juda | power_political | HIGH | abstract, power_political, legacy |

**Key finding: STILL NO VOID DREAMS.** Even words from the sparsest, most diversely-surrounded regions of seed-space are pulled into archetypal basins within 300 steps. 3/5 are MEDIUM or HIGH confidence. Only `thinges` is TENTATIVE.

The most surprising result is `galaad` — its nearest seed archetypes were abstract/power_political/domestic, but the dream landed firmly in **conflict** (HIGH confidence, 95.3% relative margin). The walk found a basin that wasn't even among the 20 nearest seeds.

### 4. Updated project files

- `README.md` — added Phase 3 status, project structure entries, Phase 3 findings section
- `notes/negative_space_candidates.json` — top 200 candidates with scores

## Interpretation

The true negative space experiment confirms and extends the Oct 7 finding: **archetype structure is not just robust, it's inescapable.** The dream walk's stochastic dynamics are strong enough to pull any seed into a recognizable archetype, even when:
- The seed is far from all archetype centroids (vector void)
- The seed is far from ALL seed words (density void)
- The seed is surrounded by diverse, competing archetypes (no local basin)

This suggests that archetypes are not just clusters in seed-space — they're **attractors in the walk dynamics themselves.** The topology of the semantic graph (which words connect to which, across eras) constrains the walk more than the starting point does.

## Next Steps

1. **Quantify basin reach** — for each archetype, what's the maximum distance from its centroid where a seed still lands in it? Is there a "gravitational radius"?
2. **Walk topology vs seed topology** — the null-model test showed seed semantics don't constrain outcomes. Maybe the walk's *trajectory* (the actual sequence of words) is what determines archetype, not the seed. Could classify dreams by their walk vectors (mean of all visited word vectors) rather than their seed.
3. **Phase 3 synthesis** — with void, anti-archetype, and negative space all explored, it may be time to write a short synthesis note and decide whether Phase 3 has answered its question ("what lives in the voids?") or needs a new direction.
4. **Dream trajectory analysis** — compute the "semantic path" of each dream (centroid of visited words per era) and see if path-shape predicts archetype better than seed does.

## Files

- `worker/negative_space_sampler.py` — new script
- `notes/negative_space_candidates.json` — candidate list
- `notes/2026-10-08-hobby-block.md` — this file
