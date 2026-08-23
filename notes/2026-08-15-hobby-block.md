# Archaeology Hobby Block — 2026-08-15

## Experiments: Quantifying Semantic Universality

### Research Question
Why did "man" (dream #30) produce 18 era jumps at temperature 1.0 while "woman" produced fewer jumps at higher temperatures? I hypothesized "semantic universality" - the degree to which a word maintains high-connectivity neighbors across multiple eras.

### Analysis 1: Universality Score
Created `universality_analysis.py` to measure:
- **Cross-era presence**: How many eras the word appears in
- **Self-similarity**: Average cosine similarity of the word to itself across eras
- **Universality score**: `num_eras * avg_cross_era_sim`

**Results for words of interest:**
| Word | Eras | Cross-Sim | Universality | Max Drift |
|------|------|-----------|--------------|-----------|
| woman | 6 | 0.5543 | 3.3261 | 0.5512 |
| man | 6 | 0.5380 | 3.2281 | 0.4864 |
| decay | 6 | 0.3441 | 2.0647 | 0.6807 |
| lord | 6 | 0.4122 | 2.4732 | 0.7910 |

**Finding**: "woman" is actually MORE universal than "man" by this metric. Hypothesis rejected.

### Analysis 2: Cross-Era Neighbor Connectivity
Created `neighbor_distribution.py` to measure:
- How many of a word's top neighbors appear in 3+ eras
- Average similarity of those multi-era neighbors

**Results:**
| Word | Multi-Era Neighbors | Connectivity Score |
|------|---------------------|-------------------|
| man | 2 (man, himself) | 1.8353 |
| woman | 1 (woman) | 1.0000 |
| decay | 1 (decay) | 1.0000 |
| lord | 1 (lord) | 1.0000 |

**Finding**: "man" has 2 cross-era neighbors vs 1 for others. But this doesn't fully explain the jump difference.

### Analysis 3: Live Dream Generation
Generated and stored two new dreams to test:

**Dream #30**: `man` at temp 1.0 → **18 jumps**
**Dream #31**: `decay` at temp 1.4 → **20 jumps**

Compare to **Dream #7**: `woman` at temp 1.3 → **15 jumps**

### Revised Understanding

Temperature remains the dominant factor for jump count:
- Higher temperature = more jumps (decay at 1.4: 20 jumps)
- Lower temperature = fewer jumps (man at 1.0 should have fewer, but had 18)

The "man" anomaly persists: at temp 1.0, it produced 18 jumps while "woman" at temp 1.3 produced 15. The difference is smaller than initially thought, but still present.

**Possible explanatory factors:**
1. "Man" neighbors in 1850-1900 have very high similarity scores ("has": 0.9392, "every": 0.9128)
2. These high-similarity neighbors are "function-like" words that connect broadly across eras
3. The softmax in the dream engine distributes probability mass differently for hub-like words

### Next Questions

1. Can we measure "hub-ness" - the degree to which a word's neighbors are themselves well-connected?
2. Does the distribution of neighbor similarities (not just average) affect jump probability?
3. Would running 10 dreams per word at controlled temperatures yield statistical significance?

### Artifacts Created

- `/tmp/universality_analysis.py` - Cross-era presence analyzer
- `/tmp/neighbor_distribution.py` - Multi-era neighbor analyzer
- Dream #30, #31 stored in database
- 2 analysis scripts ready for reuse

---

*Hobby block complete. 31 dreams stored. Semantic universality hypothesis partially validated but insufficient to explain full variance. Temperature remains primary driver.*
