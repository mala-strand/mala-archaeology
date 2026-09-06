#!/usr/bin/env python3
"""
Baseline Comparison: Real vs Random Vectors

Tests the central claim: that a seed's semantic history constrains dream character.
If the claim is true, dreams from real vectors should differ systematically from
dreams generated from random vectors with the same dimensionality and vocabulary.

Usage:
    cd worker
    python3 baseline_comparison.py --runs 20 --length 300

Outputs a comparison table and stores baseline dreams in the database
with seed_word prefixed by 'RANDOM_' for identification.
"""

import sys
import sqlite3
import json
import argparse
import numpy as np
from pathlib import Path
from collections import defaultdict
import time

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, ERA_ORDER
from dream import generate_dream, softmax, ensure_dreams_table
from archetype_taxonomy_v2 import classify_with_v2, extract_words_from_dream


def load_all_vectors(conn: sqlite3.Connection):
    """Load all word vectors into memory. Returns (vectors, words_by_era)."""
    cursor = conn.cursor()
    cursor.execute("SELECT word, era, vector_json FROM word_vectors")
    vectors = defaultdict(dict)
    words_by_era = defaultdict(list)
    for word, era, vec_json in cursor.fetchall():
        vectors[era][word] = np.array(json.loads(vec_json), dtype=np.float32)
        words_by_era[era].append(word)
    return dict(vectors), dict(words_by_era)


def make_random_vectors(real_vectors, dim=50, seed=42):
    """Create random vectors matching the structure of real_vectors."""
    rng = np.random.default_rng(seed)
    random_vectors = {}
    for era, word_dict in real_vectors.items():
        random_vectors[era] = {}
        for word, vec in word_dict.items():
            # Random unit vectors for fair comparison (cosine similarity is
            # dot product of unit vectors; random unit vectors have expected
            # similarity 0 with variance ~1/dim)
            rvec = rng.standard_normal(dim).astype(np.float32)
            rvec = rvec / np.linalg.norm(rvec)
            random_vectors[era][word] = rvec
    return random_vectors


def generate_dream_with_vectors(conn, vectors, words_by_era,
                                 seed=None, start_era=None, length=300,
                                 temperature=1.2, era_jump_prob=0.05,
                                 decay=0.7):
    """
    Generate a dream using externally provided vectors.
    This is a stripped-down version of generate_dream that accepts
    vectors as an argument instead of loading from the database.
    """
    available_eras = [e for e in ERA_ORDER if e in vectors]
    if not available_eras:
        raise ValueError("No eras found")

    if start_era is None:
        start_era = str(np.random.choice(available_eras))
    elif start_era not in vectors:
        start_era = str(np.random.choice(available_eras))

    if seed is None:
        seed = str(np.random.choice(words_by_era[start_era]))
    elif seed not in vectors[start_era]:
        seed = str(np.random.choice(words_by_era[start_era]))

    current_word = seed
    current_era = start_era
    visited = defaultdict(int)
    history = []
    jumps = []

    # Precompute arrays
    era_arrays = {}
    era_word_lists = {}
    for era in available_eras:
        wlist = words_by_era[era]
        era_word_lists[era] = wlist
        era_arrays[era] = np.array([vectors[era][w] for w in wlist], dtype=np.float32)

    for step in range(length):
        visited[current_word] += 1
        word_list = era_word_lists[current_era]
        vec_array = era_arrays[current_era]
        current_vec = vectors[current_era][current_word]

        dots = vec_array @ current_vec
        norms = np.linalg.norm(vec_array, axis=1)
        cur_norm = np.linalg.norm(current_vec)
        if cur_norm == 0:
            similarities = np.zeros(len(word_list))
        else:
            with np.errstate(invalid='ignore'):
                similarities = dots / (norms * cur_norm)
            similarities = np.nan_to_num(similarities, nan=0.0)

        probs = softmax(similarities, temperature)
        for i, w in enumerate(word_list):
            if w in visited:
                probs[i] *= (decay ** visited[w])
        probs = probs / probs.sum()

        next_word = str(np.random.choice(word_list, p=probs))

        if np.random.random() < era_jump_prob and len(available_eras) > 1:
            other_eras = [e for e in available_eras if e != current_era]
            new_era = str(np.random.choice(other_eras))
            next_vec = vectors[current_era][current_word]
            target_vecs = era_arrays[new_era]
            target_words = era_word_lists[new_era]
            t_dots = target_vecs @ next_vec
            t_norms = np.linalg.norm(target_vecs, axis=1)
            n_norm = np.linalg.norm(next_vec)
            if n_norm == 0:
                t_sims = np.zeros(len(target_words))
            else:
                with np.errstate(invalid='ignore'):
                    t_sims = t_dots / (t_norms * n_norm)
                t_sims = np.nan_to_num(t_sims, nan=0.0)
            best_idx = int(np.argmax(t_sims))
            next_word = target_words[best_idx]
            jumps.append((step, current_era, new_era, next_word))
            current_era = new_era

        history.append((current_word, current_era))
        current_word = next_word

    history.append((current_word, current_era))

    # Format dream text (same as dream.py)
    segments = []
    current_line = []
    for i, (word, era) in enumerate(history):
        jump_here = [j for j in jumps if j[0] == i]
        if jump_here:
            if current_line:
                segments.append(" ".join(current_line))
                current_line = []
            j = jump_here[0]
            segments.append(f"\n[{j[1]} → {j[2]}]\n")
        current_line.append(word)
        if len(current_line) >= 10:
            segments.append(" ".join(current_line))
            current_line = []
    if current_line:
        segments.append(" ".join(current_line))

    dream_body = "\n".join(segments)
    header = (
        f"Seed: {seed}  |  Start era: {start_era}\n"
        f"Temperature: {temperature}  |  Era-jump probability: {era_jump_prob}\n"
        f"{'─' * 40}"
    )
    dream_text = f"{header}\n{dream_body}"
    unique_words = len({w for w, _ in history})
    return dream_text, unique_words, len(jumps)


