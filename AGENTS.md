# AGENTS.md — MasterSite Maintenance Instructions

Read this before refreshing data or changing the directory. The public directory is a generated snapshot, not a live uptime or usage monitor.

## 1. Scope and current snapshot

- The directory covers public GitHub Pages repositories owned by `buffedlizard55-lab`; `kanlerxz87-cyber` is also queried and currently has no public repositories.
- The latest API snapshot (`2026-10-11T15:06:10Z`, a full network census by session `arena-d98d5339` under T-013) contains **145 listed sites** from an account census of **146 public repositories / 146 Pages-enabled repositories**, **10,863** default-branch commits and **141** irregularities. The single difference is the permanent `ProjX` exclusion below. `kanlerxz87-cyber` has 0 public repositories. Four repositories returned HTTP 404 and remain preserved separately as unreachable records (all four re-checked by hand, most recently 2026-10-11T15:38Z; see README and `OWNER-DECISIONS.md`).
- **The account grew from 108 to 146 public repositories between 2026-10-01 and 2026-10-11, and 38 public Pages sites were live with no entry here until this refresh** (`IRR-131`). The generator skips any repository without a curated overlay entry, so the gap was silent. Task `T-010` in [`TASKS.md`](TASKS.md) proposes a scheduled census that fails loudly when `counts.publicRepos` exceeds listed + excluded. **Treat "the directory is complete" as a claim to re-verify every pass, not an assumption.**
- `kind: "app"` and `kind: "stub"` are legacy schema values. They mean only that the configured Pages source path does or does not contain `index.html`. They do **not** mean interactive/noninteractive, working/broken, or online/offline. The latest audit re-derived all 145 kinds: **135 apps, 10 stubs, 0 disagreements, 0 unresolved**.
- `pagesStatus: "built"` is GitHub API metadata, not a successful HTTP or browser check. At the latest snapshot **143 entries report `built` and two report `errored`** — `GEMSDOE53` (`IRR-132`, `FL-05`) and `NFLInjuryReport` (`IRR-141`, a second failure found by the `15:06:10Z` pass). GitHub's public repository and Pages APIs do not expose site visits or last use; the UI's **Last commit** is the newest committer timestamp on the default branch.
- **51** description SHAs are behind their repositories' current heads at the `15:06:10Z` snapshot (45 at `05:12:27Z`, 40 before that; the `15:06:10Z` pass re-read two — `MALTASUPPLEMENTAL` and `59GEMSDOE` — and the account's own activity added more than that back). These entries must remain visibly flagged until their source prose is re-read; a changed SHA alone does not prove a description false. A census refresh republishes the *API* fields; it never rewrites prose, so expect this queue to move in both directions only when someone re-reads a repository.
- The independent live verifier completed **1,913 checks at the `15:06:10Z` snapshot**: 0 hard mismatches, 48 volatile drifts (fields GitHub recomputes or repositories pushed to while the audit ran), and zero entries in either direction of the API/published set difference. The numeric-token description lint checked all 145 entries with **0 unresolved items** and 42 documented exceptions; this is not semantic proof. The kind audit re-derived **145/145 with 0 disagreements and 0 unresolved**. An INCOMPLETE report (401/403/transport failure) is an access block, never a pass — that happened twice on 2026-10-11 (`verify_live` and `audit_descriptions` were re-run after the sandbox connection was restored).
- **A re-derivation caught six entries published as stubs after they had already become HTML entry points** (`GEMSDOE22`–`GEMSDOE27`, `IRR-138`): `contents/index.html?ref=<snapshot head>` returns HTTP 200 for all six at the recorded snapshot heads, so the stored label was false when published. Re-derive `kind` every pass — never trust a stored value. See `IRR-127`–`IRR-138` in `VERIFICATION.md`.
- **Protocol files exist and are binding.** [`TASKS.md`](TASKS.md) holds the claimable queue (claim one task per session, commit the claim alone, push immediately); [`FLAGGED.md`](FLAGGED.md) records fields that cannot be verified officially and items needing a human decision; [`HANDOFF.md`](HANDOFF.md) carries session context; `scripts/validate` is the mechanical gate (official source links per record, no unverified values, overlay-vs-published parity, counts, exclusions, and the per-record hand-review links in `VERIFICATION.md`). Run it before opening a PR.
- Local `npm run check` and Python syntax compilation pass. Playwright discovered 84 browser cases, but none ran: browser installation failed with `ECONNRESET` from `cdn.playwright.dev`. The PR workflow installs browsers; see README for the exact limitation. The `MasterSite` public-page fetch also hit sandbox TLS/SSL EOF, which does not prove the public site is down.

