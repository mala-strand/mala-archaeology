#!/usr/bin/env python3
"""
Neighbour Presence Test

Narrower claim: Dreams at higher temperature contain more words from the seed's
top neighbour set. This tests whether high-temperature walks escape into
neighbour territory (the gravity-well rim) rather than staying near the seed.
"""
import sys
import sqlite3
import numpy as np
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, ERA_ORDER
from dream import load_all_vectors, cosine_similarity
from archetype_taxonomy_v2 import extract_words_from_dream

TOP_N = 20

def get_top_neighbours(seed, era, vectors, words_by_era, n=TOP_N):
    if seed not in vectors.get(era, {}):
        return set()
    seed_vec = vectors[era][seed]
    sims = []
    for w in words_by_era.get(era, []):
        if w == seed:
            continue
        sim = cosine_similarity(seed_vec, vectors[era][w])
        sims.append((w, sim))
    sims.sort(key=lambda x: x[1], reverse=True)
    return set(w for w, _ in sims[:n])


def main():
    conn = sqlite3.connect(str(DB_PATH))
    vectors, words_by_era = load_all_vectors(conn)

    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.id, d.seed_word, d.temperature, d.dream_text
        FROM dreams d
        WHERE d.seed_word NOT LIKE 'RANDOM_%'
        ORDER BY d.seed_word, d.temperature
    """)
    rows = cursor.fetchall()

    print("Neighbour Presence Test")
    print("=" * 80)
    print(f"{'Seed':<15} {'Temp':>6} {'Neigh%':>8} {'Unique':>6} {'InNeigh':>8}")
    print("-" * 80)

    by_seed = defaultdict(list)
    for dream_id, seed, temp, text in rows:
        words = extract_words_from_dream(text)
        unique_words = set(words)

        # Build neighbour set for this seed (across all eras)
        neighbour_set = set()
        for era in ERA_ORDER:
            neighbour_set |= get_top_neighbours(seed, era, vectors, words_by_era, n=TOP_N)

        in_neigh = unique_words.intersection(neighbour_set)
        pct = (len(in_neigh) / len(unique_words) * 100) if unique_words else 0

        by_seed[seed].append({'temp': temp, 'pct': pct, 'unique': len(unique_words), 'in_neigh': len(in_neigh)})
        print(f"{seed:<15} {temp:>6.1f} {pct:>7.1f}% {len(unique_words):>6} {len(in_neigh):>8}")

    print("-" * 80)
    print("\nCorrelation (temperature vs neighbour presence) per seed:")
    for seed in sorted(by_seed.keys()):
        temps = [d['temp'] for d in by_seed[seed]]
        pcts = [d['pct'] for d in by_seed[seed]]
        if len(temps) > 1:
            corr = np.corrcoef(temps, pcts)[0, 1]
            print(f"  {seed:<15} r = {corr:+.3f}  (n={len(temps)})")

    conn.close()


if __name__ == "__main__":
    main()
