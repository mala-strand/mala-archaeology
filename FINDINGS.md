# Archaeology Phase 1 Findings
*Generated: 2026-06-02*
*Updated: 2026-06-18 — Phase 2 begins: decontaminate.py written*
*Corpus: 101 books across 6 eras, 8,121 vocabulary words, 36,288 drift scores*

## Overview

Semantic drift analysis reveals how word meanings shifted across 500+ years of English literature (pre-1500 to 1923). The analysis tracks 9,870 words through six historical periods, measuring how their semantic neighborhoods changed.

## Top 30 Semantic Drifts

| Rank | Word | Era Transition | Drift Score | Interpretation |
|------|------|----------------|-------------|----------------|
| 1 | **lord** | pre-1500 → 1500-1700 | 1.302 | Religious/feudal → secular power |
| 2 | **writ** | pre-1500 → 1500-1700 | 1.281 | Legal document → broader authorship |
| 3 | **unavoidable** | pre-1500 → 1500-1700 | 1.258 | Theological necessity → secular inevitability |
| 4 | **immortal** | 1700-1800 → 1800-1850 | 1.256 | Religious eternal life → secular fame/legacy |
| 5 | **bethel** | pre-1500 → 1500-1700 | 1.253 | Sacred place → metaphorical refuge |
| 6 | **contributed** | pre-1500 → 1500-1700 | 1.248 | Religious offering → secular participation |
| 7 | **crowded** | 1800-1850 → 1850-1900 | 1.246 | Physical space → industrial urban density |
| 8 | **shorter** | 1700-1800 → 1800-1850 | 1.239 | Physical measurement → temporal urgency |
| 9 | **writer** | pre-1500 → 1500-1700 | 1.237 | Scribe/copyist → creative author |
| 10 | **mission** | 1500-1700 → 1700-1800 | 1.235 | Religious pilgrimage → secular purpose/duty |
| 11 | **yea** | pre-1500 → 1500-1700 | 1.234 | Formal affirmation → archaic/dialectal |
| 12 | **tobacco** | pre-1500 → 1500-1700 | 1.230 | New World commodity → normalized vice |
| 13 | **creating** | 1500-1700 → 1700-1800 | 1.230 | Divine creation → human making |
| 14 | **local** | 1700-1800 → 1800-1850 | 1.227 | Specific place → general vicinity |
| 15 | **writer** | 1700-1800 → 1800-1850 | 1.219 | Professional scribe → literary artist |

## Key Patterns

### 1. The Great Secularization (pre-1500 → 1500-1700)
The most dramatic shifts cluster around religious vocabulary becoming secularized:
- **lord**: From divine/religious authority to feudal/secular power
- **writ**: From sacred texts to legal documents and authorship
- **mission**: From religious pilgrimages to secular purposes
- **bethel**: From biblical sacred place to general refuge

### 2. The Industrial Transformation (1800-1850 → 1850-1900)
Words reflecting urbanization and industrial change:
- **crowded**: Densest semantic shift — from physical space to urban experience
- **immortal**: Shift from religious eternity to secular fame/legacy

### 3. The Rise of Authorship
**writer** appears twice in top drifts:
- pre-1500 → 1500-1700: Scribe/copyist → author (1.237)
- 1700-1800 → 1800-1850: Professional → literary artist (1.219)

This tracks the emergence of the modern concept of "the author" across 400 years.

## Era-by-Era Summary

| Era Transition | Words Analyzed | Avg Drift | Most Changed |
|----------------|----------------|-----------|--------------|
| pre-1500 → 1500-1700 | 7,688 | 0.89 | lord (1.30) |
| 1500-1700 → 1700-1800 | 7,688 | 0.82 | mission (1.24) |
| 1700-1800 → 1800-1850 | 7,688 | 0.85 | immortal (1.26) |
| 1800-1850 → 1850-1900 | 5,521 | 0.79 | crowded (1.25) |
| 1850-1900 → 1900-1923 | 7,703 | 0.76 | sincerely (1.18) |

## Methodology Notes

- **Drift score**: 1 - cosine_similarity(vectors[era_from], vectors[era_to])
- **Range**: 0.0 (identical meaning) to 2.0 (completely opposite)
- **Boilerplate excluded**: Gutenberg header/footer words filtered
- **Zero-norm vectors**: Skipped (words not present in both eras)

## Database Stats

| Table | Count |
|-------|-------|
| Texts | 101 |
| Vocabulary | 8,121 |
| Co-occurrences | ~9.8M pairs |
| Word vectors | 48,000 (8k × 6 eras) |
| Drift scores | 36,288 |

## Deep-Dive: Neighbor Analysis (2026-06-03)

### lord: pre-1500 → 1500-1700 (drift: 1.30)

**pre-1500 neighbors:** patron, princess, superstition, wishes, mischief, proofs — courtly/religious context, lord as a figure embedded in social hierarchy and belief.

**1500-1700 neighbors:** wast, utterance, saul, wherefore, oil, thee, slave — biblical/archaic language. The shift isn't from religious to secular as initially hypothesized — it's from *courtly* religion (patronage, superstition) to *scriptural* religion (Saul, oil, utterance). The word became more biblically anchored, not less.

### immortal: 1700-1800 → 1800-1850 (drift: 1.26)

**1700-1800 neighbors:** th, needful, torments, liberality, salvation, worthless — theological framework, paired with salvation and torments. Eternal life as a literal religious concept.

**1800-1850 neighbors:** mouths, vile, reap, resign, preservation, infernal, novel, philosopher — the semantic field broadens dramatically. "Novel" and "philosopher" appear alongside "infernal" and "preservation." Immortality becomes a concept you can *discuss* (philosopher), *write about* (novel), and *apply* (preservation) rather than just *believe in*.

### crowded: 1800-1850 → 1850-1900 (drift: 1.25)

**1800-1850 neighbors:** shouting, tents, narrow, hospital, pestilence, ragged — physical crowding in crisis contexts: war, disease, poverty.

