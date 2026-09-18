#!/usr/bin/env python3
"""
Keyword-IDF weighted archetype scorer.

Weights each archetype keyword by its inverse document frequency across the
Phase 1 corpus. Distinctive keywords (e.g. 'sacrament', 'damnation') count more
than generic ones (e.g. 'sitting', 'work').

This is the principled fix for structural bias identified in the Sep 12
normalization experiment — instead of penalizing large archetypes globally,
we reward distinctive keywords locally.
"""

import sys
import math
import json
import sqlite3
import re
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, ERA_ORDER
from archetype_taxonomy_v2 import ARCHETYPES_V2, extract_words_from_dream, classify_with_v2


def compute_keyword_idf_from_corpus(corpus_dir, archetype_keywords):
    """
    Compute IDF for each keyword from the Phase 1 corpus.
    Document = one book. IDF = log(N / df).
    Returns dict: keyword -> idf_weight
    """
    corpus_path = Path(corpus_dir)
    text_files = list(corpus_path.glob("*.txt"))
    N = len(text_files)

    # Collect all unique keywords across all archetypes
    all_keywords = set()
    for kws in archetype_keywords.values():
        all_keywords.update(kws)

    # Count document frequency for each keyword
    df = defaultdict(int)
    for txt_file in text_files:
        try:
            with open(txt_file, "r", encoding="utf-8", errors="ignore") as f:
                # Simple approach: read and lower, check presence
                text = f.read().lower()
                for kw in all_keywords:
                    if kw in text:
                        df[kw] += 1
        except Exception:
            continue

    idf = {}
    for kw in all_keywords:
        # Smooth IDF: log(N / (df + 1)) + 1, or just log(N / df) if df > 0
        doc_freq = df.get(kw, 0)
        if doc_freq > 0:
            idf[kw] = math.log(N / doc_freq)
        else:
            # Keyword not in corpus — give it high distinctiveness
            idf[kw] = math.log(N) + 1.0

    return idf, N, df


def score_dream_keyword_idf(words, archetype_keywords, idf_weights, seed_word=None):
    """
    Score dream using IDF-weighted keyword counting.
    Each keyword match contributes idf(keyword) points instead of 1.
    """
    word_set = set(words)
    if seed_word:
        word_set.discard(seed_word.lower())

    scores = {}
    for archetype, keywords in archetype_keywords.items():
        total = 0.0
        for kw in keywords:
            if kw in word_set:
                total += idf_weights.get(kw, 1.0)
        scores[archetype] = total
    return scores


def classify_from_scores(scores):
    """Classify from pre-computed scores."""
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


def gini_coefficient(counts):
    """Compute Gini coefficient for a list of counts."""
    n = len(counts)
    if n == 0 or sum(counts) == 0:
        return 0.0
    sorted_counts = sorted(counts)
    cumsum = 0
    for i, c in enumerate(sorted_counts, 1):
        cumsum += (2 * i - n - 1) * c
    return cumsum / (n * sum(sorted_counts))


def entropy(counts):
    """Compute Shannon entropy (base 2) for a list of counts."""
    total = sum(counts)
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


