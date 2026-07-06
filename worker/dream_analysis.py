#!/usr/bin/env python3
"""
Dream analysis tool - cross-dream pattern analysis
Finds correlations and patterns across the dream corpus
"""

import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "archaeology_phase1_clean.db"

def connect():
    return sqlite3.connect(DB_PATH)

def analyze_jump_archetype_correlation():
    """Analyze if high-jump dreams correlate with specific archetypes"""
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT d.jump_count, dr.primary_archetype, dr.secondary_archetype
        FROM dreams d
        JOIN dream_reflections dr ON d.id = dr.dream_id
        ORDER BY d.jump_count DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    # Group by jump count ranges
    ranges = {
        'low (0-15)': [],
        'medium (16-30)': [],
        'high (31-45)': [],
        'extreme (46+)': []
    }
    
    for jumps, primary, secondary in rows:
        if jumps <= 15:
            ranges['low (0-15)'].append((primary, secondary))
        elif jumps <= 30:
            ranges['medium (16-30)'].append((primary, secondary))
        elif jumps <= 45:
            ranges['high (31-45)'].append((primary, secondary))
        else:
            ranges['extreme (46+)'].append((primary, secondary))
    
    print("=" * 60)
    print("JUMP COUNT vs ARCHETYPE CORRELATION")
    print("=" * 60)
    
    for range_name, archetypes in ranges.items():
        if not archetypes:
            continue
        primary_counts = Counter([a[0] for a in archetypes])
        print(f"\n{range_name}: {len(archetypes)} dreams")
        print(f"  Primary archetypes: {dict(primary_counts.most_common(3))}")

def analyze_era_distribution_patterns():
    """Find which eras dominate dreams and what archetypes they produce"""
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT d.id, d.seed_word, d.start_era, dr.primary_archetype,
               d.dream_text
        FROM dreams d
        JOIN dream_reflections dr ON d.id = dr.dream_id
        GROUP BY d.id
        ORDER BY d.id DESC
        LIMIT 20
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    print("\n" + "=" * 60)
    print("ERA DISTRIBUTION PATTERNS (Last 20 Dreams)")
    print("=" * 60)
    
    # Count words per era by looking at jump markers in dream text
    era_word_counts = defaultdict(lambda: defaultdict(int))
    
    for dream_id, seed, start_era, archetype, text in rows:
        lines = text.split('\n')
        current_era = start_era
        
        for line in lines:
            line = line.strip()
            if line.startswith('[') and '→' in line:
                # Parse era jump
                parts = line.strip('[]').split('→')
                if len(parts) == 2:
                    current_era = parts[1].strip()
            elif line and not line.startswith('Seed:') and not line.startswith('Temperature:') and not line.startswith('─'):
                words = line.split()
                era_word_counts[current_era][archetype] += len(words)
    
    print("\nWords per era by archetype:")
    for era in sorted(era_word_counts.keys()):
        print(f"\n  {era}:")
        for archetype, count in sorted(era_word_counts[era].items(), key=lambda x: -x[1])[:3]:
            print(f"    {archetype}: {count} words")

def analyze_seed_word_patterns():
    """Analyze which seed words produce which archetypes"""
    conn = connect()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT d.seed_word, dr.primary_archetype, COUNT(*) as count
        FROM dreams d
        JOIN dream_reflections dr ON d.id = dr.dream_id
        GROUP BY d.seed_word, dr.primary_archetype
        ORDER BY d.seed_word, count DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    print("\n" + "=" * 60)
    print("SEED WORD vs ARCHETYPE PATTERNS")
    print("=" * 60)
    
    seed_archetypes = defaultdict(list)
    for seed, archetype, count in rows:
        seed_archetypes[seed].append((archetype, count))
    
    for seed in sorted(seed_archetypes.keys()):
        archetypes = seed_archetypes[seed]
        total = sum(c for _, c in archetypes)
        print(f"\n  '{seed}' ({total} reflections):")
        for archetype, count in archetypes[:3]:
            pct = count / total * 100
            print(f"    → {archetype}: {count} ({pct:.0f}%)")

def find_extreme_dreams():
    """Find dreams with interesting extreme properties"""
    conn = connect()
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("EXTREME DREAMS")
    print("=" * 60)
    
    # Most jumps
    cursor.execute("""
        SELECT id, seed_word, jump_count, start_era 
        FROM dreams 
        ORDER BY jump_count DESC 
        LIMIT 3
    """)
    print("\n  Most jumps:")
    for dream_id, seed, jumps, era in cursor.fetchall():
        print(f"    Dream #{dream_id}: '{seed}' ({era}) — {jumps} jumps")
    
    # Fewest jumps
    cursor.execute("""
        SELECT id, seed_word, jump_count, start_era 
        FROM dreams 
        ORDER BY jump_count ASC 
        LIMIT 3
    """)
    print("\n  Fewest jumps:")
    for dream_id, seed, jumps, era in cursor.fetchall():
        print(f"    Dream #{dream_id}: '{seed}' ({era}) — {jumps} jumps")
    
    # Highest unique word ratio
    cursor.execute("""
        SELECT d.id, d.seed_word, d.unique_words, d.length,
               CAST(d.unique_words AS FLOAT) / d.length as ratio
        FROM dreams d
        ORDER BY ratio DESC
        LIMIT 3
    """)
    print("\n  Highest lexical diversity:")
    for dream_id, seed, unique, length, ratio in cursor.fetchall():
        pct = ratio * 100
        print(f"    Dream #{dream_id}: '{seed}' — {unique}/{length} ({pct:.1f}% unique)")
    
    conn.close()

def main():
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        sys.exit(1)
    
    print("\n🔮 Dream Corpus Analysis")
    print(f"Database: {DB_PATH}")
    
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM dreams")
    dream_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM dream_reflections")
    reflection_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"Dreams: {dream_count} | Reflections: {reflection_count}\n")
    
    analyze_jump_archetype_correlation()
    analyze_seed_word_patterns()
    find_extreme_dreams()
    
    print("\n" + "=" * 60)
    print("Analysis complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
