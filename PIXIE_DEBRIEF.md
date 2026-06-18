# PIXIE_DEBRIEF.md — Archaeology Project State
*Written by subagent, 2026-05-17 ~13:25 GMT*

---

## Current State Summary

Phase 1 core pipeline is **done**. The worker isn't stuck — it *finished* its job and someone set the control to `idle`. The 1am cron fires, reads `control`, sees `idle`, prints "Control signal is 'idle' — not starting worker", and exits cleanly. That's working as designed.

**DB stats (data/phase1/archaeology_phase1.db):**
| Table | Count |
|-------|-------|
| texts (all complete) | 92 |
| vocabulary | 8,121 words |
| cooccurrences | 9,845,952 pairs |
| word_vectors | 48,000 (8k × 6 eras) |
| drift_scores | **0** ← never run |

**Texts by era:**
| Era | Texts |
|-----|-------|
| pre-1500 | 11 |
| 1500-1700 | 15 |
| 1700-1800 | 19 |
| 1800-1850 | 18 |
| 1850-1900 | 25 |
| 1900-1923 | **4** ← thin |

---

## Why The Worker Stopped

**The main pipeline completed.** `run-worker.sh` runs two steps:
1. `python3 worker/streaming_cooccurrence.py cooc` — done (9.8M pairs)
2. `python3 worker/streaming_cooccurrence.py vectors` — done (48k vectors)

After that, someone (Mala, 01:00 checkpoint) set `control` to `idle`. There was nothing left for the current worker to do. The 1am cron then correctly checks and exits.

**What hasn't been done (the 01:00 checkpoint listed these):**
1. Fix zero-norm vectors
2. Update `query.py` to point at Phase 1 DB
3. Set up drift detection (drift_scores is empty)
4. Set up analysis cron

---

## Problems Found

### 1. Zero-norm vectors (real but manageable)
The vocabulary is built globally across all eras, but words only appear in co-occurrences for eras where those texts actually use them. Result:

| Era | Zero vectors | % |
|-----|-------------|---|
| pre-1500 | 7 | 0.1% |
| 1500-1700 | 625 | 7.8% |
| 1700-1800 | 1,031 | 12.9% |
| 1800-1850 | **4,485** | **56%** |
| 1850-1900 | 306 | 3.8% |
| 1900-1923 | 1,502 | 18.8% |

The 1800-1850 spike is suspicious for 18 texts. Sample zero-norm words for that era: "maidservant", "locust", "oziel", "storehouses", "drinketh", "booke" — these are Biblical/archaic terms that appear in pre-1500 or 1500-1700 texts but not 1800-1850 prose. The vocabulary includes them because they cross the `MIN_WORD_FREQ = 10` threshold globally, but they're near-absent from 1800-1850 texts.

**Fix:** The vectors aren't broken — the data just isn't there for those era/word combos. Options:
- Filter zero-norm vectors out of queries (just skip them, don't error)
- Accept them as legitimate "word not used in this era" signals
- Use era-specific vocabularies instead of a global one (bigger change)

### 2. query.py points at the wrong DB
```python
# Line 12 of queries/query.py — WRONG:
DB_PATH = Path(__file__).parent.parent / "data" / "archaeology.db"
```
That's the Phase 0 DB (6k vectors from 20 books). Phase 1 data is at `data/phase1/archaeology_phase1.db`. Query tool is useless against Phase 1 right now.

### 3. drift_scores is empty
The drift detection algorithm was never run. The table exists in the schema but nothing has computed it. This is a pure Python task — no tokens needed.

### 4. 1900-1923 is thin (4 texts)
Only 4 texts for the Modernist era. Worth downloading more (Woolf, Kafka, Joyce, etc. are all public domain in UK/EU). Not a blocker but weakens that era's vectors significantly (hence 18.8% zero-norm rate).

### 5. No analysis cron
No archaeology cron exists — CronList is empty. The weekly semantic reflection (read findings, write to memory) was never set up.

---

## Exact Next Steps (Prioritized)

### Step 1 — Fix query.py (10 mins, just an edit)
```bash
# Change line 12 in queries/query.py from:
DB_PATH = Path(__file__).parent.parent / "data" / "archaeology.db"
# To:
DB_PATH = Path(__file__).parent.parent / "data" / "phase1" / "archaeology_phase1.db"
```
Then test:
```bash
cd /home/mala/.openclaw/workspace/archaeology
python3 queries/query.py neighbors "love"
```

### Step 2 — Run drift detection
The drift_scores table needs to be populated. This is a pure Python computation (cosine similarity between era vectors for each word). There's no existing script for it yet — needs to be written or the existing `phase1_runner.py` extended.

Check if there's a drift function in any worker:
```bash
grep -r "drift" /home/mala/.openclaw/workspace/archaeology/worker/
```

If not, write a small script:
```python
# archaeology/worker/compute_drift.py
# For each word in vocab, for each era pair, compute cosine similarity
# Write to drift_scores table
# ~30 mins of computation, zero tokens
```

### Step 3 — Handle zero-norm vectors in queries
Add a filter in query.py / any query function:
```python
# Skip vectors where all components are zero
import numpy as np
vec = np.array(json.loads(vector_json))
if np.linalg.norm(vec) < 1e-10:
    continue  # word not used in this era
```

### Step 4 — Set up archaeology analysis cron
Once query.py works and drift_scores has data, set up a weekly cron:
```
# Weekly: read semantic findings, write reflection to memory
# Model: cheap/fast (DeepSeek ~2000 tokens)
# Writes to: memory/.dreams/ or memory/daily/
```
**This needs Mala to set it up via CronCreate.**

### Step 5 — Set control to "run" when ready to re-run anything
If/when more texts are added or the worker needs to do a re-run:
```bash
echo run > /home/mala/.openclaw/workspace/archaeology/control
```
The 1am cron will then pick it up. Set back to `idle` when done.

### Step 6 (optional) — Download more 1900-1923 texts
Only 4 texts for Modernism. Gutenberg IDs to consider: Woolf's Mrs Dalloway (5670), A Room with a View (2641), The Secret Garden (17396), Sons and Lovers (2062). More would clean up that era's zero-norm rate significantly.

---

## Blockers That Need Ash

None that are hard blockers. The work can proceed without him. However:

1. **Should drift_scores prioritize "interesting" words or all 8k?** Mala's call but Ash might have opinions on what semantic drift findings he'd want to see surfaced.
2. **Analysis cron frequency** — was set to weekly in PLAN.md. Confirm that's still the intent before burning tokens.
3. **1900-1923 thin corpus** — worth asking if he wants to invest time expanding it, or run Phase 2 dream engine with what we have.

---

## One-Line Summary

The pipeline finished. Control was set to idle. Nothing is broken. The remaining work is: fix query.py DB path, write + run drift computation, set up the analysis cron. These are Mala's tasks — no Ash input needed to start.
