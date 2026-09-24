#!/usr/bin/env python3
"""
Parameter-Archetype Analysis

Tests whether generative parameters (temperature, era_jump_prob, jump_count)
predict dream archetype. Natural follow-up to null-model rejection of
gravity-well hypothesis: if seed semantics don't constrain archetypes, do
parameters?

Built: 2026-09-24 (hobby block)
"""

import sqlite3
import sys
from collections import Counter, defaultdict
import math

DB_PATH = "../data/archaeology_phase1_clean.db"


def connect():
    return sqlite3.connect(DB_PATH)


def fetch_data():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.temperature, d.era_jump_prob, d.jump_count, d.seed_word,
               dr.idf_hybrid_primary, dr.confidence_tier, dr.confidence_margin
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


def analyze_temperature_gradient(data, label):
    """Archetypes sorted by mean temperature."""
    arch_temps = defaultdict(list)
    arch_jumps = defaultdict(list)
    arch_probs = defaultdict(list)
    for r in data:
        arch_temps[r[4]].append(r[0])
        arch_jumps[r[4]].append(r[2])
        arch_probs[r[4]].append(r[1])

    print(f"\n  Archetype temperature gradient ({label}):")
    sorted_archs = sorted(arch_temps.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True)
    for arch, ts in sorted_archs:
        avg_t = sum(ts) / len(ts)
        avg_j = sum(arch_jumps[arch]) / len(arch_jumps[arch])
        avg_p = sum(arch_probs[arch]) / len(arch_probs[arch])
        print(f"    {arch:20s}: temp={avg_t:.2f}  jumps={avg_j:5.1f}  jump_prob={avg_p:.3f}  (n={len(ts)})")


def analyze_parameter_independence(data):
    """Check that temperature and jump_prob are uncorrelated with seed."""
    seed_temps = defaultdict(list)
    seed_probs = defaultdict(list)
    for r in data:
        seed_temps[r[3]].append(r[0])
        seed_probs[r[3]].append(r[1])

    # Seeds with multiple dreams
    multi_seed_temps = {s: ts for s, ts in seed_temps.items() if len(ts) > 1}
    multi_seed_probs = {s: ps for s, ps in seed_probs.items() if len(ps) > 1}

    print(f"\n  Seeds with multiple dreams: {len(multi_seed_temps)}")
    print(f"  Mean temp stddev across multi-seeds: {sum(math.sqrt(sum((t-sum(ts)/len(ts))**2 for t in ts)/len(ts)) for ts in multi_seed_temps.values()) / len(multi_seed_temps):.3f}" if multi_seed_temps else "  N/A")


