#!/usr/bin/env python3
"""
dream_topology.py — Analyze the topology of dream space.

Reads data/dream_adjacency.jsonl (5 nearest neighbors per dream)
and computes graph-theoretic + archetype-stratified topology metrics.

Zero-token. Uses only stdlib + sqlite3 + math. Optional matplotlib for viz.
"""

import json
import math
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

# Optional plotting
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False

ADJACENCY_PATH = Path(__file__).parent.parent / "data" / "dream_adjacency.jsonl"
DB_PATH = Path(__file__).parent.parent / "data" / "archaeology_phase1_clean.db"
OUTPUT_DIR = Path(__file__).parent.parent / "notes"


def load_adjacency(path: Path):
    """Load adjacency list as dict[dream_id] -> list of neighbor dicts."""
    adj = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            adj[rec["dream_id"]] = rec["neighbors"]
    return adj


def load_dream_metadata(db_path: Path):
    """Load dream_id -> {seed, primary_archetype, confidence_tier}."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT d.id, d.seed_word, d.temperature, d.jump_count,
               dr.idf_hybrid_primary, dr.confidence_tier
        FROM dreams d
        LEFT JOIN dream_reflections dr ON d.id = dr.dream_id
    """)
    meta = {}
    for row in cur.fetchall():
        meta[row["id"]] = {
            "seed": row["seed_word"],
            "temperature": row["temperature"],
            "jump_count": row["jump_count"],
            "primary": row["idf_hybrid_primary"] or "unclassifiable",
            "confidence": row["confidence_tier"] or "UNKNOWN",
        }
    conn.close()
    return meta


def build_graph(adj, directed=False, threshold=None):
    """Build edge list and node sets. If threshold, only keep edges <= threshold."""
    edges = []
    nodes = set(adj.keys())
    for src, nbrs in adj.items():
        for n in nbrs:
            dst = n["neighbor_id"]
            dist = n["composite"]
            if threshold is not None and dist > threshold:
                continue
            edges.append((src, dst, dist))
            nodes.add(dst)
            if not directed:
                edges.append((dst, src, dist))
    # dedupe undirected
    if not directed:
        seen = set()
        uniq = []
        for s, d, dist in edges:
            key = tuple(sorted((s, d)))
            if key not in seen:
                seen.add(key)
                uniq.append((s, d, dist))
        edges = uniq
    return nodes, edges


def degree_distribution(edges, nodes):
    deg = {n: 0 for n in nodes}
    for s, d, _ in edges:
        deg[s] += 1
        deg[d] += 1
    return deg


def clustering_coefficient(edges, nodes):
    """Local clustering coefficient for each node (undirected)."""
    neighbors = defaultdict(set)
    for s, d, _ in edges:
        neighbors[s].add(d)
        neighbors[d].add(s)

    coeff = {}
    for n in nodes:
        nbrs = list(neighbors[n])
        k = len(nbrs)
        if k < 2:
            coeff[n] = 0.0
            continue
        actual = 0
        for i in range(k):
            for j in range(i + 1, k):
                if nbrs[j] in neighbors[nbrs[i]]:
                    actual += 1
        possible = k * (k - 1) / 2
        coeff[n] = actual / possible if possible else 0.0
    return coeff, neighbors


def connected_components(nodes, edges):
    """Return list of components (sets of nodes)."""
    neighbors = defaultdict(set)
    for s, d, _ in edges:
        neighbors[s].add(d)
        neighbors[d].add(s)
    visited = set()
    comps = []
    for n in nodes:
        if n in visited:
            continue
        stack = [n]
        comp = set()
        while stack:
            cur = stack.pop()
            if cur in visited:
                continue
            visited.add(cur)
            comp.add(cur)
            for nb in neighbors[cur]:
                if nb not in visited:
                    stack.append(nb)
        comps.append(comp)
    return comps


def articulation_points(nodes, edges):
    """Find articulation points using DFS low-link."""
    neighbors = defaultdict(set)
    for s, d, _ in edges:
        neighbors[s].add(d)
        neighbors[d].add(s)

    visited = set()
    art = set()
    parent = {}
    disc = {}
    low = {}
    time = [0]

    def dfs(u):
        visited.add(u)
        disc[u] = low[u] = time[0]
        time[0] += 1
        children = 0
        for v in neighbors[u]:
            if v not in visited:
                children += 1
                parent[v] = u
                dfs(v)
                low[u] = min(low[u], low[v])
                if parent.get(u) is None and children > 1:
                    art.add(u)
                if parent.get(u) is not None and low[v] >= disc[u]:
                    art.add(u)
            elif v != parent.get(u):
                low[u] = min(low[u], disc[v])

    for n in nodes:
        if n not in visited:
            dfs(n)
    return art


def average_neighbor_distance(node, adj):
    """Mean composite distance to neighbors."""
    nbrs = adj.get(node, [])
    if not nbrs:
        return None
    return sum(n["composite"] for n in nbrs) / len(nbrs)


