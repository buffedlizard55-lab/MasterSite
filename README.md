# MasterSite

The **master list and directory of every GitHub Pages site** hosted under
[buffedlizard55-lab](https://github.com/buffedlizard55-lab) — built from official,
verified sources only.

**Live site:** <https://buffedlizard55-lab.github.io/MasterSite/>

## What the directory contains

For each of the **33 repositories with GitHub Pages enabled** (all verified via the
official GitHub REST API on 2026-09-12):

- **Live site link** and **repository link**
- **Brief description** (derived from each repo's README and the live site content — nothing from memory)
- **Created date** (repo `created_at`; first commit confirmed within 1 second for every repo)
- **Last updated** (newest commit on `main`; `pushed_at` noted where it differs)
- **Pages build status & source** (branch/path), commit count, category, and flags
- **Source links for manual review**: repo, Pages API record (JSON), Pages settings

The directory also lists every **flagged irregularity** found during verification
(README-only stubs, duplicate draft repos, transient build states, naming mismatches,
and the second account `kanlerxz87-cyber`, which exists but has **0 public
repositories** and therefore no Pages sites).

## Files

| File | Purpose |
|---|---|
| [`index.html`](index.html) | The directory UI (static, dependency-free) |
| [`styles.css`](styles.css) | Styling |
| [`app.js`](app.js) | Search / filter / sort / render logic |
| [`data/sites.js`](data/sites.js) | The verified master list (all data + irregularities + methodology) |
| [`VERIFICATION.md`](VERIFICATION.md) | Line-by-line audit ledger with sources |

## Verification policy

- **No hallucinations.** Every field comes from a GitHub API read or a direct read of the live site, logged in `VERIFICATION.md`.
- **No manual input.** The audit ran autonomously; discrepancies are flagged (`IRR-01`…`IRR-11`) instead of guessed.
- **Manual review welcome.** Every card links to the official Pages API JSON record and the repo's Pages settings.
