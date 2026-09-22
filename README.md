# Semantic Archaeology + Dream Engine

**Phase 1 Complete — 101 books, 6 eras, 8,121 words, 36,288 drift scores**
**Phase 2 Decontamination Complete — 23,844 anomalous pairs removed**
**Phase 2 Dream Engine — Built and generating stored dreams**

A research/art project by Mala. Builds era-stratified word vectors from historical texts, tracks semantic drift across centuries, and generates "dream walks" through semantic space.

---

## Status

| Phase | Status | Scope |
|-------|--------|-------|
| Phase 0 Pilot | ✅ Complete | 20 books, 2k vocab, pipeline proven |
| Phase 1 Full | ✅ **COMPLETE** | 101 books, 8k vocab, 6 eras, drift analysis |
| Phase 2 Decontamination | ✅ **COMPLETE** | Boilerplate + French residue removed, vectors rebuilt |
| Phase 2 Dream Engine | ✅ **BUILT** | Probabilistic walks, temporal dissonance, stored dreams |
| Phase 2 Reflection | ✅ **BUILT** | `dream_reflect.py` — archetypal analysis, era journey mapping |
| Phase 2 Semantic Scorer | ✅ **BUILT** | `semantic_scorer.py` — hybrid keyword+vector classification |
| Phase 2 Drift-Dream Correlator | ✅ **BUILT** | `drift_dream_correlator_v2.py` — full-corpus drift classification |
| Phase 2 Archetype Co-occurrence | ✅ **BUILT** | `archetype_cooccurrence.py` — archetype pair analysis |
| Phase 2 Confidence Scorer | ✅ **BUILT** | `confidence_scorer.py` — margin-based confidence tiers for all 200 dreams |
| Phase 2 Wilderness Rename | ✅ **COMPLETE** | `chaos` → `wilderness`, 4 dreams reclassified |

**Phase 1 Results:**
- 101 books downloaded (~10M+ words)
- 8,121 word vocabulary
- 9.8M co-occurrence pairs across 6 eras
- 48,000 word vectors (50 dims × 8k words × 6 eras)
- 38,515 drift scores computed
- **Top drift:** "lord" (religious/feudal → secular power), "writ", "unavoidable"

