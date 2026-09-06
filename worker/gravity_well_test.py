#!/usr/bin/env python3
"""
Gravity-Well Prediction Test

Tests the claim from §4.1: for a given seed, the set of archetypes reachable
at high temperature should be predictable from the seed's top non-seed neighbours
across all eras.

Operationalization:
1. For each seed, collect its top N neighbours in each era.
2. Classify the concatenated neighbour words as a pseudo-dream -> "neighbour archetype profile".
3. Fetch all actual dreams for that seed.
4. Compare: is the dream's primary archetype in the neighbour profile's top 5?
"""
import sys
import sqlite3
import json
import numpy as np
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, ERA_ORDER
from dream import load_all_vectors, cosine_similarity
from archetype_taxonomy_v2 import classify_with_v2

TOP_N = 20

def get_top_neighbours(seed, era, vectors, words_by_era, n=TOP_N):
    """Return top n neighbour words (excluding seed) for a seed in an era."""
    if seed not in vectors.get(era, {}):
        return []
    seed_vec = vectors[era][seed]
    sims = []
    for w in words_by_era.get(era, []):
        if w == seed:
            continue
        sim = cosine_similarity(seed_vec, vectors[era][w])
        sims.append((w, sim))
    sims.sort(key=lambda x: x[1], reverse=True)
    return [w for w, _ in sims[:n]]


def main():
    conn = sqlite3.connect(str(DB_PATH))
    vectors, words_by_era = load_all_vectors(conn)

    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.id, d.seed_word, d.start_era, d.temperature, d.jump_count,
               dr.primary_archetype_v2, dr.secondary_archetype_v2
        FROM dreams d
        JOIN dream_reflections dr ON d.id = dr.dream_id
        WHERE d.seed_word NOT LIKE 'RANDOM_%'
        ORDER BY d.seed_word, d.temperature
    """)
    rows = cursor.fetchall()

    dreams_by_seed = defaultdict(list)
    for row in rows:
        dream_id, seed, era, temp, jumps, pri, sec = row
        dreams_by_seed[seed].append({
            'id': dream_id, 'era': era, 'temp': temp, 'jumps': jumps,
            'primary': pri, 'secondary': sec
        })

    print("Gravity-Well Prediction Test")
    print("=" * 90)
    print(f"{'Seed':<15} {'NeighbourProfile':<22} {'Dreams (temp → archetype)':<50}")
    print("-" * 90)

    total_classifiable = 0
    soft_matches = 0
    multi_temp_seeds = 0
    multi_temp_matches = 0

    for seed in sorted(dreams_by_seed.keys()):
        dreams = dreams_by_seed[seed]

        all_neighbours = []
        for era in ERA_ORDER:
            neighbours = get_top_neighbours(seed, era, vectors, words_by_era, n=TOP_N)
            all_neighbours.extend(neighbours)

        if not all_neighbours:
            continue

        neigh_class = classify_with_v2(all_neighbours, seed_word=seed)
        neigh_pri = neigh_class['primary'][0]
        neigh_top5 = [a for a, _ in neigh_class['top_5']]

        dream_parts = []
        for d in dreams:
            label = d['primary'] if d['primary'] else 'unclassifiable'
            dream_parts.append(f"T{d['temp']:.1f}→{label}")
        dream_summary = ", ".join(dream_parts)

        print(f"{seed:<15} {neigh_pri:<22} {dream_summary:<50}")

        # Soft match: dream primary in neighbour top-5
        for d in dreams:
            if d['primary'] and d['primary'] != 'unclassifiable':
                total_classifiable += 1
                if d['primary'] in neigh_top5:
                    soft_matches += 1

        # Multi-temperature: does high-temp dream match neighbour profile?
        if len(dreams) > 1:
            multi_temp_seeds += 1
            high_temps = [d for d in dreams if d['temp'] >= 1.4 and d['primary'] and d['primary'] != 'unclassifiable']
            matched = False
            for d in high_temps:
                if d['primary'] in neigh_top5 or (d['secondary'] and d['secondary'] in neigh_top5):
                    matched = True
                    break
            if matched:
                multi_temp_matches += 1

    print("-" * 90)
    print(f"\nAll classifiable dreams: {total_classifiable}")
    print(f"Soft matches (dream primary in neighbour top-5): {soft_matches}")
    if total_classifiable > 0:
        print(f"Soft match rate: {soft_matches/total_classifiable:.1%}")

    print(f"\nMulti-temperature seeds: {multi_temp_seeds}")
    print(f"High-temp dreams matching neighbour profile: {multi_temp_matches}")
    if multi_temp_seeds > 0:
        print(f"High-temp match rate: {multi_temp_matches/multi_temp_seeds:.1%}")

    conn.close()


if __name__ == "__main__":
    main()
