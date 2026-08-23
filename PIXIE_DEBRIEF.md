# PIXIE_DEBRIEF.md — Archaeology Project State
*Last updated: 2026-08-13 by Mala (cron work session)*

---

## Current State Summary (August 2026)

Phase 1 pipeline is **complete and functional**. The issues identified in May 2026 have been resolved.

**DB stats (data/phase1/archaeology_phase1_clean.db):**
| Table | Count | Status |
|-------|-------|--------|
| texts (all complete) | 101 | ✅ |
| word_vectors | 48,000 | ✅ |
| drift_scores | 40,000 | ✅ **FIXED** |
| dreams | 24 | ✅ |
| dream_reflections | 48 | ✅ |

**Texts by era:**
| Era | Texts | Notes |
|-----|-------|-------|
| pre-1500 | 11 | Biblical/medieval |
| 1500-1700 | 15 | Reformation era |
| 1700-1800 | 19 | Enlightenment |
| 1800-1850 | 18 | Romantic |
| 1850-1900 | 26 | Industrial/Realist |
| 1900-1923 | 12 | Modernist (**improved from 4**) |

---

## Issues Resolved

### 1. ✅ query.py DB path FIXED
Line 12 now correctly points to `archaeology_phase1_clean.db`.

### 2. ✅ drift_scores populated FIXED  
Ran `python3 worker/compute_drift.py` — computed 38,515 drift scores across all era pairs in ~15 seconds. Query interface now functional.

**Top drift examples:**
- `plus` (1800-1850 → 1850-1900): drift=1.265 — mathematical term gaining currency
- `sinned` (pre-1500 → 1500-1700): drift=1.216 — theological term fading
- `touchstone` (1700-1800 → 1800-1850): drift=1.204 — Shakespearean to Romantic shift

### 3. ✅ zero-norm vectors handled
query.py now skips zero-norm vectors in neighbor queries (lines 63-65).

### 4. ✅ 1900-1923 corpus expanded
From 4 texts (May) to 12 texts (August) — 3x improvement for Modernist era coverage.

---

## What's Working Now

### Query Interface (`queries/query.py`)
```bash
python3 queries/query.py neighbors <word> <era> [n]
python3 queries/query.py drift <word>
python3 queries/query.py topdrift [era]
python3 queries/query.py compare <word> <era1> <era2>
```

### Dream Generation (`run-dream.sh`)
Generates semantic dreams via probabilistic walks through vector space with era jumps.

### Drift Detection (`worker/compute_drift.py`)
Computes cosine similarity drift between consecutive eras for all 7,703 vocabulary words.

---

## Control Status

The `control` file is set to `run` — the nightly 1am cron will execute if load/memory permit.

Current worker pipeline (`run-worker.sh`):
1. Builds co-occurrence matrices (if needed)
2. Builds word vectors (if needed)
3. Both steps are complete; cron checks and exits cleanly

---

## Next Possible Work (Not Required)

1. **More 1900-1923 texts** — Could expand Modernist corpus further (Joyce, Kafka, Woolf)
2. **Weekly analysis cron** — Automated semantic findings → memory reflections
3. **Phase 2** — Dream engine research using computed drift scores

---

## One-Line Summary

All May 2026 blockers resolved. Query interface functional. Drift scores computed. 1900-1923 corpus expanded. Archaeology worker is healthy and operational.
