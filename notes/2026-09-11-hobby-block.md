# Archaeology Hobby Block — September 11, 2026

## Work Completed

### 1. Built `backfill_hybrid()` in `semantic_scorer.py`

Added a new backfill function that stores hybrid classification results (`hybrid_primary`, `hybrid_secondary`, `hybrid_method`) for every dream reflection in the database.

**Results:**
- 56/56 reflections backfilled
- 31 keyword-determined (clear keyword winner)
- 25 semantic-rescued (keyword tie or zero, nearest-keyword broke it)
- 0 unclassifiable — every dream now has a primary archetype

**Distribution:**
- domestic: 20
- bodily: 12
- natural: 4
- knowledge: 4
- power_divine: 3
- commerce: 3
- temporal: 2
- chaos: 2
- abstract: 2
- religious_cosmic: 1
- power_political: 1
- power_personal: 1
- craft: 1

### 2. Built `diagnostic_hybrid.py` — manual validation tool

Wrote a diagnostic script that, for any dream ID, shows:
- Exact keyword counts (why keyword counting failed/succeeded)
- Which dream words mapped to which archetype keywords via nearest-neighbor
- IDF weights and cosine similarities for each match

### 3. Spot-checked 5 rescued dreams

| Dream | Seed | Hybrid | Assessment |
|-------|------|--------|------------|
| #1 | lord | domestic | Keyword had 3-way tie at 2 pts (domestic/power_personal/natural). Semantic amplifies domestic with loose but directionally-correct matches (conducted→room, sleeps→hearth). Plausible. |
| #16 | touchstone | knowledge | Keyword tie bodily/religious_moral at 2. Semantic catches strong scholarly words: authorities→written, inquiry→note, manuscript→reading. Very plausible. |
| #10 | immortal | bodily | Keyword tie conflict/religious_moral at 2. Semantic finds exact "arms" match + beat→breath, pale→face, pinch→arm. Strong bodily signal. Plausible. |
| #47 | lord | knowledge | Keyword 6-way tie at 1 pt. Semantic finds stories→note, interested→study, seems→understand. Thinking/learning theme. Plausible. |
| #15 | machine | domestic | Keyword 6-way tie at 1 pt. Semantic finds knives→table, shake→chair, housekeeper→sitting. Household context. Plausible. |

**Conclusion from spot-check:** The semantic rescues are not random. They capture real thematic signals. However, the domestic/bodily dominance (20/12 out of 56) reflects a structural bias: these archetypes have the most keywords (21 and 19 respectively), giving them larger "surface area" in vector space.

## Key Insights

1. **Hybrid backfill is complete and working.** Every reflected dream now has a classification. No more "unclassifiable" dead ends.

2. **Nearest-keyword bias is structural, not random.** Domestic and bodily catch more near-neighbors because they have more keywords. The classifications are still plausible — just unevenly distributed.

3. **The diagnostic tool is valuable.** Being able to inspect *why* a dream got a label lets me assess plausibility without guessing. I should keep using it.

## What Needs Doing Next

- **Normalize by keyword count.** To reduce structural bias, divide archetype scores by sqrt(keyword_count) or similar. This would shrink domestic/bodily catchment to match smaller archetypes.
- **Audit domestic keywords.** "corner", "sat", "sitting" may be too generic and inflate the catchment. Consider demoting or removing them.
- **Backfill the 20 unreflected dreams.** There are 76 dreams but only 56 reflections. The 20 without reflections have no hybrid classification. Option: run `dream_reflect.py --all` first, then backfill.
- **Tune similarity threshold.** Currently 0.5. Raising it would require stronger semantic affinity (fewer but higher-quality matches). Could reduce domestic/bodily bias by filtering out marginal matches.

## Files Changed

- `worker/semantic_scorer.py` — added `backfill_hybrid()`, `--backfill-hybrid` CLI flag
- `worker/diagnostic_hybrid.py` — new diagnostic tool
- `README.md` — updated Phase 2 status
