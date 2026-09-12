#!/usr/bin/env python3
"""
Normalize archetype scores by keyword count to reduce structural bias.

Archetypes with more keywords (e.g. natural: 24, domestic: 21) have larger
"surface area" in vector space, giving them more chances to match. This script
compares raw vs normalized distributions.

Normalization methods tested:
- sqrt: divide by sqrt(keyword_count) — shrinks large archetypes moderately
- linear: divide by keyword_count — aggressive flattening
- log: divide by log(keyword_count + 1) — gentle shrink
"""

import sys
import json
import sqlite3
import math
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, ERA_ORDER
from archetype_taxonomy_v2 import ARCHETYPES_V2, classify_with_v2, extract_words_from_dream
from semantic_scorer import (
    load_era_vectors, build_archetype_centroids, build_archetype_keyword_vectors,
    compute_idf_weights, score_dream_nearest_keyword, cosine_similarity
)


def normalize_keyword_scores(scores, method="sqrt"):
    """Normalize keyword-count scores by archetype keyword count."""
    normalized = {}
    for archetype, raw_score in scores.items():
        kw_count = len(ARCHETYPES_V2.get(archetype, []))
        if kw_count == 0:
            normalized[archetype] = 0
            continue
        if method == "sqrt":
            normalized[archetype] = raw_score / math.sqrt(kw_count)
        elif method == "linear":
            normalized[archetype] = raw_score / kw_count
        elif method == "log":
            normalized[archetype] = raw_score / math.log(kw_count + 1)
        else:
            normalized[archetype] = raw_score
    return normalized


def classify_from_scores(scores):
    """Classify using same logic as classify_with_v2 but from pre-computed scores."""
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    max_score = sorted_scores[0][1] if sorted_scores else 0
    top_count = sum(1 for _, s in sorted_scores if abs(s - max_score) < 1e-10)

    if max_score == 0 or top_count >= 2:
        primary = ('unclassifiable', max_score)
        secondary = None
    else:
        primary = sorted_scores[0]
        secondary = sorted_scores[1] if len(sorted_scores) > 1 and sorted_scores[1][1] > 0 else None

    return {
        'primary': primary,
        'secondary': secondary,
        'all_scores': scores,
        'top_5': sorted_scores[:5]
    }


def normalize_semantic_scores(scores, method="sqrt"):
    """Normalize nearest-keyword semantic scores by archetype keyword count."""
    normalized = {}
    for archetype, raw_score in scores.items():
        kw_count = len(ARCHETYPES_V2.get(archetype, []))
        if kw_count == 0:
            normalized[archetype] = 0.0
            continue
        if method == "sqrt":
            normalized[archetype] = raw_score / math.sqrt(kw_count)
        elif method == "linear":
            normalized[archetype] = raw_score / kw_count
        elif method == "log":
            normalized[archetype] = raw_score / math.log(kw_count + 1)
        else:
            normalized[archetype] = raw_score
    return normalized


