#!/usr/bin/env python3
"""
Dream Engine for Semantic Archaeology — Phase 2.

Probabilistic walks through semantic space with:
- Temperature-controlled randomness (higher = wilder associations)
- Temporal dissonance (random jumps between eras)
- Decay revisits (loop avoidance via visit penalty)
- Poetic formatting

Usage:
    python3 worker/dream.py [--seed WORD] [--era ERA] [--length N]
                            [--temperature T] [--era-jump-prob P]
                            [--store]
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


def softmax(x, temperature=1.0):
    """Temperature-scaled softmax over similarities."""
    x = np.array(x, dtype=np.float64) / temperature
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


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


def cosine_similarity(v1, v2):
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 == 0 or n2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (n1 * n2))


def nearest_word_in_era(word_vec, era_vectors, words, era_array=None):
    """Find the nearest word in an era to a given vector.
    If era_array is provided, uses fast batch numpy ops."""
    if era_array is not None:
        dots = era_array @ word_vec
        norms = np.linalg.norm(era_array, axis=1)
        w_norm = np.linalg.norm(word_vec)
        if w_norm == 0:
            return words[0], 0.0
        with np.errstate(invalid='ignore'):
            sims = dots / (norms * w_norm)
        sims = np.nan_to_num(sims, nan=0.0)
        best_idx = int(np.argmax(sims))
        return words[best_idx], float(sims[best_idx])

    best_sim = -1.0
    best_word = words[0]
    for w in words:
        sim = cosine_similarity(word_vec, era_vectors[w])
        if sim > best_sim:
            best_sim = sim
            best_word = w
    return best_word, best_sim


def ensure_dreams_table(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dreams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seed_word TEXT,
            start_era TEXT,
            temperature REAL,
            era_jump_prob REAL,
            length INTEGER,
            dream_text TEXT,
            jump_count INTEGER,
            unique_words INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


def generate_dream(conn, seed=None, start_era=None, length=300, temperature=1.2,
                   era_jump_prob=0.05, decay=0.7, store=False):
    """Generate a dream walk and optionally store it."""
    vectors, words_by_era = load_all_vectors(conn)

    available_eras = [e for e in ERA_ORDER if e in vectors]
    if not available_eras:
        raise ValueError("No eras found in database")

    if start_era is None:
        start_era = str(np.random.choice(available_eras))
    elif start_era not in vectors:
        raise ValueError(f"Era {start_era!r} not found. Available: {available_eras}")

    if seed is None:
        seed = str(np.random.choice(words_by_era[start_era]))
    elif seed not in vectors[start_era]:
        old_seed = seed
        seed = str(np.random.choice(words_by_era[start_era]))
        print(f"Warning: seed {old_seed!r} not in era {start_era}, using {seed!r}")

    current_word = seed
    current_era = start_era
    visited = defaultdict(int)
    history = []
    jumps = []

    # Precompute vector arrays per era for fast batch similarity
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

        # Batch cosine similarities
        dots = vec_array @ current_vec
        norms = np.linalg.norm(vec_array, axis=1)
        cur_norm = np.linalg.norm(current_vec)
        if cur_norm == 0:
            similarities = np.zeros(len(word_list))
        else:
            with np.errstate(invalid='ignore'):
                similarities = dots / (norms * cur_norm)
            similarities = np.nan_to_num(similarities, nan=0.0)

        # Temperature + softmax
        probs = softmax(similarities, temperature)

        # Decay revisits
        for i, w in enumerate(word_list):
            if w in visited:
                probs[i] *= (decay ** visited[w])
        probs = probs / probs.sum()

        next_word = str(np.random.choice(word_list, p=probs))

        # Temporal dissonance
        if np.random.random() < era_jump_prob and len(available_eras) > 1:
            other_eras = [e for e in available_eras if e != current_era]
            new_era = str(np.random.choice(other_eras))
            next_word, _ = nearest_word_in_era(
                vectors[current_era][current_word],
                vectors[new_era],
                era_word_lists[new_era],
                era_array=era_arrays[new_era]
            )
            jumps.append((step, current_era, new_era, next_word))
            current_era = new_era

        history.append((current_word, current_era))
        current_word = next_word

    # Append final word
    history.append((current_word, current_era))

    # --- Format dream text ---
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
            (seed, start_era, temperature, era_jump_prob, length,
             dream_text, len(jumps), unique_words)
        )
        conn.commit()
        dream_id = cursor.lastrowid
        print(f"\n💾 Dream stored with id={dream_id}")

    return dream_text, unique_words, len(jumps)


def main():
    parser = argparse.ArgumentParser(description="Dream Engine for Semantic Archaeology")
    parser.add_argument("--seed", help="Starting word")
    parser.add_argument("--era", help="Starting era")
    parser.add_argument("--length", type=int, default=300, help="Dream length in words")
    parser.add_argument("--temperature", type=float, default=1.2,
                        help="Randomness (higher = wilder associations)")
    parser.add_argument("--era-jump-prob", type=float, default=0.05,
                        help="Probability of era jump per step")
    parser.add_argument("--decay", type=float, default=0.7,
                        help="Revisit penalty decay (0=strong penalty, 1=no penalty)")
    parser.add_argument("--store", action="store_true",
                        help="Store dream in database")
    parser.add_argument("--db", help="Override database path")
    args = parser.parse_args()

    db_path = Path(args.db) if args.db else DB_PATH
    conn = sqlite3.connect(str(db_path))

    t0 = time.time()
    dream_text, unique_count, jump_count = generate_dream(
        conn,
        seed=args.seed,
        start_era=args.era,
        length=args.length,
        temperature=args.temperature,
        era_jump_prob=args.era_jump_prob,
        decay=args.decay,
        store=args.store,
    )
    t1 = time.time()

    print(dream_text)
    print(f"\n{'─' * 40}")
    print(f"Unique words: {unique_count} / {args.length}  |  Jumps: {jump_count}")
    print(f"Generated in {t1 - t0:.1f}s")

    conn.close()


if __name__ == "__main__":
    main()