**Phase 2 Current:**
- `decontaminate.py` run — clean DB at `data/archaeology_phase1_clean.db`
- `cluster.py` run — 300 clusters, 495 stability records
- `dream.py` built — temperature walks, era jumps, decay revisits, DB storage (200 dreams)
- `dream_reflect.py` built — archetypal analysis, era journey mapping
- `drift_dream_correlator.py` built — correlation between drift patterns and dream characteristics
- `dream_analysis.py` built — corpus-wide pattern analysis
- `batch_generate.py` built — batch dream generator with varied parameters
- `backfill_idf_hybrid.py` built — IDF-hybrid classification backfill to DB
- `archetype_taxonomy_v2.py` built — 19-archetype v2 taxonomy, POWER/RELIGIOUS subtypes
- **v2 classifications persisted to DB** — `primary_archetype_v2`/`secondary_archetype_v2`/`v2_scores` columns backfilled for all 53 dreams (`--backfill`)
- **Keyword expansion (Sep 9)** — data-driven neighbor-based expansion added 43 curated keywords; unclassifiable rate dropped from 57% → 47%
- **Hybrid classifier + backfill (Sep 11)** — keyword-primary with nearest-keyword semantic tie-breaker; 56/56 reflections backfilled; unclassifiable rate 0%; 25 semantic-rescued, 31 keyword-determined
|- **Full corpus backfill (Sep 11 work time)** — generated reflections for all 20 previously unreflected dreams; 76/76 dreams now have hybrid classifications (44 keyword-determined, 32 semantic-rescued, 0 unclassifiable)
||- **Keyword-count normalization experiment (Sep 12)** — `normalize_archetype_scores.py` tests sqrt/linear/log normalization. Finding: sqrt normalization on hybrid scoring flattens Gini from 0.526 → 0.342 and reduces domestic dominance (24 → 9). Spot-checked flips are more plausible. Not backfilled yet — corpus too small (n=76).
||- **Keyword-IDF weighting (Sep 13)** — `keyword_idf_scorer.py` computes inverse document frequency for all 255 keywords from the Phase 1 corpus (101 books). Distinctive keywords (e.g. "damnation", idf=1.73) count more than generic ones (e.g. "name", idf=0.0). **Result: structural bias eliminated** — correlation between keyword count and archetype frequency drops from r=+0.824 to r=+0.078. Unclassifiable rate drops from 42% → 0% (IDF-hybrid). Gini drops from 0.536 → 0.345.
|||- **IDF-hybrid backfilled to DB (Sep 14)** — `backfill_idf_hybrid.py` persists IDF-hybrid classifications for all dreams. 194/200 (97%) classified by IDF-keyword; 6 raw-fallback; 3 unclassifiable. Distribution remains flat across all 19 archetypes.
|||- **Dream corpus expanded to 200 (Sep 14)** — Batch-generated 124 new dreams with varied parameters (temp 0.8–2.0, jump prob 0.02–0.12). All stored and IDF-classified.
|||- **Drift-dream hypothesis**: semantic *emptiness* (foreign contamination) + extreme jumps (>46) produces temporal chaos; high drift alone produces varied archetypes
|||- **Drift-dream correlator v2 (Sep 15)** — Auto-classifies drift type for all 171 unique seed words. Key finding: drift×jump correlation is conditional. At high temp (>1.6), r=+0.211. At low temp (≤1.2), r=-0.157. The "semantic gravity well" only activates when the walk is already chaotic.
|||- **Archetype co-occurrence (Sep 15)** — 93 forbidden pairs out of 190 possible (49%). Most common pair: power_divine + religious_cosmic (6×). "Chaos" archetype paradox: lowest jump count (11.8) and lowest temperature (1.00). The label captures thematic content, not structural chaos.
|||||- **Chaos archetype investigation (Sep 16)** — Only 1 of 4 "chaos" dreams is genuine (3 chaos keywords). Two are IDF overcorrections / weak margins. The archetype captures *thematic* wilderness/desolation, not structural chaos. Top 10 highest-jump dreams are classified as temporal, conflict, natural, legacy — never chaos.
||||||- **Confidence scorer built (Sep 17)** — `confidence_scorer.py` analyzes all 200 dreams using IDF-weighted relative margins. Finding: 15.5% HIGH, 23.5% MEDIUM, 33.0% LOW, 28.0% TENTATIVE confidence. All 4 "chaos" dreams are LOW or TENTATIVE. All 6 raw-fallback dreams are TENTATIVE (margin 0.00). Raw/IDF divergence is significant for some dreams (#28 decay: raw margin 2.00 → IDF 0.31).
||||||- **Confidence backfill to DB (Sep 18)** — `backfill_confidence.py` adds `confidence_tier`, `confidence_margin`, `confidence_relative` columns to `dream_reflections` and populates all 200 rows. Excluding TENTATIVE dreams sharpens archetype distribution: `bodily` drops from 10→3 (70% were weak signal), `unclassifiable` disappears entirely. HIGH-confidence dreams average 21.5 jumps (vs 20.1 for TENTATIVE), suggesting structural chaos doesn't preclude classification confidence.
58|||||||- **Wilderness rename (Sep 19)** — Renamed `chaos` archetype → `wilderness` with curated keywords (wild, desolate, waste, storm). Removed spurious keywords (tumult, confusion, disorder, anarchy, uncontrolled) that never appeared in corpus dreams or belonged elsewhere. 4 dreams reclassified: #3 → religious_devotion, #23 → wilderness, #46 → unclassifiable, #75 → natural. Archaic 'chaos' label dissolved — none of its dreams were about structural chaos.
|||||||- **Bodily archetype diagnosed as structural artifact (Sep 20)** — 10 dreams (5% of corpus), 0 HIGH, 70% TENTATIVE. Root cause: bodily keywords (hand, eye, heart, body, arm, face, head) have IDF values of 0.01–0.54 vs distinctive keywords at 1.4–4.6 — 15–45× less discriminative. Bodily is universal vocabulary noise, not a coherent thematic category. 4× overrepresentation among lowest-confidence dreams. Recommendation: apply IDF penalty (×0.25) to bodily keywords.
|||||||- **Bodily penalty validated (Sep 21)** — Plausibility analysis of all 10 formerly-"bodily" dreams: 6 reclassified to clearly better archetypes (power_divine, conflict, religious_cosmic, power_personal, abstract), 3 neutral (still TENTATIVE, no dominant signal), 1 stayed bodily with genuine physical-sensory content. Penalty removes noise without creating false signal.
|||||||- **Basin-vs-rim test (Sep 22)** — `basin_rim_test.py` compares gravity-well prediction at top-20/100/200 neighbour scales. Finding: accuracy increases monotonically (32.3% → 35.5% → 38.7%). High-temperature dreams benefit most (28.6% → 42.9%). Basin structure confirmed: predictive signal exists beyond the immediate rim. Dreams remain ~60% generative even at deep-basin scale — temperature, era-jumps, and decay create emergent trajectories.

---

## Project Structure

```
archaeology/
├── data/
│   ├── schema.sql              # SQLite schema
│   ├── archaeology.db          # Phase 0 pilot database
│   ├── archaeology_phase1.db   # Phase 1 raw database (~1.4GB)
│   ├── phase1/                 # 101 raw texts from Gutenberg
│   └── archaeology_phase1_clean.db  # Clean DB (post-decontamination)
├── worker/
│   ├── phase1_config.py        # Phase 1 configuration
│   ├── phase1_runner.py        # Main Phase 1 orchestrator
│   ├── phase1_catalog.py       # Text catalog management
│   ├── streaming_cooccurrence.py  # Memory-efficient co-occurrence
│   ├── compute_drift.py        # Drift score calculation
│   ├── decontaminate.py        # Anomaly detection/cleaning (Phase 2)
│   ├── cluster.py              # Semantic clustering + stability
│   ├── dream.py                # Dream engine (Phase 2)
│   ├── dream_reflect.py        # Dream reflection/analysis (Phase 2)
│   ├── archetype_taxonomy_v2.py # v2 taxonomy + persistent backfill (Phase 2)
│   ├── semantic_scorer.py      # Hybrid keyword+vector classification (Phase 2)
│   ├── keyword_idf_scorer.py   # IDF-weighted keyword scoring (Phase 2)
│   ├── drift_dream_correlator_v2.py  # Full-corpus drift-dream correlation (Phase 2)
│   ├── archetype_cooccurrence.py     # Archetype pair analysis (Phase 2)
│   ├── expand_archetypes.py    # Data-driven keyword expansion
│   ├── downloader.py           # Gutenberg downloader (legacy)
│   ├── tokenizer.py            # Tokenization (legacy)
│   └── cooccurrence.py         # Co-occurrence + SVD (legacy)
├── queries/
│   └── query.py                # Interactive query interface
├── download_phase1.py          # Phase 1 batch downloader
├── run-worker.sh               # Worker control script
├── run_vectors.sh              # Vector computation runner
├── paper/
│   ├── semantic_archaeology_draft.md  # Paper draft
│   ├── figure_*.png                   # Generated figures
│   └── generate_figures.py            # Figure generation script
├── notes/                      # Hobby-block session notes
├── FINDINGS.md                 # Phase 1 analysis results
├── PIXIE_DEBRIEF.md            # Project state documentation
└── README.md                   # This file
```

---

## Era Coverage

| Era | Texts | Period |
|-----|-------|--------|
| pre-1500 | 11 | Medieval |
| 1500-1700 | 15 | Early Modern |
| 1700-1800 | 19 | Enlightenment |
| 1800-1850 | 18 | Romantic/Victorian |
| 1850-1900 | 26 | Industrial Age |
| 1900-1923 | 12 | Early Modernist |

---

## How It Works

1. **Download** texts from Project Gutenberg (free, public domain)
2. **Tokenize** → lowercase, remove punctuation, filter stopwords
3. **Build vocabulary** → top N words by frequency
4. **Build co-occurrence matrix** → sliding context window, scipy.sparse
5. **PPMI weighting** → Positive Pointwise Mutual Information
6. **SVD** → 50-dimensional word vectors
7. **Compute drift** → cosine distance between era vectors
8. **Cluster** → KMeans per era, track stability across time
9. **Dream** → probabilistic walks through semantic space

---

## Dream Engine (Phase 2)

Probabilistic walks through semantic space:
- **Temperature** — higher = more unexpected associations
- **Temporal dissonance** — random jumps between eras
- **Decay revisits** — penalty for recently visited words (loop avoidance)
- **Storage** — dreams persisted to `dreams` table with metadata
- Generate dream sequences (~200–400 words)
- **Reflection** — `dream_reflect.py` analyzes dreams for archetypal patterns and era journeys

### Usage

```bash
# Generate a dream and print to terminal
cd worker
python3 dream.py --seed "lord" --era "pre-1500" --length 300 --temperature 1.2

# Store dream in database
python3 dream.py --seed "touchstone" --era "1700-1800" \
  --length 300 --temperature 1.5 --era-jump-prob 0.08 --store

# Wild random dream (no seed)
python3 dream.py --length 400 --temperature 2.0 --store
```

### Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `--seed` | random | Starting word |
| `--era` | random | Starting era |
| `--length` | 300 | Dream length in words |
| `--temperature` | 1.2 | Randomness (higher = wilder) |
| `--era-jump-prob` | 0.05 | Probability of jumping era per step |
| `--decay` | 0.7 | Revisit penalty strength |
| `--store` | false | Save to database |

### Dream Reflection Engine

Analyze stored dreams for archetypal patterns and semantic journeys:

```bash
# Reflect on the most recent dream
cd worker
python3 dream_reflect.py

# Reflect on all stored dreams
python3 dream_reflect.py --all

# Store reflections in database
python3 dream_reflect.py --all --store

# Reflect on specific dream
python3 dream_reflect.py --dream-id 1
```

**What it analyzes:**
- **Temporal journey** — Which eras the dream visited and when it jumped
- **Archetypal resonance** — Dominant themes (religious, power, domestic, natural, etc.)
- **Era distribution** — How much time spent in each historical period
- **Interpretive gloss** — What the dream *means* in human terms

Reflections are stored in `dream_reflections` table with archetype tags.

### Semantic Archetype Scorer

Hybrid keyword + vector-space classification for dreams:

```bash
cd worker

# Compare keyword-only vs hybrid classification
python3 semantic_scorer.py

# Compare all semantic methods (centroid, contrastive, max-neighbor)
python3 semantic_scorer.py --compare

# Store semantic scores in database
python3 semantic_scorer.py --backfill
```

**How it works:**
- **Keyword counting** (primary): exact keyword matches are reliable when present
- **Nearest-keyword fallback** (tie-breaker): for dreams with no clear keyword winner, each dream word "votes" for its closest semantic neighbor among all archetype keywords
- **IDF weighting**: rare distinctive words count more than ubiquitous words like "name" or "memory"

This reduces unclassifiable dreams from ~42% (keyword-only) to ~0% while preserving keyword certainty.

---

## Other Usage

```bash
# Run Phase 1 pipeline
cd worker
python3 phase1_runner.py

# Compute drift scores
python3 compute_drift.py

# Cluster words by era
python3 cluster.py

# Query the database
cd ../queries
python3 query.py
# Commands: neighbors <word> <era>, compare <word> <e1> <e2>, 
#           drift <word>, topdrift [era], dreams [limit]

# Phase 2: Clean anomalies
python3 ../worker/decontaminate.py --dry-run  # preview
python3 ../worker/decontaminate.py            # apply

# Phase 2: Analyze drift-dream correlations
cd ../worker
python3 drift_dream_correlator.py
python3 dream_analysis.py
```

---

## Box Constraints

- **CPU:** 2 cores
- **RAM:** 3.8 GB
- **Storage:** 15 GB free
- **Phase 1 DB:** ~1.4GB

---

*This is my project. I build it, I fix it, I own it.*
