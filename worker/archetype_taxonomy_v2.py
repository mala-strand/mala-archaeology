#!/usr/bin/env python3
"""
Archetype Taxonomy v2 Implementation

Implements the refined archetype system proposed in notes/2026-08-30-archetype-taxonomy-v2.md
Splits POWER and RELIGIOUS into subtypes for finer-grained analysis.

Usage:
    python3 worker/archetype_taxonomy_v2.py [--analyze] [--recode] [--compare]

Options:
    --analyze   Show current archetype distribution and v2 projections
    --recode    Recode all dreams with v2 taxonomy (adds v2 columns)
    --compare   Show side-by-side v1 vs v2 distribution
"""

import sys
import sqlite3
import argparse
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, ERA_ORDER

# Original v1 archetypes (for reference)
ARCHETYPES_V1 = {
    'religious': ['god', 'lord', 'prayer', 'soul', 'sin', 'grace', 'divine', 'holy', 'sacred', 'blessing', 'curse', 'damnation', 'salvation', 'faith', 'worship'],
    'power': ['king', 'lord', 'master', 'servant', 'slave', 'authority', 'command', 'obey', 'rule', 'throne', 'crown', 'subject', 'feudal', 'noble'],
    'domestic': ['home', 'house', 'family', 'mother', 'father', 'child', 'hearth', 'kitchen', 'bed', 'room', 'door', 'window', 'fire'],
    'natural': ['tree', 'river', 'mountain', 'sky', 'earth', 'water', 'fire', 'wind', 'stone', 'forest', 'sea', 'sun', 'moon', 'star'],
    'urban': ['street', 'crowd', 'city', 'building', 'room', 'shop', 'work', 'factory', 'machine', 'railway', 'carriage'],
    'bodily': ['hand', 'eye', 'heart', 'blood', 'flesh', 'bone', 'face', 'head', 'foot', 'voice', 'breath', 'touch'],
    'temporal': ['time', 'day', 'night', 'year', 'moment', 'hour', 'past', 'future', 'age', 'century', 'eternity'],
    'knowledge': ['book', 'write', 'read', 'learn', 'know', 'think', 'mind', 'wisdom', 'truth', 'false', 'understand'],
    'commerce': ['money', 'gold', 'silver', 'pay', 'buy', 'sell', 'trade', 'merchant', 'price', 'wealth', 'poor', 'rich'],
    'conflict': ['war', 'battle', 'fight', 'enemy', 'sword', 'death', 'kill', 'wound', 'struggle', 'defeat', 'victory'],
    'chaos': ['wild', 'tumult', 'confusion', 'storm', 'uncontrolled', 'disorder', 'waste', 'desolate'],
}

