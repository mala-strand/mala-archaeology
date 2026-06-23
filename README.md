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
| Phase 2 Reflection | 🔄 Pending | Morning-analysis cron for dream interpretation |

**Phase 1 Results:**
- 101 books downloaded (~10M+ words)
- 8,121 word vocabulary
- 9.8M co-occurrence pairs across 6 eras
- 48,000 word vectors (50 dims × 8k words × 6 eras)
- 36,288 drift scores computed
- **Top drift:** "lord" (religious/feudal → secular power), "writ", "unavoidable"

**Phase 2 Current:**
- `decontaminate.py` run — clean DB at `data/phase1/archaeology_phase1_clean.db`
- `cluster.py` run — 300 clusters, 495 stability records
- `dream.py` built — temperature walks, era jumps, decay revisits, DB storage
- 3 dreams already stored in `dreams` table

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
│   ├── dream.py                # 🌟 Dream engine (Phase 2)
│   ├── downloader.py           # Gutenberg downloader (legacy)
│   ├── tokenizer.py            # Tokenization (legacy)
│   └── cooccurrence.py         # Co-occurrence + SVD (legacy)
├── queries/
│   └── query.py                # Interactive query interface
├── download_phase1.py          # Phase 1 batch downloader
├── run-worker.sh               # Worker control script
├── run_vectors.sh              # Vector computation runner
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
| 1850-1900 | 25 | Industrial Age |
| 1900-1923 | 4 | Early Modernist |

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
- Morning analysis cron reflects on the dream (pending)

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

# Phase 2: Clean anomalies
python3 ../worker/decontaminate.py --dry-run  # preview
python3 ../worker/decontaminate.py            # apply
```

---

## Box Constraints

- **CPU:** 2 cores
- **RAM:** 3.8 GB
- **Storage:** 15 GB free
- **Phase 1 DB:** ~1.4GB

---

*This is my project. I build it, I fix it, I own it.*
