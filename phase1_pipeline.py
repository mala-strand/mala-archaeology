#!/usr/bin/env python3
"""
Phase 1 Pipeline: Full-scale semantic archaeology
Building tonight, running tomorrow.
"""
import sqlite3
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
import json
import time

sys.path.insert(0, str(Path(__file__).parent / "worker"))

from phase1_config import (
    DB_PATH, DATA_DIR, CACHE_DIR, PHASE1_BOOKS,
    VOCAB_SIZE, CONTEXT_WINDOW, MIN_WORD_FREQ, VECTOR_DIMS,
    BATCH_SIZE, GUTENBERG_DELAY
)
from phase1_catalog import get_valid_catalog
from streaming_tokenizer import build_vocab, save_vocab, stream_vocab_tokens, STOPWORDS

def init_phase1_db():
    """Initialize Phase 1 database with expanded schema."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Core tables (same as Phase 0)
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS texts (
            id INTEGER PRIMARY KEY,
            gutenberg_id INTEGER UNIQUE,
            title TEXT,
            author TEXT,
            year INTEGER,
            era TEXT,
            status TEXT DEFAULT 'pending',
            word_count INTEGER,
            downloaded_at TIMESTAMP,
            processed_at TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY,
            word TEXT UNIQUE,
            frequency INTEGER,
            is_stopword INTEGER DEFAULT 0,
            era TEXT
        );
        
        CREATE TABLE IF NOT EXISTS cooccurrences (
            id INTEGER PRIMARY KEY,
            word_a TEXT,
            word_b TEXT,
            era TEXT,
            count INTEGER,
            ppmi REAL,
            UNIQUE(word_a, word_b, era)
        );
        
        CREATE INDEX IF NOT EXISTS idx_cooc_era ON cooccurrences(era);
        CREATE INDEX IF NOT EXISTS idx_cooc_word_a ON cooccurrences(word_a);
        
        CREATE TABLE IF NOT EXISTS word_vectors (
            id INTEGER PRIMARY KEY,
            word TEXT,
            era TEXT,
            vector_json TEXT,
            UNIQUE(word, era)
        );
        
        CREATE INDEX IF NOT EXISTS idx_vec_word ON word_vectors(word);
        CREATE INDEX IF NOT EXISTS idx_vec_era ON word_vectors(era);
        
        -- Phase 1 additions
        CREATE TABLE IF NOT EXISTS drift_scores (
            id INTEGER PRIMARY KEY,
            word TEXT,
            era_from TEXT,
            era_to TEXT,
            drift_score REAL,
            cosine_sim REAL
        );
        
        CREATE INDEX IF NOT EXISTS idx_drift_word ON drift_scores(word);
    """)
    
    conn.commit()
    conn.close()
    print(f"Phase 1 database initialized at {DB_PATH}")

def populate_phase1_catalog():
    """Insert Phase 1 catalog into database."""
    catalog = get_valid_catalog()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    inserted = 0
    for gutenberg_id, title, author, year, era in catalog[:PHASE1_BOOKS]:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO texts (gutenberg_id, title, author, year, era)
                VALUES (?, ?, ?, ?, ?)
            """, (gutenberg_id, title, author, year, era))
            if cursor.rowcount > 0:
                inserted += 1
        except Exception as e:
            print(f"  Error inserting {title}: {e}")
    
    conn.commit()
    conn.close()
    print(f"Populated {inserted} books in Phase 1 catalog")

def build_era_vocabularies():
    """Build separate vocabularies for each era."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT era FROM texts WHERE era IS NOT NULL")
    eras = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    for era in eras:
        print(f"\nBuilding vocabulary for {era}...")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT gutenberg_id FROM texts WHERE era = ? AND status = 'complete'",
            (era,)
        )
        gutenberg_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not gutenberg_ids:
            print(f"  No texts available for {era}")
            continue
        
        # Get text paths
        text_paths = [DATA_DIR / f"{gid}.txt" for gid in gutenberg_ids]
        text_paths = [p for p in text_paths if p.exists()]
        
        if not text_paths:
            print(f"  No text files found for {era}")
            continue
        
        # Build vocab for this era
        vocab = build_vocab(text_paths, vocab_size=VOCAB_SIZE, min_freq=MIN_WORD_FREQ)
        save_vocab(vocab, era=era)

