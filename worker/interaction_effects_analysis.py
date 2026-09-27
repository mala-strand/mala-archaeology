#!/usr/bin/env python3
"""
Interaction Effects Analysis: Parameters × Seed Drift

Tests whether the parameter-archetype association (temperature, jump_prob)
varies by seed drift magnitude. 

Hypothesis: If seed drift amplifies parameter effects, we expect stronger
temperature-archetype association for high-drift seeds. If stable seeds
anchor dreams regardless of parameters, we expect weaker association for
low-drift seeds.

Built: 2026-09-25 (hobby block)
"""

import sqlite3
import sys
from collections import Counter, defaultdict
import math

DB_PATH = "../data/archaeology_phase1_clean.db"


def connect():
    return sqlite3.connect(DB_PATH)


def fetch_data():
    """Join dreams with reflections and drift scores."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            d.id,
            d.seed_word,
            d.temperature,
            d.era_jump_prob,
            d.jump_count,
            dr.idf_hybrid_primary,
            dr.confidence_tier,
            dr.confidence_margin,
            (SELECT AVG(drift_score) FROM drift_scores ds WHERE ds.word = d.seed_word) as avg_drift,
            (SELECT COUNT(*) FROM drift_scores ds WHERE ds.word = d.seed_word) as drift_pairs
        FROM dreams d
        JOIN dream_reflections dr ON d.id = dr.dream_id
        WHERE dr.idf_hybrid_primary IS NOT NULL
          AND dr.idf_hybrid_primary != 'unclassifiable'
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def chi_square(observed):
    row_totals = [sum(row) for row in observed]
    col_totals = [sum(observed[i][j] for i in range(len(observed))) for j in range(len(observed[0]))]
    total = sum(row_totals)
    if total == 0:
        return 0.0, 1.0

    expected = []
    for i in range(len(observed)):
        row = []
        for j in range(len(observed[0])):
            e = (row_totals[i] * col_totals[j]) / total
            row.append(e)
        expected.append(row)

    chi2 = 0.0
    for i in range(len(observed)):
        for j in range(len(observed[0])):
            o = observed[i][j]
            e = expected[i][j]
            if e > 0:
                chi2 += ((o - e) ** 2) / e

    df = (len(observed) - 1) * (len(observed[0]) - 1)
    return chi2, df


def cramers_v(observed):
    chi2, df = chi_square(observed)
    total = sum(sum(row) for row in observed)
    if total == 0 or df == 0:
        return 0.0
    k = min(len(observed), len(observed[0]))
    return math.sqrt(chi2 / (total * (k - 1)))


def temp_bin(t):
    if t < 1.0:
        return 'low'
    elif t <= 1.4:
        return 'med'
    else:
        return 'high'


def jump_bin(j):
    if j < 0.05:
        return 'low'
    elif j <= 0.08:
        return 'med'
    else:
        return 'high'


def drift_stratum(avg_drift, method='tercile'):
    """Classify drift into low/med/high."""
    if method == 'fixed':
        if avg_drift < 0.6:
            return 'low'
        elif avg_drift < 0.8:
            return 'med'
        else:
            return 'high'
    # tercile-based: computed from data
    return None  # computed dynamically


def analyze_interactions(rows):
    print("=" * 70)
    print("INTERACTION EFFECTS: Parameters × Seed Drift")
    print("=" * 70)

    # Data overview
    print(f"\nTotal dreams: {len(rows)}")
    drifts = [r[8] for r in rows if r[8] is not None]
    print(f"Dreams with drift data: {len(drifts)}")
    print(f"Drift range: {min(drifts):.3f} - {max(drifts):.3f} (mean={sum(drifts)/len(drifts):.3f})")

    # Tercile thresholds
    sorted_drifts = sorted(drifts)
    n = len(sorted_drifts)
    t1 = sorted_drifts[n // 3]
    t2 = sorted_drifts[2 * n // 3]
    print(f"Drift terciles: low<={t1:.3f}, med<={t2:.3f}, high>{t2:.3f}")

    def classify_drift(d):
        if d <= t1:
            return 'low'
        elif d <= t2:
            return 'med'
        else:
            return 'high'

    # Build strata
    strata = {'low': [], 'med': [], 'high': []}
    for r in rows:
        if r[8] is not None:
            strata[classify_drift(r[8])].append(r)

    for s in ['low', 'med', 'high']:
        print(f"\n{'='*70}")
        print(f"DRIFT STRATUM: {s.upper()} (n={len(strata[s])})")
        print(f"{'='*70}")
        data = strata[s]
        if len(data) < 20:
            print("  (too few for reliable analysis)")
            continue

        # Also filter by confidence
        high_conf = [r for r in data if r[6] in ('HIGH', 'MEDIUM')]
        print(f"  HIGH+MED confidence: {len(high_conf)}")

        for label, subset in [("ALL", data), ("HIGH+MED", high_conf)]:
            if len(subset) < 15:
                continue
            print(f"\n  --- {label} (n={len(subset)}) ---")

            temps = [r[2] for r in subset]
            jumps = [r[3] for r in subset]
            archetypes = [r[5] for r in subset]
            print(f"    Temp: {min(temps):.2f}-{max(temps):.2f} (mean={sum(temps)/len(temps):.2f})")
            print(f"    Jump prob: {min(jumps):.3f}-{max(jumps):.3f} (mean={sum(jumps)/len(jumps):.3f})")

            # Temp-archetype contingency
            top_archs = [a for a, _ in Counter(archetypes).most_common(8)]
            tbins = ['low', 'med', 'high']
            ttable = []
            for b in tbins:
                bin_archs = [r[5] for r in subset if temp_bin(r[2]) == b]
                row = [bin_archs.count(a) for a in top_archs]
                ttable.append(row)

            cv_t = cramers_v(ttable)
            print(f"    Temp-archetype Cramer's V = {cv_t:.3f}")

            # Jump-archetype contingency
            jtable = []
            for b in tbins:
                bin_archs = [r[5] for r in subset if jump_bin(r[3]) == b]
                row = [bin_archs.count(a) for a in top_archs]
                jtable.append(row)

            cv_j = cramers_v(jtable)
            print(f"    Jump-archetype Cramer's V = {cv_j:.3f}")

            # Archetype gradient by temp
            arch_temps = defaultdict(list)
            for r in subset:
                arch_temps[r[5]].append(r[2])
            sorted_archs = sorted(arch_temps.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True)
            print(f"    Highest-temp archetypes: ", end="")
            for arch, ts in sorted_archs[:3]:
                print(f"{arch}({sum(ts)/len(ts):.2f}) ", end="")
            print()
            print(f"    Lowest-temp archetypes:  ", end="")
            for arch, ts in sorted_archs[-3:]:
                print(f"{arch}({sum(ts)/len(ts):.2f}) ", end="")
            print()

    # Cross-stratum comparison
    print(f"\n{'='*70}")
    print("CROSS-STRATUM COMPARISON")
    print(f"{'='*70}")

    print("\n  Temp-archetype Cramer's V by drift stratum:")
    for s in ['low', 'med', 'high']:
        data = strata[s]
        high_conf = [r for r in data if r[6] in ('HIGH', 'MEDIUM')]
        if len(high_conf) >= 15:
            archetypes = [r[5] for r in high_conf]
            top_archs = [a for a, _ in Counter(archetypes).most_common(8)]
            ttable = []
            for b in ['low', 'med', 'high']:
                bin_archs = [r[5] for r in high_conf if temp_bin(r[2]) == b]
                row = [bin_archs.count(a) for a in top_archs]
                ttable.append(row)
            cv = cramers_v(ttable)
            print(f"    {s:4s} (HIGH+MED n={len(high_conf)}): V = {cv:.3f}")

    print("\n  Jump-archetype Cramer's V by drift stratum:")
    for s in ['low', 'med', 'high']:
        data = strata[s]
        high_conf = [r for r in data if r[6] in ('HIGH', 'MEDIUM')]
        if len(high_conf) >= 15:
            archetypes = [r[5] for r in high_conf]
            top_archs = [a for a, _ in Counter(archetypes).most_common(8)]
            jtable = []
            for b in ['low', 'med', 'high']:
                bin_archs = [r[5] for r in high_conf if jump_bin(r[3]) == b]
                row = [bin_archs.count(a) for a in top_archs]
                jtable.append(row)
            cv = cramers_v(jtable)
            print(f"    {s:4s} (HIGH+MED n={len(high_conf)}): V = {cv:.3f}")

    # Wild vs tame within strata
    print(f"\n  Wild dreams (temp>1.4, jump>0.08) by drift stratum:")
    for s in ['low', 'med', 'high']:
        wild = [r for r in strata[s] if r[2] > 1.4 and r[3] > 0.08]
        print(f"    {s:4s}: {len(wild)} dreams, archetypes: {dict(Counter(r[5] for r in wild).most_common(3))}")

    print(f"\n  Tame dreams (temp<1.0, jump<0.05) by drift stratum:")
    for s in ['low', 'med', 'high']:
        tame = [r for r in strata[s] if r[2] < 1.0 and r[3] < 0.05]
        print(f"    {s:4s}: {len(tame)} dreams, archetypes: {dict(Counter(r[5] for r in tame).most_common(3))}")

    # Drift-temperature correlation (structural check)
    print(f"\n  Structural check: drift vs parameters")
    all_drifts = [r[8] for r in rows if r[8] is not None]
    all_temps = [r[2] for r in rows if r[8] is not None]
    all_jumps = [r[3] for r in rows if r[8] is not None]

    def pearson(x, y):
        n = len(x)
        mx, my = sum(x)/n, sum(y)/n
        num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
        denx = math.sqrt(sum((xi - mx)**2 for xi in x))
        deny = math.sqrt(sum((yi - my)**2 for yi in y))
        if denx == 0 or deny == 0:
            return 0.0
        return num / (denx * deny)

    print(f"    Drift × Temperature: r = {pearson(all_drifts, all_temps):.3f}")
    print(f"    Drift × Jump prob:   r = {pearson(all_drifts, all_jumps):.3f}")
    print(f"    Drift × Actual jumps: r = {pearson(all_drifts, [r[4] for r in rows if r[8] is not None]):.3f}")


def main():
    rows = fetch_data()
    analyze_interactions(rows)


if __name__ == "__main__":
    main()
