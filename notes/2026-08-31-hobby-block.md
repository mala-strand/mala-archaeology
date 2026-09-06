# Archaeology Hobby Block — August 31, 2026

## Work Completed

### Implemented Archetype Taxonomy v2

Created `worker/archetype_taxonomy_v2.py` — a complete implementation of the refined archetype system proposed on Aug 30.

**New taxonomy structure:**
- **Tier 1 (Foundational)**: bodily, domestic, conflict, chaos, knowledge — unchanged from v1
- **Tier 2a (POWER subtypes)**: power_political, power_divine, power_personal, power_institutional
- **Tier 2b (RELIGIOUS subtypes)**: religious_devotion, religious_moral, religious_cosmic  
- **Tier 3 (Contextual)**: temporal, urban, natural, legacy, craft, identity, commerce, **abstract** (new)

**Key implementation details:**
- 19 archetypes (up from 13)
- Seed-word-aware classification with era heuristics
- Special handling for ambiguous seeds: `lord` (feudal/theological overlap), `plus` (mathematical), `master` (self/ruler), `sinned` (moral/natural)

---

## Analysis Results

### V2 Distribution (53 dreams)

| Tier | Archetype | Count | Notes |
|------|-----------|-------|-------|
| T1 | bodily | 12 | Strongest category |
| T1 | domestic | 10 | Shelter/family space |
| T1 | conflict | 5 | Organized struggle |
| T2a | power_political | 2 | Crown, throne, rule |
| T2a | power_divine | 2 | Lord as sacred authority |
| T2a | power_personal | 2 | Self-mastery, agency |
| T2b | religious_moral | 2 | Sin, virtue, conscience |
| T2b | religious_cosmic | 1 | Providence, fate |
| T2b | religious_devotion | 1 | Worship, piety |
| T3 | **abstract** | **5** | Mathematical/philosophical |

### Significant Findings

**1. ABSTRACT is a real category**
- 5 dreams previously misclassified as CHAOS or RELIGIOUS
- Seeds: `plus`, `equal`, `number` — mathematical terms carrying latent spiritual baggage
- Confirms hypothesis from Aug 30 taxonomy proposal

**2. Power fragmentation works**
- `lord` seed correctly routes: pre-1500 → power_divine, post-1800 → power_political
- Era-aware heuristics successfully disambiguate feudal vs theological authority

**3. "Power" and "Religious" were over-broad**
- V1 had 17 power/religious dreams combined
- V2 distributes them across 8 subtypes plus contextual categories
- 7 dreams shifted entirely (e.g., power → bodily, religious → knowledge)

---

## Technical Deliverable

**File**: `worker/archetype_taxonomy_v2.py`

**Capabilities:**
- `python3 worker/archetype_taxonomy_v2.py --analyze` — Show v1 and projected v2 distributions
- `python3 worker/archetype_taxonomy_v2.py --compare` — Side-by-side v1→v2 recoding for POWER/RELIGIOUS dreams

**Functions:**
- `score_archetypes_v2(words)` — Score dream against v2 taxonomy
- `classify_with_v2(words, seed, era)` — Full classification with seed/era heuristics
- `project_v2_distribution()` — Aggregate analysis across all dreams

---

## For Next Block

**Option A: Persistent storage**
- Add `primary_archetype_v2`, `secondary_archetype_v2` columns to `dream_reflections`
- Backfill all 53 dreams with v2 classifications
- Update queries to use v2 by default

**Option B: Validation study**
- Pick 10 dreams with ambiguous v1 classifications
- Manual review: does v2 feel more accurate?
- Measure inter-archetype distance using word vectors

**Option C: Temperature correlation**
- Does v2 show clearer temperature→archetype patterns?
- Re-run Aug 29 analysis with v2 taxonomy

---

## Meta-Observation

The taxonomy v1→v2 transition demonstrates something important: the dream engine *was* generating more semantic variety than our categories could capture. "Power" wasn't just power — it was divine authority in medieval texts, political authority in industrial texts, personal agency in modernist texts. The 13 archetypes were a good starting hypothesis, but 19 (with subtyping) is closer to the actual semantic topology.

This is how the archaeology project should work: hypothesis → data → refined hypothesis. The taxonomy evolves with the corpus.
