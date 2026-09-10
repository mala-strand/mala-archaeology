# Archaeology Hobby Block — September 10, 2026

## Work Completed

### 1. Built `semantic_scorer.py` — four semantic scoring approaches for dream classification

Wrote a comprehensive semantic scoring module to address the 47% unclassifiable rate in v2 archetype classification. Explored four distinct approaches:

**Approach A: Standard centroid**
- Build archetype centroids from keyword vectors, score dreams by average cosine similarity
- **Result:** 0% unclassifiable, but EVERY dream classified as `craft` because craft keywords (work, make, write) are so common that its centroid ≈ global corpus centroid
- **Lesson:** Centroid methods are biased toward archetypes with high-frequency generic keywords

**Approach B: Contrastive word-level**
- For each dream word, compute similarity to all archetype centroids. Contribution = sim(archetype) - mean_sim(all archetypes)
- **Result:** 6.6% unclassifiable, but rescued dreams ALL classified as `legacy`
- **Root cause:** Legacy keywords (name, memory, remember, historical) appear in almost every dream and are semantically distinct from other archetypes. The contrastive boost from ubiquitous distinctive words overwhelms everything else.
- **Lesson:** Contrastive scoring rewards archetypes with "extreme" centroids, creating systematic bias

**Approach C: Max-neighbor**
- For each dream word, find max similarity to any keyword in each archetype
- **Result:** 82.9% unclassifiable — scores are too tightly clustered in high-dimensional space
- **Lesson:** Max-neighbor doesn't discriminate enough

**Approach D: Nearest-keyword (fuzzy matching) + IDF**
- For each dream word, find its SINGLE closest keyword across ALL archetypes. Award a point to that archetype. Weight by IDF (downweight words that appear in many dreams).
- **Result:** 0% unclassifiable. Rescued distribution: domestic 17, bodily 8, knowledge 6, power_personal 1
- **Trade-off:** Some classifications seem questionable (e.g. `machine` → domestic), but it's the most balanced approach so far
- **Lesson:** Discrete nearest-neighbor assignment avoids the continuous-score bias traps

### 2. Built `classify_hybrid()` — keyword primary, semantic tie-breaker

The winning architecture: run keyword counting first. If it produces a clear winner, use that. If it's a tie or zero, fall back to nearest-keyword semantic scoring.

- Preserves the reliability of keyword matches
- Uses semantic expansion only where keyword counting fails
- Zero flips (keyword classifications are never overridden)
- Reduces unclassifiable from 42.1% → 0%

## Key Insights

1. **Semantic similarity is NOT a drop-in replacement for keyword counting.** The vector space has systematic biases that depend on archetype keyword choice. Centroid methods favor generic archetypes; contrastive methods favor distinctive-but-ubiquitous archetypes.

2. **Discrete nearest-neighbor is safer than continuous scoring.** Awarding 1 point to the closest keyword avoids the accumulation biases of averaged similarity scores.

3. **IDF weighting is essential.** Without it, common words like "name" and "memory" dominate. With it, rare distinctive words (e.g. "anvil", "temple") get proper weight.

4. **Hybrid architectures preserve trust.** Never override a clear keyword match. Use semantics only as a fallback. This matches how human readers work: exact matches are certain, related words require inference.

## What Needs Doing Next

- **Validate nearest-keyword classifications manually.** Spot-check 10-15 rescued dreams to see if the semantic labels are plausible or if domestic/bodily bias is still a problem.
- **Archetype keyword audit.** Domestic (21 keywords) and bodily (19) have the most keywords, which may inflate their nearest-neighbor catchment. Consider whether some keywords are too generic (e.g. "corner", "sat" in domestic).
- **Backfill hybrid classifications to DB.** Once validated, store hybrid_primary in dream_reflections.
- **Tune similarity threshold.** Currently 0.5 cosine similarity threshold for nearest-keyword matching. Raising it would require stronger semantic affinity; lowering it would catch more words.

## Files Changed

- `worker/semantic_scorer.py` — new (4 scoring approaches, hybrid classifier, IDF weighting)
