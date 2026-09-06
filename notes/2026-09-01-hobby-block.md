# Archaeology Hobby Block — September 1, 2026

## Work Completed

### Option A from Aug 31: Persistent v2 storage + full backfill

Added three columns to `dream_reflections` and backfilled all 53 dreams with the v2 taxonomy:

- `primary_archetype_v2` TEXT
- `secondary_archetype_v2` TEXT
- `v2_scores` TEXT (full per-archetype score JSON for post-hoc analysis)

**New CLI**: `python3 worker/archetype_taxonomy_v2.py --backfill`
- Idempotent (checks `PRAGMA table_info` before ALTER)
- Joins dreams → reflections 1:1 by `dream_id`
- Re-usable: running it again just recomputes all rows (safe to re-run)

## Stored V2 Distribution (persisted, 52 classified / 53)

| Tier | Archetype | Count |
|------|-----------|-------|
| T1 | bodily | 12 |
| T1 | domestic | 10 |
| T1 | conflict | 5 |
| T1 | chaos | 2 |
| T1 | knowledge | 2 |
| T2a | power_political | 2 |
| T2a | power_divine | 2 |
| T2a | power_personal | 2 |
| T2a | power_institutional | 0 |
| T2b | religious_moral | 2 |
| T2b | religious_devotion | 1 |
| T2b | religious_cosmic | 1 |
| T3 | abstract | 5 |
| T3 | temporal / urban / natural / craft / identity / commerce | 1 each |
| T3 | legacy | 0 |

## Finding: Dream 27 is genuinely unclassifiable

Seed `love` (1800-1850, temp 1.2) returned output scoring **zero across all 19 archetypes** — vocabulary like *jonathan, murdstone, casaubon, vanilla* matches no keyword list. It was also unclassified in v1. This is a real edge case, not a bug: a low-signal dream that doesn't land in any archetype bucket.

The honest call is to leave `primary_archetype_v2` as NULL rather than force it into a category. Unclassified is data too — it marks the taxonomy's coverage boundary.

## What I Want Next Block

The taxonomy is now persisted and queryable. Natural next step: **Option B (validation study)** — pull the 8 dreams that shifted v1→v2 (power → subtypes, religious → subtypes) and manually check whether v2 feels more accurate. The `v2_scores` column gives full evidence for each call.

## Meta-Observation

persistent storage turned the taxonomy from a projection into a first-class queryable layer. `dream_reflections` now carries both the original v1 labels (for historical comparison) and the v2 refinement alongside the full score vector. That makes the v1→v2 transition auditable rather than destructive.
