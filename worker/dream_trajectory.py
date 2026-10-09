#!/usr/bin/env python3
"""
Dream Trajectory Analysis

For each dream, computes the centroid of all visited words and compares its
distance to the assigned archetype centroid against the seed's distance.

This tests whether dreams "find" their archetype during the walk — i.e.,
whether the walk's own semantic vector is closer to the archetype than the
seed was, even when the seed started far away.

Usage:
    python3 worker/dream_trajectory.py [--plot]

Outputs:
    - Per-dream: seed_dist, walk_dist, improvement
    - Aggregate: % of dreams where walk is closer than seed
    - Per-archetype breakdown
"""

import sys
import json
import re
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
    for arch, keywords in archetypes.items():
        vecs = []
        for kw in keywords:
            if kw in word_vecs:
                vecs.append(word_vecs[kw])
        if vecs:
            centroid = np.mean(vecs, axis=0)
            norm = np.linalg.norm(centroid)
            if norm > 0:
                centroid = centroid / norm
            centroids[arch] = centroid
        else:
            centroids[arch] = None
    return centroids


def cosine_distance(a, b):
    """Cosine distance between two unit vectors."""
    return 1.0 - float(np.dot(a, b))


def parse_dream_text(dream_text):
    """
    Parse dream_text into list of (word, era) tuples.
    Extracts start_era from header, then tracks era through jump markers.
    """
    lines = dream_text.split('\n')

    # Find header info
    start_era = None
    header_end = 0
    for i, line in enumerate(lines):
        m = re.search(r'Start era:\s*(\S+)', line)
        if m:
            start_era = m.group(1)
        if '─' in line and line.replace('─', '') == '':
            header_end = i
            break

    if start_era is None:
        raise ValueError("Could not parse start_era from dream text")

    current_era = start_era
    words = []

    jump_re = re.compile(r'\[([^\]]+)\s*→\s*([^\]]+)\]')

    for line in lines[header_end + 1:]:
        line = line.strip()
        if not line:
            continue

        jump_match = jump_re.match(line)
        if jump_match:
            current_era = jump_match.group(2).strip()
            continue

        # Regular word line
        for word in line.split():
            words.append((word, current_era))

    return words, start_era


