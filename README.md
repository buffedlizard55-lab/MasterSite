# MasterSite

The **master list and directory of the GitHub Pages sites published under** [`buffedlizard55-lab`](https://github.com/buffedlizard55-lab) (with verified audit of [`kanlerxz87-cyber`](https://github.com/kanlerxz87-cyber)) — built strictly from official, verified sources with zero hallucinations, and with one repository deliberately unpublished by owner request (see [Repository Exclusions](#repository-exclusions--standing-instructions-for-future-sessions)).

**Live Directory:** <https://buffedlizard55-lab.github.io/MasterSite/>

---

## Directory Overview

For each of the **34 GitHub Pages sites published in this directory** (audited and verified via official GitHub REST API endpoints on **2026-09-15** — the account holds 35 Pages repositories in total; see [Repository Exclusions](#repository-exclusions--standing-instructions-for-future-sessions)):

- **Live Site Link** & **Repository Link**
- **Sourced Brief Description** (extracted line by line from each repo's `README.md` and live web app structure)
- **Created Date** (`created_at` timestamp + first-commit SHA verified within 1 second for every repository)
- **Last Updated Date** (newest committer timestamp on branch `main` + latest commit SHA + `pushed_at` tracking)
- **GitHub Pages Status & Build Source** (all 34 reporting `built`; 33 deploying from `main /` and 1 from `main /docs`)
- **Total Commits on Main** (exact commit count across the 34 listed repositories: 1143 total commits audited)
- **Official Source Links for Manual Review**: Live URL, GitHub Repo, Pages API JSON record, and Pages Settings
- **Detailed Flagged Irregularities Register**: 14 flagged discrepancies (`IRR-01` through `IRR-14`) documented transparently

---

## User Interface Features

- **Instant Search & Multi-Filter**: Search by title, repo name, description, category, or flags with real-time feedback.
- **Category & Type Pills**: Filter across 6 categories (*Travel & Korea Trip*, *Sports Data & Scoreboards*, *SF Local Guides*, *Markets & Trading Research*, *Science & ML Research*, *Directory & Meta*) and site types (*Interactive Apps* vs. *Doc Stubs*).
- **Dual View Modes**: Switch between responsive **Grid Cards View** and a compact **Dense Table View**.
- **Interactive Site Inspector Modal**: View detailed telemetry, timestamps, commit SHAs, size, branch, and raw verified JSON for any site.
- **Client-Side Export**: Download the verified master list as `JSON` or `CSV` with one click.
- **Copy Utilities & Accessibility**: One-click repository name copy, ARIA live regions, skip navigation, and full keyboard support (Esc to close modal).

---

## File Architecture

| File | Purpose |
|---|---|
| [`index.html`](index.html) | Semantic, accessible directory markup (Grid view, Table view, Modals, Panels) |
| [`styles.css`](styles.css) | Responsive design system (CSS custom properties, cards, tables, badges, animations) |
| [`app.js`](app.js) | Zero-dependency application logic (search, filter, sort, export, inspector modal, toast) |
| [`data/sites.js`](data/sites.js) | Complete verified data model (34 sites, 14 irregularities, 2 audited accounts, methodology) |
| [`AGENTS.md`](AGENTS.md) | Standing maintenance instructions for future sessions, including the permanent repository exclusion list |
| [`VERIFICATION.md`](VERIFICATION.md) | Exhaustive line-by-line audit ledger with official endpoints, commit SHAs, and reproduction commands |

---

## Verification & Integrity Policy

1. **Zero Hallucinations Guarantee**: Every single field is populated exclusively from GitHub REST API reads and verified repository content.
2. **Autonomous Execution**: All checks and audits were conducted without manual data entry.
3. **Transparent Irregularity Reporting**: Inconsistencies (such as draft duplicates, subfolder publishing, or README placeholders) are cataloged openly with dedicated flags.
4. **Independent Manual Review**: Every entry includes direct links to GitHub's raw API endpoints so any fact can be independently reviewed at any time.
5. **Exclusions Stay Excluded**: Directory counts are deliberately lower than account-wide API counts because of the standing exclusion below. Never "reconcile" them by re-adding an excluded repository.

---

## Repository Exclusions — Standing Instructions for Future Sessions

One repository on the account is **permanently excluded** from this site. Do not list it, link it, count it, or export it — in any future session, regeneration, or refresh of this directory.

| Excluded repository | Status | Instruction |
|---|---|---|
| `ProjX` (`buffedlizard55-lab/ProjX`) | Still live on GitHub with Pages `built`; intentionally unpublished **here** as of 2026-09-12 | **Never add it back** to `data/sites.js`, the [`VERIFICATION.md`](VERIFICATION.md) ledger table, README counts, or the JSON/CSV exports. Full rationale in [VERIFICATION.md § 2a](VERIFICATION.md#2a-repository-exclusions-deliberately-omitted). |

Because of this exclusion, the directory shows **34** sites while the GitHub API reports **35** public Pages repositories for the account. That mismatch is correct and expected — keep the account-level totals (`publicRepos: 35`, `pagesSites: 35`) at their verified API values and filter excluded names *after* the API read instead of lowering those totals. If a refresh script is ever written for this site, it must apply the exclusion list in [`AGENTS.md`](AGENTS.md) as a filter.

---

### Expected counts after the 2026-09-15 refresh

| Metric | Value |
|---|---|
| Sites published in directory | 34 |
| Interactive apps / doc stubs | 30 / 4 |
| Pages sites `built` | 34 / 34 (100%) |
| Commits audited across listed repos | 1143 |
| Public Pages repos on account (API, unchanged) | 35 |
