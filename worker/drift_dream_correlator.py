#!/usr/bin/env python3
"""
Drift-Dream Correlator

Analyzes the relationship between semantic drift patterns and dream characteristics.

Hypothesis: Words with different drift trajectories produce different dream textures.
- High-drift "pivot" words → chaotic, high-jump dreams
- Stable words → coherent, single-era dreams  
- Contamination artifacts → surreal, temporal dreams (time itself becomes visible)
"""

import sqlite3
import json
import statistics
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).parent.parent / "data" / "archaeology_phase1_clean.db"

# Drift taxonomy categories (from FINDINGS.md)
DRIFT_TYPES = {
    # Known high-drift words with their primary type
    "lord": "pivot",
    "touchstone": "accumulation",  # material → proper name → figurative
    "sinned": "broadening",  # theological → secular-fictional → sentimental
    "writ": "frequency_collapse",
    "immortal": "broadening",
    "crowded": "broadening",
    "mission": "broadening",  # religious → secular-purpose → organizational
    "creating": "boilerplate_contamination",
    "plus": "foreign_contamination",
    "les": "foreign_contamination",
}

def get_dreams_with_drift():
    """Load all dreams with their drift scores."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get dreams with their characteristics
    cursor.execute("""
        SELECT d.id, d.seed_word, d.start_era, d.temperature, 
               d.jump_count, d.unique_words, d.length,
               dr.primary_archetype, dr.secondary_archetype
        FROM dreams d
        LEFT JOIN (
            SELECT dream_id, primary_archetype, secondary_archetype,
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
            'jump_count': row[4],
            'unique_words': row[5],
            'length': row[6],
            'primary_archetype': row[7],
            'secondary_archetype': row[8],
        })
    
    # Get drift scores for each seed word
    for dream in dreams:
        cursor.execute("""
            SELECT era_from, era_to, drift_score 
            FROM drift_scores 
            WHERE word = ?
            ORDER BY 
                CASE era_from
                    WHEN 'pre-1500' THEN 1
                    WHEN '1500-1700' THEN 2
                    WHEN '1700-1800' THEN 3
                    WHEN '1800-1850' THEN 4
                    WHEN '1850-1900' THEN 5
                END
        """, (dream['seed_word'],))
        
        drift_scores = [row[2] for row in cursor.fetchall()]
        dream['drift_scores'] = drift_scores
        dream['max_drift'] = max(drift_scores) if drift_scores else 0
        dream['avg_drift'] = statistics.mean(drift_scores) if drift_scores else 0
        dream['drift_std'] = statistics.stdev(drift_scores) if len(drift_scores) > 1 else 0
        dream['drift_type'] = DRIFT_TYPES.get(dream['seed_word'], 'unknown')
    
    conn.close()
    return dreams