def load_dreams(db_path):
    """Load all dreams with penalized_primary classification."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.id, d.seed_word, d.dream_text, dr.penalized_primary
        FROM dreams d
        JOIN dream_reflections dr ON d.id = dr.dream_id
        WHERE dr.penalized_primary IS NOT NULL
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def compute_trajectory(word_vecs, centroids, dreams):
    """
    For each dream, compute seed-to-centroid and walk-to-centroid distances.
    Also tests null model: random sample of same size from full vocabulary.
    Returns list of result dicts.
    """
    results = []
    all_words = list(word_vecs.keys())

    for dream_id, seed_word, dream_text, archetype in dreams:
        if seed_word not in word_vecs:
            continue
        if centroids.get(archetype) is None:
            continue

        try:
            words, start_era = parse_dream_text(dream_text)
        except ValueError:
            continue

        seed_vec = word_vecs[seed_word]
        centroid = centroids[archetype]
        seed_dist = cosine_distance(seed_vec, centroid)

        # Compute walk centroid from visited words
        valid_words = [w for w, e in words if w in word_vecs]
        if not valid_words:
            continue

        walk_vecs = [word_vecs[w] for w in valid_words]
        walk_centroid = np.mean(walk_vecs, axis=0)
        walk_norm = np.linalg.norm(walk_centroid)
        if walk_norm > 0:
            walk_centroid = walk_centroid / walk_norm

        walk_dist = cosine_distance(walk_centroid, centroid)
        improvement = seed_dist - walk_dist  # positive = walk is closer

        # Is walk centroid closest to ASSIGNED archetype, or some other?
        other_dists = {
            arch: cosine_distance(walk_centroid, cent)
            for arch, cent in centroids.items()
            if arch != archetype and cent is not None
        }
        nearest_other = min(other_dists.values())
        assigned_is_nearest = walk_dist < nearest_other

        # Null model: random sample of same size from full vocabulary
        n = len(valid_words)
        rand_words = np.random.choice(all_words, size=n, replace=False)
        rand_vecs = [word_vecs[w] for w in rand_words]
        rand_centroid = np.mean(rand_vecs, axis=0)
        rand_norm = np.linalg.norm(rand_centroid)
        if rand_norm > 0:
            rand_centroid = rand_centroid / rand_norm
        rand_dist = cosine_distance(rand_centroid, centroid)
        rand_other_dists = [
            cosine_distance(rand_centroid, cent)
            for arch, cent in centroids.items()
            if arch != archetype and cent is not None
        ]
        rand_nearest_other = min(rand_other_dists)
        rand_assigned_is_nearest = rand_dist < rand_nearest_other

        results.append({
            'dream_id': dream_id,
            'seed_word': seed_word,
            'archetype': archetype,
            'seed_dist': float(seed_dist),
            'walk_dist': float(walk_dist),
            'improvement': float(improvement),
            'walk_closer': walk_dist < seed_dist,
            'assigned_is_nearest': assigned_is_nearest,
            'rand_dist': float(rand_dist),
            'rand_assigned_is_nearest': rand_assigned_is_nearest,
            'dream_length': len(words),
        })

    return results


def aggregate_by_archetype(results):
    """Group trajectory results by archetype."""
    by_arch = defaultdict(list)
    for r in results:
        by_arch[r['archetype']].append(r)

    agg = {}
    for arch, rows in sorted(by_arch.items()):
        improvements = [r['improvement'] for r in rows]
        closer_count = sum(1 for r in rows if r['walk_closer'])
        agg[arch] = {
            'count': len(rows),
            'closer_count': closer_count,
            'closer_pct': closer_count / len(rows) if rows else 0,
            'mean_improvement': float(np.mean(improvements)),
            'median_improvement': float(np.median(improvements)),
            'std_improvement': float(np.std(improvements)),
            'mean_seed_dist': float(np.mean([r['seed_dist'] for r in rows])),
            'mean_walk_dist': float(np.mean([r['walk_dist'] for r in rows])),
        }
    return agg


def print_report(results, agg):
    total = len(results)
    closer = sum(1 for r in results if r['walk_closer'])
    assigned_nearest = sum(1 for r in results if r['assigned_is_nearest'])
    rand_assigned_nearest = sum(1 for r in results if r['rand_assigned_is_nearest'])
    mean_walk = np.mean([r['walk_dist'] for r in results])
    mean_rand = np.mean([r['rand_dist'] for r in results])

    print("=" * 70)
    print("DREAM TRAJECTORY ANALYSIS")
    print("=" * 70)
    print(f"\nTotal dreams analyzed: {total}")
    print(f"\n--- Seed vs Walk Centroid ---")
    print(f"Walk closer to centroid than seed: {closer} / {total} ({closer/total:.1%})")
    print(f"Mean improvement (seed_dist - walk_dist): {np.mean([r['improvement'] for r in results]):.4f}")
    print(f"Median improvement: {np.median([r['improvement'] for r in results]):.4f}")

    print(f"\n--- Null Model: Random Vocabulary Sample ---")
    print(f"Walk assigned nearest: {assigned_nearest} / {total} ({assigned_nearest/total:.1%})")
    print(f"Random assigned nearest: {rand_assigned_nearest} / {total} ({rand_assigned_nearest/total:.1%})")
    print(f"Mean walk dist to assigned: {mean_walk:.4f}")
    print(f"Mean random dist to assigned: {mean_rand:.4f}")

    print("\n--- Per-Archetype Breakdown ---")
    print(f"{'Archetype':<22} {'N':>4} {'Closer':>7} {'%':>6} {'MeanImp':>8} {'MedImp':>8} {'SeedD':>7} {'WalkD':>7}")
    print("-" * 85)
    for arch, stats in sorted(agg.items(), key=lambda x: x[1]['closer_pct'], reverse=True):
        print(f"{arch:<22} {stats['count']:>4} {stats['closer_count']:>7} "
              f"{stats['closer_pct']:>5.1%} {stats['mean_improvement']:>8.4f} "
              f"{stats['median_improvement']:>8.4f} {stats['mean_seed_dist']:>7.3f} {stats['mean_walk_dist']:>7.3f}")

    # Top improvers
    print("\n--- Top 10 Dreams: Walk Finds Archetype ---")
    top = sorted(results, key=lambda r: r['improvement'], reverse=True)[:10]
    print(f"{'ID':>4} {'Seed':<15} {'Archetype':<18} {'SeedD':>7} {'WalkD':>7} {'Improve':>8}")
    print("-" * 65)
    for r in top:
        print(f"{r['dream_id']:>4} {r['seed_word']:<15} {r['archetype']:<18} "
              f"{r['seed_dist']:>7.3f} {r['walk_dist']:>7.3f} {r['improvement']:>+8.3f}")

    # Biggest regressions
    print("\n--- Top 10 Dreams: Walk Drifts From Archetype ---")
    bottom = sorted(results, key=lambda r: r['improvement'])[:10]
    print(f"{'ID':>4} {'Seed':<15} {'Archetype':<18} {'SeedD':>7} {'WalkD':>7} {'Improve':>8}")
    print("-" * 65)
    for r in bottom:
        print(f"{r['dream_id']:>4} {r['seed_word']:<15} {r['archetype']:<18} "
              f"{r['seed_dist']:>7.3f} {r['walk_dist']:>7.3f} {r['improvement']:>+8.3f}")


def plot_results(results, agg, out_path=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available, skipping plot")
        return

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Left: histogram of improvements
    ax1 = axes[0]
    improvements = [r['improvement'] for r in results]
    ax1.hist(improvements, bins=40, color='steelblue', alpha=0.7, edgecolor='white')
    ax1.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='No change')
    ax1.axvline(x=np.mean(improvements), color='orange', linestyle='-', alpha=0.8,
                label=f'Mean: {np.mean(improvements):.3f}')
    ax1.set_xlabel('Improvement (seed_dist - walk_dist)')
    ax1.set_ylabel('Count')
    ax1.set_title('Seed vs Walk Centroid Distance')
    ax1.legend()

    # Middle: per-archetype closer %
    ax2 = axes[1]
    archs = sorted(agg.keys())
    pcts = [agg[a]['closer_pct'] * 100 for a in archs]
    counts = [agg[a]['count'] for a in archs]
    colors = ['#2ecc71' if p > 50 else '#e74c3c' for p in pcts]
    bars = ax2.barh(range(len(archs)), pcts, color=colors, alpha=0.8)
    ax2.set_yticks(range(len(archs)))
    ax2.set_yticklabels(archs)
    ax2.set_xlabel('% Where Walk is Closer Than Seed')
    ax2.axvline(x=50, color='black', linestyle='--', alpha=0.5, label='50% baseline')
    ax2.set_xlim(0, 100)
    ax2.legend()

    for bar, count in zip(bars, counts):
        width = bar.get_width()
        ax2.annotate(f'n={count}',
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(3, 0), textcoords='offset points',
                    ha='left', va='center', fontsize=7)

    # Right: walk vs random assigned-nearest comparison
    ax3 = axes[2]
    assigned_nearest = sum(1 for r in results if r['assigned_is_nearest'])
    rand_assigned_nearest = sum(1 for r in results if r['rand_assigned_is_nearest'])
    total = len(results)

    categories = ['Dream Walk', 'Random Sample']
    values = [assigned_nearest / total * 100, rand_assigned_nearest / total * 100]
    colors3 = ['#3498db', '#95a5a6']
    bars3 = ax3.bar(categories, values, color=colors3, alpha=0.8, width=0.5)
    ax3.set_ylabel('% Where Centroid is Closest to Assigned Archetype')
    ax3.set_title('Null Model: Archetype Specificity')
    n_archetypes = len([c for c in agg.keys()])  # from agg which has all valid archetypes
    ax3.axhline(y=100/n_archetypes, color='red', linestyle='--', alpha=0.5, label=f'Chance (1/{n_archetypes} = {100/n_archetypes:.1f}%)')
    ax3.set_ylim(0, max(values) * 3)
    ax3.legend()

    for bar in bars3:
        height = bar.get_height()
        ax3.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    if out_path:
        plt.savefig(out_path, dpi=150)
        print(f"Plot saved to {out_path}")
    else:
        plt.savefig('/mnt/nas/mala/work/archaeology/notes/dream_trajectory.png', dpi=150)
        print("Plot saved to notes/dream_trajectory.png")


def save_json(results, agg, out_path):
    with open(out_path, 'w') as f:
        json.dump({
            'dreams': results,
            'by_archetype': agg,
            'summary': {
                'total': len(results),
                'closer_count': sum(1 for r in results if r['walk_closer']),
                'closer_pct': sum(1 for r in results if r['walk_closer']) / len(results) if results else 0,
                'mean_improvement': float(np.mean([r['improvement'] for r in results])),
                'median_improvement': float(np.median([r['improvement'] for r in results])),
                'assigned_nearest_count': sum(1 for r in results if r['assigned_is_nearest']),
                'assigned_nearest_pct': sum(1 for r in results if r['assigned_is_nearest']) / len(results) if results else 0,
                'rand_assigned_nearest_count': sum(1 for r in results if r['rand_assigned_is_nearest']),
                'rand_assigned_nearest_pct': sum(1 for r in results if r['rand_assigned_is_nearest']) / len(results) if results else 0,
                'mean_walk_dist': float(np.mean([r['walk_dist'] for r in results])),
                'mean_rand_dist': float(np.mean([r['rand_dist'] for r in results])),
            }
        }, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Dream trajectory analysis')
    parser.add_argument('--plot', action='store_true', help='Generate plot')
    parser.add_argument('--json', type=str, default='/mnt/nas/mala/work/archaeology/notes/dream_trajectory.json')
    args = parser.parse_args()

    print("Loading vectors...")
    word_vecs = load_vectors(DB_PATH)
    print(f"  {len(word_vecs)} words loaded")

    print("Building archetype centroids...")
    centroids = build_centroids(word_vecs, ARCHETYPES_V2)
    print(f"  {sum(1 for c in centroids.values() if c is not None)} centroids built")

    print("Loading dreams...")
    dreams = load_dreams(DB_PATH)
    print(f"  {len(dreams)} dreams loaded")

    print("Computing trajectories...")
    results = compute_trajectory(word_vecs, centroids, dreams)
    print(f"  {len(results)} dreams analyzed")

    agg = aggregate_by_archetype(results)
    print_report(results, agg)
    save_json(results, agg, args.json)
    print(f"\nJSON saved to {args.json}")

    if args.plot:
        plot_results(results, agg)


if __name__ == '__main__':
    main()
