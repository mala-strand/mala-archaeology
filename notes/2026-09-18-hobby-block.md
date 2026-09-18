# Archaeology Hobby Block — September 18, 2026

## Work Completed

### 1. Built `backfill_confidence.py` — Persisted confidence tiers to the database

The Sep 17 analysis computed confidence tiers but left them in a text file. Today I made them queryable.

**What the script does:**
- Adds three columns to `dream_reflections`: `confidence_tier`, `confidence_margin`, `confidence_relative`
- Computes live IDF-weighted margins for all 200 dreams
- Populates all rows in a single batch update

**Why this matters:** Downstream analysis can now filter by confidence. No more guessing whether a classification is solid.

### 2. Verified the Sep 17 findings hold across the full corpus

The backfill reproduced the exact same distribution:
- HIGH: 31 (15.5%)
- MEDIUM: 47 (23.5%)
- LOW: 66 (33.0%)
- TENTATIVE: 56 (28.0%)

### 3. Ran confidence-filtered archetype analysis

**Excluding TENTATIVE dreams (n=144):**
- `bodily` collapses from 10 → 3 (70% of bodily classifications were weak signal)
- `unclassifiable` disappears entirely (all 3 were TENTATIVE)
- `chaos` drops from 4 → 2
- Distribution flattens further among the remaining archetypes

**Structural insight:** HIGH-confidence dreams average 21.5 jumps vs 20.1 for TENTATIVE. More structural chaos (jumps) does NOT mean lower classification confidence. The classifier is picking up on *semantic* coherence, not structural regularity.

**Method purity:** All 31 HIGH-confidence dreams are `idf-keyword` method. Zero raw-fallback dreams achieve HIGH. This validates the fallback-as-safety-net design — when IDF can't classify confidently, raw doesn't rescue it.

## Key Insights

1. **bodily is a weak-signal archetype in this corpus.** 7 of its 10 classifications are TENTATIVE, 2 LOW, 1 MEDIUM. No HIGH. Either the keywords are too generic ("hand", "face", "blood" appear in almost any text) or the semantic space doesn't carve "bodily" as a natural cluster.

2. **Raw-fallback is a genuine uncertainty signal.** All 6 raw-fallback dreams are TENTATIVE. The fallback isn't saving borderline cases — it's catching dreams where even IDF sees no clear winner.

3. **Confidence filtering sharpens rather than skews.** Removing TENTATIVE doesn't just drop noise; it reveals which archetypes have genuine signal vs. which are label-grabbers.

## What Needs Doing Next

- **Rename "chaos" archetype.** Evidence is overwhelming: 4/4 are low-confidence, and it captures thematic wilderness/desolation. "Wilderness" or "desolation" would be accurate. Requires taxonomy update + reclassification.
- **Re-run `dream_analysis.py` with confidence filtering.** Exclude TENTATIVE from corpus-wide stats to see if patterns (e.g., drift×jump correlation) sharpen.
- **Consider retiring `bodily` or merging it.** If 70% of classifications are tentative and zero are HIGH, maybe "bodily" doesn't exist as a distinct archetype in this semantic space.

## Files Changed

- `worker/backfill_confidence.py` — new script
- `README.md` — updated status line
- `data/archaeology_phase1_clean.db` — schema expanded, 200 rows updated
