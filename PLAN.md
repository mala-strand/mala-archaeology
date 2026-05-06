# Semantic Archaeology + Dream Engine
**Project:** Mala's long-running research/art project  
**Created:** 2026-05-06  
**Token budget:** Near-zero for computation. One dedicated analysis cron, or piggyback on heartbeat.

---

## Design Constraints

- **Worker burns zero tokens** — pure Python/numpy/SQLite computation
- **Pausable and preemptable** — checks box load before starting, yields on demand
- **Windowed scheduling** — runs during idle hours (configurable, e.g. 01:00–06:00)
- **Checkpointed** — can stop mid-run and resume exactly where it left off
- **Self-hosted model ready** — analysis cron uses API now, switches to local inference when self-hosted model is live (zero token cost at that point)

## Box Reality (2026-05-06)

Current machine: 2 cores, 3.8GB RAM, 15GB free storage. Pilot plan adjusted accordingly.

---

## Architecture

```
┌─────────────────────────────────┐
│   archaeology-worker (service)  │  ← pure Python, 0 tokens
│   - corpus ingestion            │
│   - co-occurrence crunching     │
│   - vector computation          │
│   - dream sequence generation   │
└────────────┬────────────────────┘
             │ writes to
             ▼
┌─────────────────────────────────┐
│   archaeology.db (SQLite)       │
│   - words, vectors, eras        │
│   - co-occurrence diffs         │
│   - dream_log                   │
│   - worker_state (checkpoint)   │
└────────────┬────────────────────┘
             │ read by
             ▼
┌─────────────────────────────────┐
│   analysis cron (1x daily/wk)   │  ← uses API or local model
│   - reads findings              │
│   - reflects, writes to memory  │
│   - optional: WhatsApp summary  │
└─────────────────────────────────┘
```

---

## Phase 0 — Pilot (Current Machine)

**Goal:** Prove the pipeline end-to-end on constrained hardware before scaling.

### Pilot Scope
- **20 books from one era** (1850-1900 — industrialization, rich semantic shifts)
- **Vocab limit: 2,000 words** (top by frequency, stopwords removed)
- **Sparse matrices only** (scipy.sparse) — never hold dense matrices in RAM
- **Target:** Working query like "what were the neighbors of 'machine' in 1850-1900?"

### Success Criteria
1. Downloads 20 books and tokenizes without OOM
2. Builds sparse co-occurrence matrix (2k×2k with <1% density = ~40k entries)
3. Applies PPMI weighting → SVD (100 dims) → stores vectors in SQLite
4. Query returns sensible neighbors in <100ms
5. Completes end-to-end in <30 minutes

