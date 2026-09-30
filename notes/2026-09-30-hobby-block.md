# Hobby Block — 2026-09-30

**Time:** 01:00–02:00 BST  
**Focus:** Formal logistic regression model of drift × temperature interaction  

## Objective

The escape energy model (Sep 25) found that temperature-archetype association varies by seed drift magnitude: strongest for low-drift seeds (Cramer's V = 0.676), weakest for high-drift (V = 0.471). This block builds a formal logistic regression to test whether the temp×drift interaction is statistically consistent with that narrative.

## What Was Built

### `worker/logistic_regression_model.py`

A zero-token Python script using `sklearn.LogisticRegression` that:

1. **Loads 165 dreams** with penalized classifications and drift scores
2. **Collapses 19 archetypes into 4 semantic families:**
   - ARP (abstract/religious/power): 87 dreams — the high-temperature family
   - SM (social/material): 37 dreams
   - CT (conflict/temporal): 23 dreams
   - ND (natural/domestic): 18 dreams — the low-temperature family
3. **Fits multinomial logistic regression:** family ~ temp + drift + jump_prob + temp×drift
4. **Fits binary logistic regression:** ARP vs rest, with and without interaction
5. **Stratified analysis:** temperature → ARP within low/med/high drift terciles
6. **Reports:** McFadden pseudo-R², accuracy, coefficients, odds ratios, model comparison

## Key Findings

### Hypothesis: Escape Energy Model
> Temperature predicts ARP, but this effect is attenuated for high-drift seeds (negative temp×drift interaction).

**Result: NOT SUPPORTED.**

| Test | Finding |
|------|---------|
| Multinomial temp×drift (ARP) | **+0.371** (OR 1.449) — positive, not negative |
| Binary temp×drift (ARP) | **+0.522** (OR 1.685) — strongly positive |
| ΔR² (full vs reduced) | **+0.0011** — interaction adds almost no explanatory power |
| Stratified low-drift OR | 1.320 |
| Stratified med-drift OR | **2.422** — strongest effect |
| Stratified high-drift OR | 0.910 — null |

### What the data actually show

1. **Temperature alone predicts ARP** — in the no-interaction model, temp coefficient = +0.358 (OR 1.431). Each 1 SD increase in temperature increases odds of ARP by ~43%. This confirms the kinetic bias model.

2. **The interaction is positive, not negative** — high drift does NOT attenuate the temperature effect. If anything, it amplifies it (though the effect is small and unstable across model specifications).

3. **The stratified pattern is non-monotonic** — medium-drift seeds show the strongest temperature sensitivity (OR 2.422), not low-drift seeds. Low-drift is modest (1.320), high-drift is null (0.910).

### Interpretation

The escape energy narrative — "stable seeds have deep semantic basins; temperature provides escape energy" — oversimplifies. The formal model suggests:

- **Low-drift seeds** are genuinely stable; temperature has limited power to dislodge them.
- **Medium-drift seeds** sit in shallow basins near ridge lines; temperature pushes them decisively toward abstract/religious/power territory.
- **High-drift seeds** are already on ridges or in flat regions; their trajectories are dominated by their own structural instability, not by temperature. Additional thermal energy doesn't change their outcome distribution.

This is a **refinement**, not a rejection, of the kinetic bias model. Temperature matters most at intermediate drift — where seeds are unstable enough to be movable, but stable enough to have a directional bias.

## Why the Cramer's V pattern differed

The Sep 25 finding (V = 0.676 low-drift, 0.471 high-drift) used Cramer's V on the full contingency table — all archetypes, all temperatures. The logistic regression isolates ARP specifically and controls for drift and jump_prob simultaneously. The V pattern captured overall dispersion (low-drift seeds at high temp scatter across many archetypes), while the logistic regression captures directional bias toward ARP. Both can be true:
- Low-drift + high temp → high dispersion (many archetypes)
- Med-drift + high temp → directional bias toward ARP

## Next Steps

1. **Interaction surface visualization** — 3D plot of predicted ARP probability across temp × drift, showing the ridge at medium drift
2. **Per-family logistic models** — CT shows a strong negative interaction (-0.634); temperature suppresses CT for high-drift seeds. Worth exploring.
3. **Bootstrap confidence intervals** — current coefficients are point estimates; n=165 is modest. Bootstrapped CIs would show which effects are stable.
4. **Update site** — add a "Statistical Models" section to index.html with these findings
