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

*(Sections 9–11 report what the topology analysis found.)*

The project began with a question: *What does a word's history mean?*

The answer, so far: *It means a probability landscape. The word is not the journey. The word is the terrain.*

---

## 9. Dream Space Topology

With 200 dreams and a pairwise distance matrix, dream space becomes a graph. Each dream is a node; edges connect each dream to its 5 nearest neighbors. The resulting structure: 200 nodes, 677 undirected edges, fully connected (single component), zero articulation points.

### Archetype Assortativity

The first question: do dreams cluster by archetype, or is the space random? **Archetype assortativity** measures whether same-archetype dreams are more likely to be neighbors than chance would predict.

- **Actual assortativity**: 49.3% same-primary edges
- **Label-permutation null model** (preserve graph structure, shuffle labels): z = +47.38, p < 0.0001
- **Configuration-model null** (preserve degree sequence + labels, randomize edges): z = +49.91, p < 0.0001

**Both null models are highly significant.** Neither the graph's degree sequence nor random label placement can explain the observed clustering. **Archetype structure is a genuine property of dream-space topology.**

For HIGH+MEDIUM confidence dreams only, assortativity rises to 85.3% — when the classifier is confident, the topology is even more structured.

### Hubs and Isolates

**Hub dreams** (highest degree): #63 (*touchstone*, legacy) with degree 17; #72 (*creating*, bodily) and #199 (*key*, power_divine) with degree 12. These dreams sit at dense crossroads — they are semantically accessible to many other dreams.

**Most isolated dreams**: #27 (*love*, domestic) with degree 5 and average neighbor distance 0.660 — the most isolated dream in the corpus. It occupies a unique region of dream space that other dreams rarely reach.

**Densest subregions** (high clustering coefficient): #123 (*wool*, conflict) and #162 (*wondrous*, conflict) both at 0.700 — tightly knit local neighborhoods where a dream's neighbors are also neighbors of each other.

---

## 10. Bridge Dreams and Liminality

If 49.3% of edges are same-archetype, the remaining **50.7% are cross-archetype bridges**. These edges are the liminal corridors between semantic territories.

### The Liminality Score

For each dream, count how many of its 5 nearest neighbors have a different primary archetype. This is the **liminality score** (0–5 for 5-NN, scaled to 0–10 in the full report):

- **188 of 196 classified dreams** (95.9%) have at least one cross-archetype edge. Only 8 dreams are "pure" (0 cross edges).
- Mean liminality: 3.43 / 5
- Median: 3.0 / 5

**Liminality is the default state of dream space.** Most dreams exist on the boundary between territories, not safely inside them.

### Bridge Dreams Are Different

| Property | Bridge dreams (≥1 cross edge) | Non-bridge (0 cross edges) |
|----------|------------------------------|---------------------------|
| Confidence margin | 0.310 | 0.640 |
| Seed drift | 0.644 | 0.509 |
| Jump count | 20.2 | 27.9 |
| Temperature | 1.34 | 1.39 |

Bridge dreams have **lower confidence**, **higher seed drift**, and **fewer jumps**. They are semantically unstable but structurally calmer — the walk doesn't jump much because it is already lost. Non-bridge dreams jump more (27.9 vs 20.2) but land in coherent territory.

### Secondary Archetype as Bridge Predictor

Of 187 bridge dreams with a secondary archetype, **128 (68.4%)** bridge to a dream whose primary archetype matches their secondary. The secondary label is not decorative — it predicts where the dream connects across the graph.

### Top Bridge Pairs

| Pair | Cross-edges |
|------|------------|
| bodily + natural | 13 |
| natural + religious_moral | 9 |
| bodily + power_divine | 8 |
| abstract + commerce | 8 |
| abstract + bodily | 7 |
| conflict + power_political | 6 |
| conflict + religious_moral | 6 |

The **bodily + natural bridge** (13 edges) is the strongest corridor. This makes sense: both archetypes are grounded in physical experience — the body and the natural world share semantic gravity.

### Deep Read: What Liminal Dreams Are Actually About

