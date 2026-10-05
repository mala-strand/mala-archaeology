#!/usr/bin/env python3
"""
Null-model tests for dream-space archetype assortativity.

Two null models:
1. Label permutation — preserve graph structure, shuffle node labels.
   Tests: are archetype labels placed on nodes more clustered than random?
2. Configuration model — preserve degree sequence + label distribution, rewire edges.
   Tests: does the observed wiring create more clustering than random wiring?

Zero-token pure Python. Reads dream_adjacency.jsonl, writes report to stdout.
"""

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

# Reproducibility
random.seed(42)

DB_DIR = Path(__file__).parent.parent / "data"
ADJACENCY_PATH = DB_DIR / "dream_adjacency.jsonl"

N_PERMUTATIONS = 100


def load_adjacency(path):
    """Load adjacency list; return nodes dict and undirected edge set."""
    nodes = {}
    directed_edges = set()
    with open(path) as f:
        for line in f:
            rec = json.loads(line)
            dream_id = rec["dream_id"]
            primary = None
            neighbors = []
            for n in rec["neighbors"]:
                nid = n["neighbor_id"]
                neighbors.append(nid)
                directed_edges.add((dream_id, nid))
                # Derive primary from first neighbor's same_primary flag
                # (consistent because all neighbors of a node share the node's label)
                if primary is None:
                    # If same_primary is True, neighbor shares this node's primary archetype.
                    # We don't store the node's own primary in adjacency, but we can
                    # infer it from the DB later. For now, stub with node id.
                    pass
            nodes[dream_id] = {"neighbors": neighbors}
    # Build undirected edge set (smaller id first)
    undirected = set()
    for a, b in directed_edges:
        if a < b:
            undirected.add((a, b))
        elif b < a:
            undirected.add((b, a))
    return nodes, undirected


def load_archetypes(path):
    """Load primary archetype per dream from adjacency same_primary inference."""
    # The adjacency file doesn't store the node's own archetype directly.
    # We infer it from DB or from a sidecar. Let's read from the DB directly.
    import sqlite3
    db_path = path.parent / "archaeology_phase1_clean.db"
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        "SELECT dream_id, idf_hybrid_primary, confidence_tier FROM dream_reflections"
    )
    archetypes = {}
    confidence = {}
    for row in cur.fetchall():
        did, arch, conf = row
        archetypes[did] = arch
        confidence[did] = conf
    conn.close()
    return archetypes, confidence


def assortativity(edges, labels):
    """Fraction of edges whose endpoints share the same primary label."""
    if not edges:
        return 0.0
    same = sum(1 for a, b in edges if labels.get(a) == labels.get(b))
    return same / len(edges)


def label_permutation_null(edges, labels, n=1000):
    """Preserve graph structure, shuffle labels among nodes."""
    nodes = list(labels.keys())
    label_list = [labels[n] for n in nodes]
    actual = assortativity(edges, labels)
    null_values = []
    for _ in range(n):
        shuffled = label_list.copy()
        random.shuffle(shuffled)
        shuffled_labels = {n: shuffled[i] for i, n in enumerate(nodes)}
        null_values.append(assortativity(edges, shuffled_labels))
    null_values.sort()
    # p-value: proportion of null >= actual (one-tailed, since assortativity is positive)
    p = sum(1 for v in null_values if v >= actual) / n
    mean_null = sum(null_values) / n
    std_null = (sum((v - mean_null) ** 2 for v in null_values) / n) ** 0.5
    z = (actual - mean_null) / std_null if std_null > 0 else float("inf")
    return {
        "actual": actual,
        "null_mean": mean_null,
        "null_std": std_null,
        "null_min": null_values[0],
        "null_max": null_values[-1],
        "p_value": p,
        "z_score": z,
        "n": n,
    }


