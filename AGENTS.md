# AGENTS.md — Standing Instructions for MasterSite

Read this before editing, auditing, or regenerating anything in this repository.

---

## 1. Repository Exclusions (hard rule)

**`ProjX` must never be listed on this site — and never added back in any future session.**

| | |
|---|---|
| **Excluded repository** | `buffedlizard55-lab/ProjX` (https://github.com/buffedlizard55-lab/ProjX) |
| **Decided** | 2026-09-12, direct owner instruction: *"just remove projx from the site and don't add it in the future."* |
| **Scope of removal** | Removed from `data/sites.js` (directory entries), from the `VERIFICATION.md` § 2 ledger table, from README counts, and from the JSON/CSV exports the app produces. |
| **What was NOT done** | The repository itself was **not** deleted, un-Published, or modified on GitHub. It still exists and its Pages build still reports `built`. Only its publication in MasterSite is suppressed, permanently. |

This exclusion is **permanent and unconditional**. It survives future audits, refreshes, and "completeness" passes. Do not re-add `ProjX` to:

- `data/sites.js` → `sites[]`
- `VERIFICATION.md` → the § 2 audit ledger table, or any count derived from it
- `README.md` → directory totals
- the exported JSON / CSV (they serialize `window.MASTERDATA`, so keeping it out of the data file is enough)

If a data-refresh/regeneration script is ever added to this repo, it must filter this exclusion list **after** reading the GitHub API, e.g.:

```js
const EXCLUDED = ["ProjX"]; // owner directive 2026-09-12 — see AGENTS.md
sites = apiRepos.filter((r) => !EXCLUDED.includes(r.name));
```

## 2. Do not "fix" the 33 vs 32 count mismatch

After the exclusion, the site lists **32** sites while the account has **33** public GitHub Pages repositories. **Both numbers are correct.**

- Keep `accountsChecked[].publicRepos: 33` and `pagesSites: 33` at their verified API values — they describe the *account*, and are the auditable reason one entry is missing.
- Never lower those to 32, and never raise the directory back to 33.
- The gap is documented on purpose in three places so nobody "repairs" it: `data/sites.js` header comment, `VERIFICATION.md` § 2a, and `IRR-12` in the irregularities register.

## 3. Expected state of the directory

| Metric | Expected |
|---|---|
| `sites[]` entries in `data/sites.js` | 32 |
| `grep -c '"repo":' data/sites.js` | 32 |
| Ledger rows in `VERIFICATION.md` § 2 | 32, numbered 1–32 |
| Irregularities | 12 (`IRR-01` … `IRR-12`) |
| Commits summed across listed sites | 987 |
| Pages sites `built` | 32 / 32 |
| Categories | 5 — *Travel & Korea Trip* (11), *Sports Data & Scoreboards* (10), *SF Local Guides* (5), *Markets & Trading Research* (5), *Directory & Meta* (1: `MasterSite`) |

`Directory & Meta` is down to a single entry (`MasterSite` itself) after the exclusion; that is expected, keep the category.

## 4. Repo conventions

- Pure static site: `index.html` + `styles.css` + `app.js`, zero build step, zero dependencies. `data/sites.js` sets `window.MASTERDATA`; everything in the UI (stats, filter chips, cards, table, inspector modal, JSON/CSV export) is derived from that object at runtime. There are **no** hardcoded repository lists in the HTML/JS — removing a site means editing `data/sites.js` only.
- Published via GitHub Pages from branch `main`, path `/` (`.nojekyll` present, so files/directories starting with `_` are allowed but there are none).
- The project's core promise is **"zero hallucinations"**: every field comes from a real GitHub REST API read. Keep doc totals and data totals mutually consistent, and keep the excluded repository out of all rendered output.

## 5. If the owner later reverses this decision

Only re-list `ProjX` on an explicit, current instruction from the owner in-session. Then: re-add the `data/sites.js` entry with API-verified values, restore the § 2 ledger row and renumber, bump the counts back (33 sites / 1,114 commits audited), and delete this exclusion section.
