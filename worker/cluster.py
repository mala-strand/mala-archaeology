#!/usr/bin/env python3
"""
Semantic clustering for archaeology project.

Clusters words by semantic similarity within each era, tracks cluster
stability across eras, and identifies emerging/dissolving clusters.

Usage:
    python3 worker/cluster.py [--era ERA] [--k K] [--min-size N]

Defaults:
    --k 50          (target number of clusters)
    --min-size 5    (minimum cluster size to report)
"""
import sys
import sqlite3
import json
import argparse
from pathlib import Path
from collections import defaultdict
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, ERA_ORDER

try:
    from sklearn.cluster import KMeans, AgglomerativeClustering
    from sklearn.metrics import silhouette_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: sklearn not available, using numpy-only clustering")


def load_vectors(conn: sqlite3.Connection, era: str):
    """Load all word vectors for an era. Returns {word: vector_array}."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT word, vector_json FROM word_vectors WHERE era = ?",
        (era,)
    )
    vectors = {}
    for word, vec_json in cursor.fetchall():
        vectors[word] = np.array(json.loads(vec_json), dtype=np.float32)
    return vectors


def cosine_similarity(v1, v2):
    """Compute cosine similarity between two vectors."""
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 == 0 or n2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (n1 * n2))


def simple_greedy_clustering(vectors: dict, k: int, min_size: int):
    """
    Simple greedy clustering using cosine similarity.
    Fallback when sklearn is not available.
    """
    words = list(vectors.keys())
    if len(words) < k:
        k = max(1, len(words) // min_size)
    
    # Start with random seeds
    np.random.seed(42)
    seeds = np.random.choice(words, size=min(k, len(words)), replace=False)
    
    clusters = {seed: [seed] for seed in seeds}
    
    # Assign remaining words to nearest cluster
    for word in words:
        if word in clusters:
            continue
        best_seed = None
        best_sim = -1
        for seed in clusters:
            sim = cosine_similarity(vectors[word], vectors[seed])
            if sim > best_sim:
                best_sim = sim
                best_seed = seed
        if best_seed:
            clusters[best_seed].append(word)
    
    # Filter by min_size
    return {seed: members for seed, members in clusters.items() if len(members) >= min_size}


def sklearn_clustering(vectors: dict, k: int, min_size: int):
    """Use sklearn AgglomerativeClustering for better results."""
    words = list(vectors.keys())
    if len(words) < k:
        k = max(1, len(words) // min_size)
    
    X = np.array([vectors[w] for w in words])
    
    # Filter out zero vectors for clustering
    norms = np.linalg.norm(X, axis=1)
    non_zero_mask = norms > 0
    
    if non_zero_mask.sum() < k:
        # Fall back to simple clustering if too few non-zero vectors
        return simple_greedy_clustering(vectors, k, min_size)
    
    X_nonzero = X[non_zero_mask]
    words_nonzero = [w for w, m in zip(words, non_zero_mask) if m]
    
    # Use KMeans instead of AgglomerativeClustering (handles cosine better)
    from sklearn.cluster import KMeans
    clustering = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = clustering.fit_predict(X_nonzero)
    
    # Group by cluster label
    clusters = defaultdict(list)
    for word, label in zip(words_nonzero, labels):
        clusters[label].append(word)
    
    # Find centroid word for each cluster
    result = {}
    for label, members in clusters.items():
        if len(members) < min_size:
            continue
        # Find member closest to centroid
        member_vectors = [vectors[w] for w in members]
        centroid = np.mean(member_vectors, axis=0)
        # Handle zero centroid
        if np.linalg.norm(centroid) == 0:
            best_word = members[0]
        else:
            best_word = min(members, key=lambda w: -cosine_similarity(vectors[w], centroid))
        result[best_word] = members
    
    return result


def cluster_era(conn: sqlite3.Connection, era: str, k: int, min_size: int):
    """Cluster words for a single era. Returns clusters dict."""
    print(f"\nClustering era: {era}")
    vectors = load_vectors(conn, era)
    print(f"  Loaded {len(vectors)} vectors")
    
    if len(vectors) < k * min_size:
        k = max(1, len(vectors) // min_size)
        print(f"  Adjusted k to {k} (insufficient vectors)")
    
    if SKLEARN_AVAILABLE:
        clusters = sklearn_clustering(vectors, k, min_size)
    else:
        clusters = simple_greedy_clustering(vectors, k, min_size)
    
    print(f"  Formed {len(clusters)} clusters (min_size={min_size})")
    
    # Store in database
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clusters WHERE era = ?", (era,))
    
    batch = []
    for seed, members in clusters.items():
        batch.append((era, seed, json.dumps(members), len(members)))
    
    cursor.executemany(
        "INSERT INTO clusters (era, cluster_seed, members_json, member_count) VALUES (?, ?, ?, ?)",
        batch
    )
    conn.commit()
    
    # Print top clusters by size
    sorted_clusters = sorted(clusters.items(), key=lambda x: -len(x[1]))
    print(f"  Top clusters:")
    for seed, members in sorted_clusters[:5]:
        sample = ", ".join(members[:8])
        if len(members) > 8:
            sample += f" ... ({len(members)-8} more)"
        print(f"    {seed}: {sample}")
    
    return clusters


def compute_cluster_stability(conn: sqlite3.Connection, eras: list):
    """
    Compute cluster stability across eras.
    A cluster is 'stable' if its seed word appears in adjacent eras.
    """
    print("\n=== Cluster Stability Analysis ===")
    cursor = conn.cursor()
    
    # Load all clusters
    era_clusters = {}
    for era in eras:
        cursor.execute("SELECT cluster_seed, members_json FROM clusters WHERE era = ?", (era,))
        era_clusters[era] = {seed: json.loads(members) for seed, members in cursor.fetchall()}
    
    # Track seed presence across eras
    all_seeds = set()
    for clusters in era_clusters.values():
        all_seeds.update(clusters.keys())
    
    print(f"Total unique cluster seeds across all eras: {len(all_seeds)}")
    
    # Find seeds that persist across adjacent eras
    stable_seeds = []
    emerging = []
    dissolving = []
    
    for i, era in enumerate(eras):
        current_seeds = set(era_clusters[era].keys())
        
        if i > 0:
            prev_seeds = set(era_clusters[eras[i-1]].keys())
            new_seeds = current_seeds - prev_seeds
            if new_seeds:
                emerging.append((era, new_seeds))
        
        if i < len(eras) - 1:
            next_seeds = set(era_clusters[eras[i+1]].keys())
            ending_seeds = current_seeds - next_seeds
            if ending_seeds:
                dissolving.append((era, ending_seeds))
            # Seeds in both current and next are stable
            stable = current_seeds & next_seeds
            stable_seeds.extend([(s, era, eras[i+1]) for s in stable])
    
    print(f"\nStable clusters (persist to next era): {len(stable_seeds)}")
    print(f"Emerging clusters: {sum(len(s) for _, s in emerging)}")
    print(f"Dissolving clusters: {sum(len(s) for _, s in dissolving)}")
    
    # Show examples
    if emerging:
        era, seeds = emerging[0]
        print(f"\n  Example emerging in {era}: {', '.join(list(seeds)[:5])}")
    if dissolving:
        era, seeds = dissolving[-1]
        print(f"  Example dissolving in {era}: {', '.join(list(seeds)[:5])}")
    
    # Store stability analysis
    cursor.execute("DELETE FROM cluster_stability")
    
    batch = []
    for seed, era_from, era_to in stable_seeds:
        batch.append((seed, era_from, era_to, "stable"))
    for era, seeds in emerging:
        for seed in seeds:
            batch.append((seed, era, None, "emerging"))
    for era, seeds in dissolving:
        for seed in seeds:
            batch.append((seed, era, None, "dissolving"))
    
    if batch:
        cursor.executemany(
            "INSERT INTO cluster_stability (cluster_seed, era_from, era_to, stability_type) VALUES (?, ?, ?, ?)",
            batch
        )
        conn.commit()


def ensure_tables(conn: sqlite3.Connection):
    """Create cluster tables if they don't exist."""
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clusters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            era TEXT NOT NULL,
            cluster_seed TEXT NOT NULL,
            members_json TEXT NOT NULL,
            member_count INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(era, cluster_seed)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cluster_stability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cluster_seed TEXT NOT NULL,
            era_from TEXT NOT NULL,
            era_to TEXT,
            stability_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()


def main():
    parser = argparse.ArgumentParser(description="Semantic clustering for archaeology")
    parser.add_argument("--era", help="Cluster specific era only")
    parser.add_argument("--k", type=int, default=50, help="Target number of clusters")
    parser.add_argument("--min-size", type=int, default=5, help="Minimum cluster size")
    args = parser.parse_args()
    
    print(f"Clustering using DB: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    ensure_tables(conn)
    
    if args.era:
        cluster_era(conn, args.era, args.k, args.min_size)
    else:
        # Cluster all eras
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT era FROM word_vectors ORDER BY era")
        db_eras = [row[0] for row in cursor.fetchall()]
        eras = [e for e in ERA_ORDER if e in db_eras]
        
        print(f"Clustering {len(eras)} eras: {eras}")
        
        for era in eras:
            cluster_era(conn, era, args.k, args.min_size)
        
        # Compute stability across eras
        compute_cluster_stability(conn, eras)
    
    conn.close()
    print("\n=== Clustering complete ===")


if __name__ == "__main__":
    main()