## 2. Hard repository rules

### Permanent exclusion

`ProjX` is publicly available upstream but is **permanently excluded from MasterSite by owner instruction**. Never add its title, repository URL, API URL, Pages URL, description, or metadata to the overlay, generated data, ledger, README counts, or exports. Keep API account totals unchanged and apply the exclusion after reading the official account API. The generator asserts that listed plus excluded Pages repositories balance to the account's Pages count.

### Unreachable repositories

`JobSearchSF`, `MALTA`, `MALTA-LAWS`, and `MALTA2` returned HTTP 404 in the latest live audit. Keep them in the frozen `unreachable` section of `data/sites.js`, `VERIFICATION.md`, and the UI's Unreachable panel with their last verified values. Do not silently delete them or infer whether they were intentionally retired; only the owner can resolve that. Recheck their official endpoints during a refresh.

## 3. Source and claim policy

- Use GitHub's official REST API for account/repository metadata, Pages settings/status, configured publish path, and default-branch commits. `verify_live.py` is the independent snapshot check.
- Curated titles, categories, descriptions, and flags belong in `tools/overlay.json`. Base every factual phrase on repository-owned README/source files, preferably at the current default-branch head. Record the exact source path, full commit SHA, and reproducible official endpoint in `verifiedBasis`.
- Keep summaries brief and conservative. Do not infer behavior from a repository name, badge, topic, or a root `index.html`; do not convert a claim in project prose into an independently established result. If repository files conflict, retain the caveat and add a reproducible irregularity rather than smoothing it over.
- A `verifiedAtSha` value must be a 7–40 character lowercase commit SHA. The generator accepts full SHAs and compares them with the current head (including supported short-prefix stamps). Before carrying a short stamp, verify the referenced commit resolves and explain why the intervening changes do not affect the description. A matching SHA is provenance, not proof that each sentence is correct.
- When a description is re-read, update `description`, `lastVerified`, `verifiedBasis`, and `verifiedAtSha` together. Entries touched in one pass should share a pass-completion timestamp. If source content changes materially, log the correction in `descriptionNotes` and add an `IRR` record when useful for future review.
- Never claim “zero hallucinations,” exhaustive verification, site uptime, interactivity, or last site use. Say what the source supports and disclose what was not tested.

## 4. Data and audit workflow

Run from the repository root:

```bash
python3 tools/build_data.py
python3 tools/export_site_records.py
python3 tools/build_sites_md.py
python3 tools/verify_live.py
python3 tools/audit_provenance.py
python3 tools/audit_kind.py
rm -rf tools/.readme-cache
python3 tools/audit_descriptions.py
npm run check
python3 -m py_compile tools/build_data.py tools/build_verification.py \
  tools/audit_descriptions.py tools/audit_kind.py tools/verify_live.py \
  tools/audit_provenance.py
npm test
python3 tools/build_verification.py
```

Run `build_verification.py` **after** the audit commands so the generated ledger cites reports for the same snapshot. Its audit-status table distinguishes completed, stale, incomplete, authorization-blocked, and rate-limit-blocked reports. Re-read any `PROSE-STALE` entry whose description will be presented as current; never clear the queue by changing only its SHA. If a repository moves during the pass, refresh and rerun the independent checks. `verify_live.py` mismatches are not repaired by hand in generated data—refresh the generator and recheck. HTTP 401 is an authorization failure, not a repository mismatch or a missing README; reconnect GitHub and rerun. HTTP 403 whose body identifies an API rate limit is an access block, not 403 field drift; rerun after the documented reset rather than treating it as a data mismatch.

