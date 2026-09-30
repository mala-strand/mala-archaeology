#!/usr/bin/env python3
"""
Logistic Regression Model: drift × temperature interaction

Formal test of the escape energy model.

Hypotheses:
1. Temperature positively predicts abstract/religious/power (ARP) family.
2. This effect is stronger for low-drift (stable) seeds than high-drift (unstable) seeds.
3. The temp×drift interaction is negative: high drift attenuates the temperature effect.

Built: 2026-09-30 (hobby block)
"""

import sqlite3
import sys
import numpy as np
from collections import Counter
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

DB_PATH = "../data/archaeology_phase1_clean.db"

# Semantic families derived from parameter-archetype gradient findings
FAMILIES = {
    'abstract_religious_power': [
        'abstract', 'power_divine', 'power_political', 'power_institutional',
        'power_personal', 'religious_moral', 'religious_devotion', 'religious_cosmic'
    ],
    'natural_domestic': ['natural', 'domestic', 'wilderness'],
    'conflict_temporal': ['conflict', 'temporal'],
    'social_material': ['commerce', 'urban', 'craft', 'legacy', 'identity', 'knowledge'],
}

FAMILY_LABELS = {
    'abstract_religious_power': 'ARP (abstract/religious/power)',
    'natural_domestic': 'ND (natural/domestic)',
    'conflict_temporal': 'CT (conflict/temporal)',
    'social_material': 'SM (social/material)',
}


def family_of(archetype):
    for fam, members in FAMILIES.items():
        if archetype in members:
            return fam
    return None


def fetch_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            d.id,
            d.seed_word,
            d.temperature,
            d.era_jump_prob,
            d.jump_count,
            dr.penalized_primary,
            (SELECT AVG(drift_score) FROM drift_scores ds WHERE ds.word = d.seed_word) as avg_drift,
            (SELECT COUNT(*) FROM drift_scores ds WHERE ds.word = d.seed_word) as drift_pairs
        FROM dreams d
        JOIN dream_reflections dr ON d.id = dr.dream_id
        WHERE dr.penalized_primary IS NOT NULL
          AND dr.penalized_primary != 'unclassifiable'
          AND dr.penalized_primary != 'bodily'
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def log_likelihood(model, X, y):
    """Compute log-likelihood of fitted model."""
    probas = model.predict_proba(X)
    ll = 0.0
    for i, yi in enumerate(y):
        ll += np.log(probas[i, yi] + 1e-15)
    return ll


def mcfadden_pseudo_r2(model, X, y, n_classes):
    """McFadden's pseudo-R² = 1 - LL_model / LL_null."""
    ll_model = log_likelihood(model, X, y)
    # Null model: intercept-only
    null_proba = np.ones((len(y), n_classes)) / n_classes
    ll_null = 0.0
    for i, yi in enumerate(y):
        ll_null += np.log(null_proba[i, yi] + 1e-15)
    return 1 - (ll_model / ll_null)


def fit_multinomial(X, y, family_names, label, feature_names=None):
    """Fit multinomial logistic regression and report results."""
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    model = LogisticRegression(
        solver='lbfgs',
        C=np.inf,
        max_iter=1000,
        random_state=42,
    )
    model.fit(Xs, y)

    n_classes = len(family_names)
    r2 = mcfadden_pseudo_r2(model, Xs, y, n_classes)
    acc = model.score(Xs, y)

    print(f"\n{'='*70}")
    print(f"MULTINOMIAL LOGISTIC REGRESSION: {label}")
    print(f"{'='*70}")
    print(f"  N = {len(y)}")
    print(f"  Classes: {n_classes} ({', '.join(family_names.values())})")
    print(f"  McFadden pseudo-R² = {r2:.4f}")
    print(f"  Accuracy = {acc:.3f} (baseline = {max(Counter(y).values())/len(y):.3f})")

    if feature_names is None:
        feature_names = ['temp', 'drift', 'jump_prob', 'temp×drift'][:X.shape[1]]
    print(f"\n  Coefficients (log-odds per 1 SD increase):")
    for j, fam in enumerate(model.classes_):
        print(f"    → {family_names[fam]}:")
        for i, feat in enumerate(feature_names):
            print(f"      {feat:12s}: {model.coef_[j, i]:+7.3f}")

    print(f"\n  Odds Ratios (per 1 SD increase):")
    for j, fam in enumerate(model.classes_):
        print(f"    → {family_names[fam]}:")
        for i, feat in enumerate(feature_names):
            or_val = np.exp(model.coef_[j, i])
            print(f"      {feat:12s}: {or_val:7.3f}")

    return model, scaler, r2, acc


