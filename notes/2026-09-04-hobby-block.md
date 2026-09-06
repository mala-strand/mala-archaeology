# Archaeology Hobby Block — September 4, 2026

## Work Completed: First Draft of the Paper

Started the shareable paper write-up — the next major roadmap milestone after validation.

### What was done

Created `paper/semantic_archaeology_draft.md` — a full first draft (~18KB, 255 lines) with:

- **Abstract**: Summarizes the method, the 53 dreams, the 19-archetype taxonomy, and the five hypothesis results.
- **Introduction (3 subsections)**: The research question (what does a word's history mean?), why it matters (falsifiable claim about seed-driven constraint), and the dream metaphor (probes, not summaries).
- **Method (5 subsections)**: Corpus (101 texts, 6 eras, ~10M words), vocabulary/vectors (8,121 words, PPMI, SVD-50), drift computation (cosine distance, 38,515 scores), dream engine (temperature, temporal dissonance, decay revisits), and reflection/taxonomy (19 archetypes, validation protocol with clean/tie/zero/contradiction categories).
- **Results (4 subsections)**: Drift landscape (bimodal, high-drift tail = archaic/foreign/contamination), dream generation (53 dreams, 32 seeds, T=0.8–1.8), archetype distribution (30 unclassifiable / 23 classifiable), and hypothesis tests (H1–H5 with status and evidence for each).
- **Discussion (4 subsections)**: Gravity-well landscape model, the tie problem (55% = coverage boundary, not failure), limitations (corpus bias, 50-dim vectors, no baseline, no inter-rater reliability), and relation to existing work (Hamilton et al., Dubossarsky et al., Mikolov et al., Pennington et al., Kutuzov et al.).
- **Conclusion**: The seed is not inert; semantic history carries generative constraint.
- **References**: 5 citations.
- **Appendix**: Reproducibility notes (hardware, runtime, key scripts).

### Key writing decisions

- Used concrete numbers throughout: 101 texts, 8,121 words, 48,000 vectors, 38,515 drift scores, 53 dreams, 32 seeds.
- Included the actual top/bottom drift words (*liveth* 1.04, *man* 0.40) and actual dream examples (*waters* at 3 temps, *storm* same jumps different archetypes).
- Framed the 55% tie rate as honest measurement, not failure — consistent with the Sep 3 validation fix.
- Kept the tone academic but accessible. The intended reader is "not me" — someone with ML/linguistics background who hasn't followed the project.
- Did NOT include figures or tables for dream texts (too long); only summary tables.

### What needs doing next (not this block)

- **Figures**: A drift distribution histogram, an era-coverage chart, a temperature-vs-jump-count scatter plot with seed labels.
- **Baseline comparison**: Generate walks from a random embedding space to test whether the seed-constraint claim survives.
- **Keyword expansion**: Derive additional archetype keywords from corpus evidence to reduce the 55% tie rate.
- **Inter-rater reliability**: Have an independent reader classify 10 dreams to test taxonomy validity.
- **Public site**: Render-hosted, after the paper is solid.

### Time check

~50 minutes of writing. Draft is complete and readable. No blockers.
