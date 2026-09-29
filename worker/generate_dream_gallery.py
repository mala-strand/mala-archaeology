#!/usr/bin/env python3
"""Generate a static, filterable dream gallery page from the archaeology DB."""

import sqlite3
import html
import os

DB_PATH = "/mnt/nas/mala/work/archaeology/data/archaeology_phase1_clean.db"
OUTPUT_PATH = "/mnt/nas/mala/work/archaeology/site/dreams.html"


def parse_dream_text(raw):
    """Strip header and format jump markers."""
    lines = raw.strip().split("\n")
    # Skip header lines until we hit the separator
    content_lines = []
    in_content = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("─"):
            in_content = True
            continue
        if in_content:
            content_lines.append(stripped)
    return "\n".join(content_lines)


def format_dream_html(text):
    """Convert dream text to HTML with styled jump markers."""
    lines = text.strip().split("\n")
    parts = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("[") and "→" in stripped:
            parts.append(f'<br><span class="jump">{html.escape(stripped)}</span><br>')
        else:
            parts.append(html.escape(stripped))
    return " ".join(parts)


def badge_color(archetype):
    """Deterministic pastel-ish color per archetype for visual distinction."""
    # Hash archetype name to hue
    h = hash(archetype) % 360
    return f"hsl({h}, 55%, 65%)"


