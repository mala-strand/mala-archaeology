#!/usr/bin/env python3
"""
Confidence scorer for archetype classifications.

Computes classification margin for all dreams using both stored raw scores
and live IDF-weighted scores. Flags low-confidence classifications and
identifies dreams that are "decided by a single keyword" or have razor-thin
margins.

Usage:
    python3 worker/confidence_scorer.py [--threshold <n>] [--tiers] [--chaos] [--full]

Options:
    --threshold  Margin threshold for flagging (default: 1.0 IDF units)
    --tiers      Show distribution across confidence tiers
    --chaos      Focus on chaos-classified dreams specifically
    --full       Analyze all 200 dreams (recomputes IDF margins for those
                 without stored v2_scores)
"""

import sys
import json
import sqlite3
import argparse
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH
from archetype_taxonomy_v2 import ARCHETYPES_V2, extract_words_from_dream, classify_with_v2
from keyword_idf_scorer import score_dream_keyword_idf, classify_from_scores


def load_cached_idf():
    """Load cached IDF weights."""
    cache_path = Path(__file__).parent.parent / "cache" / "keyword_idf_weights.json"
    if cache_path.exists():
        with open(cache_path) as f:
            return json.load(f)
    return None


def compute_margin_from_scores(scores_dict):
    """
    Compute classification margin from a scores dict.
    Returns (primary, primary_score, secondary, secondary_score, margin)
    """
    sorted_scores = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)
    if not sorted_scores:
        return None, 0, None, 0, 0

    primary, primary_score = sorted_scores[0]
    secondary, secondary_score = sorted_scores[1] if len(sorted_scores) > 1 else (None, 0)
    margin = primary_score - secondary_score

    return primary, primary_score, secondary, secondary_score, margin


def confidence_tier(margin, rel_margin=None):
    """Map margin to confidence tier.
    
    In IDF-weighted space, absolute margins are small because IDF weights
    are typically < 1.0. We use relative margin (margin/primary_score)
    as the primary signal when available.
    """
    if rel_margin is not None:
        if rel_margin >= 0.50:
            return "HIGH"
        elif rel_margin >= 0.30:
            return "MEDIUM"
        elif rel_margin >= 0.15:
            return "LOW"
        else:
            return "TENTATIVE"
    # Fallback to absolute margins (for raw-keyword scores)
    if margin >= 2.0:
        return "HIGH"
    elif margin >= 1.0:
        return "MEDIUM"
    elif margin >= 0.5:
        return "LOW"
    else:
        return "TENTATIVE"


