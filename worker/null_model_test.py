#!/usr/bin/env python3
"""
Null-Model Test for Gravity-Well Prediction

Tests whether the gravity-well effect (seed's neighbours predict dream archetype)
is statistically distinguishable from chance.

Null hypothesis: Any seed's neighbour profile predicts any seed's dreams equally well.
If the observed accuracy is significantly higher than random-seed assignment,
the gravity-well effect is real.

Three null models:
1. RANDOM-SEED: For each seed's dreams, use a randomly chosen other seed's
   neighbour profile. Preserves structural properties, breaks seed-specific link.
2. SHUFFLED-VECTOR: Randomly permute word-to-vector assignments, recompute
   neighbours. Tests whether semantic structure is necessary.
3. RANDOM-WORDS: Instead of top-N neighbours, sample N random vocabulary words.
   Tests whether any word set works (weakest null).

Usage:
    python3 null_model_test.py [--iterations N] [--scales 20,100,200]
"""
import sys
import sqlite3
import argparse
import random
import numpy as np
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, ERA_ORDER
from dream import load_all_vectors, cosine_similarity
from archetype_taxonomy_v2 import classify_with_v2

DEFAULT_ITERATIONS = 1000
DEFAULT_SCALES = [20, 100, 200]


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


def compute_neighbour_profile(seed, vectors, words_by_era, scale):
    """Compute archetype profile for a seed's top-N neighbours across all eras."""
    all_neighbours = []
    for era in ERA_ORDER:
        neighbours = get_top_neighbours(seed, era, vectors, words_by_era, n=scale)
        all_neighbours.extend(neighbours)
    if not all_neighbours:
        return None
    neigh_class = classify_with_v2(all_neighbours, seed_word=seed)
    return {
        'primary': neigh_class['primary'][0] if neigh_class['primary'] else 'unclassifiable',
        'top5': [a for a, _ in neigh_class['top_5']],
    }


def compute_accuracy(dreams_by_seed, profiles, scale):
    """
    Compute soft-match accuracy: fraction of classifiable dreams whose
    primary archetype appears in their seed's neighbour-profile top-5.
    """
    total = 0
    matches = 0
    for seed, dreams in dreams_by_seed.items():
        prof = profiles.get(seed)
        if not prof:
            continue
        for d in dreams:
            pri = d['primary']
            if pri and pri != 'unclassifiable':
                total += 1
                if pri in prof['top5']:
                    matches += 1
    if total == 0:
        return 0.0, 0
    return matches / total, total


def random_seed_null(dreams_by_seed, profiles, scale, iterations=1000):
    """
    Null model 1: Random-seed assignment.
    For each iteration, randomly reassign which seed's profile predicts which seed's dreams.
    """
    seeds = list(dreams_by_seed.keys())
    null_accuracies = []

    for _ in range(iterations):
        # Create random permutation: each seed gets another seed's profile
        shuffled = seeds.copy()
        random.shuffle(shuffled)
        random_profiles = {real: profiles.get(shuffled[i]) for i, real in enumerate(seeds)}

        acc, _ = compute_accuracy(dreams_by_seed, random_profiles, scale)
        null_accuracies.append(acc)

    return np.array(null_accuracies)


def shuffled_vector_null(dreams_by_seed, vectors, words_by_era, scale, iterations=100):
    """
    Null model 2: Shuffled-vector assignment.
    Randomly permute word-to-vector mapping, recompute neighbours, classify.
    More expensive — limited iterations.
    """
    all_words = list(vectors[ERA_ORDER[0]].keys())
    null_accuracies = []

    for _ in range(iterations):
        # Build shuffled vectors: keep same set of vectors, randomly reassign to words
        shuffled_vectors = {}
        for era in ERA_ORDER:
            era_words = list(vectors[era].keys())
            era_vecs = list(vectors[era].values())
            shuffled = era_vecs.copy()
            random.shuffle(shuffled)
            shuffled_vectors[era] = {w: shuffled[i] for i, w in enumerate(era_words)}

        # Recompute profiles with shuffled vectors
        shuffled_profiles = {}
        for seed in dreams_by_seed.keys():
            prof = compute_neighbour_profile(seed, shuffled_vectors, words_by_era, scale)
            if prof:
                shuffled_profiles[seed] = prof

        acc, _ = compute_accuracy(dreams_by_seed, shuffled_profiles, scale)
        null_accuracies.append(acc)

    return np.array(null_accuracies)


def random_words_null(dreams_by_seed, all_vocab_words, scale, iterations=1000):
    """
    Null model 3: Random-word sampling.
    Instead of top-N neighbours, sample N*6 random words from vocabulary.
    """
    null_accuracies = []
    sample_size = scale * len(ERA_ORDER)

    for _ in range(iterations):
        random_profiles = {}
        for seed in dreams_by_seed.keys():
            sampled = random.sample(all_vocab_words, min(sample_size, len(all_vocab_words)))
            neigh_class = classify_with_v2(sampled, seed_word=seed)
            random_profiles[seed] = {
                'primary': neigh_class['primary'][0] if neigh_class['primary'] else 'unclassifiable',
                'top5': [a for a, _ in neigh_class['top_5']],
            }

        acc, _ = compute_accuracy(dreams_by_seed, random_profiles, scale)
        null_accuracies.append(acc)

    return np.array(null_accuracies)


