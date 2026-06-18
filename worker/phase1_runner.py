#!/usr/bin/env python3
"""
Phase 1 Runner: Co-occurrence + Vector builder for Phase 1 DB.
Adapted from cooccurrence.py but uses phase1_config.py and the Phase 1 DB.
Zero tokens — pure numpy/scipy computation.
"""

import sys
import os
import sqlite3
import numpy as np
from scipy import sparse
from collections import defaultdict
from pathlib import Path
import json
import time

# Add worker dir to path
sys.path.insert(0, str(Path(__file__).parent))

from phase1_config import (
    DB_PATH, DATA_DIR, CONTEXT_WINDOW, BATCH_SIZE,
    VOCAB_SIZE, VECTOR_DIMS, CHECKPOINT_INTERVAL
)
from tokenizer import tokenize


def get_phase1_vocabulary(db_path: Path) -> list:
    """Get vocabulary from Phase 1 DB."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM vocabulary WHERE is_stopword = 0 ORDER BY frequency DESC")
    words = [row[0] for row in cursor.fetchall()]
    conn.close()
    return words


def build_cooccurrence():
    """Build sparse co-occurrence matrix for Phase 1 texts."""
    db_path = DB_PATH
    data_dir = DATA_DIR

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Get vocabulary
    vocab = get_phase1_vocabulary(db_path)
    vocab_set = set(vocab)
    word_to_idx = {word: idx for idx, word in enumerate(vocab)}

    print(f"Building co-occurrence for {len(vocab)} words...")

    # Get texts to process
    cursor.execute("""
        SELECT gutenberg_id, era FROM texts
        WHERE status = 'complete'
    """)
    texts = cursor.fetchall()
    print(f"Processing {len(texts)} texts...")

    # Build co-occurrence per era
    era_coocs = defaultdict(lambda: defaultdict(int))
    total_tokens_processed = 0

    for gutenberg_id, era in texts:
        text_path = data_dir / f"{gutenberg_id}.txt"
        if not text_path.exists():
            print(f"  Skipping {gutenberg_id}: file not found at {text_path}")
            continue

        print(f"Processing {gutenberg_id} ({era})...")

        text = text_path.read_text(encoding='utf-8', errors='replace')
        tokens = tokenize(text)

        # Filter to vocabulary only
        tokens = [t for t in tokens if t in vocab_set]
        total_tokens_processed += len(tokens)

        # Build co-occurrence with sliding window
        for i, target in enumerate(tokens):
            start = max(0, i - CONTEXT_WINDOW)
            end = min(len(tokens), i + CONTEXT_WINDOW + 1)

            for j in range(start, end):
                if i != j:
                    context = tokens[j]
                    pair = tuple(sorted([target, context]))
                    era_coocs[era][pair] += 1

        print(f"  Processed {len(tokens)} vocab tokens (running total: {total_tokens_processed})")

    # Calculate PPMI and store
    print(f"\nCalculating PPMI and storing...")

    cursor.execute("DELETE FROM cooccurrences")

    total_pairs = 0
    for era, coocs in era_coocs.items():
        print(f"  Era: {era} ({len(coocs)} pairs)")

        word_counts = defaultdict(int)
        for (w1, w2), count in coocs.items():
            word_counts[w1] += count
            word_counts[w2] += count

        total = sum(coocs.values())
        if total == 0:
            continue

        batch = []
        for (w1, w2), count in coocs.items():
            p_joint = count / total
            p_marginal = (word_counts[w1] / total) * (word_counts[w2] / total)
            pmi = np.log2(p_joint / p_marginal) if p_marginal > 0 else 0
            ppmi = max(0, pmi)

            batch.append((w1, w2, era, count, float(ppmi)))

            if len(batch) >= BATCH_SIZE:
                cursor.executemany(
                    "INSERT INTO cooccurrences (word_a, word_b, era, count, ppmi) VALUES (?, ?, ?, ?, ?)",
                    batch
                )
                conn.commit()
                total_pairs += len(batch)
                batch = []

        if batch:
            cursor.executemany(
                "INSERT INTO cooccurrences (word_a, word_b, era, count, ppmi) VALUES (?, ?, ?, ?, ?)",
                batch
            )
            conn.commit()
            total_pairs += len(batch)

    conn.close()
    print(f"\nCo-occurrence stored: {total_pairs} pairs total")


def build_vectors():
    """Build word vectors using SVD on PPMI matrix."""
    from sklearn.decomposition import TruncatedSVD

    db_path = DB_PATH

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Get vocabulary
    vocab = get_phase1_vocabulary(db_path)
    word_to_idx = {word: idx for idx, word in enumerate(vocab)}

    # Get eras
    cursor.execute("SELECT DISTINCT era FROM cooccurrences")
    eras = [row[0] for row in cursor.fetchall()]

    print(f"Building vectors for {len(eras)} eras...")

    cursor.execute("DELETE FROM word_vectors")

    for era in eras:
        print(f"\n  Era: {era}")

        cursor.execute("""
            SELECT word_a, word_b, ppmi FROM cooccurrences
            WHERE era = ? AND ppmi > 0
        """, (era,))

        rows, cols, data = [], [], []
        for word_a, word_b, ppmi in cursor.fetchall():
            if word_a in word_to_idx and word_b in word_to_idx:
                i = word_to_idx[word_a]
                j = word_to_idx[word_b]
                rows.append(i)
                cols.append(j)
                data.append(ppmi)

        if not data:
            print(f"    No data for era {era}")
            continue

        n = len(vocab)
        matrix = sparse.csr_matrix((data, (rows, cols)), shape=(n, n))
        print(f"    Matrix shape: {matrix.shape}, nonzeros: {matrix.nnz}")

        n_components = min(VECTOR_DIMS, matrix.shape[0] - 1)
        if n_components < 10:
            print(f"    Too few dimensions ({n_components}), skipping")
            continue

        svd = TruncatedSVD(n_components=n_components, random_state=42)
        vectors = svd.fit_transform(matrix)

        print(f"    Explained variance: {svd.explained_variance_ratio_.sum():.2%}")

        batch = []
        for word, idx in word_to_idx.items():
            vec = vectors[idx].tolist()
            batch.append((word, era, json.dumps(vec)))

            if len(batch) >= BATCH_SIZE:
                cursor.executemany(
                    "INSERT INTO word_vectors (word, era, vector_json) VALUES (?, ?, ?)",
                    batch
                )
                conn.commit()
                batch = []

        if batch:
            cursor.executemany(
                "INSERT INTO word_vectors (word, era, vector_json) VALUES (?, ?, ?)",
                batch
            )
            conn.commit()

    conn.close()
    print("\nVectors built and stored")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2 or sys.argv[1] == "cooc":
        build_cooccurrence()
    elif sys.argv[1] == "vectors":
        build_vectors()
    elif sys.argv[1] == "all":
        t0 = time.time()
        build_cooccurrence()
        t1 = time.time()
        print(f"Co-occurrence took {t1-t0:.1f}s")
        build_vectors()
        t2 = time.time()
        print(f"Vectors took {t2-t1:.1f}s")
        print(f"Total: {t2-t0:.1f}s")
    else:
        print("Usage: python phase1_runner.py [cooc|vectors|all]")
