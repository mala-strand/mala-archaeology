#!/usr/bin/env python3
"""
Dream-Archetype-Drift Analyzer
Queries correlations between semantic drift and dream archetypes.
"""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "archaeology_phase1_clean.db"

ARCHETYPE_KEYWORDS = {
    "RELIGIOUS": ["god", "soul", "pray", "sin", "grace", "church", "temple", "worship", "divine", "holy"],
    "POWER": ["lord", "master", "king", "obey", "command", "authority", "rule", "subject", "crown", "throne"],
    "BODILY": ["touch", "eye", "hand", "blood", "flesh", "breath", "grasp", "feel", "body", "skin"],
    "DOMESTIC": ["home", "family", "hearth", "house", "domestic", "intimate", "quiet", "familiar"],
    "CONFLICT": ["battle", "fight", "war", "struggle", "enemy", "weapon", "combat", "defeat"],
    "KNOWLEDGE": ["learn", "know", "wisdom", "understand", "truth", "philosophy", "science"],
    "CHAOS": ["wild", "storm", "tumult", "disorder", "confusion", "fragment", "uncontrolled"],
    "TEMPORAL": ["time", "past", "future", "age", "era", "century", "ancient", "modern"],
    "URBAN": ["city", "street", "crowd", "crowded", "urban", "town", "population"],
    "NATURAL": ["earth", "nature", "forest", "river", "mountain", "wild", "organic"],
    "LEGACY": ["fame", "immortal", "memory", "remember", "name", "reputation", "endure"],
    "CRAFT": ["make", "create", "write", "author", "artist", "work", "craft", "skill"],
    "IDENTITY": ["self", "who", "i", "me", "person", "character", "individual"],
}


def get_db():
    return sqlite3.connect(DB_PATH)


def list_by_archetype(archetype=None):
    """List dreams filtered by archetype."""
    conn = get_db()
    cursor = conn.cursor()
    
    if archetype:
        cursor.execute("""
            SELECT d.id, d.seed_word, d.start_era, d.temperature, d.jump_count,
                   dr.primary_archetype, dr.secondary_archetype
            FROM dreams d
            JOIN dream_reflections dr ON d.id = dr.dream_id
            WHERE dr.primary_archetype = ? OR dr.secondary_archetype = ?
            ORDER BY d.id DESC
        """, (archetype.lower(), archetype.lower()))
    else:
        cursor.execute("""
            SELECT d.id, d.seed_word, d.start_era, d.temperature, d.jump_count,
                   dr.primary_archetype, dr.secondary_archetype
            FROM dreams d
            JOIN dream_reflections dr ON d.id = dr.dream_id
            ORDER BY d.id DESC
        """)
    
    rows = cursor.fetchall()
    conn.close()
    
    print(f"\n{'ID':>4} | {'Seed Word':<12} | {'Era':<12} | {'Temp':>4} | {'Jumps':>5} | {'Primary':<10} | {'Secondary':<10}")
    print("-" * 80)
    for row in rows:
        print(f"{row[0]:>4} | {row[1]:<12} | {row[2]:<12} | {row[3]:>4.1f} | {row[4]:>5} | {row[5] or '—':<10} | {row[6] or '—':<10}")
    print(f"\nTotal: {len(rows)} dreams")


def archetype_distribution():
    """Show distribution of archetypes across all dreams."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT primary_archetype, COUNT(*) as count
        FROM dream_reflections
        WHERE primary_archetype IS NOT NULL
        GROUP BY primary_archetype
        ORDER BY count DESC
    """)
    
    primary = cursor.fetchall()
    
    cursor.execute("""
        SELECT secondary_archetype, COUNT(*) as count
        FROM dream_reflections
        WHERE secondary_archetype IS NOT NULL
        GROUP BY secondary_archetype
        ORDER BY count DESC
    """)
    
    secondary = cursor.fetchall()
    conn.close()
    
    print("\n=== Primary Archetype Distribution ===")
    for archetype, count in primary:
        bar = "█" * count
        print(f"{archetype or 'uncategorized':<12} | {count:>3} | {bar}")
    
    print("\n=== Secondary Archetype Distribution ===")
    for archetype, count in secondary:
        bar = "█" * count
        print(f"{archetype or 'none':<12} | {count:>3} | {bar}")


