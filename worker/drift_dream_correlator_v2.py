#!/usr/bin/env python3
"""
Drift-Dream Correlator v2 — Full Corpus (n=200)

Dynamically classifies drift type for ALL seed words based on statistical
properties of their drift trajectories, then correlates with dream characteristics.

Replaces the hardcoded DRIFT_TYPES dictionary from v1.
"""

import sqlite3
import json
import statistics
import math
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).parent.parent / "data" / "archaeology_phase1_clean.db"

ERA_ORDER = ['pre-1500', '1500-1700', '1700-1800', '1800-1850', '1850-1900', '1900-1923']

def era_index(era):
    try:
        return ERA_ORDER.index(era)
    except ValueError:
        return 99

def classify_drift_type(word, drift_scores):
    """
    Auto-classify drift type based on statistical properties.
    drift_scores: list of (era_from, era_to, drift_score) tuples
    """
    if not drift_scores:
        return 'unknown'
    
    scores = [s for _, _, s in drift_scores]
    max_drift = max(scores)
    avg_drift = statistics.mean(scores)
    
    # Count how many era transitions we have (max 5 for 6 eras)
    transitions = len(scores)
    
    # Check for spike pattern (one extreme value, others low)
    if transitions > 2:
        sorted_scores = sorted(scores, reverse=True)
        spike_ratio = sorted_scores[0] / (sorted_scores[1] + 0.001)
        if spike_ratio > 2.0 and sorted_scores[0] > 1.0:
            return 'spike'
    
    # High drift across the board
    if avg_drift > 0.8:
        return 'high_drift'
    
    # Very low drift — stable core
    if avg_drift < 0.4 and max_drift < 0.5:
        return 'stable_core'
    
    # Moderate drift — stable concept
    if avg_drift < 0.55:
        return 'stable_concept'
    
    # Moderate-high with some variation — pivot
    if avg_drift >= 0.55 and max_drift > 0.7:
        return 'pivot'
    
    return 'moderate'

