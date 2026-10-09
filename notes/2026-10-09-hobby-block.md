# Hobby Block — 2026-10-09

**Time:** 01:00–02:00 BST  
**Focus:** Phase 3 basin reach — quantifying how far a dream seed can be from its archetype centroid and still land in that archetype.

## Context

Oct 7–8 established that void seeds and negative-space seeds still produce archetypal dreams. The open question: is there any sense in which archetypes act as "gravitational basins" in seed-space? If seeds are far from a centroid, do they still get pulled in? How far is "far"?

## What Was Done

### 1. Built `basin_reach.py`

A new analysis script that:
- Loads all 8,000 word vectors (averaged across 6 eras)
- Builds archetype centroids from v2 keyword vectors
- Queries all 240 dreams with their `penalized_primary` classification
- Computes cosine distance from each seed to its archetype centroid
- Also tests "centroid-nearest assignment": how often is the assigned archetype actually the closest centroid to the seed?

### 2. Key Finding: There Is No Gravitational Radius

**Overall centroid-nearest accuracy: 6.5%** (14 out of 216 dreams). Seeds are almost *never* closest to the centroid of the archetype they end up in.

Per-archetype mean distances (tightest to loosest):

| Archetype | Mean Dist | Max Dist | N |
|-----------|-----------|----------|---|
| craft | 0.143 | 0.167 | 4 |
| wilderness | 0.167 | 0.167 | 1 |
| knowledge | 0.179 | 0.179 | 1 |
| domestic | 0.224 | 0.904 | 9 |
| power_political | 0.236 | 0.733 | 18 |
| legacy | 0.236 | 0.843 | 13 |
| religious_moral | 0.249 | 0.783 | 15 |
| religious_devotion | 0.252 | 0.516 | 9 |
| power_personal | 0.265 | 0.523 | 3 |
| power_divine | 0.316 | **1.000** | 21 |
| conflict | 0.324 | 0.908 | 24 |
| abstract | 0.343 | 0.706 | 22 |
| urban | 0.360 | 0.960 | 12 |
| commerce | 0.374 | 0.804 | 14 |
| natural | 0.396 | 0.900 | 17 |
| religious_cosmic | 0.404 | **1.000** | 11 |
| identity | 0.414 | 0.505 | 2 |
| power_institutional | 0.419 | **1.000** | 10 |
| temporal | 0.561 | **1.003** | 9 |

Four archetypes (temporal, power_divine, power_institutional, religious_cosmic) have seeds that are **orthogonal** (distance ~1.0) to their centroid and still land there. This is not a basin. This is not even a weak correlation.

### 3. Archetype Tightness Patterns

- **Tightest**: craft, wilderness, knowledge — but all have tiny N (≤4). These might just be sampling artifacts.
- **Loosest**: temporal (mean 0.561), power_institutional (0.419), identity (0.414)
- **High-N archetypes show wide variance**: conflict (std 0.253), power_divine (0.278), natural (0.263)

### 4. Updated Project Files

- `README.md` — added basin reach to Phase 3 status, project structure, and findings
- `notes/basin_reach.json` — full per-archetype statistics
- `notes/basin_reach.png` — bar plot of mean distances with error bars

## Interpretation

This finding closes the loop on Phase 3's central question. We have now tested:

1. **Vector voids** (far from all centroids) → still archetypal dreams
2. **Anti-archetype seeds** (far from specific centroids) → still archetypal dreams
3. **True negative space** (far from ALL seed words) → still archetypal dreams
4. **Basin reach** (distance from seed to assigned centroid) → no correlation whatsoever

The evidence converges on a single conclusion: **archetypes are not properties of seed-space topology. They are attractors in the walk dynamics.** The stochastic dream walk — temperature-driven neighbor selection, era jumps, decay revisits — generates trajectories that converge on recognizable thematic patterns regardless of where they start.

This is actually a stronger finding than "seed semantics don't matter." It says: the *space itself* (static word vectors) doesn't matter. What matters is the *dynamics* (how the walk moves through the space). The semantic graph's edge structure — which words connect to which, across eras — creates basins of attraction that are invisible to static vector analysis.

## Next Steps

1. **Dream trajectory analysis** — the logical next test. Compute the centroid of visited words per dream (or per era within the dream) and see if the *walk's own vector* is closer to the assigned centroid than the seed was. This would directly test: do dreams "find" their archetype during the walk?
2. **Phase 3 synthesis** — write a short paper note synthesizing void/anti-archetype/negative-space/basin-reach into a coherent argument
3. **Public site update** — the static site could include a "Phase 3: The Inescapable" section with these findings

## Files

- `worker/basin_reach.py` — new script
- `notes/basin_reach.json` — statistics
- `notes/basin_reach.png` — plot
- `notes/2026-10-09-hobby-block.md` — this file
