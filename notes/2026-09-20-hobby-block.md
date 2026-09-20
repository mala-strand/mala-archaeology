# Archaeology Hobby Block — September 20, 2026

## Investigation: "Bodily" Archetype — Structural Artifact Analysis

### The Question

From Sep 19: "Investigate 'bodily' archetype: 70% TENTATIVE, zero HIGH, may not exist as a natural cluster."

Bodily has 10/200 dreams (5% of corpus). Zero HIGH confidence. 70% TENTATIVE. Only 1 MEDIUM.

### The Finding

**The bodily archetype is a structural artifact of common vocabulary, not a meaningful semantic cluster.**

**Root cause:** Bodily keywords are among the most ubiquitous words in the 101-book corpus:

| Keyword | IDF | Docs (of 101) | Distinctiveness |
|---------|-----|---------------|-----------------|
| arm | 0.010 | 100 | Essentially universal |
| hand | 0.051 | 96 | 95% of texts |
| face, head | 0.083 | 93 | 92% of texts |
| eye | 0.104 | 91 | 90% of texts |
| body, heart, foot, touch | 0.115-0.138 | 88-90 | ~88% of texts |
| bones | 0.538 | 59 | Most distinctive (still low) |

Compare to truly distinctive keywords: bureaucracy (idf=4.615, df=1), cosmic (idf=3.006, df=2), equation (idf=2.669, df=3).

**The mechanism:** Because body words appear in nearly every English text, they naturally appear in nearly every dream. The classifier counts these "free" hits and the bodily archetype accumulates a constant baseline score. Many of these dreams are actually about something else (conflict, knowledge, abstract, etc.) but bodily edges them out by a razor-thin margin due to noise-level keyword presence:

| Dream | Bodily score | Runner-up | Margin |
|-------|-------------|-----------|--------|
| #196 "othello" | 0.408 | religious_cosmic 0.396 | **0.012** |
| #72 "creating" | 0.363 | natural 0.352 | **0.011** |
| #172 "deep" | 0.675 | abstract 0.664 | **0.011** |
| #170 "variety" | 0.625 | power_personal 0.608 | **0.017** |
| #110 "honey" | 0.490 | conflict 0.425, natural 0.425 | **0.065** |

All margins are below the confidence threshold. 4 of 10 bodily dreams are in the bottom-20 lowest-margin dreams overall (20% of weakest dreams vs 5% of corpus — 4× overrepresentation).

### What This Means

The bodily archetype doesn't describe a coherent thematic category. It's a **vocabulary-frequency artifact**. Dreams aren't "about" bodies — they happen to contain universal English words that the classifier counts.

**Options for addressing this:**
1. **Downweight bodily keywords** — Multiply all bodily IDF scores by a penalty factor (e.g., 0.3). Reduces the baseline.
2. **Remove bodily from Tier 1** — Treat it as a non-archetype that only gets assigned when there's *no* other signal (last-resort fallback after unclassifiable).
3. **Merge bodily into a broader category** — Not clear what that would be; body words are too generic.
4. **Keep bodily but mark it as structural** — Document that bodily=TENTATIVE means "no actual body-themed content, just common vocabulary."

**Recommendation:** Option 1 (IDF penalty). Since bodily keywords are 15-45× less distinctive than the most distinctive keywords, and their IDF values (0.01-0.54) are 5-20× lower than the average keyword (most are 0.1-1.5), an aggressive IDF penalty of 0.2-0.3 would bring bodily scores in line with their actual discriminative power. This would likely redistribute most bodily dreams to their secondary archetype — which is probably the correct one.

### What I'd Do Next Block

1. Implement `bodily_penalty` parameter in keyword_idf_scorer.py (multiply bodily IDF scores by 0.25)
2. Run classification comparison: baseline vs penalized
3. Report:
   - How many bodily dreams flip
   - What they flip to (are the new classifications more plausible?)
   - Whether any other archetypes gain suspiciously many new dreams
4. If results are good, backfill idf_hybrid_primary for affected dreams

### Files Changed (this block)

- Created `notes/2026-09-20-hobby-block.md` — this investigation note