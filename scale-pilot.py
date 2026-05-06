#!/usr/bin/env python3
"""
Scale Phase 0 to 20 books.
Downloads all books, builds vocabulary, co-occurrence, vectors.
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "worker"))

from pilot_config import DB_PATH, DATA_DIR
from downloader import PILOT_CATALOG, download_text, clean_gutenberg_text, init_db, populate_catalog
from tokenizer import build_vocabulary, tokenize, STOPWORDS
from collections import defaultdict, Counter
import numpy as np
import json
import time

CONTEXT_WINDOW = 5

def download_all():
    """Download all pending texts."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, gutenberg_id, title, author, year 
        FROM texts 
        WHERE status = 'pending'
    """)
    
    pending = cursor.fetchall()
    print(f"Found {len(pending)} pending texts to download")
    
    success = 0
    failed = 0
    
    for text_id, gutenberg_id, title, author, year in pending:
        print(f"\n[{success+failed+1}/{len(pending)}] {title} ({year}) [ID: {gutenberg_id}]")
        
        try:
            cursor.execute("UPDATE texts SET status = 'downloading' WHERE id = ?", (text_id,))
            conn.commit()
            
            raw_text = download_text(gutenberg_id)
            clean_text = clean_gutenberg_text(raw_text)
            word_count = len(clean_text.split())
            
            # Save to file
            text_path = DATA_DIR / f"{gutenberg_id}.txt"
            text_path.write_text(clean_text, encoding='utf-8')
            
            cursor.execute("""
                UPDATE texts 
                SET status = 'complete', word_count = ?, processed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (word_count, text_id))
            conn.commit()
            
            print(f"  ✓ Downloaded {word_count} words")
            success += 1
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            cursor.execute("UPDATE texts SET status = 'failed' WHERE id = ?", (text_id,))
            conn.commit()
            failed += 1
        
        time.sleep(1)  # Be nice to Gutenberg
    
    conn.close()
    print(f"\nDownload complete: {success} success, {failed} failed")
    return success > 0


def build_cooccurrence():
    """Build co-occurrence matrix for all texts."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get vocabulary
    cursor.execute("SELECT word FROM vocabulary WHERE is_stopword = 0 ORDER BY frequency DESC")
    vocab = [row[0] for row in cursor.fetchall()]
    vocab_set = set(vocab)
    word_to_idx = {word: idx for idx, word in enumerate(vocab)}
    
    print(f"\nBuilding co-occurrence for {len(vocab)} words...")
    
    # Get texts
    cursor.execute("SELECT gutenberg_id, era FROM texts WHERE status = 'complete'")
    texts = cursor.fetchall()
    
    # Build co-occurrence per era
    era_coocs = defaultdict(lambda: defaultdict(int))
    
    for gutenberg_id, era in texts:
        text_path = DATA_DIR / f"{gutenberg_id}.txt"
        if not text_path.exists():
            continue
        
        print(f"Processing {gutenberg_id} ({era})...")
        
        text = text_path.read_text(encoding='utf-8')
        tokens = tokenize(text)
        tokens = [t for t in tokens if t in vocab_set]
        
        # Sliding window
        for i, target in enumerate(tokens):
            start = max(0, i - CONTEXT_WINDOW)
            end = min(len(tokens), i + CONTEXT_WINDOW + 1)
            for j in range(start, end):
                if i != j:
                    pair = tuple(sorted([target, tokens[j]]))
                    era_coocs[era][pair] += 1
        
        print(f"  {len(tokens)} vocab tokens")
    
    # Calculate PPMI and store
    print("\nCalculating PPMI...")
    cursor.execute("DELETE FROM cooccurrences")
    
    for era, coocs in era_coocs.items():
        print(f"  Era: {era} ({len(coocs)} pairs)")
        
        word_counts = defaultdict(int)
        for (w1, w2), count in coocs.items():
            word_counts[w1] += count
            word_counts[w2] += count
        
        total = sum(coocs.values())
        
        for (w1, w2), count in coocs.items():
            p_joint = count / total
            p_marginal = (word_counts[w1] / total) * (word_counts[w2] / total)
            pmi = np.log2(p_joint / p_marginal) if p_marginal > 0 else 0
            ppmi = max(0, pmi)
            
            cursor.execute("""
                INSERT INTO cooccurrences (word_a, word_b, era, count, ppmi)
                VALUES (?, ?, ?, ?, ?)
            """, (w1, w2, era, count, ppmi))
        
        conn.commit()
    
    conn.close()
    print(f"Stored {sum(len(c) for c in era_coocs.values())} co-occurrence pairs")


def build_vectors():
    """Build word vectors using SVD."""
    from scipy import sparse
    from sklearn.decomposition import TruncatedSVD
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT word FROM vocabulary WHERE is_stopword = 0 ORDER BY frequency DESC")
    vocab = [row[0] for row in cursor.fetchall()]
    word_to_idx = {word: idx for idx, word in enumerate(vocab)}
    
    cursor.execute("SELECT DISTINCT era FROM cooccurrences")
    eras = [row[0] for row in cursor.fetchall()]
    
    print(f"\nBuilding vectors for {len(eras)} eras...")
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
                rows.append(word_to_idx[word_a])
                cols.append(word_to_idx[word_b])
                data.append(ppmi)
        
        if not data:
            print(f"    No data")
            continue
        
        n = len(vocab)
        matrix = sparse.csr_matrix((data, (rows, cols)), shape=(n, n))
        print(f"    Matrix: {matrix.shape}, nnz: {matrix.nnz}")
        
        n_components = min(50, matrix.shape[0] - 1)
        if n_components < 10:
            print(f"    Too few dimensions")
            continue
        
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        vectors = svd.fit_transform(matrix)
        
        print(f"    SVD: {vectors.shape}, variance: {svd.explained_variance_ratio_.sum():.1%}")
        
        for word, idx in word_to_idx.items():
            vec = vectors[idx].tolist()
            cursor.execute("""
                INSERT INTO word_vectors (word, era, vector_json)
                VALUES (?, ?, ?)
            """, (word, era, json.dumps(vec)))
        
        conn.commit()
    
    conn.close()
    print("\nVectors built")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true", help="Init DB and catalog")
    parser.add_argument("--download", action="store_true", help="Download texts")
    parser.add_argument("--vocab", action="store_true", help="Build vocabulary")
    parser.add_argument("--cooc", action="store_true", help="Build co-occurrence")
    parser.add_argument("--vectors", action="store_true", help="Build vectors")
    parser.add_argument("--all", action="store_true", help="Run full pipeline")
    args = parser.parse_args()
    
    if args.init:
        init_db()
        populate_catalog()
    
    if args.download or args.all:
        download_all()
    
    if args.vocab or args.all:
        build_vocabulary()
    
    if args.cooc or args.all:
        build_cooccurrence()
    
    if args.vectors or args.all:
        build_vectors()
    
    if not any(vars(args).values()):
        print("Usage: python scale-pilot.py [--init|--download|--vocab|--cooc|--vectors|--all]")