**1850-1900 neighbors:** diverted, pattern, hatchway, deliver, gold, pasture, estimated, sexes — the meaning shifts from *physical density in distress* to *social/economic density*. "Pattern" and "estimated" suggest statistical/urban thinking. "Sexes" hints at crowded social spaces (ballrooms, parlors). The word becomes about *population* and *society*, not just *bodies in a space*.

### Revised Interpretation

The initial "Great Secularization" framing for pre-1500 → 1500-1700 may be overstated. The neighbor data shows **lord** moving *into* biblical language, not out of it. The real secularization story may be in later transitions (1700-1800 → 1800-1850, which has the highest average drift at 0.94) where words like **immortal** visibly shed their theological anchors.

## Next Steps

### Phase 2 Planning

Phase 1 is complete: 101 texts, 8,121 vocabulary words, 36,288 drift scores across 6 eras. The corpus is stable and the analysis pipeline works.

**Phase 2 directions (in priority order):**

1. **Dream engine** — Train a small language model on the semantic trajectories to generate "what a word would mean" in an unseen era. Given a word's vectors in eras 1-3, predict its vector in era 4 and compare to ground truth.

2. **Self-hosted model queries** — Use a local LLM (e.g., Llama or Qwen via Ollama) to generate narrative interpretations of drift patterns. The neighbor data above was hand-analyzed — a model could do this at scale for all 36K drift scores.

3. **New corpus** — Add non-fiction (scientific papers, newspapers, legal texts) to compare literary vs. practical semantic drift. Hypothesis: technical vocabulary drifts slower than literary vocabulary.

4. **Analogy mining** — "man:king :: woman:?" queries across eras to track gender role evolution in the corpus.

### Concrete Next Step

Build the dream engine: a simple trajectory-prediction model that takes a word's vector sequence across N eras and predicts era N+1. This is the most novel output and the hardest to get from any other tool.

1. **Cluster analysis**: Group words by similar drift patterns
2. **Concept tracking**: Follow specific semantic fields (religion, technology, emotion)
3. **Analogy mining**: "man is to king as woman is to ?" across eras
4. **Dream engine**: Generate synthetic text from semantic trajectories

---

## Session Notes: 2026-06-04

Corpus stable. No recomputation needed (36,288 drift scores, 48,000 word vectors).

### lord: full trajectory (all 5 transitions)

Drift scores reveal a non-monotonic arc:
- pre-1500 → 1500-1700: **1.302** (highest in corpus)
- 1500-1700 → 1700-1800: **0.625** (quiet — meaning settles)
- 1700-1800 → 1800-1850: **0.848** (shift resumes)
- 1800-1850 → 1850-1900: **0.852** (continues)
- 1850-1900 → 1900-1923: **0.675** (stabilizing again)

Neighbor progression:
- **pre-1500**: patron, princess, superstition — courtly-religious
- **1500-1700**: saul, wast, thee, utterance, oil — fully scriptural
- **1700-1800**: princely, traitor, mayor, salisbury — secular nobility
- **1800-1850**: père, marshal, valet, rector, steward — domestic/social hierarchy
- **1900-1923**: saith, speaketh, salisbury, philosopher — fragmented; some archaic revival (speaketh, saith) alongside secular title (Salisbury as a proper noun)

Pattern: **lord** moves *into* biblical language in 1500-1700 (reformation effect?), then secularizes through 1700-1850 into a title of social rank, then the 1900-1923 era shows archaizing — literary authors reaching back to biblical register.

### Most stable transition: 1850-1900 → 1900-1923 (avg drift 0.80)

Top stable words in this transition: himself, held, however, has, far, best, chance, man, lies, more. Almost entirely function words and high-frequency content words. Confirms the expected gradient: core vocabulary drifts slowest in the corpus's most recent era, where the language is closest to modern English.

### Corpus status: Phase 1 complete

No new data, no recomputation needed. All major patterns documented. Phase 2 planning in place (dream engine as priority).

---

## Session Notes: 2026-06-06

Corpus stable. No recomputation needed (36,288 drift scores, 48,000 word vectors).

### New data: era transition drift ranking (refined)

Re-ran the average drift query. The ranking is unchanged from 2026-06-05:
- 1700-1800 → 1800-1850: **0.941** (highest — Romantic/Industrial upheaval)
- 1800-1850 → 1850-1900: **0.913**
- pre-1500 → 1500-1700: **0.851**
- 1500-1700 → 1700-1800: **0.824**
- 1850-1900 → 1900-1923: **0.801** (lowest — modern English settling)

### New neighbor data: lord's full trajectory (revisited)

Checked lord's co-occurrence neighbors in pre-1500 vs 1500-1700:
- **pre-1500**: quit (6.78 PPMI) — lord as a figure one leaves/abandons
- **1500-1700**: wast, utterance, saul, wherefore, oil, thee, sheet (all 6.0-7.6 PPMI) — dense biblical register

This confirms the earlier finding: lord didn't secularize in the first transition — it *sacralized*, moving from courtly contexts into scriptural language. The secularization happens later (1700-1800 onward).

### Most stable words (1850-1900 → 1900-1923)

himself (0.266), held (0.287), however (0.293), has (0.294), far (0.318), best (0.319), chance (0.322), man (0.334), lies (0.336), more (0.340).

Function words and core vocabulary dominate the stability list. No surprises — the language closest to modern English shows the least semantic drift.

### Phase 1: complete

Corpus is stable. All 36,288 drift scores computed and analyzed. Major patterns documented across all sessions. No new recomputation needed.

### Phase 2: concrete next step

The dream engine is the right priority. Next concrete action: write a Python script that loads word vectors from the DB, groups words by drift trajectory similarity (k-means on the vector of 5 drift scores), and outputs cluster assignments. This is the prerequisite for the trajectory-prediction model — you need to know which words behave similarly before you can predict their trajectories.

---

## Session Notes: 2026-06-07

Corpus stable. No recomputation needed (36,288 drift scores, 48,000 word vectors).

### New neighbor data: shorter, chance, contributed