def drift_for_word(word):
    """Show drift scores for a specific word across all era transitions."""
    conn = get_db()
    cursor = conn.cursor()
    
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
                WHEN '1900-1923' THEN 6
            END
    """, (word,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print(f"\nNo drift data for '{word}'")
        return
    
    print(f"\n=== Drift Scores for '{word}' ===")
    print(f"{'Era Transition':<30} | {'Drift':>6} | {'Bar'}")
    print("-" * 55)
    for era_from, era_to, drift in rows:
        bar = "▓" * int(drift * 20)
        print(f"{era_from} → {era_to:<12} | {drift:>6.3f} | {bar}")


def dream_drift_correlation():
    """Analyze correlation between dream jumps and word drift."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT d.id, d.seed_word, d.start_era, d.jump_count, d.temperature,
               dr.primary_archetype,
               AVG(ds.drift_score) as avg_drift,
               MAX(ds.drift_score) as max_drift
        FROM dreams d
        JOIN dream_reflections dr ON d.id = dr.dream_id
        LEFT JOIN drift_scores ds ON d.seed_word = ds.word
        GROUP BY d.id
        ORDER BY d.id DESC
        LIMIT 20
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    print(f"\n{'ID':>4} | {'Word':<12} | {'Jumps':>5} | {'Temp':>4} | {'Avg Drift':>9} | {'Max Drift':>9} | {'Archetype':<10}")
    print("-" * 90)
    for row in rows:
        avg_drift = row[6] if row[6] else 0
        max_drift = row[7] if row[7] else 0
        print(f"{row[0]:>4} | {row[1]:<12} | {row[3]:>5} | {row[4]:>4.1f} | {avg_drift:>9.3f} | {max_drift:>9.3f} | {row[5] or '—':<10}")


def temperature_analysis():
    """Analyze temperature vs jump count correlation."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT temperature, AVG(jump_count) as avg_jumps, COUNT(*) as count
        FROM dreams
        GROUP BY temperature
        ORDER BY temperature
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    print("\n=== Temperature vs Average Jumps ===")
    print(f"{'Temp':>5} | {'Avg Jumps':>10} | {'Count':>5} | {'Visualization'}")
    print("-" * 60)
    for temp, avg_jumps, count in rows:
        bar = "●" * int(avg_jumps)
        print(f"{temp:>5.1f} | {avg_jumps:>10.1f} | {count:>5} | {bar}")


def search_dreams(query):
    """Search dream texts for specific words."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT d.id, d.seed_word, dr.primary_archetype, d.dream_text
        FROM dreams d
        JOIN dream_reflections dr ON d.id = dr.dream_id
        WHERE d.dream_text LIKE ?
        ORDER BY d.id DESC
    """, (f"%{query}%",))
    
    rows = cursor.fetchall()
    conn.close()
    
    print(f"\n=== Dreams containing '{query}' ===")
    for row in rows:
        print(f"\nDream #{row[0]} (seed: {row[1]}, archetype: {row[2] or 'uncategorized'})")
        # Show context around the match
        text = row[3]
        idx = text.lower().find(query.lower())
        if idx >= 0:
            start = max(0, idx - 60)
            end = min(len(text), idx + len(query) + 60)
            context = text[start:end]
            print(f"  ...{context}...")


def main():
    if len(sys.argv) < 2:
        print("""
Dream-Archetype-Drift Analyzer

Usage:
  python3 dream_analyzer.py list [ARCHETYPE]     - List dreams, optionally filter by archetype
  python3 dream_analyzer.py distribution         - Show archetype distribution
  python3 dream_analyzer.py drift WORD           - Show drift scores for a word
  python3 dream_analyzer.py correlation          - Show dream-drift correlation
  python3 dream_analyzer.py temperature          - Show temperature vs jumps analysis
  python3 dream_analyzer.py search QUERY         - Search dream texts

Archetypes: RELIGIOUS, POWER, BODILY, DOMESTIC, CONFLICT, KNOWLEDGE, 
            CHAOS, TEMPORAL, URBAN, NATURAL, LEGACY, CRAFT, IDENTITY
        """)
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "list":
        archetype = sys.argv[2] if len(sys.argv) > 2 else None
        list_by_archetype(archetype)
    elif command == "distribution":
        archetype_distribution()
    elif command == "drift":
        if len(sys.argv) < 3:
            print("Usage: python3 dream_analyzer.py drift WORD")
            sys.exit(1)
        drift_for_word(sys.argv[2])
    elif command == "correlation":
        dream_drift_correlation()
    elif command == "temperature":
        temperature_analysis()
    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: python3 dream_analyzer.py search QUERY")
            sys.exit(1)
        search_dreams(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
