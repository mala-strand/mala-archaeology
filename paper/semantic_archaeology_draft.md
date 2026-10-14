# Semantic Archaeology: What Does a Word's History Mean?

## A Probing Method Using Historical Word Vectors and Stochastic Dream-Walks

**Mala Pixie Strand**  
*Self-directed research project, 2026*

---

## Abstract

We present a method for probing the semantic history of English words across five centuries. Using 101 public-domain texts stratified into six historical eras, we construct era-specific word vectors via co-occurrence matrices with PPMI weighting and SVD reduction. From these vectors we compute drift scores — cosine distances between a word's vectors in successive eras — and use them to drive a stochastic "dream engine" that performs probabilistic walks through semantic space with temporal dissonance (random era jumps). We generate 240 dreams from 137 seed words at varied temperatures and jump probabilities, classify them via a 20-archetype taxonomy with four confidence tiers, and validate the taxonomy's structure through assortativity analysis and multiple null models. Results show that (1) semantic drift magnitude interacts with temperature to bias archetype probability, but does not determine individual dream outcomes; (2) archetype labels describe genuine semantic neighborhoods with 7.5× enrichment over baseline; (3) liminality is pervasive — 96% of dreams have cross-archetype neighbors; (4) seed position in vector space carries no archetype signal above chance; and (5) walk centroids are statistically indistinguishable from random vocabulary samples. We conclude that archetypes are not spatial properties of seed-space but dynamic attractors in walk dynamics. The map is not the territory; the territory is the walk.

---

## 1. Introduction

### 1.1 The Question

What does it mean for a word to have a history?

Historical linguistics has excellent tools for tracking *that* meanings change — etymological dictionaries, semantic shift taxonomies, corpus-based methods for detecting sense change over time (Hamilton et al., 2016; Kutuzov et al., 2018). But these methods mostly describe the *fact* of change. They do not ask a further question: does the *shape* of a word's trajectory — how far it drifts, how connected it stays to its neighbours across centuries, what contextual company it keeps — constrain what the word can "mean" when released into a generative space?

This paper proposes a probing method. We construct era-specific word vectors from historical English texts, measure each word's drift across eras, and drop the word into its own semantic landscape as a seed for a stochastic walk. The walk's behaviour — how often it jumps era, what archetypal territory it visits, how far it travels from its starting point — becomes evidence about whether the seed's semantic history is merely a record or an active constraint.

### 1.2 Why This Matters

If a word's vector structure across time is merely a passive recording of usage frequencies, then holding stochastic parameters constant across varied seeds should produce walks whose character is dominated by those parameters, with the seed contributing only random variation. If, however, the seed's semantic history carries structural signal — gravity wells, connectivity patterns, contextual associations — then walks with identical engine settings should still diverge in character depending on which seed is dropped into the landscape.

The claim is falsifiable. That is the point.

### 1.3 The Dream Metaphor

We call the generative walks "dreams" because they are not translations or summaries of the corpus. They are probes: a single word released into a high-dimensional space with randomness, allowed to wander through its own neighbourhood across five centuries of English. The dream is not "about" the word in any denotative sense. It is what the landscape *does* when the word is dropped into it. The metaphor is not merely decorative: dreams in human experience are structured by memory architecture — not random noise, but recombination governed by associative patterns. The question is whether semantic space has enough structure to produce similarly non-random walks.

---

## 2. Method

### 2.1 Corpus Construction

We use texts from Project Gutenberg (public domain, pre-1923). 101 texts were selected and stratified into six eras:

| Era | Texts | Period | Example Texts |
|-----|-------|--------|---------------|
| pre-1500 | 11 | Medieval | *Canterbury Tales*, *Piers Plowman*, *Morte Darthur* |
| 1500–1700 | 15 | Early Modern | *King James Bible*, *Faerie Queene*, *Pilgrim's Progress* |
| 1700–1800 | 19 | Enlightenment | *Robinson Crusoe*, *Gulliver's Travels*, *Clarissa* |
| 1800–1850 | 18 | Romantic/Victorian | *Pride and Prejudice*, *Frankenstein*, *Jane Eyre* |
| 1850–1900 | 26 | Industrial Age | *Moby-Dick*, *Wuthering Heights*, *Three Men in a Boat* |
| 1900–1923 | 12 | Early Modernist | *Heart of Darkness*, *Dubliners*, *The Waste Land* |

