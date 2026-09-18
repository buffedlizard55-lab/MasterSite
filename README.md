# MasterSite

The **master list and directory of the GitHub Pages sites published under** [`buffedlizard55-lab`](https://github.com/buffedlizard55-lab) (with a verified audit of [`kanlerxz87-cyber`](https://github.com/kanlerxz87-cyber)) — generated entirely from official GitHub REST API reads, with zero manual data entry and zero hallucinations. One repository is deliberately unpublished by owner request, and one previously listed site is frozen as unreachable because it no longer exists upstream.

**Live Directory:** <https://buffedlizard55-lab.github.io/MasterSite/>

---

## Audit status — 2026-09-18 (`2026-09-18T22:49:24Z`)

| Metric | Value |
|---|---|
| GitHub Pages sites published in the directory | **40** |
| Interactive apps / documentation stubs | **35 / 5** |
| Pages builds reporting `built` | **40 / 40** |
| Commits audited across the listed repositories | **1,902** |
| Public repositories on the account (API) | **41** |
| Pages sites on the account (API) | **41** |
| Repositories withheld, each with a stated reason | **1** (`ProjX` — permanently excluded by owner request) |
| Unreachable entries (needs owner review) | **1** (`JobSearchSF` — HTTP 404, re-confirmed) |
| Irregularities registered | **31** (`IRR-01` … `IRR-31`) |
| Categories | **7** — Travel & Korea Trip (11), Sports Data & Scoreboards (11), Markets & Trading Research (8), SF Local Guides (6), Directory & Meta (2), Science & ML Research (1), Gaming & Guides (1) |

The generator now proves its own arithmetic: `listed + withheld = Pages sites on the account` is asserted at build time, and every withheld repository is named with its reason in `data/sites.js → counts.unlisted`. There is no silent gap.

**What changed since the 2026-09-17 audit** (every item re-verified line by line against the API):

- **2 new Pages sites added:** `WoWForever` — created **2026-09-18T20:11:30Z**, Pages `built`, publishing from `main /`, and `Elections` — created **2026-09-18T22:42:36Z**, *two minutes after this snapshot's data was first generated*. The 2026-09-17 audit could not have listed either. Both were still being pushed to while the audit ran (`IRR-24`, `IRR-31`).
- **`Elections` is listed from its file listing alone.** Its entire contents are one 11-byte README reading `# Elections`. It satisfies every inclusion rule so it is listed, but its description says nothing about what the site is *for*, because nothing in the repository does. Inventing a purpose would have broken the one rule this project keeps.
- **`StockPaperSim` reclassified from stub to app, and its description rewritten.** It was published on 2026-09-17 as *"a single initial commit containing only a 15-byte README.md"*. It now has **67 commits**, an ~12 MB repository, and a multi-page site. The old wording was true when written and false by this audit — the single most serious error found, registered as `IRR-25`.
- **10 entries updated** with new default-branch commits: `NBAInjuryReport` 81→149, `SFWeather` 58→112, `DrugAnalysis` 77→101, `TradingViewTheLeap` 51→85, `KalshiPaperSim` 5→70, `StockPaperSim` 1→67, `GEMSDOE` 141→162, `NFLInjuryReport` 69→75, `ScheduleFreeTime` 24→31, `MasterSite` 14→16.
- **29 entries re-verified byte-identical** (same latest SHA, same commit count).
- **5 stale descriptions corrected**, not 1: `StockPaperSim` (false classification), `KalshiPaperSim` (every quoted counter had moved — `IRR-26`), `NBAInjuryReport` (test counts 188/52 no longer existed anywhere in the repository — `IRR-27`), `NFLInjuryReport` (omitted a documented missed-alert incident — `IRR-28`) and `TradingViewTheLeap` (README pointed at a superseded capture file — `IRR-29`).
- **`JobSearchSF` re-confirmed gone:** still HTTP 404, still `total_count 0` in the search API, still absent from the account's 41-repository public list.
- **Two read-only verifiers added:** `tools/verify_live.py` re-reads every API-derived field of every entry (517 checks) and `tools/audit_descriptions.py` checks every numeric claim in a description against the repository's own README. Neither writes the dataset. See [Verification & Integrity Policy](#verification--integrity-policy).

---

## Directory Overview

For each of the **40 GitHub Pages sites** in the directory:

- **Live Site Link** & **Repository Link**
- **Sourced Brief Description** — extracted line by line from the repository's own `README.md` and published file structure
- **Created Date** — GitHub `created_at`, with the first-commit timestamp and SHA shown alongside
- **Last Updated Date** — newest committer timestamp on the default branch, with the latest commit SHA, plus `pushed_at`
- **GitHub Pages Status & Build Source** — all 40 reporting `built`; 39 publishing from `main /` and 1 from `main /docs`
- **Total Commits on the Default Branch**, repository size, and app-vs-stub classification
- **Official Source Links for Manual Review** — live URL, repository, Pages API JSON, commits API, and Pages settings
- **Per-entry audit flags** and a **30-entry flagged irregularities register** (`IRR-01` … `IRR-30`), ordered by severity

---

## User Interface Features

- **Instant Search & Multi-Filter** — search by title, repository, description, category or flags, combined with category and type filter chips showing live counts.
- **Dual View Modes** — responsive **card grid** and a dense **table view**.
- **Sort** by last updated, date created, name or commit count.
- **Site Inspector Modal** — full telemetry, timestamps, commit SHAs, size, branch, Pages source and the raw verified JSON record for any entry.
- **Unreachable Panel** — retired entries kept visible with their last verified state and the exact commands that reproduce the 404.
- **Severity-Ordered Irregularities** — critical → warn → info, each with a reproduction endpoint.
- **Client-Side Export** — download the verified master list as JSON or CSV in one click (CSV marks retired rows instead of dropping them).
- **Accessibility** — skip link, ARIA live regions, `aria-pressed` on toggles, full keyboard support, Esc to close the modal.
- **No build step, no dependencies, no framework** — plain `index.html` + `styles.css` + `app.js` plus one data file.

---

## File Architecture

| File | Purpose |
|---|---|
| [`index.html`](index.html) | Semantic, accessible directory markup (grid, table, panels, inspector modal) |
| [`styles.css`](styles.css) | Responsive design system — CSS custom properties, cards, tables, badges |
| [`app.js`](app.js) | Zero-dependency application logic (search, filter, sort, export, inspector, toast) |
| [`data/sites.js`](data/sites.js) | **Generated** verified dataset — 40 sites, 1 unreachable entry, 31 irregularities, 2 audited accounts, methodology |
| [`tools/overlay.json`](tools/overlay.json) | Hand-authored narrative: titles, categories, descriptions, flags, the irregularity register, the permanent exclusion list |
| [`tools/build_data.py`](tools/build_data.py) | **Generator** — reads the official GitHub API and writes `data/sites.js` |
| [`tools/build_verification.py`](tools/build_verification.py) | **Generator** — renders `VERIFICATION.md` from `data/sites.js` |
| [`AGENTS.md`](AGENTS.md) | Standing maintenance instructions for future sessions, including the permanent repository exclusion |
| [`VERIFICATION.md`](VERIFICATION.md) | **Generated** line-by-line audit ledger with official endpoints, commit SHAs and reproduction commands |
| [`tools/verify_live.py`](tools/verify_live.py) | **Read-only verifier** — re-reads every API-derived field of every entry and reports ok / mismatch / drift. Never writes the dataset |
| [`tools/audit_descriptions.py`](tools/audit_descriptions.py) | **Read-only verifier** — checks every numeric claim in a description against the repository's own README |

### Refreshing the directory

```bash
export GITHUB_TOKEN=...                  # optional, raises the rate limit; 5,250 requests/h were
                                         # available unauthenticated in this audit sandbox
python3 tools/build_data.py              # reads api.github.com, rewrites data/sites.js
python3 tools/build_verification.py      # rewrites VERIFICATION.md from the new data

# then verify what you just generated, independently of the generator:
python3 tools/verify_live.py             # 517 field checks — expect 0 hard mismatches
python3 tools/audit_descriptions.py      # every numeric claim vs the repo's own README
```

Every timestamp, SHA, commit count, Pages status, build source and size in the output comes from an API read at that moment — nothing is carried over from memory. Repositories that vanish are moved into the `unreachable` list instead of disappearing.

`verify_live.py` separates two kinds of difference. A **hard mismatch** means the committed value and the live value disagree with no explanation, and is a defect: re-run the generator. **Drift** means the field is one GitHub recomputes asynchronously (`size`, `pushed_at`, `updated_at`) or the repository was pushed to *after* the snapshot was taken — expected, and folded in by the next refresh. The 2026-09-18 audit finished at 0 hard mismatches across 517 checks.

---

## Verification & Integrity Policy

1. **Zero Hallucinations.** Every field is read from `api.github.com` or from the repository's own files. Where a claim could not be re-verified it was **deleted or corrected, never softened** — for example `TradingViewTheLeap`'s "203-check verifier" and `GEMSDOE`'s "19/19 rules" figures no longer appear in those repositories and were removed rather than restated, and this audit removed `DrugAnalysis`'s superseded "1,038 core rows".
2. **Autonomous Execution.** No manual data entry, no owner prompts during the audit. The only hand-authored content is narrative prose in `tools/overlay.json`.
3. **Independent Re-Verification, Not Restatement.** `tools/verify_live.py` re-reads every API-derived field of every entry straight from GitHub and prints each one as ok, mismatch or drift. It is deliberately read-only — it reports, it never repairs. `tools/audit_descriptions.py` checks each description's numeric claims against the repository's own README. Run both after any refresh:
   ```bash
   python3 tools/verify_live.py           # 530 field checks across 40 entries + both accounts
   python3 tools/audit_descriptions.py    # every numeric claim vs the repo's own README
   ```
4. **Transparent Irregularity Reporting.** Every anomaly is catalogued with the endpoint needed to reproduce it, ordered by severity (`critical` → `warn` → `info`). This audit added seven and revised five.
5. **Nothing Is Silently Deleted.** Excluded and unreachable repositories are named, explained and preserved with their last verified values.
6. **Corrections Are Recorded, Not Hidden.** When a published description turns out to have been wrong, the entry is fixed *and* the mistake is registered with what it said, what it should have said, and how it was caught — see `IRR-25` through `IRR-29`.

---

## Repository Exclusions — Standing Instructions for Future Sessions

One repository on the account is **permanently excluded** from this site. Do not list it, link it, count it, or export it — in any future session, regeneration, or refresh of this directory.

| Excluded repository | Status | Instruction |
|---|---|---|
| `ProjX` | Still live on GitHub; intentionally unpublished **here** since 2026-09-12 by owner request | **Never add it back** to `data/sites.js`, the `VERIFICATION.md` ledger table, README counts, or the JSON/CSV exports. No live link, API endpoint or Pages URL for it is printed anywhere in this repository. Full rationale in [VERIFICATION.md § 2a](VERIFICATION.md#2a-repository-exclusions-deliberately-omitted). |

Because of this exclusion the directory shows **40** sites while the GitHub API reports **41** public Pages repositories. That mismatch is correct and expected: keep the account-level totals (`publicRepos: 41`, `pagesSites: 41`) at their verified API values and filter excluded names *after* the API read, instead of lowering those totals. `tools/build_data.py` applies the `excluded` list from `tools/overlay.json` automatically, records every withheld repository with its reason in `counts.unlisted`, and **asserts at build time** that `listed + withheld == pagesSites` so a silent gap is impossible.

---

## Unreachable Entries — Needs Owner Review

| Repository | Last verified | What happened | Owner action |
|---|---|---|---|
| `JobSearchSF` | `f68c452`, 2026-09-16T19:37:41Z, 68 commits | Re-confirmed 2026-09-18: `GET /repos/buffedlizard55-lab/JobSearchSF` returns **HTTP 404** and the repository is absent from the account's 40-repository public list, so it was deleted or made private. Its Pages site is therefore no longer served. | **Restore it** (undelete / make public) so it can be re-listed, **or confirm it should stay retired** and the frozen entry can be dropped. Flagged as `IRR-01` (critical). |

The entry stays visible in the site's *Unreachable — Needs Owner Review* panel and in `VERIFICATION.md` § 2b with every value it last verified, plus the three commands that reproduce the 404.

---

## Known Limitations

These are the real obstacles, stated plainly. Several of them are the reason a claim can be "verified" and still be wrong tomorrow.

1. **The prose is the fragile part, not the numbers.** Every timestamp, SHA, commit count and Pages status on this site is read from `api.github.com` at generation time and re-checked by `tools/verify_live.py`. The *descriptions* are written prose checked against a repository's README, and nothing forces them to be re-read. This audit found five that had gone stale and one that had become flatly false (`IRR-25`, `IRR-30`). Treat any description older than the current audit date as unverified.
2. **A number appearing in a README is not proof it is current.** `tools/audit_descriptions.py` narrows the search to descriptions containing tokens that no longer appear anywhere in the README. It caught `NBAInjuryReport`'s stale test counts but cannot catch a superseded figure that still sits in an old changelog section — which is exactly how `KalshiPaperSim`'s counters survived a refresh (`IRR-26`). Human or model re-reading is still required.
3. **Live page bodies are not fetched over HTTP.** Pages liveness rests on two API facts — status `built` and a real `index.html` at the published path — not an HTTP 200 on the rendered page. A site can be `built` and still render a blank page or a broken redirect. Every entry links to its live URL for one-click manual review.
4. **Repositories move faster than the audit.** Ten repositories gained 467 commits *between two consecutive daily audits*, and `TradingViewTheLeap` was pushed to again while this audit was mid-run. Timestamps and commit counts here are a point-in-time read of `2026-09-18T22:40:52Z` (`IRR-23`, `IRR-24`).
5. **`WoWForever` is hours old.** It was created `2026-09-18T20:11:30Z` and was still merging pull requests during the audit. Its numbers will be the first to be wrong.
6. **Repository size is GitHub's own asynchronously-recomputed field**, so size moves that do not line up with commit deltas are normal GitHub behaviour, not a data error (`IRR-04`–`IRR-06`). `GEMSDOE` alone is ~386 MB because competition rasters are committed as git parts, which will make clones slow and is close to the kind of growth GitHub's own guidance warns about.
7. **`kanlerxz87-cyber` contributes nothing to audit.** The account was verified to exist (`type: User`, created `2026-08-03T20:56:16Z`) but holds **0** public repositories, so there is nothing to list. If it ever publishes a Pages site, the generator picks it up automatically — the account list is hardcoded in `tools/build_data.py`, the per-account reads are not.
8. **One repository is permanently excluded by owner request** (`ProjX`), so the directory will always show one fewer site than the account-level API totals. That gap is deliberate; see [Repository Exclusions](#repository-exclusions--standing-instructions-for-future-sessions).
9. **`JobSearchSF` cannot be resolved from here.** It is HTTP 404 and absent from the account. Only the owner can say whether it should be restored or the frozen entry dropped (`IRR-01`).

---

## What Still Needs To Be Done

Ordered by what actually threatens the project's core promise. The first two are the ones worth doing next session.

| # | Task | Why it matters | Effort |
|---|---|---|---|
| 1 | **Re-read every description against its repository, by hand, once per audit.** Not a token grep — an actual read of each README's current status section against the published wording. | This is the only error class this audit found that materially misled a reader (`IRR-25`, `IRR-30`). The tooling narrows it; it cannot close it. 40 entries is a bounded, tractable job. | Medium |
| 2 | **Resolve `JobSearchSF` (`IRR-01`).** Owner decision: restore the repository, or confirm it is retired so the frozen entry can be dropped. | It is the only `critical` irregularity and it has now been open across three audits with no resolution path that a machine can take. | Owner only |
| 3 | **Add a `lastVerified` date per entry**, distinct from the dataset's `generated` timestamp, so a reader can see which descriptions were actually read this cycle and which were carried over. | Right now "verified" is ambiguous between "the API was read" and "the prose was checked". Making that explicit is cheap and removes the ambiguity permanently. | Low |
| 4 | **Fetch live pages over HTTP** to confirm each published URL really serves the expected page (not a blank, a 404 page or a redirect loop). Currently out of reach from the audit sandbox — see Limitation 3. | It is the difference between "GitHub says it built" and "it works". | Medium |
| 5 | **Move `GEMSDOE`'s ~386 MB of rasters out of git** (Git LFS or a release asset) and record the change. | Repository size is a real operational cost and the growth pattern is documented in `IRR-04`. | Medium |
| 6 | **Settle the `StockPaperSim` Pages source** with an owner action: switch Settings → Pages to `main`, `/docs`, then delete the root `index.html` redirect. | The repository documents that its own automation cannot do this (the API returns 403). It is a two-click fix that removes a redirect from every visitor's path. | Owner only |
| 7 | **Decide whether `HotelSeoulRoughdraft1` and `MLB-PBP`/`MLB-Live-PBP` should stay listed.** The draft duplicates `Itinerary-Korea` (`IRR-14`), and the two MLB viewers overlap. | A *directory* is more useful when it does not send readers to a superseded draft. This is a curation decision, not a data one. | Owner only |
| 8 | **Consider a weekly rather than daily refresh cadence**, or accept that each snapshot is a point-in-time read and label it as such in the UI (it already is, in the header). | 41 repositories, hundreds of commits a day, one repo created *during* this audit, and another pushed to mid-audit. Daily is achievable but the numbers are only ever briefly true. | Low |

