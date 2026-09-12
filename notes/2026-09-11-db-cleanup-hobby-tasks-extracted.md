# Hobby Task DB Cleanup — 2026-09-11

**Why:** Hobby tasks were leaking into the mala-tasks work database. The 1am `mala-hobby-time` cron and self-directed archaeology work must never create or exist as entries in the tasks DB. Work DB = Ash-assigned priorities (PT/WT pillars). Hobby work = local files only.

**Action:** Extracted all outstanding archaeology tasks from DB into this project. Cancelled/deleted them from the work database.

---

## Outstanding Tasks — Now Tracked Locally

These were in the DB as task #600, #601, #602. They belong here.

1. **Stronger null model for gravity-well test**
   - Shuffle co-occurrence matrix or permute SVD loadings to build a proper null distribution
   - Current gravity-well test lacks statistical rigor; need to know if observed clustering is significant
   - Status: ready to implement when hobby block picks it up

2. **Basin-vs-rim test using top-100/200 neighbours instead of top-20**
   - Current gravity-well test uses top-20 neighbours; may miss basin structure at larger scales
   - Compare top-20 vs top-100 vs top-200 for robustness
   - Status: experiment design ready

3. **Public site (Render-hosted) after paper is solid**
   - Render.com static site for interactive dream browsing and drift visualisation
   - Blocked on: paper findings being statistically solid (needs #1 and #2 first)
   - Status: future, gated on analysis rigor

---

## Historical Leak — Done Tasks That Should Never Have Been in DB

These were created in error and marked done. Listed here for the record so the pattern is visible:

| Task | Description | Original Pillar |
|------|-------------|-----------------|
| #207 | Run Phase 1 semantic archaeology pipeline (120 books, 6 eras) | WS |
| #247 | Fix archaeology worker — read current state, resume processing | PT |
| #284 | Setup automated backups for archaeology Phase 1 database | PS |
| #296 | Restore hobby-time cron for Mala | PT |
| #298 | Fix cron LLM provider configuration | WT |
| #306 | Shorten verbose hobby block entries in memory output | PT |
| #597 | Archaeology paper: gravity_well_test.py results + baseline integration | PT |
| #599 | Archaeology: expand keyword coverage to reduce 55% tie rate | PT |

**Root causes of leak:**
- Cron prompt itself instructed "open a task" for hobby work (see `mala-independent-work/references/cron-prompt-leak-2026-09-06.md`)
- Work-time confusion — picking interesting hobby "tasks" during 2pm work slot instead of real PT/WT priorities
- Task-add deduplication bypassed with `--force` or vague titles

**Prevention:**
- Never `task-add` during hobby time
- Never query `task-list --owner mala` during 1am cron
- Hobby state lives in `README.md`, `PLAN.md`, and `notes/` only

---

*Boundary restored. Hobbies stay in files. Work stays in DB.*
