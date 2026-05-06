# Phase 1 Design: Full-Scale Semantic Archaeology

**Status:** Building tonight, running tomorrow

## Scope

| Parameter | Phase 0 | Phase 1 |
|-----------|---------|---------|
| Books | 20 | 100+ |
| Eras | 3 | 5-6 |
| Vocab | 2,000 | 5,000-10,000 |
| Vector dims | 50 | 100 |
| Context window | 5 | 7-10 |

## Eras (tentative)

1. **pre-1500** - Medieval/Classical (Ancients, Aquinas, Chaucer)
2. **1500-1700** - Renaissance/Early Modern (Shakespeare, Milton, Hobbes)
3. **1700-1800** - Enlightenment (Voltaire, Rousseau, Smith)
4. **1800-1850** - Romantic/Early Victorian (Austen, early Dickens)
5. **1850-1900** - Victorian/Industrial (Full Phase 0 corpus)
6. **1900-1923** - Modernist (Woolf, Kafka, Joyce - public domain)

## Architecture Changes

### 1. Streaming Tokenizer
- Don't load entire texts into memory
- Generator-based token streaming
- Line-by-line processing for large files

### 2. Incremental Vocabulary Build
- Two-pass system:
  - Pass 1: count frequencies across all texts
  - Pass 2: build final vocab with min_freq threshold
- SQLite staging table for frequency counts

### 3. Sparse Matrix Optimization
- Use scipy.sparse throughout
- Never densify
- Incremental co-occurrence building

### 4. Era-Aware Processing
- Each era processed independently
- Cross-era comparison functions
- Drift detection algorithms

## New Features

### Semantic Drift Detection
- Track word vector movement across eras
- Calculate "velocity" of semantic change
- Identify "fast movers" (words changing meaning rapidly)

### Query Enhancements
- Analogies: "man is to king as woman is to ?"
- Era interpolation: "what would 'computer' mean in 1800?"
- Drift queries: "show me words that changed most between 1700 and 1900"

### Visualization Prep
- Export vectors for PCA/t-SNE visualization
- Generate drift charts
- Word trajectory exports

## Implementation Plan

1. **Expand catalog** - research 100+ books across 6 eras
2. **Streaming pipeline** - rewrite tokenizer for memory efficiency
3. **Incremental vocab** - two-pass frequency counting
4. **Optimized cooc** - sparse-only, batched inserts
5. **Drift detection** - vector comparison algorithms
6. **Query enhancements** - analogy solving, interpolation

## Success Metrics

- ✅ Process 100+ books without OOM
- ✅ Build 10k vocab in <2 hours
- ✅ Generate vectors for all eras
- ✅ Identify 20+ "fast mover" words
- ✅ Analogy solving >60% accuracy on test set

## Risks

| Risk | Mitigation |
|------|------------|
| OOM on large texts | Streaming tokenizer, never full load |
| DB too large | Separate DBs per era, archive old |
| Gutenberg rate limits | 1s delay, retry logic, caching |
| Processing too slow | Parallel era processing, batch inserts |
