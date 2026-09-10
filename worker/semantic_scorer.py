#!/usr/bin/env python3
"""
Semantic Archetype Scorer

Replaces brittle keyword counting with vector-space similarity.
For each archetype, computes a semantic signature (centroid of keyword vectors),
then scores dreams by average cosine similarity of dream words to that signature.

Also implements a max-neighbor variant: for each dream word, find its closest
keyword in the archetype. More robust for broad archetypes.

Usage:
    cd worker
    python3 semantic_scorer.py [--compare] [--backfill]

Options:
    --compare    Show side-by-side: keyword vs semantic classification
    --backfill   Store semantic scores in dream_reflections table
"""

import sys
import json
import sqlite3
import argparse
from pathlib import Path
from collections import defaultdict

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, ERA_ORDER
from archetype_taxonomy_v2 import ARCHETYPES_V2, extract_words_from_dream, classify_with_v2


def cosine_similarity(vec1, vec2):
    """Cosine similarity between two vectors."""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot / (norm1 * norm2))


def load_era_vectors(conn, era):
    """Load all vectors for an era into memory."""
    cursor = conn.cursor()
    cursor.execute("SELECT word, vector_json FROM word_vectors WHERE era = ?", (era,))
    vectors = {}
    for word, vec_json in cursor.fetchall():
        vec = json.loads(vec_json)
        if np.linalg.norm(vec) > 1e-10:
            vectors[word] = vec
    return vectors


def build_archetype_centroids(conn, era, contrastive=False):
    """
    Build centroid vectors for each archetype from its keyword vectors.
    
    If contrastive=True, subtracts the global corpus centroid so that
    scores measure DISTINCTIVE archetype affinity, not "average English text".
    This prevents generic archetypes (e.g. craft with keywords 'work', 'make')
    from dominating every dream.
    
    Returns dict: archetype_name -> centroid_vector
    """
    vectors = load_era_vectors(conn, era)
    centroids = {}
    missing_counts = {}

    # Global corpus centroid (mean of ALL word vectors in era)
    global_centroid = None
    if contrastive:
        all_vecs = np.array(list(vectors.values()))
        global_centroid = np.mean(all_vecs, axis=0)
        global_norm = np.linalg.norm(global_centroid)
        if global_norm > 1e-10:
            global_centroid = global_centroid / global_norm

    for archetype, keywords in ARCHETYPES_V2.items():
        keyword_vectors = []
        missing = 0
        for kw in keywords:
            if kw in vectors:
                keyword_vectors.append(vectors[kw])
            else:
                missing += 1
        
        if keyword_vectors:
            centroid = np.mean(keyword_vectors, axis=0)
            
            if contrastive and global_centroid is not None:
                # Contrastive: what makes this archetype DIFFERENT from average?
                centroid = centroid - global_centroid
            
            # Normalize
            norm = np.linalg.norm(centroid)
            if norm > 1e-10:
                centroid = centroid / norm
            centroids[archetype] = centroid.tolist()
        else:
            centroids[archetype] = None
        
        missing_counts[archetype] = missing

    return centroids, missing_counts


def build_archetype_keyword_vectors(conn, era):
    """
    Build per-archetype keyword vector lists for max-neighbor scoring.
    Returns dict: archetype_name -> list of (keyword, vector)
    """
    vectors = load_era_vectors(conn, era)
    archetype_kvecs = {}
    
    for archetype, keywords in ARCHETYPES_V2.items():
        kvecs = []
        for kw in keywords:
            if kw in vectors:
                kvecs.append((kw, vectors[kw]))
        archetype_kvecs[archetype] = kvecs
    
    return archetype_kvecs


def score_dream_centroid(dream_words, centroids, era_vectors):
    """
    Score dream using centroid approach.
    For each archetype: average cosine similarity of dream words to centroid.
    """
    scores = {}
    for archetype, centroid in centroids.items():
        if centroid is None or archetype not in era_vectors:
            scores[archetype] = 0.0
            continue
        
        sims = []
        for word in dream_words:
            if word in era_vectors:
                sim = cosine_similarity(era_vectors[word], centroid)
                sims.append(sim)
        
        if sims:
            scores[archetype] = float(np.mean(sims))
        else:
            scores[archetype] = 0.0
    
    return scores