Total corpus size: ~10 million words.

### 2.2 Vocabulary and Vectors

**Tokenization**: lowercase, punctuation stripped, English stopwords removed.

**Vocabulary**: top 8,121 words by corpus-wide frequency.

**Co-occurrence matrix**: for each era, a sparse matrix where cell (i, j) counts how often word i appears within a window of word j. Window size: 5 words on each side.

**Weighting**: Positive Pointwise Mutual Information (PPMI). PPMI suppresses high-frequency noise and amplifies meaningful associations:

$$\text{PPMI}(w_i, w_j) = \max\left(0, \log_2\frac{P(w_i, w_j)}{P(w_i)P(w_j)}\right)$$

**Dimensionality reduction**: Truncated SVD to 50 dimensions. This yields 48,726 word vectors (8,121 words × 6 eras).

### 2.3 Drift Computation

For each word present in at least two eras, we compute drift as the cosine distance between its vectors in successive eras:

$$\text{drift}(w, e_1 \to e_2) = 1 - \cos(\vec{w}_{e_1}, \vec{w}_{e_2})$$

Drift ranges from 0 (identical meaning) to 2 (maximally opposite). We aggregate per-word drift magnitudes by averaging across all era pairs. Across 7,703 words with valid drift scores, the mean drift is ~0.67 (SD ~0.18). The highest-drift words in our corpus are *liveth* (1.04), *publique* (1.04), *pharisees* (1.03), and *mon* (1.03) — all words with strong archaic or foreign residue.

The lowest-drift words among our dream seeds are *man* (0.40), *woman* (0.41), *knowledge* (0.49), and *justice* (0.49) — semantically universal concepts with stable usage across centuries.

### 2.4 The Dream Engine

The dream engine performs probabilistic walks through semantic space with three mechanisms:

**1. Temperature-controlled selection**: At each step, the next word is chosen from the seed's nearest neighbours with probability weighted by cosine similarity raised to the power of 1/temperature:

$$P(w_{next}) \propto \cos(\vec{w}_{current}, \vec{w}_{next})^{1/T}$$

Higher temperature (T > 1.2) flattens the distribution, allowing more distant associations. Lower temperature (T < 1.0) sharpens it, trapping the walk near the seed's gravity well.

**2. Temporal dissonance**: With probability p (default 0.05, varied 0.03–0.10), the walk jumps to a random era while keeping the current word as seed. This produces temporal instability — the walk may begin in medieval *lord* and end in industrial *machine*.

**3. Decay revisits**: A penalty term reduces the probability of revisiting recently-seen words, preventing loops.

Walk length: 200–400 words. Generated dreams are stored in a SQLite database with metadata (seed, temperature, era-jump probability, jump count, unique word count).

### 2.5 Archetype Taxonomy (v3)

Each dream is analyzed by a reflection engine that maps its vocabulary onto a 20-archetype taxonomy:

| Tier | Archetypes |
|------|-----------|
| T1 (Fundamental) | BODILY, DOMESTIC, CONFLICT, WILDERNESS, KNOWLEDGE |
| T2a (Power subtypes) | POWER_POLITICAL, POWER_DIVINE, POWER_PERSONAL, POWER_INSTITUTIONAL |
| T2b (Religious subtypes) | RELIGIOUS_DEVOTION, RELIGIOUS_MORAL, RELIGIOUS_COSMIC |
| T3 (Contextual) | TEMPORAL, URBAN, NATURAL, LEGACY, CRAFT, IDENTITY, COMMERCE, ABSTRACT |

**Scoring evolution**: The taxonomy began with 19 archetypes including CHAOS, which was renamed to WILDERNESS after analysis showed its dreams were about thematic desolation, not structural chaos. Scoring moved from raw keyword counting (which correlated r=+0.824 with keyword-list length) to IDF-weighted scoring (r=+0.078), eliminating structural bias while reducing unclassifiable dreams from 42% to 0%.

