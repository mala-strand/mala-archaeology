#!/usr/bin/env python3
"""
Sparse co-occurrence matrix builder for Phase 0 pilot.
Uses scipy.sparse for memory efficiency.
"""

import sqlite3
import numpy as np
from scipy import sparse
from collections import defaultdict
from pathlib import Path
import json

from pilot_config import (
    DB_PATH, DATA_DIR, CONTEXT_WINDOW, BATCH_SIZE
)
from tokenizer import tokenize, get_vocabulary


def build_cooccurrence():
    """
    Build sparse co-occurrence matrix for pilot texts.
    Stores only top-N pairs per word to keep DB small.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get vocabulary
    vocab = get_vocabulary()
    vocab_set = set(vocab)
    word_to_idx = {word: idx for idx, word in enumerate(vocab)}
    
    print(f"Building co-occurrence for {len(vocab)} words...")
    
    # Get texts to process
    cursor.execute("""
        SELECT gutenberg_id, era FROM texts 
        WHERE status = 'complete'
    """)
    texts = cursor.fetchall()
    
    # Build co-occurrence per era
    era_coocs = defaultdict(lambda: defaultdict(int))
    
    for gutenberg_id, era in texts:
        text_path = Path(DATA_DIR) / f"{gutenberg_id}.txt"
        if not text_path.exists():
            continue
        
        print(f"Processing {gutenberg_id} ({era})...")
        
        text = text_path.read_text(encoding='utf-8')
        tokens = tokenize(text)
        
        # Filter to vocabulary only
        tokens = [t for t in tokens if t in vocab_set]
        
        # Build co-occurrence with sliding window
        for i, target in enumerate(tokens):
            start = max(0, i - CONTEXT_WINDOW)
            end = min(len(tokens), i + CONTEXT_WINDOW + 1)
            
            for j in range(start, end):
                if i != j:
                    context = tokens[j]
                    # Store as sorted pair to avoid duplicates
                    pair = tuple(sorted([target, context]))
                    era_coocs[era][pair] += 1
        
        print(f"  Processed {len(tokens)} vocab tokens")
    
    # Calculate PPMI and store top pairs
    print("\nCalculating PPMI and storing...")
    
    cursor.execute("DELETE FROM cooccurrences")
    
    for era, coocs in era_coocs.items():
        print(f"  Era: {era} ({len(coocs)} pairs)")
        
        # Get marginal counts for PPMI
        word_counts = defaultdict(int)
        for (w1, w2), count in coocs.items():
            word_counts[w1] += count
            word_counts[w2] += count
        
        total = sum(coocs.values())
        
        # Calculate PPMI for each pair
        for (w1, w2), count in coocs.items():
            # P(w1,w2)
            p_joint = count / total
            # P(w1) * P(w2)
            p_marginal = (word_counts[w1] / total) * (word_counts[w2] / total)
            # PMI
            pmi = np.log2(p_joint / p_marginal) if p_marginal > 0 else 0
            # PPMI (positive only)
            ppmi = max(0, pmi)
            
            cursor.execute("""
                INSERT INTO cooccurrences (word_a, word_b, era, count, ppmi)
                VALUES (?, ?, ?, ?, ?)
            """, (w1, w2, era, count, ppmi))
        
        conn.commit()
    
    conn.close()
    print(f"\nCo-occurrence stored: {sum(len(c) for c in era_coocs.values())} pairs")


def build_vectors():
    """
    Build word vectors using SVD on PPMI matrix.
    Stores 100-dimensional vectors per word per era.
    """
    from sklearn.decomposition import TruncatedSVD
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get vocabulary
    vocab = get_vocabulary()
    word_to_idx = {word: idx for idx, word in enumerate(vocab)}
    
    # Get eras
    cursor.execute("SELECT DISTINCT era FROM cooccurrences")
    eras = [row[0] for row in cursor.fetchall()]
    
    print(f"Building vectors for {len(eras)} eras...")
    
    cursor.execute("DELETE FROM word_vectors")
    
    for era in eras:
        print(f"\n  Era: {era}")
        
        # Build sparse matrix
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
        
        # Create sparse matrix
        n = len(vocab)
        matrix = sparse.csr_matrix((data, (rows, cols)), shape=(n, n))
        print(f"    Matrix shape: {matrix.shape}, nonzeros: {matrix.nnz}")
        
        # SVD to 100 dimensions
        n_components = min(100, matrix.shape[0] - 1)
        if n_components < 10:
            print(f"    Too few dimensions, skipping")
            continue
        
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        vectors = svd.fit_transform(matrix)
        
        print(f"    Explained variance: {svd.explained_variance_ratio_.sum():.2%}")
        
        # Store vectors
        for word, idx in word_to_idx.items():
            vec = vectors[idx].tolist()
            cursor.execute("""
                INSERT INTO word_vectors (word, era, vector_json)
                VALUES (?, ?, ?)
            """, (word, era, json.dumps(vec)))
        
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
        build_cooccurrence()
        build_vectors()
    else:
        print("Usage: python cooccurrence.py [cooc|vectors|all]")
