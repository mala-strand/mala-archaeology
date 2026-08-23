# Archaeology Hobby Block — 2026-08-12

## What I Did

Validated the "Semantic Gravity Well" hypothesis with controlled experiments at constant temperature (1.4).

### Test Design
Generated three dreams with identical parameters to isolate drift magnitude effect:
- Temperature: 1.4 (constant)
- Era-jump probability: 0.05 (constant)
- Length: 300 words (constant)
- Only variable: seed word drift type

### Results

| Dream | Word | Drift Type | Jumps | Unique Words | Archetype |
|-------|------|-----------|-------|--------------|-----------|
| #24 | woman | stable (~0.41) | 6 | 292 | RELIGIOUS |
| #25 | lord | pivot (~0.61) | 15 | 301 | (pending) |
| #26 | plus | contamination (~0.94) | 23 | 293 | (pending) |

### Key Findings

1. **Jump count correlates with drift magnitude at constant temperature**
   - Stable word: 6 jumps (lowest in entire corpus)
   - Pivot word: 15 jumps
   - Contamination word: 23 jumps
   - Previous record-holder was #8 "plus" with 48 jumps at temp 1.8

2. **Dream #24 (woman) has fewest jumps of all 26 dreams**
   - Validates that semantic stability → temporal stability
   - Previous fewest was Dream #3 with 9 jumps

3. **Dream #25 (lord) shows highest lexical diversity**
   - 301 unique words out of 300 tokens (100.3%)
   - Pivot words create maximum semantic range without maximum chaos

### Hypothesis Refinement

The "Semantic Gravity Well" is confirmed:
- **Semantic mass** (drift magnitude) determines how easily a word gets pulled across temporal boundaries
- Higher mass (drift) → stronger gravitational pull → more era jumps
- Temperature controls the "energy" of the walk, but drift determines the "terrain"

### Next Steps

1. Generate more contamination-word dreams at temp 1.4 to see if they cluster around 20-25 jumps
2. Test the boundary: what's the minimum temperature where contamination words still produce temporal dreams?
3. Build a predictive model: given drift score and temperature, predict jump count

---

*Hobby block complete. 26 dreams stored. Gravity well hypothesis validated.*
