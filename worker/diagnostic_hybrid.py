#!/usr/bin/env python3
"""Diagnostic: inspect why a dream got its hybrid classification."""

import sys
import json
import sqlite3
from pathlib import Path
from collections import Counter

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, ERA_ORDER
from archetype_taxonomy_v2 import ARCHETYPES_V2, extract_words_from_dream, classify_with_v2
from semantic_scorer import (
    load_era_vectors, build_archetype_keyword_vectors, cosine_similarity, compute_idf_weights
)


def diagnose_dream(dream_id, era="1850-1900"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, seed_word, start_era, dream_text FROM dreams WHERE id = ?", (dream_id,))
    row = cursor.fetchone()
    if not row:
        print(f"Dream {dream_id} not found")
        return

    dream_id, seed, start_era, dream_text = row
    words = extract_words_from_dream(dream_text)
    word_set = set(words)
    if seed:
        word_set.discard(seed.lower())
    dream_words = list(word_set)

    # Keyword classification
    kw_result = classify_with_v2(dream_words, seed, start_era)

    # Semantic setup
    era_vectors = load_era_vectors(conn, era)
    archetype_kvecs = build_archetype_keyword_vectors(conn, era)
    idf_weights, _ = compute_idf_weights(conn)

    # Flatten keywords
    all_kvecs = []
    for archetype, kvecs in archetype_kvecs.items():
        for keyword, vec in kvecs:
            all_kvecs.append((archetype, keyword, vec))

    # Track what each dream word matched to
    matches = []
    for word in dream_words:
        if word not in era_vectors:
            continue
        word_vec = era_vectors[word]
        best_sim = -1.0
        best_archetype = None
        best_keyword = None
        for archetype, keyword, vec in all_kvecs:
            sim = cosine_similarity(word_vec, vec)
            if sim > best_sim:
                best_sim = sim
                best_archetype = archetype
                best_keyword = keyword
        if best_archetype and best_sim > 0.5:
            idf = idf_weights.get(word, 1.0)
            matches.append((word, best_archetype, best_keyword, best_sim, idf))

    conn.close()

    print(f"\n{'='*70}")
    print(f"DIAGNOSTIC: Dream #{dream_id} | Seed: {seed} | Start: {start_era}")
    print(f"{'='*70}")

    print(f"\nKeyword result: {kw_result['primary'][0]} (score: {kw_result['primary'][1]})")
    if kw_result['secondary']:
        print(f"  Secondary: {kw_result['secondary'][0]} (score: {kw_result['secondary'][1]})")
    print(f"  All keyword counts: {dict(sorted(kw_result['all_scores'].items(), key=lambda x: -x[1])[:8])}")

    print(f"\nSemantic matches (word → archetype via closest keyword, sim > 0.5):")
    # Group by archetype
    archetype_matches = Counter()
    archetype_details = {}
    for word, arch, keyword, sim, idf in matches:
        archetype_matches[arch] += idf
        if arch not in archetype_details:
            archetype_details[arch] = []
        archetype_details[arch].append((word, keyword, sim, idf))

    print(f"\n  Archetype scores (IDF-weighted):")
    for arch, score in archetype_matches.most_common():
        print(f"    {arch:20s}: {score:8.2f}")

    print(f"\n  Top matches per archetype:")
    for arch in archetype_matches.most_common(3):
        arch_name = arch[0]
        details = sorted(archetype_details[arch_name], key=lambda x: -x[3])[:5]
        print(f"\n    {arch_name}:")
        for word, keyword, sim, idf in details:
            print(f"      {word:15s} → {keyword:15s} (sim={sim:.3f}, idf={idf:.2f})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 diagnostic_hybrid.py <dream_id> [era]")
        sys.exit(1)
    dream_id = int(sys.argv[1])
    era = sys.argv[2] if len(sys.argv) > 2 else "1850-1900"
    diagnose_dream(dream_id, era)