def get_real_dream_stats(conn):
    """Fetch aggregate stats for all stored real dreams."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT seed_word, temperature, jump_count, unique_words, dream_text
        FROM dreams
        WHERE seed_word NOT LIKE 'RANDOM_%'
        ORDER BY id
    """)
    rows = cursor.fetchall()
    return rows


def classify_dreams(rows):
    """Classify a list of (seed, temp, jumps, unique, text) rows."""
    results = []
    for seed, temp, jumps, unique, text in rows:
        words = extract_words_from_dream(text)
        c = classify_with_v2(words, seed, None)
        primary = c['primary'][0] if c['primary'] else 'unclassifiable'
        results.append({
            'seed': seed,
            'temp': temp,
            'jumps': jumps,
            'unique': unique,
            'primary': primary,
            'scores': c['all_scores'],
        })
    return results


def run_comparison(runs=20, length=300, temperature=1.2, era_jump_prob=0.05,
                   store=False, db_path=None):
    db_path = Path(db_path) if db_path else DB_PATH
    conn = sqlite3.connect(str(db_path))

    print("=" * 70)
    print("BASELINE COMPARISON: Real Vectors vs Random Vectors")
    print("=" * 70)

    # Load real vectors
    print("\nLoading real vectors...")
    real_vectors, words_by_era = load_all_vectors(conn)
    print(f"  Eras: {list(real_vectors.keys())}")
    print(f"  Total words: {sum(len(v) for v in real_vectors.values())}")

    # Create random vectors
    print("\nCreating random baseline vectors...")
    random_vectors = make_random_vectors(real_vectors, dim=50, seed=42)

    # Seeds to use: pick a representative set from real dreams
    real_rows = get_real_dream_stats(conn)
    if real_rows:
        seeds_used = list({r[0] for r in real_rows})
        temps_used = list({r[1] for r in real_rows})
        print(f"\n  Real dreams in DB: {len(real_rows)}")
        print(f"  Seeds used: {seeds_used[:10]}{'...' if len(seeds_used) > 10 else ''}")
        print(f"  Temps used: {sorted(set(temps_used))}")
    else:
        seeds_used = ['lord', 'man', 'woman', 'storm', 'waters', 'machine', 'love']
        temps_used = [0.9, 1.2, 1.5]
        print(f"\n  No real dreams in DB. Using default seeds: {seeds_used}")

    # Generate baseline dreams with random vectors
    print(f"\nGenerating {runs} baseline dreams with RANDOM vectors...")
    baseline_rows = []
    available_eras = [e for e in ERA_ORDER if e in random_vectors]
    t0 = time.time()
    for i in range(runs):
        seed = str(np.random.choice(seeds_used)) if seeds_used else None
        temp = float(np.random.choice(temps_used)) if temps_used else temperature
        era = str(np.random.choice(available_eras))
        text, unique, jumps = generate_dream_with_vectors(
            conn, random_vectors, words_by_era,
            seed=seed, start_era=era, length=length,
            temperature=temp, era_jump_prob=era_jump_prob,
        )
        baseline_rows.append((f"RANDOM_{seed or 'none'}", temp, jumps, unique, text))
        if store:
            ensure_dreams_table(conn)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO dreams
                (seed_word, start_era, temperature, era_jump_prob, length,
                 dream_text, jump_count, unique_words)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (f"RANDOM_{seed or 'none'}", era, temp, era_jump_prob, length,
                 text, jumps, unique)
            )
            conn.commit()
    t1 = time.time()
    print(f"  Done in {t1 - t0:.1f}s")

    # Classify both sets
    print("\nClassifying real dreams...")
    real_classified = classify_dreams(real_rows)
    print("Classifying baseline dreams...")
    baseline_classified = classify_dreams(baseline_rows)

    # Aggregate stats
    def stats(name, classified):
        jumps = [r['jumps'] for r in classified]
        uniques = [r['unique'] for r in classified]
        primaries = defaultdict(int)
        for r in classified:
            primaries[r['primary']] += 1
        return {
            'name': name,
            'n': len(classified),
            'jumps_mean': np.mean(jumps) if jumps else 0,
            'jumps_std': np.std(jumps) if jumps else 0,
            'jumps_min': min(jumps) if jumps else 0,
            'jumps_max': max(jumps) if jumps else 0,
            'unique_mean': np.mean(uniques) if uniques else 0,
            'unique_std': np.std(uniques) if uniques else 0,
            'primaries': dict(primaries),
        }

    real_stats = stats("Real vectors", real_classified)
    base_stats = stats("Random vectors", baseline_classified)

    # Print comparison
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    print(f"\n{'Metric':<30} {'Real':>12} {'Random':>12} {'Delta':>12}")
    print("-" * 70)
    print(f"{'Dreams':<30} {real_stats['n']:>12} {base_stats['n']:>12} {'':>12}")
    print(f"{'Jumps (mean ± std)':<30} {real_stats['jumps_mean']:>5.1f} ± {real_stats['jumps_std']:>4.1f} {base_stats['jumps_mean']:>5.1f} ± {base_stats['jumps_std']:>4.1f} {base_stats['jumps_mean'] - real_stats['jumps_mean']:>+12.1f}")
    print(f"{'Jumps (range)':<30} {real_stats['jumps_min']:>5}-{real_stats['jumps_max']:>4} {base_stats['jumps_min']:>5}-{base_stats['jumps_max']:>4} {'':>12}")
    print(f"{'Unique words (mean ± std)':<30} {real_stats['unique_mean']:>5.1f} ± {real_stats['unique_std']:>4.1f} {base_stats['unique_mean']:>5.1f} ± {base_stats['unique_std']:>4.1f} {base_stats['unique_mean'] - real_stats['unique_mean']:>+12.1f}")

    print("\n  Archetype distribution:")
    all_archetypes = sorted(set(real_stats['primaries'].keys()) | set(base_stats['primaries'].keys()))
    print(f"    {'Archetype':<20} {'Real':>8} {'Random':>8}")
    for arch in all_archetypes:
        rc = real_stats['primaries'].get(arch, 0)
        bc = base_stats['primaries'].get(arch, 0)
        print(f"    {arch:<20} {rc:>8} {bc:>8}")

    # Unclassifiable rate
    real_unclass = real_stats['primaries'].get('unclassifiable', 0)
    base_unclass = base_stats['primaries'].get('unclassifiable', 0)
    real_rate = real_unclass / real_stats['n'] * 100 if real_stats['n'] else 0
    base_rate = base_unclass / base_stats['n'] * 100 if base_stats['n'] else 0
    print(f"\n  Unclassifiable rate: {real_rate:.1f}% (real) vs {base_rate:.1f}% (random)")

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    if abs(base_stats['jumps_mean'] - real_stats['jumps_mean']) < 2:
        print("  Jump counts are similar — era-jump probability dominates,")
        print("  and random vectors produce comparable temporal instability.")
    else:
        print(f"  Jump counts differ by {base_stats['jumps_mean'] - real_stats['jumps_mean']:+.1f} —")
        print("  real vectors may constrain or enable jumps differently.")

    if base_rate < real_rate - 10:
        print("  Random dreams are MORE classifiable — this is unexpected.")
        print("  Real vectors may produce sparser or more idiosyncratic vocabulary.")
    elif base_rate > real_rate + 10:
        print("  Real dreams are MORE classifiable — semantic structure produces")
        print("  more coherent archetypal vocabulary than random walks.")
    else:
        print("  Unclassifiable rates are similar — the tie rate may be driven")
        print("  more by keyword coverage than by vector structure.")

    print("\n" + "=" * 70)

    conn.close()
    return real_stats, base_stats


def main():
    parser = argparse.ArgumentParser(description="Baseline comparison: real vs random vectors")
    parser.add_argument("--runs", type=int, default=20, help="Number of baseline dreams to generate")
    parser.add_argument("--length", type=int, default=300, help="Dream length")
    parser.add_argument("--temperature", type=float, default=1.2)
    parser.add_argument("--era-jump-prob", type=float, default=0.05)
    parser.add_argument("--store", action="store_true", help="Store baseline dreams in DB")
    parser.add_argument("--db", help="Override database path")
    args = parser.parse_args()

    run_comparison(
        runs=args.runs,
        length=args.length,
        temperature=args.temperature,
        era_jump_prob=args.era_jump_prob,
        store=args.store,
        db_path=args.db,
    )


if __name__ == "__main__":
    main()
