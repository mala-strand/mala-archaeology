"""
Streaming tokenizer for Phase 1.
Never loads entire texts into memory.
"""
import re
import sqlite3
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, MIN_WORD_FREQ, MAX_TOKENS_IN_MEMORY

STOPWORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her',
    'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there',
    'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get',
    'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no',
    'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your',
    'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then',
    'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
    'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
    'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
    'give', 'day', 'most', 'us', 'is', 'was', 'are', 'were', 'been',
    'has', 'had', 'did', 'does', 'doing', 'done', 'am', 'being',
}

def tokenize_line(line):
    """Tokenize a single line of text."""
    line = line.lower()
    line = re.sub(r'[^\w\s\']', ' ', line)
    tokens = line.split()
    tokens = [t.strip("'\"") for t in tokens if len(t) > 1]
    return tokens

def stream_tokens(text_path):
    """Yield tokens from a text file, line by line."""
    with open(text_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            tokens = tokenize_line(line)
            for token in tokens:
                if token.isalpha():
                    yield token

def count_frequencies(text_paths):
    """
    First pass: count word frequencies across all texts.
    Uses streaming to stay memory-efficient.
    """
    counter = Counter()
    
    for i, path in enumerate(text_paths):
        print(f"  Counting [{i+1}/{len(text_paths)}]: {path.name}")
        
        for token in stream_tokens(path):
            counter[token] += 1
    
    return counter

def build_vocab(text_paths, vocab_size=8000, min_freq=10):
    """
    Build vocabulary from texts.
    Two-pass: count first, then filter.
    """
    print("Pass 1: Counting frequencies...")
    frequencies = count_frequencies(text_paths)
    
    print(f"  Total unique words: {len(frequencies)}")
    
    # Filter stopwords and min freq
    filtered = {
        word: count for word, count in frequencies.items()
        if word not in STOPWORDS and count >= min_freq
    }
    
    print(f"  After filtering: {len(filtered)}")
    
    # Take top N
    top_words = Counter(filtered).most_common(vocab_size)
    
    print(f"  Final vocabulary: {len(top_words)}")
    
    return {word: i for i, (word, _) in enumerate(top_words)}

def save_vocab(vocab, era=None):
    """Save vocabulary to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM vocabulary WHERE era = ? OR era IS NULL", (era,))
    
    for word, idx in vocab.items():
        is_stop = 1 if word in STOPWORDS else 0
        cursor.execute(
            "INSERT INTO vocabulary (word, frequency, is_stopword, era) VALUES (?, ?, ?, ?)",
            (word, idx, is_stop, era)
        )
    
    conn.commit()
    conn.close()
    print(f"Saved {len(vocab)} words to vocabulary")

def stream_vocab_tokens(text_path, vocab_set):
    """Stream only tokens that are in the vocabulary."""
    for token in stream_tokens(text_path):
        if token in vocab_set:
            yield token

if __name__ == "__main__":
    # Test
    DATA_DIR = Path("/mnt/nas/mala/work/archaeology/data")
    text_paths = list(DATA_DIR.glob("*.txt"))[:5]
    
    vocab = build_vocab(text_paths, vocab_size=1000, min_freq=5)
    save_vocab(vocab)
