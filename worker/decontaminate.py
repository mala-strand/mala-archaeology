#!/usr/bin/env python3
"""
Phase 2 prerequisite: decontaminate co-occurrence table by removing
Project Gutenberg boilerplate terms, then rebuild word vectors and
drift scores on the clean corpus.

Writes output to a new DB: archaeology_phase1_clean.db
Does not modify the original DB.

Usage:
    python3 worker/decontaminate.py [--dry-run]

Dry-run: reports how many pairs would be removed, per stopword.
"""
import sys
import sqlite3
import shutil
import json
import numpy as np
from pathlib import Path
from collections import defaultdict
import time

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, VECTOR_DIMS

ERA_ORDER = ["pre-1500", "1500-1700", "1700-1800", "1800-1850", "1850-1900", "1900-1923"]

# Targeted Gutenberg boilerplate stoplist.
# Derived from FINDINGS.md sessions 2026-06-13 through 2026-06-17.
# These words appear in every Gutenberg license block and contaminate
# co-occurrence vectors for nearby legitimate words (e.g. "mission").
BOILERPLATE_STOPLIST = {
    # Gutenberg project identifiers
    "electronic", "gutenberg", "hart", "michael",
    # License action verbs that appear in the license block
    "promoting", "sharing", "displaying", "performing",
    "distributing", "redistributing", "derivative",
    # Legal/operational terms from the license block
    "protect", "removed", "liability", "editions",
    # Generic verbs with confirmed Gutenberg contamination
    "using", "works",
    # French words (contamination from French texts)
    "les", "mes", "sur", "sous", "par", "ton", "beau", "cent", "chambre", "va", "tome",
    # Additional Gutenberg license residue
    "disclaimer", "warranties", "limitation", "exclusion", "maximum",
}


def dry_run(src_db: Path):
    """Report contamination scope without modifying anything."""
    conn = sqlite3.connect(str(src_db))
    cursor = conn.cursor()

    total_pairs = cursor.execute("SELECT COUNT(*) FROM cooccurrences").fetchone()[0]
    print(f"Total co-occurrence pairs: {total_pairs:,}")
    print()

    affected_by_word = {}
    for word in sorted(BOILERPLATE_STOPLIST):
        count = cursor.execute(
            "SELECT COUNT(*) FROM cooccurrences WHERE word_a = ? OR word_b = ?",
            (word, word)
        ).fetchone()[0]
        if count > 0:
            affected_by_word[word] = count

    print("Pairs affected per stoplist word:")
    for word, count in sorted(affected_by_word.items(), key=lambda x: -x[1]):
        print(f"  {word:20s}  {count:6,}  ({count/total_pairs*100:.2f}%)")

    # Total unique pairs to remove (may overlap if two stopwords co-occur)
    placeholders = ",".join("?" * len(BOILERPLATE_STOPLIST))
    stoplist = list(BOILERPLATE_STOPLIST)
    removable = cursor.execute(
        f"SELECT COUNT(*) FROM cooccurrences WHERE word_a IN ({placeholders}) OR word_b IN ({placeholders})",
        stoplist + stoplist
    ).fetchone()[0]
    print()
    print(f"Total pairs to remove: {removable:,}  ({removable/total_pairs*100:.2f}%)")
    print(f"Pairs remaining:       {total_pairs - removable:,}")
    conn.close()


def build_vectors_from_clean(conn: sqlite3.Connection) -> int:
    """
    Rebuild word_vectors from the cleaned cooccurrences using SVD.
    Returns number of (word, era) vectors written.
    """
    from sklearn.decomposition import TruncatedSVD
    from scipy import sparse

    cursor = conn.cursor()

    # Vocabulary: all words still in co-occurrences (excludes stoplist words
    # since their pairs were deleted)
    cursor.execute("SELECT DISTINCT word FROM vocabulary WHERE is_stopword = 0")
    vocab = [row[0] for row in cursor.fetchall()]
    word_to_idx = {w: i for i, w in enumerate(vocab)}
    n_vocab = len(vocab)
    print(f"  Vocabulary size: {n_vocab}")

    cursor.execute("SELECT DISTINCT era FROM cooccurrences ORDER BY era")
    eras = [row[0] for row in cursor.fetchall()]
    eras = [e for e in ERA_ORDER if e in eras]
    print(f"  Eras: {eras}")

    cursor.execute("DELETE FROM word_vectors")
    conn.commit()

    total_vectors = 0
    for era in eras:
        print(f"\n  Building vectors for era: {era}")
        cursor.execute(
            "SELECT word_a, word_b, ppmi FROM cooccurrences WHERE era = ? AND ppmi > 0",
            (era,)
        )
        rows_data = cursor.fetchall()

        r, c, vals = [], [], []
        for word_a, word_b, ppmi in rows_data:
            if word_a in word_to_idx and word_b in word_to_idx:
                i = word_to_idx[word_a]
                j = word_to_idx[word_b]
                r.append(i); c.append(j); vals.append(ppmi)
                r.append(j); c.append(i); vals.append(ppmi)  # symmetric

        if not vals:
            print(f"    No pairs for era {era}, skipping")
            continue

        matrix = sparse.csr_matrix((vals, (r, c)), shape=(n_vocab, n_vocab))
        print(f"    Matrix: {matrix.shape}, nonzeros: {matrix.nnz:,}")

        n_components = min(VECTOR_DIMS, matrix.shape[0] - 1, matrix.nnz)
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

        cursor.executemany(
            "INSERT INTO word_vectors (word, era, vector_json) VALUES (?, ?, ?)",
            batch
        )
        conn.commit()
        total_vectors += len(batch)
        print(f"    Stored {len(batch)} vectors")

    return total_vectors


