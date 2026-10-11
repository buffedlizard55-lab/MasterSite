# TASKS.md — MasterSite work queue

**Protocol for every session.** One session claims exactly one task.

1. `git pull --rebase origin main`, then read this file and [`FLAGGED.md`](FLAGGED.md).
2. Pick **one** task whose `Status` is `unclaimed`. Do not touch a task another session claimed.
3. Claim it by editing that task's `Claim` line to `session=<id> at=<UTC timestamp>`, then **commit only that claim and push it immediately**.
4. Work only on your own session branch (Arena sessions are pinned to their `arena/<session>-<slug>` branch; do not commit to `main`).
5. Rebase on `main` before opening a PR, run `scripts/validate` (and the audit commands in [`AGENTS.md`](AGENTS.md) §4), open the PR, and mark the task `Status`/`Done` in the **same PR**.
6. Append what you did, what is blocked, and what is next to [`HANDOFF.md`](HANDOFF.md) before you finish.

**Never** hand-edit `data/sites.js` or `VERIFICATION.md`; they are generated. Curated prose lives in
`tools/overlay.json` only. Every fact needs an official source URL that a reviewer can open by hand
(GitHub REST API endpoints for the record, repository-owned files for prose). If a value cannot be
verified, leave it `null` and add a row to `FLAGGED.md` — never guess.

---

## Task table

| ID | Task | Status | Claim | Blocked by |
|---|---|---|---|---|
| T-001 | Full public-repo census refresh for both accounts; publish every unlisted public Pages repository with sourced prose | **done** | session=arena-235d5594 at=2026-10-11T02:53:00Z · done 2026-10-11 · snapshot `2026-10-11T03:01:01Z`, audits re-run `03:54Z` | — |
| T-002 | Re-read the `PROSE-STALE` description stamps at current heads (never clear the queue by editing only a SHA). **40 of 145 are stale as of the 2026-10-11 snapshot**; `FL-12` (`MALTASUPPLEMENTAL`) was closed in this session's first slice, the remaining 40 are re-read one at a time | claimed | session=96e82e25 at=2026-10-11T04:12:40Z · slice 1: `MALTASUPPLEMENTAL` re-read at `81930be`, FL-12 closed, stale queue 41 → 40 | — |
| T-003 | Live HTTP smoke test of every published Pages URL (status + title), recorded separately from `pagesStatus` | **done** | session=arena-ff71591b at=2026-10-11T04:57:45Z · done 2026-10-11 · runner `38113546456`: 145/145 HTTP 200; 144 titles, `SABERENGY` title null (FL-15); separate [preserved report](reports/pages-smoke/2026-10-11T050331Z.md) | — |
| T-004 | Owner decision record: the 4 frozen unreachable repositories (`JobSearchSF`, `MALTA`, `MALTA-LAWS`, `MALTA2`) — keep frozen, restore, or drop | unclaimed | — | Owner decision |
| T-005 | Confirm Pages build health for the non-`built` entries (`GEMSDOE53` `errored`, `MALTASUPPLEMENTAL` `building`) and re-check each refresh | done | session=arena-c29c2d14 at=2026-10-11T05:00:29Z · done 2026-10-11 · re-read 2026-10-11T05:00:34Z–05:00:36Z: `GEMSDOE53` still `errored` (no push since 2026-10-09T02:00:53Z — FL-05 stays open for owner/rebuild), `MALTASUPPLEMENTAL` `built` (FL-06 re-confirmed); cadence written into AGENTS.md §4; post-snapshot head drift found → new FL-14 (T-002 queue) | Upstream GitHub Pages builds |
| T-006 | Owner decision record: `6GEMSDOE` recommends deleting the other GEMS repositories (IRR-119) — the directory takes no position | unclaimed | — | Owner decision |
| T-007 | Family view: group the 40+ `GEMSDOE`-family competition lanes so 145 entries stay readable (UI feature, generator owner session only) | unclaimed | — | T-001 |
| T-008 | Verify the three new repositories with no root `index.html` (`62GEMSDOE`, `GEMSDOE42`, `GEMSDOE44`) publish a usable landing page at the configured path | unclaimed | — | Live egress (see T-003) |
| T-009 | Confirm `kanlerxz87-cyber` stays at 0 public repositories in every refresh and keep the census note current | **done** | session=7fefeea8 at=2026-10-11T04:58:44Z · done 2026-10-11T04:59:04Z · live `GET /users/kanlerxz87-cyber` → `public_repos: 0`; `tools/census_guard.py` PASS (146 public = 145 listed + 1 excluded) | — |
| T-010 | Close the coverage-detection gap: the account grew 108 → 146 public repos (38 unlisted Pages sites) between 2026-10-01 and 2026-10-11 with nothing to warn anyone. Add a scheduled refresh workflow (or a cheap census-only check) that fails loudly when `counts.publicRepos` exceeds `counts.sites + excluded` | **done** | session=arena-631565b3 at=2026-10-11T04:17:45Z · done 2026-10-11 · `tools/census_guard.py` + daily `.github/workflows/census.yml` (opens/updates a `census-gap` issue on failure, closes it on recovery) | — |
| T-011 | Backfill inline hand-review endpoints where a basis still relies on the ledger row alone, and keep `scripts/validate` green as new entries land | unclaimed | — | — |

`Status` values: `unclaimed` · `claimed` · `in review` · `blocked` · `done`.

---

## Frozen constraints (do not violate)

- **`ProjX` is permanently excluded by owner instruction.** Never add its name, URL, description or
  metadata to the overlay, generated data, ledger, README counts or exports. The generator asserts
  that listed + excluded balances to the account's Pages count.
- **Do not silently delete the four unreachable records.** They stay frozen with their last verified
  values until the owner decides (T-004).
- **Never claim** "zero hallucinations", exhaustive verification, site uptime, interactivity, or last
  site use. GitHub's public API does not expose visits or last use; say what the source supports.

## New to this repo?

Read [`AGENTS.md`](AGENTS.md) first (scope, source policy, data workflow, test expectations), then
[`README.md`](README.md) for the current snapshot and [`VERIFICATION.md`](VERIFICATION.md) for the
per-entry evidence ledger.