def fit_binary(X, y, label, feature_names=None):
    """Fit binary logistic regression and report results."""
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    model = LogisticRegression(
        solver='lbfgs',
        C=np.inf,
        max_iter=1000,
        random_state=42,
    )
    model.fit(Xs, y)

    ll_model = log_likelihood(model, Xs, y)
    p_null = np.mean(y)
    ll_null = len(y) * (p_null * np.log(p_null + 1e-15) + (1-p_null) * np.log(1-p_null + 1e-15))
    r2 = 1 - (ll_model / ll_null)
    acc = model.score(Xs, y)

    print(f"\n{'='*70}")
    print(f"BINARY LOGISTIC REGRESSION: {label}")
    print(f"{'='*70}")
    print(f"  N = {len(y)}, positive rate = {np.mean(y):.3f}")
    print(f"  McFadden pseudo-R² = {r2:.4f}")
    print(f"  Accuracy = {acc:.3f}")

    if feature_names is None:
        feature_names = ['temp', 'drift', 'jump_prob', 'temp×drift'][:X.shape[1]]
    print(f"\n  Coefficients (log-odds per 1 SD increase):")
    for i, feat in enumerate(feature_names):
        print(f"    {feat:12s}: {model.coef_[0, i]:+7.3f}")

    print(f"\n  Odds Ratios (per 1 SD increase):")
    for i, feat in enumerate(feature_names):
        or_val = np.exp(model.coef_[0, i])
        print(f"    {feat:12s}: {or_val:7.3f}")

    return model, scaler, r2, acc


def stratified_temp_effect(rows, family_names):
    """Fit binary ARP models within drift strata to show escape energy."""
    # Build dataset
    data = []
    for r in rows:
        if r[6] is None:
            continue
        fam = family_of(r[5])
        if fam is None:
            continue
        data.append({
            'temp': r[2],
            'drift': r[6],
            'jump_prob': r[3],
            'arp': 1 if fam == 'abstract_religious_power' else 0,
        })

    drifts = [d['drift'] for d in data]
    t1 = np.percentile(drifts, 33.3)
    t2 = np.percentile(drifts, 66.7)

    print(f"\n{'='*70}")
    print("STRATIFIED ANALYSIS: Temperature → ARP by drift stratum")
    print(f"{'='*70}")
    print(f"  Drift terciles: low ≤ {t1:.3f}, med ≤ {t2:.3f}, high > {t2:.3f}")

    for label, subset in [
        ('low', [d for d in data if d['drift'] <= t1]),
        ('med', [d for d in data if t1 < d['drift'] <= t2]),
        ('high', [d for d in data if d['drift'] > t2]),
    ]:
        if len(subset) < 15:
            print(f"\n  {label.upper()} (n={len(subset)}): too few for reliable fit")
            continue

        X = np.array([[d['temp']] for d in subset])
        y = np.array([d['arp'] for d in subset])
        pos_rate = np.mean(y)

        scaler = StandardScaler()
        Xs = scaler.fit_transform(X)

        model = LogisticRegression(solver='lbfgs', C=np.inf, max_iter=1000)
        model.fit(Xs, y)

        coef = model.coef_[0, 0]
        or_val = np.exp(coef)

        print(f"\n  {label.upper()} (n={len(subset)}, ARP rate={pos_rate:.3f}):")
        print(f"    Temp coefficient: {coef:+.3f}")
        print(f"    Temp odds ratio:  {or_val:.3f}")
        print(f"    Accuracy:         {model.score(Xs, y):.3f}")


