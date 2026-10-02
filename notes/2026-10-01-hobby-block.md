# Hobby Block — 2026-10-01

**Time:** 01:00–02:00 BST  
**Focus:** Build a dream-to-dream comparison tool — new analytical direction  

## Objective

The archaeology project has 200 dreams and rich classification data, but no tool to measure *distance between dreams*. This block builds `dream_compare.py` — a multi-dimensional comparison engine that treats each dream as a point in semantic+structural space.

## What Was Built

### `worker/dream_compare.py`

A zero-token Python script using only `sqlite3` + `sklearn`-free math that:

1. **Loads two dreams** by ID, random pair, or same-seed pair
2. **Computes four distance dimensions:**
   - **Structural**: temperature, jump count, unique words, length differences (normalized to [0,1])
   - **Text overlap**: Jaccard similarity on tokenized dream text, shared word count
   - **Archetype**: primary/secondary match, cosine similarity of penalized score vectors
   - **Era jumps**: jump marker extraction, shared jump eras, jump-pattern Jaccard
3. **Composite distance**: weighted blend (40% text, 30% structural, 30% archetype)
4. **Verdict**: interpretive label based on composite score

### Key design decisions

- **No sklearn dependency**: uses only `math.sqrt` and manual dot products. Keeps the script lightweight.
- **Parse-agnostic score parsing**: handles both JSON and pipe-delimited `penalized_scores` strings.
- **Jump marker regex**: matches `[1850-1900 → 1500-1700]` format used in stored dream text.
- **Same-seed random selection**: if no seed is given, picks a seed with ≥2 dreams and compares two random instances.

## Interesting findings from testing

### Same seed, same temp, different outcomes
`lord` at T=1.4 (both pre-1500):
- Dream #25: 15 jumps, primary=power_political
- Dream #21: 32 jumps, primary=legacy
- Composite distance: **0.643** — divergent

This powerfully illustrates the stochastic nature: identical parameters, same seed, same era, but the walk's randomness produces different archetype territories. The seed constrains the probability landscape but doesn't determine individual outcomes.

### Same seed, same primary, still distant
`lord` at T=1.4 (power_political) vs T=1.8 (power_political):
- Same primary archetype
- Text Jaccard: **0.025** (2.5% overlap)
- Archetype cosine: **0.463** (moderate similarity)
- Composite distance: **0.611**

The archetype label is a broad attractor — different stochastic walks can converge on the same archetype through completely different word paths. "Same primary" doesn't mean "similar dream."

### Temperature effect is in direction, not just instability
`lord` at T=0.9 (unclassifiable) vs T=1.8 (power_political):
- Archetype cosine: **0.000** (maximally different profiles)
- Jump counts: 15 vs 11 (similar)
- Composite distance: **0.731**

Temperature doesn't just increase jumps — it changes the *direction* of the walk's semantic trajectory. Low temp stays diffuse/unclassifiable; high temp locks into power_political territory.

## README updates

- Added `dream_compare.py` to project structure tree
- Added "Phase 2 Dream Comparison" to status table

## Batch analysis: all 45 same-seed pairs

Ran `_batch_compare.py` across every same-seed pair in the corpus:

| Stat | Value |
|------|-------|
| Pairs compared | 45 |
| Mean composite distance | **0.657** |
| Median | **0.667** |
| Range | 0.520 – 0.770 |
| Same primary archetype | **4/45 (8.9%)** |

### Most divergent pair
`storm` #51(T=1.8) vs #52(T=0.6): composite=0.770, different primaries, text overlap 2.6%

### Most similar pair
`RANDOM_sinned` #66(T=0.8) vs #67(T=1.3): composite=0.520, SAME primary, text overlap 3.1%

### Key insight: even identical parameters diverge
`man` #29(T=1.0) vs #30(T=1.0): composite=0.559, different primaries, text overlap 2.7%.

Same seed. Same temperature. Same everything. Still divergent. The stochastic walk's path independence is profound — the seed creates a probability landscape, but each walk samples a different trajectory through it.

## Dream Neighbor Map: all 19,900 pairs

Built `dream_neighbor_map.py` and computed the full pairwise distance matrix:

| Stat | Value |
|------|-------|
| Pairs | 19,900 |
| Mean composite distance | **0.677** |
| Median | **0.682** |
| Range | 0.432 – 0.940 |

### Most surprising finding
The 15 most similar pairs are **all different-seed pairs**. Same-seed pairs are generally MORE distant because stochastic walk divergence dominates seed identity.

Most similar: #169(*chanced*) vs #171(*studying*): composite=0.432, archetype cosine 0.933.

Most divergent: #27(*love*) vs #147(*drag*): composite=0.940.

### Most isolated dream
**Dream #27 (*love*)** — even its 5 nearest neighbors average 0.660 distance. It occupies a unique region of dream space.

### Most connected dreams
#169, #171, #198, #186, #20 — these have close neighbors and sit in dense regions of dream space.

Adjacency list saved to `data/dream_adjacency.jsonl` for future visualization.

## Phase 2 Synthesis Document

Wrote `paper/phase2_synthesis.md` — a readable narrative covering:
1. Decontamination and the clean DB
2. The classification crisis (3 attempts: keyword expansion → hybrid → IDF)
3. Confidence hierarchy and the BODILY artifact
4. Gravity-well hypothesis rejection (null-model test)
5. Kinetic bias model and refined escape energy model
6. Dream space neighbor map findings
7. What it all means: seeds constrain distributions, not trajectories

This can serve as the basis for updating the formal paper draft or as a standalone readable summary.

## Next Steps

1. **Visualization** — scatter plot of dreams in 2D/3D using composite distance or archetype vectors
2. **Site integration** — add "compare" button to dream gallery cards
3. **Paper draft update** — merge Phase 2 synthesis into `semantic_archaeology_draft.md`
4. **Dream space topology** — analyze adjacency list for clusters, bridges, sparse regions
