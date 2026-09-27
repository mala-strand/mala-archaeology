#!/usr/bin/env python3
"""
Quick analysis: Do structural parameters (temperature, jump count) predict
archetype outcomes better than seed semantics?

Runs correlation and entropy analysis on the dream corpus.
"""
import sqlite3
import numpy as np
from collections import defaultdict, Counter
from scipy.stats import entropy as scipy_entropy
from phase1_config import DB_PATH

conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

cursor.execute("""
    SELECT d.seed_word, d.temperature, d.jump_count,
           dr.primary_archetype_v2, dr.confidence_tier
    FROM dreams d
    JOIN dream_reflections dr ON d.id = dr.dream_id
    WHERE d.seed_word NOT LIKE 'RANDOM_%'
      AND dr.primary_archetype_v2 IS NOT NULL
      AND dr.primary_archetype_v2 != 'unclassifiable'
""")
rows = cursor.fetchall()

# Group by seed
seed_data = defaultdict(list)
for seed, temp, jumps, archetype, conf in rows:
    seed_data[seed].append({
        'temp': temp, 'jumps': jumps,
        'archetype': archetype, 'conf': conf
    })

# Overall stats
temps = [r['temp'] for r in [item for sublist in seed_data.values() for item in sublist]]
jump_counts = [r['jumps'] for r in [item for sublist in seed_data.values() for item in sublist]]

print("STRUCTURAL PARAMETERS VS ARCHETYPE DIVERSITY")
print("=" * 70)
print(f"Total dreams analyzed: {len(rows)}")
print(f"Unique seeds: {len(seed_data)}")
print(f"Temperature range: {min(temps):.1f} – {max(temps):.1f}")
print(f"Jump count range: {min(jump_counts)} – {max(jump_counts)}")

# For seeds with multiple dreams, compute archetype diversity
print("\nPER-SEED ARCHETYPE DIVERSITY")
print("-" * 70)
print(f"{'Seed':<15} {'Temps':<12} {'Archetypes':<30} {'Entropy':<8}")
print("-" * 70)

diversities = []
for seed in sorted(seed_data.keys()):
    dreams = seed_data[seed]
    if len(dreams) < 2:
        continue
    temps_s = ", ".join(f"{d['temp']:.1f}" for d in dreams)
    archetypes = [d['archetype'] for d in dreams]
    counts = Counter(archetypes)
    archetype_str = ", ".join(f"{a}({c})" for a, c in counts.most_common())
    # Shannon entropy of archetype distribution
    probs = np.array(list(counts.values())) / len(archetypes)
    H = scipy_entropy(probs, base=2)
    diversities.append({
        'seed': seed, 'n': len(dreams), 'entropy': H,
        'temp_range': max(d['temp'] for d in dreams) - min(d['temp'] for d in dreams)
    })
    print(f"{seed:<15} {temps_s:<12} {archetype_str:<30} {H:.2f}")

if diversities:
    entropies = [d['entropy'] for d in diversities]
    temp_ranges = [d['temp_range'] for d in diversities]

    print(f"\nMean entropy: {np.mean(entropies):.2f} (±{np.std(entropies):.2f})")
    print(f"Max entropy:  {np.max(entropies):.2f}")

    # Correlation: temperature range vs entropy
    if len(entropies) > 2:
        r_temp = np.corrcoef(temp_ranges, entropies)[0, 1]
        print(f"\nCorrelation (temp_range vs archetype_entropy): r = {r_temp:+.3f}")

# Global: temperature vs archetype
print("\n" + "=" * 70)
print("GLOBAL: TEMPERATURE BINS VS ARCHETYPE DISTRIBUTION")
print("=" * 70)

bins = [(0.8, 1.0), (1.0, 1.2), (1.2, 1.4), (1.4, 1.6), (1.6, 2.1)]
for lo, hi in bins:
    subset = [r for r in rows if lo <= r[1] < hi]
    if not subset:
        continue
    archetypes = [r[3] for r in subset]
    counts = Counter(archetypes)
    top3 = counts.most_common(3)
    top3_str = ", ".join(f"{a}({c})" for a, c in top3)
    print(f"Temp {lo:.1f}–{hi:.1f}: {len(subset):3d} dreams | Top 3: {top3_str}")

conn.close()
