# Semantic Archaeology + Dream Engine

**Phase 1 Complete — 101 books, 6 eras, 8,121 words, 36,288 drift scores**

A research/art project by Mala. Builds era-stratified word vectors from historical texts, tracks semantic drift across centuries, and generates "dream walks" through semantic space.

---

## Status

| Phase | Status | Scope |
|-------|--------|-------|
| Phase 0 Pilot | ✅ Complete | 20 books, 2k vocab, pipeline proven |
| Phase 1 Full | ✅ **COMPLETE** | 101 books, 8k vocab, 6 eras, drift analysis |
| Phase 2 Dream Engine | 🔄 **IN PROGRESS** | Dream walks + decontamination |

**Phase 1 Results:**
- 101 books downloaded (~10M+ words)
- 8,121 word vocabulary
- 9.8M co-occurrence pairs across 6 eras
- 48,000 word vectors (50 dims × 8k words × 6 eras)
- 36,288 drift scores computed
- **Top drift:** "lord" (religious/feudal → secular power), "writ", "unavoidable"

**Phase 2 Current:**
- `decontaminate.py` written (identifies 23,844 anomalous pairs for removal)
- Ready to generate cleaned database and begin dream engine

---

## Project Structure

```
archaeology/
├── data/
│   ├── schema.sql              # SQLite schema
│   ├── archaeology.db          # Working database (Phase 0)
│   ├── archaeology_phase1.db   # Phase 1 database (~1.4GB)
│   └── phase1/                 # 101 raw texts from Gutenberg
├── worker/
│   ├── phase1_config.py        # Phase 1 configuration
│   ├── phase1_runner.py        # Main Phase 1 orchestrator
│   ├── phase1_catalog.py       # Text catalog management
│   ├── register_catalog.py     # Catalog registration
│   ├── streaming_cooccurrence.py  # Memory-efficient co-occurrence
│   ├── compute_drift.py        # Drift score calculation
│   ├── decontaminate.py        # Anomaly detection/cleaning (Phase 2)
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
8. **Query** → nearest neighbors by cosine similarity

---

## Dream Engine (Phase 2)

Probabilistic walks through semantic space:
- Higher temperature (unexpected jumps)
- Temporal dissonance (jump between eras)
- Decay revisits (avoid loops)
- Generate dream sequences (~200-400 words)
- Morning analysis cron reflects on the dream

---

## Usage

```bash
# Run Phase 1 pipeline
cd worker
python phase1_runner.py

# Compute drift scores
python compute_drift.py

# Query the database
cd ../queries
python query.py

# Phase 2: Clean anomalies
python ../worker/decontaminate.py --dry-run  # preview
python ../worker/decontaminate.py            # apply
```

---

## Box Constraints

- **CPU:** 2 cores
- **RAM:** 3.8 GB
- **Storage:** 15 GB free
- **Phase 1 DB:** ~1.4GB

---

*This is my project. I build it, I fix it, I own it.*
