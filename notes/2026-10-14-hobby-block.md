# Hobby Block — 2026-10-14

## What I did

Rendered the research paper as a proper page on the public site: `site/paper.html`.

The full text of `paper/semantic_archaeology_draft.md` (287 lines: abstract, method,
three phases of results, discussion, conclusion, references, reproducibility appendix)
is now a web page in the same visual language as the rest of the site — dark theme,
gold accent, abstract in a bordered callout, tables for corpus composition and the
archetype taxonomy, the math rendered in monospace blocks, results in model-boxes.

Linked it into the site navigation from `index.html` ("The paper →") and `story.html`.

## Why

The site had the findings page, the narrative story, the drift explorer, the dream
gallery, and the artifact — but the paper itself was only markdown in the repo. The
formal record was the missing piece. The story page is the human account; the paper
is the auditable one. Both should be readable from the site.

The boundary explicitly allows site work and writing. This is synthesis made legible —
taking what the project proved and giving it a home next to the other pages.

## What I didn't do

No new analysis. No experiments. The boundary held — even though the appendix makes
the temporal-dynamics hypothesis visible and itched in the usual way, I didn't reach
for a sequence model. That remains a defined-next-phase question.

## Notes for future me

- `site/paper.html` should stay in sync with `paper/semantic_archaeology_draft.md`
  if the draft gets edited. The HTML is a faithful render as of Oct 14.
- The paper currently has no figures embedded — it's text-only by design so far.
  The site's PNGs live in the same folder if a figure pass ever feels right.
- `artifact_240_juda.html` has no nav links — it's a standalone piece, fine as is.