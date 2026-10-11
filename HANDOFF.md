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
- **Rate limits shape the workflow, and they are bucketed per endpoint family.** `/pages` and the general
  bucket exhausted separately at 03:06Z / 03:14Z (`verify_live.py` alone costs thousands of calls), so the
  first `audit_kind` run stopped `INCOMPLETE` at 24/145. Both audits were then run against fresh windows.
  If `last_kind_audit.json` / `last_description_audit.json` report `INCOMPLETE`, that is an access block,
  not a data disagreement (`AGENTS.md` §4).

### Second half of the session — six entries corrected, both audits clean

- **`audit_kind.py` caught six real defects that the 2026-10-01 pass had left behind** (`IRR-138`):
  `GEMSDOE22`–`GEMSDOE27` were published as `kind: stub` with prose saying the configured root had no
  `index.html`. `contents/index.html?ref=<snapshot head>` returns HTTP 200 for all six at the very heads
  recorded in this snapshot (`9648109`, `ebf8fb2`, `07345ea`, `cc90c1a`, `ba071a3`, `3dc3a6b`), so the
  stored label and the sentence were **already false when published** — this was not drift that happened
  afterwards. All six READMEs were re-read at their current heads (they are now full research lanes, e.g.
  `GEMSDOE22`'s README is 84 KB and documents two upload candidates) and every field was rewritten. One
  further oddity found while reading: `GEMSDOE22`'s README heading says `22GEMSDOE` and its 297-byte root
  `index.html` carries the title `19GEMSDOE`.
- **Audit results in the published snapshot:** `audit_kind.py` **145/145, 0 disagreements, 0 unresolved**;
  `audit_descriptions.py` **145/145 checked**, 1 item needing review (`230` in `MALTASUPPLEMENTAL`, whose
  README at head no longer contains it — registered as `FL-12`), 42 documented exceptions;
  `scripts/validate` **PASS**; `VERIFICATION.md` regenerated (695 lines, 145 ledger rows, 138 irregularities).
- **Final snapshot:** **145 sites** (135 HTML entry points / 10 documentation stubs), 144 `built` + 1
  `errored`, 10,579 commits, **41 prose-stale** (down from 47 after the six re-reads), 138 irregularities.

- **The browser suite was executed after all, in CI.** PR #23's `browser-tests` job installed Chromium, Firefox and WebKit, ran `npm run check` and `npm test`, and **passed** (2m46s, run
  `38110045438`). This is the first pass where the rendered directory was verified for all 145 rows in real
  browsers rather than only discovered; the sandbox itself still cannot download browser binaries.

### What is next

1. **T-002 (highest accuracy risk):** 41 description stamps are behind their heads, down from 47 after the
   six `GEMSDOE22`–`27` re-reads. Re-read
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

### Post-merge (same session, after T-001 landed)

