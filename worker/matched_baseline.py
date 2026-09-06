#!/usr/bin/env python3
"""Matched-pair baseline: same params, real vs random vectors."""
import sqlite3
import numpy as np
import sys
from statistics import mean, stdev
sys.path.insert(0, '/mnt/nas/mala/work/archaeology/worker')
from phase1_config import DB_PATH
from baseline_comparison import load_all_vectors, make_random_vectors, generate_dream_with_vectors

conn = sqlite3.connect(str(DB_PATH))
real_vectors, words_by_era = load_all_vectors(conn)
random_vectors = make_random_vectors(real_vectors, dim=50, seed=42)

cursor = conn.cursor()
cursor.execute("""
    SELECT seed_word, start_era, temperature, era_jump_prob, length, jump_count, unique_words
    FROM dreams
    WHERE seed_word NOT LIKE 'RANDOM_%'
    ORDER BY RANDOM()
    LIMIT 53
""")
real_params = cursor.fetchall()

print("Matched-pair comparison: same params, real vs random vectors")
print("=" * 70)
print(f"{'Seed':<15} {'Era':<14} {'T':>4} {'RealJ':>6} {'RandJ':>6} {'Delta':>6} {'RealU':>6} {'RandU':>6}")
print("-" * 70)

real_jumps, rand_jumps, real_unique, rand_unique = [], [], [], []
for seed, era, temp, ej_prob, length, rj, ru in real_params:
    text, unique, jumps = generate_dream_with_vectors(
        conn, random_vectors, words_by_era,
        seed=seed, start_era=era, length=length,
        temperature=temp, era_jump_prob=ej_prob,
    )
    real_jumps.append(rj); rand_jumps.append(jumps)
    real_unique.append(ru); rand_unique.append(unique)
    print(f"{seed:<15} {era:<14} {temp:>4.1f} {rj:>6} {jumps:>6} {jumps-rj:>+6} {ru:>6} {unique:>6}")

print("-" * 70)
print(f"{'MEAN':<15} {'':<14} {'':>4} {np.mean(real_jumps):>6.1f} {np.mean(rand_jumps):>6.1f} {np.mean(rand_jumps)-np.mean(real_jumps):>+6.1f} {np.mean(real_unique):>6.1f} {np.mean(rand_unique):>6.1f}")
print(f"{'STD':<15} {'':<14} {'':>4} {np.std(real_jumps):>6.1f} {np.std(rand_jumps):>6.1f} {'':>6} {np.std(real_unique):>6.1f} {np.std(rand_unique):>6.1f}")

diffs = [r - rand_jumps[i] for i, r in enumerate(real_jumps)]
d_mean = mean(diffs)
d_std = stdev(diffs) if len(diffs) > 1 else 0
n = len(diffs)
t_stat = d_mean / (d_std / (n ** 0.5)) if d_std > 0 else 0
print(f"\nPaired difference (real - random) jumps: {d_mean:+.1f} ± {d_std:.1f}")
print(f"t-statistic (approx): {t_stat:.2f} (n={n})")

conn.close()
