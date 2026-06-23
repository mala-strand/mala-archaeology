"""
Archaeology Pilot Config (Phase 0)
Box-aware constraints for 2-core, 3.8GB RAM machine
"""
from pathlib import Path

# Base workspace
WORKSPACE = Path("/mnt/nas/mala/work/archaeology")

# Pilot scope - deliberately small to prove pipeline
PILOT_BOOKS = 20
PILOT_ERA = "1850-1900"
VOCAB_SIZE = 2000
CONTEXT_WINDOW = 5  # words before/after target
MIN_WORD_FREQ = 5   # ignore words appearing fewer than N times

# Memory constraints
MAX_MATRIX_SIZE = 2000 * 2000  # vocab x vocab
SPARSE_DENSITY_TARGET = 0.01   # aim for <1% density

# Processing
BATCH_SIZE = 1000  # words to process before checkpoint
CHECKPOINT_INTERVAL = 60  # seconds between state saves

# Gutenberg catalog
GUTENBERG_CATALOG_URL = "https://www.gutenberg.org/ebooks/offline_catalogs/catalog.rdf.gz"
GUTENBERG_TEXT_BASE = "https://www.gutenberg.org/files"

# File paths (absolute)
DATA_DIR = WORKSPACE / "data"
DB_PATH = WORKSPACE / "data" / "archaeology.db"
CONTROL_FILE = WORKSPACE / "data" / "control"

# Load gating (conservative for small box)
LOAD_THRESHOLD = 1.0  # 1-min loadavg must be below this
MEM_FLOOR = 0.20      # at least 20% memory free
