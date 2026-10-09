#!/usr/bin/env python3
"""
negative_space_sampler.py — Find words in the "true negative space" of dream seed vectors.

Instead of looking for words far from archetype centroids (vector void),
this finds words that are far from ALL seed words in the corpus — regions
where the dream walk has never been seeded from. These are not just
"anti-archetype" (far from one centroid) but genuinely in sparse regions
of the seed-word manifold.

For each candidate word, we compute:
- avg_dist_to_k_nearest_seeds: how far from the nearest seed cluster
- seed_archetype_diversity: how many different archetypes are among the K nearest seeds
- density_score: combination of distance and diversity (high = true negative space)

Zero-token. Stdlib + sqlite3 + numpy.
"""

import json
import sqlite3
import sys
from pathlib import Path
from collections import Counter

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "archaeology_phase1_clean.db"
K_NEAREST = 20
DIVERSITY_WEIGHT = 0.3  # how much to weight archetype diversity vs distance


def load_vectors():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT word, era, vector_json FROM word_vectors")
    vecs_by_word = {}
    for word, era, vjson in cursor:
        v = np.array(json.loads(vjson), dtype=np.float32)
        vecs_by_word.setdefault(word, []).append(v)
    conn.close()
    result = {}
    for w, vs in vecs_by_word.items():
        avg = np.mean(vs, axis=0)
        norm = np.linalg.norm(avg)
        if norm > 0:
            result[w] = avg / norm  # normalize
    return result


def load_qualified_words(min_eras=3):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT word, COUNT(DISTINCT era) as era_count
        FROM word_vectors
        GROUP BY word
        HAVING era_count >= ?
    """, (min_eras,))
    words = {row[0] for row in cursor.fetchall()}
    conn.close()
    return words


def load_word_frequencies(min_freq=20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT word, SUM(frequency) as total_freq
        FROM vocabulary
        GROUP BY word
        HAVING total_freq >= ?
    """, (min_freq,))
    freqs = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return freqs


def load_seeds_with_archetypes():
    """Returns list of (seed_word, penalized_primary)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.seed_word, r.penalized_primary
        FROM dreams d
        JOIN dream_reflections r ON d.id = r.dream_id
        WHERE r.penalized_primary IS NOT NULL
          AND r.penalized_primary != 'unclassifiable'
        GROUP BY d.seed_word, r.penalized_primary
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def cosine_distance(a, b):
    # a and b are already normalized
    sim = np.dot(a, b)
    return float(1 - sim)


def compute_negative_space(vectors, qualified, frequencies, seed_archetypes, k=K_NEAREST):
    """For every qualified non-seed word, compute density score.
    Returns sorted list of (word, avg_dist, diversity, density_score, nearest_archetypes).
    """
    seeded = {s for s, _ in seed_archetypes if s in vectors}
    seed_list = [s for s, _ in seed_archetypes if s in vectors]
    seed_vecs = np.array([vectors[s] for s in seed_list])
    seed_archs = [a for s, a in seed_archetypes if s in vectors]

    scores = []
    for word, vec in vectors.items():
        if word not in qualified or word in seeded:
            continue
        if not word.isalpha() or len(word) < 3:
            continue
        if not word.isascii():
            continue
        if word not in frequencies:
            continue

        # Compute distances to all seeds
        distances = 1 - np.dot(seed_vecs, vec)  # cosine distance since normalized
        # Find k nearest
        nearest_idx = np.argpartition(distances, k)[:k]
        nearest_dists = distances[nearest_idx]
        avg_dist = float(np.mean(nearest_dists))

        # Archetype diversity among k nearest
        nearest_archs = [seed_archs[i] for i in nearest_idx]
        unique_archs = len(set(nearest_archs))
        diversity = unique_archs / len(set(seed_archs))  # normalized 0-1

        # Density score: high avg_dist + high diversity = true negative space
        # We want words that are far from seeds AND surrounded by diverse archetypes
        # (not just on the edge of one territory)
        density_score = avg_dist + DIVERSITY_WEIGHT * diversity

        arch_counts = Counter(nearest_archs)
        top_archs = ", ".join([f"{a}({c})" for a, c in arch_counts.most_common(3)])

        scores.append((word, avg_dist, diversity, density_score, top_archs, frequencies[word]))

    # Sort by density score descending
    scores.sort(key=lambda x: -x[3])
    return scores


def generate_dream(seed, temp=1.5, jump_prob=0.08, length=300):
    import subprocess
    result = subprocess.run(
        [sys.executable, str(ROOT / "worker" / "dream.py"),
         "--seed", seed,
         "--temperature", str(temp),
         "--era-jump-prob", str(jump_prob),
         "--length", str(length),
         "--store"],
        capture_output=True, text=True
    )
    return result.returncode == 0, result.stdout, result.stderr


def main():
    print("Loading vectors...")
    vectors = load_vectors()
    print(f"  {len(vectors)} words (normalized)")

    print("Loading qualified words + frequencies...")
    qualified = load_qualified_words()
    frequencies = load_word_frequencies(min_freq=20)
    print(f"  {len(qualified)} qualified, {len(frequencies)} frequent")

    print("Loading seed archetypes...")
    seed_archetypes = load_seeds_with_archetypes()
    print(f"  {len(seed_archetypes)} seeds")

    print(f"\nComputing negative space (k={K_NEAREST}, diversity_weight={DIVERSITY_WEIGHT})...")
    scores = compute_negative_space(vectors, qualified, frequencies, seed_archetypes)
    print(f"  Scored {len(scores)} candidate words")

    print(f"\nTop 30 true negative space words:")
    print(f"  {'Rank':>4} {'Word':<18} {'AvgDist':>8} {'Div':>5} {'Score':>7} {'Freq':>6} {'NearestArchetypes'}")
    for i, (word, avg_dist, diversity, density_score, top_archs, freq) in enumerate(scores[:30]):
        print(f"  {i+1:>4} {word:<18} {avg_dist:>8.4f} {diversity:>5.2f} {density_score:>7.4f} {freq:>6} {top_archs}")

    # Save candidates
    out_path = ROOT / "notes" / "negative_space_candidates.json"
    with open(out_path, "w") as f:
        json.dump([{
            "word": w,
            "avg_dist": float(ad),
            "diversity": float(dv),
            "density_score": float(ds),
            "nearest_archetypes": ta,
            "frequency": int(fr)
        } for w, ad, dv, ds, ta, fr in scores[:200]], f, indent=2)
    print(f"\nSaved top 200 to {out_path}")

    # Generate dreams from top 5
    print(f"\nGenerating dreams from top 5 negative space seeds...")
    generated = []
    for word, avg_dist, diversity, density_score, top_archs, freq in scores[:5]:
        print(f"\n  Seed: '{word}' (avg_dist={avg_dist:.4f}, diversity={diversity:.2f})")
        ok, stdout, stderr = generate_dream(word)
        if ok:
            generated.append(word)
            lines = stdout.strip().splitlines()
            preview = ' '.join(lines[-8:]) if lines else '(no output)'
            print(f"    OK — preview: {preview[:180]}...")
        else:
            print(f"    FAILED: {stderr.strip()[:200]}")

    print(f"\nGenerated {len(generated)} negative-space dreams")


if __name__ == "__main__":
    main()
