#!/bin/bash
# Archaeology Phase 0 Pilot Runner
# Downloads texts, builds vocab, creates co-occurrence matrix, builds vectors

set -e

cd "$(dirname "$0")"

echo "================================"
echo "Archaeology Pilot (Phase 0)"
echo "================================"
echo ""

# Check dependencies
echo "Checking dependencies..."
python3 -c "import numpy, scipy, sklearn" 2>/dev/null || {
    echo "Installing dependencies..."
    pip3 install numpy scipy scikit-learn requests --user
}

# Initialize
echo ""
echo "Step 1: Initialize database"
python3 worker/downloader.py init

# Download (test with 3 books first for quick validation)
echo ""
echo "Step 2: Download texts (first 3 for quick test)"
python3 worker/downloader.py download

# Check if we got any downloads
if [ ! -f data/1400.txt ]; then
    echo "ERROR: No texts downloaded. Check connection to Project Gutenberg."
    exit 1
fi

# Build vocabulary
echo ""
echo "Step 3: Build vocabulary"
python3 worker/tokenizer.py

# Build co-occurrence
echo ""
echo "Step 4: Build co-occurrence matrix"
python3 worker/cooccurrence.py cooc

# Build vectors
echo ""
echo "Step 5: Build word vectors (SVD)"
python3 worker/cooccurrence.py vectors

# Test query
echo ""
echo "Step 6: Test query"
echo ""
python3 queries/query.py << 'EOF'
neighbors love 1850-1900 5
quit
EOF

echo ""
echo "================================"
echo "Pilot complete!"
echo "Run: python3 queries/query.py"
echo "================================"
