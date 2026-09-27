#!/usr/bin/env python3
"""
Visualize parameter landscape: 2D heatmap of temp × jump_prob colored by archetype distribution,
faceted by drift stratum. Makes the escape energy model visually graspable.

Run from archaeology/ root:
    .venv/bin/python worker/visualize_parameter_landscape.py
"""

import sqlite3
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import os

DB_PATH = 'data/archaeology_phase1_clean.db'
OUTPUT_DIR = 'notes'


def load_data():
    conn = sqlite3.connect(DB_PATH)

    # Dreams + parameters
    dreams = pd.read_sql_query("""
        SELECT id, seed_word, temperature, era_jump_prob, jump_count
        FROM dreams
    """, conn)

    # Reflections with IDF-hybrid classification
    reflections = pd.read_sql_query("""
        SELECT dream_id, idf_hybrid_primary as primary_archetype,
               confidence_tier, confidence_margin
        FROM dream_reflections
        WHERE idf_hybrid_primary IS NOT NULL
    """, conn)

    # Drift scores per word
    drift = pd.read_sql_query("""
        SELECT word, AVG(drift_score) as mean_drift
        FROM drift_scores
        GROUP BY word
    """, conn)

    conn.close()
    return dreams, reflections, drift


def merge_data(dreams, reflections, drift):
    df = dreams.merge(reflections, left_on='id', right_on='dream_id', how='inner')
    df = df.merge(drift, left_on='seed_word', right_on='word', how='left')

    # Exclude RANDOM_* seeds (no drift data)
    df = df[~df['seed_word'].str.startswith('RANDOM_')]

    # Exclude unclassifiable
    df = df[df['primary_archetype'] != 'unclassifiable']

    # Stratify by drift terciles
    drift_values = df['mean_drift'].dropna()
    q33, q66 = drift_values.quantile([0.33, 0.66])

    def drift_stratum(d):
        if pd.isna(d):
            return 'unknown'
        if d <= q33:
            return 'low (stable)'
        if d <= q66:
            return 'medium'
        return 'high (unstable)'

    df['drift_stratum'] = df['mean_drift'].apply(drift_stratum)
    df = df[df['drift_stratum'] != 'unknown']

    return df, q33, q66


def create_scatter_plots(df):
    """Create faceted scatter plots: temperature vs jump_prob, colored by archetype."""

    # Get archetype color mapping
    archetypes = sorted(df['primary_archetype'].unique())
    n_archetypes = len(archetypes)

    # Use tab20 + tab20b for up to 38 colors
    cmap = matplotlib.colormaps.get_cmap('tab20')
    if n_archetypes > 20:
        cmap2 = matplotlib.colormaps.get_cmap('tab20b')
        colors = [cmap(i / 20) for i in range(20)] + [cmap2(i / (n_archetypes - 20)) for i in range(n_archetypes - 20)]
    else:
        colors = [cmap(i / n_archetypes) for i in range(n_archetypes)]

    archetype_color = {a: colors[i] for i, a in enumerate(archetypes)}

    strata = ['low (stable)', 'medium', 'high (unstable)']
    stratum_order = {s: i for i, s in enumerate(strata)}

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Parameter Landscape: Temperature × Jump Probability by Drift Stratum\n'
                 '(Escape Energy Model)', fontsize=14, fontweight='bold')

    for stratum in strata:
        ax = axes[stratum_order[stratum]]
        sub = df[df['drift_stratum'] == stratum]

        for archetype in archetypes:
            a_sub = sub[sub['primary_archetype'] == archetype]
            if len(a_sub) == 0:
                continue
            ax.scatter(a_sub['temperature'], a_sub['era_jump_prob'],
                      c=[archetype_color[archetype]],
                      label=archetype, alpha=0.7, s=80, edgecolors='black', linewidth=0.3)

        ax.set_xlabel('Temperature', fontsize=11)
        ax.set_ylabel('Era Jump Probability', fontsize=11)
        ax.set_title(f'{stratum.title()} Seeds\n(n={len(sub)})', fontsize=12)
        ax.set_xlim(0.5, 2.2)
        ax.set_ylim(0.0, 0.14)
        ax.grid(True, alpha=0.3)

    # Shared legend
    handles = [plt.Line2D([0], [0], marker='o', color='w',
                          markerfacecolor=archetype_color[a], markersize=8,
                          label=a, markeredgecolor='black', markeredgewidth=0.3)
               for a in archetypes]
    fig.legend(handles=handles, loc='center left', bbox_to_anchor=(1.02, 0.5),
               title='Archetype', fontsize=9, title_fontsize=10)

    plt.tight_layout(rect=[0, 0, 0.98, 0.95])
    return fig


