#!/usr/bin/env python3
"""
Streaming co-occurrence builder for Phase 1.
Processes one text at a time, writes to DB incrementally.
Never holds more than one text + current batch in memory.
Zero tokens — pure Python/numpy/scipy.
"""
import sys
import sqlite3
import numpy as np
from collections import defaultdict
from pathlib import Path
import json
import time

sys.path.insert(0, str(Path(__file__).parent))

from phase1_config import (
    DB_PATH, DATA_DIR, CONTEXT_WINDOW, BATCH_SIZE,
    VOCAB_SIZE, VECTOR_DIMS, CHECKPOINT_INTERVAL
)
from streaming_tokenizer import stream_tokens, STOPWORDS


def get_vocab_set(db_path):
    """Get vocabulary as a set for fast lookup."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM vocabulary WHERE is_stopword = 0")
    words = [row[0] for row in cursor.fetchall()]
    conn.close()
    return set(words)


def get_texts_to_process(db_path):
    """Get texts that need co-occurrence processing."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT gutenberg_id, era FROM texts
        WHERE status = 'complete'
        ORDER BY era, gutenberg_id
    """)
    texts = cursor.fetchall()
    conn.close()
    return texts


def build_cooccurrence_streaming():
    """Build co-occurrence matrix using streaming approach.
    
    Processes one text at a time, accumulates per-era counts in memory,
    writes to DB in batches. If memory gets tight, flushes to DB early.
    """
    db_path = DB_PATH
    data_dir = DATA_DIR

    print("Loading vocabulary...")
    vocab_set = get_vocab_set(db_path)
    print(f"  {len(vocab_set)} content words in vocabulary")

    texts = get_texts_to_process(db_path)
    print(f"  {len(texts)} texts to process")

    # Clear existing co-occurrences
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cooccurrences")
    conn.commit()
    conn.close()

    # Process one era at a time to keep memory manageable
    eras = sorted(set(era for _, era in texts))
    print(f"  Eras: {eras}")

    total_pairs = 0
    total_tokens = 0

    for era in eras:
        era_texts = [(gid, e) for gid, e in texts if e == era]
        print(f"\n{'='*60}")
        print(f"Era: {era} ({len(era_texts)} texts)")
        print(f"{'='*60}")

        # Per-era co-occurrence accumulator
        cooc = defaultdict(int)

        for idx, (gutenberg_id, _) in enumerate(era_texts, 1):
            text_path = data_dir / f"{gutenberg_id}.txt"
            if not text_path.exists():
                print(f"  [{idx}/{len(era_texts)}] Skipping {gutenberg_id}: file not found")
                continue

            print(f"  [{idx}/{len(era_texts)}] Processing {gutenberg_id}...", end=" ", flush=True)

            # Stream tokens, filter to vocab
            tokens = [t for t in stream_tokens(text_path) if t in vocab_set]
            total_tokens += len(tokens)

            # Build co-occurrence with sliding window
            text_pairs = 0
            for i, target in enumerate(tokens):
                start = max(0, i - CONTEXT_WINDOW)
                end = min(len(tokens), i + CONTEXT_WINDOW + 1)

                for j in range(start, end):
                    if i != j:
                        context = tokens[j]
                        pair = tuple(sorted([target, context]))
                        cooc[pair] += 1
                        text_pairs += 1

            print(f"{len(tokens)} tokens, {text_pairs} pairs (total: {len(cooc)} unique)")

            # Check memory: flush if cooc gets too large (>2M entries ~ 200MB)
            if len(cooc) > 2000000:
                print(f"  Memory threshold reached ({len(cooc)} pairs), flushing to DB...")
                flush_cooccurrences(db_path, era, cooc, BATCH_SIZE)
                total_pairs += len(cooc)
                cooc = defaultdict(int)
                print(f"  Flushed. Resetting accumulator.")

        # Flush remaining for this era
        if cooc:
            print(f"  Flushing {len(cooc)} pairs for era {era}...")
            flush_cooccurrences(db_path, era, cooc, BATCH_SIZE)
            total_pairs += len(cooc)

    print(f"\n{'='*60}")
    print(f"Co-occurrence build complete: {total_pairs} total pairs")
    print(f"Total tokens processed: {total_tokens}")
    print(f"{'='*60}")


def flush_cooccurrences(db_path, era, cooc, batch_size=5000):
    """Calculate PPMI and write co-occurrences to DB in batches."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Calculate word frequencies within this era
    word_counts = defaultdict(int)
    for (w1, w2), count in cooc.items():
        word_counts[w1] += count
        word_counts[w2] += count

    total = sum(cooc.values())
    if total == 0:
        conn.close()
        return

    print(f"    PPMI calculation: {len(cooc)} pairs, {total} total co-occurrences")

    batch = []
    written = 0

    for (w1, w2), count in cooc.items():
        p_joint = count / total
        p_marginal = (word_counts[w1] / total) * (word_counts[w2] / total)
        pmi = np.log2(p_joint / p_marginal) if p_marginal > 0 else 0
        ppmi = max(0, pmi)

        if ppmi > 0:
            batch.append((w1, w2, era, count, float(ppmi)))

            if len(batch) >= batch_size:
                cursor.executemany(
                    "INSERT OR IGNORE INTO cooccurrences (word_a, word_b, era, count, ppmi) VALUES (?, ?, ?, ?, ?)",
                    batch
                )
                conn.commit()
                written += len(batch)
                batch = []

    if batch:
        cursor.executemany(
            "INSERT OR IGNORE INTO cooccurrences (word_a, word_b, era, count, ppmi) VALUES (?, ?, ?, ?, ?)",
            batch
        )
        conn.commit()
        written += len(batch)

    conn.close()
    print(f"    Written: {written} PPMI-weighted pairs")


