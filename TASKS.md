# TASKS.md — Multi-session task ledger

Claim protocol: one task per session. Add `claimed: <session-id> @ <UTC ISO timestamp>` to
the line, commit **only** the claim, and push immediately before any other work. Do not
work on a claimed task. Mark `[x]` and release the claim in the PR that completes it.
Sequenced/parallel work: one task per small PR, rebase on `main` before opening the PR.

Conventions that supersede earlier drafts of this protocol (documented in `AGENTS.md`):
per-site curation lives in `tools/overlay.json` keyed by repo name (one entry per site —
the conflict-avoidance goal of the original `data/sites/<owner>__<repo>.json` proposal),
and `data/sites.js` + `VERIFICATION.md` are generated, never hand-edited.

## Task list

| ID | Status | Task | Claimed |
|---|---|---|---|
| T-01 | [ ] open | Refresh the full API census (account grew 108 → 146 public repos since the 2026-10-01 snapshot; 38 new repos must be verified, Pages-checked, and either curated into `tools/overlay.json` or recorded as unlisted with reasons), then regenerate `data/sites.js` + `VERIFICATION.md` and update README counts | claimed: arena-d833703f @ 2026-10-11T03:05Z |
| T-02 | [ ] open | Re-read the stale-description queue (38 entries behind their snapshot heads per the 2026-10-01 table) against current repository-owned files; update `description`, `lastVerified`, `verifiedBasis`, `verifiedAtSha` together. Never clear the queue by changing only a SHA | — |
| T-03 | [ ] open | Confirm the Playwright PR workflow actually executes the 84 browser cases (local runs were blocked by `cdn.playwright.dev` `ECONNRESET`); report the real result in README/AGENTS status lines | — |
| T-04 | [ ] open | OWNER INPUT NEEDED: `JobSearchSF`, `MALTA`, `MALTA-LAWS`, `MALTA2` returned HTTP 404 — restore or confirm retirement; until then they stay in the frozen `unreachable` section | blocked on owner |
| T-05 | [ ] open | Consider per-repo overlay files (e.g. `tools/overlay.d/<repo>.json`) to reduce parallel-session conflicts on the single `tools/overlay.json`, and/or a scheduled audit that opens a review PR on drift | — |