def report_null_result(scale, actual_acc, actual_n, null_arr, model_name):
    """Print formatted null-model results."""
    null_mean = np.mean(null_arr)
    null_std = np.std(null_arr)
    null_median = np.median(null_arr)
    null_95 = np.percentile(null_arr, 95)
    null_99 = np.percentile(null_arr, 99)

    # Z-score and p-value (one-tailed: is actual > null?)
    if null_std > 0:
        z = (actual_acc - null_mean) / null_std
        p = np.mean(null_arr >= actual_acc)
    else:
        z = float('inf') if actual_acc > null_mean else float('-inf')
        p = 0.0 if actual_acc > null_mean else 1.0

    print(f"\n  {model_name}:")
    print(f"    Actual accuracy:      {actual_acc:.1%} ({actual_n} dreams)")
    print(f"    Null mean ± std:      {null_mean:.1%} ± {null_std:.1%}")
    print(f"    Null median:          {null_median:.1%}")
    print(f"    Null 95th percentile: {null_95:.1%}")
    print(f"    Null 99th percentile: {null_99:.1%}")
    print(f"    Z-score:              {z:+.2f}")
    print(f"    p-value (one-tailed): {p:.4f}")

    if p < 0.01:
        print(f"    ✅ SIGNIFICANT at α=0.01")
    elif p < 0.05:
        print(f"    ✅ SIGNIFICANT at α=0.05")
    else:
        print(f"    ❌ NOT SIGNIFICANT")

    return {
        'scale': scale,
        'model': model_name,
        'actual': actual_acc,
        'null_mean': null_mean,
        'null_std': null_std,
        'z': z,
        'p': p,
        'significant_05': p < 0.05,
        'significant_01': p < 0.01,
    }


def main():
    parser = argparse.ArgumentParser(description="Null-model test for gravity-well prediction")
    parser.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS,
                        help="Iterations for cheap null models (default 1000)")
    parser.add_argument("--scales", type=str, default="20,100,200",
                        help="Comma-separated neighbour scales (default 20,100,200)")
    parser.add_argument("--skip-shuffle", action="store_true",
                        help="Skip expensive shuffled-vector null model")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)

    scales = [int(s.strip()) for s in args.scales.split(",")]

    print("=" * 80)
    print("NULL-MODEL TEST FOR GRAVITY-WELL PREDICTION")
    print("=" * 80)
    print(f"Random seed: {args.seed}")
    print(f"Scales: {scales}")
    print(f"Cheap iterations: {args.iterations}")

    # Load data
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

    # Precompute actual neighbour profiles for all seeds at all scales
    print("\nPrecomputing neighbour profiles...")
    profiles_by_scale = {}
    for scale in scales:
        profiles = {}
        for seed in dreams_by_seed.keys():
            prof = compute_neighbour_profile(seed, vectors, words_by_era, scale)
            if prof:
                profiles[seed] = prof
        profiles_by_scale[scale] = profiles
        print(f"  Scale {scale}: {len(profiles)} seeds with profiles")

    # Vocabulary for random-words null
    all_vocab_words = list(vectors[ERA_ORDER[0]].keys())
    print(f"  Vocabulary size: {len(all_vocab_words)}")

    all_results = []

    for scale in scales:
        print("\n" + "=" * 80)
        print(f"SCALE: Top-{scale} neighbours")
        print("=" * 80)

        profiles = profiles_by_scale[scale]
        actual_acc, actual_n = compute_accuracy(dreams_by_seed, profiles, scale)
        print(f"\n  Actual accuracy: {actual_acc:.1%} ({actual_n} classifiable dreams)")

        # Null model 1: Random-seed
        print(f"\n  Running random-seed null ({args.iterations} iterations)...")
        null_random = random_seed_null(dreams_by_seed, profiles, scale, args.iterations)
        res = report_null_result(scale, actual_acc, actual_n, null_random, "Random-Seed Null")
        all_results.append(res)

        # Null model 3: Random-words
        print(f"\n  Running random-words null ({args.iterations} iterations)...")
        null_random_words = random_words_null(dreams_by_seed, all_vocab_words, scale, args.iterations)
        res = report_null_result(scale, actual_acc, actual_n, null_random_words, "Random-Words Null")
        all_results.append(res)

        # Null model 2: Shuffled-vector (expensive, skip if requested)
        if not args.skip_shuffle:
            shuffle_iters = min(args.iterations // 10, 100)
            print(f"\n  Running shuffled-vector null ({shuffle_iters} iterations)...")
            null_shuffled = shuffled_vector_null(dreams_by_seed, vectors, words_by_era, scale, shuffle_iters)
            res = report_null_result(scale, actual_acc, actual_n, null_shuffled, "Shuffled-Vector Null")
            all_results.append(res)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"\n{'Scale':<8} {'Null Model':<22} {'Actual':<8} {'Null Mean':<10} {'Z-Score':<10} {'p-value':<10} {'Sig?':<6}")
    print("-" * 80)
    for r in all_results:
        sig = "***" if r['significant_01'] else "**" if r['significant_05'] else "ns"
        print(f"{r['scale']:<8} {r['model']:<22} {r['actual']:<8.1%} {r['null_mean']:<10.1%} {r['z']:<+10.2f} {r['p']:<10.4f} {sig:<6}")

    print("\n*** = p < 0.01, ** = p < 0.05, ns = not significant")

    conn.close()


if __name__ == "__main__":
    main()
