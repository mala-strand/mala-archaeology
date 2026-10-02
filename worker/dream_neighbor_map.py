#!/usr/bin/env python3
"""
dream_neighbor_map.py — Compute all pairwise dream distances and find neighbors.

Usage:
    python3 dream_neighbor_map.py           # full analysis
    python3 dream_neighbor_map.py --dream-id 1   # neighbors of specific dream
"""

import sqlite3
import sys
import argparse
from dream_compare import fetch_dream, compare

DB_PATH = "../data/archaeology_phase1_clean.db"


def compute_all_pairs(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM dreams ORDER BY id")
    ids = [row[0] for row in cur.fetchall()]

    n = len(ids)
    print(f"Computing {n} dreams = {n*(n-1)//2} pairs...", file=sys.stderr)

    # Pre-load all dreams
    dreams = {}
    for did in ids:
        d = fetch_dream(conn, did)
        if d:
            dreams[did] = d

    distances = []
    for i in range(n):
        for j in range(i+1, n):
            d1 = dreams[ids[i]]
            d2 = dreams[ids[j]]
            m = compare(d1, d2)
            distances.append({
                'id1': ids[i], 'id2': ids[j],
                'seed1': d1['seed_word'], 'seed2': d2['seed_word'],
                'primary1': d1['penalized_primary'], 'primary2': d2['penalized_primary'],
                'composite': m['composite'],
                'text_jaccard': m['text']['jaccard'],
                'archetype_cosine': m['archetype']['cosine_similarity'],
                'same_seed': d1['seed_word'] == d2['seed_word'] and d1['seed_word'] is not None,
                'same_primary': m['archetype']['same_primary'],
            })
        if (i+1) % 20 == 0:
            print(f"  {i+1}/{n} done...", file=sys.stderr)

    print(f"Done. {len(distances)} pairs computed.", file=sys.stderr)
    return distances


def get_neighbors(distances, dream_id, k=5):
    """Find k nearest neighbors for a given dream."""
    relevant = []
    for d in distances:
        if d['id1'] == dream_id:
            relevant.append((d['id2'], d))
        elif d['id2'] == dream_id:
            relevant.append((d['id1'], d))
    relevant.sort(key=lambda x: x[1]['composite'])
    return relevant[:k]


def analyze(distances):
    print("=" * 70)
    print("DREAM NEIGHBOR MAP — Full Corpus Analysis")
    print("=" * 70)
    print()

    # Global stats
    comps = [d['composite'] for d in distances]
    mean_c = sum(comps) / len(comps)
    sorted_c = sorted(comps)
    median_c = sorted_c[len(sorted_c)//2]
    print(f"Total pairs: {len(distances)}")
    print(f"Composite distance: mean={mean_c:.3f}, median={median_c:.3f}, min={min(comps):.3f}, max={max(comps):.3f}")
    print()

    # Most similar pairs (any seeds)
    distances_sorted = sorted(distances, key=lambda x: x['composite'])
    print("-" * 70)
    print("MOST SIMILAR PAIRS (any seeds)")
    print("-" * 70)
    for d in distances_sorted[:15]:
        seed_note = " [SAME SEED]" if d['same_seed'] else ""
        primary_note = " [SAME PRIMARY]" if d['same_primary'] else ""
        print(f"  #{d['id1']}({d['seed1']}) vs #{d['id2']}({d['seed2']})"
              f"  composite={d['composite']:.3f}"
              f"  text={d['text_jaccard']:.3f}"
              f"  archetype_cos={d['archetype_cosine']:.3f}"
              f"{seed_note}{primary_note}")
    print()

    # Most similar DIFFERENT-seed pairs
    diff_seed = [d for d in distances_sorted if not d['same_seed']]
    print("-" * 70)
    print("MOST SIMILAR DIFFERENT-SEED PAIRS")
    print("-" * 70)
    for d in diff_seed[:15]:
        primary_note = " [SAME PRIMARY]" if d['same_primary'] else ""
        print(f"  #{d['id1']}({d['seed1']}) vs #{d['id2']}({d['seed2']})"
              f"  composite={d['composite']:.3f}"
              f"  text={d['text_jaccard']:.3f}"
              f"  archetype_cos={d['archetype_cosine']:.3f}"
              f"{primary_note}")
    print()

    # Most divergent pairs
    print("-" * 70)
    print("MOST DIVERGENT PAIRS")
    print("-" * 70)
    for d in distances_sorted[-10:]:
        seed_note = " [SAME SEED]" if d['same_seed'] else ""
        print(f"  #{d['id1']}({d['seed1']}) vs #{d['id2']}({d['seed2']})"
              f"  composite={d['composite']:.3f}"
              f"  text={d['text_jaccard']:.3f}"
              f"  archetype_cos={d['archetype_cosine']:.3f}"
              f"{seed_note}")
    print()

    # Per-dream neighbor analysis
    print("-" * 70)
    print("NEIGHBOR ANALYSIS — Top 10 dreams with most surprising neighbors")
    print("-" * 70)
    all_ids = set()
    for d in distances:
        all_ids.add(d['id1'])
        all_ids.add(d['id2'])
    all_ids = sorted(all_ids)

    surprise_scores = []
    for did in all_ids:
        neighbors = get_neighbors(distances, did, k=5)
        # Surprise = average distance of k nearest neighbors
        avg_dist = sum(n[1]['composite'] for n in neighbors) / len(neighbors)
        # Also count how many neighbors share the same seed
        same_seed_neighbors = sum(1 for n in neighbors if n[1]['same_seed'])
        surprise_scores.append({
            'id': did,
            'avg_neighbor_dist': avg_dist,
            'same_seed_neighbors': same_seed_neighbors,
            'neighbors': neighbors,
        })

    # Most isolated dreams (highest avg neighbor distance)
    surprise_scores.sort(key=lambda x: x['avg_neighbor_dist'], reverse=True)
    print("Most isolated dreams (even nearest neighbors are distant):")
    for s in surprise_scores[:10]:
        d = s['neighbors'][0][1]
        # Find the dream's own seed and primary
        dream_info = next((x for x in distances if x['id1'] == s['id'] or x['id2'] == s['id']), None)
        # Actually we need to fetch it
        # Skip for now, just print id and avg dist
        print(f"  Dream #{s['id']}: avg neighbor distance = {s['avg_neighbor_dist']:.3f}")

    print()
    print("Most connected dreams (nearest neighbors are close):")
    for s in surprise_scores[-10:]:
        print(f"  Dream #{s['id']}: avg neighbor distance = {s['avg_neighbor_dist']:.3f}")
    print()

    # Save adjacency list for visualization
    print("-" * 70)
    print("Saving adjacency list to /mnt/nas/mala/work/archaeology/data/dream_adjacency.jsonl")
    print("-" * 70)
    import json
    with open('/mnt/nas/mala/work/archaeology/data/dream_adjacency.jsonl', 'w') as f:
        for did in all_ids:
            neighbors = get_neighbors(distances, did, k=5)
            record = {
                'dream_id': did,
                'neighbors': [
                    {
                        'neighbor_id': n[0],
                        'composite': n[1]['composite'],
                        'same_seed': n[1]['same_seed'],
                        'same_primary': n[1]['same_primary'],
                    }
                    for n in neighbors
                ]
            }
            f.write(json.dumps(record) + '\n')
    print("Done.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dream-id", type=int, help="Show neighbors for a specific dream")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    distances = compute_all_pairs(conn)

    if args.dream_id:
        neighbors = get_neighbors(distances, args.dream_id)
        print(f"\nTop 5 neighbors for dream #{args.dream_id}:")
        for nid, d in neighbors:
            seed_note = " [SAME SEED]" if d['same_seed'] else ""
            print(f"  #{nid}({d['seed2'] if d['id1'] == args.dream_id else d['seed1']})"
                  f"  composite={d['composite']:.3f}{seed_note}")
    else:
        analyze(distances)


if __name__ == "__main__":
    main()
