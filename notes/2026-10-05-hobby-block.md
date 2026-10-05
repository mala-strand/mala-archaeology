# Hobby Block — 2026-10-05

**Time:** 01:00–02:00 BST  
**Focus:** Archetype territory mapping + site integration

## Objective

The topology and bridge blocks (Oct 2–4) proved archetype structure is real and liminality is pervasive. But we still didn't have a *visual map* of the dream space. This block builds a territory map and integrates the Oct 2–4 findings into the public site.

## What Was Built

### `worker/dream_territory_map.py`

Zero-token Python script that:

1. Loads `dream_topology_positions.json` (200 dream 2D coordinates)
2. Queries the DB for IDF-hybrid primary archetype, confidence, seed, temperature, jumps
3. Computes liminality per dream: count of cross-archetype edges among 5-NN
4. Plots each dream as a scatter point colored by archetype
5. Draws convex hulls (dashed, low-alpha) for each archetype territory
6. Labels the top 10 most liminal dreams with dream IDs
7. Saves as `notes/dream_territory_map.png`

### Key findings from the map

- **14 archetypes** have enough dreams (≥3) to form convex hulls
- **Territories overlap extensively** — the space is not partitioned cleanly
- **Top 5 liminal dreams** all have liminality=5/5 (all nearest neighbors are cross-archetype):
  - #2 (identity, TENTATIVE, seed=touchstone)
  - #3 (religious_devotion, TENTATIVE, seed=sinned)
  - #7 (religious_cosmic, LOW, seed=woman)
  - #8 (legacy, LOW, seed=plus)
  - #9 (legacy, TENTATIVE, seed=mission)

- **All top-liminal dreams are LOW or TENTATIVE confidence** — liminality and uncertainty are the same phenomenon viewed through different lenses

### Site integration

Updated `site/index.html`:
- Added **Dream Topology** section with narrative, model box, territory map (Figure 5), bridge analysis plot (Figure 6)
- Added 3 new findings to the findings list (assortativity, bridge dreams, secondary archetype prediction)
- Updated status: Phase 2 complete, next = public deployment or Phase 3
- Copied `dream_territory_map.png` and `dream_bridge_analysis.png` into `site/`

## Files created/modified

- `worker/dream_territory_map.py` (new)
- `notes/dream_territory_map.png` (new)
- `site/dream_territory_map.png` (new, copy)
- `site/dream_bridge_analysis.png` (new, copy)
- `site/index.html` (updated — topology section + findings + status)
- `notes/2026-10-05-hobby-block.md` (this file)

## Next Steps

1. **Bridge dream deep-read** — read the actual text of top-5 liminal dreams, look for blended imagery
2. **Paper draft update** — merge topology/bridge findings into `phase2_synthesis.md`
3. **Public site deployment** — push to Render (or similar static host)
4. **Phase 3 sketch** — "generative drift": what words *don't* exist in any era? Can we find semantic voids?