def main():
    print("=" * 70)
    print("LOGISTIC REGRESSION: drift × temperature interaction")
    print("=" * 70)

    rows = fetch_data()
    print(f"\nFetched {len(rows)} dreams with penalized classifications")

    # Filter to rows with drift data
    data = []
    for r in rows:
        avg_drift = r[6]
        drift_pairs = r[7]
        if avg_drift is None or drift_pairs < 2:
            continue
        fam = family_of(r[5])
        if fam is None:
            continue
        data.append({
            'id': r[0],
            'seed': r[1],
            'temp': r[2],
            'jump_prob': r[3],
            'jump_count': r[4],
            'archetype': r[5],
            'family': fam,
            'drift': avg_drift,
        })

    print(f"After drift filter: {len(data)} dreams")

    # Family distribution
    fam_counts = Counter(d['family'] for d in data)
    print("\nFamily distribution:")
    for fam, count in fam_counts.most_common():
        print(f"  {FAMILY_LABELS[fam]:40s}: {count:3d}")

    # Build predictor matrix
    temps = np.array([d['temp'] for d in data])
    drifts = np.array([d['drift'] for d in data])
    jump_probs = np.array([d['jump_prob'] for d in data])
    temp_drift = temps * drifts

    # Encode families
    family_list = list(FAMILIES.keys())
    family_names = {i: FAMILY_LABELS[f] for i, f in enumerate(family_list)}
    y_multi = np.array([family_list.index(d['family']) for d in data])
    y_binary = np.array([1 if d['family'] == 'abstract_religious_power' else 0 for d in data])

    # --- Model 1: Multinomial with interaction ---
    X_full = np.column_stack([temps, drifts, jump_probs, temp_drift])
    fit_multinomial(X_full, y_multi, family_names, "full model (temp + drift + jump_prob + temp×drift)")

    # --- Model 2: Multinomial without interaction ---
    X_noint = np.column_stack([temps, drifts, jump_probs])
    model_noint, scaler_noint, r2_noint, acc_noint = fit_multinomial(
        X_noint, y_multi, family_names, "no-interaction model (temp + drift + jump_prob)"
    )

    # Re-fit and compare properly
    scaler_full = StandardScaler()
    X_full_s = scaler_full.fit_transform(X_full)
    model_full_multi = LogisticRegression(solver='lbfgs', C=np.inf, max_iter=1000, random_state=42)
    model_full_multi.fit(X_full_s, y_multi)
    r2_full = mcfadden_pseudo_r2(model_full_multi, X_full_s, y_multi, len(family_list))

    scaler_noint = StandardScaler()
    X_noint_s = scaler_noint.fit_transform(X_noint)
    model_noint_multi = LogisticRegression(solver='lbfgs', C=np.inf, max_iter=1000, random_state=42)
    model_noint_multi.fit(X_noint_s, y_multi)
    r2_noint = mcfadden_pseudo_r2(model_noint_multi, X_noint_s, y_multi, len(family_list))

    print(f"\n  {'='*70}")
    print("  MULTINOMIAL MODEL COMPARISON")
    print(f"  {'='*70}")
    print(f"    Full (with interaction):    R² = {r2_full:.4f}")
    print(f"    Reduced (no interaction):   R² = {r2_noint:.4f}")
    print(f"    ΔR²:                        {r2_full - r2_noint:+.4f}")

    # --- Model 3: Binary ARP vs rest, with interaction ---
    fit_binary(X_full, y_binary, "ARP vs all others (with interaction)")

    # --- Model 4: Binary ARP vs rest, no interaction ---
    model_bin_noint, _, _, _ = fit_binary(X_noint, y_binary, "ARP vs all others (no interaction)")

    # --- Stratified analysis ---
    stratified_temp_effect(rows, family_names)

    # --- Coefficient summary table ---
    print(f"\n{'='*70}")
    print("SUMMARY: Escape Energy Model Test")
    print(f"{'='*70}")
    print("""
  Hypothesis: Temperature predicts ARP family, but this effect is
  attenuated for high-drift seeds (negative temp×drift interaction).

  If supported:
    - temp coefficient: positive
    - temp×drift interaction: negative
    - stratified: low-drift OR >> high-drift OR
""")

    print("\nDone.")


if __name__ == "__main__":
    main()
