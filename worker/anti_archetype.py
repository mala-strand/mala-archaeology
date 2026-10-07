#!/usr/bin/env python3
"""
anti_archetype.py — Find words that are maximally distant from a SPECIFIC archetype.

For each archetype, compute its centroid, then find words that are far from
that centroid but not necessarily far from all others. Generate dreams from
these "anti-archetype" seeds and see if the walk avoids the target.

Zero-token. Stdlib + sqlite3 + numpy.
"""

import json
import sqlite3
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "archaeology_phase1_clean.db"


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


def load_qualified_words(min_eras=3):
    """Words appearing in min_eras+ eras."""
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


def load_word_frequencies(min_freq=50):
    """Returns {word: total_frequency} for words with total freq >= min_freq."""
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


def load_english_dict():
    """Load English word list from dwyl/english-words. Auto-downloads if missing."""
    dict_path = ROOT / "data" / "words_alpha.txt"
    if not dict_path.exists():
        print("    Downloading English word list...")
        import urllib.request
        url = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
        urllib.request.urlretrieve(url, dict_path)
        print(f"    Saved to {dict_path}")
    with open(dict_path, encoding="utf-8") as f:
        words = {w.strip().lower() for w in f if len(w.strip()) >= 3}
    return words


# Common foreign words that appear in English dictionaries but are not
# genuinely English vocabulary in this corpus context.
FOREIGN_BLOCKLIST = {
    "elle", "fille", "comme", "vers", "fait", "entre", "nous", "lui",
    "tout", "moi", "temps", "jour", "aux", "bien", "faut", "femme",
    "homme", "monde", "sans", "dont", "deux", "tres", "trop", "peu",
    "roi", "vie", "yeux", "voila", "voici", "sous", "sur", "son", "sa",
    "mes", "tes", "ses", "nos", "vos", "leur", "leurs", "ceux", "celui",
    "celle", "celles", "ce", "cet", "cette", "ces", "mais", "ou", "et",
    "donc", "or", "ni", "car", "que", "quoi", "qui", "dont", "ou",
    "par", "pour", "avec", "dans", "en", "sur", "sous", "vers", "apres",
    "avant", "pendant", "depuis", "durant", "chez", "malgre", "selon",
    "voix", "bras", "dit", "encore", "faire", "pas", "por", "porte",
    "mal", "sitten", "suzanne", "pacha", "roxane", "cyrano", "bret",
    "oui",
}


def load_seeds_with_archetypes():
    """Returns list of (seed_word, primary_archetype)."""
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


def compute_archetype_centroids(vectors, seed_archetypes):
    """Returns {archetype: centroid_vector}."""
    by_arch = {}
    for seed, arch in seed_archetypes:
        if seed in vectors:
            by_arch.setdefault(arch, []).append(vectors[seed])
    return {arch: np.mean(vs, axis=0) for arch, vs in by_arch.items()}


def find_anti_archetype_words(vectors, qualified, frequencies, english_dict, seed_archetypes, centroids, target_arch, top_n=10):
    """Find words that are maximally distant from target_arch centroid.
    Returns list of (word, distance_to_target, nearest_other_archetype).
    """
    seeded = {s for s, _ in seed_archetypes}
    target_cent = centroids.get(target_arch)
    if target_cent is None:
        return []

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
        if english_dict is not None and word not in english_dict:
            continue
        if word in FOREIGN_BLOCKLIST:
            continue

        d_target = cosine_distance(vec, target_cent)

        # Find nearest archetype OTHER than target
        best_other = None
        best_other_dist = float('inf')
        for arch, cent in centroids.items():
            if arch == target_arch:
                continue
            d = cosine_distance(vec, cent)
            if d < best_other_dist:
                best_other_dist = d
                best_other = arch

        scores.append((word, d_target, best_other, best_other_dist))

    # Sort by distance to target (descending)
    scores.sort(key=lambda x: -x[1])
    return scores[:top_n]


def generate_dream(seed, temp=1.5, jump_prob=0.08, length=300):
    """Generate a single dream and return (success, stdout, stderr)."""
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
    print(f"  {len(vectors)} words")

    print("Loading qualified words + frequencies...")
    qualified = load_qualified_words()
    frequencies = load_word_frequencies(min_freq=50)
    print(f"  {len(qualified)} qualified, {len(frequencies)} frequent")

    print("Loading English dictionary...")
    english_dict = load_english_dict()
    print(f"  {len(english_dict) if english_dict else 'None'} words")

    print("Loading seed archetypes...")
    seed_archetypes = load_seeds_with_archetypes()
    print(f"  {len(seed_archetypes)} seeds")

    centroids = compute_archetype_centroids(vectors, seed_archetypes)
    archetypes = sorted(centroids.keys())
    print(f"  {len(archetypes)} archetypes")

    # For each archetype, find top anti-archetype words
    all_results = {}
    for arch in archetypes:
        print(f"\nFinding anti-{arch} words...")
        anti = find_anti_archetype_words(vectors, qualified, frequencies, english_dict, seed_archetypes, centroids, arch, top_n=5)
        all_results[arch] = anti
        print(f"  Top 5:")
        for word, d_target, best_other, d_other in anti:
            print(f"    {word:20s}  anti-{arch}={d_target:.4f}  nearest={best_other}({d_other:.4f})")

    # Save results
    out_path = ROOT / "notes" / "anti_archetype_candidates.json"
    with open(out_path, "w") as f:
        serializable = {}
        for arch, words in all_results.items():
            serializable[arch] = [
                {"word": w, "distance_to_target": float(d), "nearest_other": o, "distance_to_nearest_other": float(nd)}
                for w, d, o, nd in words
            ]
        json.dump(serializable, f, indent=2)
    print(f"\nSaved anti-archetype candidates to {out_path}")

    # Dream generation skipped in this run — candidates are the deliverable.
    # To generate: run this script with the loop below uncommented.
    print(f"\n(Dream generation skipped — {len(archetypes)} archetypes would take ~10 min)")
    print("Top anti-archetype seeds per archetype ready for generation.")


if __name__ == "__main__":
    main()