- `tools/build_sites_md.py` renders `SITES.md`, the plain one-row-per-site master list (live link, sourced description, creation date, last default-branch commit, description stamp, official review endpoints). It reads `data/sites.js` and writes nothing else; rerun it after **every** refresh, because `scripts/validate` §L fails when it does not match the published snapshot, when a published site has no row, or when a row lacks its official Pages API link. It never invents a value: a missing date prints as `—`, never as a guess.
- `tools/verify_live.py` is read-only and compares API fields to the generated snapshot.
- `tools/audit_provenance.py` is read-only and audits the *citations* rather than the fields: for every published entry it re-resolves each recorded SHA (`verifiedAtSha`, `firstCommitSha`, `lastCommitSha`, `headSha`) through `GET /repos/{owner}/{repo}/commits/{sha}`, re-issues every `api.github.com` URL cited inside that entry's own `verifiedBasis` (README reads must return 200; the cited `index.html` read must agree with the entry's `kind`; a cited root listing must contain `index.html` when `kind` is `app`; a cited `/pages` read must report the published `pagesUrl`), and re-checks the description's numeric tokens against the README at the recorded provenance SHA — the SHA the record actually claims — instead of at the head. It writes `tools/last_provenance_audit.json` plus a per-entry hand-review report in `reports/provenance/`. Reproducing a citation is **not** proof that a sentence is true or current; a 401/403/transport failure aborts the run and is reported INCOMPLETE, never as a pass. It never writes `data/sites.js`. `tools/build_verification.py` reads `last_provenance_audit.json` and renders its run state (complete — with the per-entry `reports/provenance/` link when the file exists; stale; incomplete; access-blocked, parsing the HTTP code out of `accessBlockReason`; not available) as the fourth row of the ledger's §4b audit-status table, and `scripts/validate` §B fails closed when that row is missing (T-015/T-018).
- `tools/audit_kind.py` is read-only. HTTP 200 at the configured `index.html` path means HTML entry point; HTTP 404 means no entry point. Other status codes are unresolved, **not** stubs, and the audit must fail so an API problem cannot silently change a classification.
- `tools/audit_descriptions.py` is read-only. It checks whether numeric tokens in each description occur in that repository's README at the snapshot head. This is only a lint: it cannot establish what a number means or validate non-numeric claims. Any exceptions must be individually justified in `acceptedDescriptionExceptions`; do not add exceptions just to silence a finding.
- `tools/scheduled_audit.py` is the budgeted scheduled runner (`T-022`, workflow `.github/workflows/audit-schedule.yml`, daily 07:23 UTC plus manual dispatch). It runs a **weekday subset** of the four audits inside a hard request ceiling (`--budget` 900 plus a `--reserve` 60 that is never planned for spending) because GitHub documents the built-in Actions `GITHUB_TOKEN` at **1,000 requests/hour/repository** (<https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api>) while a full pass measured **2,151 requests**. It reports one verdict per audit (`PASS` / `FINDINGS` / `INCOMPLETE` / `ERROR` / `NOT-RUN`) and one outcome per run (`CLEAN` / `FINDINGS` / `INCOMPLETE` / `PARTIAL`); **`NOT-RUN` means the audit was not checked and `PARTIAL` is never a pass**, and only a clean pass of a four-audit run closes the tracking issue. It writes only into `.work/scheduled-audit/` (the report and one log per audit) and never to a published file (`data/sites.js`, `SITES.md`, `VERIFICATION.md`, `README.md` are untouched) — but each audit tool rewrites its own tracked `tools/last_*.json` report, so a **local** run leaves those dirty (revert them unless you mean to publish that run); the workflow's throwaway checkout discards them. Measured per-tool costs and the arithmetic behind the slots are preserved in [`reports/scheduled-audit/`](reports/scheduled-audit/); `audit_provenance` alone measured 904 requests against 840 spendable, so its slot reports `NOT-RUN`/`PARTIAL` until the budget is raised or an owner-provided larger token exists (README Known Limitations, T-023). Offline gates: `python3 tools/scheduled_audit.py --self-test` and `tests/test_scheduled_audit.py`, both wired into `.github/workflows/test.yml`. The earlier `weekly-audits.yml` all-four weekly run is **retired** (T-016): it ran the whole suite in one job, which the measured 2,151-request cost cannot fit inside the documented 1,000/hour token, so it would abort mid-pass with an HTTP 403 on every run.
- `audit_descriptions.py` caches fetched READMEs in `tools/.readme-cache`; clear that directory before relying on fresh source content. `audit_provenance.py` shares that cache through identical keys (`<repo>-<sha[:40]>.md`) and is content-addressed by SHA, so a cached file for a commit SHA is safe to reuse; the same rule as above applies when a ref is a branch name instead of a SHA.
- The generated `data/sites.js` and `VERIFICATION.md` must not be hand-edited. Edit the overlay and rerun their generators.

