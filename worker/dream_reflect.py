#!/usr/bin/env python3
"""
Dream Reflection Engine for Semantic Archaeology — Phase 2 Reflection.

Analyzes stored dreams and generates interpretive reflections on:
- Era transition patterns (where did the dream jump?)
- Semantic themes (what kinds of words clustered?)
- Archetypal resonances (what does this dream *mean*?)

Usage:
    python3 worker/dream_reflect.py [--dream-id ID] [--latest] [--all] [--store]
"""
import sys
import sqlite3
import argparse
import re
from pathlib import Path
from collections import Counter
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from phase1_config import DB_PATH, ERA_ORDER


# Archetypal resonance patterns — semantic fields that recur across eras
ARCHETYPES = {
    'religious': ['god', 'lord', 'prayer', 'soul', 'sin', 'grace', 'divine', 'holy', 'sacred', 'blessing', 'curse', 'damnation', 'salvation', 'faith', 'worship'],
    'power': ['king', 'lord', 'master', 'servant', 'slave', 'authority', 'command', 'obey', 'rule', 'throne', 'crown', 'subject', 'feudal', 'noble'],
    'domestic': ['home', 'house', 'family', 'mother', 'father', 'child', 'hearth', 'kitchen', 'bed', 'room', 'door', 'window', 'fire'],
    'natural': ['tree', 'river', 'mountain', 'sky', 'earth', 'water', 'fire', 'wind', 'stone', 'forest', 'sea', 'sun', 'moon', 'star'],
    'urban': ['street', 'crowd', 'city', 'building', 'room', 'shop', 'work', 'factory', 'machine', 'railway', 'carriage'],
    'bodily': ['hand', 'eye', 'heart', 'blood', 'flesh', 'bone', 'face', 'head', 'foot', 'voice', 'breath', 'touch'],
    'temporal': ['time', 'day', 'night', 'year', 'moment', 'hour', 'past', 'future', 'age', 'century', 'eternity'],
    'knowledge': ['book', 'write', 'read', 'learn', 'know', 'think', 'mind', 'wisdom', 'truth', 'false', 'understand'],
    'commerce': ['money', 'gold', 'silver', 'pay', 'buy', 'sell', 'trade', 'merchant', 'price', 'wealth', 'poor', 'rich'],
    'conflict': ['war', 'battle', 'fight', 'enemy', 'sword', 'death', 'kill', 'wound', 'struggle', 'defeat', 'victory'],
}

# Era characterizations for interpretation
ERA_CHARACTER = {
    'pre-1500': 'medieval, theological, feudal, oral residue',
    '1500-1700': 'Reformation, biblical, transitional, print culture emerging',
    '1700-1800': 'Enlightenment, rational, classical, nascent modernity',
    '1800-1850': 'Romantic, emotional, nature-focused, individual emerging',
    '1850-1900': 'Industrial, urban, realist, social, scientific',
    '1900-1923': 'Modernist, psychological, fragmented, stream-of-consciousness',
}


def extract_words_from_dream(dream_text: str) -> list:
    """Extract just the word sequence from dream text (skip headers and jump markers)."""
    lines = dream_text.split('\n')
    words = []
    for line in lines:
        line = line.strip()
        # Skip header lines
        if line.startswith('Seed:') or line.startswith('Temperature:') or line.startswith('─'):
            continue
        # Skip jump markers but note them
        if line.startswith('[') and '→' in line:
            continue
        # Extract words
        line_words = re.findall(r'\b[a-z]+\b', line.lower())
        words.extend(line_words)
    return words


def analyze_era_jumps(dream_text: str) -> list:
    """Extract era jump sequences from dream text."""
    jumps = re.findall(r'\[(.+?) → (.+?)\]', dream_text)
    return jumps


def score_archetypes(words: list) -> dict:
    """Score how strongly each archetype appears in the word list."""
    word_set = set(words)
    scores = {}
    for archetype, keywords in ARCHETYPES.items():
        matches = word_set.intersection(keywords)
        scores[archetype] = len(matches)
    return scores


def get_era_prevalence(dream_text: str) -> dict:
    """Count how many words fall into each era based on the dream text structure."""
    # This is approximate — the dream stores which era each word came from
    # We can infer from the jump markers
    lines = dream_text.split('\n')
    current_era = None
    era_counts = Counter()

    for line in lines:
        # Check for era jump marker
        jump_match = re.search(r'\[.+? → (.+?)\]', line)
        if jump_match:
            current_era = jump_match.group(1).strip()
            continue

        # Check for seed era in header
        if 'Start era:' in line:
            era_match = re.search(r'Start era:\s*(\S+)', line)
            if era_match:
                current_era = era_match.group(1)
            continue

        # Count words in current era section
        if current_era:
            words = re.findall(r'\b[a-z]+\b', line.lower())
            era_counts[current_era] += len(words)

    return dict(era_counts)


