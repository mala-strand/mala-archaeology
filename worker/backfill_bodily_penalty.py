#!/usr/bin/env python3
"""
Backfill bodily IDF penalty (×0.25) to dream_reflections.

Uses archetype_taxonomy_v2.score_archetypes_v2_idf() with the default
BODILY_IDF_PENALTY multiplier and persists the new classifications.
"""

import sys
import json
import sqlite3
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, ERA_ORDER
from archetype_taxonomy_v2 import (
    ARCHETYPES_V2,
    extract_words_from_dream,
    score_archetypes_v2_idf,
    load_idf_weights,
    BODILY_IDF_PENALTY,
)
from keyword_idf_scorer import classify_from_scores, score_dream_keyword_idf


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 70)
    print(f"Bodily IDF Penalty Backfill  (penalty = {BODILY_IDF_PENALTY})")
    print("=" * 70)

    # Verify IDF weights are available
    idf_weights = load_idf_weights()
    if not idf_weights:
        print("ERROR: IDF weights not found. Run keyword_idf_scorer.py first.")
        sys.exit(1)
    print(f"\n[1] Loaded IDF weights for {len(idf_weights)} keywords")

    # Add new columns idempotently
    cursor.execute("PRAGMA table_info(dream_reflections)")
    cols = {row[1] for row in cursor.fetchall()}
    new_cols = [
        ("penalized_primary", "TEXT"),
        ("penalized_secondary", "TEXT"),
        ("penalized_method", "TEXT"),
        ("penalized_scores", "TEXT"),
    ]
    for col_name, col_type in new_cols:
        if col_name not in cols:
            cursor.execute(f"ALTER TABLE dream_reflections ADD COLUMN {col_name} {col_type}")
            print(f"    Added column: {col_name}")
    conn.commit()

    # Load all dreams
    cursor.execute("""
        SELECT d.id, d.seed_word, d.start_era, d.dream_text, dr.id as ref_id,
               dr.idf_hybrid_primary, dr.idf_hybrid_secondary
        FROM dreams d
        LEFT JOIN dream_reflections dr ON d.id = dr.dream_id
        ORDER BY d.id
    """)
    rows = cursor.fetchall()
    print(f"\n[2] Loaded {len(rows)} dreams")

    updated = 0
    changed = 0
    bodily_before = Counter()
    bodily_after = Counter()

    for row in rows:
        dream_id, seed, start_era, dream_text, ref_id, old_pri, old_sec = row
        words = extract_words_from_dream(dream_text)
        word_set = set(words)
        if seed:
            word_set.discard(seed.lower())
        words_clean = list(word_set)

        # Penalized IDF score
        penalized_scores = score_archetypes_v2_idf(words_clean)
        penalized_res = classify_from_scores(penalized_scores)

        # Fallback to raw if still unclassifiable
        if penalized_res['primary'][0] == 'unclassifiable':
            from archetype_taxonomy_v2 import score_archetypes_v2
            raw_scores = score_archetypes_v2(words_clean)
            penalized_res = classify_from_scores(raw_scores)
            method = 'raw-fallback'
        else:
            method = 'idf-penalized'

        primary = penalized_res['primary'][0]
        secondary = penalized_res['secondary'][0] if penalized_res['secondary'] else None
        scores_json = json.dumps(penalized_res['all_scores'])

        if ref_id:
            cursor.execute("""
                UPDATE dream_reflections
                SET penalized_primary = ?,
                    penalized_secondary = ?,
                    penalized_method = ?,
                    penalized_scores = ?
                WHERE id = ?
            """, (primary, secondary, method, scores_json, ref_id))
            updated += 1
        else:
            cursor.execute("""
                INSERT INTO dream_reflections
                (dream_id, reflection_text, penalized_primary, penalized_secondary,
                 penalized_method, penalized_scores)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (dream_id, "[Penalized backfill]", primary, secondary, method, scores_json))
            updated += 1

        if old_pri == 'bodily':
            bodily_before[old_pri] += 1
            if primary != old_pri:
                changed += 1
            bodily_after[primary] += 1

    conn.commit()
    conn.close()

    print(f"\n[3] Updated {updated} reflections")

    # Summary
    print(f"\n{'=' * 70}")
    print("Bodily archetype impact")
    print(f"{'=' * 70}")
    print(f"  Dreams previously 'bodily' (idf_hybrid): {sum(bodily_before.values())}")
    print(f"  Dreams reclassified away from 'bodily':   {changed}")
    print(f"  Dreams still 'bodily' (penalized):        {bodily_after.get('bodily', 0)}")
    if changed > 0:
        print(f"\n  Reclassified to:")
        for arch, count in sorted(bodily_after.items(), key=lambda x: x[1], reverse=True):
            if arch != 'bodily':
                print(f"    {arch:25s}: {count}")

    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    main()