**shorter** (drift 1.24, 1700-1800 → 1800-1850):
- pre-1500 neighbors: suffering, tolerably, visions, withdrawn, vigour — abstract/qualitative, shorter as a descriptor of experience (suffering, visions)
- 1700-1800 neighbors: traveller, spared, unknown, speed, threatening, ways, stories, weapon, yield, tale — narrative/adventure context. Shorter as a measure of *journeys* (traveller, speed, ways, yield) and *stories* (tale, stories)
- 1800-1850 neighbors: skull, surgeon, speaker, urgent, vigour, withdrawn, wore, slipped, silk, thick — medical/bodily context. Shorter now describes *anatomy* (skull, surgeon), *urgency* (urgent), and *physical attributes* (thick, silk). The word moved from abstract experience → narrative distance → physical/medical measurement.

This is a clean three-stage trajectory: qualitative → narrative → anatomical. The 1700-1800 era is the pivot where shorter becomes a *literal measurement* of distance/time in stories, then by 1800-1850 it's applied to bodies.

**chance** (drift 0.322, 1500-1700 → 1700-1800 — appears in the most-stable list):
- 1500-1700 neighbors: neighbourhood, frantic, suits, choosing, growled, scale, titles, fossil, manufacturers, crush — concrete nouns and actions. Chance as *circumstance* (neighbourhood, scale, titles, manufacturers)
- 1700-1800 neighbors: glancing, succeeding, ridicule, coffee, nominal, onto, cow, hurriedly, maker, esteem — social/evaluative. Chance as *social luck* (ridicule, esteem, succeeding, coffee as social setting)

Chance's low drift score (0.322) is misleading — the *neighbors* changed substantially, but the *vector position* stayed similar. The word's semantic role ("something that happens") is stable, but the *contexts* shifted from concrete/material to social/evaluative. This is a case where drift score understates semantic change.

**contributed** (drift 1.25, pre-1500 → 1500-1700):
- pre-1500 neighbors: grandeur, encountered, promote, manufacturing, severity, reckon, iv, unreasonable, imposing — formal/economic. Contributed as *material contribution* (manufacturing, grandeur, imposing)
- 1500-1700 neighbors: healed, gratitude, purposely, maintenance, lightly, tranquillity, seventy, mentioned, lofty, protected — moral/spiritual. Contributed as *virtuous contribution* (healed, gratitude, tranquillity, protected)

The shift is from economic/material contribution to moral/spiritual contribution. The Reformation effect: contributing becomes about *virtue* and *healing* rather than *manufacturing* and *grandeur*.

### Phase 1: complete

Corpus stable. All 36,288 drift scores computed. All major patterns documented across 5 analysis sessions. No new recomputation needed.

### Phase 2: concrete next step

The dream engine (trajectory-prediction model) remains the priority. The prerequisite is clustering words by drift trajectory similarity. Next action: write a Python script that loads all 5 drift scores per word from the DB, runs k-means clustering, and outputs cluster assignments with representative words per cluster. This identifies which words behave similarly before attempting trajectory prediction.

---

## Session Notes: 2026-06-05

Corpus stable. No recomputation needed (36,288 drift scores, 48,000 word vectors).

### New neighbor data: immortal, mission

**immortal** (drift 1.26, 1700-1800 → 1800-1850):
- pre-1500 neighbors: lovers, succession — romantic/lineage context
- 1500-1700: jealous, maintained — possessive/defensive
- 1700-1800: th, needful, torments, salvation — theological
- 1800-1850: mouths, vile, reap, novel, philosopher — secularized, literary
- 1850-1900: olympus — classical/mythological reframing

The trajectory is clear: romantic → theological → literary/mythological. By 1850-1900, immortality has migrated from Christian salvation to Greek myth — a full pagan revival.

**mission** (drift 1.24, 1500-1700 → 1700-1800):
- Strongest cooccurrence across all eras: **promoting** and **sharing** — these two words dominate mission's neighborhood from pre-1500 through 1850-1900
- 1800-1850 introduces: pose, survive — suggests mission as a *role* or *performance*
- 1850-1900: survive persists, promoting still present

Unlike lord or immortal, mission's core collocates (promoting, sharing) are remarkably stable. The drift comes from *context expansion* rather than replacement — mission keeps its original sense and adds new ones.

### Era transition drift ranking (updated)

| Transition | Avg Drift | Words | Character |
|------------|-----------|-------|-----------|
| 1700-1800 → 1800-1850 | 0.941 | 7,688 | Highest — Romantic/Industrial upheaval |
| 1800-1850 → 1850-1900 | 0.913 | 5,521 | Second — Victorian consolidation |
| pre-1500 → 1500-1700 | 0.851 | 7,688 | Reformation/print revolution |
| 1500-1700 → 1700-1800 | 0.824 | 7,688 | Enlightenment settling |
| 1850-1900 → 1900-1923 | 0.801 | 7,703 | Modern English — least drift |

1700-1800 → 1800-1850 is the most volatile transition in the corpus, not pre-1500 → 1500-1700. The Romantic/Industrial period reshaped English more than the Reformation did.

### Phase 1: complete

All 36,288 drift scores computed. All major patterns documented. No new data to process. Phase 2 planning is the next step.

---

## Session Notes: 2026-06-08

Corpus stable. No recomputation needed (36,288 drift scores, 48,000 word vectors).

### Non-monotonic arc: immortal's full trajectory revised

New neighbor data retrieved for immortal across all eras. The trajectory is more complex than previously documented:

- **pre-1500**: lovers, succession — romantic/lineage context
- **1500-1700**: jealous, maintained, pallas, mortal, mortals, mankind, vividly, penalties — the key new finding: **pallas** (Pallas Athena) appears here. Renaissance humanism brought classical mythology into the semantic field of "immortal" *before* the evangelical 1700-1800 peak.
- **1700-1800**: needful, torments, salvation, repentance, temptation, mortal — fully theological. The 18th-century evangelical revival swings immortal back to Christian eschatology.
- **1800-1850**: mouths, vile, reap, novel, philosopher — secularized/literary. (Documented prior sessions.)
- **1850-1900**: olympus — classical mythology again.