def interpret_dream(dream_row: sqlite3.Row) -> dict:
    """Generate an interpretation of a single dream."""
    dream_id = dream_row['id']
    seed = dream_row['seed_word']
    start_era = dream_row['start_era']
    temperature = dream_row['temperature']
    jump_count = dream_row['jump_count']
    dream_text = dream_row['dream_text']
    created_at = dream_row['created_at']

    # Extract and analyze
    words = extract_words_from_dream(dream_text)
    jumps = analyze_era_jumps(dream_text)
    archetype_scores = score_archetypes(words)
    era_prevalence = get_era_prevalence(dream_text)

    # Determine dominant archetypes
    sorted_archetypes = sorted(archetype_scores.items(), key=lambda x: x[1], reverse=True)
    primary_archetype = sorted_archetypes[0] if sorted_archetypes[0][1] > 0 else ('none', 0)
    secondary_archetype = sorted_archetypes[1] if len(sorted_archetypes) > 1 and sorted_archetypes[1][1] > 0 else None

    # Determine temporal character
    eras_visited = [start_era] + [jump[1] for jump in jumps] if jumps else [start_era]
    era_span = f"{eras_visited[0]} → {eras_visited[-1]}" if len(set(eras_visited)) > 1 else start_era

    # Build interpretation
    interpretation = {
        'dream_id': dream_id,
        'seed': seed,
        'start_era': start_era,
        'temperature': temperature,
        'jump_count': jump_count,
        'created_at': created_at,
        'word_count': len(words),
        'unique_words': len(set(words)),
        'eras_visited': list(set(eras_visited)),
        'era_span': era_span,
        'jumps': jumps,
        'primary_archetype': primary_archetype,
        'secondary_archetype': secondary_archetype,
        'archetype_scores': archetype_scores,
        'era_prevalence': era_prevalence,
    }

    return interpretation


def format_reflection(interpretation: dict) -> str:
    """Format an interpretation into a readable reflection."""
    lines = []
    lines.append(f"Dream #{interpretation['dream_id']} — Reflection")
    lines.append("=" * 50)
    lines.append(f"Seed: '{interpretation['seed']}' | Era: {interpretation['start_era']}")
    lines.append(f"Temperature: {interpretation['temperature']} | Jumps: {interpretation['jump_count']}")
    lines.append(f"Words: {interpretation['word_count']} total, {interpretation['unique_words']} unique")
    lines.append("")

    # Temporal journey
    lines.append("Temporal Journey:")
    if interpretation['jump_count'] == 0:
        lines.append(f"  The dream remained anchored in {interpretation['start_era']} —")
        lines.append(f"  {ERA_CHARACTER[interpretation['start_era']]}.")
    else:
        lines.append(f"  Started: {interpretation['start_era']} ({ERA_CHARACTER[interpretation['start_era']]})")
        for i, (from_era, to_era) in enumerate(interpretation['jumps'][:5], 1):
            lines.append(f"  Jump {i}: {from_era} → {to_era}")
        if len(interpretation['jumps']) > 5:
            lines.append(f"  ... and {len(interpretation['jumps']) - 5} more jumps")
    lines.append("")

    # Archetypal resonance
    lines.append("Archetypal Resonance:")
    pa_name, pa_score = interpretation['primary_archetype']
    if pa_score > 0:
        lines.append(f"  Primary: {pa_name.upper()} (score: {pa_score})")
        if interpretation['secondary_archetype']:
            sa_name, sa_score = interpretation['secondary_archetype']
            lines.append(f"  Secondary: {sa_name} (score: {sa_score})")

        # Interpretive gloss based on primary archetype
        gloss = {
            'religious': 'The dream moves through theological space — salvation, sin, grace, the divine.',
            'power': 'Hierarchies emerge: masters and servants, crowns and subjects, authority and obedience.',
            'domestic': 'Intimate spaces predominate — hearths, families, the quiet architecture of home.',
            'natural': 'The dream is grounded in elemental things: earth, water, sky, the ancient vocabulary of place.',
            'urban': 'Crowds, streets, buildings — the compressed energy of human congregation.',
            'bodily': 'Corporeal immediacy: hands that touch, eyes that see, blood, breath, flesh.',
            'temporal': 'Time itself becomes visible — days, years, the weight of ages, eternity.',
            'knowledge': 'Books, minds, understanding — the dream circulates through epistemic space.',
            'commerce': 'Exchange, value, wealth and poverty — the social mathematics of goods.',
            'conflict': 'Struggle, battle, death and victory — the dream moves through antagonism.',
        }.get(pa_name, 'The dream resists simple categorization.')
        lines.append(f"  → {gloss}")
    else:
        lines.append("  No strong archetypal resonance detected.")
    lines.append("")

    # Era prevalence
    if interpretation['era_prevalence']:
        lines.append("Era Distribution:")
        total_words = sum(interpretation['era_prevalence'].values())
        for era, count in sorted(interpretation['era_prevalence'].items(), key=lambda x: x[1], reverse=True):
            pct = (count / total_words * 100) if total_words > 0 else 0
            lines.append(f"  {era}: {count} words ({pct:.1f}%)")
    lines.append("")

    lines.append("—" * 50)
    return '\n'.join(lines)