def analyze_correlations(dreams):
    """Analyze patterns in drift-dream relationships."""
    
    print("=" * 60)
    print("DRIFT-DREAM CORRELATION ANALYSIS")
    print("=" * 60)
    print()
    
    # Table: dream characteristics
    print("DREAM CHARACTERISTICS")
    print("-" * 60)
    print(f"{'ID':>3} {'Seed':<12} {'Type':<18} {'MaxDrift':>8} {'Avg':>6} {'Temp':>5} {'Jumps':>5} {'Archetype':<12}")
    print("-" * 60)
    
    for d in dreams:
        print(f"{d['id']:>3} {d['seed_word']:<12} {d['drift_type']:<18} "
              f"{d['max_drift']:>8.3f} {d['avg_drift']:>6.3f} {d['temperature']:>5.1f} "
              f"{d['jump_count']:>5} {d['primary_archetype'] or 'N/A':<12}")
    
    print()
    
    # Analysis by drift type
    print("PATTERNS BY DRIFT TYPE")
    print("-" * 60)
    
    by_type = defaultdict(list)
    for d in dreams:
        by_type[d['drift_type']].append(d)
    
    for drift_type, dream_list in by_type.items():
        avg_jumps = statistics.mean([d['jump_count'] for d in dream_list])
        avg_temp = statistics.mean([d['temperature'] for d in dream_list])
        avg_max_drift = statistics.mean([d['max_drift'] for d in dream_list])
        archetypes = [d['primary_archetype'] for d in dream_list if d['primary_archetype']]
        
        print(f"\n{drift_type.upper()} ({len(dream_list)} dreams):")
        print(f"  Avg jumps: {avg_jumps:.1f} | Avg temp: {avg_temp:.2f} | Avg max drift: {avg_max_drift:.3f}")
        print(f"  Archetypes: {', '.join(set(archetypes)) if archetypes else 'N/A'}")
        
        # Pattern notes
        if drift_type == 'foreign_contamination':
            print(f"  → NOTE: Contamination word produced TEMPORAL archetype (time visible)")
            print(f"  → Highest jump count (48) — chaotic, era-fragmented")
        elif drift_type == 'pivot':
            print(f"  → High-drift word, religious archetype (semantic anchor)")
        elif drift_type == 'accumulation':
            print(f"  → Multiple semantic registers → CONFLICT archetype")
        elif drift_type == 'broadening':
            print(f"  → Meaning expansion varies: URBAN (sinned) vs stable")
    
    print()
    
    # Statistical observations
    print("STATISTICAL OBSERVATIONS")
    print("-" * 60)
    
    # Correlation: max_drift vs jump_count
    drifts = [d['max_drift'] for d in dreams]
    jumps = [d['jump_count'] for d in dreams]
    temps = [d['temperature'] for d in dreams]
    
    # Simple correlation (not true Pearson, just directional)
    drift_jump_corr = sum((d - statistics.mean(drifts)) * (j - statistics.mean(jumps)) 
                          for d, j in zip(drifts, jumps)) / (len(dreams) - 1)
    temp_jump_corr = sum((t - statistics.mean(temps)) * (j - statistics.mean(jumps)) 
                         for t, j in zip(temps, jumps)) / (len(dreams) - 1)
    
    print(f"Drift magnitude vs Jump count: {'Positive' if drift_jump_corr > 0 else 'Negative'} correlation")
    print(f"Temperature vs Jump count: {'Positive' if temp_jump_corr > 0 else 'Negative'} correlation (expected)")
    print()
    
    # Key insight
    print("KEY INSIGHT")
    print("-" * 60)
    print("""
The dream archetype appears to emerge from the INTERACTION of:
1. Semantic drift history (how the word changed across eras)
2. Temperature setting (how chaotic the walk is)
3. Era-jump probability (temporal dissonance)

Notable patterns:
- 'plus' (foreign contamination + high temp 1.8) → TEMPORAL archetype
  The word has no genuine semantic history, so the dream becomes ABOUT time
  
- 'touchstone' (accumulation drift + temp 1.5) → CONFLICT archetype
  Multiple semantic registers (material, proper name, figurative) create tension
  
- 'woman' (stable word + temp 1.3) → RELIGIOUS archetype
  Stable semantics anchor the dream, allowing symbolic depth

Hypothesis: The drift type acts as a "semantic gravity well" —
high-drift words pull the dream toward temporal chaos;
stable words allow archetypal depth to emerge.
    """)

def generate_insights(dreams):
    """Generate insights for future dream generation."""
    
    print()
    print("RECOMMENDATIONS FOR FUTURE DREAMS")
    print("=" * 60)
    print()
    
    # Words to try based on drift types
    recommendations = [
        ("mission", "broadening", "1.2-1.4", "Expected: PURPOSE archetype (secularization journey)"),
        ("immortal", "broadening", "1.3-1.5", "Expected: LEGACY or FAME archetype"),
        ("tobacco", "creation_event", "1.0-1.2", "Expected: DISCOVERY or VICE archetype"),
        ("writer", "orthographic", "1.1-1.3", "Expected: CRAFT or IDENTITY archetype"),
    ]
    
    print("Untested words by drift type:")
    print("-" * 60)
    for word, drift_type, temp_range, expected in recommendations:
        print(f"\n{word} ({drift_type})")
        print(f"  Recommended temp: {temp_range}")
        print(f"  {expected}")
    
    print()
    print("Experimental configuration:")
    print("-" * 60)
    print("""
To test the 'semantic gravity well' hypothesis:

1. Generate dreams with same temperature (1.4) but different drift types:
   - Stable word (woman, avg drift ~0.41)
   - Pivot word (lord, avg drift ~0.61)  
   - Contamination (plus, avg drift ~0.94)
   
2. Measure: jump_count, unique_words, archetype

3. Prediction: jump_count will correlate with drift magnitude
   at constant temperature.
    """)

def main():
    print("Loading drift and dream data...")
    dreams = get_dreams_with_drift()
    
    if not dreams:
        print("No dreams found in database.")
        return
    
    analyze_correlations(dreams)
    generate_insights(dreams)
    
    print()
    print("=" * 60)
    print("Analysis complete. Add more dreams to strengthen correlations.")
    print("=" * 60)

if __name__ == "__main__":
    main()