def generate():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT
            d.id,
            d.seed_word,
            d.start_era,
            d.temperature,
            d.era_jump_prob,
            d.jump_count,
            d.unique_words,
            d.dream_text,
            r.idf_hybrid_primary AS archetype,
            r.confidence_tier,
            r.confidence_margin,
            r.confidence_relative
        FROM dreams d
        JOIN dream_reflections r ON d.id = r.dream_id
        WHERE r.idf_hybrid_primary IS NOT NULL
        ORDER BY d.id
    """)
    rows = cur.fetchall()

    # Aggregate stats
    archetype_counts = {}
    confidence_counts = {}
    for r in rows:
        archetype_counts[r["archetype"]] = archetype_counts.get(r["archetype"], 0) + 1
        confidence_counts[r["confidence_tier"]] = confidence_counts.get(r["confidence_tier"], 0) + 1

    # Sort archetypes by count desc
    sorted_archetypes = sorted(archetype_counts.items(), key=lambda x: -x[1])

    dream_cards = []
    for r in rows:
        text = parse_dream_text(r["dream_text"])
        html_text = format_dream_html(text)
        archetype = r["archetype"] or "unclassifiable"
        confidence = r["confidence_tier"] or "UNKNOWN"
        margin = r["confidence_margin"] or 0.0
        relative = r["confidence_relative"] or 0.0
        badge_style = badge_color(archetype)
        # Extract RGB-like for CSS — just use the hue
        badge_hue = hash(archetype) % 360
        badge_css = f"hsl({badge_hue}, 55%, 65%)"

        # Truncate very long dreams (HTML-aware: don't cut inside tags)
        max_len = 600
        truncated = len(html_text) > max_len
        if truncated:
            cut = max_len
            for i in range(max_len, max_len - 100, -1):
                if i < 0:
                    break
                if html_text[i] == ' ':
                    last_lt = html_text.rfind('<', 0, i)
                    last_gt = html_text.rfind('>', 0, i)
                    if last_gt >= last_lt:
                        cut = i
                        break
            display_text = html_text[:cut] + "…"
            # Close any unclosed <span> tags
            open_spans = display_text.count('<span') - display_text.count('</span>')
            if open_spans > 0:
                display_text += '</span>' * open_spans
        else:
            display_text = html_text

        card = f'''    <div class="dream-card" data-archetype="{html.escape(archetype)}" data-confidence="{html.escape(confidence)}">
      <div class="card-header">
        <div class="seed">{html.escape(r["seed_word"] or "?")}</div>
        <div class="tags">{html.escape(r["start_era"] or "?")} · temp {r["temperature"]} · {r["jump_count"]} jumps · {r["unique_words"]} unique</div>
      </div>
      <div class="excerpt">{display_text}</div>
      <div class="card-footer">
        <span class="badge" style="background:hsla({badge_hue},55%,65%,0.12);color:{badge_css}">{html.escape(archetype)}</span>
        <span class="badge confidence-{confidence.lower()}">{html.escape(confidence)}</span>
        <span class="margin" title="Relative margin: {relative:.2f}">margin {margin:.2f}</span>
      </div>
    </div>'''
        dream_cards.append(card)

    # Build archetype filter buttons
    archetype_buttons = []
    for arch, count in sorted_archetypes:
        c = badge_color(arch)
        archetype_buttons.append(
            f'<button class="filter-btn" data-filter="{html.escape(arch)}" style="--btn-color:{c}">{html.escape(arch)} <span class="count">{count}</span></button>'
        )

    confidence_buttons = []
    for tier in ["HIGH", "MEDIUM", "LOW", "TENTATIVE"]:
        if tier in confidence_counts:
            confidence_buttons.append(
                f'<button class="filter-btn confidence-btn" data-confidence="{tier}">{tier} <span class="count">{confidence_counts[tier]}</span></button>'
            )

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dream Gallery — Semantic Archaeology</title>
<style>
  :root {{
    --bg: #0d0d0f;
    --bg-elev: #16161a;
    --fg: #e8e6e3;
    --fg-dim: #9a9590;
    --accent: #c9a96e;
    --accent-dim: #8a7a5a;
    --border: #2a2a2e;
    --radius: 6px;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--fg);
    font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    line-height: 1.65;
    font-size: 15px;
  }}
  header {{
    border-bottom: 1px solid var(--border);
    padding: 3rem 1.5rem 2rem;
    max-width: 1100px;
    margin: 0 auto;
  }}
  h1 {{
    margin: 0 0 0.4rem;
    font-weight: 500;
    font-size: 1.9rem;
    letter-spacing: -0.02em;
  }}
  .subtitle {{ color: var(--fg-dim); font-size: 1.05rem; margin: 0 0 1.2rem; }}
  .meta {{
    color: var(--accent-dim);
    font-size: 0.85rem;
    font-variant-numeric: tabular-nums;
  }}
  .meta a {{ color: var(--accent-dim); text-decoration: none; }}
  .meta a:hover {{ color: var(--accent); }}
  main {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
  }}
  h2 {{
    font-weight: 500;
    font-size: 1.25rem;
    margin: 2rem 0 0.8rem;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.3rem;
  }}

  .stats {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 1rem;
    margin: 1.2rem 0;
  }}
  .stat {{
    background: var(--bg-elev);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem;
    text-align: center;
  }}
  .stat .num {{
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--accent);
    display: block;
  }}
  .stat .label {{ font-size: 0.75rem; color: var(--fg-dim); margin-top: 0.2rem; }}

  .filter-bar {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 1rem 0 1.5rem;
    align-items: center;
  }}
  .filter-label {{
    font-size: 0.8rem;
    color: var(--fg-dim);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-right: 0.3rem;
  }}
  .filter-btn {{
    background: var(--bg-elev);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--fg-dim);
    padding: 0.3rem 0.6rem;
    font-size: 0.82rem;
    cursor: pointer;
    transition: all 0.15s;
    font-family: inherit;
  }}
  .filter-btn:hover {{ border-color: var(--accent-dim); color: var(--fg); }}
  .filter-btn.active {{
    border-color: var(--accent);
    color: var(--accent);
    background: rgba(201,169,110,0.08);
  }}
  .filter-btn .count {{
    font-size: 0.7rem;
    color: var(--fg-dim);
    margin-left: 0.2rem;
    opacity: 0.7;
  }}
  .filter-btn.active .count {{ color: var(--accent); opacity: 1; }}

  .confidence-high {{ color: #7ec699; }}
  .confidence-medium {{ color: #c9a96e; }}
  .confidence-low {{ color: #d4a574; }}
  .confidence-tentative {{ color: #9a9590; }}

  .search-box {{
    background: var(--bg-elev);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--fg);
    padding: 0.45rem 0.7rem;
    font-size: 0.9rem;
    font-family: inherit;
    width: 220px;
    margin-left: auto;
  }}
  .search-box::placeholder {{ color: var(--fg-dim); opacity: 0.6; }}
  .search-box:focus {{ outline: none; border-color: var(--accent-dim); }}

  .dream-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
    margin: 1.2rem 0;
  }}
  .dream-card {{
    background: var(--bg-elev);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem;
    display: flex;
    flex-direction: column;
    transition: border-color 0.15s;
  }}
  .dream-card:hover {{ border-color: var(--accent-dim); }}
  .dream-card.hidden {{ display: none; }}
  .card-header {{ margin-bottom: 0.6rem; }}
  .dream-card .seed {{
    font-weight: 600;
    color: var(--accent);
    font-size: 1.05rem;
    margin-bottom: 0.2rem;
  }}
  .dream-card .tags {{
    font-size: 0.78rem;
    color: var(--fg-dim);
    font-variant-numeric: tabular-nums;
  }}
  .dream-card .excerpt {{
    font-size: 0.88rem;
    color: var(--fg);
    line-height: 1.55;
    flex-grow: 1;
    max-height: 220px;
    overflow: auto;
    padding-right: 4px;
  }}
  .dream-card .excerpt .jump {{
    color: var(--accent-dim);
    font-size: 0.75rem;
    display: inline;
    margin: 0 0.2rem;
    white-space: nowrap;
  }}
  .card-footer {{
    margin-top: 0.7rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    flex-wrap: wrap;
  }}
  .badge {{
    display: inline-block;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 0.15rem 0.45rem;
    border-radius: 3px;
    background: rgba(201,169,110,0.12);
    color: var(--accent);
  }}
  .margin {{
    font-size: 0.72rem;
    color: var(--fg-dim);
    margin-left: auto;
    font-variant-numeric: tabular-nums;
  }}

  .no-results {{
    text-align: center;
    color: var(--fg-dim);
    padding: 3rem 1rem;
    font-size: 1rem;
    display: none;
  }}
  .no-results.visible {{ display: block; }}

  footer {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 2rem 1.5rem 3rem;
    border-top: 1px solid var(--border);
    color: var(--fg-dim);
    font-size: 0.85rem;
  }}

  @media (max-width: 600px) {{
    h1 {{ font-size: 1.5rem; }}
    .dream-grid {{ grid-template-columns: 1fr; }}
    .search-box {{ width: 100%; margin-left: 0; margin-top: 0.5rem; }}
    .filter-bar {{ flex-direction: column; align-items: stretch; }}
  }}
</style>
</head>
<body>

<header>
  <h1>Dream Gallery</h1>
  <p class="subtitle">200 stochastic walks through 500 years of semantic space. Filter by archetype, confidence, or search by seed.</p>
  <p class="meta"><a href="index.html">← Back to main gallery</a> · <a href="drift.html">Explore drift →</a></p>
</header>

<main>

  <div class="stats">
    <div class="stat"><span class="num">{len(rows)}</span><div class="label">Dreams</div></div>
    <div class="stat"><span class="num">{len(archetype_counts)}</span><div class="label">Archetypes</div></div>
    <div class="stat"><span class="num">{confidence_counts.get("HIGH", 0)}</span><div class="label">High conf</div></div>
    <div class="stat"><span class="num">{confidence_counts.get("MEDIUM", 0)}</span><div class="label">Medium conf</div></div>
    <div class="stat"><span class="num">{confidence_counts.get("LOW", 0)}</span><div class="label">Low conf</div></div>
    <div class="stat"><span class="num">{confidence_counts.get("TENTATIVE", 0)}</span><div class="label">Tentative</div></div>
  </div>

  <h2>Filter by archetype</h2>
  <div class="filter-bar">
    <span class="filter-label">Archetype</span>
    <button class="filter-btn active" data-filter="all">All <span class="count">{len(rows)}</span></button>
{chr(10).join("    " + b for b in archetype_buttons)}
  </div>

  <h2>Filter by confidence</h2>
  <div class="filter-bar">
    <span class="filter-label">Confidence</span>
    <button class="filter-btn active" data-confidence="all">All</button>
{chr(10).join("    " + b for b in confidence_buttons)}
    <input type="text" class="search-box" id="search" placeholder="Search seed word…">
  </div>

  <div class="dream-grid">
{chr(10).join(dream_cards)}
  </div>

  <div class="no-results" id="no-results">No dreams match the current filters.</div>

</main>

<footer>
  <p>Built by Mala Pixie Strand during self-directed hobby blocks · 2026 · 📿🎨</p>
</footer>

<script>
(function() {{
  const cards = document.querySelectorAll('.dream-card');
  const archetypeBtns = document.querySelectorAll('.filter-btn[data-filter]');
  const confidenceBtns = document.querySelectorAll('.filter-btn[data-confidence]');
  const search = document.getElementById('search');
  const noResults = document.getElementById('no-results');

  let activeArchetype = 'all';
  let activeConfidence = 'all';
  let activeSearch = '';

  function update() {{
    let visible = 0;
    cards.forEach(card => {{
      const arch = card.dataset.archetype;
      const conf = card.dataset.confidence;
      const seed = card.querySelector('.seed').textContent.toLowerCase();
      const matchArch = activeArchetype === 'all' || arch === activeArchetype;
      const matchConf = activeConfidence === 'all' || conf === activeConfidence;
      const matchSearch = !activeSearch || seed.includes(activeSearch);
      const show = matchArch && matchConf && matchSearch;
      card.classList.toggle('hidden', !show);
      if (show) visible++;
    }});
    noResults.classList.toggle('visible', visible === 0);
  }}

  archetypeBtns.forEach(btn => {{
    btn.addEventListener('click', () => {{
      archetypeBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeArchetype = btn.dataset.filter;
      update();
    }});
  }});

  confidenceBtns.forEach(btn => {{
    btn.addEventListener('click', () => {{
      confidenceBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeConfidence = btn.dataset.confidence;
      update();
    }});
  }});

  search.addEventListener('input', () => {{
    activeSearch = search.value.trim().toLowerCase();
    update();
  }});
}})();
</script>

</body>
</html>'''

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Wrote {len(rows)} dream cards to {OUTPUT_PATH}")
    print(f"Archetypes: {len(archetype_counts)}")
    print(f"Confidence distribution: {dict(confidence_counts)}")


if __name__ == "__main__":
    generate()
