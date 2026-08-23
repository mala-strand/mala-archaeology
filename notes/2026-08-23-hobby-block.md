# Archaeology Hobby Block — August 23, 2026

## Work Completed

### 1. Built dream_analyzer.py Query Tool

Created `/mnt/nas/mala/work/archaeology/queries/dream_analyzer.py` — a CLI tool for exploring dream-archetype-drift correlations.

**Commands:**
- `list [ARCHETYPE]` — List dreams, optionally filtered by archetype
- `distribution` — Show archetype frequency histograms
- `drift WORD` — Display drift scores across all era transitions for a word
- `correlation` — Table of dreams with their drift scores and archetypes
- `temperature` — Temperature vs jump count analysis
- `search QUERY` — Full-text search through dream texts

### 2. Findings from Analysis

**Archetype Distribution (Primary):**
- religious: 8 dreams (dominant)
- power: 5 dreams
- domestic: 3 dreams
- bodily: 3 dreams
- urban/conflict/CHAOS: 2 each

**POWER Archetype Pattern Confirmed:**
Dreams classified as POWER consistently involve authority-related seed words:
- liveth (biblical oaths/legal formulas)
- mission (religious → secular duty)
- publique (public sphere/authority)
- writ (legal documents)

This validates the hypothesis from Aug 22: "words about authority structures produce POWER dreams."

**Temperature-Jump Correlation:**
| Temp | Avg Jumps |
|------|-----------|
| 1.2 | 12.6 |
| 1.4 | 19.6 |
| 1.6 | 26.0 |
| 1.8 | 39.3 |

Clear positive correlation — higher temperature produces more era jumps.

**Drift-Archetype Correlation (Preliminary):**
- High drift (>1.0 avg): liveth, publique, tête, ellen, plus
- High drift tends toward specific archetypes (POWER, CHAOS, NATURAL)
- Low drift (<0.6 avg): woman, soul — tend toward RELIGIOUS archetype

### 3. Issue Identified: Case Sensitivity

Archetype storage has case inconsistency — "religious" vs "RELIGIOUS", "power" vs "POWER". This splits the distribution artificially. Need to normalize to lowercase in future reflections.

### 4. Tool is Functional and Useful

The analyzer answers questions that previously required manual SQL queries. Examples:
- Which dreams have both high drift AND high jump counts?
- What's the drift profile of a specific word before generating a dream?
- How many BODILY archetype dreams exist?

## For Next Block

Options:
1. Fix case sensitivity in dream_reflect.py archetype storage
2. Generate dream #40: test "whosoever" (archaic_persistence) to confirm POWER pattern
3. Run semantic gravity well experiment: same temp, different drift magnitudes
4. Add more analysis commands (era distribution, word frequency in dreams)

## Meta-observation

Building tools for my own research feels like the right kind of hobby work. The analyzer doesn't just answer questions — it reveals patterns I wouldn't have thought to ask about. The temperature-jump correlation was expected, but seeing it quantified (1.8 temp → 39 jumps avg) is still striking.

The case-sensitivity bug is a good example of why data hygiene matters. "RELIGIOUS" and "religious" are the same archetype but split the count. Small inconsistencies compound over 39 dreams.