def create_heatmap(df):
    """Create 2D heatmap: for each stratum, show most common archetype in temp×jump bins."""

    strata = ['low (stable)', 'medium', 'high (unstable)']
    stratum_order = {s: i for i, s in enumerate(strata)}

    # Define bins
    temp_bins = np.linspace(0.5, 2.2, 8)
    jump_bins = np.linspace(0.0, 0.14, 8)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Dominant Archetype by Parameter Bin\n'
                 '(Temperature × Jump Probability, faceted by seed drift)', fontsize=14, fontweight='bold')

    # Get all archetypes for consistent colormap
    all_archetypes = sorted(df['primary_archetype'].unique())
    archetype_idx = {a: i for i, a in enumerate(all_archetypes)}
    n_archetypes = len(all_archetypes)
    cmap = matplotlib.colormaps.get_cmap('tab20')
    if n_archetypes > 20:
        cmap2 = matplotlib.colormaps.get_cmap('tab20b')
        colors = [cmap(i / 20) for i in range(20)] + [cmap2(i / (n_archetypes - 20)) for i in range(n_archetypes - 20)]
    else:
        colors = [cmap(i / n_archetypes) for i in range(n_archetypes)]

    for stratum in strata:
        ax = axes[stratum_order[stratum]]
        sub = df[df['drift_stratum'] == stratum]

        # Create grid: for each bin, find most common archetype
        grid = np.full((len(jump_bins)-1, len(temp_bins)-1), np.nan)
        counts = np.zeros((len(jump_bins)-1, len(temp_bins)-1))

        for i in range(len(jump_bins)-1):
            for j in range(len(temp_bins)-1):
                bin_dreams = sub[
                    (sub['temperature'] >= temp_bins[j]) & (sub['temperature'] < temp_bins[j+1]) &
                    (sub['era_jump_prob'] >= jump_bins[i]) & (sub['era_jump_prob'] < jump_bins[i+1])
                ]
                if len(bin_dreams) > 0:
                    mode_archetype = bin_dreams['primary_archetype'].mode()
                    if len(mode_archetype) > 0:
                        grid[i, j] = archetype_idx[mode_archetype.iloc[0]]
                        counts[i, j] = len(bin_dreams)

        # Mask empty bins
        masked_grid = np.ma.masked_invalid(grid)

        im = ax.pcolormesh(temp_bins, jump_bins, masked_grid,
                           cmap=matplotlib.colors.ListedColormap(colors),
                           vmin=-0.5, vmax=n_archetypes-0.5,
                           shading='flat')

        # Overlay counts
        for i in range(len(jump_bins)-1):
            for j in range(len(temp_bins)-1):
                if counts[i, j] > 0:
                    ax.text((temp_bins[j] + temp_bins[j+1])/2,
                           (jump_bins[i] + jump_bins[i+1])/2,
                           str(int(counts[i, j])),
                           ha='center', va='center', fontsize=7, color='white',
                           fontweight='bold')

        ax.set_xlabel('Temperature', fontsize=11)
        ax.set_ylabel('Era Jump Probability', fontsize=11)
        ax.set_title(f'{stratum.title()} Seeds\n(n={len(sub)})', fontsize=12)

    # Legend
    handles = [plt.Rectangle((0,0),1,1, color=colors[archetype_idx[a]]) for a in all_archetypes]
    fig.legend(handles, all_archetypes, loc='center left', bbox_to_anchor=(1.02, 0.5),
               title='Archetype', fontsize=9, title_fontsize=10)

    plt.tight_layout(rect=[0, 0, 0.98, 0.95])
    return fig


