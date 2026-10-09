#!/usr/bin/env python3
"""
Basin Reach Quantifier

For each archetype, computes the distribution of distances from dream seeds
to the archetype centroid. This quantifies the "gravitational radius" —
how far from the centroid can a seed be and still get pulled into the basin.

Usage:
    python3 worker/basin_reach.py [--plot]

Outputs:
    - Per-archetype statistics (count, max, median, mean, std)
    - Cross-archetype distance matrix (seed centroid vs other centroids)
    - Optional plot of distance distributions
"""

import sys
import json
import math
import sqlite3
import argparse
from pathlib import Path
from collections import defaultdict

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, ERA_ORDER
from archetype_taxonomy_v2 import ARCHETYPES_V2


def load_vectors(db_path):
    """Load all word vectors, return {word: mean_vector_across_eras}."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT word, era, vector_json FROM word_vectors")

    word_era_vecs = defaultdict(dict)
    for word, era, vec_json in cursor:
        vec = np.array(json.loads(vec_json), dtype=np.float32)
        word_era_vecs[word][era] = vec

    conn.close()

    # Average across eras for each word
    word_vecs = {}
    for word, era_dict in word_era_vecs.items():
        vecs = list(era_dict.values())
        mean_vec = np.mean(vecs, axis=0)
        norm = np.linalg.norm(mean_vec)
        if norm > 0:
            word_vecs[word] = mean_vec / norm
        else:
            word_vecs[word] = mean_vec

    return word_vecs


def build_centroids(word_vecs, archetypes):
    """Build centroid for each archetype from its keyword vectors."""
    centroids = {}
    missing = {}
    for arch, keywords in archetypes.items():
        vecs = []
        miss = 0
        for kw in keywords:
            if kw in word_vecs:
                vecs.append(word_vecs[kw])
            else:
                miss += 1
        if vecs:
            centroid = np.mean(vecs, axis=0)
            norm = np.linalg.norm(centroid)
            if norm > 0:
                centroid = centroid / norm
            centroids[arch] = centroid
        else:
            centroids[arch] = None
        missing[arch] = miss
    return centroids, missing


def cosine_distance(a, b):
    """Cosine distance between two unit vectors."""
    # Since vectors are normalized, cosine similarity = dot product
    return 1.0 - float(np.dot(a, b))


def load_dreams(db_path):
    """Load all dreams with their penalized_primary classification."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.id, d.seed_word, dr.penalized_primary
        FROM dreams d
        JOIN dream_reflections dr ON d.id = dr.dream_id
        WHERE dr.penalized_primary IS NOT NULL
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def compute_basin_reach(word_vecs, centroids, dreams):
    """Compute per-archetype distance statistics."""
    # Group dreams by archetype
    arch_dreams = defaultdict(list)
    for dream_id, seed_word, archetype in dreams:
        if seed_word in word_vecs and centroids.get(archetype) is not None:
            arch_dreams[archetype].append({
                'dream_id': dream_id,
                'seed_word': seed_word,
                'seed_vec': word_vecs[seed_word],
            })

    results = {}
    for arch, dream_list in sorted(arch_dreams.items()):
        centroid = centroids[arch]
        distances = []
        for d in dream_list:
            dist = cosine_distance(d['seed_vec'], centroid)
            distances.append(dist)

        distances = np.array(distances)
        results[arch] = {
            'count': int(len(distances)),
            'max_dist': float(np.max(distances)),
            'median_dist': float(np.median(distances)),
            'mean_dist': float(np.mean(distances)),
            'std_dist': float(np.std(distances)),
            'min_dist': float(np.min(distances)),
            'q25': float(np.percentile(distances, 25)),
            'q75': float(np.percentile(distances, 75)),
        }

    return results


def compute_cross_distances(word_vecs, centroids, dreams):
    """
    For each dream, compute distance from its seed to:
    - Its assigned archetype centroid
    - All other archetype centroids
    Report how often the assigned centroid is the nearest.
    """
    arch_list = sorted([a for a, c in centroids.items() if c is not None])

    correct = 0
    total = 0
    assignment_breakdown = defaultdict(lambda: {'correct': 0, 'total': 0})

    for dream_id, seed_word, assigned_arch in dreams:
        if seed_word not in word_vecs:
            continue
        if centroids.get(assigned_arch) is None:
            continue

        seed_vec = word_vecs[seed_word]
        dists = {}
        for arch in arch_list:
            dists[arch] = cosine_distance(seed_vec, centroids[arch])

        nearest = min(dists, key=dists.get)
        is_correct = (nearest == assigned_arch)

        correct += is_correct
        total += 1
        assignment_breakdown[assigned_arch]['total'] += 1
        if is_correct:
            assignment_breakdown[assigned_arch]['correct'] += 1

    return {
        'overall_accuracy': correct / total if total > 0 else 0,
        'total': total,
        'per_archetype': {
            arch: {
                'accuracy': info['correct'] / info['total'] if info['total'] > 0 else 0,
                'count': info['total']
            }
            for arch, info in sorted(assignment_breakdown.items())
        }
    }


