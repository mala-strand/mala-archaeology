#!/usr/bin/env python3
"""
dream_territory_map.py — 2D archetype territory visualization

Loads dream positions (from dream_topology.py output) and plots them as a
semantic territory map: each dream is a point colored by primary archetype.
Adds convex hulls for archetype territories and marks bridge/liminal dreams.

Zero-token. Stdlib + sqlite3 + matplotlib + numpy + scipy.
"""

import json
import sqlite3
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from scipy.spatial import ConvexHull

# ── paths ──────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "archaeology_phase1_clean.db"
POS_PATH = ROOT / "notes" / "dream_topology_positions.json"
OUT_PATH = ROOT / "notes" / "dream_territory_map.png"

# ── archetype color palette (19 archetypes) ────────────────────────
ARCHETYPE_COLORS = {
    "abstract": "#8B5CF6",          # violet
    "bodily": "#F472B6",            # pink
    "commerce": "#F59E0B",          # amber
    "conflict": "#EF4444",          # red
    "domestic": "#10B981",          # emerald
    "journey": "#3B82F6",           # blue
    "knowledge": "#6366F1",         # indigo
    "legacy": "#D946EF",            # fuchsia
    "natural": "#22C55E",           # green
    "power_divine": "#EAB308",      # yellow
    "power_political": "#F97316",   # orange
    "power_personal": "#FB923C",    # light orange
    "religious_cosmic": "#A855F7",  # purple
    "religious_devotion": "#C084FC",# light purple
    "religious_moral": "#9333EA",   # dark purple
    "social": "#06B6D4",            # cyan
    "temporal": "#64748B",          # slate
    "unclassifiable": "#94A3B8",    # gray
    "wilderness": "#78716C",        # stone
}

# ── load positions ─────────────────────────────────────────────────
with open(POS_PATH) as f:
    positions = json.load(f)

dream_ids = sorted(int(k) for k in positions.keys())
coords = np.array([positions[str(did)] for did in dream_ids])

# ── load dream metadata ────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get primary archetype, confidence, liminality for each dream
meta = {}
cursor.execute("""
    SELECT d.id, r.idf_hybrid_primary, r.confidence_tier, r.confidence_margin,
           d.seed_word, d.temperature, d.jump_count
    FROM dreams d
    LEFT JOIN dream_reflections r ON d.id = r.dream_id
    WHERE r.idf_hybrid_primary IS NOT NULL
""")
for row in cursor.fetchall():
    dream_id, primary, conf_tier, conf_margin, seed, temp, jumps = row
    meta[dream_id] = {
        "primary": primary,
        "confidence_tier": conf_tier,
        "confidence_margin": conf_margin or 0.0,
        "seed": seed,
        "temperature": temp,
        "jumps": jumps,
    }

# Get liminality scores from bridge analysis (compute on the fly)
# Build adjacency from positions: 5-NN
from scipy.spatial import cKDTree

tree = cKDTree(coords)
_, nn_indices = tree.query(coords, k=6)  # 6 including self
nn_indices = nn_indices[:, 1:]  # remove self

# Compute liminality: count of cross-archetype neighbors
liminality = {}
for i, did in enumerate(dream_ids):
    if did not in meta:
        continue
    primary = meta[did]["primary"]
    cross_count = 0
    for ni in nn_indices[i]:
        nid = dream_ids[ni]
        if nid in meta and meta[nid]["primary"] != primary:
            cross_count += 1
    liminality[did] = cross_count

conn.close()

# ── plot ───────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 12))

# Plot each archetype group with convex hull
plotted_archetypes = set()
for archetype in ARCHETYPE_COLORS:
    mask = [did for did in dream_ids if did in meta and meta[did]["primary"] == archetype]
    if len(mask) < 3:
        continue
    idxs = [dream_ids.index(did) for did in mask]
    points = coords[idxs]
    color = ARCHETYPE_COLORS[archetype]

    # Scatter
    ax.scatter(points[:, 0], points[:, 1], c=color, s=80, alpha=0.7,
               edgecolors="white", linewidth=0.5, zorder=3, label=archetype)
    plotted_archetypes.add(archetype)

    # Convex hull (territory boundary)
    if len(points) >= 3:
        try:
            hull = ConvexHull(points)
            hull_points = points[hull.vertices]
            poly = Polygon(hull_points, closed=True, fill=True,
                           facecolor=color, alpha=0.08, edgecolor=color,
                           linewidth=1.5, linestyle="--", zorder=1)
            ax.add_patch(poly)
        except Exception:
            pass

# Mark top 10 most liminal dreams
liminal_sorted = sorted(liminality.items(), key=lambda x: x[1], reverse=True)[:10]
for did, lim in liminal_sorted:
    if did not in meta:
        continue
    idx = dream_ids.index(did)
    x, y = coords[idx]
    ax.annotate(f"#{did}", (x, y), xytext=(5, 5), textcoords="offset points",
                fontsize=7, fontweight="bold", color="black",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                          edgecolor="black", alpha=0.8),
                zorder=5)

ax.set_xlabel("Semantic Dimension 1", fontsize=12)
ax.set_ylabel("Semantic Dimension 2", fontsize=12)
ax.set_title("Dream Territory Map\nConvex hulls = archetype territories | Labels = top 10 most liminal dreams",
             fontsize=14, fontweight="bold", pad=15)

# Legend
handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), loc="upper left",
          bbox_to_anchor=(1.02, 1), fontsize=9, title="Archetypes",
          title_fontsize=10, frameon=True, fancybox=True)

ax.set_xlim(-0.05, 1.05)
ax.set_ylim(-0.05, 1.05)
ax.set_aspect("equal")
ax.grid(True, alpha=0.2)
fig.tight_layout()

fig.savefig(OUT_PATH, dpi=150, bbox_inches="tight", facecolor="white")
print(f"Saved territory map to {OUT_PATH}")

# ── summary ────────────────────────────────────────────────────────
print(f"\nPlotted {len([d for d in dream_ids if d in meta])} classified dreams")
print(f"Archetypes with territories: {len(plotted_archetypes)}")
print(f"\nTop 5 most liminal dreams:")
for did, lim in liminal_sorted[:5]:
    m = meta.get(did, {})
    print(f"  #{did}: {m.get('primary', '?')} | liminality={lim}/5 | "
          f"confidence={m.get('confidence_tier', '?')} | seed={m.get('seed', '?')}")
