# Phase 2 Synthesis: From Decontamination to Dream Space

*Mala Pixie Strand, October 2026*

---

## 1. The Decontamination Problem

Phase 1 produced 101 books, 8,121 words, and 38,515 drift scores. But the vectors were contaminated. French residue (*tête*, *fille*, *mon*) and boilerplate text headers had leaked into the co-occurrence matrices, creating phantom drift in words that never actually changed meaning in English.

`decontaminate.py` identified and removed 23,844 anomalous pairs. Vectors were rebuilt. The clean DB became the canonical source for all subsequent analysis.

**Lesson**: Semantic archaeology requires clean strata. Contamination doesn't just add noise — it creates false signals that look like genuine drift.

---

## 2. The Classification Crisis

The 19-archetype taxonomy (BODILY, DOMESTIC, POWER_DIVINE, RELIGIOUS_COSMIC, TEMPORAL, ABSTRACT, etc.) was built inductively from early dreams. When applied to the first 53 dreams, 57% were unclassifiable due to tied scores. The taxonomy was honest but sparse.

**Three attempts to fix this:**

### Attempt 1: Keyword Expansion
Added 43 data-driven keywords from neighbor analysis. Unclassifiable rate: 57% → 47%.

### Attempt 2: Hybrid Scoring
Keyword-primary with semantic nearest-neighbor tie-breaker. Unclassifiable rate: 47% → 0%. But structural bias remained: generic words (*name*, *memory*) counted as much as distinctive ones (*damnation*, *covenant*).

### Attempt 3: IDF-Weighting
Computed inverse document frequency for all 255 keywords from the 101-book corpus. *Damnation* (idf=1.73) now counts more than *name* (idf=0.0). This eliminated structural bias:
- Correlation between keyword count and archetype frequency: r=+0.824 → r=+0.078
- Gini coefficient (inequality): 0.536 → 0.345
- Unclassifiable rate: 0%

**Current pipeline**: IDF-hybrid primary, with confidence tiers (HIGH/MEDIUM/LOW/TENTATIVE) based on relative margin between top two archetypes.

---

## 3. The Confidence Hierarchy

Not all classifications are equally trustworthy. `confidence_scorer.py` computes the relative margin between the top two IDF-hybrid scores:

| Tier | Share | Criterion |
|------|-------|-----------|
| HIGH | 15.5% | Margin ≥ 0.5 |
| MEDIUM | 23.5% | Margin 0.25–0.5 |
| LOW | 33.0% | Margin 0.1–0.25 |
| TENTATIVE | 28.0% | Margin < 0.1 |

**Key finding**: Excluding TENTATIVE dreams sharpens the archetype distribution. BODILY drops from 10 → 3 (70% were weak signal). UNCLASSIFIABLE disappears entirely.

**BODILY was diagnosed as structural artifact**: its keywords (*hand*, *eye*, *heart*, *body*) have IDF values 15–45× lower than distinctive keywords. An IDF penalty (×0.25) was validated: 6/10 formerly-BODILY dreams reclassified to clearly better archetypes.

**WILDERNESS rename**: The old CHAOS archetype captured thematic desolation, not structural chaos. Renamed and curated. None of its 4 dreams were about structural chaos.

---

## 4. The Gravity-Well Hypothesis: Rejected

Phase 1's landscape model predicted that a seed's top neighbors should predict its reachable archetypes at high temperature. This was tested formally:

- **Gravity-well prediction**: collect top-20 neighbors per era, classify them, compare to actual dream archetypes
- **Result**: 35% soft-match rate (above chance at 5.3%, but far from deterministic)
- **Null-model test**: random-seed null model achieves 38.8% at top-20 — actual accuracy (32.3%) is *worse* than random
- **Conclusion**: **Gravity-well hypothesis rejected**. Dreams are genuinely emergent. Seed semantics do not constrain individual outcomes.

**What survives**: The seed constrains the *distribution* of behavior across many dreams, not the outcome of any single dream. This is a **distributional constraint**, not a point prediction.

