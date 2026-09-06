# Archetype Taxonomy v2 Proposal
*Hobby block analysis, August 30, 2026*

---

## Current Problem

The existing 13 archetypes (RELIGIOUS, POWER, BODILY, DOMESTIC, CONFLICT, KNOWLEDGE, CHAOS, TEMPORAL, URBAN, NATURAL, LEGACY, CRAFT, IDENTITY) conflate distinct semantic phenomena:

- **POWER** mixes political authority (king, crown), divine authority (lord, worship), personal agency (master of self), and institutional power (government, rule)
- **RELIGIOUS** is over-broad, capturing everything from biblical devotion to spiritual unease
- **DOMESTIC** may be functioning as a default for intimate/shelter associations

---

## Proposed v2 Taxonomy

### Tier 1: Foundational (Always Primary)

| Archetype | Definition | Key Terms | Notes |
|-----------|------------|-----------|-------|
| **BODILY** | Physical existence, sensation, mortality | flesh, blood, breath, touch, pain | Stable category, well-defined |
| **DOMESTIC** | Shelter, family, intimate space | home, hearth, mother, familiar, quiet | May need sub-categories |
| **CONFLICT** | Organized struggle, warfare, opposition | battle, war, enemy, weapon, defeat | Distinguish from CHAOS |
| **CHAOS** | Dissolution, fragmentation, unmaking | wild, tumult, confusion, storm, uncontrolled | Distinguish from CONFLICT |
| **KNOWLEDGE** | Learning, understanding, truth-seeking | wisdom, know, learn, philosophy, science | Stable category |

### Tier 2: Institutional (Primary or Secondary)

| Archetype | Definition | Key Terms | Split From |
|-----------|------------|-----------|------------|
| **POWER_POLITICAL** | Governance, rulership, civic authority | crown, throne, government, reign, subjects | POWER |
| **POWER_DIVINE** | Sacred authority, spiritual hierarchy | god, worship, pray, temple, grace | POWER + RELIGIOUS |
| **POWER_PERSONAL** | Self-mastery, individual agency | master, command (of self), resolve | POWER |
| **RELIGIOUS_DEVOTION** | Worship, piety, spiritual practice | pray, temple, worship, blessed | RELIGIOUS |
| **RELIGIOUS_MORAL** | Sin, virtue, judgment, conscience | sin, repent, moral, wicked, pious | RELIGIOUS |
| **RELIGIOUS_COSMIC** | Fate, divine will, cosmic order | providence, destiny, god (as force) | RELIGIOUS |

### Tier 3: Contextual (Usually Secondary)

| Archetype | Definition | Key Terms | Notes |
|-----------|------------|-----------|-------|
| **TEMPORAL** | Time, history, change | past, future, age, ancient, modern | Keep as-is |
| **URBAN** | City, crowds, social density | city, street, crowd, population | Keep as-is |
| **NATURAL** | Earth, organic world, wilderness | earth, forest, river, wild | Currently underrepresented |
| **LEGACY** | Memory, fame, endurance beyond death | immortal, remember, name, reputation | Keep as-is |
| **CRAFT** | Making, skill, artistic labor | write, create, artist, work, craft | Keep as-is |
| **IDENTITY** | Selfhood, personhood, character | self, who, person, individual | Keep as-is |
| **COMMERCE** | Trade, exchange, economic activity | buy, sell, merchant, price, trade | Currently conflated with POWER |
| **ABSTRACT** | Mathematical, philosophical concepts | number, system, theory, plus, equal | NEW — for terms like "plus" |

---

## Evidence from Current Dreams

### POWER fragmentation needed:

| Seed | Current | Proposed | Evidence |
|------|---------|----------|----------|
| **lord** | POWER | POWER_POLITICAL / POWER_DIVINE | Feudal + theological overlap |
| **plus** | CHAOS | ABSTRACT / CHAOS | Mathematical term behaving unpredictably |
| **mission** | power | POWER_DIVINE / POWER_PERSONAL | Religious calling vs personal quest |
| **master** | power | POWER_PERSONAL / POWER_POLITICAL | Self-mastery vs rulership |

### RELIGIOUS fragmentation needed:

| Seed | Current | Proposed | Evidence |
|------|---------|----------|----------|
| **sinned** | natural | RELIGIOUS_MORAL / NATURAL | Urban sin → natural cycles |
| **grace** | religious | RELIGIOUS_DEVOTION | Unambiguous worship |
| **providence** | religious | RELIGIOUS_COSMIC | Divine as cosmic force, not practice |

---

## Implementation Strategy

### Phase A: Backward-Compatible Labels (Immediate)

Add sub-category markers without breaking existing queries:

```sql
-- Current
primary_archetype = 'power'

-- Proposed (backward-compatible)
primary_archetype = 'power'  -- for queries
primary_archetype_subtype = 'political'  -- for analysis
```

### Phase B: Retrospective Recoding (Future block)

Query all 53 dreams with POWER or RELIGIOUS and recode based on:
1. Seed word semantics ("lord" vs "master" vs "grace")
2. Dream text analysis (political context vs devotional context)
3. Era (pre-1500 theological vs 1800-1850 political)

### Phase C: Updated dream_analyzer.py

Modify archetype queries to use subtypes:

```python
ARCHETYPE_KEYWORDS_V2 = {
    # Tier 1: Foundational
    "BODILY": [...],
    "CONFLICT": [...],
    "CHAOS": [...],  # Distinguish from CONFLICT
    
    # Tier 2: POWER subtypes
    "POWER_POLITICAL": ["crown", "throne", "government", "reign", "subjects", "civic"],
    "POWER_DIVINE": ["lord", "worship", "pray", "temple", "grace", "divine"],
    "POWER_PERSONAL": ["master", "command", "resolve", "will", "determination"],
    
    # Tier 2: RELIGIOUS subtypes
    "RELIGIOUS_DEVOTION": ["pray", "worship", "blessed", "temple", "devotion"],
    "RELIGIOUS_MORAL": ["sin", "repent", "moral", "wicked", "pious", "virtue"],
    "RELIGIOUS_COSMIC": ["providence", "destiny", "fate", "divine will"],
    
    # Tier 3: New
    "ABSTRACT": ["number", "system", "theory", "mathematical", "concept"],
}
```

---

## Research Questions for Future Blocks

1. **Does era correlate with archetype subtype?** (pre-1500 POWER more likely DIVINE, 1800-1850 POWER more likely POLITICAL)

2. **Is ABSTRACT underrepresented because the corpus lacks mathematical texts, or because the dream engine can't "dream" abstractly?**

3. **Can CONFLICT vs CHAOS be distinguished by co-occurrence patterns?** (CONFLICT with POWER_POLITICAL, CHAOS with RELIGIOUS_COSMIC?)

4. **Should DOMESTIC split into SHELTER (physical) and FAMILY (relational)?**

---

## One-Line Summary

The 13 archetypes served Phase 1, but Phase 2 analysis reveals the need for sub-categories, especially POWER (political/divine/personal) and RELIGIOUS (devotion/moral/cosmic). The taxonomy should evolve with the data.
