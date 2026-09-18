#!/usr/bin/env python3
"""Investigate why 'chaos' archetype has low jumps and low temperature."""

import sys, json, sqlite3
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))
from archetype_taxonomy_v2 import ARCHETYPES_V2, extract_words_from_dream, classify_with_v2
from keyword_idf_scorer import compute_keyword_idf_from_corpus, score_dream_keyword_idf, classify_from_scores

corpus_dir = Path(__file__).parent.parent / 'data' / 'phase1'
idf_weights, N, df = compute_keyword_idf_from_corpus(corpus_dir, ARCHETYPES_V2)

conn = sqlite3.connect('../data/archaeology_phase1_clean.db')
c = conn.cursor()

# Get all chaos-classified dreams
c.execute("""
    SELECT d.id, d.seed_word, d.start_era, d.temperature, d.jump_count, d.dream_text,
           dr.idf_hybrid_primary, dr.idf_hybrid_method, dr.idf_hybrid_secondary, dr.v2_scores
    FROM dreams d
    JOIN dream_reflections dr ON d.id = dr.dream_id
    WHERE dr.idf_hybrid_primary = 'chaos'
    ORDER BY d.jump_count
""")

chaos_dreams = c.fetchall()
print(f"=== CHAOS ARCHETYPE INVESTIGATION ===")
print(f"Found {len(chaos_dreams)} dreams classified as 'chaos'\n")

for row in chaos_dreams:
    dream_id, seed, start_era, temp, jumps, text, primary, method, secondary, v2_scores_json = row
    words = extract_words_from_dream(text)
    word_set = set(words)
    if seed:
        word_set.discard(seed.lower())
    words_clean = list(word_set)
    
    raw_scores = classify_with_v2(words_clean, seed, None)['all_scores']
    idf_scores = score_dream_keyword_idf(words_clean, ARCHETYPES_V2, idf_weights, seed)
    
    raw_res = classify_from_scores(raw_scores)
    idf_res = classify_from_scores(idf_scores)
    
    print(f"Dream #{dream_id} | seed: '{seed}' | era: {start_era} | temp: {temp} | jumps: {jumps}")
    print(f"  Stored method: {method} | secondary: {secondary}")
    print(f"  Raw primary: {raw_res['primary']} | IDF primary: {idf_res['primary']}")
    
    # Show raw vs IDF top scores
    raw_top = sorted(raw_scores.items(), key=lambda x: -x[1])[:5]
    idf_top = sorted(idf_scores.items(), key=lambda x: -x[1])[:5]
    print(f"  Raw top 5: {raw_top}")
    print(f"  IDF top 5: {idf_top}")
    
    # Which chaos keywords are present?
    chaos_present = [w for w in words_clean if w in ARCHETYPES_V2['chaos']]
    print(f"  Chaos keywords present: {chaos_present}")
    
    # Check if any other archetype has much higher score
    print()

# Now analyze ALL dreams to see jump/temp distribution by archetype
print("\n=== JUMP/TEMP DISTRIBUTION BY ARCHETYPE ===")
c.execute("""
    SELECT dr.idf_hybrid_primary, 
           AVG(d.jump_count) as avg_jumps, 
           AVG(d.temperature) as avg_temp,
           COUNT(*) as n
    FROM dreams d
    JOIN dream_reflections dr ON d.id = dr.dream_id
    WHERE dr.idf_hybrid_primary IS NOT NULL
    GROUP BY dr.idf_hybrid_primary
    ORDER BY avg_jumps
""")

for archetype, avg_jumps, avg_temp, n in c.fetchall():
    print(f"  {archetype:25s}: jumps={avg_jumps:5.1f}  temp={avg_temp:4.2f}  n={n:3d}")

conn.close()
