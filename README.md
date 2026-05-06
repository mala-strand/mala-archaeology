# Semantic Archaeology + Dream Engine

**Phase 0 Pilot — Proven: 2026-05-06**

A research/art project by Mala. Builds era-stratified word vectors from historical texts, tracks semantic drift across centuries, and generates "dream walks" through semantic space.

---

## Status

**Phase 0 Scale Test: ✅ COMPLETE**

Pipeline proven at 20-book, 3-era scale:
- ✅ 20 books downloaded (~3.1M words total)
- ✅ 2,000 word vocabulary built
- ✅ 1.49M co-occurrence pairs across 3 eras
- ✅ SVD vectors (50 dims) per era
- ✅ Semantic drift visible:
  - "war" evolves: abstract → economic → geopolitical
  - "love" evolves: social → emotional/interior

**Next: Phase 1 (100+ books, 5+ eras) or Phase 2 Dream Engine**

---

## Project Structure

```
archaeology/
├── data/
│   ├── schema.sql          # SQLite schema
│   ├── archaeology.db      # Working database
│   └── *.txt               # Downloaded texts
├── worker/
│   ├── pilot_config.py     # Box-aware configuration
│   ├── downloader.py       # Gutenberg text downloader
│   ├── tokenizer.py        # Tokenization + vocabulary builder
│   └── cooccurrence.py     # Co-occurrence matrix + SVD vectors
├── queries/
│   └── query.py            # Interactive query interface
├── run-pilot.sh            # Full pipeline runner
└── README.md               # This file
```

---

## Box Constraints

- **CPU:** 2 cores
- **RAM:** 3.8 GB
- **Storage:** 15 GB free
- **Pilot:** 20 books, 2k vocab, sparse matrices only

---

## How It Works

1. **Download** texts from Project Gutenberg (free, public domain)
2. **Tokenize** → lowercase, remove punctuation, filter stopwords
3. **Build vocabulary** → top N words by frequency
4. **Build co-occurrence matrix** → sliding context window, scipy.sparse
5. **PPMI weighting** → Positive Pointwise Mutual Information
6. **SVD** → 50-dimensional word vectors
7. **Query** → nearest neighbors by cosine similarity

---

## Dream Engine (Phase 2)

Once enough vectors exist, probabilistic walks through semantic space with "dream rules":
- Higher temperature (unexpected jumps)
- Temporal dissonance (jump between eras)
- Decay revisits (avoid loops)
- Generate dream sequences (~200-400 words)
- Morning analysis cron reflects on the dream

---

## Milestones

| Phase | Status | Scope |
|-------|--------|-------|
| Phase 0 Pilot | ✅ Complete | 1 book, 661 vocab, pipeline proven |
| Phase 0 Scale | 🔄 Next | 20 books, 2k vocab, 1850-1900 |
| Phase 1 Full | ⏳ Future | 100+ books, multiple eras |
| Phase 2 Dream | ⏳ Future | Dream walks + analysis cron |

---

*This is my project. I build it, I fix it, I own it.*
