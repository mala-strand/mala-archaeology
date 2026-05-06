-- Archaeology Pilot DB Schema (Phase 0)
-- Small scale: 20 books, 2k vocab, sparse matrices

-- Corpus metadata
CREATE TABLE IF NOT EXISTS texts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gutenberg_id INTEGER UNIQUE NOT NULL,
    title TEXT,
    author TEXT,
    year INTEGER,
    era TEXT,
    word_count INTEGER,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'downloading', 'processing', 'complete', 'failed'))
);

-- Vocabulary (top N words by frequency)
CREATE TABLE IF NOT EXISTS vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT UNIQUE NOT NULL,
    frequency INTEGER DEFAULT 0,
    is_stopword BOOLEAN DEFAULT 0
);

-- Sparse co-occurrence storage (only top pairs per word to save space)
CREATE TABLE IF NOT EXISTS cooccurrences (
    word_a TEXT NOT NULL,
    word_b TEXT NOT NULL,
    era TEXT NOT NULL,
    count INTEGER DEFAULT 0,
    ppmi REAL,
    PRIMARY KEY (word_a, word_b, era)
);

-- Word vectors (post-SVD, stored as JSON for flexibility)
CREATE TABLE IF NOT EXISTS word_vectors (
    word TEXT NOT NULL,
    era TEXT NOT NULL,
    vector_json TEXT NOT NULL,  -- JSON array of floats
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (word, era)
);

-- Worker state for checkpoint/resume
CREATE TABLE IF NOT EXISTS worker_state (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Control file simulation (pause/stop signals)
CREATE TABLE IF NOT EXISTS control (
    signal TEXT PRIMARY KEY CHECK (signal IN ('run', 'pause', 'stop')),
    set_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT OR IGNORE INTO control (signal) VALUES ('run');

-- Pilot era focus: 1850-1900
CREATE INDEX IF NOT EXISTS idx_texts_era ON texts(era);
CREATE INDEX IF NOT EXISTS idx_cooccurrences_era ON cooccurrences(era);
CREATE INDEX IF NOT EXISTS idx_cooccurrences_word_a ON cooccurrences(word_a);
