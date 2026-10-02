#!/usr/bin/env python3
"""
dream_compare.py — Compare two dreams across multiple dimensions.

New analytical direction: dream-to-dream distance. Treats each dream as a
point in semantic+structural space and measures how far apart they are.

Usage:
    python3 dream_compare.py --id1 1 --id2 2
    python3 dream_compare.py --random
    python3 dream_compare.py --same-seed "waters"
"""

import sqlite3
import sys
import random
import json
import math
import re
import argparse
from collections import Counter

DB_PATH = "../data/archaeology_phase1_clean.db"


def fetch_dream(conn, dream_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT d.id, d.seed_word, d.start_era, d.temperature, d.era_jump_prob,
               d.length, d.dream_text, d.jump_count, d.unique_words,
               r.penalized_primary, r.penalized_secondary, r.penalized_scores,
               r.confidence_tier, r.confidence_margin
        FROM dreams d
        LEFT JOIN dream_reflections r ON d.id = r.dream_id
        WHERE d.id = ?
    """, (dream_id,))
    row = cur.fetchone()
    if not row:
        return None
    keys = ["id", "seed_word", "start_era", "temperature", "era_jump_prob",
            "length", "dream_text", "jump_count", "unique_words",
            "penalized_primary", "penalized_secondary", "penalized_scores",
            "confidence_tier", "confidence_margin"]
    return dict(zip(keys, row))


def tokenize(text):
    """Simple tokenizer matching the dream engine's style."""
    return set(re.findall(r"[a-z]+", text.lower()))


def jaccard(a, b):
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def parse_scores(score_str):
    """Parse penalized_scores JSON or pipe-delimited string."""
    if not score_str:
        return {}
    score_str = score_str.strip()
    if score_str.startswith("{"):
        try:
            return json.loads(score_str)
        except json.JSONDecodeError:
            return {}
    # pipe-delimited fallback: "archetype:score|..."
    result = {}
    for part in score_str.split("|"):
        if ":" in part:
            k, v = part.split(":", 1)
            try:
                result[k.strip()] = float(v)
            except ValueError:
                pass
    return result


def cosine_sim(dict_a, dict_b):
    """Cosine similarity between two sparse score dicts."""
    keys = set(dict_a) | set(dict_b)
    if not keys:
        return 0.0
    dot = sum(dict_a.get(k, 0) * dict_b.get(k, 0) for k in keys)
    norm_a = math.sqrt(sum(v ** 2 for v in dict_a.values()))
    norm_b = math.sqrt(sum(v ** 2 for v in dict_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def extract_era_jumps(text):
    """Extract era jump markers like [1850-1900 → 1500-1700] from dream text."""
    return re.findall(r"\[([^\]]+→[^\]]+)\]", text)


def compare(d1, d2):
    """Compute all comparison metrics between two dreams."""
    tokens1 = tokenize(d1["dream_text"])
    tokens2 = tokenize(d2["dream_text"])

    scores1 = parse_scores(d1["penalized_scores"])
    scores2 = parse_scores(d2["penalized_scores"])

    jumps1 = extract_era_jumps(d1["dream_text"])
    jumps2 = extract_era_jumps(d2["dream_text"])

    # Structural
    temp_diff = abs(d1["temperature"] - d2["temperature"])
    jump_diff = abs(d1["jump_count"] - d2["jump_count"])
    unique_diff = abs(d1["unique_words"] - d2["unique_words"])
    len_diff = abs(d1["length"] - d2["length"])

    # Text overlap
    shared_words = tokens1 & tokens2
    total_unique_words = tokens1 | tokens2
    jaccard_sim = jaccard(tokens1, tokens2)

    # Archetype
    same_primary = d1["penalized_primary"] == d2["penalized_primary"]
    same_secondary = d1["penalized_secondary"] == d2["penalized_secondary"]
    archetype_cosine = cosine_sim(scores1, scores2)

    # Era jump pattern
    shared_jumps = set(jumps1) & set(jumps2)
    jump_jaccard = jaccard(set(jumps1), set(jumps2))

    # Composite distance (0 = identical, 1 = maximally different)
    # Normalize each component to [0,1] approximately
    struct_dist = (
        min(temp_diff / 2.0, 1.0) * 0.25 +
        min(jump_diff / 40.0, 1.0) * 0.25 +
        min(unique_diff / 200.0, 1.0) * 0.25 +
        min(len_diff / 200.0, 1.0) * 0.25
    )
    text_dist = 1.0 - jaccard_sim
    archetype_dist = 1.0 - archetype_cosine
    composite = (struct_dist * 0.3 + text_dist * 0.4 + archetype_dist * 0.3)

    return {
        "struct": {
            "temp_diff": temp_diff,
            "jump_diff": jump_diff,
            "unique_diff": unique_diff,
            "length_diff": len_diff,
            "structural_distance": struct_dist,
        },
        "text": {
            "shared_words": len(shared_words),
            "total_unique": len(total_unique_words),
            "jaccard": jaccard_sim,
            "text_distance": text_dist,
        },
        "archetype": {
            "primary_1": d1["penalized_primary"],
            "primary_2": d2["penalized_primary"],
            "secondary_1": d1["penalized_secondary"],
            "secondary_2": d2["penalized_secondary"],
            "same_primary": same_primary,
            "same_secondary": same_secondary,
            "cosine_similarity": archetype_cosine,
            "archetype_distance": archetype_dist,
        },
        "era_jumps": {
            "jumps_1": len(jumps1),
            "jumps_2": len(jumps2),
            "shared_jump_eras": len(shared_jumps),
            "jump_jaccard": jump_jaccard,
        },
        "composite": composite,
    }


def pick_random_pair(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM dreams ORDER BY RANDOM() LIMIT 2")
    rows = cur.fetchall()
    return rows[0][0], rows[1][0]


def pick_same_seed_pair(conn, seed=None):
    cur = conn.cursor()
    if seed:
        cur.execute("SELECT id FROM dreams WHERE seed_word = ? ORDER BY RANDOM() LIMIT 2", (seed,))
    else:
        cur.execute("""
            SELECT seed_word FROM dreams
            WHERE seed_word IS NOT NULL
            GROUP BY seed_word HAVING COUNT(*) >= 2
            ORDER BY RANDOM() LIMIT 1
        """)
        row = cur.fetchone()
        if not row:
            return None, None
        seed = row[0]
        cur.execute("SELECT id FROM dreams WHERE seed_word = ? ORDER BY RANDOM() LIMIT 2", (seed,))
    rows = cur.fetchall()
    if len(rows) < 2:
        return None, None
    return rows[0][0], rows[1][0], seed


def print_report(d1, d2, metrics):
    print("=" * 70)
    print("DREAM COMPARISON REPORT")
    print("=" * 70)
    print()
    print(f"Dream A: #{d1['id']}  seed={d1['seed_word']}  era={d1['start_era']}  T={d1['temperature']}")
    print(f"         jumps={d1['jump_count']}  unique={d1['unique_words']}  len={d1['length']}")
    print(f"         primary={d1['penalized_primary']}  confidence={d1['confidence_tier']}")
    print()
    print(f"Dream B: #{d2['id']}  seed={d2['seed_word']}  era={d2['start_era']}  T={d2['temperature']}")
    print(f"         jumps={d2['jump_count']}  unique={d2['unique_words']}  len={d2['length']}")
    print(f"         primary={d2['penalized_primary']}  confidence={d2['confidence_tier']}")
    print()
    print("-" * 70)
    print("STRUCTURAL")
    print("-" * 70)
    s = metrics["struct"]
    print(f"  Temperature difference:     {s['temp_diff']:.2f}")
    print(f"  Jump count difference:      {s['jump_diff']}")
    print(f"  Unique words difference:    {s['unique_diff']}")
    print(f"  Length difference:          {s['length_diff']}")
    print(f"  Structural distance:        {s['structural_distance']:.3f}")
    print()
    print("-" * 70)
    print("TEXT OVERLAP")
    print("-" * 70)
    t = metrics["text"]
    print(f"  Shared words:               {t['shared_words']} / {t['total_unique']} total unique")
    print(f"  Jaccard similarity:         {t['jaccard']:.3f}")
    print(f"  Text distance:              {t['text_distance']:.3f}")
    print()
    print("-" * 70)
    print("ARCHETYPE")
    print("-" * 70)
    a = metrics["archetype"]
    print(f"  Dream A primary:            {a['primary_1']}")
    print(f"  Dream B primary:            {a['primary_2']}")
    print(f"  Same primary:               {'YES' if a['same_primary'] else 'NO'}")
    print(f"  Same secondary:             {'YES' if a['same_secondary'] else 'NO'}")
    print(f"  Archetype cosine sim:       {a['cosine_similarity']:.3f}")
    print(f"  Archetype distance:         {a['archetype_distance']:.3f}")
    print()
    print("-" * 70)
    print("ERA JUMPS")
    print("-" * 70)
    e = metrics["era_jumps"]
    print(f"  Jump markers in A:          {e['jumps_1']}")
    print(f"  Jump markers in B:          {e['jumps_2']}")
    print(f"  Shared jump eras:           {e['shared_jump_eras']}")
    print(f"  Jump-pattern Jaccard:       {e['jump_jaccard']:.3f}")
    print()
    print("=" * 70)
    print(f"COMPOSITE DISTANCE:           {metrics['composite']:.3f}")
    print("=" * 70)
    print()
    if metrics['composite'] < 0.25:
        print("Verdict: Very similar — nearly the same dream.")
    elif metrics['composite'] < 0.45:
        print("Verdict: Related — shared DNA but distinct trajectories.")
    elif metrics['composite'] < 0.65:
        print("Verdict: Divergent — same seed region, different outcomes.")
    else:
        print("Verdict: Distant — different worlds entirely.")
    print()


def main():
    parser = argparse.ArgumentParser(description="Compare two dreams")
    parser.add_argument("--id1", type=int, help="First dream ID")
    parser.add_argument("--id2", type=int, help="Second dream ID")
    parser.add_argument("--random", action="store_true", help="Pick two random dreams")
    parser.add_argument("--same-seed", type=str, nargs="?", const="", metavar="SEED",
                        help="Compare two dreams from the same seed (random if no seed given)")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)

    if args.random:
        id1, id2 = pick_random_pair(conn)
    elif args.same_seed is not None:
        result = pick_same_seed_pair(conn, args.same_seed or None)
        if result[0] is None:
            print("No paired dreams found for that seed.")
            sys.exit(1)
        id1, id2, seed = result
        print(f"Selected seed: '{seed}'")
    elif args.id1 and args.id2:
        id1, id2 = args.id1, args.id2
    else:
        # Default: compare two random same-seed dreams
        result = pick_same_seed_pair(conn)
        if result[0] is None:
            print("No seed with multiple dreams found.")
            sys.exit(1)
        id1, id2, seed = result
        print(f"Selected seed: '{seed}'")

    d1 = fetch_dream(conn, id1)
    d2 = fetch_dream(conn, id2)

    if not d1 or not d2:
        print("Failed to load one or both dreams.")
        sys.exit(1)

    metrics = compare(d1, d2)
    print_report(d1, d2, metrics)


if __name__ == "__main__":
    main()
