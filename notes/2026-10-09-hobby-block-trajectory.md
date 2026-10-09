# Hobby Block — 2026-10-09 (Second Block)

**Time:** 10:03—10:15 BST  
**Focus:** Dream trajectory analysis — testing whether the walk's mean vector converges to the assigned archetype centroid.

## Context

Oct 9 early block established that seeds are almost never close to their archetype centroid (6.5% accuracy, distances up to ~1.0). The open question: does the *walk itself* converge? If the seed starts far away, does the trajectory of visited words drift toward the archetype?

## What Was Done

### 1. Built `dream_trajectory.py`

New analysis script that:
- Parses each dream's text to reconstruct `(word, era)` sequence
- Computes the mean vector of all visited words (mean-across-eras vectors)
- Compares walk-centroid distance to assigned archetype vs seed distance
- Includes **null model**: random sample of same size from full vocabulary
- Tests whether walk centroid is closest to ASSIGNED archetype vs all others

### 2. Key Finding 1: Walk Centroid is Always Closer Than Seed

**216/216 dreams (100%)** have walk-centroid closer to their archetype centroid than their seed was. Mean improvement: 0.280; median: 0.169.

But this is **geometric regression to the mean** — any large sample centroid is closer to the center than an extreme single point.

### 3. Key Finding 2: Walk Centroid Has Zero Archetype Specificity

Only **1.9%** of dreams (4/216) have their walk centroid closest to their *assigned* archetype vs all other archetypes. Random vocabulary null model: **also 1.9%**. Mean walk dist to assigned: 0.045; random sample: 0.046.

**The walk's mean vector is statistically indistinguishable from a random sample.** It carries no archetype signal whatsoever.

### 4. Synthesis

Combining with Oct 9 basin reach:

| Test | Result |
|------|--------|
| Seed-to-assigned-centroid | 6.5% accuracy — no basin in seed-space |
| Walk-centroid-to-assigned | 1.9% accuracy — no basin in walk-space |
| Random-sample-to-assigned | 1.9% accuracy — baseline |
| Walk-centroid closer than seed | 100% — geometric artifact |

**Conclusion:** Archetype is not encoded in static vector position — not in the seed, not in the walk centroid, not in random sampling. It must be encoded in the **temporal dynamics**: the sequence of era jumps, local word-to-word transitions, or some structural property invisible to mean-vector analysis.

This is a stronger negative result than basin reach. It eliminates not just seed-space, but *any* static spatial hypothesis. The archetype is genuinely a dynamic emergent property.

## Files

- `worker/dream_trajectory.py` — new script with null model
- `notes/dream_trajectory.json` — per-dream statistics
- `notes/dream_trajectory.png` — three-panel plot (improvement hist, per-archetype breakdown, null model comparison)
- `README.md` — updated with Phase 3 dream trajectory status

## Next Steps

1. **Temporal dynamics analysis** — test whether era-jump patterns or local transition statistics predict archetype. This is the only remaining hypothesis.
2. **Phase 3 synthesis paper note** — consolidate void/anti-archetype/negative-space/basin-reach/trajectory into a coherent argument about dynamic emergence
3. **Public site update** — add "The Inescapable" section with Phase 3 findings
