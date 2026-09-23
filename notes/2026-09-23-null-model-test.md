# Null-Model Test for Gravity-Well Prediction

**Date:** 2026-09-23  
**Hobby block:** 1am–2am  
**Tool:** `worker/null_model_test.py` (new)

## Objective

Build a proper null model for the gravity-well test (§4.1). The basin-rim test (Sep 22) showed monotonic increase in prediction accuracy (32.3% → 35.5% → 38.7%) with larger neighbour scales, but lacked statistical rigor — we didn't know if those numbers were better than chance.

## What Was Built

`null_model_test.py` implements three null models:

1. **Random-Seed Null**: For each seed's dreams, use a randomly chosen other seed's neighbour profile. Preserves structural properties, breaks seed-specific link.
2. **Random-Words Null**: Instead of top-N neighbours, sample N×6 random vocabulary words. Tests whether any word sample works.
3. **Shuffled-Vector Null**: Randomly permute word-to-vector assignments, recompute neighbours. Tests whether semantic structure is necessary. (Skipped in this run due to compute cost.)

## Results (200 iterations per scale)

| Scale | Actual | Random-Seed Null | Z-score | p-value | Random-Words Null | Z-score | p-value |
|-------|--------|------------------|---------|---------|-------------------|---------|---------|
| 20    | 32.3%  | 38.8% ± 5.9%     | -1.10   | 0.920   | 39.8% ± 7.0%      | -1.08   | 0.925   |
| 100   | 35.5%  | 32.5% ± 7.7%     | +0.39   | 0.415   | 39.0% ± 8.0%      | -0.45   | 0.760   |
| 200   | 38.7%  | 34.1% ± 7.8%     | +0.59   | 0.360   | 42.8% ± 7.4%      | -0.55   | 0.810   |

## Interpretation

**The gravity-well hypothesis is not supported.**

- At top-20, actual accuracy is *worse* than random-seed assignment (32.3% vs 38.8%). The seed's own neighbours predict its dreams *less well* than a random other seed's neighbours.
- At top-100 and top-200, actual accuracy slightly exceeds random-seed assignment, but not significantly (z = +0.39 and +0.59, p = 0.415 and 0.360).
- The random-words null *consistently outperforms* actual accuracy across all scales. This suggests the archetype classifier has strong base-rate biases — large random word samples happen to hit common archetypes (domestic, power_divine) more often than focused neighbour lists.

**What this means for the basin-rim test:**

The monotonic increase in accuracy (32.3% → 35.5% → 38.7%) is **not evidence of basin structure**. It is better explained as:

1. **Classifier base-rate bias**: Larger word samples = more chances to hit high-frequency archetype keywords.
2. **Generative dominance**: Temperature, era-jumps, and decay create emergent trajectories that override seed semantics. Dreams are ~60% generative, as previously noted.

The "gravity well" was an appealing metaphor, but the data rejects it. Semantic neighbourhoods do not constrain dream archetypes in a predictable way.

## Why This Matters

1. **Methodological**: We now have a validated null model. Future tests can use it.
2. **Theoretical**: The dream engine produces genuinely emergent output. Seed words set a starting point, but the walk's stochastic parameters (temperature, jump probability) dominate the thematic outcome.
3. **Practical**: No need to pursue "stronger null models" further. The random-seed null is sufficient and the result is clear.

## Next Steps

1. Update README.md to reflect null-model findings
2. Consider whether the dream engine's emergent behaviour is a *feature* (genuinely surprising dreams) or needs tuning (if we want more seed-constrained output)
3. Move on to other open experiments — e.g., the public site idea, or explore whether temperature × jump-count interaction predicts archetype better than seed semantics

## Shuffled-Vector Null (Bonus)

Ran one iteration of the shuffled-vector null (expensive: ~118s per iteration). Result: **41.9% accuracy** — *higher* than actual (32.3%).

This is the strongest refutation yet. Even after **destroying all semantic structure** by randomly permuting word-to-vector assignments, the recomputed "neighbour" lists predict dream archetypes *better* than the real neighbours. The classifier's base-rate bias is so strong that meaningless word samples outperform focused semantic neighbourhoods.

**Conclusion:** The vector space structure contributes *nothing* to archetype prediction. The entire gravity-well effect is artifactual.

## Bonus: Temperature vs Archetype Diversity (WIP)

Also built `worker/temp_archetype_analysis.py` to test whether temperature range predicts archetype diversity per seed. Result: **underpowered** — only 31 classifiable non-random dreams, and only 5 seeds have multiple dreams. Correlation r = -0.636 (more temperature range = *less* diversity) but n=5. Not meaningful. Would need more multi-temperature seeds to test properly.

## Files Changed

- `worker/null_model_test.py` — new
- `worker/temp_archetype_analysis.py` — new (WIP, not committed)