# Refined v2 archetypes - splits POWER and RELIGIOUS into subtypes
ARCHETYPES_V2 = {
    # Tier 1: Foundational (unchanged from v1)
    'bodily': ['hand', 'eye', 'heart', 'blood', 'flesh', 'bone', 'face', 'head', 'foot', 'voice', 'breath', 'touch', 'body', 'skin', 'hands', 'arm', 'arms', 'bones', 'eyes'],
    'domestic': ['home', 'house', 'family', 'mother', 'father', 'child', 'hearth', 'kitchen', 'bed', 'room', 'door', 'window', 'fire', 'table', 'corner', 'floor', 'sat', 'sitting', 'chair', 'children', 'sister'],
    'conflict': ['war', 'battle', 'fight', 'enemy', 'sword', 'death', 'kill', 'wound', 'struggle', 'defeat', 'victory', 'weapon', 'armor', 'army', 'campaign', 'fought', 'retreat'],
    'chaos': ['wild', 'tumult', 'confusion', 'storm', 'uncontrolled', 'disorder', 'waste', 'desolate', 'chaos', 'anarchy'],
    'knowledge': ['book', 'write', 'read', 'learn', 'know', 'think', 'mind', 'wisdom', 'truth', 'false', 'understand', 'study', 'school', 'reading', 'writing', 'written', 'note'],
    
    # Tier 2: POWER subtypes (split from v1 'power')
    'power_political': ['king', 'crown', 'throne', 'government', 'reign', 'subjects', 'civic', 'state', 'nation', 'empire', 'republic', 'court'],
    'power_divine': ['lord', 'worship', 'pray', 'temple', 'grace', 'divine', 'sacred', 'holy', 'blessing', 'god', 'providence', 'almighty', 'faith', 'bless', 'prayers'],
    'power_personal': ['master', 'command', 'resolve', 'will', 'determination', 'self', 'agency', 'choice', 'decision', 'control'],
    'power_institutional': ['authority', 'obey', 'rule', 'office', 'official', 'bureaucracy', 'administration', 'institution'],
    
    # Tier 2: RELIGIOUS subtypes (split from v1 'religious')
    'religious_devotion': ['pray', 'worship', 'blessed', 'temple', 'devotion', 'piety', 'prayer', 'adoration', 'reverence', 'forgive'],
    'religious_moral': ['sin', 'repent', 'moral', 'wicked', 'pious', 'virtue', 'sinned', 'guilt', 'conscience', 'damnation', 'salvation', 'faith', 'spirit'],
    'religious_cosmic': ['providence', 'destiny', 'fate', 'divine will', 'judgment', 'creation', 'cosmic', 'eternal', 'soul', 'immortal'],
    
    # Tier 3: Contextual (unchanged or refined)
    'temporal': ['time', 'day', 'night', 'year', 'moment', 'hour', 'past', 'future', 'age', 'century', 'eternity', 'ancient', 'modern'],
    'urban': ['street', 'crowd', 'city', 'building', 'shop', 'work', 'factory', 'machine', 'railway', 'carriage', 'population', 'corner'],
    'natural': ['tree', 'river', 'mountain', 'sky', 'earth', 'water', 'wind', 'stone', 'forest', 'sea', 'sun', 'moon', 'star', 'ocean', 'rain', 'cloud', 'clouds', 'mist', 'snow', 'trees', 'island', 'shadows', 'shining', 'shore'],
    'legacy': ['immortal', 'remember', 'name', 'reputation', 'fame', 'memory', 'endure', 'posterity', 'historical'],
    'craft': ['write', 'create', 'artist', 'work', 'craft', 'make', 'skill', 'art', 'design', 'compose'],
    'identity': ['self', 'who', 'person', 'individual', 'character', 'soul', 'mind', 'essence'],
    'commerce': ['money', 'gold', 'silver', 'pay', 'buy', 'sell', 'trade', 'merchant', 'price', 'wealth', 'poor', 'rich', 'market', 'bought', 'buying', 'goods', 'sold', 'paid', 'worth'],
    'abstract': ['number', 'system', 'theory', 'mathematical', 'concept', 'abstract', 'plus', 'equal', 'formula', 'equation'],
}


def connect():
    """Connect to database."""
    return sqlite3.connect(DB_PATH)


def extract_words_from_dream(dream_text: str) -> list:
    """Extract words from dream text."""
    import re
    lines = dream_text.split('\n')
    words = []
    for line in lines:
        line = line.strip()
        if line.startswith('Seed:') or line.startswith('Temperature:') or line.startswith('─'):
            continue
        if line.startswith('[') and '→' in line:
            continue
        line_words = re.findall(r'\b[a-z]+\b', line.lower())
        words.extend(line_words)
    return words


def score_archetypes_v2(words: list) -> dict:
    """Score dream against v2 archetype taxonomy."""
    word_set = set(words)
    scores = {}
    for archetype, keywords in ARCHETYPES_V2.items():
        matches = word_set.intersection(keywords)
        scores[archetype] = len(matches)
    return scores


def classify_with_v2(words: list, seed_word: str = None, start_era: str = None) -> dict:
    """
    Classify a dream using v2 taxonomy.
    Returns primary, secondary, and detailed breakdown.
    """
    word_set = set(words)

    # Decontaminate: remove the seed word from scoring set so it cannot
    # self-fulfill categories (e.g. 'plus' forcing ABSTRACT by construction).
    if seed_word:
        seed_lower = seed_word.lower()
        word_set.discard(seed_lower)

    scores = score_archetypes_v2(list(word_set))
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    max_score = sorted_scores[0][1] if sorted_scores else 0

    # Count how many archetypes share the top score.
    top_count = sum(1 for _, s in sorted_scores if s == max_score)

    # Principled tie-breaking: if multiple archetypes tie for first,
    # or if the top score is zero, mark as unclassifiable.
    if max_score == 0 or top_count >= 2:
        primary = ('unclassifiable', max_score)
        secondary = None
    else:
        primary = sorted_scores[0]
        secondary = sorted_scores[1] if len(sorted_scores) > 1 and sorted_scores[1][1] > 0 else None

    # Special case handling based on seed word and era
    # These heuristics address the fragmentation needs identified in taxonomy v2
    # NOTE: the 'plus' → abstract heuristic was REMOVED because seed
    # decontamination makes it unnecessary (and it caused contradictions).

    if seed_word and primary[0] != 'unclassifiable':
        seed_lower = seed_word.lower()

        # LORD: Feudal + theological overlap
        if seed_lower == 'lord':
            if start_era in ['pre-1500', '1500-1700']:
                if primary[0].startswith('power'):
                    primary = ('power_divine', primary[1])
            else:
                if primary[0].startswith('power'):
                    primary = ('power_political', primary[1])

        # MASTER: Self-mastery vs rulership
        if seed_lower == 'master':
            if 'self' in word_set or 'will' in word_set:
                primary = ('power_personal', primary[1])
            elif 'king' in word_set or 'crown' in word_set:
                primary = ('power_political', primary[1])

        # SINNED: Moral vs natural
        if seed_lower == 'sinned':
            if scores.get('natural', 0) > scores.get('religious_moral', 0):
                if secondary and secondary[0] == 'natural':
                    primary, secondary = secondary, primary

    return {
        'primary': primary,
        'secondary': secondary,
        'all_scores': scores,
        'top_5': sorted_scores[:5]
    }


