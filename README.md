# MasterSite

The **master list and directory of the GitHub Pages sites published under** [`buffedlizard55-lab`](https://github.com/buffedlizard55-lab) (with a verified audit of [`kanlerxz87-cyber`](https://github.com/kanlerxz87-cyber)) — generated entirely from official GitHub REST API reads, with zero manual data entry and zero hallucinations. One repository is deliberately unpublished by owner request, and one previously listed site is frozen as unreachable because it no longer exists upstream.

**Live Directory:** <https://buffedlizard55-lab.github.io/MasterSite/>

---

## Audit status — 2026-09-17 (`2026-09-17T21:47:46Z`)

| Metric | Value |
|---|---|
| GitHub Pages sites published in the directory | **38** |
| Interactive apps / documentation stubs | **33 / 5** |
| Pages builds reporting `built` | **38 / 38** |
| Commits audited across the listed repositories | **1,503** |
| Public repositories on the account (API) | **39** |
| Pages sites on the account (API) | **39** |
| Permanently excluded repositories | **1** (`ProjX`, owner directive 2026-09-12) |
| Unreachable entries (needs owner review) | **1** (`JobSearchSF` — HTTP 404) |
| Irregularities registered | **23** (`IRR-01` … `IRR-23`) |
| Categories | **6** — Travel & Korea Trip (11), Sports Data & Scoreboards (11), Markets & Trading Research (8), SF Local Guides (6), Science & ML Research (1), Directory & Meta (1) |

**What changed since the 2026-09-16 audit** (every item re-verified line by line against the API):

- **4 new Pages sites added:** `KalshiPaperSim`, `NBAInjuryReport`, `SFWeather`, `StockPaperSim` — all created on 2026-09-17, all `built`.
- **1 entry moved to *Unreachable*:** `JobSearchSF` returns **HTTP 404** on the repository API and no longer appears in the account's public repository list. Its last verified values are preserved rather than deleted; its live link is expected to be dead. See [Unreachable entries](#unreachable-entries-needs-owner-review).
- **8 entries updated** with new default-branch commits (+167): `GEMSDOE` 77→141, `TradingViewTheLeap` 10→51, `DrugAnalysis` 52→77, `TinoLunchSpecial` 52→64, `BathTubOverflowSF` 46→58, `NFLInjuryReport` 62→69, `ScheduleFreeTime` 20→24, `MasterSite` 12→14.
- **26 entries re-verified byte-identical** (same latest SHA, same commit count).
- **4 stale descriptions corrected** where a repository's README no longer supported the published wording — see [VERIFICATION.md § 4](VERIFICATION.md#4-line-by-line-description-verification).
- **The data is now generated, not hand-maintained:** `tools/build_data.py` reads the API and writes `data/sites.js`; `tools/build_verification.py` renders `VERIFICATION.md` from that data. Only narrative prose is hand-authored, in `tools/overlay.json`.

---

## Directory Overview

For each of the **38 GitHub Pages sites** in the directory:

- **Live Site Link** & **Repository Link**
- **Sourced Brief Description** — extracted line by line from the repository's own `README.md` and published file structure
- **Created Date** — GitHub `created_at`, with the first-commit timestamp and SHA shown alongside
- **Last Updated Date** — newest committer timestamp on the default branch, with the latest commit SHA, plus `pushed_at`
- **GitHub Pages Status & Build Source** — all 38 reporting `built`; 37 publishing from `main /` and 1 from `main /docs`
- **Total Commits on the Default Branch**, repository size, and app-vs-stub classification
- **Official Source Links for Manual Review** — live URL, repository, Pages API JSON, commits API, and Pages settings
- **Per-entry audit flags** and a **23-entry flagged irregularities register** (`IRR-01` … `IRR-23`)

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
| [`data/sites.js`](data/sites.js) | **Generated** verified dataset — 38 sites, 1 unreachable entry, 23 irregularities, 2 audited accounts, methodology |
| [`tools/overlay.json`](tools/overlay.json) | Hand-authored narrative: titles, categories, descriptions, flags, the irregularity register, the permanent exclusion list |
| [`tools/build_data.py`](tools/build_data.py) | **Generator** — reads the official GitHub API and writes `data/sites.js` |
| [`tools/build_verification.py`](tools/build_verification.py) | **Generator** — renders `VERIFICATION.md` from `data/sites.js` |
| [`AGENTS.md`](AGENTS.md) | Standing maintenance instructions for future sessions, including the permanent repository exclusion |
| [`VERIFICATION.md`](VERIFICATION.md) | **Generated** line-by-line audit ledger with official endpoints, commit SHAs and reproduction commands |

### Refreshing the directory

```bash
export GITHUB_TOKEN=...                  # optional, raises the rate limit from 60 to 5,000 req/h
python3 tools/build_data.py              # reads api.github.com, rewrites data/sites.js
python3 tools/build_verification.py      # rewrites VERIFICATION.md from the new data
```

Every timestamp, SHA, commit count, Pages status, build source and size in the output comes from an API read at that moment — nothing is carried over from memory. Repositories that vanish are moved into the `unreachable` list instead of disappearing.

---

## Verification & Integrity Policy

1. **Zero Hallucinations** — every field is read from `api.github.com` or from the repository's own files. Where a claim could not be re-verified it was removed rather than restated (for example, `TradingViewTheLeap`'s "203-check verifier" and `GEMSDOE`'s "19/19 rules" figures no longer appear in those repositories' READMEs and are no longer published here).
2. **Autonomous Execution** — no manual data entry, no owner prompts during the audit.
3. **Transparent Irregularity Reporting** — every anomaly is catalogued with the endpoint needed to reproduce it, ordered by severity.
4. **Independent Manual Review** — every row links to the live site, the repository, the Pages API record, the commits API and the Pages settings page.
5. **Nothing Is Silently Deleted** — excluded and unreachable repositories are named, explained and preserved with their last verified values.

