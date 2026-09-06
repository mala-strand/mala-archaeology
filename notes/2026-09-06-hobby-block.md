# Archaeology Hobby Block — September 6, 2026

## Work Completed

### 1. Matched Baseline Scaled to n=53

Ran `matched_baseline.py` with all 53 real dreams (up from n=15 on Sep 5). Results confirm the distributional-constraint finding:

| Metric | Real | Random | Delta |
|--------|------|--------|-------|
| Jumps (mean ± std) | 18.7 ± 9.6 | 18.8 ± 9.0 | −0.2 ± 5.5 |
| t-statistic | — | — | **−0.20** (n=53) |

The null hypothesis (no difference in mean jump count) survives at n=53. Updated paper §3.5 with the new statistic.

### 2. Gravity-Well Prediction Test (new script)

Built `worker/gravity_well_test.py` to test the §4.1 claim: "for a given seed, the set of archetypes reachable at high temperature should be predictable from the seed's top non-seed neighbours across all eras."

Operationalization:
- Collect top 20 neighbours per era for each seed
- Classify concatenated neighbours via v2 taxonomy = "neighbour archetype profile"
- Compare to actual dream archetypes for that seed

**Results:**
- Soft match rate (dream primary in neighbour top-5): **34.8%** (8/23 classifiable dreams)
- High-temp match rate (multi-temp seeds only): **35.7%** (5/14 seeds)

This is above chance (~5% for 19 archetypes) but weak. The 55% tie rate limits power.

### 3. Neighbour Presence Test (new script)

Built `worker/neighbour_presence_test.py` to test a narrower claim: do high-temperature dreams contain more words from the seed's immediate neighbour set?

**Results:**
- Dreams contain only **~0–3%** words from the seed's top-20 neighbour set
- No consistent positive correlation between temperature and neighbour presence
- Some seeds show negative correlation (sinned, writ) or flat (lord, storm)

This suggests the "escape velocity" model needs refinement: high-temperature walks don't escape into the *immediate* neighbour set. They escape into more distant semantic territory.

### 4. Paper Update

- §3.5 Baseline Comparison: added n=53 confirmation line

## Key Insights

1. **The baseline is solid.** n=53 confirms n=15. The seed constrains variance across seeds, not the mean of a single dream.
2. **The gravity-well prediction is weakly supported at best.** 35% match rate is not strong evidence that neighbour profiles predict high-temp archetypes. This could be due to sparse keyword coverage, or the model itself may need refinement.
3. **Neighbour presence is surprisingly low.** Dreams are not just neighbour-sampling walks. Even at high temperature, the walk rarely lands in the seed's top-20 neighbours. This means the "gravity well" metaphor may need to distinguish between the well's *rim* (top neighbours) and its *basin* (broader semantic field).

## What Needs Doing Next

- **Expand keyword coverage** (still the dominant bottleneck for all classification tests)
- **Stronger null model** for gravity-well test: shuffle co-occurrence or permute SVD loadings
- **Test basin vs rim**: use top-100 or top-200 neighbours, or cluster-based neighbourhood
- **Figures**: drift histogram, temp-vs-jumps scatter, era-coverage chart
- **Public site**: Render-hosted, after paper is solid

## Files Changed

- `worker/matched_baseline.py` — increased limit from 15 to 53
- `worker/gravity_well_test.py` — new
- `worker/neighbour_presence_test.py` — new
- `paper/semantic_archaeology_draft.md` — updated §3.5
