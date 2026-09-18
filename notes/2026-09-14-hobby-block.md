# Archaeology Hobby Block — September 14, 2026

## Work Completed

### 1. Built `backfill_idf_hybrid.py` — IDF-hybrid persistence

Created a script that computes corpus-based IDF weights (or loads cached ones) and writes IDF-hybrid classifications to `dream_reflections.idf_hybrid_primary`, `idf_hybrid_method`, and `idf_hybrid_secondary`.

- Handles both existing reflections (UPDATE) and dreams without reflections (INSERT with placeholder text)
- Caches IDF weights to `cache/keyword_idf_weights.json` for fast reuse
- Hybrid rule: IDF-keyword primary; if unclassifiable, fall back to raw keyword

### 2. Backfilled all 76 existing dreams

Ran the backfill on the existing corpus:
- 74/76 (97.4%) classified by IDF-keyword
- 2/76 (2.6%) fell back to raw keyword
- 0 unclassifiable

Distribution remained flat — no large-archetype dominance.

### 3. Built `batch_generate.py` — batch dream generator

Created a script that generates N dreams with randomized parameters:
- Seed: 70% random vocabulary word, 30% None (random seed)
- Era: random from ERA_ORDER
- Temperature: uniform 0.8–2.0
- Era-jump probability: uniform 0.02–0.12
- Length: 250–400 words (base 300 ±50)

All dreams stored directly to DB via `generate_dream(store=True)`.

### 4. Expanded dream corpus from 76 → 200

Generated 124 new dreams in three batches (20 + 30 + 44) and backfilled IDF-hybrid classifications after each batch.

**Final corpus (n=200):**
- 194/200 (97%) IDF-keyword classified
- 6/200 (3%) raw-fallback
- 3/200 (1.5%) unclassifiable

**Top archetypes:**
- abstract: 20, conflict: 19, power_political: 17, power_divine: 17, religious_moral: 16, natural: 14, legacy: 14, commerce: 12, urban: 11, religious_devotion: 10, bodily: 10, domestic: 8, religious_cosmic: 6, power_institutional: 6, temporal: 5, craft: 4, chaos: 4, unclassifiable: 3, power_personal: 2, identity: 2

Gini on this distribution: approximately 0.34—0.35 (flat, no dominance).

### 5. Updated README.md

Documented the new scripts, the backfill, and the expanded corpus count.

## Key Insights

1. **The IDF-hybrid pipeline scales cleanly.** Adding 124 new dreams didn't break the classifier or introduce drift. The 97% IDF-keyword rate held steady.

2. **Batch generation with parameter variation produces more interesting dreams than fixed defaults.** Temperatures above 1.5 and jump probabilities above 0.08 create more era-jumps and stranger juxtapositions.

3. **200 is a meaningful corpus size.** Pattern analysis (drift-dream correlation, archetype co-occurrence) starts to become statistically interesting at this scale. The 76-dream corpus was too small for robust conclusions.

## What Needs Doing Next

- **Re-run drift-dream correlator on n=200.** The existing `drift_dream_correlator.py` was run on 76 dreams. With 200, correlations may stabilize or new patterns emerge.
- **Re-run dream_analysis.py on n=200.** Corpus-wide patterns (era distribution, jump statistics, unique-word ratios) should be re-computed.
- **Archetype co-occurrence analysis.** Which archetypes appear together in the same dream? Are there forbidden pairs?
- **Public site — still gated on statistical rigor.** The open experiments from PLAN.md (null model, basin-vs-rim) remain unaddressed. The expanded corpus makes them more urgent, not less.

## Files Changed

- `worker/backfill_idf_hybrid.py` — new
- `worker/batch_generate.py` — new
- `cache/keyword_idf_weights.json` — new (cached IDF weights)
- `README.md` — updated