---

## Repository Exclusions — Standing Instructions for Future Sessions

One repository on the account is **permanently excluded** from this site. Do not list it, link it, count it, or export it — in any future session, regeneration, or refresh of this directory.

| Excluded repository | Status | Instruction |
|---|---|---|
| `ProjX` | Still live on GitHub; intentionally unpublished **here** since 2026-09-12 by owner request | **Never add it back** to `data/sites.js`, the `VERIFICATION.md` ledger table, README counts, or the JSON/CSV exports. No live link, API endpoint or Pages URL for it is printed anywhere in this repository. Full rationale in [VERIFICATION.md § 2a](VERIFICATION.md#2a-repository-exclusions-deliberately-omitted). |

Because of this exclusion the directory shows **38** sites while the GitHub API reports **39** public Pages repositories. That mismatch is correct and expected: keep the account-level totals (`publicRepos: 39`, `pagesSites: 39`) at their verified API values and filter excluded names *after* the API read, instead of lowering those totals. `tools/build_data.py` applies the `excluded` list from `tools/overlay.json` automatically.

---

## Unreachable Entries — Needs Owner Review

| Repository | Last verified | What happened | Owner action |
|---|---|---|---|
| `JobSearchSF` | `f68c452`, 2026-09-16T19:37:41Z, 68 commits | `GET /repos/buffedlizard55-lab/JobSearchSF` returns **HTTP 404** and the repository is absent from the account's 39-repository public list, so it was deleted or made private. Its Pages site is therefore no longer served. | **Restore it** (undelete / make public) so it can be re-listed, **or confirm it should stay retired** and the frozen entry can be dropped. Flagged as `IRR-01` (critical). |

The entry stays visible in the site's *Unreachable — Needs Owner Review* panel and in `VERIFICATION.md` § 2b with every value it last verified, plus the three commands that reproduce the 404.

---

## Known Limitations

- **Live page bodies are not re-fetched over HTTP.** The audit environment can reach `github.com` / `api.github.com` but not `*.github.io`, so liveness rests on two API facts — Pages status `built` and a real `index.html` at the published path — rather than an HTTP 200 on the rendered page. Every entry still links to its live site for manual review.
- **Descriptions are README-sourced and can lag.** A push that rewrites a README leaves the wording behind until the next refresh. The generator re-reads every README whose commit count moved, and `IRR-20` documents the residual risk.
- **Timestamps are a point-in-time read.** Several repositories were still receiving pushes while the audit ran (`IRR-23`); re-run the generator for a fresh snapshot.
- **`kanlerxz87-cyber` contributes nothing to audit.** The account exists and was verified, but holds 0 public repositories, so there is nothing to list from it.
- **Repository size is GitHub's own asynchronously-recomputed field**, which is why several entries show size moves that do not line up with their commit deltas (`IRR-04` … `IRR-06`).
