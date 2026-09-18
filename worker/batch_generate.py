#!/usr/bin/env python3
"""
Batch dream generator.
Generates N dreams with varied parameters and stores them.
"""

import sys
import random
import sqlite3
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from dream import generate_dream, ensure_dreams_table
from phase1_config import DB_PATH, ERA_ORDER


def batch_generate(count=10, length=300):
    conn = sqlite3.connect(str(DB_PATH))
    ensure_dreams_table(conn)

    # Need a seed pool — get vocabulary from DB
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT word FROM word_vectors")
    vocab = [row[0] for row in cursor.fetchall()]
    print(f"Vocab size: {len(vocab)}")

    generated = 0
    for i in range(count):
        seed = random.choice(vocab) if random.random() > 0.3 else None
        era = random.choice(ERA_ORDER)
        temp = round(random.uniform(0.8, 2.0), 2)
        jump_prob = round(random.uniform(0.02, 0.12), 3)
        actual_length = length + random.randint(-50, 100)

        dream_text, unique_count, jump_count = generate_dream(
            conn,
            seed=seed,
            start_era=era,
            length=actual_length,
            temperature=temp,
            era_jump_prob=jump_prob,
            decay=0.7,
            store=True,
        )
        generated += 1

    conn.close()
    print(f"\nGenerated {generated} dreams")
    return generated


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--length", type=int, default=300)
    args = parser.parse_args()
    batch_generate(args.count, args.length)