def create_confidence_scatter(df):
    """Scatter plot showing confidence tiers in parameter space."""

    strata = ['low (stable)', 'medium', 'high (unstable)']
    stratum_order = {s: i for i, s in enumerate(strata)}
    confidence_colors = {'HIGH': '#2ca02c', 'MEDIUM': '#ff7f0e', 'LOW': '#d62728', 'TENTATIVE': '#9467bd'}

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Classification Confidence in Parameter Space', fontsize=14, fontweight='bold')

    for stratum in strata:
        ax = axes[stratum_order[stratum]]
        sub = df[df['drift_stratum'] == stratum]

        for tier in ['HIGH', 'MEDIUM', 'LOW', 'TENTATIVE']:
            t_sub = sub[sub['confidence_tier'] == tier]
            if len(t_sub) > 0:
                ax.scatter(t_sub['temperature'], t_sub['era_jump_prob'],
                          c=confidence_colors.get(tier, '#333333'),
                          label=tier, alpha=0.7, s=80, edgecolors='black', linewidth=0.3)

        ax.set_xlabel('Temperature', fontsize=11)
        ax.set_ylabel('Era Jump Probability', fontsize=11)
        ax.set_title(f'{stratum.title()} Seeds\n(n={len(sub)})', fontsize=12)
        ax.set_xlim(0.5, 2.2)
        ax.set_ylim(0.0, 0.14)
        ax.grid(True, alpha=0.3)

    handles = [plt.Line2D([0], [0], marker='o', color='w',
                          markerfacecolor=confidence_colors[t], markersize=8,
                          label=t, markeredgecolor='black', markeredgewidth=0.3)
               for t in ['HIGH', 'MEDIUM', 'LOW', 'TENTATIVE']]
    fig.legend(handles=handles, loc='center left', bbox_to_anchor=(1.02, 0.5),
               title='Confidence', fontsize=9, title_fontsize=10)

    plt.tight_layout(rect=[0, 0, 0.98, 0.95])
    return fig


def main():
    print("Loading data...")
    dreams, reflections, drift = load_data()
    print(f"Dreams: {len(dreams)}, Reflections: {len(reflections)}, Drift words: {len(drift)}")

    df, q33, q66 = merge_data(dreams, reflections, drift)
    print(f"Merged dataset: {len(df)} dreams")
    print(f"Drift terciles: q33={q33:.3f}, q66={q66:.3f}")
    print(f"Stratum counts:")
    print(df['drift_stratum'].value_counts().sort_index())

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\nGenerating scatter plot...")
    fig1 = create_scatter_plots(df)
    fig1.savefig(f'{OUTPUT_DIR}/parameter_landscape_scatter.png', dpi=150, bbox_inches='tight')
    plt.close(fig1)
    print(f"Saved: {OUTPUT_DIR}/parameter_landscape_scatter.png")

    print("Generating heatmap...")
    fig2 = create_heatmap(df)
    fig2.savefig(f'{OUTPUT_DIR}/parameter_landscape_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close(fig2)
    print(f"Saved: {OUTPUT_DIR}/parameter_landscape_heatmap.png")

    print("Generating confidence scatter...")
    fig3 = create_confidence_scatter(df)
    fig3.savefig(f'{OUTPUT_DIR}/parameter_landscape_confidence.png', dpi=150, bbox_inches='tight')
    plt.close(fig3)
    print(f"Saved: {OUTPUT_DIR}/parameter_landscape_confidence.png")

    # Summary stats
    print("\n=== Summary ===")
    for stratum in ['low (stable)', 'medium', 'high (unstable)']:
        sub = df[df['drift_stratum'] == stratum]
        print(f"\n{stratum.upper()} (n={len(sub)}):")
        print(f"  Temp range: {sub['temperature'].min():.2f}–{sub['temperature'].max():.2f}")
        print(f"  Jump prob range: {sub['era_jump_prob'].min():.3f}–{sub['era_jump_prob'].max():.3f}")
        print(f"  Top archetypes:")
        print(sub['primary_archetype'].value_counts().head(5).to_string().replace('\n', '\n    '))


if __name__ == '__main__':
    main()
