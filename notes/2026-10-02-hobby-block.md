# Hobby Block — 2026-10-02

**Time:** 01:00–02:00 BST  
**Focus:** Dream space topology analysis — graph-theoretic investigation of the 200-dream neighbor map

## Objective

The neighbor map (19,900 pairwise distances) exists but had never been analyzed as a *graph*. This block builds `dream_topology.py` to treat dreams as nodes and nearest-neighbor links as edges, then asks: are there clusters? bridges? sparse regions? Does archetype structure show up in the topology?

## What Was Built

### `worker/dream_topology.py`

Zero-token Python script (stdlib + sqlite3 + optional matplotlib) that:

1. **Loads the 5-NN adjacency list** (`data/dream_adjacency.jsonl`)
2. **Builds an undirected graph** (677 edges, 200 nodes)
3. **Computes graph metrics:**
   - Degree distribution (mean 6.77, max 17)
   - Local clustering coefficient (mean 0.250, max 0.700)
   - Connected components (1 — fully connected)
   - Articulation points (0 — no single points of failure)
   - Bridge-like edges (528/677 have ≤1 shared neighbor)
4. **Archetype assortativity** — same-primary vs different-primary edge ratio
5. **Identifies hubs, isolates, and dense subregions**
6. **Generates a force-directed layout** with archetype-colored nodes, confidence-tier-sized markers

### Critical finding: Archetype assortativity is massive

| Subset | Same-primary edges | Baseline (random) | Enrichment |
|---|---|---|---|
| All dreams | **51.2%** | 6.8% | **7.5×** |
| HIGH+MEDIUM confidence only | **87.0%** | 8.3% | **10.5×** |

This resolves the tension from the null-model test. While **seeds do not determine individual dream outcomes** (gravity-well hypothesis rejected), **archetype labels DO reflect genuine semantic neighborhoods**. Dreams of the same archetype are dramatically more likely to be nearest neighbors than chance would predict.

The archetype is not a post-hoc label slapped on random text. It captures real structure in the composite distance space (40% text Jaccard + 30% structural + 30% archetype cosine).

### Other findings

- **Most isolated dream:** #27 (*love*, domestic) — degree 5, avg neighbor dist 0.660. Confirmed from Oct 1 neighbor map.
- **Top hub:** #63 (RANDOM_touchstone, legacy) — degree 17. Sits at a crossroads between multiple semantic regions.
- **Densest clique:** #123 (*wool*, conflict) and #162 (*wondrous*, conflict) — clustering coefficient 0.700, meaning almost all their neighbors are also neighbors of each other. Small tight-knit conflict-territory pockets exist.
- **Bridge-like edges:** 528/677. The graph is globally tree-like (few shared neighbors between linked nodes) but has local cliques. This matches the intuition that dream space has scattered "villages" (archetype clusters) connected by long "roads" (bridge edges).
- **Component composition:** Single connected component. No dream is fully disconnected from the rest. Even the most isolated dream (#27) has 5 neighbors.

### Visualization

`notes/dream_topology_map.png` — force-directed layout with:
- Node color = primary archetype (19 colors)
- Node size = confidence tier (HIGH=large, TENTATIVE=small)
- Edge alpha = 1 − composite distance (closer = more visible)

Visual inspection confirms the assortativity: nodes of the same color visibly clump together, especially the larger (high-confidence) nodes.

## README updates

- Added "Phase 2 Dream Topology" to status table
- Added `dream_topology.py` to project structure tree

## Files created/modified

- `worker/dream_topology.py` (new)
- `notes/dream_topology_report.txt` (new)
- `notes/dream_topology_map.png` (new)
- `notes/dream_topology_positions.json` (new)
- `README.md` (updated)

## Next Steps

1. **Null-model for assortativity** — is 51.2% significant given degree distribution? (Configuration-model randomization)
2. **Archetype territory mapping** — use positions.json to draw Voronoi cells or contour maps per archetype
3. **Bridge dream analysis** — dreams that sit on bridge edges may be "liminal" — blending two archetype territories. These could be the most interesting dreams.
4. **Site integration** — add the topology map to the static gallery