def archetype_assortativity(edges, meta):
    """Count edges that connect same-primary vs different-primary."""
    same = 0
    diff = 0
    for s, d, _ in edges:
        ps = meta.get(s, {}).get("primary", "UNKNOWN")
        pd = meta.get(d, {}).get("primary", "UNKNOWN")
        if ps == pd:
            same += 1
        else:
            diff += 1
    total = same + diff
    return same / total if total else 0, diff / total if total else 0


def spectral_layout_2d(edges, nodes, dim=2, iterations=50):
    """Simple force-directed layout using spring-like repulsion/attraction."""
    # Initialize randomly in unit square
    import random
    rng = random.Random(42)
    pos = {n: [rng.random(), rng.random()] for n in nodes}

    # Precompute edge set for quick lookup
    edge_set = set()
    edge_dist = {}
    for s, d, dist in edges:
        edge_set.add(tuple(sorted((s, d))))
        edge_dist[tuple(sorted((s, d)))] = dist

    node_list = list(nodes)
    k = 1.0 / math.sqrt(len(nodes))

    for _ in range(iterations):
        # compute forces
        disp = {n: [0.0, 0.0] for n in nodes}
        for i, u in enumerate(node_list):
            for v in node_list[i + 1 :]:
                dx = pos[u][0] - pos[v][0]
                dy = pos[u][1] - pos[v][1]
                dist = math.sqrt(dx * dx + dy * dy) + 1e-6
                # repulsive
                fr = k * k / dist
                fx = (dx / dist) * fr
                fy = (dy / dist) * fr
                disp[u][0] += fx
                disp[u][1] += fy
                disp[v][0] -= fx
                disp[v][1] -= fy

        for s, d, comp in edges:
            dx = pos[s][0] - pos[d][0]
            dy = pos[s][1] - pos[d][1]
            dist = math.sqrt(dx * dx + dy * dy) + 1e-6
            # attractive: stronger when composite distance is small
            fa = (dist * dist) / k * (1.0 - comp)
            fx = (dx / dist) * fa
            fy = (dy / dist) * fa
            disp[s][0] -= fx
            disp[s][1] -= fy
            disp[d][0] += fx
            disp[d][1] += fy

        # apply with cooling
        temp = 0.1 * (1 - _ / iterations)
        for n in nodes:
            dx, dy = disp[n]
            disp_len = math.sqrt(dx * dx + dy * dy) + 1e-6
            pos[n][0] += (dx / disp_len) * min(disp_len, temp)
            pos[n][1] += (dy / disp_len) * min(disp_len, temp)
            # keep in bounds
            pos[n][0] = max(0, min(1, pos[n][0]))
            pos[n][1] = max(0, min(1, pos[n][1]))

    return pos


def plot_topology(pos, edges, meta, output_path):
    if not HAS_MPL:
        return

    # Color by primary archetype
    archetypes = sorted({m.get("primary", "UNKNOWN") for m in meta.values()})
    cmap = plt.colormaps.get_cmap("tab20").resampled(len(archetypes))
    color_map = {a: cmap(i) for i, a in enumerate(archetypes)}

    fig, ax = plt.subplots(figsize=(14, 10))

    # Draw edges with alpha based on distance
    for s, d, dist in edges:
        alpha = max(0.05, 1.0 - dist)
        ax.plot(
            [pos[s][0], pos[d][0]],
            [pos[s][1], pos[d][1]],
            "k-",
            alpha=alpha,
            linewidth=0.5,
        )

    # Draw nodes
    for n, (x, y) in pos.items():
        archetype = meta.get(n, {}).get("primary", "UNKNOWN")
        conf = meta.get(n, {}).get("confidence", "UNKNOWN")
        size = 60 if conf == "HIGH" else (40 if conf == "MEDIUM" else 25)
        ax.scatter(x, y, c=[color_map.get(archetype, "#888888")], s=size, edgecolors="k", linewidths=0.3, zorder=3)

    # Legend
    handles = [plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=color_map[a], markersize=8, label=a) for a in archetypes]
    ax.legend(handles=handles, loc="upper left", fontsize=7, title="Archetype")

    ax.set_title("Dream Space Topology — Force-Directed Layout (5-NN Graph)")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_xticks([])
    ax.set_yticks([])
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Plot saved to {output_path}")


