# Hobby Block — 2026-10-04

**Time:** 01:00–02:00 BST  
**Focus:** Bridge dream analysis — cross-archetype edges as liminality

## Objective

The topology blocks (Oct 2–3) proved archetype assortativity is real (z > 36–53). But 677 edges exist — what about the ones that *cross* archetype boundaries? This block builds `dream_bridge_analysis.py` to analyze "bridge" dreams: those on edges between different archetype territories.

## What Was Built

### `worker/dream_bridge_analysis.py`

Zero-token Python script (stdlib + sqlite3 + optional matplotlib) that:

1. **Loads the 5-NN adjacency list** and builds an undirected graph
2. **Classifies every edge** as same-archetype or cross-archetype (excluding unclassifiable dreams)
3. **Computes a "liminality score"** per dream: number of cross-archetype edges it participates in
4. **Compares bridge dreams vs non-bridge dreams** on confidence, temperature, jumps, seed drift, confidence margin
5. **Tests secondary archetype as bridge predictor**: does a dream's secondary archetype match its bridge targets?
6. **Generates two plots**: liminality histogram + top-10 bridge pair bar chart

### Critical findings

| Metric | Bridge Dreams | Non-Bridge | Interpretation |
|---|---|---|---|
| Count | 188 | 8 | Almost all dreams are liminal |
| Confidence margin | 0.310 | 0.640 | Liminality = uncertainty |
| Seed drift | 0.644 | 0.509 | Unstable seeds produce boundary-crossing dreams |
| Jump count | 20.2 | 27.9 | **Fewer jumps** → more liminal (counterintuitive) |
| Temperature | 1.34 | 1.39 | Slightly lower for bridge dreams |

**Edge split:** 50.8% same-archetype, 49.2% cross-archetype. The graph is almost perfectly bisected.

**Top bridge pairs:**
1. bodily + natural: 13 edges
2. natural + religious_moral: 9
3. bodily + power_divine: 8
4. abstract + commerce: 8

**Secondary archetype predicts bridge target 68.4% of the time.** The secondary label is not decorative — it genuinely forecasts which territories a dream touches.

### Most liminal dreams

| Dream | Seed | Primary | Liminality | Key bridges |
|---|---|---|---|---|
| #72 | RANDOM_creating | bodily | 10/12 | Almost entirely to natural |
| #63 | RANDOM_touchstone | legacy | 9/17 | Scattered across 7 archetypes |
| #25 | lord | power_political | 8/10 | conflict, religious_cosmic, bodily |
| #151 | final | natural | 8/9 | legacy, bodily, religious_moral |
| #7 | woman | religious_cosmic | 7/10 | conflict, power_divine, power_political |

Dream #72 is fascinating: "bodily" (the diagnosed structural artifact) bridges almost exclusively to "natural." The noisy archetype bleeds into its nearest semantic neighbor.

Dream #25 (*lord*, power_political) has secondary=conflict and bridges heavily to conflict dreams. The secondary archetype matches.

### Counterintuitive finding: fewer jumps = more liminal

Bridge dreams average 20.2 jumps vs 27.9 for non-bridge. This inverts the naive expectation that structural chaos (more jumps) would produce boundary-crossing dreams. Instead, **stable walks (fewer jumps) stay in semantic territory long enough to be classified, but that territory itself sits on a boundary.** High-jump dreams are so chaotic they either collapse into a single archetype or become unclassifiable — they don't linger on borders.

## Files created/modified

- `worker/dream_bridge_analysis.py` (new)
- `notes/dream_bridge_report.txt` (new)
- `notes/dream_bridge_analysis.png` (new)
- `README.md` (updated — status table + project structure)
- `PLAN.md` (updated — item #9 marked done)

## Next Steps

1. **Archetype territory mapping** — Voronoi/contour maps from positions.json
2. **Bridge dream deep-read** — actually read the text of top-5 liminal dreams, look for blended imagery
3. **Site integration** — add bridge report + plot to static gallery
4. **Paper draft update** — merge bridge findings into `phase2_synthesis.md`
