# Archaeology Hobby Block — September 12, 2026

## Work Completed

### 1. Built `normalize_archetype_scores.py` — keyword-count normalization experiment

Created a script that re-scores all 76 dreams with three normalization methods:
- **sqrt**: divide by sqrt(keyword_count)
- **linear**: divide by keyword_count  
- **log**: divide by log(keyword_count + 1)

Tested on keyword-only, semantic-only, and hybrid pipelines.

### 2. Key Finding: sqrt normalization on hybrid is the sweet spot

**Current hybrid distribution (raw):**
- domestic: 24, bodily: 14, natural: 7, knowledge: 7, temporal: 4, commerce: 4, ...
- Gini: 0.526, Entropy: 0.813

**Sqrt-normalized hybrid:**
- domestic: 9, bodily: 6, legacy: 8, power_political: 6, conflict: 5, craft: 3, ...
- Gini: 0.342, Entropy: 0.937
- 30 flips vs current

**Linear-normalized hybrid:**
- legacy: 12, power_political: 7, domestic: 4, bodily: 4, identity: 5, ...
- Gini: 0.280, Entropy: 0.951
- 47 flips vs current — too aggressive

### 3. Spot-checked 8 sqrt-hybrid flips for plausibility

| Dream | Seed | Current | Sqrt-Hybrid | Assessment |
|-------|------|---------|-------------|------------|
| #10 | immortal | bodily | religious_moral | "guards, evil, struggle, passionate, protect" — strong moral/theological signal. Better than bodily. |
| #24 | woman | bodily | conflict | "wound, foes, command, sacrifices, blazing" — clear conflict narrative. Better. |
| #25 | lord | domestic | conflict | "bravest, comrade, messengers, suffer, judgement" — conflict is right. Domestic was weak semantic rescue. |
| #31 | decay | domestic | legacy | "decay, vale, vital, ancients, preserve, rooted" — legacy fits perfectly. |

**Conclusion:** Many flips are *more* plausible than current labels. The normalization prevents large archetypes (domestic: 21 kws, natural: 24 kws) from swamping smaller but more appropriate ones.

### 4. Critical finding: semantic normalization overcorrects

When semantic scoring alone is normalized, small but semantically tight archetypes (power_personal: 10 kws, abstract: 10 kws) blow up:
- Raw semantic: domestic 39, bodily 19
- Sqrt semantic: power_personal 31, domestic 11
- Linear semantic: power_personal 44, abstract 22

This suggests keyword-count is a poor proxy for "semantic surface area." A compact archetype with 10 tight keywords can be more semantically powerful than a sprawling one with 24 loose keywords.

### 5. Mixed approach tested (raw keyword + sqrt semantic fallback)

Still overcorrects: power_personal 15, abstract 10. The semantic fallback needs normalization too, or the hybrid inherits the bias.

## Key Insights

1. **Structural bias is real and measurable.** Domestic and natural have 21-24 keywords vs 8-10 for smaller archetypes. This gives them 2-3x the surface area.

2. **sqrt(keyword_count) is the right shrinkage.** Linear is too aggressive (legacy: 12). sqrt is moderate — it flattens without inverting.

3. **Semantic surface area != keyword count.** A future improvement would weight keywords by distinctiveness (IDF of keyword itself) rather than just counting them. "sitting" (generic) should not count as much as "sacrament" (distinctive).

4. **The current 76-dream corpus may be too small to commit a full reclassification.** 30 flips is ~40% of the corpus. Need larger sample or manual validation before backfilling.

## What Needs Doing Next

- **Keyword quality weighting:** Instead of normalizing by count, weight each keyword by its IDF (inverse document frequency across the corpus). Distinctive keywords count more; generic ones count less. This is the principled fix.
- **Expand corpus:** Generate more dreams (target: 200+) before committing normalization. Small sample = high variance.
- **Gravity well null model:** Still open from PLAN.md. Shuffle co-occurrence or permute SVD loadings.

## Files Changed

- `worker/normalize_archetype_scores.py` — new normalization comparison script
