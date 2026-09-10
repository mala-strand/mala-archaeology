#!/usr/bin/env python3
"""
Data-driven archetype keyword expansion.

Uses semantic neighbors from the vector database to propose new keywords
for each archetype. A candidate word is suggested for an archetype if it
appears frequently as a top neighbor of that archetype's existing keywords.

Usage:
    cd worker
    python3 expand_archetypes.py [--top-n 15] [--threshold 3] [--dry-run]

Options:
    --top-n        How many neighbors to collect per keyword (default: 15)
    --threshold    Minimum number of archetype keywords a candidate must be neighbor to (default: 3)
    --dry-run      Print proposals without modifying taxonomy file
"""

import sys
import json
import sqlite3
import argparse
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, ERA_ORDER
from archetype_taxonomy_v2 import ARCHETYPES_V2


def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot / (norm1 * norm2))


def get_all_vectors_for_era(conn, era):
    """Load all non-zero vectors for an era into memory."""
    cursor = conn.cursor()
    cursor.execute("SELECT word, vector_json FROM word_vectors WHERE era = ?", (era,))
    vectors = {}
    for word, vec_json in cursor.fetchall():
        vec = json.loads(vec_json)
        if np.linalg.norm(vec) > 1e-10:
            vectors[word] = vec
    return vectors


def find_neighbors(word, target_vec, all_vectors, n=15, exclude=None):
    """Find top-n neighbors for a word among all_vectors."""
    if exclude is None:
        exclude = set()
    exclude.add(word)

    sims = []
    for other_word, other_vec in all_vectors.items():
        if other_word in exclude:
            continue
        sim = cosine_similarity(target_vec, other_vec)
        sims.append((other_word, sim))

    sims.sort(key=lambda x: x[1], reverse=True)
    return sims[:n]


def load_keyword_vectors(conn, era):
    """Load vectors for all current archetype keywords in one era."""
    all_keywords = set()
    for words in ARCHETYPES_V2.values():
        all_keywords.update(words)

    cursor = conn.cursor()
    cursor.execute(
        "SELECT word, vector_json FROM word_vectors WHERE era = ? AND word IN ({})".format(
            ",".join("?" * len(all_keywords))
        ),
        (era,) + tuple(all_keywords),
    )
    keyword_vectors = {}
    for word, vec_json in cursor.fetchall():
        vec = json.loads(vec_json)
        if np.linalg.norm(vec) > 1e-10:
            keyword_vectors[word] = vec
    return keyword_vectors


def propose_expansions(top_n=15, threshold=3):
    conn = sqlite3.connect(DB_PATH)

    # Use the middle era (1850-1900) as representative — rich vocabulary, modern enough
    representative_era = "1850-1900"
    print(f"Loading vectors for era: {representative_era}")
    all_vectors = get_all_vectors_for_era(conn, representative_era)
    keyword_vectors = load_keyword_vectors(conn, representative_era)

    print(f"Total vocabulary in era: {len(all_vectors)}")
    print(f"Keywords with vectors: {len(keyword_vectors)} / {sum(len(v) for v in ARCHETYPES_V2.values())}")

    # For each archetype, collect neighbor candidates from its keywords
    archetype_candidates = defaultdict(Counter)

    for archetype_name, keywords in ARCHETYPES_V2.items():
        print(f"\nProcessing archetype: {archetype_name} ({len(keywords)} keywords)")
        found_vectors = 0
        for kw in keywords:
            if kw not in keyword_vectors:
                continue
            found_vectors += 1
            neighbors = find_neighbors(kw, keyword_vectors[kw], all_vectors, n=top_n)
            for neighbor_word, sim in neighbors:
                archetype_candidates[archetype_name][neighbor_word] += 1
        print(f"  {found_vectors} keywords had vectors")

    # Build proposals: candidates that meet threshold and aren't already in the archetype
    proposals = {}
    for archetype_name, counter in archetype_candidates.items():
        existing = set(ARCHETYPES_V2[archetype_name])
        # Require candidate to be neighbor to at least `threshold` different keywords
        candidates = [
            (word, count)
            for word, count in counter.items()
            if count >= threshold and word not in existing
        ]
        # Sort by how many keywords they're neighbors to, then alphabetically
        candidates.sort(key=lambda x: (-x[1], x[0]))
        proposals[archetype_name] = candidates[:20]  # cap at 20 per archetype

    conn.close()
    return proposals


def print_proposals(proposals, threshold):
    print("\n" + "=" * 60)
    print("PROPOSED KEYWORD EXPANSIONS")
    print(f"Threshold: neighbor to >= {threshold} existing keywords")
    print("=" * 60)

    for archetype_name, candidates in sorted(proposals.items()):
        if not candidates:
            continue
        print(f"\n{archetype_name}:")
        print(f"  Existing: {', '.join(ARCHETYPES_V2[archetype_name])}")
        print(f"  Proposed additions ({len(candidates)}):")
        for word, count in candidates:
            print(f"    - {word}  (neighbor to {count} keywords)")


def generate_patch(proposals, threshold):
    """Generate a Python dict patch that could be applied to archetype_taxonomy_v2.py."""
    lines = ["\n# AUTO-GENERATED EXPANSION (threshold={threshold})".format(threshold=threshold)]
    lines.append("ARCHETYPES_V2_EXPANDED = {")

    for archetype_name in sorted(ARCHETYPES_V2.keys()):
        existing = ARCHETYPES_V2[archetype_name]
        additions = [word for word, count in proposals.get(archetype_name, [])]
        combined = existing + additions
        lines.append(f"    '{archetype_name}': {combined},")

    lines.append("}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Data-driven archetype keyword expansion")
    parser.add_argument("--top-n", type=int, default=15, help="Neighbors per keyword")
    parser.add_argument("--threshold", type=int, default=3, help="Min keyword-neighbor count")
    parser.add_argument("--dry-run", action="store_true", help="Print only, don't modify")
    parser.add_argument("--patch", action="store_true", help="Output as Python patch")
    args = parser.parse_args()

    proposals = propose_expansions(top_n=args.top_n, threshold=args.threshold)

    if args.patch:
        print(generate_patch(proposals, args.threshold))
    else:
        print_proposals(proposals, args.threshold)


if __name__ == "__main__":
    main()
