#!/usr/bin/env python3
"""Generate figures for the Semantic Archaeology paper."""

import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

DB_PATH = "/mnt/nas/mala/work/archaeology/data/archaeology_phase1_clean.db"
OUT_DIR = "/mnt/nas/mala/work/archaeology/paper"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# --- Figure 1: Drift score distribution ---
cur.execute("SELECT drift_score FROM drift_scores")
all_drifts = [row[0] for row in cur.fetchall()]

# Per-word average drifts for annotation
cur.execute("""
    SELECT word, AVG(drift_score) as avg_drift
    FROM drift_scores
    GROUP BY word
    ORDER BY avg_drift DESC
""")
word_drifts = {row[0]: row[1] for row in cur.fetchall()}

fig, ax = plt.subplots(figsize=(8, 5))
n, bins, patches = ax.hist(all_drifts, bins=60, color='#4a7c59', edgecolor='white', alpha=0.85)
ax.axvline(np.mean(all_drifts), color='#c0392b', linestyle='--', linewidth=1.5, label=f'Mean = {np.mean(all_drifts):.2f}')

# Annotate some high-drift words
high_annotations = ['liveth', 'publique', 'tête', 'pharisees']
for w in high_annotations:
    if w in word_drifts:
        d = word_drifts[w]
        ax.annotate(w, xy=(d, ax.get_ylim()[1]*0.85), xytext=(d+0.05, ax.get_ylim()[1]*0.92),
                    fontsize=8, color='#8e44ad',
                    arrowprops=dict(arrowstyle='->', color='#8e44ad', lw=0.8))

ax.set_xlabel('Drift Score (cosine distance)', fontsize=11)
ax.set_ylabel('Count (word–era pairs)', fontsize=11)
ax.set_title('Distribution of Semantic Drift Scores Across 5 Era Transitions', fontsize=12)
ax.legend()
ax.set_xlim(0, 1.4)
fig.tight_layout()
fig.savefig(f"{OUT_DIR}/figure_1_drift_distribution.png", dpi=150)
plt.close(fig)
print("Saved figure_1_drift_distribution.png")

# --- Figure 2: Temperature vs Jump Count ---
cur.execute("""
    SELECT d.seed_word, d.temperature, d.jump_count, dr.primary_archetype_v2
    FROM dreams d
    LEFT JOIN dream_reflections dr ON d.id = dr.dream_id
    WHERE d.seed_word NOT LIKE 'RANDOM_%'
""")
dreams = cur.fetchall()

# Get per-seed average drift for coloring
seed_drifts = {}
for seed in set(d[0] for d in dreams):
    if seed in word_drifts:
        seed_drifts[seed] = word_drifts[seed]
    else:
        seed_drifts[seed] = 0.5  # default

fig, ax = plt.subplots(figsize=(8, 6))

# Plot by whether classifiable
colors_map = {'classifiable': '#2980b9', 'unclassifiable': '#bdc3c7'}
for row in dreams:
    seed, temp, jumps, archetype = row
    cls = 'unclassifiable' if archetype in (None, 'unclassifiable') else 'classifiable'
    ax.scatter(temp, jumps, c=colors_map[cls], alpha=0.7, s=60, edgecolors='white', linewidth=0.5)

# Annotate extreme points
extremes = [
    ('plus', 1.8, 48),
    ('love', 1.2, 3),
    ('touchstone', 1.7, 42),
    ('knowledge', 0.9, 7),
]
for seed, temp, jumps in extremes:
    ax.annotate(seed, xy=(temp, jumps), xytext=(temp+0.08, jumps+2),
                fontsize=8, color='#c0392b',
                arrowprops=dict(arrowstyle='->', color='#c0392b', lw=0.7))

ax.set_xlabel('Temperature', fontsize=11)
ax.set_ylabel('Era Jumps', fontsize=11)
ax.set_title('Temperature vs Temporal Instability (Non-Random Dreams, n=53)', fontsize=12)

from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#2980b9', markersize=8, label='Classifiable'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#bdc3c7', markersize=8, label='Unclassifiable')
]
ax.legend(handles=legend_elements, loc='upper left')
ax.set_xlim(0.4, 2.6)
fig.tight_layout()
fig.savefig(f"{OUT_DIR}/figure_2_temp_vs_jumps.png", dpi=150)
plt.close(fig)
print("Saved figure_2_temp_vs_jumps.png")

# --- Figure 3: Archetype Distribution ---
cur.execute("""
    SELECT dr.primary_archetype_v2, COUNT(*)
    FROM dreams d
    JOIN dream_reflections dr ON d.id = dr.dream_id
    WHERE d.seed_word NOT LIKE 'RANDOM_%'
    GROUP BY dr.primary_archetype_v2
    ORDER BY COUNT(*) DESC
""")
archetype_counts = cur.fetchall()

labels = [row[0] if row[0] else 'unclassifiable' for row in archetype_counts]
counts = [row[1] for row in archetype_counts]

# Color unclassifiable distinctly
colors = ['#e74c3c' if l == 'unclassifiable' else '#3498db' for l in labels]

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh(labels[::-1], counts[::-1], color=colors[::-1], edgecolor='white')
ax.set_xlabel('Number of Dreams', fontsize=11)
ax.set_title('Primary Archetype Distribution (v2 Taxonomy, n=53 Dreams)', fontsize=12)

# Add value labels
for bar in bars:
    width = bar.get_width()
    ax.text(width + 0.3, bar.get_y() + bar.get_height()/2, str(int(width)),
            va='center', fontsize=9)

fig.tight_layout()
fig.savefig(f"{OUT_DIR}/figure_3_archetype_distribution.png", dpi=150)
plt.close(fig)
print("Saved figure_3_archetype_distribution.png")

conn.close()
print("\nAll figures generated.")
