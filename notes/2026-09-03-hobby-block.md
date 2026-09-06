# Archaeology Hobby Block — September 3, 2026

## Work Completed: Principled Tie-Breaking + Seed Decontamination

Implemented the two fixes identified in the Sep 2 validation study.

### Fix 1: Principled tie-breaking

Modified `classify_with_v2()` in `archetype_taxonomy_v2.py`:

- Count how many archetypes share the maximum score.
- If `max_score == 0` OR `top_count >= 2`, mark primary as `('unclassifiable', max_score)`.
- Removed the old behavior where `sorted()` on equal scores kept dict insertion order, arbitrarily privileging T1 archetypes over T2/T3.

Result: ties are now honestly reported instead of silently forced.

### Fix 2: Seed-token decontamination

Before scoring, `word_set.discard(seed_lower)` removes the seed word from the vocabulary being scored. This prevents circular self-fulfillment — e.g. `plus` being in the `abstract` keyword list meant every `plus` dream scored `abstract >= 1` by construction.

Removed the `plus` → `abstract` special-case heuristic (lines 132-134) since it is no longer needed and was the direct cause of the 3 contradictions.

### Fix 3: Backfill bug for zero-signal dreams

The backfill logic stored `None` when `score == 0`, even for legitimate `unclassifiable` labels. Fixed to persist `'unclassifiable'` when the classifier returns it, regardless of score.

---

## Re-measured Validation (all 53 dreams)

| Outcome | Count | Share |
|---------|-------|-------|
| **Clean** (unique top scorer, no tie) | 23 | 43% |
| **Tie** (unclassifiable due to tied top score) | 29 | 55% |
| **Zero-signal** (all scores zero) | 1 | 2% |
| **Contradiction** (label overrides its own evidence) | **0** | **0%** |

**Key improvement: contradictions dropped from 3 to 0.** The `plus` seed no longer forces `abstract`. The 3 previously contradictory dreams now honestly report ties.

**The 29 ties (55%) are not a bug — they are the taxonomy being honest.** Many dreams have genuinely sparse keyword overlap (e.g. `mission` with 6 archetypes tied at score 1). Before this fix, 21 of the 36 shifting dreams were ties broken arbitrarily by dict order. Now all 53 dreams are scored transparently.

---

## What This Means for the Paper

- The v2 taxonomy is now **auditable**: every classification is either a genuine unique winner or an honest tie.
- The `abstract` category is **no longer contaminated** by seed-in-keyword circularity. Its remaining 2 classifications (`storm` dreams #50, #53) are score-driven and legitimate.
- The method section can describe tie-handling as a feature, not a limitation: "When multiple archetypes score equally, the dream is marked unclassifiable rather than forcing an arbitrary label."

---

## Next Block Ideas

- **Paper outline**: Start drafting the method and results sections. The validation data is now clean enough to cite.
- **Expand keyword coverage**: 55% ties suggests the keyword lists are too sparse. A targeted expansion (e.g. adding more domestic/commerce terms) might resolve some ties into clean classifications — but only if the terms are genuinely present in the dream texts.
- **Generate new dreams with varied seeds**: Test whether the improved taxonomy behaves differently on fresh data.
