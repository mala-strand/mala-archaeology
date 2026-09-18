#!/usr/bin/env python3
"""
Backfill confidence tiers to dream_reflections table.

Adds confidence_tier, confidence_margin, confidence_relative columns
and populates them for all dreams using live IDF-weighted scoring.

Usage:
    python3 worker/backfill_confidence.py [--dry-run]
"""

import sys
import json
import sqlite3
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH
from archetype_taxonomy_v2 import ARCHETYPES_V2, extract_words_from_dream
from keyword_idf_scorer import score_dream_keyword_idf


def load_cached_idf():
    cache_path = Path(__file__).parent.parent / "cache" / "keyword_idf_weights.json"
    if cache_path.exists():
        with open(cache_path) as f:
            return json.load(f)
    return None


def compute_margin_from_scores(scores_dict):
    sorted_scores = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)
    if not sorted_scores:
        return None, 0, None, 0, 0
    primary, primary_score = sorted_scores[0]
    secondary, secondary_score = sorted_scores[1] if len(sorted_scores) > 1 else (None, 0)
    margin = primary_score - secondary_score
    return primary, primary_score, secondary, secondary_score, margin


def confidence_tier(rel_margin):
    if rel_margin >= 0.50:
        return "HIGH"
    elif rel_margin >= 0.30:
        return "MEDIUM"
    elif rel_margin >= 0.15:
        return "LOW"
    else:
        return "TENTATIVE"


def add_columns(cursor):
    """Add confidence columns if they don't exist."""
    cursor.execute("PRAGMA table_info(dream_reflections)")
    existing = {row[1] for row in cursor.fetchall()}

    additions = []
    if "confidence_tier" not in existing:
        additions.append("ALTER TABLE dream_reflections ADD COLUMN confidence_tier TEXT")
    if "confidence_margin" not in existing:
        additions.append("ALTER TABLE dream_reflections ADD COLUMN confidence_margin REAL")
    if "confidence_relative" not in existing:
        additions.append("ALTER TABLE dream_reflections ADD COLUMN confidence_relative REAL")

    for sql in additions:
        cursor.execute(sql)
        print(f"  Added column: {sql}")

    if not additions:
        print("  Confidence columns already exist.")


def main():
    parser = argparse.ArgumentParser(description="Backfill confidence tiers to DB")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without writing")
    args = parser.parse_args()

    idf_weights = load_cached_idf()
    if not idf_weights:
        print("ERROR: No cached IDF weights found. Run keyword_idf_scorer.py first.")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Ensuring confidence columns exist...")
    add_columns(cursor)

    # Load all dreams with text
    cursor.execute("""
        SELECT d.id, d.seed_word, d.temperature, d.jump_count,
               dr.idf_hybrid_primary, dr.idf_hybrid_method, dr.idf_hybrid_secondary,
               dr.v2_scores, d.dream_text
        FROM dreams d
        JOIN dream_reflections dr ON d.id = dr.dream_id
        ORDER BY d.id
    """)
    rows = cursor.fetchall()

    print(f"\nComputing confidence for {len(rows)} dreams...")

    updates = []
    for row in rows:
        dream_id, seed, temp, jumps, primary, method, secondary, v2_scores_json, dream_text = row

        words = extract_words_from_dream(dream_text)
        word_set = set(words)
        if seed:
            word_set.discard(seed.lower())
        words_clean = list(word_set)

        idf_scores = score_dream_keyword_idf(words_clean, ARCHETYPES_V2, idf_weights, seed)
        _, primary_score, sec_name, sec_score, margin = compute_margin_from_scores(idf_scores)
        rel_margin = margin / primary_score if primary_score > 0 else 0.0
        tier = confidence_tier(rel_margin)

        updates.append((tier, margin, rel_margin, dream_id))

    if args.dry_run:
        print("\n--- DRY RUN ---")
        tier_counts = {}
        for tier, margin, rel_margin, dream_id in updates:
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            if tier == "TENTATIVE":
                print(f"  Dream {dream_id}: TENTATIVE (margin={margin:.2f}, rel={rel_margin:.2%})")
        print(f"\nWould update {len(updates)} rows.")
        for tier, count in sorted(tier_counts.items()):
            print(f"  {tier}: {count}")
    else:
        cursor.executemany("""
            UPDATE dream_reflections
            SET confidence_tier = ?,
                confidence_margin = ?,
                confidence_relative = ?
            WHERE dream_id = ?
        """, updates)
        conn.commit()

        tier_counts = {}
        for tier, _, _, _ in updates:
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        print(f"\nUpdated {len(updates)} rows.")
        print("\n--- Confidence Tier Distribution ---")
        for tier in ["HIGH", "MEDIUM", "LOW", "TENTATIVE"]:
            count = tier_counts.get(tier, 0)
            pct = 100 * count / len(updates)
            bar = "█" * int(count / 3)
            print(f"  {tier:12s}: {count:3d} ({pct:5.1f}%) {bar}")

        # Show tentative dreams
        print("\n--- TENTATIVE Dreams ---")
        for tier, margin, rel_margin, dream_id in updates:
            if tier == "TENTATIVE":
                print(f"  Dream {dream_id}: margin={margin:.2f}, rel={rel_margin:.2%}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
