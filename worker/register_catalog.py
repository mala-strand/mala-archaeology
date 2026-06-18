#!/usr/bin/env python3
"""
Register Phase 1 catalog in the DB and build vocabulary.
Run this once to populate the Phase 1 DB before the worker runs.
Zero tokens — pure Python.
"""
import sys
from pathlib import Path
import sqlite3
import re
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))

from phase1_config import DB_PATH, DATA_DIR, VOCAB_SIZE, MIN_WORD_FREQ
from phase1_catalog import get_valid_catalog
from tokenizer import tokenize, STOPWORDS


def register_texts():
    """Register texts from catalog into DB."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    catalog = get_valid_catalog()
    print(f"Registering {len(catalog)} texts...")
    
    registered = 0
    for gutenberg_id, title, author, year, era in catalog:
        text_path = DATA_DIR / f"{gutenberg_id}.txt"
        if not text_path.exists():
            print(f"  Skipping {gutenberg_id}: file not found")
            continue
        
        # Check if already registered
        cursor.execute("SELECT id FROM texts WHERE gutenberg_id = ?", (gutenberg_id,))
        if cursor.fetchone():
            print(f"  Skipping {gutenberg_id}: already registered")
            continue
        
        cursor.execute(
            "INSERT INTO texts (gutenberg_id, title, author, year, era, status) VALUES (?, ?, ?, ?, ?, 'complete')",
            (gutenberg_id, title, author, year, era)
        )
        registered += 1
        print(f"  Registered: {gutenberg_id} - {title} ({year}) [{era}]")
    
    conn.commit()
    conn.close()
    print(f"\nRegistered {registered} new texts")


def build_vocabulary():
    """Build vocabulary from all registered texts."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Get all completed texts
    cursor.execute("SELECT gutenberg_id FROM texts WHERE status = 'complete'")
    text_ids = [row[0] for row in cursor.fetchall()]
    print(f"Building vocabulary from {len(text_ids)} texts...")
    
    word_counts = Counter()
    total_tokens = 0
    
    for gid in text_ids:
        text_path = DATA_DIR / f"{gid}.txt"
        if not text_path.exists():
            continue
        
        text = text_path.read_text(encoding='utf-8', errors='replace')
        tokens = tokenize(text)
        total_tokens += len(tokens)
        word_counts.update(tokens)
        
        if len(word_counts) % 1000 == 0:
            print(f"  Processed {len(word_counts)} unique tokens so far...")
    
    print(f"Total tokens: {total_tokens}, unique words: {len(word_counts)}")
    
    # Filter by frequency and remove stopwords
    cursor.execute("DELETE FROM vocabulary")
    
    stopwords_set = set(STOPWORDS)
    vocab_words = []
    for word, count in word_counts.most_common():
        if count < MIN_WORD_FREQ:
            continue
        is_stopword = 1 if word in stopwords_set else 0
        vocab_words.append((word, count, is_stopword))
    
    print(f"Vocabulary size (freq >= {MIN_WORD_FREQ}): {len(vocab_words)}")
    
    # Insert in batches
    batch_size = 5000
    for i in range(0, len(vocab_words), batch_size):
        batch = vocab_words[i:i+batch_size]
        cursor.executemany(
            "INSERT INTO vocabulary (word, frequency, is_stopword) VALUES (?, ?, ?)",
            batch
        )
        conn.commit()
    
    # Trim to VOCAB_SIZE (top N non-stopwords)
    cursor.execute("""
        DELETE FROM vocabulary WHERE word NOT IN (
            SELECT word FROM vocabulary WHERE is_stopword = 0
            ORDER BY frequency DESC LIMIT ?
        ) AND is_stopword = 0
    """, (VOCAB_SIZE,))
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM vocabulary WHERE is_stopword = 0")
    final_vocab = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM vocabulary WHERE is_stopword = 1")
    final_stop = cursor.fetchone()[0]
    print(f"Final vocabulary: {final_vocab} content words + {final_stop} stopwords")
    
    conn.close()


if __name__ == "__main__":
    register_texts()
    build_vocabulary()
    print("\nCatalog registration complete. Ready for phase1_runner.py cooc")