def analyze():
    rows = fetch_data()
    print(f"Total classified dreams: {len(rows)}")

    all_rows = rows
    high_conf = [r for r in rows if r[5] in ('HIGH', 'MEDIUM')]
    low_conf = [r for r in rows if r[5] == 'LOW']
    tentative = [r for r in rows if r[5] == 'TENTATIVE']

    print(f"  HIGH confidence: {len([r for r in rows if r[5]=='HIGH'])}")
    print(f"  MEDIUM confidence: {len([r for r in rows if r[5]=='MEDIUM'])}")
    print(f"  LOW confidence: {len(low_conf)}")
    print(f"  TENTATIVE: {len(tentative)}")
    print()

    # Parameter independence check
    analyze_parameter_independence(all_rows)

    for label, data in [("ALL", all_rows), ("HIGH+MED", high_conf)]:
        print(f"\n{'='*60}")
        print(f"=== {label} (n={len(data)}) ===")
        print(f"{'='*60}")
        if len(data) < 20:
            print("  (too few for reliable analysis)")
            continue

        temps = [r[0] for r in data]
        archetypes = [r[4] for r in data]

        print(f"\nTemperature range: {min(temps):.2f} - {max(temps):.2f} (mean={sum(temps)/len(temps):.2f})")

        # Temp bins
        temp_bins = defaultdict(list)
        for r in data:
            t = r[0]
            if t < 1.0:
                temp_bins['low'].append(r)
            elif t <= 1.4:
                temp_bins['med'].append(r)
            else:
                temp_bins['high'].append(r)

        print(f"  Low temp (<1.0): {len(temp_bins['low'])}")
        print(f"  Med temp (1.0-1.4): {len(temp_bins['med'])}")
        print(f"  High temp (>1.4): {len(temp_bins['high'])}")

        all_archetypes = sorted(set(archetypes))
        print(f"\n  Archetypes ({len(all_archetypes)}): {', '.join(all_archetypes)}")

        analyze_temperature_gradient(data, label)

        # Contingency: temp bin x top archetypes
        top_archetypes = [a for a, _ in Counter(archetypes).most_common(8)]
        bins = ['low', 'med', 'high']
        table = []
        for b in bins:
            row = []
            bin_archetypes = [r[4] for r in temp_bins[b]]
            for a in top_archetypes:
                row.append(bin_archetypes.count(a))
            table.append(row)

        print(f"\n  Temp bin x Top archetype counts:")
        header = "bin    " + " ".join(f"{a[:8]:>8s}" for a in top_archetypes)
        print(f"  {header}")
        for i, b in enumerate(bins):
            line = f"{b:6s} " + " ".join(f"{table[i][j]:8d}" for j in range(len(top_archetypes)))
            print(f"  {line}")

        chi2, df = chi_square(table)
        cv = cramers_v(table)
        print(f"\n  Temp-archetype: Chi²({df}) = {chi2:.2f}, Cramer's V = {cv:.3f}")
        if cv < 0.1:
            print("  → Negligible association")
        elif cv < 0.3:
            print("  → Small association")
        elif cv < 0.5:
            print("  → Medium association")
        else:
            print("  → Large association")

        # Jump prob vs archetype
        jump_probs = [r[1] for r in data]
        print(f"\n  Jump prob range: {min(jump_probs):.3f} - {max(jump_probs):.3f}")

        jump_bins = defaultdict(list)
        for r in data:
            j = r[1]
            if j < 0.05:
                jump_bins['low'].append(r)
            elif j <= 0.08:
                jump_bins['med'].append(r)
            else:
                jump_bins['high'].append(r)

        # Jump prob contingency
        jtable = []
        for b in bins:
            row = []
            bin_archetypes = [r[4] for r in jump_bins[b]]
            for a in top_archetypes:
                row.append(bin_archetypes.count(a))
            jtable.append(row)

        chi2_j, df_j = chi_square(jtable)
        cv_j = cramers_v(jtable)
        print(f"  Jump-archetype: Chi²({df_j}) = {chi2_j:.2f}, Cramer's V = {cv_j:.3f}")

        # Combined wild/tame
        wild = [r for r in data if r[0] > 1.4 and r[1] > 0.08]
        tame = [r for r in data if r[0] < 1.0 and r[1] < 0.05]
        print(f"\n  'Wild' (temp>1.4, jump>0.08): {len(wild)}")
        if wild:
            for a, c in Counter(r[4] for r in wild).most_common():
                print(f"    {a}: {c}")
        print(f"  'Tame' (temp<1.0, jump<0.05): {len(tame)}")
        if tame:
            for a, c in Counter(r[4] for r in tame).most_common():
                print(f"    {a}: {c}")

        # Simple rule: predict archetype from temp alone
        print(f"\n  --- Naïve temperature classifier ---")
        correct = 0
        for r in data:
            t = r[0]
            actual = r[4]
            # Predict the archetype with mean temp closest to this dream's temp
            arch_temps = defaultdict(list)
            for rr in data:
                if rr[3] != r[3]:  # leave-one-out (by seed)
                    arch_temps[rr[4]].append(rr[0])
            if not arch_temps:
                continue
            pred = min(arch_temps.items(), key=lambda x: abs(sum(x[1])/len(x[1]) - t))[0]
            if pred == actual:
                correct += 1

        print(f"  Leave-one-seed-out accuracy: {correct}/{len(data)} = {correct/len(data)*100:.1f}%")
        print(f"  Chance baseline (random guess): {1/len(set(archetypes))*100:.1f}%")

    print()


def main():
    analyze()


if __name__ == "__main__":
    main()