def cosine_similarity(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 == 0 or n2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (n1 * n2))


def build_drift_scores(conn: sqlite3.Connection) -> int:
    """Recompute drift_scores from the new word_vectors. Returns count written."""
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT era FROM word_vectors")
    db_eras = {row[0] for row in cursor.fetchall()}
    eras = [e for e in ERA_ORDER if e in db_eras]

    cursor.execute("SELECT word, era, vector_json FROM word_vectors")
    vectors = defaultdict(dict)
    for word, era, vec_json in cursor.fetchall():
        vectors[word][era] = json.loads(vec_json)

    all_words = list(vectors.keys())
    print(f"  Computing drift for {len(all_words)} words across {len(eras)} eras")

    cursor.execute("DELETE FROM drift_scores")
    conn.commit()

    total = 0
    for i in range(len(eras) - 1):
        era_from, era_to = eras[i], eras[i + 1]
        batch = []
        for word in all_words:
            if era_from in vectors[word] and era_to in vectors[word]:
                sim = cosine_similarity(vectors[word][era_from], vectors[word][era_to])
                drift = 1.0 - sim
                batch.append((word, era_from, era_to, float(drift), float(sim)))

        batch.sort(key=lambda x: x[3], reverse=True)
        cursor.executemany(
            "INSERT OR IGNORE INTO drift_scores (word, era_from, era_to, drift_score, cosine_sim) VALUES (?, ?, ?, ?, ?)",
            batch
        )
        conn.commit()
        total += len(batch)
        top = batch[0] if batch else None
        print(f"  {era_from} → {era_to}: {len(batch)} scores | top drifter: {top[0] if top else 'n/a'} ({top[3]:.4f} if top else 0)")

    return total


def run(src_db: Path):
    dst_db = src_db.parent / "archaeology_phase1_clean.db"

    print(f"Source DB:      {src_db}")
    print(f"Destination DB: {dst_db}")
    print()

    # Copy original DB to clean DB
    print("Copying DB...")
    shutil.copy2(str(src_db), str(dst_db))
    conn = sqlite3.connect(str(dst_db))

    # --- Step 1: Remove boilerplate pairs ---
    cursor = conn.cursor()
    before = cursor.execute("SELECT COUNT(*) FROM cooccurrences").fetchone()[0]
    print(f"\nBefore decontamination: {before:,} pairs")

    placeholders = ",".join("?" * len(BOILERPLATE_STOPLIST))
    stoplist = list(BOILERPLATE_STOPLIST)
    cursor.execute(
        f"DELETE FROM cooccurrences WHERE word_a IN ({placeholders}) OR word_b IN ({placeholders})",
        stoplist + stoplist
    )
    conn.commit()

    after = cursor.execute("SELECT COUNT(*) FROM cooccurrences").fetchone()[0]
    removed = before - after
    print(f"After decontamination:  {after:,} pairs  (removed {removed:,}, {removed/before*100:.2f}%)")

    # --- Step 2: Rebuild word vectors ---
    print("\nRebuilding word vectors...")
    t0 = time.time()
    n_vectors = build_vectors_from_clean(conn)
    print(f"  Total vectors written: {n_vectors:,}  ({time.time()-t0:.1f}s)")

    # --- Step 3: Recompute drift scores ---
    print("\nRecomputing drift scores...")
    t0 = time.time()
    n_drifts = build_drift_scores(conn)
    print(f"  Total drift scores written: {n_drifts:,}  ({time.time()-t0:.1f}s)")

    conn.close()

    # --- Summary ---
    print("\n=== Decontamination complete ===")
    print(f"Clean DB: {dst_db}")
    print(f"  Co-occurrence pairs: {after:,}")
    print(f"  Word vectors:        {n_vectors:,}")
    print(f"  Drift scores:        {n_drifts:,}")
    print()
    print("Next: update phase1_config.py to point DB_PATH at the clean DB,")
    print("then re-run the clustering script (to be built).")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    src = DB_PATH

    if dry:
        print("=== DRY RUN ===\n")
        dry_run(src)
    else:
        run(src)