def configuration_model_null(edges, labels, n=100, swaps_per_run=3000):
    """Preserve degree sequence + label distribution, rewire edges via double-edge swaps.

    Uses Markov-chain edge swapping: repeatedly pick two edges (a-b, c-d),
    swap to (a-d, c-b), accept if no self-loop or duplicate is created.
    This preserves degree exactly and converges to uniform randomization.
    """
    actual = assortativity(edges, labels)
    null_values = []
    edge_list = list(edges)

    for _ in range(n):
        # Start from actual edge set and randomize via swaps
        current = set(edges)
        swaps = 0
        attempts = 0
        max_attempts = swaps_per_run * 10
        while swaps < swaps_per_run and attempts < max_attempts:
            attempts += 1
            e1, e2 = random.sample(edge_list, 2)
            # Edges may have been removed by prior swaps; skip if absent
            if e1 not in current or e2 not in current:
                continue
            a, b = e1
            c, d = e2
            # avoid sharing a node (would create self-loop or no-op)
            if len({a, b, c, d}) < 4:
                continue
            # propose swap: a-b + c-d -> a-d + c-b
            # also try a-c + b-d with 50% probability to avoid bipartite bias
            if random.random() < 0.5:
                new1 = (a, d) if a < d else (d, a)
                new2 = (c, b) if c < b else (b, c)
            else:
                new1 = (a, c) if a < c else (c, a)
                new2 = (b, d) if b < d else (d, b)
            # check validity
            if new1[0] == new1[1] or new2[0] == new2[1]:
                continue
            if new1 in current or new2 in current:
                continue
            # apply swap
            current.remove(e1)
            current.remove(e2)
            current.add(new1)
            current.add(new2)
            swaps += 1
        null_values.append(assortativity(current, labels))

    null_values.sort()
    p = sum(1 for v in null_values if v >= actual) / n
    mean_null = sum(null_values) / n
    std_null = (sum((v - mean_null) ** 2 for v in null_values) / n) ** 0.5
    z = (actual - mean_null) / std_null if std_null > 0 else float("inf")
    return {
        "actual": actual,
        "null_mean": mean_null,
        "null_std": std_null,
        "null_min": null_values[0],
        "null_max": null_values[-1],
        "p_value": p,
        "z_score": z,
        "n": n,
    }


def subset_edges(edges, labels, confidence, tiers):
    """Return edges where BOTH endpoints have confidence in tiers."""
    allowed = {n for n, t in confidence.items() if t in tiers}
    return [e for e in edges if e[0] in allowed and e[1] in allowed]


