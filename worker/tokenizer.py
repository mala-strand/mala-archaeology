#!/usr/bin/env python3
"""
Tokenizer and vocabulary builder for Phase 0 pilot.
Builds top-N vocabulary from downloaded texts.
"""

import sqlite3
import re
import string
from collections import Counter
from pathlib import Path

from pilot_config import (
    DB_PATH, DATA_DIR, VOCAB_SIZE, MIN_WORD_FREQ
)

# Basic English stopwords
STOPWORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
    'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
    'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
    'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
    'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
    'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
    'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
    'give', 'day', 'most', 'us', 'is', 'was', 'are', 'were', 'been', 'had',
    'did', 'said', 'each', 'may', 'too', 'very', 'still', 'own', 'under',
    'while', 'last', 'might', 'great', 'old', 'never', 'shall', 'much',
}


def tokenize(text: str) -> list:
    """
    Simple tokenizer: lowercase, remove punctuation, split on whitespace.
    Returns list of word tokens.
    """
    # Lowercase
    text = text.lower()
    # Remove punctuation (keep apostrophes for contractions)
    text = re.sub(r'[^\w\s\']', ' ', text)
    # Split
    tokens = text.split()
    # Filter: must be alphabetic (no pure numbers), length > 1
    tokens = [t.strip("'") for t in tokens if t.isalpha() and len(t) > 1]
    return tokens


def build_vocabulary():
    """
    Build top-N vocabulary from all downloaded texts.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all completed texts
    cursor.execute("""
        SELECT gutenberg_id, era FROM texts 
        WHERE status = 'complete'
    """)
    texts = cursor.fetchall()
    
    print(f"Building vocabulary from {len(texts)} texts...")
    
    word_counts = Counter()
    
    for gutenberg_id, era in texts:
        text_path = Path(DATA_DIR) / f"{gutenberg_id}.txt"
        if not text_path.exists():
            continue
        
        text = text_path.read_text(encoding='utf-8')
        tokens = tokenize(text)
        word_counts.update(tokens)
        print(f"  Processed {gutenberg_id}: {len(tokens)} tokens")
    
    # Filter: remove stopwords, require min frequency
    filtered_counts = {
        word: count for word, count in word_counts.items()
        if word not in STOPWORDS and count >= MIN_WORD_FREQ
    }
    
    # Take top N
    top_words = Counter(filtered_counts).most_common(VOCAB_SIZE)
    
    print(f"\nTop 20 words:")
    for word, count in top_words[:20]:
        print(f"  {word}: {count}")
    
    # Insert into DB
    cursor.execute("DELETE FROM vocabulary")
    for word, count in top_words:
        cursor.execute(
            "INSERT INTO vocabulary (word, frequency, is_stopword) VALUES (?, ?, ?)",
            (word, count, 0)
        )
    
    # Also mark stopwords
    for stopword in STOPWORDS:
        cursor.execute(
            "INSERT OR IGNORE INTO vocabulary (word, frequency, is_stopword) VALUES (?, ?, ?)",
            (stopword, word_counts.get(stopword, 0), 1)
        )
    
    conn.commit()
    conn.close()
    
    print(f"\nVocabulary built: {len(top_words)} words")
    return [word for word, _ in top_words]


def get_vocabulary() -> list:
    """Get current vocabulary from DB."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM vocabulary WHERE is_stopword = 0 ORDER BY frequency DESC")
    words = [row[0] for row in cursor.fetchall()]
    conn.close()
    return words


if __name__ == "__main__":
    build_vocabulary()
