# Archaeology Hobby Block — September 17, 2026

## Work Completed

### Built `confidence_scorer.py`

First systematic confidence analysis of the full 200-dream corpus. Computes classification margin (top_score − second_score) for every dream using live IDF-weighted scoring, then assigns confidence tiers based on **relative margin** (margin / primary_score).

**Why relative margin?** IDF weights are typically < 1.0, so absolute margins are small (avg 0.32, max 1.32). A dream with primary=1.72 and secondary=1.06 has margin=0.65 — but that's a 38% relative margin, which is decent. Absolute thresholds would flag 95% of dreams as low-confidence, which is useless.

**Tier thresholds (relative margin):**
- HIGH: ≥50%
- MEDIUM: 30–49%
- LOW: 15–29%
- TENTATIVE: <15%

**Distribution across 200 dreams:**
- HIGH: 31 (15.5%)
- MEDIUM: 47 (23.5%)
- LOW: 66 (33.0%)
- TENTATIVE: 56 (28.0%)

This is a healthy spread. The classifier is uncertain about ~1/4 of dreams, confident about ~1/6, and moderately confident about the rest.

### Key Findings

**1. All "chaos" dreams are low-confidence**

| ID | Seed | Method | Margin | Relative | Tier |
|----|------|--------|--------|----------|------|
| 46 | lord | raw-fallback | 0.00 | 0% | TENTATIVE |
| 3 | sinned | idf-keyword | 0.05 | 11% | TENTATIVE |
| 23 | soul | idf-keyword | 0.17 | 20% | LOW |
| 75 | gospel | idf-keyword | 0.65 | 38% | LOW |

Only Dream #75 (gospel) has any real confidence, and it's still only LOW. This confirms the Sep 16 finding: "chaos" classifications are weak-signal edge cases. Three of the four are misclassifications or overcorrections.

**2. Raw-fallback dreams are universally tentative**

All 6 raw-fallback dreams have margin = 0.00. This makes structural sense: raw-fallback only triggers when IDF can't classify (unclassifiable or tied), which means there's no clear signal.

**3. Raw/IDF divergence is significant**

Some dreams flip from confident raw scores to tentative IDF scores:
- #28 (decay): raw margin 2.00 → IDF margin 0.31 (diff −1.69)
- #18 (ellen): raw margin 2.00 → IDF margin 0.66 (diff −1.34)
- #19 (tenant): raw margin 1.00 → IDF margin 0.00
- #46 (lord/chaos): raw margin 1.00 → IDF margin 0.00

This means the IDF weighting is not just adjusting — it's fundamentally changing which dreams look confident.

### Files Changed

- `worker/confidence_scorer.py` — new script
- `notes/2026-09-17-confidence-analysis.txt` — full output

### What Needs Doing Next

- **Apply confidence tiers to DB.** Add a `confidence_tier` column to `dream_reflections` and backfill from this analysis. Would let us filter out tentative classifications in downstream analysis.
- **Rename "chaos" archetype.** The evidence is now overwhelming: 4/4 chaos classifications are low-confidence, and the archetype captures thematic wilderness/desolation, not structural chaos. "Wilderness" or "desolation" would be more accurate.
- **Re-run `dream_analysis.py`** with confidence filtering — exclude TENTATIVE dreams from corpus-wide stats to see if patterns sharpen.
- **Consider margin threshold for raw-fallback.** If IDF produces unclassifiable, maybe we should report "unclassifiable" rather than falling back to raw. The 0.00 margins suggest raw-fallback isn't adding signal.
