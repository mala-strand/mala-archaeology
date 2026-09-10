#!/usr/bin/env python3
"""Analyze unclassifiable dreams to understand tie patterns and coverage gaps."""
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from archetype_taxonomy_v2 import ARCHETYPES_V2, extract_words_from_dream, classify_with_v2

DB_PATH = '/mnt/nas/mala/work/archaeology/data/archaeology_phase1_clean.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    SELECT d.id, d.seed_word, d.start_era, d.dream_text, dr.v2_scores
    FROM dreams d
    JOIN dream_reflections dr ON d.id = dr.dream_id
    WHERE dr.primary_archetype_v2 = 'unclassifiable'
    ORDER BY d.id
""")

unclassifiable = cursor.fetchall()
print(f"Unclassifiable dreams: {len(unclassifiable)}\n")

tie_patterns = Counter()
tied_archetype_counts = Counter()
for dream_id, seed, era, text, v2_scores_json in unclassifiable:
    words = extract_words_from_dream(text)
    scores = classify_with_v2(words, seed, era)['all_scores']
    max_score = max(scores.values()) if scores else 0
    if max_score == 0:
        tie_patterns['ZERO_SIGNAL'] += 1
        continue
    tied = sorted([a for a, s in scores.items() if s == max_score])
    tie_key = ','.join(tied)
    tie_patterns[tie_key] += 1
    for a in tied:
        tied_archetype_counts[a] += 1

print("=== TIE PATTERNS (top 15) ===")
for pattern, count in tie_patterns.most_common(15):
    print(f"  {count:2d}x: {pattern}")

print(f"\n=== ARCHETYPES MOST OFTEN TIED ===")
for arch, count in tied_archetype_counts.most_common():
    print(f"  {arch:25s}: {count:2d}")

all_keywords = set()
for keywords in ARCHETYPES_V2.values():
    all_keywords.update(keywords)

uncovered_words = Counter()
for dream_id, seed, era, text, v2_scores_json in unclassifiable:
    words = extract_words_from_dream(text)
    for w in set(words):
        if w not in all_keywords:
            uncovered_words[w] += 1

print(f"\n=== TOP UNCOVERED WORDS (in unclassifiable dreams, not in any archetype list) ===")
for w, count in uncovered_words.most_common(40):
    print(f"  {w:20s}: {count:2d} dreams")

print(f"\n=== KEYWORD LIST SIZES ===")
for arch, keywords in sorted(ARCHETYPES_V2.items(), key=lambda x: len(x[1])):
    print(f"  {arch:25s}: {len(keywords):2d} keywords")

conn.close()
