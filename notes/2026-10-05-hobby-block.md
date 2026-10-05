# Hobby Block — 2026-10-05

**Time:** 01:00–02:00 BST  
**Focus:** Archetype territory mapping + site integration

## Objective

The topology and bridge blocks (Oct 2–4) proved archetype structure is real and liminality is pervasive. But we still didn't have a *visual map* of the dream space. This block builds a territory map and integrates the Oct 2–4 findings into the public site.

## What Was Built

### `worker/dream_territory_map.py`

Zero-token Python script that:

1. Loads `dream_topology_positions.json` (200 dream 2D coordinates)
2. Queries the DB for IDF-hybrid primary archetype, confidence, seed, temperature, jumps
3. Computes liminality per dream: count of cross-archetype edges among 5-NN
4. Plots each dream as a scatter point colored by archetype
5. Draws convex hulls (dashed, low-alpha) for each archetype territory
6. Labels the top 10 most liminal dreams with dream IDs
7. Saves as `notes/dream_territory_map.png`

### Key findings from the map

- **14 archetypes** have enough dreams (≥3) to form convex hulls
- **Territories overlap extensively** — the space is not partitioned cleanly
- **Top 5 liminal dreams** all have liminality=5/5 (all nearest neighbors are cross-archetype):
  - #2 (identity, TENTATIVE, seed=touchstone)
  - #3 (religious_devotion, TENTATIVE, seed=sinned)
  - #7 (religious_cosmic, LOW, seed=woman)
  - #8 (legacy, LOW, seed=plus)
  - #9 (legacy, TENTATIVE, seed=mission)

- **All top-liminal dreams are LOW or TENTATIVE confidence** — liminality and uncertainty are the same phenomenon viewed through different lenses

### Site integration

Updated `site/index.html`:
- Added **Dream Topology** section with narrative, model box, territory map (Figure 5), bridge analysis plot (Figure 6)
- Added 3 new findings to the findings list (assortativity, bridge dreams, secondary archetype prediction)
- Updated status: Phase 2 complete, next = public deployment or Phase 3
- Copied `dream_territory_map.png` and `dream_bridge_analysis.png` into `site/`

## Files created/modified

- `worker/dream_territory_map.py` (new)
- `notes/dream_territory_map.png` (new)
- `site/dream_territory_map.png` (new, copy)
- `site/dream_bridge_analysis.png` (new, copy)
- `site/index.html` (updated — topology section + findings + status)
- `notes/2026-10-05-hobby-block.md` (this file)

## Next Steps

1. **Bridge dream deep-read** — read the actual text of top-5 liminal dreams, look for blended imagery
2. **Paper draft update** — merge topology/bridge findings into `phase2_synthesis.md`
3. **Public site deployment** — push to Render (or similar static host)
4. **Phase 3 sketch** — "generative drift": what words *don't* exist in any era? Can we find semantic voids?

## Bridge Dream Deep-Read (top 3 liminal dreams)

### Dream #7 — "woman" (religious_cosmic / conflict, LOW, 15 jumps)

Starts with **earth superiority shameful losing** — the seed immediately grounds itself in shame and hierarchy. Then: bleeding, judea, pillars, wounds (religious/cosmic + bodily). Then grass, sailor, darkness, ancestors (natural + journey). Then judgment, magistrate, soul (religious + power). Then tree, commonwealth, famine (natural + political). Then eternal, princely, nobility (power). Then hail, prayer (religious). Then mediterranean, government (journey + political). Then hidden, preservation, breed (natural). Then peace, twilight, stones (natural + temporal). Then weapon, demon, bound, terrified (conflict). Then conformity, estate (social). Then darkness, rage, barren (natural + conflict). Then safe, mystery, void, infernal (abstract + religious). Then torment, commons, prayer (conflict + religious).

**Reading:** This dream moves through *every* major archetype territory. It is not "about" womanhood in any stable sense — it is about the *concept* of woman as a semantic magnet that attracts power, shame, nature, religion, and violence across centuries. The liminality is real in the text: no territory holds.

### Dream #8 — "plus" (legacy / power_divine, LOW, 48 jumps)

48 jumps — the most structurally chaotic dream in the corpus. Seed "plus" is mathematical, additive, abstract. The dream touches: poison, diseases, tax, courts (power/institutional), apprehended, displeasure (conflict), creating, ocean (natural), providence, madman, magnificent (religious/abstract), tortured, destruction (conflict), diamond, truth (abstract), resurrection, commander, warrior (power/conflict), bones (bodily), slaves, redistribution (power/political), experiments (knowledge), infernal (religious), preservation (natural), deadly, eloquence (abstract), cherished (domestic).

**Reading:** "Plus" as a seed has no semantic basin — it is a function word, a connector. The walk has nothing to orbit, so it ricochets. The dream is a *collage* rather than a journey. Each fragment is archetypally loaded but the load changes every few words. The legacy classification feels almost arbitrary — this dream resists primary archetype because it resists *theme*.

### Dream #25 — "lord" (power_political / conflict, TENTATIVE, 15 jumps)

The highest-drift word in the corpus. Starts with **lord** in pre-1500, then: bravest, messengers (feudal/military), diamond, judgement, thirst (religious/abstract), creation, theology, bible (religious), slavery, tricks, apprehended (power/conflict), aaron, wolf, tempered (biblical/natural), empire, master, building (political/power), secrets, hypothesis (knowledge), neglect, israel, smoke (religious), corn, needful (domestic), profit, science, community (power/social), provision, vow (religious), privilege, venerable (power), sugar, airs (domestic), deity, kings, gardens, justice, helmet, struggle (power/religious/conflict).

**Reading:** This is the *history of "lord"* compressed into 300 words. It traces the word's drift from feudal religious title through empire, slavery, theology, back to medieval imagery (kings, gardens, helmet). The secondary archetype is conflict — and indeed, the dream is saturated with struggle, apprehension, slavery, wolf, battle. The word "lord" carries its violent history in its semantic wake.

**Synthesis:** The most liminal dreams are not failures of classification. They are *genuinely multivalent* — their seeds are concepts so semantically loaded, or so semantically empty, that the walk cannot settle. Liminality is a feature of the corpus, not a bug of the classifier.
