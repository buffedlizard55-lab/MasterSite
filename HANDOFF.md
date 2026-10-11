# HANDOFF.md — session log

Append-only. Newest entry last. Each entry: what was done, what is blocked, what is next.
Every claim in an entry must name the source it came from.

---

## Session `arena-235d5594` — 2026-10-11 (bootstrap + T-001: full census refresh)

**Branch:** `arena/235d5594-mastersite` (this session is pinned to its Arena branch, which satisfies
the "own branch, never `main`" rule; no other branch was created, and `main` was only touched by the
merged PR).

### What was done

- **Repository review.** The implementation was further along than the request assumed: the directory,
  generator, ledger and read-only audit tools already exist (`tools/build_data.py`, `verify_live.py`,
  `audit_kind.py`, `audit_descriptions.py`, `build_verification.py`), and `data/sites.js` +
  `VERIFICATION.md` are generated artifacts that must never be hand-edited.
- **Created the missing multi-session protocol files:** `TASKS.md` (claim protocol + queue),
  `FLAGGED.md` (null fields and unresolved irregularities), this file, and `scripts/validate`
  (dependency-free validator: official source links present, no unverified values, counts and overlay
  in agreement, ledger rows carrying Live / Pages API / Commits API links per record).
- **T-001 — independent census.** Read `GET /users/buffedlizard55-lab` and
  `GET /users/kanlerxz87-cyber`, paginated `GET /users/{login}/repos` across two pages, then
  `GET /repos/{owner}/{repo}`, `GET /repos/{owner}/{repo}/pages`, the default-branch commit list and
  the configured-path `contents/index.html` probe for every repository. Result:
  **146 public repositories / 146 with Pages enabled** for `buffedlizard55-lab`, **0** for
  `kanlerxz87-cyber`.
- **The headline defect: 38 public Pages repositories were missing from the directory.** The previous
  snapshot published 107 of 108; the account had since grown to 146, and 33 GEMSDOE-family lanes plus
  3 scoring-discrepancy repositories (created 2026-10-02 → 2026-10-08) were live on the web with no
  entry here. `build_data.py` skips any repository with no `tools/overlay.json` entry by design, so the
  gap was silent — nothing was wrong, 38 things were absent (`IRR-131`, `FL-11`).
- **All 38 published**, each with prose curated from the repository's own `README.md` at the recorded
  head SHA, plus `flags` for every self-reported caveat, and a `verifiedBasis` naming the README
  contents endpoint, the Pages endpoint and the configured-path probe with their observed results.
  The 3 stubs among them (`62GEMSDOE`, `GEMSDOE42`, `GEMSDOE44`) are classified from their own
  official probe, not from a name: two of them do publish full documentation sites under `docs/`
  (`IRR-134`).
- **Fixed a latent generator bug that blocked exactly this work (`IRR-137`).** `api_get()` passed raw
  file bodies through `json.loads`, so `has_entry_point()` lost the HTTP status of a successful probe
  and the build aborted on the first entry without an explicit `kind`. Every one of the 107 pre-existing
  entries happened to carry one, so the path had never run. `api_get()` now returns the text when the
  body is not JSON; the 38 new entries pin `kind` from their own probe and `audit_kind.py` re-derives
  all kinds independently.
- **Prose provenance hardening.** 47 records' bases mixed a bare `GET /repos/...` path (accurate but
  not clickable) into otherwise sourced prose, and 8 carried a read note with no endpoint at all. Both
  classes now carry full official URLs; the original wording was preserved and the added lines state
  explicitly that the prose was **not** re-read at those endpoints.
- **Unreachable records re-checked, not dropped.** `JobSearchSF`, `MALTA`, `MALTA-LAWS`, `MALTA2` all
  still return HTTP 404 and remain absent from the 146-repository public list; each frozen record gained
  a dated 2026-10-11 re-confirmation plus the note that the search API's single "MALTA" match is
  **`MALTASUPPLEMENTAL`** (a live repository), not the retired `MALTA`.
- **Snapshot published:** 145 sites (129 HTML entry points / 16 documentation stubs), 144 `built` +
  1 `errored`, 10,579 default-branch commits, 13 categories, 4 frozen unreachable, `ProjX` still
  excluded by owner instruction. `verify_live.py`: **1,901 checks, 0 hard mismatches, 3 volatile drifts**
  (`59GEMSDOE.pushedAt`, `61GEMSDOE.sizeKb`, `KalshiPaperSim.sizeKb` — fields GitHub recomputes
  asynchronously).

### What is blocked

- **Live HTTP checks of `*.github.io` are impossible from this sandbox.** `curl` returns HTTP 000 for
  every Pages URL, including this project's own, so nothing here asserts uptime, rendering or
  interactivity. `pagesStatus: built` remains build metadata only (`FL-02`, `T-003`).
- **`GEMSDOE53` reports Pages status `errored`** — the only non-`built` entry — while its own README
  labels its artifact `OK TO SUBMIT`. Those are different objects (a failed site build vs a locally
  gated GeoTIFF); the directory records the API value and infers nothing (`FL-05`, `IRR-132`, `T-005`).
- **Owner-only decisions:** the four frozen 404 repositories (`FL-03`, `T-004`) and `6GEMSDOE`'s
  instruction to delete the other GEMS repositories (`FL-08`, `T-006`).
- **Rate limits shape the workflow.** `verify_live.py` alone costs thousands of calls; that window was
  exhausted mid-`audit_kind` at 03:07Z and the audit chain was rescheduled for the 03:53Z reset. If
  `last_kind_audit.json` / `last_description_audit.json` report `INCOMPLETE`, that is a rate-limit
  block, not a data disagreement (`AGENTS.md` §4).

### What is next

1. **T-002 (highest accuracy risk):** 47 description stamps are behind their heads, up from 38. Re-read
   each against the repository's own files at the current head and update `description` +
   `lastVerified` + `verifiedBasis` + `verifiedAtSha` **together**; never clear staleness by editing
   only a SHA. Several GEMS lanes commit multiple times per day — `60GEMSDOE` advanced mid-session and
   its entry was re-read at the new head while writing it — so expect fresh drift at every refresh.
2. **T-010 (highest structural risk):** nothing detects a new repository appearing. Add a scheduled
   census (or a `--census-only` mode) that fails when `counts.publicRepos > counts.sites + excluded`.
3. **T-003 / T-008:** live smoke test of all 145 Pages URLs from a machine with general egress, kept
   separate from `pagesStatus`, including whether `62GEMSDOE` / `GEMSDOE42` / `GEMSDOE44` serve a page
   at the configured root.
4. **T-007:** 145 entries is now a wall; the GEMS family alone is 40+ lanes needing a family view.
