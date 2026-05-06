#!/usr/bin/env python3
"""
Query interface for archaeology pilot.
Find nearest neighbors and semantic drift between eras.
"""

import sqlite3
import json
import numpy as np
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "archaeology.db"


def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot / (norm1 * norm2)


def get_vector(word: str, era: str):
    """Get vector for a word in a specific era."""
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


def get_neighbors(word: str, era: str, n: int = 10):
    """
    Find n nearest neighbors for a word in a specific era.
    """
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
    
    # Sort by similarity descending
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:n]


def compare_eras(word: str, era1: str, era2: str, n: int = 10):
    """
    Compare a word's neighbors between two eras.
    Shows which neighbors are shared vs unique to each era.
    """
    neighbors1 = get_neighbors(word, era1, n)
    neighbors2 = get_neighbors(word, era2, n)
    
    set1 = set(w for w, _ in neighbors1)
    set2 = set(w for w, _ in neighbors2)
    
    shared = set1 & set2
    only_era1 = set1 - set2
    only_era2 = set2 - set1
    
    return {
        'era1': era1,
        'era2': era2,
        'neighbors1': neighbors1,
        'neighbors2': neighbors2,
        'shared': shared,
        'only_era1': only_era1,
        'only_era2': only_era2,
    }


def interactive_query():
    """Interactive query loop."""
    print("=" * 50)
    print("Archaeology Pilot Query Interface")
    print("=" * 50)
    print("\nAvailable commands:")
    print("  neighbors <word> <era> [n]  - Find nearest neighbors")
    print("  compare <word> <era1> <era2> [n]  - Compare between eras")
    print("  eras                        - List available eras")
    print("  quit                        - Exit")
    print()
    
    while True:
        try:
            cmd = input("> ").strip().lower()
            if not cmd:
                continue
            
            parts = cmd.split()
            
            if parts[0] == "quit":
                break
            
            elif parts[0] == "eras":
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT era FROM word_vectors ORDER BY era")
                for row in cursor.fetchall():
                    print(f"  {row[0]}")
                conn.close()
            
            elif parts[0] == "neighbors" and len(parts) >= 3:
                word = parts[1]
                era = parts[2]
                n = int(parts[3]) if len(parts) > 3 else 10
                
                print(f"\n'{word}' in {era}:")
                neighbors = get_neighbors(word, era, n)
                if not neighbors:
                    print("  (no data)")
                for i, (neighbor, sim) in enumerate(neighbors, 1):
                    print(f"  {i}. {neighbor:<15} (sim: {sim:.3f})")
                print()
            
            elif parts[0] == "compare" and len(parts) >= 4:
                word = parts[1]
                era1 = parts[2]
                era2 = parts[3]
                n = int(parts[4]) if len(parts) > 4 else 10
                
                result = compare_eras(word, era1, era2, n)
                print(f"\n'{word}' comparison:")
                print(f"\nShared neighbors ({len(result['shared'])}):")
                for w in sorted(result['shared'])[:10]:
                    print(f"  {w}")
                if len(result['shared']) > 10:
                    print(f"  ... and {len(result['shared']) - 10} more")
                
                print(f"\nOnly in {era1} ({len(result['only_era1'])}):")
                for w in sorted(result['only_era1'])[:5]:
                    print(f"  {w}")
                
                print(f"\nOnly in {era2} ({len(result['only_era2'])}):")
                for w in sorted(result['only_era2'])[:5]:
                    print(f"  {w}")
                print()
            
            else:
                print("Unknown command. Type 'quit' to exit.")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("Goodbye!")


if __name__ == "__main__":
    interactive_query()