def analyze_current_distribution():
    """Show current v1 archetype distribution from reflections."""
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT primary_archetype, COUNT(*) as count
        FROM dream_reflections
        GROUP BY primary_archetype
        ORDER BY count DESC
    """)
    
    print("=" * 60)
    print("CURRENT V1 ARCHETYPE DISTRIBUTION")
    print("=" * 60)
    
    total = 0
    for archetype, count in cursor.fetchall():
        if archetype:
            print(f"  {archetype:20s}: {count:3d}")
            total += count
    print(f"  {'TOTAL':20s}: {total:3d}")
    
    conn.close()


def project_v2_distribution():
    """Project what v2 distribution would look like."""
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT d.id, d.seed_word, d.start_era, d.dream_text
        FROM dreams d
        ORDER BY d.id
    """)
    
    v2_counts = Counter()
    
    for dream_id, seed, era, text in cursor.fetchall():
        words = extract_words_from_dream(text)
        classification = classify_with_v2(words, seed, era)
        v2_counts[classification['primary'][0]] += 1
    
    print("\n" + "=" * 60)
    print("PROJECTED V2 ARCHETYPE DISTRIBUTION")
    print("=" * 60)
    
    # Group by tier for clarity
    tier1 = ['bodily', 'domestic', 'conflict', 'chaos', 'knowledge']
    tier2_power = ['power_political', 'power_divine', 'power_personal', 'power_institutional']
    tier2_religious = ['religious_devotion', 'religious_moral', 'religious_cosmic']
    tier3 = ['temporal', 'urban', 'natural', 'legacy', 'craft', 'identity', 'commerce', 'abstract']
    
    print("\n  Tier 1 (Foundational):")
    for arch in tier1:
        count = v2_counts.get(arch, 0)
        print(f"    {arch:25s}: {count:3d}")
    
    print("\n  Tier 2a (POWER subtypes):")
    for arch in tier2_power:
        count = v2_counts.get(arch, 0)
        print(f"    {arch:25s}: {count:3d}")
    
    print("\n  Tier 2b (RELIGIOUS subtypes):")
    for arch in tier2_religious:
        count = v2_counts.get(arch, 0)
        print(f"    {arch:25s}: {count:3d}")
    
    print("\n  Tier 3 (Contextual):")
    for arch in tier3:
        count = v2_counts.get(arch, 0)
        print(f"    {arch:25s}: {count:3d}")
    
    total = sum(v2_counts.values())
    print(f"\n  {'TOTAL':25s}: {total:3d}")
    
    conn.close()