def main():
    if not ADJACENCY_PATH.exists():
        print(f"Adjacency file not found: {ADJACENCY_PATH}", file=sys.stderr)
        sys.exit(1)

    nodes, edges = load_adjacency(ADJACENCY_PATH)
    labels, confidence = load_archetypes(ADJACENCY_PATH)

    # Exclude unclassifiable dreams from primary analysis
    classified_labels = {k: v for k, v in labels.items() if v != "unclassifiable"}
    classified_nodes = set(classified_labels.keys())
    classified_edges = [e for e in edges if e[0] in classified_nodes and e[1] in classified_nodes]

    # Also HIGH+MEDIUM subset
    hm_edges = subset_edges(edges, labels, confidence, {"HIGH", "MEDIUM"})
    hm_labels = {k: v for k, v in labels.items() if confidence.get(k) in ("HIGH", "MEDIUM")}

    print("=" * 60)
    print("DREAM SPACE TOPOLOGY — NULL MODEL TESTS")
    print("=" * 60)
    print(f"Total dreams: {len(nodes)}")
    print(f"Total edges (undirected 5-NN): {len(edges)}")
    print(f"Classified dreams (excl. unclassifiable): {len(classified_nodes)}")
    print(f"Classified edges: {len(classified_edges)}")
    print(f"HIGH+MEDIUM confidence edges: {len(hm_edges)}")
    print()

    # --- Label permutation ---
    print("-" * 60)
    print("NULL MODEL 1: LABEL PERMUTATION")
    print("  (Preserve graph structure, shuffle archetype labels)")
    print("-" * 60)

    for name, e_set, lbls in [
        ("All dreams", edges, labels),
        ("Classified only", classified_edges, classified_labels),
        ("HIGH+MEDIUM confidence", hm_edges, hm_labels),
    ]:
        if len(e_set) == 0:
            print(f"\n{name}: no edges, skipping")
            continue
        # Only include labels for nodes that appear in edges
        nodes_in_edges = set()
        for a, b in e_set:
            nodes_in_edges.add(a)
            nodes_in_edges.add(b)
        filtered_labels = {k: v for k, v in lbls.items() if k in nodes_in_edges}
        res = label_permutation_null(e_set, filtered_labels, N_PERMUTATIONS)
        print(f"\n{name}:")
        print(f"  Actual assortativity:     {res['actual']:.4f}")
        print(f"  Null mean ± std:          {res['null_mean']:.4f} ± {res['null_std']:.4f}")
        print(f"  Null range:               [{res['null_min']:.4f}, {res['null_max']:.4f}]")
        print(f"  Z-score:                  {res['z_score']:.2f}")
        print(f"  P-value (one-tailed):     {res['p_value']:.4f}")
        if res["p_value"] < 0.001:
            print(f"  Result:                   *** HIGHLY SIGNIFICANT ***")
        elif res["p_value"] < 0.01:
            print(f"  Result:                   ** SIGNIFICANT **")
        elif res["p_value"] < 0.05:
            print(f"  Result:                   * MARGINALLY SIGNIFICANT *")
        else:
            print(f"  Result:                   NOT SIGNIFICANT")

    # --- Configuration model ---
    print()
    print("-" * 60)
    print("NULL MODEL 2: CONFIGURATION MODEL (STUB MATCHING)")
    print("  (Preserve degree sequence + labels, randomize edges)")
    print("-" * 60)

    for name, e_set, lbls in [
        ("All dreams", edges, labels),
        ("Classified only", classified_edges, classified_labels),
    ]:
        if len(e_set) == 0:
            print(f"\n{name}: no edges, skipping")
            continue
        nodes_in_edges = set()
        for a, b in e_set:
            nodes_in_edges.add(a)
            nodes_in_edges.add(b)
        filtered_labels = {k: v for k, v in lbls.items() if k in nodes_in_edges}
        res = configuration_model_null(e_set, filtered_labels, N_PERMUTATIONS)
        if res is None:
            print(f"\n{name}: failed to generate valid random graphs")
            continue
        print(f"\n{name}:")
        print(f"  Actual assortativity:     {res['actual']:.4f}")
        print(f"  Null mean ± std:          {res['null_mean']:.4f} ± {res['null_std']:.4f}")
        print(f"  Null range:               [{res['null_min']:.4f}, {res['null_max']:.4f}]")
        print(f"  Z-score:                  {res['z_score']:.2f}")
        print(f"  P-value (one-tailed):     {res['p_value']:.4f}")
        if res["p_value"] < 0.001:
            print(f"  Result:                   *** HIGHLY SIGNIFICANT ***")
        elif res["p_value"] < 0.01:
            print(f"  Result:                   ** SIGNIFICANT **")
        elif res["p_value"] < 0.05:
            print(f"  Result:                   * MARGINALLY SIGNIFICANT *")
        else:
            print(f"  Result:                   NOT SIGNIFICANT")

    print()
    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print("""
If Label Permutation is significant:
  → The observed graph structure places same-archetype dreams closer
    together than random label assignment would predict.
    The ARCHETYPE LABELS are non-randomly arranged on the graph.

If Configuration Model is significant:
  → The specific wiring of edges creates more same-label connections
    than a random graph with the same degree sequence would.
    The EDGES themselves are structured by archetype.

If both are significant:
  → Archetype structure is a genuine property of dream space topology.
    Neither label distribution nor degree sequence can explain it.
""")


if __name__ == "__main__":
    main()