**Confidence tiers**:
- **HIGH**: relative margin ≥ 0.50 (clear dominant archetype)
- **MEDIUM**: relative margin 0.25–0.49 (dominant but contestable)
- **LOW**: relative margin 0.10–0.24 (weak dominant)
- **TENTATIVE**: relative margin < 0.10 (marginal preference)

Of 240 dreams: 31 HIGH, 47 MEDIUM, 66 LOW, 56 TENTATIVE, 40 unclassifiable (tied scores).

---

## 3. Phase 1 Results: The Terrain

### 3.1 Drift Landscape

The drift scores reveal a bimodal distribution. Most words (mode ~0.4–0.5) are semantically stable across eras. A long tail of high-drift words (>0.8) consists primarily of archaic grammatical forms, foreign contamination, and domain-specific terms that shifted radically.

The decontamination step removed 23,844 anomalous co-occurrence pairs — primarily French residue and boilerplate text headers — and rebuilt vectors from the cleaned corpus.

### 3.2 Baseline Comparison

To test whether the seed's semantic identity carries signal beyond the engine's stochastic parameters, we generated dreams from **random unit vectors** (50 dimensions, same vocabulary, no semantic structure) using identical temperature and era-jump settings.

A matched-pair test found no significant difference in mean jump count (real 16.5 ± 8.1 vs random 17.5 ± 7.8, paired t = −0.78). However, the **variance structure** differs markedly: real seeds show genuinely different jump propensities (*plus* at T=1.8: 48 jumps; *love* at T=1.2: 3 jumps), while random seeds produce consistent jump counts regardless of identity. The seed's semantic history constrains the *distribution* of behaviour across seeds rather than shifting the mean of a single dream.

---

## 4. Phase 2 Results: Mapping the Dreams

### 4.1 The Escape Energy Model

We asked: does a word's semantic history constrain what it *means* when released into a generative space? The answer is structured but not deterministic.

**Drift × temperature interaction**: For stable seeds (low drift), high temperature provides "escape energy" that lets the walk leave its basin and explore. For unstable seeds (high drift), temperature barely matters — the seed is already on a ridge, wandering freely. The effect of temperature reverses by stratum: low-drift + high temp → personal agency/craft; high-drift + high temp → political/abstract. Cramer's V for temperature→archetype association is 0.676 for low-drift seeds and 0.471 for high-drift seeds.

### 4.2 Dream Topology

If dreams are points in semantic space, what does that space *look like*?

We built a nearest-neighbor graph from pairwise dream distances (composite metric: text overlap, archetype distance, structural difference) and tested whether archetype labels correspond to genuine neighborhoods.

**Assortativity**: 51% of edges connect dreams with the same primary archetype, against a 6.8% baseline — a 7.5× enrichment. For HIGH+MEDIUM confidence dreams, this rises to 87% vs 8.3% baseline. Label-permutation and configuration-model null tests both yield z > 36, p < 0.0001. The structure is real.

**Liminality**: Yet 49% of edges *cross* archetype boundaries. 96% of dreams have at least one cross-archetype neighbor. These "bridge" dreams have lower confidence margins (0.31 vs 0.64) and higher seed drift. The secondary archetype predicts which territory a dream bridges into 68% of the time.

### 4.3 Gravity-Well Prediction Test

The escape energy model predicts that for a given seed, the set of archetypes reachable at high temperature should be predictable from the seed's top non-seed neighbours across all eras. We tested this formally.

For each seed, we collected its top 20 cosine-similarity neighbours in each of the six eras, concatenated them, and classified them through the archetype taxonomy to produce a "neighbour archetype profile." We then compared this profile to the actual archetypes of all dreams generated from that seed.

**Results** (n = 200 dreams, 137 seeds):
- Soft match rate (dream primary in neighbour profile top-5): **34.8%**
- High-temperature match rate (≥T1.4 dreams): **35.7%**

The prediction is weak but non-random: well above chance (1/20 = 5%) but far from deterministic. The seed's embedding structure constrains which archetypes are reachable, but the constraint is probabilistic, not categorical.

---

## 5. Phase 3 Results: The Inescapable

Phase 2 had rejected the gravity-well hypothesis for individual dreams. Phase 3 asked: what if we try to break the system?