def compare_v1_v2():
    """Show side-by-side comparison of v1 vs v2 for dreams with POWER or RELIGIOUS."""
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT d.id, d.seed_word, d.start_era, d.dream_text,
               dr.primary_archetype as v1_primary
        FROM dreams d
        JOIN dream_reflections dr ON d.id = dr.dream_id
        WHERE dr.primary_archetype IN ('power', 'POWER', 'religious', 'RELIGIOUS')
        ORDER BY d.id
    """)
    
    print("\n" + "=" * 80)
    print("V1 → V2 RECODING FOR POWER/RELIGIOUS DREAMS")
    print("=" * 80)
    
    for dream_id, seed, era, text, v1_arch in cursor.fetchall():
        words = extract_words_from_dream(text)
        v2 = classify_with_v2(words, seed, era)
        
        print(f"\n  Dream #{dream_id}: '{seed}' ({era})")
        print(f"    V1: {v1_arch:15s} → V2: {v2['primary'][0]}")
        if v2['secondary']:
            print(f"    Secondary: {v2['secondary'][0]}")
    
    conn.close()


def backfill_v2():
    """Persist v2 classifications: add columns to dream_reflections and backfill all dreams."""
    conn = connect()
    cursor = conn.cursor()

    # Add columns idempotently
    cursor.execute("PRAGMA table_info(dream_reflections)")
    cols = {row[1] for row in cursor.fetchall()}
    if 'primary_archetype_v2' not in cols:
        cursor.execute("ALTER TABLE dream_reflections ADD COLUMN primary_archetype_v2 TEXT")
    if 'secondary_archetype_v2' not in cols:
        cursor.execute("ALTER TABLE dream_reflections ADD COLUMN secondary_archetype_v2 TEXT")
    if 'v2_scores' not in cols:
        cursor.execute("ALTER TABLE dream_reflections ADD COLUMN v2_scores TEXT")
    conn.commit()

    # Join dreams -> reflections (1:1 by dream_id)
    cursor.execute("""
        SELECT d.id, d.seed_word, d.start_era, d.dream_text, dr.id AS reflection_id
        FROM dreams d
        JOIN dream_reflections dr ON d.id = dr.dream_id
        ORDER BY d.id
    """)
    rows = cursor.fetchall()

    import json
    updated = 0
    print("=" * 60)
    print("BACKFILLING V2 CLASSIFICATIONS")
    print("=" * 60)
    for dream_id, seed, era, text, refl_id in rows:
        words = extract_words_from_dream(text)
        c = classify_with_v2(words, seed, era)
        # Store 'unclassifiable' even when score is 0 (e.g. dream 27 zero-signal)
        if c['primary'] and c['primary'][0] == 'unclassifiable':
            primary = 'unclassifiable'
        else:
            primary = c['primary'][0] if c['primary'] and c['primary'][1] > 0 else None
        secondary = c['secondary'][0] if c['secondary'] else None
        scores_json = json.dumps(c['all_scores'])
        cursor.execute(
            "UPDATE dream_reflections SET primary_archetype_v2=?, secondary_archetype_v2=?, v2_scores=? WHERE id=?",
            (primary, secondary, scores_json, refl_id),
        )
        updated += 1
    conn.commit()
    conn.close()
    print(f"\n  Backfilled v2 classifications for {updated} reflections")
    return updated


def analyze_stored_v2_distribution():
    """Show the stored v2 archetype distribution from the persisted columns."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT primary_archetype_v2, COUNT(*) as count
        FROM dream_reflections
        WHERE primary_archetype_v2 IS NOT NULL
        GROUP BY primary_archetype_v2
        ORDER BY count DESC
    """)
    dist = cursor.fetchall()

    tier1 = ['bodily', 'domestic', 'conflict', 'chaos', 'knowledge']
    tier2_power = ['power_political', 'power_divine', 'power_personal', 'power_institutional']
    tier2_religious = ['religious_devotion', 'religious_moral', 'religious_cosmic']
    tier3 = ['temporal', 'urban', 'natural', 'legacy', 'craft', 'identity', 'commerce', 'abstract']
    counts = dict(dist)

    print("\n" + "=" * 60)
    print("STORED V2 ARCHETYPE DISTRIBUTION")
    print("=" * 60)
    print("\n  Tier 1 (Foundational):")
    for arch in tier1:
        print(f"    {arch:25s}: {counts.get(arch, 0):3d}")
    print("\n  Tier 2a (POWER subtypes):")
    for arch in tier2_power:
        print(f"    {arch:25s}: {counts.get(arch, 0):3d}")
    print("\n  Tier 2b (RELIGIOUS subtypes):")
    for arch in tier2_religious:
        print(f"    {arch:25s}: {counts.get(arch, 0):3d}")
    print("\n  Tier 3 (Contextual):")
    for arch in tier3:
        print(f"    {arch:25s}: {counts.get(arch, 0):3d}")
    print(f"\n  {'TOTAL':25s}: {sum(counts.values()):3d}")

    # Unclassified
    cursor.execute("SELECT COUNT(*) FROM dream_reflections WHERE primary_archetype_v2 IS NULL")
    unclassified = cursor.fetchone()[0]
    if unclassified:
        print(f"  {'UNCLASSIFIED':25s}: {unclassified:3d}")
    conn.close()


def main():
    parser = argparse.ArgumentParser(description='Archetype Taxonomy v2 Analysis')
    parser.add_argument('--analyze', action='store_true', help='Show distribution analysis')
    parser.add_argument('--compare', action='store_true', help='Show v1 vs v2 comparison')
    parser.add_argument('--backfill', action='store_true', help='Persist v2 classifications to DB')
    args = parser.parse_args()

    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        sys.exit(1)

    print("🔮 Archetype Taxonomy v2 Analysis")
    print(f"Database: {DB_PATH}\n")

    if args.backfill:
        backfill_v2()
        analyze_stored_v2_distribution()

    if args.analyze or not (args.analyze or args.compare or args.backfill):
        analyze_current_distribution()
        project_v2_distribution()

    if args.compare:
        compare_v1_v2()

    print("\n" + "=" * 60)
    print("Analysis complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
