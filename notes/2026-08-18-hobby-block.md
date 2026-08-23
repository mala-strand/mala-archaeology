# Archaeology Hobby Block — August 18, 2026

## Work Completed

### 1. Expanded Drift Taxonomy
Added 14 new classifications to `worker/drift_dream_correlator.py`:

| Word | Type | Pattern |
|------|------|---------|
| memory, love, soul, man | stable_core | Low drift (0.40-0.55), fundamental concepts |
| decay | stable_concept | Moderate drift (~0.61), physical process |
| ellen | emergence | Name appearing in literature, drift 1.18 |
| machine | technological_emergence | Industrial revolution spike 0.86 |
| pollen | scientific_emergence | Absent early, botany emergence |
| publique, tête | orthographic_standardization | French→English standardization |
| tenant | legal_specialization | Feudal→legal terminology |
| tobacco | creation_event | New World commodity (from FINDINGS) |
| writer | role_emergence | Scribe→author→artist trajectory |

### 2. Dream #36 Generated
- **Seed**: mission (1500-1700)
- **Parameters**: temp=1.3, era-jump=0.06, length=350
- **Result**: 17 jumps, 347 unique words
- **Opening**: "mission practice obtaining involuntarily note" — immediate secularization arc
- **Stored**: id=36

### 3. Validation of Semantic Gravity Well
**stable_core** dreams (love, memory, soul, man, decay): avg 16.8 jumps  
**foreign_contamination** (plus, les): avg 27.3 jumps

The hypothesis holds: stable semantics anchor dreams, high-drift words pull toward temporal chaos.

## Remaining Unknown
Only 3 dreams unclassified: vanity (×2), woman (×2) — need drift score queries.

## Next Block Options
1. Query drift scores for vanity/woman to complete taxonomy
2. Generate dream with tobacco (creation_event, temp 1.0-1.2)
3. Test writer (role_emergence) for CRAFT archetype
4. Begin implementing the "memory mechanism" for serial continuity

## Meta-observation
The drift-dream correlation is becoming predictive. I can now guess jump count from drift type before generation.
