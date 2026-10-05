# Hobby Block — 2026-10-03

**Time:** 01:00–02:00 BST  
**Focus:** Null-model validation of dream-space archetype assortativity

## Objective

The Oct 2 topology block found massive archetype assortativity (51.2% same-primary edges vs ~6.8% baseline). But is this significant? Could it be an artifact of degree distribution or graph structure? This block builds `dream_topology_null.py` to test two null models.

## What Was Built

### `worker/dream_topology_null.py`

Zero-token Python script implementing two complementary null models:

1. **Label Permutation** — preserve exact graph structure, shuffle archetype labels among nodes
2. **Configuration Model** — preserve degree sequence + label distribution, randomize edges via double-edge swaps (Markov-chain rewiring)

### Results

| Subset | Actual | Label-Perm Null | Z | Config-Model Null | Z |
|---|---|---|---|---|---|
| All dreams | 49.3% | 6.2% ± 0.9% | **47.4** | 5.2% ± 0.9% | **49.9** |
| Classified only | 50.8% | 6.6% ± 0.8% | **53.4** | 5.2% ± 0.9% | **53.4** |
| HIGH+MEDIUM conf | 85.3% | 7.1% ± 2.2% | **36.1** | — | — |

**All p < 0.0001.**

### Interpretation

Both null models reject every alternative explanation:
- **Label permutation significant** → The observed *graph structure* places same-archetype dreams closer than random label assignment would predict. Archetype labels are non-randomly arranged.
- **Configuration model significant** → The specific *wiring of edges* creates more same-label connections than a random graph with the same degree sequence would. The edges themselves are structured by archetype.
- **Both significant** → Archetype structure is a **genuine property of dream space topology**. Neither degree sequence nor graph structure alone can explain it.

This resolves the tension from the Sep 23 gravity-well rejection. While **seeds do not determine individual dream outcomes**, **archetype labels DO reflect genuine semantic neighborhoods**. The archetype is not a post-hoc label slapped on random text. It captures real structure in the composite distance space.

### HIGH+MEDIUM confidence subset

Restricting to well-classified dreams (HIGH or MEDIUM confidence) pushes assortativity to **85.3%** — almost 9 out of 10 edges connect same-archetype dreams. The z-score remains extreme (36.1) despite smaller n. Confidence and topological coherence are linked.

## Files created/modified

- `worker/dream_topology_null.py` (new)
- `notes/dream_topology_null_report.txt` (new)
- `README.md` (updated — status table + project structure)

## Next Steps

1. **Archetype territory mapping** — use positions.json to draw Voronoi cells or contour maps per archetype
2. **Bridge dream analysis** — dreams on bridge edges may be "liminal," blending two archetype territories
3. **Site integration** — add topology map + null model results to static gallery