def compare_normalizations(conn, era="1850-1900"):
    """Compare raw vs normalized classification across all methods."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.id, d.seed_word, d.start_era, d.dream_text,
               dr.hybrid_primary, dr.hybrid_method, dr.v2_scores
        FROM dreams d
        LEFT JOIN dream_reflections dr ON d.id = dr.dream_id
        ORDER BY d.id
    """)
    rows = cursor.fetchall()

    print(f"Loaded {len(rows)} dreams for normalization comparison")
    print(f"Building semantic models for era: {era}")

    era_vectors = load_era_vectors(conn, era)
    archetype_kvecs = build_archetype_keyword_vectors(conn, era)
    idf_weights, dream_count = compute_idf_weights(conn)

    print(f"Era vocabulary: {len(era_vectors)} words")
    print(f"IDF computed from {dream_count} dreams")
    print()

    # Counters for distributions
    methods = {
        'raw_keyword': Counter(),
        'sqrt_keyword': Counter(),
        'linear_keyword': Counter(),
        'raw_semantic': Counter(),
        'sqrt_semantic': Counter(),
        'linear_semantic': Counter(),
        'raw_hybrid': Counter(),
        'sqrt_hybrid': Counter(),
        'linear_hybrid': Counter(),
    }

    flips = {
        'sqrt_keyword': [],
        'linear_keyword': [],
        'sqrt_semantic': [],
        'linear_semantic': [],
        'sqrt_hybrid': [],
        'linear_hybrid': [],
    }

    for row in rows:
        dream_id, seed, start_era, dream_text, current_primary, current_method, v2_scores_json = row
        words = extract_words_from_dream(dream_text)
        word_set = set(words)
        if seed:
            word_set.discard(seed.lower())
        words_clean = list(word_set)

        # --- Keyword scoring ---
        kw_scores = classify_with_v2(words_clean, seed, start_era)['all_scores']
        kw_sqrt = normalize_keyword_scores(kw_scores, "sqrt")
        kw_linear = normalize_keyword_scores(kw_scores, "linear")

        kw_raw_result = classify_from_scores(kw_scores)
        kw_sqrt_result = classify_from_scores(kw_sqrt)
        kw_linear_result = classify_from_scores(kw_linear)

        methods['raw_keyword'][kw_raw_result['primary'][0]] += 1
        methods['sqrt_keyword'][kw_sqrt_result['primary'][0]] += 1
        methods['linear_keyword'][kw_linear_result['primary'][0]] += 1

        if kw_raw_result['primary'][0] != kw_sqrt_result['primary'][0]:
            flips['sqrt_keyword'].append((dream_id, seed, kw_raw_result['primary'][0], kw_sqrt_result['primary'][0]))
        if kw_raw_result['primary'][0] != kw_linear_result['primary'][0]:
            flips['linear_keyword'].append((dream_id, seed, kw_raw_result['primary'][0], kw_linear_result['primary'][0]))

        # --- Semantic scoring ---
        sem_scores = score_dream_nearest_keyword(words_clean, archetype_kvecs, era_vectors, idf_weights)
        sem_sqrt = normalize_semantic_scores(sem_scores, "sqrt")
        sem_linear = normalize_semantic_scores(sem_scores, "linear")

        sem_raw_result = classify_from_scores(sem_scores)
        sem_sqrt_result = classify_from_scores(sem_sqrt)
        sem_linear_result = classify_from_scores(sem_linear)

        methods['raw_semantic'][sem_raw_result['primary'][0]] += 1
        methods['sqrt_semantic'][sem_sqrt_result['primary'][0]] += 1
        methods['linear_semantic'][sem_linear_result['primary'][0]] += 1

        if sem_raw_result['primary'][0] != sem_sqrt_result['primary'][0]:
            flips['sqrt_semantic'].append((dream_id, seed, sem_raw_result['primary'][0], sem_sqrt_result['primary'][0]))
        if sem_raw_result['primary'][0] != sem_linear_result['primary'][0]:
            flips['linear_semantic'].append((dream_id, seed, sem_raw_result['primary'][0], sem_linear_result['primary'][0]))

        # --- Hybrid scoring ---
        # Hybrid: keyword first, if unclassifiable -> semantic
        def make_hybrid(kw_res, sem_res):
            if kw_res['primary'][0] != 'unclassifiable':
                return kw_res
            return sem_res

        raw_hybrid = make_hybrid(kw_raw_result, sem_raw_result)
        sqrt_hybrid = make_hybrid(kw_sqrt_result, sem_sqrt_result)
        linear_hybrid = make_hybrid(kw_linear_result, sem_linear_result)

        methods['raw_hybrid'][raw_hybrid['primary'][0]] += 1
        methods['sqrt_hybrid'][sqrt_hybrid['primary'][0]] += 1
        methods['linear_hybrid'][linear_hybrid['primary'][0]] += 1

        if raw_hybrid['primary'][0] != sqrt_hybrid['primary'][0]:
            flips['sqrt_hybrid'].append((dream_id, seed, raw_hybrid['primary'][0], sqrt_hybrid['primary'][0]))
        if raw_hybrid['primary'][0] != linear_hybrid['primary'][0]:
            flips['linear_hybrid'].append((dream_id, seed, raw_hybrid['primary'][0], linear_hybrid['primary'][0]))

    # --- Print distributions ---
    print("=" * 80)
    print("DISTRIBUTION COMPARISON")
    print("=" * 80)

    for method_name in ['keyword', 'semantic', 'hybrid']:
        print(f"\n--- {method_name.upper()} ---")
        print(f"{'Archetype':<20} {'Raw':>6} {'Sqrt':>6} {'Linear':>6}")
        print("-" * 40)
        all_archetypes = set()
        for m in [f'raw_{method_name}', f'sqrt_{method_name}', f'linear_{method_name}']:
            all_archetypes.update(methods[m].keys())

        for arch in sorted(all_archetypes, key=lambda a: -methods[f'raw_{method_name}'][a]):
            r = methods[f'raw_{method_name}'][arch]
            s = methods[f'sqrt_{method_name}'][arch]
            l = methods[f'linear_{method_name}'][arch]
            marker = ""
            if s != r or l != r:
                marker = "  << CHANGED"
            print(f"{arch:<20} {r:>6} {s:>6} {l:>6}{marker}")

    # --- Print flips ---
    print("\n" + "=" * 80)
    print("FLIPS (dreams that change archetype under normalization)")
    print("=" * 80)

    for flip_name, flip_list in flips.items():
        if flip_list:
            print(f"\n{flip_name}: {len(flip_list)} flips")
            for dream_id, seed, old, new in flip_list[:10]:
                print(f"  #{dream_id} (seed={seed}): {old} -> {new}")
            if len(flip_list) > 10:
                print(f"  ... and {len(flip_list) - 10} more")
        else:
            print(f"\n{flip_name}: 0 flips")

    # --- Entropy / evenness metric ---
    print("\n" + "=" * 80)
    print("DISTRIBUTION EVENNESS (higher = more flat/uniform)")
    print("=" * 80)

    def gini(counter):
        """Compute Gini coefficient for evenness. 0 = perfectly even, 1 = all in one."""
        vals = list(counter.values())
        n = len(vals)
        if n == 0:
            return 0
        mean = sum(vals) / n
        if mean == 0:
            return 0
        diffs = sum(abs(v1 - v2) for v1 in vals for v2 in vals)
        return diffs / (2 * n * n * mean)

    def shannon_entropy(counter):
        """Shannon entropy, normalized by max possible."""
        total = sum(counter.values())
        if total == 0:
            return 0
        probs = [c / total for c in counter.values() if c > 0]
        entropy = -sum(p * math.log(p) for p in probs)
        max_entropy = math.log(len(probs))
        return entropy / max_entropy if max_entropy > 0 else 0

    for method_name in ['keyword', 'semantic', 'hybrid']:
        print(f"\n{method_name.upper()}:")
        for norm in ['raw', 'sqrt', 'linear']:
            key = f"{norm}_{method_name}"
            c = methods[key]
            # Filter out unclassifiable for evenness calculation
            c_classified = Counter({k: v for k, v in c.items() if k != 'unclassifiable'})
            g = gini(c_classified)
            h = shannon_entropy(c_classified)
            unclass = c.get('unclassifiable', 0)
            print(f"  {norm:<7}: Gini={g:.3f}  Entropy={h:.3f}  Unclassifiable={unclass}")

    return methods, flips


def main():
    conn = sqlite3.connect(DB_PATH)
    compare_normalizations(conn, era="1850-1900")
    conn.close()


if __name__ == "__main__":
    main()