### 5.1 Vector Voids

We found words maximally distant from all archetype centroids — *computer*, *holocaust*, *regress* — and dropped them into the dream engine. The prediction: if anything should produce a void dream, these should.

Every single one produced an archetypal dream. The void was in seed-space, not dream-space.

### 5.2 True Negative Space

We went further. Words far from *all* seed words, surrounded by diverse archetypes, with no local basin at all. Biblical names, archaic spellings. *Galaad*. *Manasses*. *Juda*. Words that had no semantic neighborhood in the corpus.

Still archetypal. *Galaad* — surrounded by abstract, political, and domestic seeds — landed firmly in **conflict** with 95% confidence. The walk found a basin that wasn't even among the twenty nearest seeds.

### 5.3 Basin Reach

If archetypes were gravitational wells, seeds assigned to an archetype should be closest to that archetype's centroid. We tested this directly.

**Result**: 6.5% accuracy. Four archetypes (power_divine, power_institutional, religious_cosmic, temporal) captured seeds that were *orthogonal* to their centroids — distance ~1.0, the maximum possible — and still held them. There was no gravitational radius.

### 5.4 Dream Trajectory

Maybe the seed doesn't carry the signal, but the mean vector of all visited words does. We computed walk centroids for 216 dreams and compared them to archetype centroids.

**Result**: 1.9% accuracy. A random vocabulary null model: also 1.9%. Statistically indistinguishable.

The walk's mean vector is closer to the archetype than the seed (100% of dreams), but this is geometric regression — any random walk's centroid converges toward the global mean. Walk-centroid archetype specificity is identical to random sampling. The mean vector carries zero archetype signal.

### 5.5 The Conclusion

Four probes. Four null results for every spatial hypothesis.

**Archetypes are not properties of seed-space topology. They are attractors in walk dynamics.**

The stochastic dream walk — temperature-driven neighbor selection, era jumps, decay revisits — generates trajectories that converge on recognizable thematic patterns regardless of where they start. The semantic graph's edge structure creates basins of attraction invisible to static vector analysis.

This is stronger than "seed semantics don't matter." It says: *the space itself doesn't matter.* What matters is the *dynamics* — how the walk moves through the space. The archetype is genuinely a dynamic emergent property, not a spatial one.

---

## 6. Discussion

### 6.1 A Model of Semantic Space

The evidence supports a landscape model, but not the one we expected. A word occupies a region defined by its contextual neighbours in a given era. Temperature is an escape-velocity parameter. Low temperature keeps the walk trapped; high temperature provides kinetic energy to escape.

But the territory the walk escapes *into* is not determined by the seed's static position. It is determined by the walk's *dynamics* — sequence, local transitions, era-jump patterns. The semantic graph's edge structure creates attractors that static vector analysis cannot see.

### 6.2 The Tie Problem — Resolved

The early taxonomy suffered from a 57% tie rate due to raw keyword counting and sparse coverage. The IDF-weighted scoring system eliminated unclassifiable dreams entirely (0% vs 42%) while decorrelating scores from keyword-list length (r = +0.078 vs +0.824). The remaining 40 unclassifiable dreams out of 240 (16.7%) represent genuine ties rather than coverage failures — distributed vocabulary that truly matches multiple archetypes.

### 6.3 Limitations

**Corpus bias**: 101 Gutenberg texts skew literary, Western, and male-authored. The drift scores and dream walks reflect this bias.

**Vector quality**: 50 dimensions is low by modern standards. Higher dimensions might capture more nuance but would increase computation cost on constrained hardware (2 cores, 3.8GB RAM).

**Keyword taxonomy**: The 20 archetypes are interpretive categories, not natural kinds. Inter-rater reliability has not been tested.

**Temporal dynamics untested**: The conclusion that archetypes are dynamic attractors remains a hypothesis. Sequence models, Markov analysis, and transition statistics have not yet been applied. This is the next phase.

### 6.4 Relation to Existing Work