def compute_idf_weights(conn):
    """
    Compute IDF-like weights for words based on dream frequency.
    Words that appear in many dreams get lower weight.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT dream_text FROM dreams")
    
    dream_count = 0
    word_doc_freq = {}
    
    for (dream_text,) in cursor.fetchall():
        dream_count += 1
        words = set(extract_words_from_dream(dream_text))
        for word in words:
            word_doc_freq[word] = word_doc_freq.get(word, 0) + 1
    
    # IDF = log(N / df)
    idf = {}
    for word, df in word_doc_freq.items():
        idf[word] = np.log(dream_count / df)
    
    return idf, dream_count


def score_dream_contrastive(dream_words, centroids, era_vectors, idf_weights=None):
    """
    Contrastive word-level scoring with optional IDF weighting.

    For each dream word, compute its similarity to ALL archetype centroids.
    The word's contribution to an archetype = its sim to that archetype
    MINUS the mean sim to all archetypes. This means words that are
    equally similar to everything contribute ~0. Only DISTINCTIVE words
    contribute positively.

    With IDF: downweight words that appear in many dreams (e.g. 'name', 'memory')
    so that rare distinctive words dominate the score.

    Archetype score = weighted mean of these contrastive contributions.
    """
    # Pre-load all centroids as numpy arrays (skip None)
    valid_archetypes = []
    valid_centroids = []
    for archetype, centroid in centroids.items():
        if centroid is not None:
            valid_archetypes.append(archetype)
            valid_centroids.append(np.array(centroid))
    
    if not valid_archetypes:
        return {a: 0.0 for a in centroids}
    
    centroid_matrix = np.stack(valid_centroids)  # shape: (n_archetypes, dim)
    
    scores = {a: [] for a in valid_archetypes}
    weights = {a: [] for a in valid_archetypes}
    
    for word in dream_words:
        if word not in era_vectors:
            continue
        word_vec = np.array(era_vectors[word])
        word_norm = np.linalg.norm(word_vec)
        if word_norm < 1e-10:
            continue
        word_vec = word_vec / word_norm  # normalize for proper cosine similarity
        
        # IDF weight for this word (default 1.0 if not computed)
        idf = idf_weights.get(word, 1.0) if idf_weights else 1.0
        
        # Cosine sim to all archetype centroids
        sims = np.dot(centroid_matrix, word_vec)  # shape: (n_archetypes,)
        mean_sim = np.mean(sims)
        contrastive = sims - mean_sim  # deviation from average archetype similarity
        
        for i, archetype in enumerate(valid_archetypes):
            scores[archetype].append(float(contrastive[i]) * idf)
            weights[archetype].append(idf)
    
    # Compute weighted mean contrastive score per archetype
    result = {}
    for archetype in centroids:
        if archetype in scores and scores[archetype]:
            result[archetype] = float(np.sum(scores[archetype]) / np.sum(weights[archetype]))
        else:
            result[archetype] = 0.0
    
    return result


def score_dream_max_neighbor(dream_words, archetype_kvecs, era_vectors):
    """
    Score dream using max-neighbor approach.
    For each dream word and each archetype: max similarity to any keyword.
    Archetype score = average of these max similarities.
    """
    scores = {}
    for archetype, kvecs in archetype_kvecs.items():
        if not kvecs:
            scores[archetype] = 0.0
            continue
        
        max_sims = []
        for word in dream_words:
            if word not in era_vectors:
                continue
            word_vec = era_vectors[word]
            best_sim = max(cosine_similarity(word_vec, kv) for _, kv in kvecs)
            max_sims.append(best_sim)
        
        if max_sims:
            scores[archetype] = float(np.mean(max_sims))
        else:
            scores[archetype] = 0.0
    
    return scores


def score_dream_nearest_keyword(dream_words, archetype_kvecs, era_vectors, idf_weights=None):
    """
    Fuzzy keyword scoring via nearest-neighbor assignment.

    For each dream word, find its single closest keyword across ALL archetypes.
    Award 1 point to that keyword's archetype. With IDF weighting, rare words
    contribute more points.

    This is a discrete semantic expansion: instead of exact keyword matching,
    we allow semantically related words to 'vote' for their closest archetype.
    It avoids the continuous-score biases of centroid methods.
    """
    # Flatten all keywords across archetypes
    all_kvecs = []  # list of (archetype, keyword, vector)
    for archetype, kvecs in archetype_kvecs.items():
        for keyword, vec in kvecs:
            all_kvecs.append((archetype, keyword, vec))
    
    if not all_kvecs:
        return {a: 0.0 for a in archetype_kvecs}
    
    scores = {a: 0.0 for a in archetype_kvecs}
    
    for word in dream_words:
        if word not in era_vectors:
            continue
        word_vec = era_vectors[word]
        
        # Find closest keyword across all archetypes
        best_sim = -1.0
        best_archetype = None
        for archetype, keyword, vec in all_kvecs:
            sim = cosine_similarity(word_vec, vec)
            if sim > best_sim:
                best_sim = sim
                best_archetype = archetype
        
        if best_archetype and best_sim > 0.5:  # threshold: must be genuinely similar
            idf = idf_weights.get(word, 1.0) if idf_weights else 1.0
            scores[best_archetype] += idf
    
    return scores


def classify_semantic(scores, method_name="semantic"):
    """
    Classify from semantic scores using z-score normalization.

    In keyword counting, integer gaps are meaningful. In cosine similarity,
    absolute values cluster. Z-scoring per-dream asks: which archetype stands
    out *relative to the others for this dream*?

    Thresholds (empirical, tunable):
        - Primary z-score > 0.5 (meaningfully above the pack)
        - Gap to runner-up > 0.3 z (clear winner, not a near-tie)
    """
    # Filter out zero/None scores (archetypes with no vector representation)
    valid_scores = {k: v for k, v in scores.items() if v > 1e-10}
    
    if not valid_scores:
        return {
            'primary': ('unclassifiable', 0.0),
            'secondary': None,
            'all_scores': scores,
            'top_5': []
        }
    
    values = np.array(list(valid_scores.values()))
    mean = np.mean(values)
    std = np.std(values)
    
    if std < 1e-10:
        # All scores identical — no signal
        sorted_scores = sorted(valid_scores.items(), key=lambda x: x[1], reverse=True)
        return {
            'primary': ('unclassifiable', sorted_scores[0][1]),
            'secondary': None,
            'all_scores': scores,
            'top_5': sorted_scores[:5]
        }
    
    z_scores = {k: (v - mean) / std for k, v in valid_scores.items()}
    sorted_z = sorted(z_scores.items(), key=lambda x: x[1], reverse=True)
    sorted_raw = sorted(valid_scores.items(), key=lambda x: x[1], reverse=True)
    
    primary_z = sorted_z[0]
    secondary_z = sorted_z[1] if len(sorted_z) > 1 else None
    
    # Must be meaningfully above average AND not in a near-tie
    if primary_z[1] < 0.5:
        primary = ('unclassifiable', valid_scores[primary_z[0]])
        secondary = None
    elif secondary_z and (primary_z[1] - secondary_z[1]) < 0.3:
        primary = ('unclassifiable', valid_scores[primary_z[0]])
        secondary = None
    else:
        primary = (primary_z[0], valid_scores[primary_z[0]])
        secondary = (secondary_z[0], valid_scores[secondary_z[0]]) if secondary_z else None
    
    return {
        'primary': primary,
        'secondary': secondary,
        'all_scores': scores,
        'top_5': sorted_raw[:5],
        'z_scores': sorted_z[:5]
    }


def compare_classifications(conn, era="1850-1900"):
    """Compare keyword vs semantic classifications on all stored dreams."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.id, d.seed_word, d.start_era, d.dream_text, 
               dr.primary_archetype_v2, dr.v2_scores
        FROM dreams d
        LEFT JOIN dream_reflections dr ON d.id = dr.dream_id
        ORDER BY d.id
    """)
    
    rows = cursor.fetchall()
    print(f"Loaded {len(rows)} dreams for comparison")
    print(f"Building semantic models for era: {era}")
    
    era_vectors = load_era_vectors(conn, era)
    centroids, missing = build_archetype_centroids(conn, era)
    archetype_kvecs = build_archetype_keyword_vectors(conn, era)
    
    print(f"Era vocabulary: {len(era_vectors)} words")
    print(f"Centroids built. Missing keywords per archetype (max shown): {max(missing.values())}")
    
    keyword_unclass = 0
    centroid_unclass = 0
    contrastive_unclass = 0
    maxneighbor_unclass = 0
    changes = []
        
    for dream_id, seed, start_era, dream_text, kw_primary, kw_scores_json in rows:
        words = extract_words_from_dream(dream_text)
        # Decontaminate
        word_set = set(words)
        if seed:
            word_set.discard(seed.lower())
        dream_words = list(word_set)
            
        # Keyword classification (re-run for consistency)
        kw_result = classify_with_v2(dream_words, seed, start_era)
        if kw_result['primary'][0] == 'unclassifiable':
            keyword_unclass += 1
            
        # Standard centroid semantic classification
        centroid_scores = score_dream_centroid(dream_words, centroids, era_vectors)
        centroid_result = classify_semantic(centroid_scores)
        if centroid_result['primary'][0] == 'unclassifiable':
            centroid_unclass += 1
            
        # Word-level contrastive semantic classification
        contrastive_scores = score_dream_contrastive(dream_words, centroids, era_vectors)
        contrastive_result = classify_semantic(contrastive_scores)
        if contrastive_result['primary'][0] == 'unclassifiable':
            contrastive_unclass += 1
            
        # Max-neighbor semantic classification
        maxneighbor_scores = score_dream_max_neighbor(dream_words, archetype_kvecs, era_vectors)
        maxneighbor_result = classify_semantic(maxneighbor_scores)
        if maxneighbor_result['primary'][0] == 'unclassifiable':
            maxneighbor_unclass += 1
            
        kw_prim = kw_result['primary'][0]
        cent_prim = centroid_result['primary'][0]
        contr_prim = contrastive_result['primary'][0]
        maxn_prim = maxneighbor_result['primary'][0]
            
        if kw_prim != contr_prim:
            changes.append({
                'id': dream_id,
                'seed': seed,
                'keyword': kw_prim,
                'contrastive': contr_prim,
                'contrastive_score': round(contrastive_result['primary'][1], 3),
            })
        
    total = len(rows)
    print(f"\n{'='*60}")
    print("CLASSIFICATION COMPARISON")
    print(f"{'='*60}")
    print(f"Total dreams: {total}")
    print(f"Keyword unclassifiable: {keyword_unclass} ({keyword_unclass/total*100:.1f}%)")
    print(f"Standard centroid unclassifiable: {centroid_unclass} ({centroid_unclass/total*100:.1f}%)")
    print(f"Contrastive (word-level) unclassifiable: {contrastive_unclass} ({contrastive_unclass/total*100:.1f}%)")
    print(f"Max-neighbor unclassifiable: {maxneighbor_unclass} ({maxneighbor_unclass/total*100:.1f}%)")
    print(f"Dreams where contrastive differs from keyword: {len(changes)}")
        
    if changes:
        print(f"\nSample disagreements with keyword (first 15):")
        print(f"{'ID':>4} {'Seed':>12} {'Keyword':>18} {'Contrastive':>18} {'Score':>8}")
        for c in changes[:15]:
            print(f"{c['id']:>4} {c['seed'] or 'random':>12} {c['keyword']:>18} {c['contrastive']:>18} {c['contrastive_score']:>8.3f}")
        
    return {
        'total': total,
        'keyword_unclass': keyword_unclass,
        'centroid_unclass': centroid_unclass,
        'contrastive_unclass': contrastive_unclass,
        'maxneighbor_unclass': maxneighbor_unclass,
        'changes': changes
    }


def classify_hybrid(dream_words, seed, start_era, centroids, era_vectors, archetype_kvecs, idf_weights=None):
    """
    Hybrid classifier: keyword counting primary, semantic tie-breaker.

    1. Run keyword scoring (v2).
    2. If keyword result is classifiable, return it.
    3. If keyword result is unclassifiable (tie or zero), use nearest-keyword
       semantic scoring (with IDF weighting) to break the tie.
    """
    # Decontaminate for keyword scoring
    word_set = set(dream_words)
    if seed:
        word_set.discard(seed.lower())
    dream_words_clean = list(word_set)
    
    # Step 1: keyword scoring
    kw_result = classify_with_v2(dream_words_clean, seed, start_era)
    
    if kw_result['primary'][0] != 'unclassifiable':
        return {
            'primary': kw_result['primary'],
            'secondary': kw_result['secondary'],
            'method': 'keyword',
            'keyword_result': kw_result,
            'semantic_result': None
        }
    
    # Step 2: nearest-keyword semantic tie-breaker
    semantic_scores = score_dream_nearest_keyword(dream_words_clean, archetype_kvecs, era_vectors, idf_weights)
    # Use same tie-breaking logic as keyword counting for integer scores
    sorted_scores = sorted(semantic_scores.items(), key=lambda x: x[1], reverse=True)
    max_score = sorted_scores[0][1] if sorted_scores else 0
    top_count = sum(1 for _, s in sorted_scores if s == max_score)
    
    if max_score == 0 or top_count >= 2:
        primary = ('unclassifiable', max_score)
        secondary = None
    else:
        primary = sorted_scores[0]
        secondary = sorted_scores[1] if len(sorted_scores) > 1 and sorted_scores[1][1] > 0 else None
    
    return {
        'primary': primary,
        'secondary': secondary,
        'method': 'semantic',
        'keyword_result': kw_result,
        'semantic_result': {
            'primary': primary,
            'secondary': secondary,
            'all_scores': semantic_scores,
            'top_5': sorted_scores[:5]
        }
    }


def compare_hybrid(conn, era="1850-1900"):
    """Compare keyword-only vs hybrid classification."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.id, d.seed_word, d.start_era, d.dream_text, 
               dr.primary_archetype_v2, dr.v2_scores
        FROM dreams d
        LEFT JOIN dream_reflections dr ON d.id = dr.dream_id
        ORDER BY d.id
    """)
    
    rows = cursor.fetchall()
    print(f"Loaded {len(rows)} dreams for hybrid comparison")
    print(f"Building semantic models for era: {era}")
    
    era_vectors = load_era_vectors(conn, era)
    centroids, missing = build_archetype_centroids(conn, era)
    archetype_kvecs = build_archetype_keyword_vectors(conn, era)
    idf_weights, dream_count = compute_idf_weights(conn)
    
    print(f"Era vocabulary: {len(era_vectors)} words")
    print(f"IDF computed from {dream_count} dreams")
    
    keyword_unclass = 0
    hybrid_unclass = 0
    rescued = []  # dreams that keyword couldn't classify but hybrid could
    flipped = []  # dreams where keyword classified but hybrid disagreed
    
    for dream_id, seed, start_era, dream_text, kw_primary, kw_scores_json in rows:
        words = extract_words_from_dream(dream_text)
        
        # Keyword classification
        word_set = set(words)
        if seed:
            word_set.discard(seed.lower())
        dream_words = list(word_set)
        
        kw_result = classify_with_v2(dream_words, seed, start_era)
        if kw_result['primary'][0] == 'unclassifiable':
            keyword_unclass += 1
        
        # Hybrid classification
        hybrid_result = classify_hybrid(words, seed, start_era, centroids, era_vectors, archetype_kvecs, idf_weights)
        if hybrid_result['primary'][0] == 'unclassifiable':
            hybrid_unclass += 1
        
        kw_prim = kw_result['primary'][0]
        hyb_prim = hybrid_result['primary'][0]
        hyb_method = hybrid_result['method']
        
        if kw_prim == 'unclassifiable' and hyb_prim != 'unclassifiable':
            rescued.append({
                'id': dream_id,
                'seed': seed,
                'hybrid': hyb_prim,
                'method': hyb_method,
                'hyb_score': round(hybrid_result['primary'][1], 3),
            })
        elif kw_prim != 'unclassifiable' and kw_prim != hyb_prim:
            flipped.append({
                'id': dream_id,
                'seed': seed,
                'keyword': kw_prim,
                'hybrid': hyb_prim,
                'method': hyb_method,
            })
    
    total = len(rows)
    print(f"\n{'='*60}")
    print("HYBRID CLASSIFICATION COMPARISON")
    print(f"{'='*60}")
    print(f"Total dreams: {total}")
    print(f"Keyword unclassifiable: {keyword_unclass} ({keyword_unclass/total*100:.1f}%)")
    print(f"Hybrid unclassifiable: {hybrid_unclass} ({hybrid_unclass/total*100:.1f}%)")
    print(f"Rescued by semantic tie-breaker: {len(rescued)}")
    print(f"Flipped by semantic override: {len(flipped)}")
    
    if rescued:
        print(f"\nRescued dreams (first 20):")
        print(f"{'ID':>4} {'Seed':>12} {'Hybrid':>18} {'Method':>10} {'Score':>8}")
        for r in rescued[:20]:
            print(f"{r['id']:>4} {r['seed'] or 'random':>12} {r['hybrid']:>18} {r['method']:>10} {r['hyb_score']:>8.3f}")
    
    if flipped:
        print(f"\nFlipped dreams (first 10):")
        print(f"{'ID':>4} {'Seed':>12} {'Keyword':>18} {'Hybrid':>18}")
        for f in flipped[:10]:
            print(f"{f['id']:>4} {f['seed'] or 'random':>12} {f['keyword']:>18} {f['hybrid']:>18}")
    
    return {
        'total': total,
        'keyword_unclass': keyword_unclass,
        'hybrid_unclass': hybrid_unclass,
        'rescued': rescued,
        'flipped': flipped
    }


def backfill_semantic_scores(conn, era="1850-1900", contrastive=True):
    """Add semantic_score columns to dream_reflections and backfill."""
    cursor = conn.cursor()
    
    # Check if columns exist
    cursor.execute("PRAGMA table_info(dream_reflections)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'semantic_primary' not in columns:
        cursor.execute("ALTER TABLE dream_reflections ADD COLUMN semantic_primary TEXT")
    if 'semantic_scores' not in columns:
        cursor.execute("ALTER TABLE dream_reflections ADD COLUMN semantic_scores TEXT")
    
    conn.commit()
    
    era_vectors = load_era_vectors(conn, era)
    centroids, _ = build_archetype_centroids(conn, era)
    
    cursor.execute("""
        SELECT d.id, d.seed_word, d.dream_text
        FROM dreams d
        JOIN dream_reflections dr ON d.id = dr.dream_id
    """)
    
    updated = 0
    for dream_id, seed, dream_text in cursor.fetchall():
        words = extract_words_from_dream(dream_text)
        word_set = set(words)
        if seed:
            word_set.discard(seed.lower())
        
        scores = score_dream_centroid(list(word_set), centroids, era_vectors)
        result = classify_semantic(scores)
        
        cursor.execute("""
            UPDATE dream_reflections 
            SET semantic_primary = ?, semantic_scores = ?
            WHERE dream_id = ?
        """, (result['primary'][0], json.dumps(scores), dream_id))
        updated += 1
    
    conn.commit()
    print(f"Backfilled {updated} reflections with semantic scores")


def main():
    parser = argparse.ArgumentParser(description="Semantic archetype scorer")
    parser.add_argument("--compare", action="store_true", help="Compare all semantic methods")
    parser.add_argument("--hybrid", action="store_true", help="Compare keyword vs hybrid (default)")
    parser.add_argument("--backfill", action="store_true", help="Store semantic scores in DB")
    parser.add_argument("--era", default="1850-1900", help="Era to use for vectors")
    args = parser.parse_args()
    
    conn = sqlite3.connect(DB_PATH)
    
    if args.backfill:
        backfill_semantic_scores(conn, args.era)
    elif args.compare:
        compare_classifications(conn, args.era)
    else:
        # Default: hybrid comparison
        compare_hybrid(conn, args.era)
    
    conn.close()


if __name__ == "__main__":
    main()