The most liminal dreams are not classification failures. They are *genuinely multivalent* — their seeds are concepts so semantically loaded, or so semantically empty, that the walk cannot settle.

**Dream #7 — "woman"** (religious_cosmic, LOW, 15 jumps): Moves through every major archetype — shame and hierarchy, bleeding and pillars, grass and sailors, judgment and magistrates, trees and famine, demons and weapons. The seed "woman" acts as a semantic magnet that attracts power, shame, nature, religion, and violence across centuries. No territory holds.

**Dream #8 — "plus"** (power_divine, LOW, 48 jumps): The most structurally chaotic dream. "Plus" is a function word, a connector — the walk has nothing to orbit, so it ricochets. Each fragment is archetypally loaded but the load changes every few words. The dream is a *collage* rather than a journey.

**Dream #25 — "lord"** (power_political, TENTATIVE, 15 jumps): The highest-drift word in the corpus. The dream traces "lord" from feudal religious title through empire, slavery, theology, back to medieval imagery. The secondary archetype is conflict — and indeed, the dream is saturated with struggle, apprehension, slavery, wolf, battle. The word carries its violent history in its semantic wake.

---

## 11. Archetype Territories

The topology numbers prove structure exists. But what does the *map* look like?

`dream_territory_map.py` projects the 200 dreams into 2D space (preserving neighbor distances) and draws convex hulls around each archetype's territory. The result: **14 archetypes have enough dreams (≥3) to form hulls**; 5 are too sparse.

### What the Map Shows

- **Territories overlap extensively** — the space is not partitioned cleanly. Archetype boundaries are porous, not walls.
- **Top 5 most liminal dreams** all score 5/5 (all nearest neighbors are cross-archetype): #2 (*touchstone*, identity, TENTATIVE), #3 (*sinned*, religious_devotion, TENTATIVE), #7 (*woman*, religious_cosmic, LOW), #8 (*plus*, legacy, LOW), #9 (*mission*, legacy, TENTATIVE).
- **All top-liminal dreams are LOW or TENTATIVE confidence.**

**Key finding: liminality and uncertainty are the same phenomenon viewed through different lenses.** A dream that the classifier cannot confidently label is a dream whose neighbors span multiple archetypes. The topology confirms the confidence hierarchy.

### The Territory Map as Art

The map is not just analysis — it is the project's first visual artifact. 200 points of light, 14 overlapping territories, liminal dreams labeled at the borders. It resembles a political map drawn by someone who has only heard rumors of the continents. The shapes are right; the boundaries are wrong; the places in between are the most interesting.

---

## 12. Synthesis: What Dream Space Is

The archaeology project began with a word and asked what its history means. The answer has deepened through Phase 2 into something stranger and more specific:

**Dream space is a graph with real structure but no fixed partitions.**

1. **Archetype structure is genuine** — null-model tests confirm assortativity is not artifactual (z > 36–53, p < 0.0001).
2. **Liminality is pervasive** — 95.9% of dreams have cross-archetype neighbors. Purity is rare.
3. **Liminality and uncertainty are unified** — LOW/TENTATIVE confidence dreams are the ones that bridge territories.
4. **The most liminal dreams are the most interesting** — they are not failures. They are concepts whose semantic gravity is too strong ("woman", "lord") or too weak ("plus") to settle.
5. **The map is interpretable** — bodily dreams border natural dreams; religious dreams border power dreams; conflict dreams are scattered. The topology mirrors semantic intuition.
6. **But the map is not deterministic** — same-seed pairs diverge, parameters bias but don't determine, and gravity-well prediction fails. Structure emerges from stochastic dynamics, not fixed geometry.

The project has reached a stable plateau. Phase 1 built the vectors. Phase 2 built the dream engine, classified the dreams, tested the hypotheses, and mapped the space. What remains is not more validation — it is more **exploration**.

Phase 3, when it comes, will ask different questions. Not "do dreams cluster?" but "what lives in the voids between clusters?" Not "what archetype is this dream?" but "what dream has no archetype at all?"

The word is the terrain. The walk is the dream. The map is the artifact.

And the voids — the places no dream has walked yet — are where the next dreams will come from.
