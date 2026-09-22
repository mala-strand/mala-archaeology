#!/usr/bin/env python3
"""
Basin-vs-Rim Test

Extends gravity_well_test.py to compare prediction accuracy at different
neighbourhood scales: top-20 (rim), top-100 (mid-basin), top-200 (deep-basin).

Hypothesis: if the "gravity well" effect is real, prediction accuracy should
increase as we include more neighbours — the seed's "basin" of semantic
attraction is larger than its immediate rim.

Null expectation (no gravity well): accuracy stays flat or drops as noise
increases with larger neighbour sets.
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

SCALES = [20, 100, 200]

def get_top_neighbours(seed, era, vectors, words_by_era, n=20):
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
        SELECT d.id, d.seed_word, d.temperature, d.jump_count,
               dr.primary_archetype_v2, dr.secondary_archetype_v2
        FROM dreams d
        JOIN dream_reflections dr ON d.id = dr.dream_id
        WHERE d.seed_word NOT LIKE 'RANDOM_%'
        ORDER BY d.seed_word, d.temperature
    """)
    rows = cursor.fetchall()

    dreams_by_seed = defaultdict(list)
    for row in rows:
        dream_id, seed, temp, jumps, pri, sec = row
        dreams_by_seed[seed].append({
            'id': dream_id, 'temp': temp, 'jumps': jumps,
            'primary': pri, 'secondary': sec
        })

    # Results storage: scale -> metric -> value
    results = {scale: {'total': 0, 'soft_matches': 0, 'multi_total': 0, 'multi_matches': 0}
               for scale in SCALES}
    seed_scale_matches = {scale: [] for scale in SCALES}  # per-seed match rates

    print("Basin-vs-Rim Test: Does prediction improve at larger neighbourhood scales?")
    print("=" * 100)
    header = f"{'Seed':<15}"
    for scale in SCALES:
        header += f" | {'Top-' + str(scale):<18}"
    header += " | Dreams"
    print(header)
    print("-" * 100)

    for seed in sorted(dreams_by_seed.keys()):
        dreams = dreams_by_seed[seed]

        scale_profiles = {}
        for scale in SCALES:
            all_neighbours = []
            for era in ERA_ORDER:
                neighbours = get_top_neighbours(seed, era, vectors, words_by_era, n=scale)
                all_neighbours.extend(neighbours)

            if not all_neighbours:
                scale_profiles[scale] = None
                continue

            neigh_class = classify_with_v2(all_neighbours, seed_word=seed)
            neigh_pri = neigh_class['primary'][0] if neigh_class['primary'] else 'unclassifiable'
            neigh_top5 = [a for a, _ in neigh_class['top_5']]
            scale_profiles[scale] = {
                'primary': neigh_pri,
                'top5': neigh_top5,
                'neighbour_count': len(all_neighbours)
            }

        dream_parts = []
        for d in dreams:
            label = d['primary'] if d['primary'] else 'unclassifiable'
            dream_parts.append(f"T{d['temp']:.1f}→{label}")
        dream_summary = ", ".join(dream_parts)

        row_str = f"{seed:<15}"
        for scale in SCALES:
            prof = scale_profiles.get(scale)
            if prof:
                row_str += f" | {prof['primary']:<18}"
            else:
                row_str += f" | {'(no vectors)':<18}"
        row_str += f" | {dream_summary}"
        print(row_str)

        # Per-scale metrics
        for scale in SCALES:
            prof = scale_profiles.get(scale)
            if not prof:
                continue

            seed_matches = 0
            seed_classifiable = 0
            for d in dreams:
                if d['primary'] and d['primary'] != 'unclassifiable':
                    seed_classifiable += 1
                    results[scale]['total'] += 1
                    if d['primary'] in prof['top5']:
                        results[scale]['soft_matches'] += 1
                        seed_matches += 1

            if seed_classifiable > 0:
                seed_scale_matches[scale].append(seed_matches / seed_classifiable)

            # Multi-temperature check
            if len(dreams) > 1:
                high_temps = [d for d in dreams if d['temp'] >= 1.4 and d['primary'] and d['primary'] != 'unclassifiable']
                matched = False
                for d in high_temps:
                    if d['primary'] in prof['top5'] or (d['secondary'] and d['secondary'] in prof['top5']):
                        matched = True
                        break
                results[scale]['multi_total'] += 1
                if matched:
                    results[scale]['multi_matches'] += 1

    print("-" * 100)

    print("\n📊 RESULTS BY SCALE")
    print("=" * 60)
    for scale in SCALES:
        r = results[scale]
        print(f"\nTop-{scale} neighbours:")
        if r['total'] > 0:
            rate = r['soft_matches'] / r['total']
            print(f"  Soft match rate:     {r['soft_matches']}/{r['total']} = {rate:.1%}")
        else:
            print(f"  Soft match rate:     N/A (no classifiable dreams)")

        if r['multi_total'] > 0:
            mrate = r['multi_matches'] / r['multi_total']
            print(f"  High-temp match rate: {r['multi_matches']}/{r['multi_total']} = {mrate:.1%}")
        else:
            print(f"  High-temp match rate: N/A")

        if seed_scale_matches[scale]:
            avg = np.mean(seed_scale_matches[scale])
            med = np.median(seed_scale_matches[scale])
            print(f"  Per-seed avg match:  {avg:.1%}")
            print(f"  Per-seed median:     {med:.1%}")

    print("\n📈 INTERPRETATION")
    print("=" * 60)
    rates = {scale: (results[scale]['soft_matches'] / results[scale]['total'])
             if results[scale]['total'] > 0 else 0
             for scale in SCALES}

    if rates[20] < rates[100] < rates[200]:
        print("TREND: Accuracy increases with scale (20 < 100 < 200)")
        print("IMPLICATION: The gravity well has BASIN structure — predictive")
        print("             signal exists beyond the immediate rim.")
    elif rates[20] > rates[100] > rates[200]:
        print("TREND: Accuracy decreases with scale (20 > 100 > 200)")
        print("IMPLICATION: Noise dominates beyond the rim — top-20 is optimal.")
    elif rates[100] > rates[20] and rates[100] > rates[200]:
        print("TREND: Mid-scale (100) is optimal")
        print("IMPLICATION: Basin has a sweet spot — too few misses structure,")
        print("             too many drowns in noise.")
    else:
        print("TREND: Flat or non-monotonic")
        print("IMPLICATION: No clear basin structure, or effect is seed-dependent.")

    # Statistical note
    print(f"\n📝 NOTES")
    print(f"  - Top-20 uses {6 * 20} words max (20 per era × 6 eras)")
    print(f"  - Top-100 uses {6 * 100} words max")
    print(f"  - Top-200 uses {6 * 200} words max")
    print(f"  - Vocabulary size: ~8,121 words")
    print(f"  - All scales sample from the same 6-era vector space")

    conn.close()


if __name__ == "__main__":
    main()