def main():
    corpus_dir = Path(__file__).parent.parent / "data" / "phase1"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 70)
    print("Keyword-IDF Weighted Archetype Scorer")
    print("=" * 70)

    # Step 1: Compute IDF weights
    print(f"\n[1] Computing IDF from corpus: {corpus_dir}")
    idf_weights, N, df = compute_keyword_idf_from_corpus(corpus_dir, ARCHETYPES_V2)
    print(f"    Corpus documents: {N}")
    print(f"    Keywords evaluated: {len(idf_weights)}")

    # Show most and least distinctive keywords
    sorted_idf = sorted(idf_weights.items(), key=lambda x: x[1], reverse=True)
    print(f"\n    Most distinctive (highest IDF):")
    for kw, w in sorted_idf[:10]:
        print(f"      {kw:20s}  idf={w:.3f}  df={df.get(kw, 0)}")
    print(f"\n    Least distinctive (lowest IDF):")
    for kw, w in sorted_idf[-10:]:
        print(f"      {kw:20s}  idf={w:.3f}  df={df.get(kw, 0)}")

    # Step 2: Load dreams
    cursor.execute("""
        SELECT d.id, d.seed_word, d.start_era, d.dream_text,
               dr.hybrid_primary, dr.v2_scores
        FROM dreams d
        LEFT JOIN dream_reflections dr ON d.id = dr.dream_id
        ORDER BY d.id
    """)
    rows = cursor.fetchall()
    print(f"\n[2] Loaded {len(rows)} dreams")

    # Step 3: Score all dreams with three methods
    raw_counts = Counter()
    idf_counts = Counter()
    hybrid_counts = Counter()

    flips_idf = []
    flips_hybrid = []

    for row in rows:
        dream_id, seed, start_era, dream_text, hybrid_primary, v2_scores_json = row
        words = extract_words_from_dream(dream_text)
        word_set = set(words)
        if seed:
            word_set.discard(seed.lower())
        words_clean = list(word_set)

        # Raw keyword (current)
        raw_scores = classify_with_v2(words_clean, seed, start_era)['all_scores']
        raw_res = classify_from_scores(raw_scores)

        # IDF-weighted keyword
        idf_scores = score_dream_keyword_idf(words_clean, ARCHETYPES_V2, idf_weights, seed)
        idf_res = classify_from_scores(idf_scores)

        # Hybrid: IDF-keyword first, if unclassifiable -> raw keyword (as fallback)
        if idf_res['primary'][0] != 'unclassifiable':
            hybrid_res = idf_res
        else:
            hybrid_res = raw_res

        raw_counts[raw_res['primary'][0]] += 1
        idf_counts[idf_res['primary'][0]] += 1
        hybrid_counts[hybrid_res['primary'][0]] += 1

        if raw_res['primary'][0] != idf_res['primary'][0]:
            flips_idf.append((dream_id, seed, raw_res['primary'][0], idf_res['primary'][0]))
        if raw_res['primary'][0] != hybrid_res['primary'][0]:
            flips_hybrid.append((dream_id, seed, raw_res['primary'][0], hybrid_res['primary'][0]))

    # Step 4: Print distributions
    all_archetypes = sorted(ARCHETYPES_V2.keys())

    def print_dist(label, counter):
        counts = [counter.get(a, 0) for a in all_archetypes]
        g = gini_coefficient(counts)
        h = entropy(counts)
        print(f"\n{label}")
        print(f"  Gini: {g:.3f}  |  Entropy: {h:.3f}")
        for a in all_archetypes:
            c = counter.get(a, 0)
            bar = "█" * c
            print(f"  {a:22s}: {c:2d} {bar}")
        uncl = counter.get('unclassifiable', 0)
        if uncl:
            print(f"  {'unclassifiable':22s}: {uncl:2d}")

    print_dist("RAW keyword (current)", raw_counts)
    print_dist("IDF-weighted keyword", idf_counts)
    print_dist("IDF-hybrid (IDF first, raw fallback)", hybrid_counts)

    # Step 5: Flips analysis
    print(f"\n[3] Flips vs raw keyword")
    print(f"    IDF-weighted flips: {len(flips_idf)} / {len(rows)} ({100*len(flips_idf)/len(rows):.1f}%)")
    print(f"    IDF-hybrid flips:   {len(flips_hybrid)} / {len(rows)} ({100*len(flips_hybrid)/len(rows):.1f}%)")

    if flips_idf:
        print(f"\n    Sample IDF flips (dream_id | seed | raw -> idf):")
        for dream_id, seed, raw, idf in flips_idf[:15]:
            print(f"      #{dream_id:2d}  {str(seed):12s}  {raw:20s} -> {idf}")

    # Step 6: Structural bias check — correlation between keyword count and raw score
    print(f"\n[4] Structural bias: keyword count vs archetype frequency")
    for label, counter in [("raw", raw_counts), ("idf", idf_counts)]:
        kw_counts = [len(ARCHETYPES_V2[a]) for a in all_archetypes]
        freqs = [counter.get(a, 0) for a in all_archetypes]
        # Pearson correlation
        n = len(all_archetypes)
        mean_kw = sum(kw_counts) / n
        mean_freq = sum(freqs) / n
        num = sum((kw_counts[i] - mean_kw) * (freqs[i] - mean_freq) for i in range(n))
        den_kw = math.sqrt(sum((k - mean_kw)**2 for k in kw_counts))
        den_freq = math.sqrt(sum((f - mean_freq)**2 for f in freqs))
        r = num / (den_kw * den_freq) if den_kw and den_freq else 0.0
        print(f"    {label:4s}: r(keyword_count, frequency) = {r:+.3f}")

    conn.close()
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
