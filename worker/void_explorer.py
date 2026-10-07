#!/usr/bin/env python3
"""
void_explorer.py — Find and probe semantic voids in dream space.

A "void word" is a vocabulary word whose vector position is far from all
archetype centroids — it lives in the negative space between territories.

Filters out foreign words and proper nouns by requiring presence in 3+ eras.
Zero-token. Stdlib + sqlite3 + numpy.
"""

import json
import sqlite3
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "archaeology_phase1_clean.db"

# ── vector loading ─────────────────────────────────────────────────

def load_vectors():
    """Load word vectors, averaged across eras. Returns {word: vec}."""
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
            result[w] = avg
    return result


def load_qualified_words():
    """Words appearing in 3+ eras = genuinely cross-era English vocabulary."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT word, COUNT(DISTINCT era) as era_count
        FROM word_vectors
        GROUP BY word
        HAVING era_count >= 3
    """)
    words = {row[0] for row in cursor.fetchall()}
    conn.close()
    return words


def load_seeds_with_archetypes():
    """Returns list of (seed_word, primary_archetype).
    Uses penalized_primary (latest classification with bodily penalty).
    """
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
    sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return float(1 - sim)


# ── void scoring ───────────────────────────────────────────────────

def compute_archetype_centroids(vectors, seed_archetypes):
    """Returns {archetype: centroid_vector}."""
    by_arch = {}
    for seed, arch in seed_archetypes:
        if seed in vectors:
            by_arch.setdefault(arch, []).append(vectors[seed])
    return {arch: np.mean(vs, axis=0) for arch, vs in by_arch.items()}


def score_voids(vectors, qualified_words, seed_archetypes, centroids):
    """For every qualified unseeded word, compute min distance to any archetype centroid.
    Returns sorted list of (word, min_distance, nearest_archetype).
    """
    seeded = {s for s, _ in seed_archetypes}
    scores = []
    for word, vec in vectors.items():
        if word not in qualified_words or word in seeded:
            continue
        if not word.isalpha() or len(word) < 3:
            continue
        best_dist = float('inf')
        best_arch = None
        for arch, cent in centroids.items():
            d = cosine_distance(vec, cent)
            if d < best_dist:
                best_dist = d
                best_arch = arch
        scores.append((word, best_dist, best_arch))
    scores.sort(key=lambda x: -x[1])
    return scores


# ── dream generation wrapper ───────────────────────────────────────

def generate_void_dreams(void_words, count=5):
    """Generate dreams from top void seeds using dream.py."""
    import subprocess
    generated = []
    for word, dist, arch in void_words[:count]:
        print(f"  Generating void dream: seed='{word}' (dist={dist:.3f}, nearest={arch})")
        result = subprocess.run(
            [sys.executable, str(ROOT / "worker" / "dream.py"),
             "--seed", word,
             "--temperature", "1.5",
             "--era-jump-prob", "0.08",
             "--length", "300",
             "--store"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            generated.append(word)
            lines = result.stdout.strip().splitlines()
            preview = ' '.join(lines[-10:]) if lines else '(no output)'
            print(f"    Preview: {preview[:200]}...")
        else:
            print(f"    FAILED: {result.stderr.strip()}")
    return generated


# ── main ───────────────────────────────────────────────────────────

def main():
    print("Loading vectors...")
    vectors = load_vectors()
    print(f"  {len(vectors)} words (non-zero)")

    print("Loading qualified words (3+ eras)...")
    qualified = load_qualified_words()
    print(f"  {len(qualified)} words")

    print("Loading seed archetypes...")
    seed_archetypes = load_seeds_with_archetypes()
    print(f"  {len(seed_archetypes)} seeded words with archetypes")

    print("Computing archetype centroids...")
    centroids = compute_archetype_centroids(vectors, seed_archetypes)
    for arch in sorted(centroids):
        n = len([s for s, a in seed_archetypes if a == arch])
        print(f"  {arch}: {n} seeds")

    print("Scoring void words...")
    void_scores = score_voids(vectors, qualified, seed_archetypes, centroids)
    print(f"  Top 30 void words (furthest from any centroid):")
    for word, dist, arch in void_scores[:30]:
        print(f"    {word:20s}  dist={dist:.4f}  nearest={arch}")

    out_path = ROOT / "notes" / "void_candidates.json"
    with open(out_path, "w") as f:
        json.dump([{"word": w, "distance": d, "nearest_archetype": a}
                   for w, d, a in void_scores[:200]], f, indent=2)
    print(f"  Saved top 200 to {out_path}")

    print("\nGenerating void dreams...")
    generated = generate_void_dreams(void_scores, count=3)
    print(f"  Generated {len(generated)} void dreams")


if __name__ == "__main__":
    main()
