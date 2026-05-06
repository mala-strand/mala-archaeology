"""
Phase 1 Configuration
Full-scale semantic archaeology
"""
from pathlib import Path

WORKSPACE = Path("/home/mala/.openclaw/workspace/archaeology")

# Phase 1 scope
PHASE1_BOOKS = 100
PHASE1_ERAS = ["pre-1500", "1500-1700", "1700-1800", "1800-1850", "1850-1900", "1900-1923"]
VOCAB_SIZE = 8000  # Target vocabulary size
CONTEXT_WINDOW = 7  # Larger context for richer semantics
MIN_WORD_FREQ = 10  # Higher threshold for cleaner vocab
VECTOR_DIMS = 100  # Deeper embeddings

# Memory constraints (still box-aware)
MAX_TOKENS_IN_MEMORY = 100000  # Streaming buffer size
BATCH_SIZE = 5000  # Co-occurrence batch inserts
CHECKPOINT_INTERVAL = 120  # Seconds between checkpoints

# File paths
DATA_DIR = WORKSPACE / "data" / "phase1"
DB_PATH = DATA_DIR / "archaeology_phase1.db"
CACHE_DIR = WORKSPACE / "cache"

# Processing
PARALLEL_ERAS = True  # Process eras in parallel where possible
USE_STREAMING = True  # Never load full texts

# Gutenberg
GUTENBERG_DELAY = 1.0  # Seconds between requests
GUTENBERG_RETRY = 3  # Retry attempts

# Drift detection
DRIFT_TOP_K = 50  # Track top K most changed words
DRIFT_METRIC = "cosine"  # Distance metric for drift
