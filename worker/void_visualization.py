#!/usr/bin/env python3
"""
void_visualization.py — Plot void candidates alongside archetype territories.

Uses a simple 2D PCA projection of word vectors to show where void candidates
sit relative to seeded words (colored by archetype).

Zero-token. Stdlib + sqlite3 + numpy + matplotlib.
"""

import json
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "archaeology_phase1_clean.db"
VOID_PATH = ROOT / "notes" / "void_candidates_v2.json"
OUT_PATH = ROOT / "notes" / "void_territory_overlay.png"

ARCHETYPE_COLORS = {
    "abstract": "#8B5CF6",
    "bodily": "#F472B6",
    "commerce": "#F59E0B",
    "conflict": "#EF4444",
    "domestic": "#10B981",
    "journey": "#3B82F6",
    "knowledge": "#6366F1",
    "legacy": "#D946EF",
    "natural": "#22C55E",
    "power_divine": "#EAB308",
    "power_political": "#F97316",
    "power_personal": "#FB923C",
    "religious_cosmic": "#A855F7",
    "religious_devotion": "#C084FC",
    "religious_moral": "#9333EA",
    "social": "#06B6D4",
    "temporal": "#64748B",
    "unclassifiable": "#94A3B8",
    "wilderness": "#78716C",
}


def load_vectors():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT word, era, vector_json FROM word_vectors")
    vecs_by_word = {}
    for word, era, vjson in cursor:
        v = np.array(json.loads(vjson), dtype=np.float32)
        vecs_by_word.setdefault(word, []).append(v)
    conn.close()
    result = {}
    for w, vs in vecs_by_word.items():
        avg = np.mean(vs, axis=0)
        norm = np.linalg.norm(avg)
        if norm > 0:
            result[w] = avg
    return result


def load_seed_archetypes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.seed_word, r.penalized_primary
        FROM dreams d
        JOIN dream_reflections r ON d.id = r.dream_id
        WHERE r.penalized_primary IS NOT NULL
          AND r.penalized_primary != 'unclassifiable'
        GROUP BY d.seed_word, r.penalized_primary
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def simple_pca(data, n_components=2):
    """Simple PCA using numpy SVD. data is (n_samples, n_features)."""
    centered = data - np.mean(data, axis=0)
    u, s, vt = np.linalg.svd(centered, full_matrices=False)
    components = vt[:n_components]
    transformed = np.dot(centered, components.T)
    explained = (s[:n_components] ** 2) / np.sum(s ** 2)
    return transformed, explained


def main():
    print("Loading vectors...")
    vectors = load_vectors()
    print(f"  {len(vectors)} words")

    print("Loading seed archetypes...")
    seed_archetypes = load_seed_archetypes()
    print(f"  {len(seed_archetypes)} seeds")

    print("Loading void candidates...")
    if not VOID_PATH.exists():
        print(f"  ERROR: {VOID_PATH} not found. Run void_explorer_v2.py first.")
        return
    with open(VOID_PATH) as f:
        void_candidates = json.load(f)
    print(f"  {len(void_candidates)} void candidates")

    # Build matrix: seeded words + void candidates
    seeded_words = [s for s, _ in seed_archetypes if s in vectors]
    void_words = [v["word"] for v in void_candidates if v["word"] in vectors]

    seeded_archetypes = [a for s, a in seed_archetypes if s in vectors]

    all_words = seeded_words + void_words
    all_vecs = np.array([vectors[w] for w in all_words])

    print(f"\nProjecting {len(all_words)} words to 2D (PCA)...")
    projected, explained = simple_pca(all_vecs)
    print(f"  Explained variance: {explained[0]:.1%} + {explained[1]:.1%} = {sum(explained):.1%}")

    seeded_proj = projected[:len(seeded_words)]
    void_proj = projected[len(seeded_words):]

    # Plot
    fig, ax = plt.subplots(figsize=(14, 12))

    # Plot seeded words by archetype
    plotted = set()
    for arch in ARCHETYPE_COLORS:
        mask = [i for i, a in enumerate(seeded_archetypes) if a == arch]
        if not mask:
            continue
        pts = seeded_proj[mask]
        color = ARCHETYPE_COLORS[arch]
        ax.scatter(pts[:, 0], pts[:, 1], c=color, s=60, alpha=0.5,
                   edgecolors="white", linewidth=0.5, zorder=2, label=arch)
        plotted.add(arch)

    # Plot void candidates
    ax.scatter(void_proj[:, 0], void_proj[:, 1], c="black", s=120,
               marker="x", linewidths=2, alpha=0.9, zorder=4, label="void candidates")

    # Label top 20 void candidates
    for i, v in enumerate(void_candidates[:20]):
        if v["word"] not in vectors:
            continue
        idx = void_words.index(v["word"])
        x, y = void_proj[idx]
        ax.annotate(v["word"], (x, y), xytext=(4, 4), textcoords="offset points",
                    fontsize=7, color="black", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                              edgecolor="black", alpha=0.7),
                    zorder=5)

    ax.set_xlabel(f"PC1 ({explained[0]:.1%} variance)", fontsize=12)
    ax.set_ylabel(f"PC2 ({explained[1]:.1%} variance)", fontsize=12)
    ax.set_title("Void Candidates in Semantic Space\nSeeded words = colored by archetype | X = void candidates",
                 fontsize=14, fontweight="bold", pad=15)

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc="upper left",
              bbox_to_anchor=(1.02, 1), fontsize=9, title="Legend",
              title_fontsize=10, frameon=True, fancybox=True)

    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"\nSaved visualization to {OUT_PATH}")

    # Summary stats
    print(f"\nSummary:")
    print(f"  Seeded words plotted: {len(seeded_words)}")
    print(f"  Void candidates plotted: {len(void_words)}")
    print(f"  Archetypes with seeds: {len(plotted)}")


if __name__ == "__main__":
    main()
