#!/usr/bin/env python3
"""
Simple Gutenberg downloader for Phase 0 pilot.
Fetches texts from Project Gutenberg's mirror.
"""

import sqlite3
import requests
import zipfile
import io
import re
import time
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))

from pilot_config import (
    DB_PATH, PILOT_BOOKS, PILOT_ERA, DATA_DIR,
    CHECKPOINT_INTERVAL
)

# 20 curated books from 1850-1900 (Phase 0 pilot)
# Mix of fiction and philosophy for rich semantic drift potential
PILOT_CATALOG = [
    # 1850s
    (1400, "Great Expectations", "Charles Dickens", 1861),
    (74, "The Adventures of Tom Sawyer", "Mark Twain", 1876),
    (11, "Alice's Adventures in Wonderland", "Lewis Carroll", 1865),
    (98, "A Tale of Two Cities", "Charles Dickens", 1859),
    (84, "Frankenstein", "Mary Shelley", 1851),  # later edition
    # 1860s-1870s
    (219, "Heart of Darkness", "Joseph Conrad", 1899),
    (1260, "Jane Eyre", "Charlotte Brontë", 1850),  # later edition
    (768, "Wuthering Heights", "Emily Brontë", 1850),  # later edition
    (145, "Middlemarch", "George Eliot", 1871),
    (541, "The Age of Innocence", "Edith Wharton", 1899),
    # Philosophy/Political
    (61, "The Communist Manifesto", "Karl Marx", 1848),  # just pre-era but influential
    (3207, "Leviathan", "Thomas Hobbes", 1651),  # baseline old
    (3300, "The Republic", "Plato", -375),  # ancient baseline
    # More fiction
    (1342, "Pride and Prejudice", "Jane Austen", 1813),  # pre-era comparison
    (158, "Emma", "Jane Austen", 1815),
    (161, "Sense and Sensibility", "Jane Austen", 1811),
    (105, "Persuasion", "Jane Austen", 1818),
    (121, "Northanger Abbey", "Jane Austen", 1817),
    # Later 1800s
    (2600, "War and Peace", "Leo Tolstoy", 1869),
    (1399, "Anna Karenina", "Leo Tolstoy", 1878),
]


def init_db():
    """Initialize SQLite database with schema."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    with open(Path(__file__).parent.parent / "data" / "schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


def populate_catalog():
    """Insert pilot catalog into database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for gutenberg_id, title, author, year in PILOT_CATALOG[:PILOT_BOOKS]:
        # Determine era
        if year < 1800:
            era = "pre-1800"
        elif year < 1850:
            era = "1800-1850"
        elif year < 1900:
            era = "1850-1900"
        else:
            era = "1900-1950"
        
        cursor.execute("""
            INSERT OR IGNORE INTO texts (gutenberg_id, title, author, year, era)
            VALUES (?, ?, ?, ?, ?)
        """, (gutenberg_id, title, author, year, era))
    
    conn.commit()
    conn.close()
    print(f"Populated {PILOT_BOOKS} books in catalog")


def download_text(gutenberg_id: int) -> str:
    """
    Download a text from Project Gutenberg.
    Tries multiple formats: plain text UTF-8, plain text ASCII, zip.
    """
    base_url = f"https://www.gutenberg.org/files/{gutenberg_id}"
    
    # Try UTF-8 plain text
    urls = [
        f"{base_url}/{gutenberg_id}-0.txt",
        f"{base_url}/{gutenberg_id}.txt",
        f"{base_url}/{gutenberg_id}-8.txt",  # UTF-8 variant
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"  Failed {url}: {e}")
            continue
    
    # Try zip file
    zip_url = f"{base_url}/{gutenberg_id}.zip"
    try:
        response = requests.get(zip_url, timeout=30)
        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                # Find the text file inside
                for name in z.namelist():
                    if name.endswith('.txt'):
                        return z.read(name).decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"  Failed zip {zip_url}: {e}")
    
    raise Exception(f"Could not download text {gutenberg_id}")


def clean_gutenberg_text(text: str) -> str:
    """
    Remove Gutenberg boilerplate and normalize text.
    """
    # Find start marker
    start_markers = [
        "*** START OF",
        "***START OF",
        "*END*THE SMALL PRINT!",
    ]
    
    end_markers = [
        "*** END OF",
        "***END OF",
        "End of Project Gutenberg",
    ]
    
    # Find content boundaries
    start_idx = 0
    for marker in start_markers:
        idx = text.find(marker)
        if idx != -1:
            # Find newline after marker
            nl_idx = text.find('\n', idx)
            if nl_idx != -1:
                start_idx = nl_idx + 1
                break
    
    end_idx = len(text)
    for marker in end_markers:
        idx = text.find(marker)
        if idx != -1:
            end_idx = idx
            break
    
    content = text[start_idx:end_idx]
    
    # Normalize whitespace
    content = re.sub(r'\s+', ' ', content)
    content = content.strip()
    
    return content


def download_all():
    """Download all pending texts."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, gutenberg_id, title, author, year 
        FROM texts 
        WHERE status = 'pending'
        LIMIT ?
    """, (PILOT_BOOKS,))
    
    pending = cursor.fetchall()
    print(f"Found {len(pending)} pending texts to download")
    
    for text_id, gutenberg_id, title, author, year in pending:
        print(f"Downloading: {title} ({year}) [ID: {gutenberg_id}]")
        
        try:
            cursor.execute(
                "UPDATE texts SET status = 'downloading' WHERE id = ?",
                (text_id,)
            )
            conn.commit()
            
            raw_text = download_text(gutenberg_id)
            clean_text = clean_gutenberg_text(raw_text)
            word_count = len(clean_text.split())
            
            # Save to file
            text_path = Path(DATA_DIR) / f"{gutenberg_id}.txt"
            text_path.write_text(clean_text, encoding='utf-8')
            
            cursor.execute("""
                UPDATE texts 
                SET status = 'complete', word_count = ?, processed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (word_count, text_id))
            conn.commit()
            
            print(f"  ✓ Downloaded {word_count} words")
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            cursor.execute(
                "UPDATE texts SET status = 'failed' WHERE id = ?",
                (text_id,)
            )
            conn.commit()
        
        time.sleep(1)  # Be nice to Gutenberg servers
    
    conn.close()
    print("Download complete")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2 or sys.argv[1] == "init":
        init_db()
        populate_catalog()
    elif sys.argv[1] == "download":
        download_all()
    else:
        print("Usage: python downloader.py [init|download]")
