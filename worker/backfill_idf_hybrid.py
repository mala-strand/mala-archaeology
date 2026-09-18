#!/usr/bin/env python3
"""
Backfill IDF-hybrid classifications to dream_reflections table.

Uses corpus-based IDF weights and the v2 taxonomy to compute
idf_hybrid_primary, idf_hybrid_method, idf_hybrid_secondary
for all dreams that have reflections.
"""

import sys
import math
import json
import sqlite3
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, ERA_ORDER
from archetype_taxonomy_v2 import ARCHETYPES_V2, extract_words_from_dream, classify_with_v2
from keyword_idf_scorer import compute_keyword_idf_from_corpus, score_dream_keyword_idf, classify_from_scores


def main():
    corpus_dir = Path(__file__).parent.parent / "data" / "phase1"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("[1] Computing IDF weights from corpus...")
    idf_weights, N, df = compute_keyword_idf_from_corpus(corpus_dir, ARCHETYPES_V2)
    print(f"    Corpus: {N} books, {len(idf_weights)} keywords")

    # Cache IDF weights to JSON for reuse
    cache_path = Path(__file__).parent.parent / "cache" / "keyword_idf_weights.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump(idf_weights, f, indent=2)
    print(f"    Cached to {cache_path}")

    # Load all dreams with their reflection rows
    cursor.execute("""
        SELECT d.id, d.seed_word, d.start_era, d.dream_text, dr.id as ref_id
        FROM dreams d
        LEFT JOIN dream_reflections dr ON d.id = dr.dream_id
        ORDER BY d.id
    """)
    rows = cursor.fetchall()
    print(f"[2] Loaded {len(rows)} dreams")

    updated = 0
    inserted = 0

    for row in rows:
        dream_id, seed, start_era, dream_text, ref_id = row
        words = extract_words_from_dream(dream_text)
        word_set = set(words)
        if seed:
            word_set.discard(seed.lower())
        words_clean = list(word_set)

        # Raw keyword scores (fallback)
        raw_scores = classify_with_v2(words_clean, seed, start_era)['all_scores']
        raw_res = classify_from_scores(raw_scores)

        # IDF-weighted keyword scores
        idf_scores = score_dream_keyword_idf(words_clean, ARCHETYPES_V2, idf_weights, seed)
        idf_res = classify_from_scores(idf_scores)

        # Hybrid: IDF first, raw fallback if unclassifiable
        if idf_res['primary'][0] != 'unclassifiable':
            hybrid_res = idf_res
            method = 'idf-keyword'
        else:
            hybrid_res = raw_res
            method = 'raw-fallback'

        primary = hybrid_res['primary'][0]
        secondary = hybrid_res['secondary'][0] if hybrid_res['secondary'] else None

        if ref_id:
            cursor.execute("""
                UPDATE dream_reflections
                SET idf_hybrid_primary = ?,
                    idf_hybrid_method = ?,
                    idf_hybrid_secondary = ?
                WHERE id = ?
            """, (primary, method, secondary, ref_id))
            updated += 1
        else:
            # No reflection exists — create a minimal one
            cursor.execute("""
                INSERT INTO dream_reflections
                (dream_id, reflection_text, idf_hybrid_primary, idf_hybrid_method, idf_hybrid_secondary)
                VALUES (?, ?, ?, ?, ?)
            """, (dream_id, f"[IDF backfill — no prior reflection]", primary, method, secondary))
            inserted += 1

    conn.commit()
    conn.close()

    print(f"[3] Done: {updated} updated, {inserted} inserted")
    print(f"    Total: {updated + inserted} dreams now have IDF-hybrid classifications")


if __name__ == "__main__":
    main()
