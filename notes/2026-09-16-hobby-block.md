# Archaeology Hobby Block — September 16, 2026

## Work Completed

### Chaos Archetype Investigation

Investigated why the "chaos" archetype has the lowest average jump count (11.8) and lowest average temperature (1.00) of all 19 archetypes — despite its name suggesting structural chaos.

**Method:** Recomputed IDF-weighted scores for all 4 chaos-classified dreams using `keyword_idf_scorer.py` directly. Examined raw vs IDF score breakdowns, keyword presence, and classification margins.

**Findings:**

| Dream | Seed | Jumps | Temp | Chaos Keywords | Raw Primary | IDF Primary | Stored Method |
|-------|------|-------|------|----------------|-------------|-------------|---------------|
| #3 | sinned | 9 | 0.8 | disorder (1×) | bodily (2) | chaos (0.46) | idf-keyword |
| #75 | gospel | 10 | 1.0 | wild, tumult, desolate (3×) | chaos (3) | chaos (1.72) | idf-keyword |
| #23 | soul | 13 | 1.3 | desolate (1×) | bodily (3) | chaos (0.83) | idf-keyword |
| #46 | lord | 15 | 0.9 | wild, confusion (2×) | chaos (2) | unclassifiable | raw-fallback |

**Key insights:**

1. **Only 1 of 4 is genuinely chaotic.** Dream #75 (gospel) has 3 chaos keywords and wins both raw and IDF. The others are edge cases.

2. **IDF overcorrection on Dream #23.** Raw scores: bodily=3, religious_moral=2, chaos=1. IDF flips it to chaos (0.83) because "desolate" has high IDF weight. The margin over bodily (0.57) is only 0.26 — not a confident classification.

3. **Dream #46 is raw fallback.** IDF couldn't classify it (power_divine and religious_devotion tied at 0.52). Raw scores pushed it to chaos because "wild" and "confusion" were present.

4. **Dream #3 has razor-thin margin.** Chaos wins by 0.046 over religious_devotion. One keyword ("disorder") determines the entire classification.

5. **The paradox is real and structural.** "Chaos" captures *thematic* content (wilderness, desolation, disorder) not *structural* chaos (high jumps, high temperature). The words "wild", "tumult", "desolate", "disorder" are rare in the corpus → high IDF → they overweight the classifier. Meanwhile, truly chaotic walks (high temp, many jumps) produce diverse vocabulary that gets classified as abstract, commerce, or power_personal.

**The name is a misnomer.** "Chaos" should perhaps be "wilderness" or "desolation" — it captures semantic emptiness and natural disorder, not walk instability. This aligns with the Sep 15 finding that chaos has the lowest jumps and lowest temperature.

**Top 10 highest-jump dreams are classified as:** temporal (54), conflict (51), natural (50), legacy (48), abstract (45), religious_moral (44), commerce (42), conflict (42), commerce (42). None are chaos. The chaos archetype simply does not correlate with structural chaos.

## What Needs Doing Next

- **Consider renaming "chaos" archetype.** "Wilderness" or "desolation" would be more accurate. Requires updating `archetype_taxonomy_v2.py` and re-backfilling.
- **Dream #23 reclassification.** Should probably be bodily or religious_moral, not chaos. IDF overcorrection.
- **Margin threshold.** The tiny margins on Dreams #3 and #46 suggest a "confidence threshold" would improve quality. If top-two margin < 0.2, flag as low-confidence or use semantic tie-breaker.
- **Re-run `dream_analysis.py` on n=200.** Still needs updating to use `idf_hybrid_primary` instead of old `primary_archetype` column.

## Files Changed

- `worker/_investigate_chaos.py` — temporary investigation script (to be removed or kept for reproducibility)
