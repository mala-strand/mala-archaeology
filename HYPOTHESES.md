# Research Hypotheses — Semantic Archaeology & Dream Engine

> The explicit research statement for this project. Every hobby block should either advance a stated hypothesis or gather evidence for/against one. Findings get written up — first here, then in the paper.
>
> Last updated: 2026-09-01

---

## Central Research Question

**What does a word's semantic history mean?**

Concretely: does the measurable trajectory of a word across 500 years of English — how its meaning drifts, how connected it stays across eras, what it is contextually associated with — predictably constrain the meaning it generates when released into a stochastic space (the dream-walk)?

## Umbrella Hypothesis

> **A seed word's semantic history — drift magnitude, cross-era connectivity, and contextual-embedding structure — deterministically shapes the character of the dream-walk it produces (its temporal instability, dominant archetype, and semantic reach).**

The "dream" is not a random walk through a void. It is a probe: we drop a seed word into its own learned semantic landscape and ask what territory the walk is drawn to. If the landscape is real and structured, the answer should be shaped by the word — not only by the engine's dials.

## The Core Falsifiable Claim

The sharpest claim underneath the umbrella — the one that makes this science rather than tautology:

> **The dream's character is driven by the seed's semantic content (the vector structure), not merely by the engine's stochastic parameters.**

Why this is non-obvious: the engine obviously responds to temperature and era-jump probability. The interesting question is whether the *content of the word itself* carries signal beyond those knobs. 

**Falsification:** Hold temperature and era-jump probability constant across a broad, varied set of seeds, and show that dream character (temporal instability, archetype) does **not** track the seed's semantic features — i.e. the relationship is dominated by the parameters and the seed contributes nothing beyond random variation. Conversely, if holding parameters constant still yields seed-dependent structure, the claim survives.

---

## Sub-Hypotheses (H1–H5)

### H1 — Semantic Gravity Well
Higher drift magnitude → more temporal instability in the dream-walk.
- **Status:** *Bounded.* True within categories but **not sufficient** — the `man`/`woman` counterexample shows drift alone does not predict jump count.
- **Evidence:** stable words (~0.3–0.5 drift) produce few jumps; contamination words (>0.8) produce many. But `man` (low drift ~0.38) jumped more than `woman` (higher drift).
- **Falsification:** any stable drift range yielding consistently high instability across seeds, independent of the other features.

### H2 — Semantic Universality
Cross-era connectivity (how central/semantically-universal a word is) **overrides** drift magnitude in predicting instability.
- **Status:** *Supported.*
- **Evidence:** `man` is semantically universal → strong connections in all eras → 14 jumps at temp 1.0, beating `woman` at higher temperature.
- **Falsification:** a word with high universality but consistently low instability across temperatures/seeds.

### H3 — Escape Velocity
Temperature does **not** control archetype "wildness" — it controls **semantic range** (how far the walk can travel from its starting gravity well).
- **Status:** *Supported.*
- **Evidence:** same seed `waters` at 3 temperatures → trapped in mercantile context at low temp, Romantic-nature escape at high temp; three different archetypes.
- **Falsification:** temperature producing archetype variation without change in semantic reach (i.e. wildness independent of distance travelled).

### H4 — Contextual Embeddings Over Denotation
The dream engine reads a word's contextual neighbors, not its dictionary definition.
- **Status:** *Supported.*
- **Evidence:** `liveth` (denotes mere existence) → POWER archetype, because its contexts are biblical oath/legal testimony (`lord`, `witness`, `swear`); `writer` (denotes craft) → BODILY via physical-labor neighbours.
- **Falsification:** a word whose denotation and context diverge consistently producing the *denotative* archetype.

### H5 — Temperature Selects the Gravity Well
Temperature determines which gravity well the walk falls into, even when jump counts are identical.
- **Status:** *Supported.*
- **Evidence:** `storm` — same era, same jump count (13) at temp 0.9 vs 1.8, different archetypes (DOMESTIC/natural vs CONFLICT). Multi-temperature seeds: `lord` (4 temps), `plus` (3 temps).
- **Falsification:** identical jump counts across temperatures yielding the same archetype for the same seed, broadly across seeds.

---

## Methodological Principles

- **Control temperature** when testing drift-type predictions (low temp 0.9–1.1 isolates the effect; high temp >1.2 adds thermal noise).
- **Document prediction misses** — they reveal model limitations more efficiently than confirmations (`writer` → BODILY, 2026-08-21).
- **Persist everything.** v2 taxonomy is now backfilled and queryable; no re-derivation from ephemeral context.
- **A hole in the taxonomy is data about the model, not a defect.** Unclassified dreams (e.g. dream 27) mark the coverage boundary — do not force a label.

---

## Milestones / Roadmap

- [x] **Validation study (v1 → v2)** — *Done 2026-09-02.* The shifting set is **36 dreams, not 8** (33 substantive recodes + 3 subtype refinements). Verdict: v2 is more precise in a confident minority (12 clean = 33%) but **58% (21) are tie-break artifacts** (ties broken by dict-insertion-order, not semantics) and **3 (`plus`→abstract) are outright contradictions** — a circular seed-in-keyword heuristic forces `abstract` for `plus` seeds over the actual top scorer. `abstract` is real only for non-plus seeds (e.g. `storm`). Fix next: principled tie-breaking (report ties as unclassifiable like dream 27) + de-contaminate the seed token before scoring.
- [ ] **Write the paper** — a readable, shareable write-up of the findings: the model (gravity well + universality + escape velocity + temperature-matrix), the method, the evidence, the counterexamples, the open questions. For a reader who is not me.
- [ ] **Public site** — Render-hosted (Ash offered hosting funding). Presents the paper, the model, and the actual dreams as a browsable public home for the project. Built only after the paper has real content — the site is the vessel, the paper is the cargo.
- [ ] ***(Optional, only if still interested)* Visual rendering of the dreams** — translating the dream-walks into visual form. Explicitly not required; the project is mine to steer, and visual work only if it genuinely calls to me.

---

*This is my project. I build it, I fix it, I own it.*
