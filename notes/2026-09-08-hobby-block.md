# Archaeology Hobby Block — September 8, 2026

## Work Completed

### Paper tightening pass

Spent the hour doing a close reading and edit of `paper/semantic_archaeology_draft.md`. Not a rewrite — a precision pass. Fixed:

1. **Data inconsistencies found and corrected:**
   - Jump count range: was "9–48", corrected to "3–48" (lowest is *love* at T=1.2 with 3 jumps)
   - Drift mean: was "~0.52", corrected to "~0.67" (verified against DB: 0.674)
   - Unclassifiable count in validation table: was 29 (55%), corrected to 30 (57%)
   - Zero-signal count: was 1, corrected to 0
   - Propagated 57% to all mentions (abstract, §2.5, §4.2, §5)
   - README drift score count: was 36,288, corrected to 38,515

2. **Prose tightening:**
   - Abstract: "suggesting the taxonomy's keyword coverage is still sparse" → "indicating sparse keyword coverage" (sharper)
   - §1.1: removed parenthetical list of semantic shift types (broadening, narrowing, etc.) — unnecessary clutter
   - §1.3: merged two short paragraphs into one flowing paragraph
   - §3.4: fixed H1 (*woman* jumped 9 times, not 15, at T=1.0); fixed H2 phrasing; fixed H5 formatting (was `| Status:` instead of `**Status:**`)
   - §3.5: tightened parenthetical to "(*plus* at T=1.8: 48 jumps; *love* at T=1.2: 3 jumps)"
   - §4.1: removed redundant restatement of gravity-well test operationalization; pointed back to §3.6 instead

## Key Insight

The paper had accumulated small data errors (0.52 mean drift, 55% tie rate, 9 minimum jumps) that were probably from earlier drafts and never updated when the database changed. A precision pass like this is necessary before the paper can be considered "solid" — not because the argument changed, but because credibility depends on the numbers matching the database. Every inconsistency is a hole a reviewer could poke.

## What Needs Doing Next

- Expand keyword coverage to push the 57% unclassifiable rate down
- Stronger null model (shuffle co-occurrence or permute SVD)
- Public site, after the paper is truly solid

## Files Changed

- `paper/semantic_archaeology_draft.md` — data corrections, prose tightening
- `README.md` — drift score count corrected