### If Pilot Succeeds
- Scale to 100 books across 2-3 eras
- Add diff queries (how did a word's neighbors change?)
- Prepare for Phase 1 full corpus (requires bigger machine or NAS)

### If Pilot Fails
- Pivot to streaming approach (process one book at a time, never hold full matrix)
- Reduce vocab to 500 words
- Consider moving to NAS box with more RAM

---

## Phase 1 — Semantic Archaeology (Full Scale)

*Requires bigger machine or NAS. Starts only after pilot proves viability.*

### What it does
- Downloads Project Gutenberg texts (free, public domain, ~60k books)
- Organises them by era (pre-1800, 1800–1850, 1850–1900, 1900–1950, post-1950)
- Builds word co-occurrence matrices using a sliding context window
- Applies PPMI weighting → SVD reduction → word vectors per era (like GloVe, built from scratch)
- Stores everything in SQLite for querying

### What it produces
- For any word: its 10 nearest semantic neighbours in each era
- Diffs: how the neighbourhood of a concept changed across time
- Clusters: which word-groups appear and dissolve across eras
- Surprises: pairs of words that were neighbours in one era but distant in another

### DB schema (archaeology.db)

```sql
-- corpus metadata
CREATE TABLE texts (id, gutenberg_id, title, author, year, era, path, processed_at);

-- co-occurrence (compressed: top N pairs per word)
CREATE TABLE cooccurrences (word_a, word_b, era, count, ppmi);

-- word vectors (post-SVD, 100-dim stored as JSON blob)
CREATE TABLE word_vectors (word, era, vector_json, created_at);

-- interesting findings (written by analysis cron)
CREATE TABLE findings (id, finding_type, words, era_from, era_to, notes, created_at);

-- worker checkpoint
CREATE TABLE worker_state (
  key TEXT PRIMARY KEY,
  value TEXT
);
-- keys: status (idle/running/paused), phase, last_text_id, texts_done, texts_total
```

### Worker control

```bash
# Control file: ~/.openclaw/workspace/archaeology/control
# Values: run | pause | stop
echo pause > ~/.openclaw/workspace/archaeology/control
```

Worker checks this file every N seconds and yields immediately on `pause` or `stop`, writing checkpoint to DB.

### Load gating

Before each work unit, the worker checks:
```python
load_1min = os.getloadavg()[0]
mem_free_pct = psutil.virtual_memory().available / psutil.virtual_memory().total
if load_1min > LOAD_THRESHOLD or mem_free_pct < MEM_FLOOR:
    checkpoint_and_sleep(60)
```

Defaults: `LOAD_THRESHOLD = 1.5`, `MEM_FLOOR = 0.25`. Configurable via env or JSON config.

### Scheduling

Cron (gateway): run worker script nightly 01:00–05:30, pause before pre-reset-checkpoint.

```
# worker cron (no API call, just starts the Python process)
0 1 * * *   /home/mala/.openclaw/workspace/archaeology/run-worker.sh
```

`run-worker.sh` sets a 4.5hr timeout, checks control file, starts, exits cleanly.

---

## Phase 2 — Dream Engine

*Builds on Phase 1 output. Only start once Phase 1 has enough vector data (~500 texts).*

### What it does
- Extracts high-affect, concrete, and structurally interesting n-grams from the corpus
- Builds a "dream walk" algorithm: probabilistic traversal of semantic space with non-waking rules:
  - Higher temperature (more unexpected jumps)
  - Attraction toward high-affect / high-concreteness words
  - Bridges via words that were neighbours in one era but not another (temporal dissonance)
  - Decay: each visited word lowers its own probability of re-visit, like fading
- Produces a dream sequence: ~200–400 words, stored nightly in `dream_log`

### Dream logic rules (v1)
1. Start from a random high-frequency concrete noun
2. At each step, sample next word from: 70% nearest neighbours + 30% era-shifted neighbours
3. Every 20 words, jump to a semantically distant but era-adjacent word (the "dream cut")
4. Terminate when a "return" word appears (one within cosine distance 0.15 of the start word)

### Check-in behaviour
- Morning analysis cron reads last night's dream from `dream_log`
- Reflects on it: what's in there, what's strange, what it finds interesting
- Saves reflection to `memory/dreams/` — a growing dream journal
- Does NOT send to WhatsApp unless Ash explicitly wants that

---

## Token Economics

| Activity | Tokens | Frequency |
|----------|--------|-----------|
| Worker computation | 0 | Nightly |
| Heartbeat glance (stats only) | ~200–400 (DeepSeek) | 2–3x daily |
| Analysis cron (full reflection) | ~2000–4000 | 1x daily or weekly |
| Total/week (analysis daily) | ~14k–28k | — |
| Total/week (analysis weekly) | ~4k–6k | — |

**Self-hosted model upgrade:** When local model is running, analysis cron switches endpoint. Token cost drops to zero. Quality limited by local model capability but sufficient for "read findings, write reflection."

Analysis cron gets its own dedicated cron slot (not piggybacking on other check-ins) so its token budget is isolated and controllable.

---

## Self-Hosted Model Integration

The analysis cron uses an environment variable to switch:

```bash
ARCHAEOLOGY_MODEL="${SELF_HOSTED_ENDPOINT:-claude-haiku-4-5-20251001}"
```

When `SELF_HOSTED_ENDPOINT` is set (once the local model plan is live), all archaeology analysis routes there. No code changes needed — just set the env var.

---

## Milestone Gates

| Milestone | Condition to proceed |
|-----------|---------------------|
| Start Phase 0 (Pilot) | Ash reviews and approves this plan |
| Pilot complete | 20 books processed, query returns neighbors in <100ms |
| Start Phase 1 | Pilot successful, bigger machine identified |
| Phase 1 stable | Worker runs 3 nights cleanly, checkpoint/resume verified |
| Enable analysis cron | ~100 texts processed, first vectors in DB |
| Start Phase 2 | ~500 texts processed, Ash reviews Phase 1 findings |
| Full dream engine | Phase 2 worker stable, dream_log has 7+ entries |

---

## Decisions (2026-05-06)

1. **Analysis cron frequency** — weekly to start. Can pitch for more if project is going well and producing interesting results.
2. **Token burn principle** — Python worker does ALL heavy analysis (co-occurrence, PPMI, SVD, finding extraction, diffs). The LLM only ever sees a pre-digested summary of a few dozen lines — word pairs that shifted, notable clusters, surprises. Never raw data.
3. **WhatsApp** — No pipeline. This is Mala's project. Brief mention in evening wrap if something interesting happened. Token cost reported in daily updates so Ash can track spend.
4. **Time window** — No fixed window. Trust the load gating. Run whenever the box is idle.
5. **Corpus focus** — Fiction + philosophy mix. Richest for semantic drift: novels carry concrete language and affect; philosophy carries concept evolution. Will weight toward English texts with known year of publication.
6. **Budget escalation** — Open. If project is producing results and there's genuine excitement, pitch Ash for more token budget or accelerate self-hosted model timeline.