def build_vectors_streaming():
    """Build word vectors using SVD on PPMI matrix.
    
    Processes one era at a time to keep memory manageable.
    """
    from sklearn.decomposition import TruncatedSVD

    db_path = DB_PATH

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Get vocabulary
    cursor.execute("SELECT word FROM vocabulary WHERE is_stopword = 0 ORDER BY frequency DESC")
    vocab = [row[0] for row in cursor.fetchall()]
    word_to_idx = {word: idx for idx, word in enumerate(vocab)}
    n = len(vocab)
    print(f"Vocabulary: {n} words")

    # Get eras
    cursor.execute("SELECT DISTINCT era FROM cooccurrences")
    eras = [row[0] for row in cursor.fetchall()]
    print(f"Eras with data: {len(eras)}")

    cursor.execute("DELETE FROM word_vectors")
    conn.commit()

    for era in eras:
        print(f"\n  Era: {era}")

        cursor.execute("""
            SELECT word_a, word_b, ppmi FROM cooccurrences
            WHERE era = ? AND ppmi > 0
        """, (era,))

        rows, cols, data = [], [], []
        for word_a, word_b, ppmi in cursor.fetchall():
            if word_a in word_to_idx and word_b in word_to_idx:
                rows.append(word_to_idx[word_a])
                cols.append(word_to_idx[word_b])
                data.append(ppmi)

        if not data:
            print(f"    No data for era {era}")
            continue

        from scipy import sparse
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
                    "INSERT OR IGNORE INTO word_vectors (word, era, vector_json) VALUES (?, ?, ?)",
                    batch
                )
                conn.commit()
                batch = []

        if batch:
            cursor.executemany(
                "INSERT OR IGNORE INTO word_vectors (word, era, vector_json) VALUES (?, ?, ?)",
                batch
            )
            conn.commit()

    conn.close()
    print(f"\nVectors built and stored for {len(eras)} eras")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2 or sys.argv[1] == "cooc":
        t0 = time.time()
        build_cooccurrence_streaming()
        t1 = time.time()
        print(f"\nCo-occurrence took {t1-t0:.1f}s")
    elif sys.argv[1] == "vectors":
        t0 = time.time()
        build_vectors_streaming()
        t1 = time.time()
        print(f"\nVectors took {t1-t0:.1f}s")
    elif sys.argv[1] == "all":
        t0 = time.time()
        build_cooccurrence_streaming()
        t1 = time.time()
        print(f"\nCo-occurrence took {t1-t0:.1f}s")
        build_vectors_streaming()
        t2 = time.time()
        print(f"\nVectors took {t2-t1:.1f}s")
        print(f"Total: {t2-t0:.1f}s")
    else:
        print("Usage: python streaming_cooccurrence.py [cooc|vectors|all]")
