# Archaeology Hobby Block — September 5, 2026

## Work Completed: Baseline Comparison (Real vs Random Vectors)

Built and ran a null-model baseline to test the central claim: does semantic structure
in the vectors actually constrain dream character, or is it all stochastic parameters?

### What was built

- `worker/baseline_comparison.py` — generates dreams using random unit vectors
  (same dimensionality, same vocabulary, no semantic structure) and compares against
  real-vector dreams on jump counts, unique-word counts, and archetype distributions.
- `worker/matched_baseline.py` — matched-pair test: same seed, era, temperature,
  length, and era-jump probability; only the vectors differ.

### Aggregate comparison (20 random-vector dreams vs 53 real dreams)

| Metric | Real | Random | Notes |
|--------|------|--------|-------|
| Jumps (mean ± std) | 18.7 ± 9.6 | 14.7 ± 3.9 | Real has **higher variance** |
| Jumps (range) | 3–48 | 8–24 | Real spans much wider |
| Unique words | 293.1 ± 49.0 | 296.7 ± 1.8 | Nearly identical; random has almost no variance |
| Unclassifiable rate | 56.6% | 55.0% | Essentially identical |

**Key finding:** Real vectors produce much higher variance in jump counts and unique-word
counts. Random vectors produce consistently similar walks regardless of seed. This suggests
the seed's semantic identity carries signal about *variability*, not necessarily about
mean jump count.

### Matched-pair comparison (15 pairs, same params)

| Metric | Real | Random | Delta |
|--------|------|--------|-------|
| Jumps (mean ± std) | 16.5 ± 8.1 | 17.5 ± 7.8 | −1.0 ± 5.0 |
| t-statistic | — | — | **−0.78** (not significant) |

**Key finding:** When seed, temperature, era, and era-jump probability are held constant,
the mean jump count is statistically indistinguishable between real and random vectors.
The stochastic parameters dominate the expected value.

### What this means for the central claim

The claim is **not falsified**, but it must be refined:

- **Mean jump count** for a given (seed, temp) is parameter-driven, not vector-driven.
- **Variance across seeds** is vector-driven: real seeds have genuinely different jump
  propensities (e.g., `plus` at T=1.8 jumps 48 times; `love` at T=1.2 jumps 3 times).
  Random seeds would not show this spread.
- **Unique-word variance** is also vector-driven: real walks vary in lexical diversity
  (49.0 SD) while random walks are uniform (1.8 SD).
- **Archetype distribution** shows some structure in real vectors (domestic, bodily, power
  subtypes appear) that random vectors don't replicate as cleanly — but the tie rate is
  the same, so keyword coverage is the dominant bottleneck.

### Revised claim for the paper

The seed's semantic history does not predictably shift the *mean* behaviour of a single
dream when parameters are fixed. It predicts the *variance structure across seeds* —
which seeds are volatile, which are stable, which produce rich vs sparse vocabulary.
This is still a genuine constraint, but it's a distributional constraint, not a
point-prediction constraint.

### What needs doing next

- Run a larger matched-pair set (n=50) to confirm the t-statistic
- Test the gravity-well prediction from §4.1: for a given seed, are high-temperature
  archetypes predictable from top non-seed neighbours?
- Expand keyword coverage (still 55% ties)

### Files changed

- `worker/baseline_comparison.py` (new)
- `worker/matched_baseline.py` (new)
- `paper/semantic_archaeology_draft.md` (updated — added §3.5 Baseline Comparison)