def analyze_dreams(rows, idf_weights, use_idf=True):
    """Analyze a batch of dreams. Returns list of analysis dicts."""
    results = []
    for row in rows:
        dream_id, seed, temp, jumps, primary, method, secondary, v2_scores_json, dream_text = row

        # Raw scores from stored JSON if available
        raw_margin = None
        if v2_scores_json:
            raw_scores = json.loads(v2_scores_json)
            _, _, _, _, raw_margin = compute_margin_from_scores(raw_scores)

        # Compute IDF-weighted scores live
        words = extract_words_from_dream(dream_text)
        word_set = set(words)
        if seed:
            word_set.discard(seed.lower())
        words_clean = list(word_set)

        if use_idf and idf_weights:
            idf_scores = score_dream_keyword_idf(words_clean, ARCHETYPES_V2, idf_weights, seed)
            _, primary_score, sec_name, sec_score, margin = compute_margin_from_scores(idf_scores)
            rel_margin = margin / primary_score if primary_score > 0 else 0.0
        else:
            # Fall back to raw scores
            if v2_scores_json:
                raw_scores = json.loads(v2_scores_json)
                _, primary_score, sec_name, sec_score, margin = compute_margin_from_scores(raw_scores)
            else:
                margin = 0
                primary_score = 0
                sec_name = None
                sec_score = 0
            rel_margin = None

        tier = confidence_tier(margin, rel_margin)

        results.append({
            'id': dream_id,
            'seed': seed,
            'temp': temp,
            'jumps': jumps,
            'stored_primary': primary,
            'stored_method': method,
            'stored_secondary': secondary,
            'primary_score': primary_score,
            'secondary': sec_name,
            'secondary_score': sec_score,
            'margin': margin,
            'raw_margin': raw_margin,
            'tier': tier,
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Confidence scorer for dream archetypes")
    parser.add_argument("--threshold", type=float, default=1.0, help="Margin threshold for flagging")
    parser.add_argument("--tiers", action="store_true", help="Show tier distribution")
    parser.add_argument("--chaos", action="store_true", help="Focus on chaos-classified dreams")
    parser.add_argument("--full", action="store_true", help="Analyze all 200 dreams with live IDF scoring")
    args = parser.parse_args()

    idf_weights = load_cached_idf()
    if not idf_weights:
        print("ERROR: No cached IDF weights found. Run keyword_idf_scorer.py or backfill_idf_hybrid.py first.")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 70)
    print("Archetype Classification Confidence Scorer")
    print("=" * 70)

    if args.full:
        # Load ALL dreams with their text for live IDF scoring
        cursor.execute("""
            SELECT d.id, d.seed_word, d.temperature, d.jump_count,
                   dr.idf_hybrid_primary, dr.idf_hybrid_method, dr.idf_hybrid_secondary,
                   dr.v2_scores, d.dream_text
            FROM dreams d
            JOIN dream_reflections dr ON d.id = dr.dream_id
            ORDER BY d.id
        """)
    else:
        # Only dreams with stored v2_scores
        cursor.execute("""
            SELECT d.id, d.seed_word, d.temperature, d.jump_count,
                   dr.idf_hybrid_primary, dr.idf_hybrid_method, dr.idf_hybrid_secondary,
                   dr.v2_scores, d.dream_text
            FROM dreams d
            JOIN dream_reflections dr ON d.id = dr.dream_id
            WHERE dr.v2_scores IS NOT NULL
            ORDER BY d.id
        """)

    rows = cursor.fetchall()
    use_idf = args.full
    results = analyze_dreams(rows, idf_weights, use_idf=use_idf)

    scoring_label = "IDF-weighted" if use_idf else "stored raw-keyword"
    print(f"\nAnalyzed {len(results)} dreams using {scoring_label} margins\n")

    # Summary statistics
    margins = [r['margin'] for r in results]
    avg_margin = sum(margins) / len(margins) if margins else 0
    min_margin = min(margins) if margins else 0
    max_margin = max(margins) if margins else 0
    median_margin = sorted(margins)[len(margins) // 2] if margins else 0

    low_confidence = [r for r in results if r['margin'] < args.threshold]

    print(f"--- Margin Statistics ({scoring_label}) ---")
    print(f"  Average margin:    {avg_margin:.2f}")
    print(f"  Min margin:        {min_margin:.2f}")
    print(f"  Max margin:        {max_margin:.2f}")
    print(f"  Median margin:     {median_margin:.2f}")
    print(f"  Flagged (<{args.threshold}):    {len(low_confidence)} / {len(results)} ({100*len(low_confidence)/len(results):.1f}%)")

    if args.tiers:
        tier_counts = Counter(r['tier'] for r in results)
        method_tiers = defaultdict(lambda: Counter())
        method_counts = Counter(r['stored_method'] for r in results)

        for r in results:
            method_tiers[r['stored_method']][r['tier']] += 1

        print(f"\n--- Confidence Tier Distribution ---")
        for tier in ["HIGH", "MEDIUM", "LOW", "TENTATIVE"]:
            c = tier_counts[tier]
            pct = 100 * c / len(results)
            bar = "█" * int(c / 3)
            print(f"  {tier:12s}: {c:3d} ({pct:5.1f}%) {bar}")

        print(f"\n--- Tier Distribution by Method ---")
        for method in sorted(method_tiers.keys()):
            total = method_counts[method]
            print(f"\n  {method} (n={total}):")
            for tier in ["HIGH", "MEDIUM", "LOW", "TENTATIVE"]:
                c = method_tiers[method][tier]
                pct = 100 * c / total if total else 0
                print(f"    {tier:12s}: {c:3d} ({pct:5.1f}%)")

    # Low-confidence detail
    if low_confidence:
        print(f"\n--- Low-Confidence Dreams (margin < {args.threshold}) ---")
        print(f"{'ID':>4} {'Seed':>12} {'StoredPrimary':>18} {'Method':>14} {'Score':>6} {'2nd':>18} {'2ndSc':>6} {'Margin':>7} {'Tier':>10}")
        print("-" * 103)

        for d in sorted(low_confidence, key=lambda x: x['margin']):
            print(f"{d['id']:4d} {str(d['seed']):>12} {d['stored_primary']:>18} {d['stored_method']:>14} "
                  f"{d['primary_score']:6.2f} {str(d['secondary']):>18} {d['secondary_score']:6.2f} "
                  f"{d['margin']:7.2f} {d['tier']:>10}")

    # Focus on chaos if requested
    if args.chaos:
        print(f"\n--- Chaos-Classified Dreams (all, sorted by margin) ---")
        chaos_results = [r for r in results if r['stored_primary'] == 'chaos']
        print(f"{'ID':>4} {'Seed':>12} {'Temp':>5} {'Jumps':>5} {'Method':>14} {'Score':>6} {'2nd':>18} {'2ndSc':>6} {'Margin':>7} {'Tier':>10}")
        print("-" * 102)
        for d in sorted(chaos_results, key=lambda x: x['margin']):
            print(f"{d['id']:4d} {str(d['seed']):>12} {d['temp']:5.1f} {d['jumps']:5d} {d['stored_method']:>14} "
                  f"{d['primary_score']:6.2f} {str(d['secondary']):>18} {d['secondary_score']:6.2f} "
                  f"{d['margin']:7.2f} {d['tier']:>10}")

    # Special: dreams where raw margin and IDF margin diverge significantly
    if use_idf:
        divergent = []
        for r in results:
            if r['raw_margin'] is not None and abs(r['margin'] - r['raw_margin']) >= 1.0:
                divergent.append(r)
        if divergent:
            print(f"\n--- Dreams with Raw/IDF Margin Divergence (≥1.0) ---")
            print(f"{'ID':>4} {'Seed':>12} {'Primary':>18} {'RawMarg':>7} {'IDFMarg':>7} {'Diff':>6}")
            print("-" * 60)
            for d in sorted(divergent, key=lambda x: abs(x['margin'] - x['raw_margin']), reverse=True):
                diff = d['margin'] - d['raw_margin']
                print(f"{d['id']:4d} {str(d['seed']):>12} {d['stored_primary']:>18} {d['raw_margin']:7.2f} {d['margin']:7.2f} {diff:+6.2f}")

    conn.close()
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