def print_report(results, cross_results, missing):
    print("=" * 70)
    print("BASIN REACH ANALYSIS")
    print("=" * 70)
    print(f"\nOverall centroid-nearest accuracy: {cross_results['overall_accuracy']:.1%} (n={cross_results['total']})")
    print("\n--- Per-Archetype Basin Statistics ---")
    print(f"{'Archetype':<22} {'N':>4} {'Min':>6} {'Q25':>6} {'Med':>6} {'Mean':>6} {'Q75':>6} {'Max':>6} {'Std':>6} {'MissKW':>6}")
    print("-" * 90)

    for arch, stats in sorted(results.items(), key=lambda x: x[1]['mean_dist']):
        print(f"{arch:<22} {stats['count']:>4} {stats['min_dist']:>6.3f} {stats['q25']:>6.3f} "
              f"{stats['median_dist']:>6.3f} {stats['mean_dist']:>6.3f} {stats['q75']:>6.3f} "
              f"{stats['max_dist']:>6.3f} {stats['std_dist']:>6.3f} {missing.get(arch, 0):>6}")

    print("\n--- Centroid-Nearest Assignment Accuracy ---")
    print(f"{'Archetype':<22} {'N':>4} {'Accuracy':>10}")
    print("-" * 40)
    for arch, info in sorted(cross_results['per_archetype'].items(), key=lambda x: x[1]['accuracy'], reverse=True):
        print(f"{arch:<22} {info['count']:>4} {info['accuracy']:>9.1%}")


def save_json(results, cross_results, out_path):
    with open(out_path, 'w') as f:
        json.dump({
            'basin_reach': results,
            'cross_assignment': cross_results,
        }, f, indent=2)


def plot_distributions(results, out_path=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available, skipping plot")
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    archetypes = sorted(results.keys())
    positions = range(len(archetypes))
    data = [[] for _ in archetypes]

    # We only have summary stats, not raw distances — skip violin, do bar of means with error bars
    means = [results[a]['mean_dist'] for a in archetypes]
    stds = [results[a]['std_dist'] for a in archetypes]
    counts = [results[a]['count'] for a in archetypes]

    bars = ax.bar(positions, means, yerr=stds, capsize=3, color='steelblue', alpha=0.7)
    ax.set_xticks(positions)
    ax.set_xticklabels(archetypes, rotation=45, ha='right')
    ax.set_ylabel('Mean Cosine Distance from Seed to Centroid')
    ax.set_title('Basin Reach: How Far Do Seeds Land from Their Archetype Centroid?')
    ax.axhline(y=np.mean(means), color='red', linestyle='--', alpha=0.5, label=f'Overall mean: {np.mean(means):.3f}')
    ax.legend()

    # Annotate with counts
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax.annotate(f'n={count}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=7)

    plt.tight_layout()
    if out_path:
        plt.savefig(out_path, dpi=150)
        print(f"Plot saved to {out_path}")
    else:
        plt.savefig('/mnt/nas/mala/work/archaeology/notes/basin_reach.png', dpi=150)
        print("Plot saved to notes/basin_reach.png")


def main():
    parser = argparse.ArgumentParser(description='Basin reach quantifier')
    parser.add_argument('--plot', action='store_true', help='Generate plot')
    parser.add_argument('--json', type=str, default='/mnt/nas/mala/work/archaeology/notes/basin_reach.json', help='JSON output path')
    args = parser.parse_args()

    print("Loading vectors...")
    word_vecs = load_vectors(DB_PATH)
    print(f"  {len(word_vecs)} words loaded")

    print("Building archetype centroids...")
    centroids, missing = build_centroids(word_vecs, ARCHETYPES_V2)
    print(f"  {sum(1 for c in centroids.values() if c is not None)} centroids built")

    print("Loading dream classifications...")
    dreams = load_dreams(DB_PATH)
    print(f"  {len(dreams)} dreams loaded")

    print("Computing basin reach...")
    results = compute_basin_reach(word_vecs, centroids, dreams)

    print("Computing cross-assignment accuracy...")
    cross_results = compute_cross_distances(word_vecs, centroids, dreams)

    print_report(results, cross_results, missing)
    save_json(results, cross_results, args.json)
    print(f"\nJSON saved to {args.json}")

    if args.plot:
        plot_distributions(results)


if __name__ == '__main__':
    main()
