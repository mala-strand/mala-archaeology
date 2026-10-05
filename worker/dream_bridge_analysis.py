#!/usr/bin/env python3
"""
dream_bridge_analysis.py — Analyze "bridge" dreams: those on edges between
different archetype territories.

Reads data/dream_adjacency.jsonl and the clean DB.
Zero-token. Uses only stdlib + sqlite3 + math.
"""

import json
import math
import sqlite3
import sys
from collections import Counter, defaultdict
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
    """Load dream_id -> rich metadata including drift."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Base dream + reflection data
    cur.execute("""
        SELECT d.id, d.seed_word, d.temperature, d.jump_count,
               dr.idf_hybrid_primary, dr.idf_hybrid_secondary,
               dr.confidence_tier, dr.confidence_margin, dr.confidence_relative
        FROM dreams d
        LEFT JOIN dream_reflections dr ON d.id = dr.dream_id
    """)
    meta = {}
    for row in cur.fetchall():
        meta[row["id"]] = {
            "seed": row["seed_word"],
            "temperature": row["temperature"] or 0.0,
            "jump_count": row["jump_count"] or 0,
            "primary": row["idf_hybrid_primary"] or "unclassifiable",
            "secondary": row["idf_hybrid_secondary"] or "none",
            "confidence": row["confidence_tier"] or "UNKNOWN",
            "confidence_margin": row["confidence_margin"] or 0.0,
            "confidence_relative": row["confidence_relative"] or 0.0,
            "drift": 0.0,
        }

    # Seed drift: mean drift_score for the seed word across all era pairs
    cur.execute("""
        SELECT word, AVG(drift_score) as mean_drift
        FROM drift_scores
        GROUP BY word
    """)
    drift_by_word = {}
    for row in cur.fetchall():
        drift_by_word[row["word"]] = row["mean_drift"]

    for dream_id, m in meta.items():
        seed = m["seed"]
        if seed and seed in drift_by_word:
            m["drift"] = drift_by_word[seed]
        elif seed and seed.startswith("RANDOM_"):
            # Random seeds have no drift entry; use a sentinel
            m["drift"] = -1.0

    conn.close()
    return meta


def build_undirected_edges(adj):
    """Build set of undirected edges (min_id, max_id) with distance."""
    edges = {}
    for src, nbrs in adj.items():
        for n in nbrs:
            dst = n["neighbor_id"]
            key = (min(src, dst), max(src, dst))
            if key not in edges:
                edges[key] = n["composite"]
    return edges


def analyze(meta, edges):
    # Attach archetypes to edges
    cross_edges = []   # different primary archetype
    same_edges = []    # same primary archetype
    for (a, b), dist in edges.items():
        if a not in meta or b not in meta:
            continue
        pa = meta[a]["primary"]
        pb = meta[b]["primary"]
        if pa == "unclassifiable" or pb == "unclassifiable":
            continue
        if pa == pb:
            same_edges.append((a, b, dist, pa))
        else:
            cross_edges.append((a, b, dist, pa, pb))

    total_classified_edges = len(cross_edges) + len(same_edges)

    # Liminality score: how many cross-archetype edges is each dream part of?
    liminality = defaultdict(int)
    bridge_partners = defaultdict(list)  # dream_id -> list of (partner_id, partner_primary, dist)
    for a, b, dist, pa, pb in cross_edges:
        liminality[a] += 1
        liminality[b] += 1
        bridge_partners[a].append((b, pb, dist))
        bridge_partners[b].append((a, pa, dist))

    # Also count total edges per dream (degree in undirected classified graph)
    degree = defaultdict(int)
    for a, b, *_ in cross_edges:
        degree[a] += 1
        degree[b] += 1
    for a, b, *_ in same_edges:
        degree[a] += 1
        degree[b] += 1

    return {
        "cross_edges": cross_edges,
        "same_edges": same_edges,
        "total_classified_edges": total_classified_edges,
        "liminality": liminality,
        "bridge_partners": bridge_partners,
        "degree": degree,
    }


def report(meta, results):
    cross = results["cross_edges"]
    same = results["same_edges"]
    lim = results["liminality"]
    deg = results["degree"]
    bp = results["bridge_partners"]
    total = results["total_classified_edges"]

    lines = []
    lines.append("=" * 70)
    lines.append("DREAM BRIDGE ANALYSIS")
    lines.append("=" * 70)
    lines.append("")

    # Edge summary
    lines.append("--- Edge Summary ---")
    lines.append(f"Total classified edges (excluding unclassifiable): {total}")
    lines.append(f"Same-archetype edges: {len(same)} ({100*len(same)/total:.1f}%)")
    lines.append(f"Cross-archetype edges: {len(cross)} ({100*len(cross)/total:.1f}%)")
    lines.append("")

    # Archetype pair frequencies
    pair_counts = Counter()
    for a, b, dist, pa, pb in cross:
        pair = tuple(sorted([pa, pb]))
        pair_counts[pair] += 1

    lines.append("--- Top Cross-Archetype Bridges ---")
    for pair, count in pair_counts.most_common(15):
        lines.append(f"  {' + '.join(pair)}: {count}")
    lines.append("")

    # Liminality distribution
    lim_values = list(lim.values())
    if lim_values:
        lines.append("--- Liminality Score Distribution ---")
        lines.append(f"Dreams with cross-archetype edges: {len(lim)}")
        lines.append(f"Max liminality: {max(lim_values)}")
        lines.append(f"Mean liminality: {sum(lim_values)/len(lim_values):.2f}")
        lines.append(f"Median liminality: {sorted(lim_values)[len(lim_values)//2]:.1f}")
        lines.append("")

    # Most liminal dreams
    most_liminal = sorted(lim.items(), key=lambda x: (-x[1], x[0]))[:15]
    lines.append("--- Most Liminal Dreams (most cross-archetype bridges) ---")
    for dream_id, score in most_liminal:
        m = meta[dream_id]
        prim = m["primary"]
        conf = m["confidence"]
        degv = deg.get(dream_id, 0)
        lines.append(f"  #{dream_id} ({m['seed']}, {prim}, {conf}): {score}/{degv} cross-archetype edges")
        # List bridge targets
        targets = bp[dream_id][:5]
        tstrs = [f"#{tid}({tp})" for tid, tp, _ in targets]
        lines.append(f"      bridges to: {', '.join(tstrs)}")
    lines.append("")

    # Compare bridge dreams vs non-bridge dreams
    bridge_dreams = set(lim.keys())
    all_dreams = set(meta.keys())
    non_bridge = []
    for did in all_dreams:
        if did not in bridge_dreams and meta[did]["primary"] != "unclassifiable":
            non_bridge.append(did)

    def avg(vals):
        return sum(vals) / len(vals) if vals else 0.0

    def conf_dist(dream_ids):
        tiers = Counter(meta[d]["confidence"] for d in dream_ids)
        return dict(tiers)

    lines.append("--- Bridge Dreams vs Non-Bridge Dreams ---")
    lines.append(f"Bridge dreams (≥1 cross edge): {len(bridge_dreams)}")
    lines.append(f"Non-bridge dreams (0 cross edges): {len(non_bridge)}")
    lines.append("")

    # Confidence comparison
    b_conf = conf_dist(bridge_dreams)
    n_conf = conf_dist(non_bridge)
    lines.append("Confidence distribution:")
    for tier in ["HIGH", "MEDIUM", "LOW", "TENTATIVE", "UNKNOWN"]:
        bc = b_conf.get(tier, 0)
        nc = n_conf.get(tier, 0)
        bpct = 100 * bc / len(bridge_dreams) if bridge_dreams else 0
        npct = 100 * nc / len(non_bridge) if non_bridge else 0
        lines.append(f"  {tier:10s}: bridge {bc:3d} ({bpct:5.1f}%) | non-bridge {nc:3d} ({npct:5.1f}%)")
    lines.append("")

    # Structural comparison
    b_temp = [meta[d]["temperature"] for d in bridge_dreams]
    n_temp = [meta[d]["temperature"] for d in non_bridge]
    b_jump = [meta[d]["jump_count"] for d in bridge_dreams]
    n_jump = [meta[d]["jump_count"] for d in non_bridge]
    b_drift = [meta[d]["drift"] for d in bridge_dreams if meta[d]["drift"] >= 0]
    n_drift = [meta[d]["drift"] for d in non_bridge if meta[d]["drift"] >= 0]
    b_margin = [meta[d]["confidence_margin"] for d in bridge_dreams]
    n_margin = [meta[d]["confidence_margin"] for d in non_bridge]

    lines.append("Structural means:")
    lines.append(f"  Temperature:    bridge {avg(b_temp):.2f} | non-bridge {avg(n_temp):.2f}")
    lines.append(f"  Jump count:     bridge {avg(b_jump):.1f} | non-bridge {avg(n_jump):.1f}")
    lines.append(f"  Seed drift:     bridge {avg(b_drift):.3f} | non-bridge {avg(n_drift):.3f}")
    lines.append(f"  Conf margin:    bridge {avg(b_margin):.3f} | non-bridge {avg(n_margin):.3f}")
    lines.append("")

    # Secondary archetype match analysis
    # For bridge dreams, does their secondary archetype match any of their bridge targets?
    secondary_matches = 0
    secondary_total = 0
    for dream_id in bridge_dreams:
        sec = meta[dream_id]["secondary"]
        if sec and sec != "none" and sec != "unclassifiable":
            secondary_total += 1
            targets = set(tp for _, tp, _ in bp[dream_id])
            if sec in targets:
                secondary_matches += 1

    lines.append("--- Secondary Archetype as Bridge Predictor ---")
    lines.append(f"Bridge dreams with a secondary archetype: {secondary_total}")
    lines.append(f"Secondary matches a bridge target: {secondary_matches} ({100*secondary_matches/secondary_total:.1f}%)")
    lines.append("")

    # Bridge-edge distance comparison
    cross_dists = [d for _, _, d, _, _ in cross]
    same_dists = [d for _, _, d, _ in same]
    lines.append("--- Edge Distance Comparison ---")
    lines.append(f"Mean cross-archetype edge distance:  {avg(cross_dists):.3f}")
    lines.append(f"Mean same-archetype edge distance:   {avg(same_dists):.3f}")
    lines.append(f"Cross edges are {'longer' if avg(cross_dists) > avg(same_dists) else 'shorter'} on average")
    lines.append("")

    # High-liminality deep dive (top 5)
    lines.append("--- Deep Dive: Top 5 Most Liminal Dreams ---")
    for dream_id, score in most_liminal[:5]:
        m = meta[dream_id]
        lines.append(f"")
        lines.append(f"Dream #{dream_id}")
        lines.append(f"  Seed: {m['seed']}  Temp: {m['temperature']:.1f}  Jumps: {m['jump_count']}")
        lines.append(f"  Primary: {m['primary']}  Secondary: {m['secondary']}  Confidence: {m['confidence']} (margin {m['confidence_margin']:.2f})")
        lines.append(f"  Seed drift: {m['drift']:.3f}")
        lines.append(f"  Cross-archetype bridges: {score}")
        for tid, tp, dist in bp[dream_id]:
            tm = meta[tid]
            lines.append(f"    -> #{tid} ({tm['seed']}, {tp}, {tm['confidence']}) dist={dist:.3f}")
    lines.append("")

    lines.append("=" * 70)
    lines.append("END OF REPORT")
    lines.append("=" * 70)

    return "\n".join(lines)


def plot_results(meta, results):
    if not HAS_MPL:
        return None

    cross = results["cross_edges"]
    lim = results["liminality"]
    pair_counts = Counter()
    for a, b, dist, pa, pb in cross:
        pair = tuple(sorted([pa, pb]))
        pair_counts[pair] += 1

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram of liminality scores
    ax = axes[0]
    lim_values = list(lim.values())
    ax.hist(lim_values, bins=range(0, max(lim_values)+2), align="left", rwidth=0.8, color="steelblue", edgecolor="black")
    ax.set_xlabel("Liminality score (cross-archetype edges)")
    ax.set_ylabel("Number of dreams")
    ax.set_title("Distribution of Liminality Scores")
    ax.axvline(sum(lim_values)/len(lim_values), color="red", linestyle="--", label=f"Mean = {sum(lim_values)/len(lim_values):.1f}")
    ax.legend()

    # Top 10 bridge pairs
    ax = axes[1]
    top_pairs = pair_counts.most_common(10)
    labels = [" + ".join(p) for p, _ in top_pairs]
    counts = [c for _, c in top_pairs]
    y_pos = range(len(labels))
    ax.barh(y_pos, counts, color="coral", edgecolor="black")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Number of bridge edges")
    ax.set_title("Top 10 Cross-Archetype Bridge Pairs")

    plt.tight_layout()
    out_path = OUTPUT_DIR / "dream_bridge_analysis.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def main():
    if not ADJACENCY_PATH.exists():
        print(f"Adjacency file not found: {ADJACENCY_PATH}", file=sys.stderr)
        sys.exit(1)
    if not DB_PATH.exists():
        print(f"DB not found: {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    adj = load_adjacency(ADJACENCY_PATH)
    meta = load_dream_metadata(DB_PATH)
    edges = build_undirected_edges(adj)
    results = analyze(meta, edges)
    text = report(meta, results)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "dream_bridge_report.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

    plot_path = plot_results(meta, results)

    print(text)
    print(f"\nReport written to {out_path}")
    if plot_path:
        print(f"Plot written to {plot_path}")


if __name__ == "__main__":
    main()