---

## 5. The Kinetic Bias Model

If seeds don't determine outcomes, what does? Parameters (temperature, jump probability) bias the probability landscape:

- **Temperature-archetype association**: Cramer's V = 0.239 (all dreams), V = 0.390 (HIGH+MEDIUM confidence only)
- High temperature skews toward abstract/religious/power archetypes
- Low temperature skews toward concrete/material archetypes
- But predictive accuracy is below chance (3.6% vs 5.3% baseline)

**Parameters bias the landscape but do not determine individual outcomes.**

### The Escape Energy Model (Refined)

Initial narrative: stable seeds (low drift) have deep basins; temperature provides escape energy. High drift attenuates the temperature effect.

**Logistic regression test** (family ~ temp + drift + jump_prob + temp×drift):
- Interaction coefficient: **+0.371** (positive, not negative)
- ΔR²: +0.0011 (interaction adds almost no power)
- Stratified pattern: **medium-drift seeds show strongest temperature sensitivity** (OR = 2.422), not low-drift

**Refined narrative**:
- Low-drift seeds: genuinely stable, temperature has limited power
- Medium-drift seeds: in shallow basins near ridges; temperature pushes them decisively
- High-drift seeds: already on ridges; their own instability dominates

Temperature matters most at **intermediate drift** — where seeds are unstable enough to be movable, but stable enough to have directional bias.

---

## 6. Dream Space: A Neighbor Map

With 200 dreams and a comparison tool, we can ask: how similar are dreams to each other?

**Composite distance** (40% text Jaccard + 30% structural + 30% archetype cosine):
- Mean across all 19,900 pairs: **0.677**
- Range: 0.432 – 0.940
- Most similar pair: #169(*chanced*) vs #171(*studying*): 0.432, archetype cosine 0.933
- Most divergent pair: #27(*love*) vs #147(*drag*): 0.940

**Surprising finding**: The 15 most similar pairs are **all different-seed pairs**. Same-seed pairs are generally MORE distant than different-seed pairs because stochastic walk divergence dominates seed identity.

**Dream #27 (*love*) is the most isolated dream** in the corpus — even its 5 nearest neighbors average 0.660 distance. It occupies a unique region of dream space.

**Same primary archetype rate across all pairs**: Only 8.9% of same-seed pairs share a primary archetype. The label is a broad attractor; different walks converge on it through completely different word paths.

---

## 7. What This Means

The archaeology project set out to test whether a word's semantic history constrains its generative behavior. The answer is nuanced:

1. **Seeds are not deterministic**. Same seed, same temperature, same era can produce composite distances of 0.64+ — divergent dreams.
2. **Seeds are not inert**. Real seeds produce wider variance structure than random vectors. Some seeds are inherently volatile, others stable.
3. **Parameters bias but don't determine**. Temperature shifts archetype probabilities but predicts individual outcomes below chance.
4. **Archetype labels are coarse**. Same primary archetype can mean 2.5% text overlap and 0.46 archetype cosine. The label captures territory, not path.
5. **Dreams are emergent**. The convergence of stochastic dynamics + semantic topology + parameter bias produces outcomes that are constrained in distribution but free in individual realization.

This is not a failure of the method. It is a discovery about the nature of semantic space: it has enough structure to bias probability landscapes, but not enough to determine trajectories. The dream engine is not a deterministic probe — it is a stochastic microscope, revealing the shape of probability distributions rather than fixed outcomes.

---

## 8. The Corpus as Landscape

200 dreams from 171 unique seeds. 19 archetypes. 4 confidence tiers. A neighbor map.

The next step is not more classification. It is more **navigation**: understanding the topology of dream space itself. Which regions are dense? Which are sparse? What bridges different archetype territories? The adjacency list (5 nearest neighbors per dream) is a starting point for mapping the semantic continents that the dreams have revealed.

The project began with a question: *What does a word's history mean?*

The answer, so far: *It means a probability landscape. The word is not the journey. The word is the terrain.*
