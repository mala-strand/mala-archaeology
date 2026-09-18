# Archaeology Hobby Block — September 13, 2026

## Work Completed

### 1. Built `keyword_idf_scorer.py` — IDF-weighted keyword scoring

Created a script that computes inverse document frequency (IDF) for all 255 archetype keywords from the Phase 1 corpus (101 books), then re-scores all 76 dreams with IDF-weighted keyword counting instead of raw integer counting.

**Key principle:** Distinctive keywords count more. "sacrament" (appears in 5 books, idf=3.0) contributes 3x more than "name" (appears in all 101 books, idf=0.0).

### 2. Result: Structural bias eliminated

| Metric | Raw Keyword | IDF-Weighted | IDF-Hybrid |
|--------|-------------|--------------|------------|
| Gini | 0.536 | 0.350 | 0.345 |
| Entropy | 3.560 | 4.014 | 4.020 |
| Unclassifiable | 32 (42%) | 2 (2.6%) | 0 (0%) |
| r(keyword_count, frequency) | +0.824 | +0.078 | +0.078 |

**The correlation between keyword list size and archetype frequency collapses from +0.824 to +0.078.** This is the principled fix that the Sep 12 normalization experiment pointed toward.

### 3. Distribution comparison

**Raw keyword** is dominated by large archetypes:
- domestic: 7, natural: 7, bodily: 6, unclassifiable: 32

**IDF-weighted** is much flatter:
- legacy: 8, conflict: 7, abstract: 7, power_political: 6, power_divine: 6, religious_moral: 6, natural: 5, commerce: 4, religious_devotion: 4, urban: 3, bodily: 3, chaos: 3

### 4. Flips analysis

75% of dreams flip classification vs raw keyword. The majority of flips are **unclassifiable → meaningful archetype**, which is a quality improvement, not noise.

Sample plausibility check:
- Dream #1 (seed: "lord"): raw=unclassifiable → idf=legacy. Contains "firstfruits", "crowned", "historical", "dwelling" — legacy words with high IDF.
- Dream #10 (seed: "immortal"): raw=unclassifiable → idf=religious_moral. Contains "prayer", "pious", "angels", "commandments", "glorified", "mortal", "evil" — all high-IDF religious terms.

### 5. Most/least distinctive keywords

Most distinctive (high IDF): bureaucracy, cosmic, equation, divine will, uncontrolled, civic, sinned, anarchy, damnation, mathematical.

Least distinctive (IDF ≈ 0): age, name, star, art, sea, read, sin — these appear in virtually every book.

## Key Insights

1. **Keyword count is a terrible proxy for semantic surface area.** A large archetype with 24 generic keywords (natural: tree, river, mountain, sky...) is not semantically 3x richer than a small archetype with 8 distinctive keywords (religious_moral: sin, repent, damnation, salvation...).

2. **IDF from the corpus is the right weighting.** It requires no hyperparameters (unlike sqrt/linear/log normalization), no manual tuning, and has a clear information-theoretic interpretation.

3. **The hybrid pipeline is now extremely strong:** IDF-weighted keyword primary → if unclassifiable, raw keyword fallback. 0% unclassifiable, flat distribution, no structural bias.

## What Needs Doing Next

- **Backfill IDF-hybrid classifications to DB.** The 76-dream corpus is still small, but the improvement is so dramatic (unclassifiable 42% → 0%) that it's worth persisting. Can be done in a future block.
- **Add IDF weights to `semantic_scorer.py`.** The existing semantic scorer has `compute_idf_weights` but it computes IDF from *dreams*, not from the *corpus*. The corpus-based IDF is more principled and should replace or augment it.
- **Generate more dreams.** Target 200+. The IDF-weighted pipeline scales naturally with more data.

## Files Changed

- `worker/keyword_idf_scorer.py` — new IDF-weighted keyword scorer and comparison script
