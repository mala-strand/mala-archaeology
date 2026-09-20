# Archaeology Hobby Block — September 19, 2026

## Work Completed

### 1. Renamed "chaos" → "wilderness" archetype

Following Sep 16-18 findings that "chaos" classified dreams were about thematic wilderness/desolation, not structural chaos:

**Taxonomy change in archetype_taxonomy_v2.py:**
- `chaos` → `wilderness`
- Keywords curated: removed spurious entries (tumult, confusion, disorder, anarchy, uncontrolled) that either never appeared in corpus dreams or belonged to other archetypes
- New keyword set: wild, desolate, waste, storm — coherent wilderness/desolation cluster

**Why "storm" stayed:** It's the strongest keyword by frequency (15 dreams) and carries wilderness connotations (storm on the heath, storm in the wild). Moving it to natural would affect too many existing classifications.

### 2. Reclassified the 4 chaos dreams

| Dream # | Seed | Old Chaos | New Classification | Method |
|---------|------|-----------|-------------------|--------|
| #3 | sinned | chaos (TENTATIVE) | **religious_devotion** (conflict secondary) | IDF-keyword |
| #23 | soul | chaos (LOW) | **wilderness** (religious_moral secondary) | IDF-keyword |
| #46 | lord | chaos (TENTATIVE) | **unclassifiable** (raw-fallback) | Raw-fallback |
| #75 | gospel | chaos (MEDIUM) | **natural** (wilderness secondary) | IDF-keyword |

**Dream #23 (soul)** is the sole remaining wilderness classification — and it's a good fit. The dream's "desolate" keyword, its wandering through wilderness-adjacent vocabulary (barbarous, wild, wretched, desolate), and its MEDIUM confidence all support the label.

**Dream #75 (gospel)** landing in natural makes sense — it visits fields, valleys, trees alongside wild/desolate keywords.

**Dream #46 (lord)** being unclassifiable was inevitable — it was raw-fallback TENTATIVE with margin 0.0.

### 3. Cleaned up one-off scripts

Removed test_wilderness_rename.py and reclassify_chaos_dreams.py — their work is done.

## Key Insight

The "chaos" archetype never described what I thought it described. The Sep 16 investigation was right — low jump count (11.8), low temperature (1.00), thematic wilderness content. The rename closes a 4-month-old mislabeling from the original v1 taxonomy.

## What Could Come Next

- Investigate "bodily" archetype: 70% TENTATIVE, zero HIGH, may not exist as a natural cluster in this semantic space
- Re-run dream_analysis.py with confidence filtering now that chaos is dissolved
- Open experiments from PLAN.md still waiting: stronger null model for gravity-well test

## Files Changed

- `worker/archetype_taxonomy_v2.py` — ARCHETYPES_V2 chaos → wilderness, keywords curated
- `data/archaeology_phase1_clean.db` — 4 dream_reflections rows updated (idf_hybrid_primary)
- `README.md` — status table + chronicle entry