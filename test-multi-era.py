#!/usr/bin/env python3
"""Test query interface with multiple eras."""
import sqlite3
import json
import numpy as np
from pathlib import Path

DB_PATH = Path("/home/mala/.openclaw/workspace/archaeology/data/archaeology.db")

def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot / (norm1 * norm2)

def get_vector(word, era):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT vector_json FROM word_vectors WHERE word = ? AND era = ?",
        (word, era)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

def get_neighbors(word, era, n=10):
    target_vec = get_vector(word, era)
    if target_vec is None:
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT word, vector_json FROM word_vectors WHERE era = ?",
        (era,)
    )
    
    similarities = []
    for other_word, vec_json in cursor.fetchall():
        if other_word != word:
            other_vec = json.loads(vec_json)
            sim = cosine_similarity(target_vec, other_vec)
            similarities.append((other_word, sim))
    
    conn.close()
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:n]

def compare_eras(word, era1, era2, n=10):
    neighbors1 = get_neighbors(word, era1, n)
    neighbors2 = get_neighbors(word, era2, n)
    
    set1 = set(w for w, _ in neighbors1)
    set2 = set(w for w, _ in neighbors2)
    
    shared = set1 & set2
    only_era1 = set1 - set2
    only_era2 = set2 - set1
    
    return {
        'shared': shared,
        'only_era1': only_era1,
        'only_era2': only_era2,
        'neighbors1': neighbors1,
        'neighbors2': neighbors2,
    }

# Test queries
eras = ["pre-1800", "1800-1850", "1850-1900"]

test_words = ["love", "man", "woman", "war", "king", "god", "nature", "soul"]

for word in test_words:
    print(f"\n{'='*50}")
    print(f"Word: '{word}'")
    print('='*50)
    
    for era in eras:
        neighbors = get_neighbors(word, era, 5)
        if neighbors:
            neighbor_str = ", ".join([w for w, _ in neighbors])
            print(f"  {era}: {neighbor_str}")

# Cross-era comparison
print("\n" + "="*50)
print("CROSS-ERA COMPARISON: 'war'")
print("="*50)

result = compare_eras("war", "pre-1800", "1850-1900", 10)
print(f"\nShared ({len(result['shared'])}):")
for w in sorted(result['shared']):
    print(f"  {w}")

print(f"\nOnly in pre-1800 ({len(result['only_era1'])}):")
for w in list(result['only_era1'])[:5]:
    print(f"  {w}")

print(f"\nOnly in 1850-1900 ({len(result['only_era2'])}):")
for w in list(result['only_era2'])[:5]:
    print(f"  {w}")

print("\n" + "="*50)
print("CROSS-ERA COMPARISON: 'love'")
print("="*50)

result = compare_eras("love", "1800-1850", "1850-1900", 10)
print(f"\nShared ({len(result['shared'])}):")
for w in sorted(result['shared']):
    print(f"  {w}")

print(f"\nOnly in 1800-1850 ({len(result['only_era1'])}):")
for w in list(result['only_era1'])[:5]:
    print(f"  {w}")

print(f"\nOnly in 1850-1900 ({len(result['only_era2'])}):")
for w in list(result['only_era2'])[:5]:
    print(f"  {w}")