def get_dreams_with_drift():
    """Load all dreams with their drift scores."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get dreams with latest reflection only
    cursor.execute("""
        SELECT d.id, d.seed_word, d.start_era, d.temperature, 
               d.jump_count, d.unique_words, d.length,
               dr.primary_archetype, dr.secondary_archetype,
               dr.idf_hybrid_primary, dr.idf_hybrid_method
        FROM dreams d
        LEFT JOIN (
            SELECT dream_id, primary_archetype, secondary_archetype,
                   idf_hybrid_primary, idf_hybrid_method,
                   ROW_NUMBER() OVER (PARTITION BY dream_id ORDER BY id DESC) as rn
            FROM dream_reflections
        ) dr ON d.id = dr.dream_id AND dr.rn = 1
        ORDER BY d.id
    """)
    
    dreams = []
    for row in cursor.fetchall():
        dreams.append({
            'id': row[0],
            'seed_word': row[1],
            'start_era': row[2],
            'temperature': row[3],
            'jump_count': row[4] or 0,
            'unique_words': row[5] or 0,
            'length': row[6] or 0,
            'primary_archetype': row[7],
            'secondary_archetype': row[8],
            'idf_primary': row[9],
            'idf_method': row[10],
        })
    
    # Get drift scores for each seed word
    drift_lookup = {}
    cursor.execute("SELECT word, era_from, era_to, drift_score FROM drift_scores")
    for word, ef, et, score in cursor.fetchall():
        if word not in drift_lookup:
            drift_lookup[word] = []
        drift_lookup[word].append((ef, et, score))
    
    for dream in dreams:
        word = dream['seed_word']
        # Handle RANDOM_ prefix
        if word.startswith('RANDOM_'):
            word = word[7:]
        
        drift_scores = drift_lookup.get(word, [])
        scores = [s for _, _, s in drift_scores]
        dream['drift_scores'] = drift_scores
        dream['max_drift'] = max(scores) if scores else 0
        dream['avg_drift'] = statistics.mean(scores) if scores else 0
        dream['drift_std'] = statistics.stdev(scores) if len(scores) > 1 else 0
        dream['drift_type'] = classify_drift_type(word, drift_scores)
        dream['transitions'] = len(scores)
    
    conn.close()
    return dreams

def pearson_r(x, y):
    """Compute Pearson correlation coefficient."""
    n = len(x)
    if n < 2:
        return 0
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)
    num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    den = math.sqrt(sum((xi - mean_x)**2 for xi in x)) * math.sqrt(sum((yi - mean_y)**2 for yi in y))
    if den == 0:
        return 0
    return num / den

def analyze_correlations(dreams):
    """Analyze patterns in drift-dream relationships."""
    
    print("=" * 70)
    print("DRIFT-DREAM CORRELATION ANALYSIS v2 — Full Corpus (n=%d)" % len(dreams))
    print("=" * 70)
    print()
    
    # Summary stats
    drifts = [d['max_drift'] for d in dreams if d['max_drift'] > 0]
    jumps = [d['jump_count'] for d in dreams]
    temps = [d['temperature'] for d in dreams]
    unique_ratios = [d['unique_words'] / max(d['length'], 1) for d in dreams]
    
    print("CORpus OVERVIEW")
    print("-" * 70)
    print(f"Total dreams: {len(dreams)}")
    print(f"Dreams with drift data: {sum(1 for d in dreams if d['max_drift'] > 0)}")
    print(f"Avg max drift: {statistics.mean(drifts):.3f} (std: {statistics.stdev(drifts):.3f})")
    print(f"Avg jumps: {statistics.mean(jumps):.1f} (std: {statistics.stdev(jumps):.1f})")
    print(f"Avg temperature: {statistics.mean(temps):.2f}")
    print(f"Avg unique word ratio: {statistics.mean(unique_ratios):.3f}")
    print()
    
    # Correlations
    valid = [d for d in dreams if d['max_drift'] > 0]
    if len(valid) > 2:
        print("PEARSON CORRELATIONS (drift magnitude vs dream characteristics)")
        print("-" * 70)
        drift_vals = [d['max_drift'] for d in valid]
        jump_vals = [d['jump_count'] for d in valid]
        temp_vals = [d['temperature'] for d in valid]
        unique_vals = [d['unique_words'] / max(d['length'], 1) for d in valid]
        
        r_drift_jump = pearson_r(drift_vals, jump_vals)
        r_drift_temp = pearson_r(drift_vals, temp_vals)
        r_drift_unique = pearson_r(drift_vals, unique_vals)
        r_temp_jump = pearson_r(temp_vals, jump_vals)
        
        print(f"  Max drift vs Jump count:     r = {r_drift_jump:+.3f}")
        print(f"  Max drift vs Temperature:    r = {r_drift_temp:+.3f}")
        print(f"  Max drift vs Unique ratio:   r = {r_drift_unique:+.3f}")
        print(f"  Temperature vs Jump count:   r = {r_temp_jump:+.3f}")
        print()
    
    # Analysis by drift type
    print("PATTERNS BY DRIFT TYPE")
    print("-" * 70)
    
    by_type = defaultdict(list)
    for d in dreams:
        by_type[d['drift_type']].append(d)
    
    print(f"{'Type':<18} {'Count':>6} {'AvgJumps':>9} {'AvgTemp':>8} {'AvgMaxDrift':>12} {'Top Archetypes'}")
    print("-" * 70)
    
    for drift_type in sorted(by_type.keys(), key=lambda t: -len(by_type[t])):
        dream_list = by_type[drift_type]
        avg_jumps = statistics.mean([d['jump_count'] for d in dream_list])
        avg_temp = statistics.mean([d['temperature'] for d in dream_list])
        avg_max_drift = statistics.mean([d['max_drift'] for d in dream_list if d['max_drift'] > 0]) if any(d['max_drift'] > 0 for d in dream_list) else 0
        archetypes = [d['idf_primary'] or d['primary_archetype'] for d in dream_list if d['idf_primary'] or d['primary_archetype']]
        top_arch = Counter(archetypes).most_common(2) if archetypes else []
        top_str = ', '.join(f"{a}:{c}" for a, c in top_arch)
        
        print(f"{drift_type:<18} {len(dream_list):>6} {avg_jumps:>9.1f} {avg_temp:>8.2f} {avg_max_drift:>12.3f} {top_str}")
    
    print()
    
    # Key insight
    print("KEY INSIGHTS")
    print("-" * 70)
    
    # Find the dreams with highest jumps and their drift types
    top_jumpers = sorted(dreams, key=lambda d: d['jump_count'], reverse=True)[:5]
    print("\nTop 5 jump-count dreams:")
    for d in top_jumpers:
        arch = d['idf_primary'] or d['primary_archetype'] or 'N/A'
        print(f"  #{d['id']:>3} '{d['seed_word']:<20}' drift={d['drift_type']:<16} jumps={d['jump_count']:>3} temp={d['temperature']:.1f} archetype={arch}")
    
    # Find dreams with zero jumps
    zero_jump = [d for d in dreams if d['jump_count'] == 0]
    if zero_jump:
        print(f"\nZero-jump dreams ({len(zero_jump)}):")
        for d in zero_jump[:5]:
            arch = d['idf_primary'] or d['primary_archetype'] or 'N/A'
            print(f"  #{d['id']:>3} '{d['seed_word']:<20}' drift={d['drift_type']:<16} temp={d['temperature']:.1f} archetype={arch}")
    
    print()
    return by_type

def analyze_temperature_interaction(dreams):
    """Analyze drift-temperature interaction."""
    print("=" * 70)
    print("DRIFT × TEMPERATURE INTERACTION")
    print("=" * 70)
    print()
    
    valid = [d for d in dreams if d['max_drift'] > 0]
    
    # Bin by temperature
    low_temp = [d for d in valid if d['temperature'] <= 1.2]
    mid_temp = [d for d in valid if 1.2 < d['temperature'] <= 1.6]
    high_temp = [d for d in valid if d['temperature'] > 1.6]
    
    for label, group in [('Low temp (≤1.2)', low_temp), ('Mid temp (1.2–1.6)', mid_temp), ('High temp (>1.6)', high_temp)]:
        if len(group) < 3:
            continue
        drift_vals = [d['max_drift'] for d in group]
        jump_vals = [d['jump_count'] for d in group]
        r = pearson_r(drift_vals, jump_vals)
        print(f"{label}: n={len(group)}, drift×jump r = {r:+.3f}")
    
    print()

def main():
    print("Loading drift and dream data...")
    dreams = get_dreams_with_drift()
    
    if not dreams:
        print("No dreams found in database.")
        return
    
    by_type = analyze_correlations(dreams)
    analyze_temperature_interaction(dreams)
    
    print("=" * 70)
    print("Analysis complete.")
    print("=" * 70)

if __name__ == "__main__":
    from collections import Counter
    main()