If GitHub API access is unavailable, `python3 tools/build_data.py --overlay-only` can render curated narrative fields into the existing snapshot without network access. It cannot add repositories or refresh API fields, and it cannot see commits since the snapshot. Do not present an overlay-only render as a fresh API audit or publish it as a replacement for a full build.

**Pages build-health re-check cadence (T-005).** On every refresh or health pass, re-read
`GET /repos/{owner}/{repo}/pages` for each entry whose `pagesStatus` is not `built` (currently
`GEMSDOE53`) and record the timestamped result in `FLAGGED.md` (FL-05) with the repository's
`pushed_at` beside it — a status that is unchanged with no new push needs no data regeneration,
and FL-05 must not be cleared while the API still reports `errored`. A recovery to `built`
changes `counts.pagesBuilt` and requires a full `build_data.py` refresh. Also spot-check
`pushed_at` on spot-touched repositories: a head that moved after the snapshot makes the
published `proseStale` flag out of date even when the prose was correctly re-read at the
snapshot head (see FL-14).

## 5. Documentation and test expectations

- Update the **current** README snapshot counts, audit results, unresolved queue, and limitations after a final refresh. Historical pass notes should be clearly dated and kept separate from current claims.
- Regenerate `VERIFICATION.md`; it contains the per-entry dates, SHAs, live/repository/API/settings links, exclusions, unreachable records, and irregularity register.
- Run `npm run check` and the Playwright suite when browser binaries are available. `.github/workflows/test.yml` installs Chromium, Firefox, and WebKit and runs the suite on pull requests. A sandbox browser-download failure is a blocked test, not a pass; report it accurately.
- The deployed app is static (`index.html`, CSS, JavaScript, and `data/sites.js`). Do not hardcode repository lists in UI markup/scripts.
- Preserve the table DOM contract asserted by `tests/directory.spec.js`: fixed cell count/order, row repository slug, Pages status position, and matching empty-state colspan. Responsive layout should remain CSS-driven.
- Density is a local reading preference, not a filter or URL parameter. Keep URL state limited to the documented search/category/type/prose/sort/view fields, and keep JSON/CSV output independent of density. Family grouping (`tools/families.json`, rendered by the grid view only) follows the same rule: a per-browser preference that never enters the URL, never changes the table's nine-cell rows, and never infers membership from a repository name — every member's curated description must document the family's project or competition. `scripts/validate` (section K) enforces that the published `family` fields, `MASTERDATA.families` and `counts.families` agree with the curated member list, and its `nameToken`/`ungroupedByDesign` coverage warning reports any published site whose name matches a family string without being curated in (or deliberately excluded), so a newly published lane cannot sit ungrouped unnoticed.

For the latest counts, status, source limits, and remaining review work, see [`README.md`](README.md).