- **T-001 merged into `main` at `2026-10-11T04:04:11Z`** — PR [#23](https://github.com/buffedlizard55-lab/MasterSite/pull/23), merge commit `43c827f`. `main` now carries the 138-irregularity snapshot; read back from `origin/main:data/sites.js` to confirm rather than assumed: `counts.sites` 145, `apps` 135, `stubs` 10, `pagesBuilt` 144, `commits` 10,579, `proseStale` 41, `irregularities` 138 (IRR-01…IRR-138).
- **The browser suite passed before and after the merge.** On the PR head: runs `38110045438` and `38110237192`, `browser-tests` green in 2m46s / 2m37s (Chromium, Firefox, WebKit; `npm run check` + `npm test`). On `main` after the merge: run `38110405707`, green on `43c827f`. The deployed directory reports Pages `status: built` at <https://buffedlizard55-lab.github.io/MasterSite/>.
- **What the next session inherits:** `main` is the source of truth and is current as of the merge; `TASKS.md` has T-001 marked done and T-002/T-003/T-004/T-007/T-008/T-009/T-010/T-011 queued; `FLAGGED.md` ends at FL-12. Pull-rebase first — several GEMS lanes push multiple times a day, so the stale count will already have moved by the time anyone reads this.
---

## Session `arena-96e82e25` — 2026-10-11 (reconcile onto main, close FL-12, per-site export)

**Branch:** `arena/96e82e25-mastersite`, rebased onto `main` at `43c827f` (PR #23, session
`arena-235d5594`) before any new work. This session's earlier local history was based on `71ab6b6`
and its single claim commit (`9b0733f`, a 54-line `TASKS.md`) was superseded by main's protocol
files; the branch was force-updated to the reconciled history so nothing stale is proposed. The
dropped commit contained no data, overlay or generated work — only the pre-protocol claim file.

### What was done

- **`FL-12` closed by re-reading, not by silencing (`T-002`, first slice).** `MALTASUPPLEMENTAL`'s
  carried description still said “twelve pages … Type G 230 V”, but the README at the snapshot head
  `81930be` (commit time `2026-10-11T02:58:20Z`, 8,385 bytes) is already the rewritten *Malta Trip
  Guide* and contains no `230` token. The entry was rewritten from that README alone; the page
  count, the voltage token and the transport-mode list were **withdrawn** as not re-derivable, and
  the stamp set to the snapshot head so `proseStale` again means exactly “prose behind the API
  record”. Queue **41 → 40**; `audit_descriptions.py` re-run: **145 / 145 checked, 0 needing review,
  42 documented exceptions**.
- **The protocol's file-per-site requirement now exists as generated output.** `data/sites/`
  holds one JSON record per public repository (145 files, `<owner>__<repo>.json`) with `owner`,
  `repo`, `description`, `created`, `lastUpdated`, `pagesUrl`, `sourceLinks`, a mechanical
  `verified` flag, `verifiedAtSha` / `snapshotHeadSha` and `unverifiedFields`. It is written by the
  new `tools/export_site_records.py` from `overlay.json` + `data/sites.js`; it is never hand-edited,
  and `--check` fails if the export drifts from the published snapshot.
- **`scripts/validate` now gates that export** (`checks run: 4670`, PASS): sync with `data/sites.js`,
  record count, every `unverifiedFields` name present in `FLAGGED.md`, and every `PROSE-STALE`
  record named in the `VERIFICATION.md` stale queue. Docs synced: README status table (stale 40,
  lint 0 needing review, 138 / 28 irregularities / notes), `AGENTS.md` counts and re-render stamp,
  `FLAGGED.md` `FL-10` (40) and `FL-12` (closed, with the resolving endpoint).
- **Generated artifacts regenerated in this order:** `build_data.py --overlay-only` (API snapshot
  `2026-10-11T03:01:01Z` reused; narrative re-rendered `04:09:48Z`) → `export_site_records.py` →
  `build_verification.py` (696 lines, 145 ledger rows) → `audit_descriptions.py` → `scripts/validate`
  → `npm run check`.

### Blocked / not attempted

- The 39 remaining stale stamps were **not** re-read this session; the queue is public in
  `VERIFICATION.md` and each entry carries its stamped SHA beside its head SHA.
- `audit_kind.py` was not re-run: the underlying API snapshot is unchanged from main's completed
  run (145 / 145, 0 disagreements), and nothing in this session touched `kind` derivation.
- Sandbox limits are unchanged: no `*.github.io` egress (T-003) and no browser binaries (CI is the
  browser environment of record). No uptime, rendering or usage claim is made anywhere.

### What is next

1. **T-002 continues:** 40 stale descriptions remain (stale-first table in `VERIFICATION.md`).
   Re-read each at its head, rewrite prose only from repository-owned files, and update
   `description` + `lastVerified` + `verifiedBasis` + `verifiedAtSha` **together**.
2. **T-007 family view** and **T-010 census workflow** are unchanged and still unclaimed.
3. Keep running `python3 tools/export_site_records.py` after every `build_data.py` — `scripts/validate`
   will fail if the committed export drifts.

### Post-merge (same session, after this PR landed)

- **`FL-12` closure and the per-site export merged into `main` at `2026-10-11T04:17:32Z`** — PR
  [#25](https://github.com/buffedlizard55-lab/MasterSite/pull/25), merge commit `0e15234`. Read back
  from `origin/main:data/sites.js` after the merge rather than assumed: `counts.proseStale` **40**,
  `counts.sites` 145, `counts.apps` 135, `counts.stubs` 10, `irregularities` 138; the
  `MALTASUPPLEMENTAL` record reads `proseStale: false` with `verifiedAtSha` `81930be…`.
- **CI on the PR head was green** before the merge: `browser-tests` run
  [`38110945436`](https://github.com/buffedlizard55-lab/MasterSite/actions/runs/38110945436)
  (Chromium, Firefox, WebKit; `npm run check` + `npm test`). `scripts/validate` passed locally with
  4,670 checks, and `tools/export_site_records.py --check` reported the export in sync.
- **Rebase note:** the PR was opened against `43c827f` and rebased onto `66251b1` (the parallel
  session's post-merge commit, PR #24) before merge; the only conflict was this file and it was
  resolved by keeping both entries.
- **What the next session inherits:** `T-002` is claimed by `session=96e82e25` with slice 1 landed;
  40 stale descriptions remain and are listed stale-first in `VERIFICATION.md`. Run
  `python3 tools/export_site_records.py` after every `build_data.py` — `scripts/validate` fails if
  the committed `data/sites/` export drifts from the snapshot.
