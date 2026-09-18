# AGENTS.md — Standing Instructions for MasterSite

Read this before editing, auditing, or regenerating anything in this repository.

---

## 1. Repository Exclusions (hard rule)

**`ProjX` must never be listed on this site — and never added back in any future session.**

| | |
|---|---|
| **Excluded repository** | `ProjX` under `buffedlizard55-lab` |
| **Decided** | 2026-09-12, direct owner instruction: *"just remove projx from the site and don't add it in the future."* |
| **Scope of removal** | Removed from `data/sites.js` (directory entries), from the `VERIFICATION.md` § 2 ledger table, from README counts, and from the JSON/CSV exports the app produces. No live link, API endpoint or Pages URL for it is printed anywhere in this repository. |
| **What was NOT done** | The repository itself was **not** deleted, un-Published, or modified on GitHub. It still exists and its Pages build still reports `built`. Only its publication in MasterSite is suppressed, permanently. |

This exclusion is **permanent and unconditional**. It survives future audits, refreshes, and "completeness" passes. Do not re-add `ProjX` to:

- `data/sites.js` → `sites[]`
- `VERIFICATION.md` → the § 2 audit ledger table, or any count derived from it
- `README.md` → directory totals
- the exported JSON / CSV (they serialize `window.MASTERDATA`, so keeping it out of the data file is enough)

`tools/build_data.py` enforces this automatically: it filters the `excluded` list from `tools/overlay.json` **after** reading the GitHub API. Do not add the name to `tools/overlay.json → entries` either.

## 2. Do not "fix" the 40 vs 41 count mismatch

The directory lists **40** sites while the account has **41** public GitHub Pages repositories. **Both numbers are correct.**

- Keep `accountsChecked[].publicRepos: 41` and `pagesSites: 41` at their verified API values — they describe the *account*, and are the auditable reason one entry is missing.
- Never lower those to 40, and never raise the directory back to 41.
- `tools/build_data.py` asserts `len(sites) + len(unlisted) == pagesSites` at build time and records every withheld repository in `counts.unlisted` with a reason. If that assertion ever fires, the accounting is wrong — fix the accounting, do not loosen the assertion.
- These totals move every time the owner publishes a repository. Always re-read them from the API rather than trusting this file.
- The gap is documented on purpose in three places so nobody "repairs" it: the `data/sites.js` header comment, `VERIFICATION.md` § 2a, and `IRR-08` in the irregularities register.

## 3. Unreachable entries: freeze, never silently delete

Repositories that were published in a previous audit but return **HTTP 404** (or any non-200) from the API today go into the `unreachable` array — **not** into `sites[]`, and **not** into the bin.

- `JobSearchSF` was listed on 2026-09-16 (68 commits, last main commit `f68c452`) and returned 404 on 2026-09-17. **Re-confirmed 2026-09-18:** still HTTP 404, still `total_count 0` in the search API, still absent from the account's public list. It is frozen in `tools/overlay.json → retired[]` with its last verified values plus the endpoints that reproduce the 404.
- It renders on the site in the *Unreachable — Needs Owner Review* panel and in `VERIFICATION.md` § 2b.
- It is excluded from the live directory counts and from the `sites[]` array, but it **is** included in the CSV export with `Status = unreachable-404`.
- Only remove a frozen entry after the owner explicitly confirms it, or after the repository reappears (in which case move it back into `sites[]` with fresh API values).

## 4. Expected state of the directory

As of the **2026-09-18** audit (`generated: 2026-09-18T22:49:24Z`):

