# Hobby Block — 2026-09-24

**Time:** 01:00–02:00 BST  
**Focus:** Parameter-archetype analysis — the follow-up to null-model rejection  
**Tool:** `worker/parameter_archetype_analysis.py` (new)

## Objective

The null-model test (Sep 23) rejected the gravity-well hypothesis: seed semantics do not constrain dream archetypes. The natural next question: do generative PARAMETERS constrain archetypes? If neither seed nor parameters matter, dreams are fully emergent. If parameters matter, we have a "kinetic bias" model.

## What Was Built

`parameter_archetype_analysis.py` tests whether temperature, era_jump_prob, or actual jump count predict dream archetype. Uses 196 classified dreams (200 total minus 4 unclassifiable). Parameters were uniformly random (batch_generate used `random.uniform(0.8, 2.0)` for temp, `random.uniform(0.02, 0.12)` for jump_prob), so no seed-parameter confound.

## Results

### Temperature-Archetype Association

| Dataset | N | Cramer's V | Interpretation |
|---------|---|------------|----------------|
| ALL classified | 196 | 0.239 | Small association |
| HIGH+MED confidence | 78 | **0.390** | **Medium association** |

Filtering to high-confidence dreams strengthens the association. Low-confidence classifications add noise that masks the parameter signal.

### Jump-Probability Association

| Dataset | N | Cramer's V | Interpretation |
|---------|---|------------|----------------|
| ALL classified | 196 | 0.242 | Small association |
| HIGH+MED confidence | 78 | **0.343** | **Medium association** |

Similar pattern to temperature.

### Temperature Gradient (HIGH+MED confidence)

Sorted by mean temperature:

| Archetype | Mean Temp | N | Character |
|-----------|-----------|---|-----------|
| power_personal | 1.95 | 1 | Individual agency |
| craft | 1.80 | 1 | Making/creating |
| religious_devotion | 1.50 | 2 | Spiritual practice |
| religious_moral | 1.48 | 9 | Ethical/religious judgment |
| abstract | 1.47 | 9 | Conceptual/non-concrete |
| power_divine | 1.47 | 8 | Sacred authority |
| conflict | 1.42 | 10 | Struggle/contestation |
| power_political | 1.40 | 4 | Secular authority |
| ... | | | |
| urban | 1.23 | 6 | City/material life |
| legacy | 1.18 | 6 | Inheritance/tradition |
| commerce | 1.14 | 4 | Trade/economy |
| temporal | 1.06 | 4 | Time/history |
| bodily | 1.00 | 1 | Physical/sensory |

**Pattern:** High-temperature dreams skew toward abstract, religious, and power archetypes. Low-temperature dreams skew toward concrete, grounded, material archetypes (urban, legacy, commerce, temporal, bodily).

**Key correction:** The `bodily` archetype's high mean temp (1.51) in ALL data was driven entirely by low-confidence classifications. In HIGH+MED, bodily drops to 1.00 — confirming the bodily-penalty finding (Sep 21) that bodily is noise, not signal.

### Predictive Power

A naïve leave-one-seed-out classifier (predict archetype whose mean temp is closest to the dream's temp) achieves:
- ALL: 3.6% accuracy (chance: 5.3%)
- HIGH+MED: 3.8% accuracy (chance: 5.9%)

**Worse than chance.** Temperature biases the distribution but cannot predict individual dreams.

### Wild vs Tame Dreams

- **Wild** (temp > 1.4, jump_prob > 0.08): Distributed across 13 archetypes. No dominant archetype. Maximum diversity.
- **Tame** (temp < 1.0, jump_prob < 0.05): Only 9 dreams (ALL) or 1 dream (HIGH+MED). Too few for conclusions, but they cluster in fewer archetypes.

## Interpretation: The Kinetic Bias Model

The gravity-well model (seed semantics constrain archetypes) is **rejected**.

The kinetic bias model (parameters bias but do not determine archetypes) is **supported**:

1. **Parameters create probability landscapes, not destinies.** Higher temperature increases the probability of abstract/religious/power archetypes but does not guarantee them. Any archetype is possible at any temperature.

2. **Confidence matters.** The parameter signal is masked in low-confidence classifications. When the classifier is confident (HIGH/MEDIUM), the parameter-archetype association strengthens from small to medium. This suggests parameters interact with genuine semantic structure — the walk's dynamics matter more when the landscape is clear.

3. **Dreams are genuinely emergent.** Neither seed semantics nor parameters can predict individual dream archetypes above chance. The walk's stochastic dynamics + semantic landscape produce outcomes that are biased but not determined.

4. **Temperature as semantic altitude.** Low temperature = walk stays near seed, producing concrete/material archetypes. High temperature = walk escapes to distant regions, producing abstract/conceptual archetypes. This is a spatial metaphor: temperature controls how far the walk travels, and distance from origin correlates with abstraction.

## Why This Matters

1. **Theoretical:** Dreams are not echoes of seeds (gravity-well rejected) and not simple parameter readouts (predictive power negligible). They are emergent from the interaction of stochastic dynamics and semantic topology.

2. **Practical:** The dream engine is doing something genuinely generative. You cannot predict what you'll get, but you can bias the probability landscape.

3. **Methodological:** The finding that confidence filtering strengthens the parameter signal suggests a general principle: when analyzing generative output, filter noise first to reveal structural patterns.

## Next Steps

1. Test interaction effects: temp × jump_prob × seed drift score. Does the parameter bias vary by seed drift?
2. Build a proper multinomial model (logistic regression or random forest) to quantify marginal effects.
3. Visualize the parameter landscape: 2D heatmap of temp × jump_prob colored by archetype distribution.
4. Update paper draft with null-model rejection + kinetic bias model.

## Files Changed

- `worker/parameter_archetype_analysis.py` — new