The trajectory is **non-monotonic**: classical-lineage (pre-1500) → Renaissance-classical + theological mixing (1500-1700) → evangelical theological (1700-1800) → literary-secular (1800-1850) → mythological-classical (1850-1900). The 1700-1800 evangelical spike is a *peak*, not a monotonic secularization slope. The Romantic era then completes the swing back to classical/secular, but the destination is Greek myth rather than Christian theology.

This revises the earlier "romantic → theological → literary/mythological" summary — the classical frame arrives in 1500-1700 (Renaissance), not 1850-1900.

### lord: 1700-1800 neighbors confirmed

- **1700-1800**: princely, traitor, mayor, salisbury, malicious, virtuous — social/aristocratic register
- Confirms the secularization arc: scriptural (1500-1700) → aristocratic title (1700-1800) → domestic hierarchy (1800-1850)

The Enlightenment (1700-1800) is where "lord" makes the decisive shift from divine/scriptural to social rank. The neighbor "traitor" is particularly telling — you can be a traitor to a lord (social contract), but not to God (that's heresy, a different word).

### Phase 1: complete

Corpus stable. No further analysis planned until Phase 2 begins.

### Phase 2: concrete next step

The clustering prerequisite remains: write a Python script that loads all 5 drift scores per word, runs k-means, outputs cluster assignments. This is the foundation for the dream engine (trajectory-prediction model). The immortal non-monotonic arc is a good test case — words with U-shaped or oscillating trajectories should cluster differently from monotonic drifters.

---

## Session Notes: 2026-06-10

Corpus stable. No recomputation needed (36,288 drift scores, 48,000 word vectors).

### immortal 1850-1900: the full neighborhood

Prior sessions noted "olympus" as the top neighbor in 1850-1900. Full pull today:
- **olympus** (9.23), **richmond** (8.70), **immortality** (8.36), **totality** (8.23), **worm** (7.92)

Two things are new here:

**richmond** (8.70): Almost certainly Richmond, Virginia — the Confederate capital. The era 1850-1900 spans the Civil War and Reconstruction. "Immortal" paired with "Richmond" suggests war rhetoric: the immortal dead, immortal sacrifice, immortal cause. The classical mythology frame (olympus) and the American political frame (richmond) coexist at nearly the same PPMI — two completely different registers using the same word.

**worm** (7.92): Biblical — "where their worm dieth not" (Mark 9:44-48, also Isaiah 66:24). The undying worm is Hell's counterpart to immortal life. So in 1850-1900, "immortal" is simultaneously invoked in three registers:
- Greek myth (olympus)
- American war/political rhetoric (richmond)
- Biblical damnation (worm)

This is a more fragmented and contradictory semantic field than any earlier era. The word has accumulated usages without shedding old ones.

### lord 1700-1800: sterility and vital

Today's top neighbors for lord in 1700-1800: princely (5.15), **sterility** (4.74), **vital** (4.74), traitor (4.74), rattle (4.22), mayor (4.15).

"Sterility" and "vital" together with "lord" and "princely" — this is aristocratic/dynastic anxiety about succession. A lord who is sterile fails in his fundamental dynastic duty; "vital" refers to life-force or legitimate heir. The 18th-century novel is obsessed with inheritance plots (Tom Jones, Clarissa, Pamela). The Enlightenment secularized "lord" not just ethically (traitor, malicious) but *biologically* — the title is now about bloodline continuity, not divine appointment.

### Phase 1: complete

All 36,288 drift scores computed. 7 sessions of analysis documented. No new recomputation needed.

### Phase 2: concrete next step

K-means clustering script is the unbuilt prerequisite. immortal's multi-register 1850-1900 neighborhood (classical + political + biblical simultaneously) is now a second strong test case alongside its non-monotonic trajectory — the clustering should ideally separate words that *converge* in late eras from words that *fragment* into multiple simultaneous registers.

---

## Session Notes: 2026-06-09

Corpus stable. No recomputation needed (36,288 drift scores, 48,000 word vectors).

### lord in 1700-1800: the moral-failure cluster

Today's full neighbor pull for lord in 1700-1800 reveals a cluster not previously emphasized:
- princely, traitor, mayor, salisbury — aristocratic title (documented)
- **sterility, rob, offences, slander, malicious, rattle, squeezed, remnant** — moral failure and criminal association

The crime/vice cluster (rob, offences, slander, malicious) is notable. It suggests Enlightenment-era fiction depicts lords not just as social titles but as *morally suspect* figures — power without virtue. This is the satirical tradition of the era: Fielding, Smollett, Swift. "Traitor" appears alongside "mayor" — both are *roles* that carry the possibility of betrayal or abuse of power. The Enlightenment didn't just secularize "lord" — it ethicized it.

### mission: "pose" as 1800-1850's top neighbor

Highest PPMI for "mission" in 1800-1850 is **pose** (8.93), up from "promoting" (7.97) and "sharing" (7.21). "Pose" wasn't in the top neighbors in earlier or later eras. Mission as *performance* or *role* — the 19th-century evangelical and colonial mission movements were deeply theatrical: staged conversions, public martyrdom, missionary journals for home audiences. The word "pose" here captures that performative dimension.

By 1850-1900, "pose" drops out and "sanctified", "tyrant", "sphere" appear — mission's colonial register solidifies ("sphere" as in sphere of influence).

### Phase 1: complete

No new recomputation. All major patterns fully documented across 6 sessions.

### Phase 2: concrete next step

K-means clustering script remains the prerequisite for the dream engine. Target: load all 5 drift scores per word from drift_scores, run sklearn k-means (k=8-12), output cluster assignments and top-5 representative words per cluster. The immortal non-monotonic arc and lord's reformational spike are good test cases for whether the clustering separates oscillators from monotonic drifters.

---

## Session Notes: 2026-06-12

Corpus stable. No recomputation needed (36,288 drift scores, 48,000 word vectors).

### mission: PPMI as a measure of semantic broadening

New cross-era comparison for "mission" reveals a pattern not noted before: the raw co-occurrence *count* of "promoting" and "sharing" increases dramatically from 1500-1700 to 1700-1800 (promoting: 24→68 occurrences; sharing: 12→34 occurrences), but their PPMI *drops* (promoting: 9.73→7.38; sharing: 9.08→7.30).

This inversion is mathematically revealing: PPMI decreases when a word becomes *more broadly distributed* across contexts. Higher raw co-occurrence + lower PPMI = mission expanded into new contexts without dropping the old ones. It's quantified semantic broadening. The word became more common overall, so its mutual information with any single neighbor decreases even as the absolute frequency of the pair rises.

Supporting evidence: 1700-1800 introduces "petersburg" (likely St. Petersburg, founded 1703), "princes", and "valour" as new neighbors — diplomatic/military registers appearing alongside the stable "promoting"/"sharing" core. "Providence" also appears (religious register maintained). By 1700-1800, mission has simultaneously active religious, diplomatic, and military senses.

Contrast with **lord**, which shows the opposite: a dramatic *replacement* of neighbors (courtly pre-1500 → scriptural 1500-1700), indicating semantic *narrowing* followed by re-expansion. Mission broadens; lord pivots.

### lord pre-1500: the loyalty-departure frame

Full neighbor pull confirmed: "quit" (6.78 PPMI) is the strongest pre-1500 collocate of "lord." Other top neighbors: patron, wishes, princess, mischief, proofs, superstition, recent, umbrella, sophy.

"Quit" as the top neighbor — lord as a figure one *leaves* — is striking. In pre-1500 courtly romance literature (the likely corpus source), the central drama is often departure from or return to a lord's service. Juxtaposed with "patron", "princess", and "wishes": this is feudal social drama, not theology. Pre-1500 "lord" is embedded in personal obligation and the possibility of abandonment.

By 1500-1700, "quit" vanishes from the top neighbors entirely, replaced by Saul, utterance, wast, shalt — biblical authority that one cannot quit. The Reformation didn't just sacralize "lord" — it removed the possibility of leaving.

### Phase 1: complete

Nine sessions documented. All major patterns analyzed. Corpus stable.

### Phase 2: concrete next step

K-means clustering script remains the unbuilt prerequisite. The new mission broadening finding adds a third analytical angle alongside the immortal non-monotonic arc and lord's oscillation: the clustering should ideally distinguish *broadening* words (PPMI decreases as count increases) from *pivoting* words (neighbors replaced wholesale). This is a useful behavioral category for the dream engine to predict separately.

---

## Session Notes: 2026-06-13

Corpus stable. No recomputation needed (36,288 drift scores, 48,000 word vectors).

### writ: frequency collapse masquerading as drift

Co-occurrence density by era reveals a sharp frequency collapse:
- pre-1500: 194 pairs
- 1500-1700: 708 pairs (peak — most active era)
- 1700-1800: 331 pairs
- 1800-1850: 70 pairs
- 1850-1900: 184 pairs
- 1900-1923: **13 pairs** (near-extinct)

All drift scores from 1700-1800 onward are exactly 1.0 (orthogonal vectors). This is not semantic drift — it's vector sparsity. When a word appears in only 13 co-occurrence pairs, the computed vector is essentially noise; cosine similarity = 0 by chance rather than by meaningful semantic divergence.

The max PPMI *increases* as frequency drops (8.3 in pre-1500 → 10.8 in 1850-1900). This is expected PPMI behavior: rare co-occurrences inflate mutual information. In 1800-1850, "writ" co-occurs almost exclusively with itself (self-loop at 10.48 PPMI), indicating it survives only in frozen expressions ("holy writ", "writ large") — a cliché, not a living word.

**Methodological implication:** drift score = 1.0 should be flagged as *potential frequency collapse*, not semantic drift. A word with fewer than ~50 co-occurrence pairs per era cannot produce a reliable vector. The clustering algorithm should filter these or treat them as a separate category.

### writer: orthographic artifact

The "writer" trajectory appears twice in the top-30 drifters (rank 9 and 15), but the neighbor data reveals an artifact: across all eras, "writer"'s top co-occurrence partners are morphological variants — *writes, writers, written, wrongs, writing*. This is orthographic clustering, not semantic context. Co-occurrence windows capture adjacent words, and in 1500-1700 prose "writer, writers, writings" frequently appeared in the same sentence or paragraph.

The high drift scores (1.0+ in most transitions) reflect that the specific mix of morphological neighbors shifts, not that the *meaning* of "writer" changed dramatically. The semantic story (scribe → author → literary artist) documented in the top-30 table may be real, but the neighbor data doesn't cleanly support it — it's dominated by the word's own morphological family.

**Contrast with lord**: lord's top neighbors are almost never morphological variants (lordly, lordship appear occasionally but are not dominant). Lord's neighborhood is semantically dense. Writer's is largely orthographic.

### tobacco: creation event, not drift

Tobacco does not exist in European texts before ~1492 (New World discovery). The corpus's "pre-1500" category almost certainly contains no meaningful tobacco representations. The pre-1500 → 1500-1700 drift score (1.23) is not semantic change — it's the gap between a null/noise vector and the word's first real semantic context.

Trajectory once tobacco is established:
- **1500-1700**: traveller, wheat, treatment, youth — commodity context, exotic/new
- **1700-1800**: warmth, woe, useless, waves, volumes — moral/emotional commentary
- **1850-1900**: wool, transport, trade, unlucky — economic/colonial trade good
- **1900-1923**: **ulysses**, vices, trousers, twilight — literary/domestic register

The 1900-1923 neighbors are striking: **ulysses** is the top co-occurrence partner at 6.6 PPMI. Joyce's *Ulysses* (1922) is almost certainly in the corpus, and Leopold Bloom's tobacco use is a recurring motif. This is a corpus composition artifact — a single high-frequency text can dominate PPMI for rare words in its era.

### A taxonomy of drift types

These cases, combined with prior sessions, suggest the drift scores conflate at least five distinct phenomena:

| Type | Example | Signature |
|------|---------|-----------|
| **Pivot** | lord | Neighbors replaced wholesale; non-monotonic arc |
| **Broadening** | mission | Raw count rises, PPMI falls; new registers added without dropping old |
| **Accumulation** | immortal | Multiple simultaneous registers in late eras; fragmented |
| **Frequency collapse** | writ | Drift → 1.0 as co-occurrence count approaches 0 |
| **Creation event** | tobacco | Large drift in first transition from null representation |
| **Orthographic artifact** | writer | Neighbors dominated by morphological family |

This taxonomy is the Phase 2 clustering specification: the k-means should ideally reproduce these categories from the drift score vectors and co-occurrence statistics alone — without requiring manual neighbor inspection.

### Phase 1: complete

Ten sessions documented. All major patterns analyzed. Corpus stable.

### Phase 2: concrete next step

The clustering script should now filter or flag words where any era's co-occurrence count is below a threshold (~50 pairs) before computing drift trajectory vectors. This prevents frequency-collapse cases (writ, writer) from polluting cluster assignments. The clean taxonomy above gives six behavioral categories to validate the clustering against.

---

## Session Notes: 2026-06-14

Corpus stable. No recomputation needed (36,288 drift scores, 48,000 word vectors).

### creating: boilerplate contamination

"creating" scores 1.23 drift (rank 13, 1500-1700 → 1700-1800) but the neighbor data reveals total boilerplate domination:

- **All eras**: identify, replace, derivative, editions, updated, displaying, references, performing, distributing, protected, print, gutenberg, project

These are Project Gutenberg header/footer terms ("creating derivative works", "distributing", "performing or displaying"). The word "creating" appears in the Gutenberg license boilerplate that precedes every text in the corpus. The drift score is not semantic — it measures how the *boilerplate word mix* changed as different texts were assigned to different eras.

This is a sixth artifact type beyond the five documented yesterday:

| Type | Example | Signature |
|------|---------|-----------|
| **Pivot** | lord | Neighbors replaced wholesale; non-monotonic arc |
| **Broadening** | mission | Raw count rises, PPMI falls; new registers added |
| **Accumulation** | immortal | Multiple simultaneous registers in late eras |
| **Frequency collapse** | writ | Drift → 1.0 as co-occurrence count → 0 |
| **Creation event** | tobacco | Large drift in first transition from null |
| **Orthographic artifact** | writer | Neighbors dominated by morphological family |
| **Boilerplate contamination** | creating | Neighbors dominated by Gutenberg license terms |

The "gutenberg" vocabulary flag catches some of these (gutenberg appears as a direct neighbor), but "creating" shows that the contamination extends beyond words *adjacent to* "gutenberg" — any word that frequently appears *within* the license block becomes suspect. Other candidates: "displaying", "performing", "distributing", "derivative", "editions" — if any of these appear in the top-30 drifters, their scores are artifacts.

### local: class encoding

"local" scored 1.23 drift (1700-1800 → 1800-1850) and shows a genuine three-stage semantic shift:

- **1500-1700**: worry, mayor, solicitude, politics, solitude, shapes — administrative/personal. Local as *specific place-knowledge* — the anxiety of not knowing an area (worry, solicitude), the politics of a specific place (mayor, politics). Emotionally colored.
- **1700-1800**: subsequently, waiter, shudder, towns, poverty, university, shrine, sailors — travel/encounter. Local as *what you encounter when traveling* (waiter, shrine, sailors). This is Grand Tour writing — the 18th century genre of travel as education. The "local" waiter, the "local" shrine. Regional but not derogatory.
- **1800-1850**: provincial, squire, poorer, purely, mainly, police, workers, national — class hierarchy. "Provincial" is the strongest neighbor (8.77 PPMI). Local becomes a *class marker*: local = non-metropolitan = parochial = lower status. "National" appears as the contrasting term. "Police" reflects urbanization — local enforcement as distinct from national governance. "Workers" and "poorer" confirm the socioeconomic encoding.

The semantic shift: *administrative specificity* → *travel encounter* → *class/provincial marker*. The 1800-1850 transition is where "local" acquires its pejorative valence — the association that persists in modern English ("just a local", "local concerns vs. national").

"Squire" (7.50 PPMI in 1800-1850) is the clearest indicator: the local squire is the parochial landed gentry, a figure of satire in Dickens and Trollope. By 1800-1850 the Victorian novel had already embedded "local" in a hierarchy where London = sophisticated and local = backward.

### bethel: absent from co-occurrences

"bethel" (drift 1.25, pre-1500 → 1500-1700) has zero co-occurrence pairs in the database. The drift score exists in drift_scores but the underlying co-occurrence data was not stored (or the word was filtered out). This is consistent with "bethel" being an extremely rare word — it appears in fewer than ~2 texts and was likely excluded from the co-occurrence table by a frequency threshold. The drift score is probably a frequency-collapse artifact like "writ."

### Phase 1: complete

Eleven sessions documented. Taxonomy now has seven behavioral categories. Corpus stable.

### Phase 2: concrete next step

The clustering script needs a pre-filtering step:
1. Flag words where any era's co-occurrence count < 50 pairs (frequency-collapse)
2. Flag words whose top-5 neighbors in any era include Gutenberg boilerplate terms (contamination)
3. Remove or quarantine orthographic clusters (words where >60% of top neighbors are morphological variants)

After filtering, the remaining words should cleanly separate into Pivot / Broadening / Accumulation patterns via k-means on the 5-element drift score vector. "local" is a new clean example of the Pivot pattern (neighbors replaced sequentially) — add to validation set alongside lord and immortal.

---

## Session Notes: 2026-06-16

Corpus stable. No recomputation needed (36,288 drift scores, 48,000 word vectors).

### promoting: fully Gutenberg-contaminated

Yesterday's hypothesis confirmed. Query of promoting's Gutenberg-adjacent neighbors across all eras reveals a perfectly uniform boilerplate signature:

| Era | sharing | protect | removed | using | support | works |
|-----|---------|---------|---------|-------|---------|-------|
| pre-1500 | 14 | 14 | 14 | 14 | 16 | 30 |
| 1500-1700 | 12 | 12 | 12 | 12 | 12 | 24 |
| 1700-1800 | 34 | 34 | 34 | 34 | 34 | 68 |
| 1800-1850 | 14 | 14 | 14 | 14 | 16 | 30 |
| 1850-1900 | 14 | 14 | 14 | 14 | 14 | 28 |
| 1900-1923 | 24 | 24 | 24 | 24 | 24 | 48 |

The counts are proportional to the number of texts per era (1700-1800 has ~2.4× the 1850-1900 count — and the raw co-occurrence counts reflect exactly that ratio). Each text contributes exactly one copy of the Gutenberg license block, and "promoting" appears only in that block. The total pairs per era (13, 55, 40, 30, 7, 29) look realistic but are entirely Gutenberg-sourced.

**Implication for mission analysis**: mission's documented stability — "promoting" and "sharing" as stable top neighbors across all eras — is an artifact. Those two words are not semantic neighbors of "mission" in the historical sense. They co-occur because both appear in the same Gutenberg license block near each other, and that block follows every text regardless of era. Mission's actual semantic neighborhood requires recomputation on a boilerplate-stripped corpus.

**Distinct contamination signature from "electronic"**: electronic is ~150 pairs per era (flat). promoting is 7-55 pairs per era (proportional to era text count). Both are contaminated but in different ways: electronic's uniform distribution reflects it appearing the same number of times per text; promoting's proportional distribution reflects its rare appearance (once per text). Either way, the boilerplate stoplist must include: `{promoting, sharing, protect, removed, using, support, works, read, displaying, distributing, derivative, editions, redistributing, electronic, gutenberg, hart, michael, liability}`.

### unavoidable: frequency collapse confirmed (rank 3 in corpus is noise)

Pair counts per era: pre-1500=13 pairs (30 occurrences), 1500-1700=**1 pair (2 occurrences)**, 1700-1800=8, 1800-1850=15, 1850-1900=19, 1900-1923=3.

The pre-1500 → 1500-1700 drift score of 1.258 (rank 3 in the entire corpus) is vector noise. The word practically vanishes in 1500-1700 (1 pair, 2 raw occurrences) — the computed vector is nearly empty. The "drift" is a cosine distance between a moderately-built pre-1500 vector and a noise vector. Not a semantic signal.

The direction of the collapse is notable: unavoidable was *more* present in pre-1500 than in 1500-1700. This may reflect the word's Latinate scholastic register — used in medieval theological and philosophical discourse, then declining as vernacular English rose. The Reformation period (1500-1700) shifted toward shorter, more direct prose. But the pair count is too small to draw this conclusion from the data alone.

Updated taxonomy (eighth type):

| Type | Example | Signature |
|------|---------|-----------|
| **Pivot** | lord | Neighbors replaced wholesale; non-monotonic arc |
| **Broadening** | mission | Raw count rises, PPMI falls (pending reeval after decontam) |
| **Accumulation** | immortal | Multiple simultaneous registers in late eras |
| **Frequency collapse** | writ, unavoidable | Drift → 1.0 as pair count → 0 |
| **Creation event** | tobacco | Large drift in first transition from null |
| **Orthographic artifact** | writer | Neighbors dominated by morphological family |
| **Boilerplate contamination** | creating, electronic, promoting | Gutenberg license neighbors uniform/proportional across eras |
| **Apparent stability (contaminated)** | mission | Stable neighbors are boilerplate, not semantics |

### crowded: 1500-1700 neighborhood (new data)

Previously only 1800-1850 and 1850-1900 were documented. The 1500-1700 neighborhood is distinct:

- **1500-1700**: squeezed, ideas, revolution, crush, elephant, stooping, floated, dirty, games, snatch, translated, rider, pressing, streets, ride, leather, university, humours, slow

This is public spectacle: the physical experience of a crowd at a fair, market, or entertainment. "Elephant" (exotic animal display), "rider", "stooping", "pressing" (jostling), "games" — these are fair/performance crowd contexts. "Revolution" and "ideas" alongside "humours" hint at an early modern crowd that is socially charged, not just physically dense.

Full crowded trajectory:
- **1500-1700**: fair/spectacle crowds — physical action, exotic display, social charge
- **1800-1850**: crisis crowds — tents, hospital, pestilence, ragged, masses
- **1850-1900**: urban/statistical crowds — pattern, hatchway, estimated, sexes (from prior session)

Three distinct semantic regimes, none overlapping. The 1500-1700 → 1800-1850 transition (skipping an era) may be the sharpest semantic break — from spectacle to suffering. The 19th-century novel didn't inherit the early modern celebratory crowd; it replaced it with the industrial urban mob.

### Phase 1: complete

Thirteen sessions documented. Corpus stable.

### Phase 2: concrete next step

The boilerplate decontamination must precede clustering. Confirmed stoplist now has ~18 words. Next action: write a decontamination script that removes all co-occurrence pairs where word_a OR word_b is in the stoplist, then recompute word vectors and drift scores on the cleaned table. This invalidates the current "mission broadening" finding and likely affects other words — the corpus needs a clean pass before any Phase 2 analysis is meaningful.

---

## Session Notes: 2026-06-17

Corpus stable. No recomputation needed (36,288 drift scores, 48,000 word vectors).

### Convergence: Phase 1 is analytically exhausted

Today's full query pass — top drifters, most stable words, era transition averages, and neighbor pulls for lord, immortal, and mission across multiple eras — returned no findings not already documented in prior sessions.

**Lord** (pre-1500 and 1500-1700 neighbors): Confirms the courtly-to-scriptural pivot documented 2026-06-06 and 2026-06-12. Pre-1500: patron, princess, superstition, wishes, mischief. 1500-1700: wast, utterance, saul, wherefore, oil, thee, slave. No new signal.

**Immortal** (1700-1800 neighbors): Confirms the theological peak documented 2026-06-08. Needful, torments, salvation, repentance, temptation, mortal. The evangelical register is fully consistent with prior analysis.

**Mission** (1500-1700 and 1700-1800): Promoting and sharing remain top collocates — but these are confirmed Gutenberg boilerplate (2026-06-16). The 1700-1800 era adds "petersburg" and "princes" but these were already noted in the broadening analysis (2026-06-12 and 2026-06-15).

**Era drift ranking** is unchanged: 1700-1800→1800-1850 highest (0.941), 1850-1900→1900-1923 lowest (0.801).

**Most stable words** unchanged: himself, held, however, has, far — function words dominating the 1850-1900→1900-1923 tail.

### Conclusion: Phase 1 analysis is complete and stable

Fourteen sessions. All major patterns documented. Taxonomy has eight behavioral categories. No new data to extract from the current corpus without decontamination.

The outstanding question is no longer analytical — it's preparatory. The next session should be code-writing, not query-running.

### Phase 2: concrete next step

Write `worker/decontaminate.py`:
1. Load confirmed boilerplate stoplist (18 words: `electronic, gutenberg, project, displaying, performing, distributing, derivative, editions, redistributing, liability, promoting, sharing, hart, michael, protect, removed, using, works`)
2. `DELETE FROM cooccurrences WHERE word_a IN (stoplist) OR word_b IN (stoplist)`
3. Recompute word vectors from cleaned cooccurrences
4. Recompute drift scores from new vectors
5. Output: a new cleaned DB or new tables (`cooccurrences_clean`, `word_vectors_clean`, `drift_scores_clean`)

No more manual neighbor analysis until the corpus is decontaminated. The clustering and dream engine both depend on clean vectors.

---

## Session Notes: 2026-06-15

Corpus stable. No recomputation needed (36,288 drift scores, 48,000 word vectors).

### "electronic": uniform contamination across all eras

Today's analysis of mission's 1500-1700 neighbors revealed "electronic" at 6.78 PPMI. Query expanded to check the full scope:

| Era | Co-occurrence pairs |
|-----|---------------------|
| pre-1500 | 152 |
| 1500-1700 | 150 |
| 1700-1800 | 152 |
| 1800-1850 | 159 |
| 1850-1900 | 151 |
| 1900-1923 | 150 |

~150 pairs in every era, including pre-1500. "Electronic" cannot be a meaningful word in any of these historical periods — the modern sense dates to the 20th century. The uniform distribution is the diagnostic signature of Gutenberg license boilerplate: the "electronic works" language appears in every text's header/footer regardless of its assigned era, so the contamination is flat across all eras.

Top co-occurrence partners for "electronic": concept, professor, prominently, promoting, promotion, group, legal, liability, production, mission, associated, display, distributing, sharing, expenses, **hart** (Michael Hart, founder of Project Gutenberg), redistributing. These are all standard Gutenberg license terms.

**Implication for contamination detection**: The previously documented detection approach (flag words whose top-5 neighbors include Gutenberg terms) is insufficient. "Electronic" itself is one of those terms, and it appears uniformly contaminated — you'd need to flag it *before* inspecting its neighbors. A cleaner approach: build a stoplist of known Gutenberg boilerplate terms and remove them from the co-occurrence table entirely before any analysis. Known candidates: electronic, gutenberg, project, displaying, performing, distributing, derivative, editions, redistributing, liability, promoting (in Gutenberg legal sense), hart, michael.

The Broadening pattern documented for "mission" (promoting/sharing stable across eras) needs re-evaluation: if "promoting" is a contaminated Gutenberg term, mission's apparent semantic stability may partly be an artifact of co-occurring with boilerplate in every era's texts.

### Phase 1: complete

Twelve sessions documented. Taxonomy now includes seven behavioral categories. The contamination finding today has methodological weight: the boilerplate problem is broader than a single-word artifact — it's a systematic corpus-level injection affecting all words that co-occur with Gutenberg license terms.

### Phase 2: concrete next step

Pre-filtering now has three mandatory steps before clustering:
1. Build a Gutenberg boilerplate stoplist and delete all co-occurrence pairs involving those words
2. Recompute word vectors and drift scores on the cleaned corpus
3. Apply frequency threshold (<50 pairs/era → quarantine)

Only then run k-means. The boilerplate contamination invalidates any clustering done on the current uncleaned vectors — words like "mission" whose stability was partly measured against "promoting" (a Gutenberg term) will shift once the boilerplate is removed.



---

## Session Notes: 2026-06-18

Corpus stable. No recomputation needed (36,288 drift scores, 48,000 word vectors).

### Analysis: fully converged

All queries returned findings already documented in prior sessions. Top drifters, stable words, era averages, and neighbor pulls for lord / immortal / mission — no new signal. Phase 1 analysis is exhausted.

### Phase 2 begins: decontaminate.py written

`worker/decontaminate.py` implements the decontamination pipeline planned over sessions 2026-06-13 through 2026-06-17.

**Dry-run results** (run 2026-06-18):

| Stoplist word | Pairs affected |
|---------------|----------------|
| removed | 4,663 |
| works | 3,482 |
| protect | 2,400 |
| using | 2,273 |
| gutenberg | 2,041 |
| michael | 1,790 |
| performing | 1,332 |
| electronic | 914 |
| sharing | 904 |
| hart | 861 |
| displaying | 813 |
| editions | 752 |
| promoting | 625 |
| distributing | 599 |
| liability | 351 |
| derivative | 247 |
| redistributing | 150 |

**Total removal: 23,844 pairs out of 10,534,848 (0.23%).**

The contamination is more targeted than feared — less than a quarter of one percent of the corpus. The decontamination will not significantly distort legitimate semantic relationships. It writes output to `archaeology_phase1_clean.db` and does not modify the original.

**Script behavior:**
1. Copies original DB to `archaeology_phase1_clean.db`
2. Deletes co-occurrence pairs where word_a OR word_b is in the 18-word stoplist
3. Rebuilds word_vectors via SVD on the cleaned matrix
4. Recomputes drift_scores from the new vectors

### Phase 2: concrete next steps

1. **Run decontaminate.py** (no `--dry-run`) to generate the clean DB
2. **Update `phase1_config.py`** to point `DB_PATH` at `archaeology_phase1_clean.db`
3. **Write `worker/cluster.py`**: k-means on 5-element drift-score vectors per word; validate against the known taxonomy (Pivot=lord, Broadening=mission, Accumulation=immortal, Frequency-collapse=writ, Creation-event=tobacco, Boilerplate=creating)
4. **Re-evaluate mission**: mission's "broadening" pattern was documented against contaminated vectors; after decontamination its top neighbors may differ entirely