def get_dreams(conn: sqlite3.Connection, dream_id=None, latest=False, limit=None):
    """Query dreams from database."""
    cursor = conn.cursor()
    cursor.row_factory = sqlite3.Row

    if dream_id:
        cursor.execute("SELECT * FROM dreams WHERE id = ?", (dream_id,))
        return cursor.fetchall()
    elif latest:
        cursor.execute("SELECT * FROM dreams ORDER BY created_at DESC LIMIT 1")
        return cursor.fetchall()
    elif limit:
        cursor.execute("SELECT * FROM dreams ORDER BY created_at DESC LIMIT ?", (limit,))
        return cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM dreams ORDER BY created_at DESC")
        return cursor.fetchall()


def ensure_reflections_table(conn: sqlite3.Connection):
    """Create reflections table if it doesn't exist."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dream_reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dream_id INTEGER NOT NULL,
            reflection_text TEXT NOT NULL,
            primary_archetype TEXT,
            secondary_archetype TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (dream_id) REFERENCES dreams(id)
        )
    """)
    conn.commit()


def store_reflection(conn: sqlite3.Connection, interpretation: dict, reflection_text: str):
    """Store a reflection in the database."""
    ensure_reflections_table(conn)
    cursor = conn.cursor()

    # Check if reflection already exists for this dream
    cursor.execute(
        "SELECT id FROM dream_reflections WHERE dream_id = ?",
        (interpretation['dream_id'],)
    )
    if cursor.fetchone():
        print(f"  ⚠️ Reflection already exists for dream {interpretation['dream_id']}, skipping")
        return None

    cursor.execute(
        """
        INSERT INTO dream_reflections
        (dream_id, reflection_text, primary_archetype, secondary_archetype)
        VALUES (?, ?, ?, ?)
        """,
        (
            interpretation['dream_id'],
            reflection_text,
            interpretation['primary_archetype'][0] if interpretation['primary_archetype'][1] > 0 else None,
            interpretation['secondary_archetype'][0] if interpretation['secondary_archetype'] else None,
        )
    )
    conn.commit()
    return cursor.lastrowid


def main():
    parser = argparse.ArgumentParser(description="Dream Reflection Engine")
    parser.add_argument("--dream-id", type=int, help="Reflect on specific dream ID")
    parser.add_argument("--latest", action="store_true", help="Reflect on most recent dream")
    parser.add_argument("--all", action="store_true", help="Reflect on all dreams")
    parser.add_argument("--limit", type=int, help="Reflect on N most recent dreams")
    parser.add_argument("--store", action="store_true", help="Store reflections in database")
    parser.add_argument("--db", help="Override database path")
    args = parser.parse_args()

    db_path = Path(args.db) if args.db else DB_PATH
    conn = sqlite3.connect(str(db_path))

    # Get dreams to reflect on
    if args.dream_id:
        dreams = get_dreams(conn, dream_id=args.dream_id)
    elif args.latest:
        dreams = get_dreams(conn, latest=True)
    elif args.limit:
        dreams = get_dreams(conn, limit=args.limit)
    elif args.all:
        dreams = get_dreams(conn)
    else:
        # Default: latest
        dreams = get_dreams(conn, latest=True)

    if not dreams:
        print("No dreams found in database.")
        conn.close()
        return

    print(f"Reflecting on {len(dreams)} dream(s)...\n")

    for dream_row in dreams:
        interpretation = interpret_dream(dream_row)
        reflection = format_reflection(interpretation)
        print(reflection)

        if args.store:
            reflection_id = store_reflection(conn, interpretation, reflection)
            print(f"💾 Reflection stored with id={reflection_id}")
            print()

    conn.close()


if __name__ == "__main__":
    main()