def build_cooccurrence_sparse():
    """Build sparse co-occurrence matrices using streaming."""
    from scipy import sparse
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT era FROM texts WHERE era IS NOT NULL")
    eras = [row[0] for row in cursor.fetchall()]
    
    for era in eras:
        print(f"\nProcessing {era}...")
        
        # Get vocabulary for this era
        cursor.execute(
            "SELECT word FROM vocabulary WHERE era = ? AND is_stopword = 0 ORDER BY frequency",
            (era,)
        )
        vocab = [row[0] for row in cursor.fetchall()]
        
        if not vocab:
            print(f"  No vocabulary for {era}")
            continue
        
        vocab_set = set(vocab)
        word_to_idx = {word: i for i, word in enumerate(vocab)}
        
        # Get texts for this era
        cursor.execute(
            "SELECT gutenberg_id FROM texts WHERE era = ? AND status = 'complete'",
            (era,)
        )
        gutenberg_ids = [row[0] for row in cursor.fetchall()]
        
        # Build co-occurrence
        cooc_dict = defaultdict(int)
        word_counts = defaultdict(int)
        total_coocs = 0
        
        for gid in gutenberg_ids:
            text_path = DATA_DIR / f"{gid}.txt"
            if not text_path.exists():
                continue
            
            tokens = list(stream_vocab_tokens(text_path, vocab_set))
            
            for i, target in enumerate(tokens):
                start = max(0, i - CONTEXT_WINDOW)
                end = min(len(tokens), i + CONTEXT_WINDOW + 1)
                
                for j in range(start, end):
                    if i != j:
                        pair = tuple(sorted([target, tokens[j]]))
                        cooc_dict[pair] += 1
                        word_counts[target] += 1
                        total_coocs += 1
        
        print(f"  {len(cooc_dict)} pairs, {total_coocs} total")
        
        # Calculate PPMI and store
        cursor.execute("DELETE FROM cooccurrences WHERE era = ?", (era,))
        
        batch = []
        for (w1, w2), count in cooc_dict.items():
            p_joint = count / total_coocs
            p_marginal = (word_counts[w1] / total_coocs) * (word_counts[w2] / total_coocs)
            pmi = np.log2(p_joint / p_marginal) if p_marginal > 0 else 0
            ppmi = max(0, pmi)
            
            batch.append((w1, w2, era, count, ppmi))
            
            if len(batch) >= BATCH_SIZE:
                cursor.executemany(
                    "INSERT INTO cooccurrences (word_a, word_b, era, count, ppmi) VALUES (?, ?, ?, ?, ?)",
                    batch
                )
                batch = []
        
        if batch:
            cursor.executemany(
                "INSERT INTO cooccurrences (word_a, word_b, era, count, ppmi) VALUES (?, ?, ?, ?, ?)",
                batch
            )
        
        conn.commit()
        print(f"  Stored co-occurrences for {era}")
    
    conn.close()

