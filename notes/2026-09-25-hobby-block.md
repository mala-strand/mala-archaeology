# Hobby Block — 2026-09-25

**Time:** 01:00–02:00 BST  
**Focus:** Parameter × Seed Drift interaction effects (follow-up to kinetic bias model)  
**Tool:** `worker/interaction_effects_analysis.py` (new)

## Objective

The kinetic bias model (Sep 24) found that temperature biases archetype distribution but cannot predict individual dreams. Natural next question: does this bias depend on the *seed word's semantic stability*? If a word is already semantically unstable across eras (high drift), maybe parameters matter less. If a word is stable (low drift), maybe temperature is the primary driver of archetype escape.

## What Was Built

`interaction_effects_analysis.py` stratifies dreams by seed drift magnitude (terciles), then computes temp-archetype and jump-archetype associations (Cramer's V) within each stratum. Uses 166/196 dreams with drift data (30 excluded: RANDOM_* seeds or words not in corpus vocabulary).

## Results

### Temp-Archetype Association by Drift Stratum (HIGH+MED confidence)

| Drift Stratum | N | Cramer's V | Interpretation |
|---------------|---|------------|----------------|
| Low drift (stable seeds) | 24 | **0.676** | **Medium-large** |
| Med drift | 18 | **0.676** | **Medium-large** |
| High drift (unstable seeds) | 27 | **0.471** | **Medium** |

In the full dataset (including LOW/TENTATIVE confidence):

| Drift Stratum | N | Cramer's V |
|---------------|---|------------|
| Low drift | 56 | 0.473 |
| Med drift | 55 | 0.576 |
| High drift | 55 | 0.254 |

**Finding: Temperature has a stronger archetype-biasing effect when the seed is semantically stable.** When the seed itself is already drifting across eras (high drift), temperature matters less. The seed's own semantic instability provides enough "escape energy" that added temperature doesn't change the archetype landscape as much.

### Jump-Archetype Association by Drift Stratum (HIGH+MED)

| Drift Stratum | V |
|---------------|---|
| Low | 0.611 |
| Med | 0.645 |
| High | 0.590 |

No clear interaction — jump probability biases archetypes similarly regardless of seed drift.

### Archetype Gradient Reverses by Stratum

**Low-drift seeds (stable):**
- High temp → power_personal(1.95), craft(1.81), conflict(1.61) — agency, making, struggle
- Low temp → power_divine(1.15), bodily(1.00), urban(0.95) — sacred, physical, material

**High-drift seeds (unstable):**
- High temp → power_political(1.59), abstract(1.53), urban(1.52) — secular authority, concepts, city
- Low temp → religious_cosmic(1.30), commerce(1.23), power_institutional(1.19) — cosmic order, trade, institutions

The *meaning* of temperature changes depending on seed stability. Low-drift + high temp = escape into personal agency. High-drift + high temp = escape into political/abstract territory.

### Structural Checks

- Drift × Temperature: r = 0.028 (no correlation — not a confound)
- Drift × Jump prob: r = 0.037 (no correlation)
- Drift × Actual jumps: r = 0.078 (negligible)

The interaction is genuine, not an artifact of drift correlating with parameters.

## Interpretation: The Escape Energy Model

Building on the kinetic bias model:

1. **Stable seeds have deep basins.** A low-drift word sits in a stable semantic neighborhood across all eras. Low temperature keeps the walk near this basin → concrete/material archetypes. High temperature provides the energy to escape → abstract/power archetypes.

2. **Unstable seeds are already on ridges.** A high-drift word has no consistent basin — its neighborhood changes completely across eras. The walk is already in an unstable region regardless of temperature. Parameters bias the direction of escape but less strongly.

3. **Temperature is escape energy, not direction.** Temperature controls *whether* the walk escapes the seed's basin. But when there's no basin (high drift), temperature has less to do. The seed's own instability is the dominant driver.

4. **Confidence filtering reveals structure.** The ALL-data pattern (low=0.473, med=0.576, high=0.254) is clearer than HIGH+MED (low=0.676, med=0.676, high=0.471) because low-confidence classifications add noise that differentially affects the high-drift stratum. High-drift seeds may produce more ambiguous dreams, leading to weaker classifier confidence and masking the true parameter signal.

## Why This Matters

1. **Theoretical:** We now have a three-factor model: seed semantics (gravity-well: rejected), parameters (kinetic bias: supported), and seed stability (escape energy: new). Dreams are emergent from the interaction of all three, with seed stability moderating parameter effects.

2. **Practical:** If you want a predictable dream archetype, choose a stable seed + extreme temperature. If you want maximum unpredictability, choose an unstable seed — temperature barely matters.

3. **Methodological:** The confidence-filtering finding suggests a general principle for generative analysis: low-confidence classifications don't just add noise — they add *differential* noise that can obscure interactions. Always report both raw and filtered results.

## Limitations

- Sample sizes within strata are modest (24–27 for HIGH+MED)
- Tercile boundaries are data-dependent; replication on a larger corpus needed
- The "escape energy" metaphor is interpretive, not mechanistic
- Some archetypes have n=1 within strata — gradient extremes are unstable

## Next Steps

1. **Visualize the interaction:** 2D heatmap of temp × drift_score colored by archetype distribution
2. **Build a proper multinomial model:** Logistic regression with temp × drift interaction term
3. **Test actual jump count × drift interaction:** Does the number of era jumps (not just probability) vary by drift?
4. **Replicate on expanded corpus:** Batch-generate 200 more dreams, stratify by drift, test if interaction holds
5. **Paper update:** Add escape energy model to draft

## Files Changed

- `worker/interaction_effects_analysis.py` — new
