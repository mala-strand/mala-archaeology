#!/usr/bin/env python3
"""
Phase 1 book downloader.
Downloads remaining books for Phase 1 catalog.
Runs with Gutenberg delay to respect rate limits.
"""
import sys
import time
import sqlite3
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

sys.path.insert(0, str(Path(__file__).parent / "worker"))
from phase1_config import DATA_DIR, DB_PATH, GUTENBERG_DELAY, GUTENBERG_RETRY

def download_book(gutenberg_id, retries=GUTENBERG_RETRY):
    """Download a single book from Project Gutenberg."""
    url = f"https://www.gutenberg.org/cache/epub/{gutenberg_id}/pg{gutenberg_id}.txt"
    
    for attempt in range(retries):
        try:
            req = Request(url, headers={'User-Agent': 'MalaArchaeology/1.0'})
            with urlopen(req, timeout=30) as response:
                text = response.read().decode('utf-8', errors='ignore')
            
            out_path = DATA_DIR / f"{gutenberg_id}.txt"
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            return True, len(text)
        except HTTPError as e:
            if e.code == 404:
                # Try alternate URL format
                alt_url = f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}-0.txt"
                try:
                    req = Request(alt_url, headers={'User-Agent': 'MalaArchaeology/1.0'})
                    with urlopen(req, timeout=30) as response:
                        text = response.read().decode('utf-8', errors='ignore')
                    
                    out_path = DATA_DIR / f"{gutenberg_id}.txt"
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                    
                    return True, len(text)
                except:
                    pass
            return False, str(e)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(GUTENBERG_DELAY * 2)
                continue
            return False, str(e)
    
    return False, "Max retries exceeded"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get books that need downloading
    cursor.execute("""
        SELECT gutenberg_id, title, author FROM texts 
        WHERE status = 'pending'
        ORDER BY era, gutenberg_id
    """)
    pending = cursor.fetchall()
    
    if not pending:
        print("No books pending download.")
        return
    
    print(f"Downloading {len(pending)} books to {DATA_DIR}...")
    
    downloaded = 0
    failed = 0
    total_bytes = 0
    
    for i, (gid, title, author) in enumerate(pending, 1):
        out_path = DATA_DIR / f"{gid}.txt"
        if out_path.exists():
            cursor.execute("UPDATE texts SET status = 'complete' WHERE gutenberg_id = ?", (gid,))
            conn.commit()
            downloaded += 1
            print(f"  [{i}/{len(pending)}] Already exists: {title}")
            continue
        
        print(f"  [{i}/{len(pending)}] Downloading {title} ({gid})...", end=" ", flush=True)
        
        success, result = download_book(gid)
        
        if success:
            cursor.execute("UPDATE texts SET status = 'complete' WHERE gutenberg_id = ?", (gid,))
            conn.commit()
            downloaded += 1
            total_bytes += result
            print(f"OK ({result/1024:.0f}KB)")
        else:
            cursor.execute("UPDATE texts SET status = 'failed' WHERE gutenberg_id = ?", (gid,))
            conn.commit()
            failed += 1
            print(f"FAILED: {result}")
        
        time.sleep(GUTENBERG_DELAY)
    
    conn.close()
    print(f"\nDone: {downloaded} downloaded, {failed} failed, {total_bytes/1024/1024:.1f}MB total")

if __name__ == "__main__":
    main()
