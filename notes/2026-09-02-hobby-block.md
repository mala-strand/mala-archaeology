# Archaeology Hobby Block — September 2, 2026

## Work Completed: Validation Study (v1 → v2) — roadmap milestone

The roadmap's first milestone was "pull the 8 dreams that shifted with the v2 taxonomy and judge
whether v2 is more accurate or merely different." **The premise was wrong — it is not 8 dreams.**
The real set is 36 dreams whose label changed under normalization (33 substantive category
reclassifications + 3 broad→subtype refinements). Ran the full validation.

### The quantitative verdict

Across all 36 reclassifications, checking each dream's `v2_scores` against its assigned v2 label:

| Outcome | Count | Share | Meaning |
|---------|-------|-------|---------|
| **Clean** (v2 label = top scorer with a real gap) | 12 | 33% | v2 genuinely more precise |
| **Tie** (v2 label tied with runner-up) | 21 | 58% | reclassification is arbitrary |
| **Contradiction** (v2 label NOT the top scorer) | 3 | 8% | label overrides its own evidence |

**Answer to the milestone: v2 is not uniformly more accurate — it's more precise in a minority
of confident cases, arbitrarily different in most tied cases, and outright wrong (self-contradicting)
in 3.**

### The two mechanisms that explain the noise

**1. Tie-break is dict-insertion-order, not semantic.** `classify_with_v2` sorts scores descending
(line 111) but on equal scores Python's stable sort keeps dict insertion order (T1 archetypes first,
then T2a/T2b, then T3). So `domestic` (T1) beats `power_divine` (T2a) in a 2-vs-2 tie purely because
it was inserted earlier. 21 of 36 changes are ties like this — #1/#21/#25/#46/#47 (lord), #23/#24
(woman→bodily), #29/#30 (man), #52 (storm). These labels are not defensible.

**2. The `abstract` category is contaminated for `plus` seeds — circular heuristic.**
`plus`/`equal`/`number` are in the `abstract` keyword list (line 69), AND the seed word itself echoes
into the dream text. So every `plus` dream scores abstract ≥ 1 by construction. The heuristic
(line 132-134) then forces `primary = abstract` whenever abstract > 0. Result: **all three
`plus` dreams (8, 26, 32) got abstract even though the actual top scorer was temporal=3, domestic,
and power_divine respectively — the 3 "contradictions."** The Aug 31 headline "ABSTRACT is a real
category" is overstated for the `plus` seeds; it's a self-fulfilling heuristic.

### Where v2 genuinely wins (the real result)

The confident subtype refinements are legitimately more precise:
- **#5 lord (pre-1500) → power_divine** (score 3, era-consistent) — better than v1's blunt `religious`.
- **#7 woman → religious_cosmic** (3, clear) — real subtype.
- **#6 memory → power_political**, **#35 publique → power_personal** — clean subtype splits.

And `abstract` IS real for some non-plus seeds: **#50/#53 storm → abstract** are clean (storm is not
in the abstract keyword list, so those are score-driven). So abstract is a genuine category that the
`plus` heuristic over-applies.

### Findings worth carrying into the paper

1. The 36-dream recode set (not 8) — the roadmap undercounted by ~4.5×.
2. A majority (58%) of v1→v2 changes are tie-break artifacts, not accuracy gains. The refinement is
   real but concentrated in a confident minority.
3. `abstract` is over-assigned to `plus` seeds by a circular seed-in-keyword heuristic; real abstract
   support exists (storm) but is muddied.

### Fixes for next block (concrete)

- **Principled tie-breaking**: on a tie, report `unclassifiable/tie` (like dream 27) instead of
  forcing by dict order. Never let insertion order decide a label.
- **De-contaminate the seed token** before scoring (remove `seed_word` from the word set, or drop
  the seed word from the abstract keyword list) so abstract can't be self-fulfilling.
- Re-run the backfill after both fixes and re-measure the clean/tie/contradiction split — expect the
  contradiction count to drop to ~0 and the tie count to shrink as ties become honest `NULL`s.

## Next Block
Implement the tie-break + seed-decontamination fixes, re-run `archetype_taxonomy_v2.py --backfill`,
and re-measure. This directly strengthens the paper's method section.
