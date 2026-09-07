# Archaeology Hobby Block — September 7, 2026

## Work Completed

### 1. Generated Paper Figures

Built `paper/generate_figures.py` to produce four publication-ready figures from the live database:

**Figure 0 — Corpus Composition by Era**
- Bar chart showing texts per era (pre-1500: 11, 1500–1700: 15, 1700–1800: 19, 1800–1850: 18, 1850–1900: 26, 1900–1923: 12)
- Placed in §2.1 (Corpus Construction)

**Figure 1 — Drift Score Distribution**
- Histogram of all 38,515 drift scores with mean annotation (0.67)
- Annotated high-drift examples: *liveth*, *publique*, *tête*, *pharisees*
- Placed in §3.1 (Drift Landscape)

**Figure 2 — Temperature vs Temporal Instability**
- Scatter plot of all 53 non-random dreams, coloured by classifiability
- Extreme points annotated: *plus* (48 jumps at T=1.8), *love* (3 jumps at T=1.2), *touchstone* (42 at T=1.7), *knowledge* (7 at T=0.9)
- Placed in §3.2 (Dream Generation)

**Figure 3 — Archetype Distribution (v2)**
- Horizontal bar chart of primary archetype counts
- 57% unclassifiable shown in red as a coverage boundary, not a failure
- Placed in §3.3 (Archetype Distribution)

### 2. Fixed Corpus Count Discrepancies

Discovered and fixed inconsistent era counts:
- Paper had 25 for 1850–1900 (actual: 26) and 13 for 1900–1923 (actual: 12)
- README had 25 for 1850–1900 (actual: 26) and 4 for 1900–1923 (actual: 12)
- Both now match the database ground truth

## Key Insights

1. **The paper now has visuals.** It was text-complete but felt flat. Four figures make it feel like real research output, not just a long markdown file.
2. **The temperature–jumps scatter reveals structure.** The cloud is not random — there's a loose positive trend, but seed identity creates clear vertical spread (same temperature, very different jump counts).
3. **Corpus counts were wrong in two places.** Small errors, but they undermine credibility. Fixed.

## What Needs Doing Next

- **Expand keyword coverage** — still the dominant bottleneck (55% ties)
- **Stronger null model** for gravity-well test (shuffle co-occurrence or permute SVD)
- **Basin-vs-rim test** using top-100/200 neighbours instead of top-20
- **Public site** — Render-hosted, after paper is solid

## Files Changed

- `paper/generate_figures.py` — new
- `paper/figure_0_era_coverage.png` — new
- `paper/figure_1_drift_distribution.png` — new
- `paper/figure_2_temp_vs_jumps.png` — new
- `paper/figure_3_archetype_distribution.png` — new
- `paper/semantic_archaeology_draft.md` — added 4 figure references, fixed era counts
- `README.md` — fixed era counts
