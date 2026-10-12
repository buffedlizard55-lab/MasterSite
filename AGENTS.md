# AGENTS.md — MasterSite Maintenance Instructions

Read this before refreshing data or changing the directory. The public directory is a generated snapshot, not a live uptime or usage monitor.

## 1. Scope and current snapshot

- Both accounts are queried. The current published snapshot is
  **`2026-10-12T02:09:11Z` (T-035/PR #73)**: 155 listed sites, 142 HTML entry
  points / 13 documentation stubs, 153 `built` / 2 `errored` at that read,
  11,797 default-branch commits, 147 irregularities, **56 prose-stale**, 70
  curated family members. Primary public census 156 = 155 + excluded ProjX;
  secondary public repositories 0. Four unreachable records remain frozen.
- Published `GEMSDOE67`/`GEMSDOE69` classifications and all three T-035 source
  rereads were retained when T-029 rebased. `GEMSDOE68` is still `stub` because
  no configured-path index existed at the recorded kind read, irrespective of
  its documented project purpose. Never infer purpose from names or HTML existence.
- The published audit layer completed: kind 155/155 with no disagreements,
  numeric lint 155/155 with one known `60GEMSDOE` finding, provenance 155/155
  and 1,118 checks with no hard findings, live fields 2,057 checks with no hard
  mismatches and 106 volatile drifts. Those are timestamped results, not current
  semantic accuracy, rendering, uptime, visits or last use. The stale queue is
  only cleared by rereading sources, not changing a SHA.
- Build metadata is not uptime. The published snapshot records `GEMSDOE53` and
  `GEMSDOE68` `errored`; later independent T-029 reads observed `GEMSDOE68`
  `built` at 04:03:58Z (FL-21 recovery), while GEMSDOE53 remained `errored` at
  04:03:37Z with unchanged pushed_at. Do not hand-edit the historical record.
- T-029 completed all six stages across seven bounded invocations/two actual
  quota resets ([historical staged report](reports/refresh/20261012T041123Z-v2-full-collection.md)):
  2,938 requests, final census 156/0 with no gaps, provenance 1,118 checks and
  live fields 2,049 checks / 0 hard / 80 drift. **No staged data was promoted.**
  Its old curation produced two legitimate kind blockers, now resolved by T-035
  (historical FL-23). Input changes intentionally invalidate that checkpoint.
- Code gates: **193 Python tests**, validator, JavaScript checks and compilation
  passed; **52 local desktop/mobile Chromium tests** passed with temporary
  runtime files, no dependency changes. Full implementation Chromium/Firefox/WebKit
  [CI passed](https://github.com/buffedlizard55-lab/MasterSite/actions/runs/38198039418).
  Require the latest PR's actual green check before merging.
- Protocol is binding: claim one task, commit/push the claim alone; review TASKS,
  FLAGGED and HANDOFF. Never edit shared generated datasets by hand, remove frozen
  records, ignore permanent exclusions or treat an INCOMPLETE audit as passing.
  Every active record must retain official review links and supported dates.

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

**Preferred full refresh: [`tools/refresh.py`](tools/refresh.py), T-029.** Start with
`python3 tools/refresh.py --checkpoint .work/refresh --budget 900 --reserve 60`,
continue the same collection with `--resume` only when its recorded quota/access
window permits, and explicitly add `--publish` to promote a completed eligible
collection. This stages the builder, all four independent audits and a final
both-account public census without changing published files on a pause. It has a
hard per-invocation request ceiling, independent phase response namespaces, original
API read timestamps, pinned commit pagination, integrity/age/input gates and a
checkpoint lock. See [`tools/REFRESH.md`](tools/REFRESH.md) for commands, exit codes,
publication gates and limitations. Never hand-edit a checkpoint to bypass a gate.
After promotion, rebuild `data/sites/`, `SITES.md`, `master-list.html`, and
`VERIFICATION.md`, sync the README, and run `scripts/validate`. Replayed responses
keep their original read times; collection completion is not fresh verification
of every field. This does not clear prose staleness or persist checkpoints across
scheduled Actions jobs.

The individual tools below remain available (but do not themselves provide the
full coordinator's continuation path). Run from the repository root:

```bash
python3 tools/build_data.py
python3 tools/export_site_records.py
python3 tools/build_sites_md.py
python3 tools/build_master_list.py
python3 tools/verify_live.py
python3 tools/audit_provenance.py
python3 tools/audit_kind.py
rm -rf tools/.readme-cache
python3 tools/audit_descriptions.py
npm run check
python3 -m py_compile tools/build_data.py tools/build_verification.py \
  tools/build_sites_md.py tools/build_master_list.py \
  tools/audit_descriptions.py tools/audit_kind.py tools/verify_live.py \
  tools/audit_provenance.py
npm test
python3 tools/build_verification.py
```

Run `build_verification.py` **after** the audit commands so the generated ledger cites reports for the same snapshot. Its audit-status table distinguishes completed, stale, incomplete, authorization-blocked, and rate-limit-blocked reports. Re-read any `PROSE-STALE` entry whose description will be presented as current; never clear the queue by changing only its SHA. If a repository moves during the pass, refresh and rerun the independent checks. `verify_live.py` mismatches are not repaired by hand in generated data—refresh the generator and recheck. HTTP 401 is an authorization failure, not a repository mismatch or a missing README; reconnect GitHub and rerun. HTTP 403 whose body identifies an API rate limit is an access block, not 403 field drift; rerun after the documented reset rather than treating it as a data mismatch. **Trust the `x-ratelimit-*` headers on the failing response, not `GET /rate_limit`:** on 2026-10-12 (session `arena-973e4afd`, T-035) real endpoints returned `x-ratelimit-remaining: 0` with `x-ratelimit-reset` giving the true retry time while `GET /rate_limit` concurrently reported `remaining: 5000, used: 0` for a different accounting window — two build attempts were wasted trusting the endpoint, and the token pool is shared across parallel sessions, so a fresh window can be consumed by someone else before your run starts. Check `x-ratelimit-remaining` on a real endpoint immediately before launching a full pass.

- `tools/build_sites_md.py` renders `SITES.md`, the plain one-row-per-site master list (live link, sourced description, creation date, last default-branch commit, description stamp, official review endpoints). It reads `data/sites.js` and writes nothing else; rerun it after **every** refresh, because `scripts/validate` §L fails when it does not match the published snapshot, when a published site has no row, or when a row lacks its official Pages API link. It never invents a value: a missing date prints as `—`, never as a guess.
- `tools/build_master_list.py` renders `master-list.html`, the **JavaScript-free** copy of the whole directory, and is the only page surface that survives JavaScript being off (crawlers, print, archive, `curl`, a failed `data/sites.js` request). It reads `data/sites.js` and makes **no network calls**, so it can neither invent a value nor spend the live-audit rate budget: one static block per published site carries the live link, repository, category, sourced description, created, last default-branch commit, recorded Pages build status, description stamp and that row's official endpoints. It **fails closed** — an empty required field, a `pagesUrl` that does not match the owner/repository pattern, a stranded `counts.unlisted` entry, a broken census balance, or any `<script>` in its own output aborts the run and writes nothing. Rerun it after **every** refresh: `scripts/validate` §M fails when the committed page drifts from the snapshot, loses a published site, drops a row's official links, renders an excluded repository, or gains a script or inline handler. The page is static by construction, so it needs no browser test; `tests/test_master_list.py` pins the guarantees offline.
- `scripts/validate` §N also checks the README's headline numbers for generated `data/sites.js` (site count, irregularity count, unreachable count, census stamp) against the snapshot, so prose cannot keep advertising a superseded census.
- `tools/verify_live.py` is read-only and compares API fields to the generated snapshot.
- `tools/audit_provenance.py` is read-only and audits the *citations* rather than the fields: for every published entry it re-resolves each recorded SHA (`verifiedAtSha`, `firstCommitSha`, `lastCommitSha`, `headSha`) through `GET /repos/{owner}/{repo}/commits/{sha}`, re-issues every `api.github.com` URL cited inside that entry's own `verifiedBasis` (README reads must return 200; the cited `index.html` read must agree with the entry's `kind`; a cited root listing must contain `index.html` when `kind` is `app`; a cited `/pages` read must report the published `pagesUrl`), and re-checks the description's numeric tokens against the README at the recorded provenance SHA — the SHA the record actually claims — instead of at the head. It writes `tools/last_provenance_audit.json` plus a per-entry hand-review report in `reports/provenance/`. Reproducing a citation is **not** proof that a sentence is true or current; a 401/403/transport failure aborts the run and is reported INCOMPLETE, never as a pass. It never writes `data/sites.js`. `tools/build_verification.py` reads `last_provenance_audit.json` and renders its run state (complete — with the per-entry `reports/provenance/` link when the file exists; stale; incomplete; access-blocked, parsing the HTTP code out of `accessBlockReason`; not available) as the fourth row of the ledger's §4b audit-status table, and `scripts/validate` §B fails closed when that row is missing (T-015/T-018).
- `tools/build_verification.py` also reads the committed `reports/scheduled-audit/*.json` history and renders §4c: the latest recorded run outcome, every audit's latest `PASS`/`FINDINGS`/`INCOMPLETE`/`ERROR`/`NOT-RUN` verdict, and the last explicit clean pass per audit. A `PARTIAL` run and a `NOT-RUN` result are never treated as a clean pass. The scheduled workflow is deliberately read-only, so a workflow artifact appears in §4c only after its exact `report.json` is preserved in that directory and the ledger is regenerated; a report whose `run.snapshot` differs from the current dataset is historical, not current.
- `tools/audit_kind.py` is read-only. HTTP 200 at the configured `index.html` path means HTML entry point; HTTP 404 means no entry point. Other status codes are unresolved, **not** stubs, and the audit must fail so an API problem cannot silently change a classification.
- `tools/audit_descriptions.py` is read-only. It checks whether numeric tokens in each description occur in that repository's README at the snapshot head. This is only a lint: it cannot establish what a number means or validate non-numeric claims. Any exceptions must be individually justified in `acceptedDescriptionExceptions`; do not add exceptions just to silence a finding.
- `tools/scheduled_audit.py` is the budgeted scheduled runner (`T-022`, workflow `.github/workflows/audit-schedule.yml`, daily 07:23 UTC plus manual dispatch). It runs a **weekday subset** of the four audits inside a hard request ceiling (`--budget` 900 plus a `--reserve` 60 that is never planned for spending) because GitHub documents the built-in Actions `GITHUB_TOKEN` at **1,000 requests/hour/repository** (<https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api>) while a full pass measured **2,151 requests**. It reports one verdict per audit (`PASS` / `FINDINGS` / `INCOMPLETE` / `ERROR` / `NOT-RUN`) and one outcome per run (`CLEAN` / `FINDINGS` / `INCOMPLETE` / `PARTIAL`); **`NOT-RUN` means the audit was not checked and `PARTIAL` is never a pass**, and only a clean four-audit pass with no nonvolatile review items closes the tracking issue. It writes only into `.work/scheduled-audit/` (the report and one log per audit) and never to a published file (`data/sites.js`, `SITES.md`, `VERIFICATION.md`, `README.md` are untouched) — but each audit tool rewrites its own tracked `tools/last_*.json` report, so a **local** run leaves those dirty (revert them unless you mean to publish that run); the workflow's throwaway checkout discards them. Measured per-tool costs and the arithmetic behind the slots are preserved in [`reports/scheduled-audit/`](reports/scheduled-audit/); `audit_provenance` alone measured 904 requests against 840 spendable, so its slot reports `NOT-RUN`/`PARTIAL` until the budget is raised or an owner-provided larger token exists (README Known Limitations, T-023). Offline gates: `python3 tools/scheduled_audit.py --self-test` and `tests/test_scheduled_audit.py`, both wired into `.github/workflows/test.yml`. `report.json` carries each result's `reviewItems`; `report.md` renders individual findings, hard mismatches, volatile drift values and provenance `{path}` templates with the recorded API source. The workflow copies that Markdown into the job summary and PR comment, and into the tracking issue when it opens/updates one. Nonvolatile review items (including placeholder citations) open/update the issue even when the audit verdict is `CLEAN`; volatile drift alone does not create an issue, but updates one that is already open. A clean four-audit run closes an existing issue only when no nonvolatile items remain; a `PARTIAL` run can open/update only when it actually reports a nonvolatile review item. Missing source URLs stay visibly missing. The earlier `weekly-audits.yml` all-four weekly run is **retired** (T-016): it ran the whole suite in one job, which the measured 2,151-request cost cannot fit inside the documented 1,000/hour token, so it would abort mid-pass with an HTTP 403 on every run.
- `audit_descriptions.py` caches fetched READMEs in `tools/.readme-cache`; clear that directory before relying on fresh source content. `audit_provenance.py` shares that cache through identical keys (`<repo>-<sha[:40]>.md`) and is content-addressed by SHA, so a cached file for a commit SHA is safe to reuse; the same rule as above applies when a ref is a branch name instead of a SHA.
- `tools/pages_status_guard.py` is the daily Pages status transition watch (`T-026`, same workflow as the coverage guard: `.github/workflows/census.yml`, 05:17 UTC). One read-only `GET /repos/{owner}/{repo}/pages` per listed entry (≈150 requests with the 1-second politeness floor), compared to the published `pagesStatus`. It fails loudly on any entry that is not live `built` — a transition in either direction (`built`→`errored` may take the site down; `errored`→`built` means the published record is stale), an entry that is `errored` even when it matches the snapshot, or HTTP 404 on a listed entry's Pages endpoint — and the workflow opens/updates a `pages-status` issue with the per-entry endpoint and UTC read time, closing it only when every entry is live `built` again. Exit 2 (rate limit, auth, transport) is a red run with **no verdict**, never a pass and never a finding. It never writes data; remediation is always §4. Offline gates: `python3 tools/pages_status_guard.py --self-test` (pass / transition / stable-non-built / pages-404 / recovery-stale / api-failure) and `python3 -m unittest tests.test_pages_status_guard -v` (14 tests), both wired into `.github/workflows/test.yml`.
- The generated `data/sites.js` and `VERIFICATION.md` must not be hand-edited. Edit the overlay and rerun their generators.

If GitHub API access is unavailable, `python3 tools/build_data.py --overlay-only` can render curated narrative fields into the existing snapshot without network access. It cannot add repositories or refresh API fields, and it cannot see commits since the snapshot. Do not present an overlay-only render as a fresh API audit or publish it as a replacement for a full build.

**Pages build-health re-check cadence (T-005).** On every refresh or health pass, re-read
`GET /repos/{owner}/{repo}/pages` for each entry whose `pagesStatus` is not `built` (currently
`GEMSDOE53` and `NFLInjuryReport`) and record the timestamped result in `FLAGGED.md` (FL-05,
FL-17) with the repository's
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
