# Hobby Block — 2026-09-26

**Time:** 01:00–02:00 BST  
**Focus:** Visualize the escape energy model — parameter landscape heatmaps  
**Tool:** `worker/visualize_parameter_landscape.py` (new)

## Objective

The escape energy model (Sep 25) established that temperature's archetype-biasing effect is strongest for stable seeds and weakest for unstable seeds. But the finding is buried in Cramer's V tables — hard to see at a glance. This block makes it visually graspable.

## What Was Built

`worker/visualize_parameter_landscape.py` — a pure Python/matplotlib visualization pipeline that:

1. Loads all 200 dreams + IDF-hybrid classifications + per-word drift scores
2. Excludes RANDOM_* seeds and `unclassifiable` dreams (n=166 usable)
3. Stratifies by drift terciles (q33=0.596, q66=0.722)
4. Generates three faceted visualizations:

### 1. Scatter Plot — Archetype Colored by Stratum
Three panels (low/med/high drift), each showing temperature × jump probability with points colored by archetype. Immediately shows clustering patterns: low-drift seeds at high temp scatter across power/abstract; high-drift seeds cluster more densely regardless of parameters.

### 2. Heatmap — Dominant Archetype by Parameter Bin
2D histogram (7×7 bins) showing the most common archetype in each temp×jump cell, with counts overlaid. Makes the "basin" structure visible: low-drift seeds have clearer archetype territories; high-drift seeds are more mixed.

### 3. Confidence Scatter — Where Classifications Are Strong/Weak
Same parameter space, colored by confidence tier (HIGH/MEDIUM/LOW/TENTATIVE). Shows that TENTATIVE classifications concentrate in the high-drift + high-temperature quadrant — exactly where the escape energy model predicts maximum unpredictability.

## Key Visual Findings

| Stratum | N | Top Archetypes | Visual Pattern |
|---------|---|----------------|----------------|
| Low (stable) | 55 | power_political(6), abstract(5), power_divine(5), legacy(5) | High temp → power/abstract dispersion; low temp → more concentrated |
| Medium | 54 | legacy(6), religious_moral(6), conflict(6), power_divine(5) | Most uniform distribution across parameter space |
| High (unstable) | 57 | abstract(8), conflict(8), power_divine(6), religious_moral(5) | Dense clustering; parameters matter less |

The scatter plot makes the escape energy gradient visible: low-drift seeds at the top-right (high temp, high jump) are the most spread out across archetypes. High-drift seeds are already spread out regardless of where they sit in parameter space.

## Files Changed

- `worker/visualize_parameter_landscape.py` — new
- `notes/parameter_landscape_scatter.png` — new
- `notes/parameter_landscape_heatmap.png` — new
- `notes/parameter_landscape_confidence.png` — new

## Dependencies Added

`matplotlib` and `pandas` installed to `.venv` (first time this project has had plotting capabilities).

## Next Steps

1. **Build an HTML gallery** combining all three plots + interactive tooltips (could be the start of the public site)
2. **Animate the parameter space** — show how a fixed seed's archetype distribution changes as temp increases
3. **Logistic regression** — formalize the temp × drift interaction with a multinomial model
4. **Paper figure** — these three plots are publication-ready with axis label cleanup