def build_vectors_svd():
    """Build word vectors using SVD."""
    from scipy import sparse
    from sklearn.decomposition import TruncatedSVD
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT era FROM cooccurrences")
    eras = [row[0] for row in cursor.fetchall()]
    
    for era in eras:
        print(f"\nBuilding vectors for {era}...")
        
        cursor.execute(
            "SELECT word FROM vocabulary WHERE era = ? AND is_stopword = 0 ORDER BY frequency",
            (era,)
        )
        vocab = [row[0] for row in cursor.fetchall()]
        word_to_idx = {word: i for i, word in enumerate(vocab)}
        
        if not vocab:
            continue
        
        cursor.execute(
            "SELECT word_a, word_b, ppmi FROM cooccurrences WHERE era = ? AND ppmi > 0",
            (era,)
        )
        
        rows, cols, data = [], [], []
        for word_a, word_b, ppmi in cursor.fetchall():
            if word_a in word_to_idx and word_b in word_to_idx:
                rows.append(word_to_idx[word_a])
                cols.append(word_to_idx[word_b])
                data.append(ppmi)
        
        if not data:
            continue
        
        n = len(vocab)
        matrix = sparse.csr_matrix((data, (rows, cols)), shape=(n, n))
        
        n_components = min(VECTOR_DIMS, matrix.shape[0] - 1)
        if n_components < 10:
            continue
        
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        vectors = svd.fit_transform(matrix)
        
        print(f"  SVD: {vectors.shape}, variance: {svd.explained_variance_ratio_.sum():.1%}")
        
        cursor.execute("DELETE FROM word_vectors WHERE era = ?", (era,))
        
        batch = []
        for word, idx in word_to_idx.items():
            vec = vectors[idx].tolist()
            batch.append((word, era, json.dumps(vec)))
            
            if len(batch) >= BATCH_SIZE:
                cursor.executemany(
                    "INSERT INTO word_vectors (word, era, vector_json) VALUES (?, ?, ?)",
                    batch
                )
                batch = []
        
        if batch:
            cursor.executemany(
                "INSERT INTO word_vectors (word, era, vector_json) VALUES (?, ?, ?)",
                batch
            )
        
        conn.commit()
    
    conn.close()
    print("\nVector construction complete")

def calculate_drift():
    """Calculate semantic drift between eras."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT era FROM word_vectors ORDER BY era")
    eras = [row[0] for row in cursor.fetchall()]
    
    if len(eras) < 2:
        print("Need at least 2 eras for drift calculation")
        return
    
    print(f"\nCalculating drift across {len(eras)} eras...")
    
    cursor.execute("DELETE FROM drift_scores")
    
    for i in range(len(eras) - 1):
        era_from = eras[i]
        era_to = eras[i + 1]
        
        print(f"  {era_from} → {era_to}")
        
        cursor.execute(
            "SELECT word, vector_json FROM word_vectors WHERE era = ?",
            (era_from,)
        )
        vectors_from = {w: json.loads(v) for w, v in cursor.fetchall()}
        
        cursor.execute(
            "SELECT word, vector_json FROM word_vectors WHERE era = ?",
            (era_to,)
        )
        vectors_to = {w: json.loads(v) for w, v in cursor.fetchall()}
        
        # Find common words
        common = set(vectors_from.keys()) & set(vectors_to.keys())
        
        drifts = []
        for word in common:
            v1 = np.array(vectors_from[word])
            v2 = np.array(vectors_to[word])
            
            # Cosine similarity
            cos_sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            drift = 1 - cos_sim  # Distance
            
            drifts.append((word, era_from, era_to, drift, cos_sim))
        
        # Store top drifts
        drifts.sort(key=lambda x: x[3], reverse=True)
        
        cursor.executemany(
            "INSERT INTO drift_scores (word, era_from, era_to, drift_score, cosine_sim) VALUES (?, ?, ?, ?, ?)",
            drifts[:1000]  # Top 1000
        )
        conn.commit()
        
        print(f"    {len(common)} common words, top drift: {drifts[0][0]} ({drifts[0][3]:.3f})")
    
    conn.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true", help="Init DB and catalog")
    parser.add_argument("--vocab", action="store_true", help="Build era vocabularies")
    parser.add_argument("--cooc", action="store_true", help="Build co-occurrence")
    parser.add_argument("--vectors", action="store_true", help="Build vectors")
    parser.add_argument("--drift", action="store_true", help="Calculate drift")
    parser.add_argument("--all", action="store_true", help="Run full pipeline")
    args = parser.parse_args()
    
    if args.init:
        init_phase1_db()
        populate_phase1_catalog()
    
    if args.vocab or args.all:
        build_era_vocabularies()
    
    if args.cooc or args.all:
        build_cooccurrence_sparse()
    
    if args.vectors or args.all:
        build_vectors_svd()
    
    if args.drift or args.all:
        calculate_drift()
    
    if not any(vars(args).values()):
        print("Phase 1 Pipeline - Building tonight, running tomorrow")
        print("Usage: python phase1_pipeline.py [--init|--vocab|--cooc|--vectors|--drift|--all]")
