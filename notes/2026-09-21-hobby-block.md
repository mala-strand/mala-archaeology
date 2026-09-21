# Archaeology Hobby Block — September 21, 2026

## Work: Bodily Penalty Plausibility Analysis

The IDF penalty (×0.25) for bodily keywords was backfilled on Sep 20. This block I read all 10 dreams previously classified as "bodily" and assessed whether their new classifications are more plausible.

### Results

| Dream | Seed | Old | New | Confidence | Verdict |
|-------|------|-----|-----|------------|---------|
| #29 | man | bodily | **power_divine** | MEDIUM | ✅ Much better — full of conquest, cathedral, apollo, execution, dominion |
| #61 | machine | bodily | natural | LOW | ↔ Neutral — mixed dream, natural no worse than bodily |
| #72 | creating | bodily | natural | TENTATIVE | ↔ No improvement — extremely chaotic, basically unclassifiable |
| #90 | stepped | bodily | **conflict** | TENTATIVE | ✅ Better — prisoners, rage, wars, fight, axe, enemy, terror |
| #104 | impressions | bodily | **religious_cosmic** | LOW | ✅ Much better — thunder, christ, saviour, pharisees, sacrifices, bible |
| #110 | honey | bodily | bodily | TENTATIVE | ↔ Stayed bodily — sensory/physical theme is actually present, but still weak |
| #137 | cool | bodily | knowledge | TENTATIVE | ↔ Neutral — fragmented dream with 35+ jumps, nothing fits well |
| #170 | variety | bodily | **power_personal** | TENTATIVE | ✅ Better — arms, council, wounded, sovereign, conquer, punishments, justice |
| #172 | deep | bodily | **abstract** | TENTATIVE | ✅ Better — estimation, conclusions, consciousness, deliberation, conceptions, sphere |
| #196 | othello | bodily | **religious_cosmic** | TENTATIVE | ✅ Much better — judgements, commandments, wickedness, flames, fate, ghost, christian |

**Score: 6 clear improvements, 3 neutral, 1 unchanged.**

### What This Means

The penalty works. Dreams that were incorrectly pushed into "bodily" by ubiquitous vocabulary (hand, eye, face, etc.) now fall into categories that match their actual thematic content. The 3 neutral cases are all TENTATIVE-confidence dreams where no archetype dominates — the penalty doesn't create false signal, it just removes false noise.

Dream #110 (honey) is interesting: it stayed bodily even with the penalty. Reading it closely, the physical/sensory vocabulary is genuinely dominant: tasted, groans, leap, waking, breathing, corpse, naked, eyes, climbed, grave, sighs, breath. This suggests the archetype *can* be valid when there's actual body-themed content, not just incidental body-word noise.

### No DB Changes This Block

Analysis only. The penalized classifications are already in the DB. This note is the record.

### What I'd Do Next Block

1. **Corpus expansion to 300+ books** — The archetype system is now robust (IDF-hybrid + confidence tiers + bodily penalty). More books = more distinctive keywords = better classifications.
2. **Gravity well null model** — Still open from PLAN.md. Build a proper statistical null by shuffling co-occurrence matrices.
3. **Generate a few wild dreams** — High temp, high jump prob, see what emerges.
