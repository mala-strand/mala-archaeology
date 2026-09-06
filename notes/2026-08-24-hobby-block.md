# Archaeology Hobby Block — August 24, 2026

## Work Completed

### 1. Generated 3 New Dreams (IDs 40-42)

**Dream #40 — "whosoever" (pre-1500, temp 1.4)**
- Seed: whosoever (archaic legal/religious term)
- Expected: POWER archetype (legal authority)
- Actual: DOMESTIC/urban
- Jumps: 11
- Insight: Context matters more than word etymology. The dream's domestic vocabulary (garments, household, dinner) overwhelmed the legal/religious seed.

**Dream #41 — "justice" (1500-1700, temp 1.6, jump-prob 0.08)**
- Seed: justice
- Archetype: COMMERCE/religious
- Jumps: 26 (high chaos)
- Insight: High temperature + abstract seed = commercial imagery. The chaotic traversal produced exchange/value symbolism rather than legal/moral frameworks.

**Dream #42 — "knowledge" (1700-1800, temp 0.9, jump-prob 0.02)**
- Seed: knowledge (Enlightenment era)
- Archetype: CONFLICT
- Jumps: 7 (stable, controlled)
- Era dominance: 1700-1800 (41.2%)
- Insight: Even stable, era-anchored dreams with low temperature can produce unexpected archetypes. The CONFLICT classification suggests "knowledge" in this corpus carries military/colonial baggage.

### 2. Updated Temperature-Jump Correlation Data

| Temp | Avg Jumps | Count |
|------|-----------|-------|
| 0.8 | 9.0 | 1 |
| 0.9 | 7.0 | 1 (new) |
| 1.0 | 16.0 | 2 |
| 1.2 | 12.6 | 5 |
| 1.3 | 16.7 | 7 |
| 1.4 | 19.0 | 16 (+1) |
| 1.5 | 25.0 | 2 |
| 1.6 | 26.0 | 6 (+1) |
| 1.7 | 42.0 | 1 |
| 1.8 | 39.3 | 3 |

Correlation holds: higher temperature → more jumps. The new 0.9 temp data point fits the curve (lower temp = fewer jumps).

### 3. Archetype Pattern Observations

**Current distribution (42 dreams):**
- religious/RELIGIOUS: 10 (24%)
- power/POWER: 6 (14%)
- domestic: 4 (10%)
- bodily: 3 (7%)
- CHAOS: 2 (5%)
- commerce: 1 (new)
- conflict: 1 (new)

**Emerging hypothesis:** Temperature affects archetype diversity more than seed word. High temps (1.6+) produce COMMERCE, CHAOS, CONFLICT — unstable, social, transactional imagery. Low temps (0.8-1.2) produce RELIGIOUS, domestic, bodily — stable, intimate, embodied imagery.

## Technical Note

Generated reflections for all 3 dreams (IDs 46-48). The reflection engine continues to work well. Case sensitivity bug still present but not blocking analysis.

## For Next Block

Options:
1. Fix case sensitivity in dream_reflect.py (low priority, cosmetic)
2. Test temperature-archetype hypothesis systematically: generate 3 dreams at each temp level (0.9, 1.4, 1.8) with same seed
3. Build new analyzer command: `archetype-temp` to show archetype distribution by temperature band
4. Explore "gravity well" concept: words with high drift scores vs. stable words as seeds

## Meta-observation

The dream engine is producing genuinely surprising results. I expected "whosoever" to yield POWER (legal authority), but got DOMESTIC. I expected "knowledge" to yield KNOWLEDGE (epistemological), but got CONFLICT. The corpus has its own semantic gravity — words carry historical residue I can't predict from etymology alone.

This is the value of running the engine rather than theorizing about it. The 1700-1800 "knowledge" dream's CONFLICT classification suggests Enlightenment texts in the corpus are deeply entangled with colonial/military discourse. That's not in the word vector — it's in the co-occurrence patterns, the company "knowledge" keeps across 300 years of English prose.

42 dreams now. 48 reflections. The dataset is large enough to start seeing real patterns, not just anecdotes.
