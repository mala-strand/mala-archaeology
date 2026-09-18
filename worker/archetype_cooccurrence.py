#!/usr/bin/env python3
"""
Archetype Co-occurrence Analysis

Analyzes which archetypes appear together in the same dream
(via primary + secondary pairings) and which never co-occur.

Also analyzes drift-type × archetype crosstabs.
"""

import sqlite3
import statistics
import math
from pathlib import Path
from collections import Counter, defaultdict

DB_PATH = Path(__file__).parent.parent / "data" / "archaeology_phase1_clean.db"

def get_latest_reflections():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT d.id, d.seed_word, d.temperature, d.jump_count,
               dr.idf_hybrid_primary, dr.idf_hybrid_secondary, dr.idf_hybrid_method
        FROM dreams d
        LEFT JOIN (
            SELECT dream_id, idf_hybrid_primary, idf_hybrid_secondary, idf_hybrid_method,
                   ROW_NUMBER() OVER (PARTITION BY dream_id ORDER BY id DESC) as rn
            FROM dream_reflections
        ) dr ON d.id = dr.dream_id AND dr.rn = 1
        ORDER BY d.id
    """)
    
    dreams = []
    for row in cursor.fetchall():
        dreams.append({
            'id': row[0],
            'seed': row[1],
            'temp': row[2],
            'jumps': row[3] or 0,
            'primary': row[4] or 'unclassifiable',
            'secondary': row[5],
            'method': row[6] or 'unknown',
        })
    
    conn.close()
    return dreams

def analyze_cooccurrence(dreams):
    print("=" * 70)
    print("ARCHETYPE CO-OCCURRENCE ANALYSIS (n=%d)" % len(dreams))
    print("=" * 70)
    print()
    
    # Build primary-only distribution
    primary_counts = Counter(d['primary'] for d in dreams)
    print("PRIMARY ARCHETYPE DISTRIBUTION")
    print("-" * 70)
    total = len(dreams)
    for arch, count in primary_counts.most_common():
        pct = count / total * 100
        bar = "█" * int(pct / 2)
        print(f"  {arch:<22} {count:>4} ({pct:>5.1f}%) {bar}")
    
    print()
    
    # Co-occurrence: primary + secondary pairs
    pairs = Counter()
    single = Counter()
    for d in dreams:
        p = d['primary']
        s = d['secondary']
        if s and s != p:
            pairs[(p, s)] += 1
        else:
            single[p] += 1
    
    print("PRIMARY + SECONDARY PAIRS (co-occurring archetypes)")
    print("-" * 70)
    print(f"{'Pair':<50} {'Count':>6}")
    for (p, s), count in pairs.most_common(20):
        print(f"  {p:<22} + {s:<22} {count:>4}")
    
    print()
    
    # Archetypes that NEVER appear as secondary
    all_primary = set(d['primary'] for d in dreams)
    all_secondary = set(d['secondary'] for d in dreams if d['secondary'])
    never_secondary = all_primary - all_secondary
    
    print("ARCHETYPES NEVER SEEN AS SECONDARY")
    print("-" * 70)
    if never_secondary:
        for arch in sorted(never_secondary):
            print(f"  {arch} (appears as primary {primary_counts.get(arch, 0)} times)")
    else:
        print("  All archetypes have appeared as secondary at least once.")
    
    print()
    
    # Forbidden pairs: which combinations never happen?
    print("FORBIDDEN PAIRS (never co-occur, primary+secondary)")
    print("-" * 70)
    
    all_archetypes = sorted(all_primary | all_secondary)
    existing_pairs = set(pairs.keys()) | set((p, p) for p in all_primary)
    
    forbidden = []
    for a in all_archetypes:
        for b in all_archetypes:
            if a == b:
                continue
            if (a, b) not in existing_pairs and (b, a) not in existing_pairs:
                # Only report each unordered pair once
                if (b, a) not in forbidden:
                    forbidden.append((a, b))
    
    # Filter to pairs where both archetypes actually appear in corpus
    active = set(all_primary)
    forbidden = [(a, b) for a, b in forbidden if a in active and b in active]
    
    print(f"Total unordered forbidden pairs: {len(forbidden)}")
    print(f"Total possible unordered pairs: {math.comb(len(active), 2)}")
    print()
    
    # Show some examples
    shown = 0
    for a, b in sorted(forbidden):
        a_count = primary_counts.get(a, 0)
        b_count = primary_counts.get(b, 0)
        if a_count >= 3 and b_count >= 3 and shown < 15:
            print(f"  {a:<22} + {b:<22} (counts: {a_count} + {b_count})")
            shown += 1
    
    if shown == 0:
        print("  (No forbidden pairs where both archetypes appear ≥3 times)")
    
    print()
    
    # Jump count by archetype
    print("JUMP COUNT BY ARCHETYPE")
    print("-" * 70)
    arch_jumps = defaultdict(list)
    for d in dreams:
        arch_jumps[d['primary']].append(d['jumps'])
    
    print(f"{'Archetype':<22} {'N':>4} {'Mean':>6} {'Std':>6} {'Max':>4}")
    for arch in sorted(arch_jumps.keys(), key=lambda a: -statistics.mean(arch_jumps[a])):
        jumps = arch_jumps[arch]
        print(f"  {arch:<22} {len(jumps):>4} {statistics.mean(jumps):>6.1f} {statistics.stdev(jumps) if len(jumps) > 1 else 0:>6.1f} {max(jumps):>4}")
    
    print()
    
    # Temperature by archetype
    print("TEMPERATURE BY ARCHETYPE")
    print("-" * 70)
    arch_temps = defaultdict(list)
    for d in dreams:
        arch_temps[d['primary']].append(d['temp'])
    
    print(f"{'Archetype':<22} {'N':>4} {'Mean':>6} {'Std':>6}")
    for arch in sorted(arch_temps.keys(), key=lambda a: -statistics.mean(arch_temps[a])):
        temps = arch_temps[arch]
        print(f"  {arch:<22} {len(temps):>4} {statistics.mean(temps):>6.2f} {statistics.stdev(temps) if len(temps) > 1 else 0:>6.2f}")
    
    print()
    
    # Method distribution
    print("CLASSIFICATION METHOD DISTRIBUTION")
    print("-" * 70)
    method_counts = Counter(d['method'] for d in dreams)
    for method, count in method_counts.most_common():
        pct = count / total * 100
        print(f"  {method:<22} {count:>4} ({pct:>5.1f}%)")
    
    print()

def main():
    dreams = get_latest_reflections()
    if not dreams:
        print("No dreams found.")
        return
    
    analyze_cooccurrence(dreams)
    
    print("=" * 70)
    print("Analysis complete.")
    print("=" * 70)

if __name__ == "__main__":
    main()
