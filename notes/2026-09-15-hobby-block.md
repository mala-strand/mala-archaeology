# Archaeology Hobby Block — September 15, 2026

## Work Completed

### 1. Built `drift_dream_correlator_v2.py` — Full-corpus drift analysis

Replaced the hardcoded DRIFT_TYPES dictionary from v1 with dynamic auto-classification based on statistical properties of each word's drift trajectory.

**Auto-classification rules:**
- `spike` — one extreme transition, others low (ratio >2.0, peak >1.0)
- `high_drift` — average drift >0.8
- `stable_core` — avg <0.4 and max <0.5
- `stable_concept` — avg <0.55
- `pivot` — avg ≥0.55 and max >0.7
- `moderate` — everything else

**Results on n=200:**
- 190/200 dreams have drift data
- **Drift × jump count: r = +0.014** (no correlation overall)
- **Temperature × jump count: r = +0.130** (weak positive, as expected)
- **Critical interaction:** At high temp (>1.6), drift×jump r = **+0.211**. At low temp (≤1.2), drift×jump r = **-0.157**.

This validates the "semantic gravity well" hypothesis — but only conditionally. High-drift words pull dreams toward chaos **when the temperature is already high enough to allow it**. At low temperature, high-drift words are actually *less* likely to jump. The drift type doesn't override the walk parameters; it modulates them.

### 2. Built `archetype_cooccurrence.py` — Archetype pair analysis

Analyzes which archetypes appear together (primary + secondary) and which never co-occur.

**Key findings:**
- Distribution remains flat across 19 archetypes (top: abstract 10.0%, bottom: identity/power_personal 1.0% each)
- **93 forbidden pairs** out of 190 possible unordered pairs (49%)
- Most common pairing: **power_divine + religious_cosmic** (6 times)
- `unclassifiable` never appears as secondary
- Notable forbidden pairs with both members ≥3×: abstract+chaos, bodily+legacy, chaos+commerce, bodily+power_political

**Jump count by archetype:**
- Highest: power_personal (30.0), commerce (26.6), religious_devotion (23.7)
- Lowest: chaos (11.8), religious_cosmic (13.5), craft (15.0)
- Surprising: chaos has the *lowest* jumps. The archetype labeled "chaos" is associated with the most stable walks.

**Temperature by archetype:**
- Highest: craft (1.66), bodily (1.50), religious_moral (1.49)
- Lowest: chaos (1.00), urban (1.12), domestic (1.18)
- The chaos archetype is generated at the lowest average temperature — it emerges from stable walks, not wild ones.

### 3. Updated README.md

Documented the two new scripts and their findings.

## Key Insights

1. **The semantic gravity well is conditional, not absolute.** Drift magnitude doesn't directly cause jumps — it amplifies jump probability *given* high temperature. This is an interaction effect, not a main effect. The v1 hypothesis was too simple.

2. **"Chaos" archetype is a misnomer in practice.** Dreams classified as "chaos" have the lowest jump counts and are generated at the lowest temperatures. The archetype captures something else — perhaps thematic content (disorder, destruction) rather than structural chaos. The classifier may be picking up on vocabulary clusters rather than walk behavior.

3. **Nearly half of all archetype pairs are forbidden.** 93/190 pairs never co-occur. This suggests the taxonomy has real structure — the archetypes aren't randomly distributed. Some combinations are semantically incompatible (e.g., bodily + power_political).

4. **power_divine + religious_cosmic is the strongest pair.** These two co-occur 6 times — more than any other pair. This makes sense: cosmic-scale divinity and religious devotion are conceptually adjacent.

## What Needs Doing Next

- **Re-run `dream_analysis.py` on n=200.** The existing script still uses raw JOIN without latest-reflection windowing. Fix and re-run for updated seed-word patterns and extreme dreams.
- **Null model for gravity-well test.** The PLAN.md open experiment #1 is still unaddressed. Shuffle co-occurrence or permute SVD loadings to test whether the drift×temperature interaction is significant.
- **Basin-vs-rim test.** Compare top-20 vs top-100 vs top-200 neighbor scales for gravity-well structure.
- **Chaos archetype investigation.** Why does the "chaos" archetype correlate with low jumps and low temperature? Examine the actual dream texts classified as chaos.

## Files Changed

- `worker/drift_dream_correlator_v2.py` — new
- `worker/archetype_cooccurrence.py` — new
- `README.md` — updated