def main():
    adj = load_adjacency(ADJACENCY_PATH)
    meta = load_dream_metadata(DB_PATH)

    nodes, edges = build_graph(adj, directed=False)
    deg = degree_distribution(edges, nodes)
    coeff, neighbors = clustering_coefficient(edges, nodes)
    comps = connected_components(nodes, edges)
    art = articulation_points(nodes, edges)
    same_frac, diff_frac = archetype_assortativity(edges, meta)

    # Sparse / dense region analysis
    avg_nbr_dist = {n: average_neighbor_distance(n, adj) for n in nodes}

    # Report
    lines = []
    lines.append("=" * 60)
    lines.append("DREAM SPACE TOPOLOGY REPORT")
    lines.append("=" * 60)
    lines.append(f"Nodes: {len(nodes)}")
    lines.append(f"Edges (undirected, 5-NN): {len(edges)}")
    lines.append(f"Connected components: {len(comps)}")
    for i, comp in enumerate(sorted(comps, key=len, reverse=True)[:5]):
        lines.append(f"  Component {i+1}: {len(comp)} nodes")
    lines.append(f"Articulation points: {len(art)} ({sorted(art)})")
    lines.append("")

    # Degree stats
    deg_vals = list(deg.values())
    lines.append(f"Degree — min: {min(deg_vals)}, max: {max(deg_vals)}, mean: {sum(deg_vals)/len(deg_vals):.2f}")
    lines.append("")

    # Clustering
    coeff_vals = [coeff[n] for n in nodes]
    lines.append(f"Clustering coefficient — mean: {sum(coeff_vals)/len(coeff_vals):.3f}, max: {max(coeff_vals):.3f}")
    lines.append("")

    # Assortativity
    lines.append(f"Archetype assortativity: {same_frac:.1%} same-primary edges, {diff_frac:.1%} different-primary")
    lines.append("")

    # Top hub nodes (highest degree)
    top_deg = sorted(deg.items(), key=lambda x: x[1], reverse=True)[:10]
    lines.append("Top 10 hub dreams (degree):")
    for nid, d in top_deg:
        m = meta.get(nid, {})
        lines.append(f"  #{nid} ({m.get('seed','?')}, {m.get('primary','?')}) — degree {d}")
    lines.append("")

    # Most isolated (lowest degree, highest avg neighbor distance)
    isolation = []
    for n in nodes:
        if avg_nbr_dist[n] is not None:
            # composite distance is [0,1], higher = farther
            isolation.append((n, deg[n], avg_nbr_dist[n]))
    isolation.sort(key=lambda x: (x[1], -x[2]))
    lines.append("Most isolated dreams (low degree, far neighbors):")
    for nid, d, ad in isolation[:10]:
        m = meta.get(nid, {})
        lines.append(f"  #{nid} ({m.get('seed','?')}, {m.get('primary','?')}) — degree {d}, avg neighbor dist {ad:.3f}")
    lines.append("")

    # Densest subregions (highest local clustering + high degree)
    dense = [(n, deg[n], coeff[n]) for n in nodes]
    dense.sort(key=lambda x: (x[2], x[1]), reverse=True)
    lines.append("Densest subregions (high clustering + degree):")
    for nid, d, c in dense[:10]:
        m = meta.get(nid, {})
        lines.append(f"  #{nid} ({m.get('seed','?')}, {m.get('primary','?')}) — degree {d}, clustering {c:.3f}")
    lines.append("")

    # Bridges: edges whose endpoints have no other shared neighbors
    bridge_candidates = []
    for s, d, dist in edges:
        shared = len(neighbors[s] & neighbors[d]) - (1 if d in neighbors[s] else 0)
        if shared <= 1:
            bridge_candidates.append((s, d, dist, shared))
    bridge_candidates.sort(key=lambda x: x[2])
    lines.append(f"Bridge-like edges (≤1 shared neighbor): {len(bridge_candidates)}")
    for s, d, dist, shared in bridge_candidates[:10]:
        ms = meta.get(s, {})
        md = meta.get(d, {})
        lines.append(f"  #{s}({ms.get('seed','?')},{ms.get('primary','?')}) <-> #{d}({md.get('seed','?')},{md.get('primary','?')}) — dist {dist:.3f}, shared {shared}")
    lines.append("")

    # Component archetype composition
    lines.append("Component archetype composition (largest 3 components):")
    for i, comp in enumerate(sorted(comps, key=len, reverse=True)[:3]):
        arch_counts = defaultdict(int)
        for n in comp:
            arch_counts[meta.get(n, {}).get("primary", "UNKNOWN")] += 1
        lines.append(f"  Component {i+1} ({len(comp)} nodes):")
        for a, c in sorted(arch_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            lines.append(f"    {a}: {c}")
    lines.append("")

    report = "\n".join(lines)
    print(report)

    # Save report
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / "dream_topology_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport saved to {report_path}")

    # Plot
    if HAS_MPL:
        pos = spectral_layout_2d(edges, nodes, iterations=80)
        plot_path = OUTPUT_DIR / "dream_topology_map.png"
        plot_topology(pos, edges, meta, plot_path)

        # Save positions for future use
        pos_path = OUTPUT_DIR / "dream_topology_positions.json"
        with open(pos_path, "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in pos.items()}, f)
        print(f"Positions saved to {pos_path}")


if __name__ == "__main__":
    main()
