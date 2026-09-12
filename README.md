# MasterSite

The **master list and directory of every GitHub Pages site** hosted under [`buffedlizard55-lab`](https://github.com/buffedlizard55-lab) (with verified audit of [`kanlerxz87-cyber`](https://github.com/kanlerxz87-cyber)) — built strictly from official, verified sources with zero hallucinations.

**Live Directory:** <https://buffedlizard55-lab.github.io/MasterSite/>

---

## Directory Overview

For each of the **33 repositories with GitHub Pages enabled** (audited and verified via official GitHub REST API endpoints on **2026-09-12**):

- **Live Site Link** & **Repository Link**
- **Sourced Brief Description** (extracted line by line from each repo's `README.md` and live web app structure)
- **Created Date** (`created_at` timestamp + first-commit SHA verified within 1 second for every repository)
- **Last Updated Date** (newest committer timestamp on branch `main` + latest commit SHA + `pushed_at` tracking)
- **GitHub Pages Status & Build Source** (all 33 reporting `built`; 32 deploying from `main /` and 1 from `main /docs`)
- **Total Commits on Main** (exact commit count across all 33 repositories: 1,014 total commits audited)
- **Official Source Links for Manual Review**: Live URL, GitHub Repo, Pages API JSON record, and Pages Settings
- **Detailed Flagged Irregularities Register**: 11 flagged discrepancies (`IRR-01` through `IRR-11`) documented transparently

---

## User Interface Features

- **Instant Search & Multi-Filter**: Search by title, repo name, description, category, or flags with real-time feedback.
- **Category & Type Pills**: Filter across 5 categories (*Travel & Korea Trip*, *Sports Data & Scoreboards*, *SF Local Guides*, *Markets & Trading Research*, *Directory & Meta*) and site types (*Interactive Apps* vs. *Doc Stubs*).
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
| [`data/sites.js`](data/sites.js) | Complete verified data model (33 sites, 11 irregularities, 2 audited accounts, methodology) |
| [`VERIFICATION.md`](VERIFICATION.md) | Exhaustive line-by-line audit ledger with official endpoints, commit SHAs, and reproduction commands |

---

## Verification & Integrity Policy

1. **Zero Hallucinations Guarantee**: Every single field is populated exclusively from GitHub REST API reads and verified repository content.
2. **Autonomous Execution**: All checks and audits were conducted without manual data entry.
3. **Transparent Irregularity Reporting**: Inconsistencies (such as draft duplicates, subfolder publishing, or README placeholders) are cataloged openly with dedicated flags.
4. **Independent Manual Review**: Every entry includes direct links to GitHub's raw API endpoints so any fact can be independently reviewed at any time.
