#!/usr/bin/env python3
"""
void_explorer_v2.py — Refined semantic void finder with foreign-word filtering.

Improvements over v1:
- Requires ASCII-only characters (filters French, Finnish, Portuguese, etc.)
- Requires minimum corpus frequency (filters rare proper nouns)
- Words must appear in 3+ eras (already in v1)

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


def load_qualified_words(min_eras=3):
    """Words appearing in min_eras+ eras = cross-era vocabulary."""
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


# ── void scoring ───────────────────────────────────────────────────

def compute_archetype_centroids(vectors, seed_archetypes):
    """Returns {archetype: centroid_vector}."""
    by_arch = {}
    for seed, arch in seed_archetypes:
        if seed in vectors:
            by_arch.setdefault(arch, []).append(vectors[seed])
    return {arch: np.mean(vs, axis=0) for arch, vs in by_arch.items()}


def score_voids(vectors, qualified_words, frequencies, english_dict, seed_archetypes, centroids):
    """For every qualified unseeded word, compute min distance to any archetype centroid.
    Returns sorted list of (word, min_distance, nearest_archetype).
    """
    seeded = {s for s, _ in seed_archetypes}
    scores = []
    for word, vec in vectors.items():
        # Filters
        if word not in qualified_words or word in seeded:
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

    print("Loading word frequencies (min 50)...")
    frequencies = load_word_frequencies(min_freq=50)
    print(f"  {len(frequencies)} words with freq >= 50")

    print("Loading English dictionary...")
    english_dict = load_english_dict()
    print(f"  {len(english_dict) if english_dict else 'None'} words")

    print("Loading seed archetypes...")
    seed_archetypes = load_seeds_with_archetypes()
    print(f"  {len(seed_archetypes)} seeded words with archetypes")

    print("Computing archetype centroids...")
    centroids = compute_archetype_centroids(vectors, seed_archetypes)
    for arch in sorted(centroids):
        n = len([s for s, a in seed_archetypes if a == arch])
        print(f"  {arch}: {n} seeds")

    print("Scoring void words (with ASCII + freq + English dict filters)...")
    void_scores = score_voids(vectors, qualified, frequencies, english_dict, seed_archetypes, centroids)
    print(f"  {len(void_scores)} void words after filtering")

    print(f"\n  Top 30 void words (furthest from any centroid):")
    for word, dist, arch in void_scores[:30]:
        print(f"    {word:20s}  dist={dist:.4f}  nearest={arch}")

    out_path = ROOT / "notes" / "void_candidates_v2.json"
    with open(out_path, "w") as f:
        json.dump([{"word": w, "distance": d, "nearest_archetype": a}
                   for w, d, a in void_scores[:200]], f, indent=2)
    print(f"\n  Saved top 200 to {out_path}")

    # Compare with v1
    v1_path = ROOT / "notes" / "void_candidates.json"
    if v1_path.exists():
        with open(v1_path) as f:
            v1 = json.load(f)
        v1_words = {x["word"] for x in v1[:30]}
        v2_words = {x[0] for x in void_scores[:30]}
        overlap = v1_words & v2_words
        print(f"\n  Comparison with v1 (top 30):")
        print(f"    v1 had {len(v1_words)} unique words")
        print(f"    v2 has {len(v2_words)} unique words")
        print(f"    Overlap: {len(overlap)} ({len(overlap)/30*100:.0f}%)")
        print(f"    v1-only (foreign/proper): {sorted(v1_words - v2_words)[:10]}")

    print("\nGenerating void dreams from v2 candidates...")
    generated = generate_void_dreams(void_scores, count=3)
    print(f"  Generated {len(generated)} void dreams")


if __name__ == "__main__":
    main()