| Metric | Expected |
|---|---|
| `sites[]` entries in `data/sites.js` | 40 |
| `unreachable[]` entries | 1 (`JobSearchSF`) |
| `counts.unlisted[]` entries | 1 (`ProjX` — permanently excluded by owner request) |
| `grep -c '"repo":' data/sites.js` | 41 (40 sites + the 1 unreachable entry) |
| Ledger rows in `VERIFICATION.md` § 2 | 40, numbered 1–40 |
| Irregularities | 31 (`IRR-01` … `IRR-31`) |
| Commits summed across listed sites | 1,902 |
| Pages sites `built` | 40 / 40 |
| Apps / doc stubs | 35 / 5 |
| Public repos on account (API) | 41 |
| Categories | 7 — *Travel & Korea Trip* (11), *Sports Data & Scoreboards* (11), *Markets & Trading Research* (8), *SF Local Guides* (6), *Directory & Meta* (2: `MasterSite`, `Elections`), *Science & ML Research* (1: `GEMSDOE`), *Gaming & Guides* (1: `WoWForever`) |

Counts drift every time a repository is pushed to — always re-read them from `data/sites.js → counts` after a refresh rather than trusting this table.

### Verify, then trust

After every refresh, run both read-only verifiers. Neither one writes the dataset; they only report.

```bash
python3 tools/verify_live.py           # re-reads every API-derived field of every entry
python3 tools/audit_descriptions.py    # every numeric claim in a description vs its own README
```

`verify_live.py` distinguishes a **hard mismatch** (committed value disagrees with the live value, unexplained — a defect, re-run the generator) from **drift** (a field GitHub recomputes asynchronously, or a repository pushed to *after* the snapshot was taken). A run is clean when there are **0 hard mismatches**; the 2026-09-18 audit finished with 0 hard mismatches across 530 checks. Do not chase drift by re-running the generator in a loop — 41 actively-developed repositories will never hold still, and one was created *while* the 2026-09-18 audit was running.

### The prose is the fragile part

Every audit so far has found the same thing: the API-derived numbers are right and one or more *descriptions* have quietly stopped being true. The 2026-09-18 audit found five, including one that had become flatly false (`StockPaperSim` — see `IRR-25`). `audit_descriptions.py` only narrows the search by flagging numeric tokens that no longer appear in the README; a figure that survives in an old changelog section will slip past it. **Re-read the descriptions by hand each cycle.** That is the single highest-value task in this repository.

## 5. Repo conventions

- **The data file is generated.** Run `python3 tools/build_data.py` to rewrite `data/sites.js` from the API, then `python3 tools/build_verification.py` to rewrite `VERIFICATION.md`. Do not hand-edit the API-derived fields in either file.
- **Narrative lives in `tools/overlay.json`** — `entries` (title / category / description / flags per repo), `retired` (unreachable entries), `irregularities`, `excluded`, and `descriptionNotes`. A repository with no `entries` block is skipped with a warning, so a new site can never land in the directory with an invented description. New categories are picked up automatically by the UI (the chips are built from the data), so adding one needs no HTML change.
- **Two read-only verifiers exist; use them and do not "improve" them into writers.** `tools/verify_live.py` and `tools/audit_descriptions.py` must never modify `data/sites.js`. Their whole value is that they are independent of the generator.
- **New repositories are not auto-published.** `build_data.py` skips any repo with no curated `entries` block and prints a warning, so a fresh repo cannot land in the directory with an invented description. Add a sourced entry to `tools/overlay.json` first.
- Pure static site: `index.html` + `styles.css` + `app.js`, zero build step, zero dependencies. `data/sites.js` sets `window.MASTERDATA`; everything in the UI (stats, chips, cards, table, modal, exports) is derived from it at runtime. There are **no** hardcoded repository lists in the HTML/JS.
- Published via GitHub Pages from branch `main`, path `/` (`.nojekyll` present).
- The project's core promise is **"zero hallucinations"**. If a claim cannot be re-verified from a repository's own files, delete it — do not soften it into a still-unsupported number.

## 6. If the owner later reverses an exclusion

Only re-list `ProjX` on an explicit, current instruction from the owner in-session. Then: add a `tools/overlay.json → entries` block with API-verified values, re-run both generators, update README counts, and delete the exclusion section from this file.