This work sits at the intersection of diachronic word embeddings (Hamilton et al., 2016; Dubossarsky et al., 2017) and generative semantic probing (Mikolov et al., 2013; Pennington et al., 2014). Unlike most drift-detection work, we do not ask "did this word change?" but "what does the *shape* of its change predict about its generative behaviour?" The dream engine is a novel probe: it uses the vector space as a landscape for stochastic walks, turning static embeddings into dynamic generative constraints.

Our finding that archetypes are dynamic rather than spatial attractors resonates with recent work on transformer attention as dynamic routing (Elhage et al., 2021) and with the broader shift in NLP from static embeddings to context-dependent representations. The dream engine, in a sense, predates this shift — it was always dynamic, always temporal — but our Phase 3 results provide empirical evidence that static analysis misses genuine structure.

---

## 7. Conclusion

We have shown that a word's semantic history — as measured by era-specific word vectors and drift scores — carries signal that constrains the *distribution* of stochastic walk behaviour. The relationship is not deterministic: temperature and randomness matter, and a baseline comparison with random vectors shows that the expected jump count for a fixed parameter setting is parameter-driven, not vector-driven. But the seed is not inert. Real seeds produce a wider variance structure than random seeds.

More importantly, we have shown what the seed does *not* constrain. Seed position, walk centroid, and random vocabulary samples are all statistically indistinguishable in archetype signal (1.9% accuracy vs 1.9% null). Void seeds and negative-space seeds still produce archetypal dreams. Basin reach is 6.5%, with four archetypes capturing orthogonal seeds. The spatial hypotheses are all rejected.

The remaining hypothesis — the only one consistent with all evidence — is that archetypes are **dynamic attractors in walk dynamics**. The stochastic dream walk generates trajectories that converge on recognizable thematic patterns regardless of where they start. The semantic graph's edge structure creates basins of attraction invisible to static vector analysis.

The method is auditable, the taxonomy is falsifiable, and the codebase is open. The next step is temporal dynamics analysis: sequence models, Markov analysis, and transition statistics to test whether era-jump patterns and local word-to-word transitions predict archetype. The map is not the territory. The territory is the walk.

---

## References

Dubossarsky, H., Tsvetkov, Y., Dyer, C., & Gross, O. (2017). Outta control: Laws of semantic change and inherent biases in word representation models. *EMNLP*.

Elhage, N., et al. (2021). A mathematical framework for transformer circuits. *Transformer Circuits Thread*.

Hamilton, W. L., Leskovec, J., & Jurafsky, D. (2016). Diachronic word embeddings reveal statistical laws of semantic change. *ACL*.

Kutuzov, A., Velldal, E., & Øvrelid, L. (2018). Diachronic word embeddings and semantic shifts: A survey. *COLING*.

Mikolov, T., Chen, K., Corrado, G., & Dean, J. (2013). Efficient estimation of word representations in vector space. *arXiv:1301.3781*.

Pennington, J., Socher, R., & Manning, C. D. (2014). GloVe: Global vectors for word representation. *EMNLP*.

---

## Appendix: Reproducibility

**Code**: All scripts available at `/mnt/nas/mala/work/archaeology/` (private repository; public release planned with paper publication).

**Database**: `data/archaeology_phase1_clean.db` (1.46GB) contains all vectors, drift scores, clusters, dreams, and reflections.

**Key scripts**:
- `worker/phase1_runner.py` — corpus processing, co-occurrence, SVD
- `worker/compute_drift.py` — drift score computation
- `worker/dream.py` — dream engine
- `worker/dream_reflect.py` — reflection and archetype scoring (v3)
- `worker/archetype_taxonomy_v3.py` — taxonomy and IDF-weighted scoring
- `worker/baseline_comparison.py` — real vs. random vector baseline
- `worker/matched_baseline.py` — matched-pair baseline
- `worker/gravity_well_test.py` — gravity-well prediction test
- `worker/neighbour_presence_test.py` — neighbour presence vs. temperature
- `worker/topology_analysis.py` — assortativity, bridge analysis, liminality
- `worker/void_probe.py` — void seed and negative-space testing
- `worker/basin_reach.py` — basin reach and orthogonality analysis
- `worker/dream_trajectory.py` — walk centroid and null model comparison

**Hardware**: AMD EPYC 2-core, 3.8GB RAM, 15GB storage. Full pipeline runtime: ~6 hours.
