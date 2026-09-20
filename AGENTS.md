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

## 2. Do not "fix" the 44 vs 45 count mismatch

The directory lists **44** sites while the account has **45** public GitHub Pages repositories. **Both numbers are correct.**

- Keep `accountsChecked[].publicRepos: 45` and `pagesSites: 45` at their verified API values — they describe the *account*, and are the auditable reason one entry is missing.
- Never lower those to 44, and never raise the directory back to 45.
- `tools/build_data.py` asserts `len(sites) + len(unlisted) == pagesSites` at build time and records every withheld repository in `counts.unlisted` with a reason. If that assertion ever fires, the accounting is wrong — fix the accounting, do not loosen the assertion.
- These totals move every time the owner publishes a repository (45 as of 2026-09-20, up from 41 on 2026-09-18). Always re-read them from the API rather than trusting this file.
- The gap is documented on purpose in three places so nobody "repairs" it: the `data/sites.js` header comment, `VERIFICATION.md` § 2a, and `IRR-08` in the irregularities register.

## 3. Unreachable entries: freeze, never silently delete

Repositories that were published in a previous audit but return **HTTP 404** (or any non-200) from the API today go into the `unreachable` array — **not** into `sites[]`, and **not** into the bin.

- `JobSearchSF` was listed on 2026-09-16 (68 commits, last main commit `f68c452`) and returned 404 on 2026-09-17. **Re-confirmed 2026-09-18 and 2026-09-20:** still HTTP 404, still `total_count 0` in the search API, still absent from the account's public list (now 45 repositories). It is frozen in `tools/overlay.json → retired[]` with its last verified values plus the endpoints that reproduce the 404.
- It renders on the site in the *Unreachable — Needs Owner Review* panel and in `VERIFICATION.md` § 2b.
- It is excluded from the live directory counts and from the `sites[]` array, but it **is** included in the CSV export with `Status = unreachable-404`.
- Only remove a frozen entry after the owner explicitly confirms it, or after the repository reappears (in which case move it back into `sites[]` with fresh API values).

## 4. Expected state of the directory

As of the **2026-09-20** third-pass audit (`generated: 2026-09-20T05:15:50Z`):

| Metric | Expected |
|---|---|
| `sites[]` entries in `data/sites.js` | 44 |
| `unreachable[]` entries | 1 (`JobSearchSF`) |
| `counts.unlisted[]` entries | 1 (`ProjX` — permanently excluded by owner request) |
| `grep -c '"repo":' data/sites.js` | 45 (44 sites + the 1 unreachable entry) |
| Ledger rows in `VERIFICATION.md` § 2 | 44, numbered 1–44 |
| Irregularities | 62 (`IRR-01` … `IRR-62`) — 5 critical, 30 warn, 27 info |
| Commits summed across listed sites | 2,413 |
| Pages sites `built` | 44 / 44 |
| Apps / doc stubs | 39 / 5 |
| Public repos on account (API) | 45 |
| Categories | 9 — *Sports Data & Scoreboards* (13), *Travel & Korea Trip* (11), *Markets & Trading Research* (9), *SF Local Guides* (6), *Directory & Meta* (1: `MasterSite`), *Elections & Civic Data* (1: `Elections`), *Science & ML Research* (1: `GEMSDOE`), *Gaming & Guides* (1: `WoWForever`), *Health & Personal Guides* (1: `ShoulderPain`) |
| `counts.proseShaStamped` | 44 / 44 |
| `counts.proseStale` | **0** — must be 0 before publishing; see below |
| `counts.proseReReadLatestPass` / carried | 14 / 30 |
| `descriptionNotes` / `acceptedDescriptionExceptions` | 16 / 7 real entries (plus a `__doc__` key the tools filter out) |
| Verifier results | all three clean: 582/582 live checks (0 hard, 0 drift) · 0 descriptions needing manual confirmation · 44/44 `kind` re-derivations, 0 disagreements |

*Personal & Placeholders* disappeared this pass: its only member, `VacationSchedule`, went from an 18-byte placeholder to a full project and moved to *Sports Data & Scoreboards*. Categories are derived from the data, so an empty one drops out on its own and the UI's filter chips follow — never hardcode a category count.

GitHub credentials expired mid-audit at ~`2026-09-20T03:07Z` and were restored by the owner about two hours later (`IRR-55`). The snapshot above is the post-reconnect rebuild; the second-pass snapshot at `03:06:19Z` was 2 hours stale and had to be rebuilt rather than pushed, which exposed 8 further repository moves (`IRR-61`).

Counts drift every time a repository is pushed to — always re-read them from `data/sites.js → counts` after a refresh rather than trusting this table.

### Verify, then trust

After every refresh, run both read-only verifiers. Neither one writes the dataset; they only report.

```bash
python3 tools/build_data.py            # FIRST: refresh, then read its prose-staleness gate
python3 tools/build_verification.py
python3 tools/verify_live.py           # re-reads every API-derived field of every entry
python3 tools/audit_descriptions.py    # every numeric claim in a description vs its own README
python3 tools/audit_kind.py            # re-derives app-vs-stub `kind` from the API
```

**Three ways a verifier run lies to you.** Check these before acting on any output:

1. **Uniform HTTP 401 means dead credentials, not broken data.** `verify_live.py` will report every entry as `MISMATCH ... committed=200 live=401`. Run `gh auth status` first and *discard* such a run — do not commit it. The second pass did exactly that and restored `tools/last_live_verify.json` from git rather than shipping 44 false mismatches (`IRR-55`).
2. **`pagesStatus: 'building'` is a live deployment state, not a defect.** A repository pushed to seconds ago reports `building` until the deploy finishes, so a snapshot can read 43/44 built when all 44 are healthy. The generator now re-reads a non-`built` status up to four times at six-second intervals and still records a genuinely broken build (`IRR-53`). Re-read the endpoint before treating a low `pagesBuilt` as a finding.
3. **A count quoted from a README may not match the file it describes.** `VacationSchedule`'s README says "16 flagged irregularities" while `docs/IRREGULARITIES.md` holds 21, because `IR-17`…`IR-21` were appended as `###` headings under a different section (`IRR-51`). Count headings at *both* levels, and prefer counting over quoting wherever a number can be counted.

`verify_live.py` distinguishes a **hard mismatch** (committed value disagrees with the live value, unexplained — a defect, re-run the generator) from **drift** (a field GitHub recomputes asynchronously, or a repository pushed to *after* the snapshot was taken). A run is clean when there are **0 hard mismatches**; the 2026-09-20 *first* pass finished with 0 hard mismatches across 582 checks. The second pass could not re-run it at all (`IRR-55`) — that is recorded as **blocked, not passed**, and no artifact in this repository claims otherwise. Do not chase drift by re-running the generator in a loop — 45 actively-developed repositories will never hold still; one was created *while* the 2026-09-18 audit was running and another ten minutes before the 2026-09-20 audit generated its data.

### The prose is the fragile part

Every audit so far has found the same thing: the API-derived numbers are right and one or more *descriptions* have quietly stopped being true. The 2026-09-18 audit found five, including one that had become flatly false (`StockPaperSim` — see `IRR-25`); the 2026-09-20 first pass found six more, including a second false placeholder (`Elections` — see `IRR-33`). Both critical errors came from repositories less than 48 hours old — **re-read the youngest entries first.** `audit_descriptions.py` only narrows the search by flagging numeric tokens that no longer appear in the README; a figure that survives in an old changelog section will slip past it. **Re-read the descriptions by hand each cycle.** That is the single highest-value task in this repository.

### `verifiedAtSha`: staleness is now computed, not guessed

The second pass of 2026-09-20 added the missing half (`IRR-50`). Each entry records **`verifiedAtSha`** — the default-branch commit its description was actually read at — alongside `lastVerified` (when) and `verifiedBasis` (what was read, and why carrying it forward is safe). `build_data.py` compares `verifiedAtSha` with the live head SHA on every build and prints the result as its final line:

```
prose: 12 re-read this pass, 32 carried, 44 stamped with a SHA, 0 provably behind their repo
PROSE-STALE <repo>   description read at <sha>, repository is now at <sha>
```

**`0 provably behind their repo` is the pass's completion gate.** A `PROSE-STALE` line is not an error — repositories are allowed to move — but it *is* a work item, and the entry must be re-read before publishing. `VERIFICATION.md` § 4a renders the same comparison as a ledger with rows ordered stale-first, so that table is literally the next session's work queue.

It earned its keep immediately, catching **five** repositories that moved *during* the second pass: `GEMSDOE` (`1b341d2`→`3093c6b`, session 18→19), `DrugAnalysis` (`6cb77f6`→`b6cdb8a`, v21→v21.1), `OLBG-Competition` (`a371b63`→`fee61ea`, a whole ice-hockey pipeline and 126→144 tests, `IRR-54`), `VacationSchedule` (`83663f7`→`6488222`, every recommended window changed, `IRR-52`), and `SFWeather` (`d5b1030`→`42f9892`). Note *which* it caught: `GEMSDOE`, `SFWeather` and `ShoulderPain` had been re-read minutes earlier in the same session, but `DrugAnalysis` and `OLBG-Competition` were **carried** entries — precisely the ones a human auditor would least think to re-check, and the ones whose prose had actually gone false. A timestamp stamp cannot make that distinction; a commit SHA can (`IRR-50`).

**The gate is necessary but not sufficient — read what the prose quotes.** `GEMSDOE` moved via a `[skip ci]` commit touching 6 evidence files at +1/−1 each, with `README.md` and `STATUS.md` both byte-identical, so no SHA comparison could ever have flagged the resulting problem: the published description quoted one replicate of a measurement that had fired twice, and `STATUS.md` says in terms that "quoting either one alone would overstate the precision" (`IRR-62`). Only opening the evidence files found it. Two rules follow. An evidence-only commit is **not** automatically benign — evidence is what a research description quotes, unlike a `data: refresh` commit, so open it. And a matching SHA proves the prose was read against those bytes, never that the prose is *true*.

**Rebuild and re-read are one loop, not two steps.** The third pass needed four successive builds before the gate reached zero, catching seventeen gate reports across ten repositories; one entry (`SFWeather`) was re-read against five successive heads, and `ShoulderPain` moved again nine minutes after being rewritten. Any claim of the form "repository X is unchanged" has a shelf life of minutes (`IRR-61`). When a repository's churn is provably automated and data-only, record a durable rule in its `verifiedBasis` — `SFWeather`'s now states that a `data: refresh … [skip ci]` commit with `README_changed=false` warrants a re-stamp, while a session commit warrants a re-read — so the next session triages instead of re-deriving.

When you re-read an entry, update all three fields together, and record *why* a carried entry is still safe. Where the intervening commit is provably benign — an automated data refresh that does not touch `README.md`, confirmed via `GET /repos/{owner}/{repo}/compare/{base}...{head}` — say so in `verifiedBasis` and re-stamp the SHA; that is a verification, not a shortcut. Where the prose changed, rewrite the description and log an `IRR` entry with the compare endpoint that reproduces the finding.

**Two traps this pass hit, so you do not have to:**

- Never build overlay text with Python `%`-formatting. A literal `%` in the prose (`"96.7%"`) breaks the format string and the write fails silently-ish with a `TypeError`. Use concatenation or `.replace()`.
- Never estimate diff statistics. A drafted irregularity claimed `+955/-884`; the API reported `+758/−977`. Pull additions/deletions from `gh api repos/{owner}/{repo}/compare/{base}...{head}`.

### `--overlay-only`: landing narrative work without network access

If `api.github.com` is unreachable or credentials have expired, `python3 tools/build_data.py --overlay-only` re-renders the narrative fields (title, category, description, flags, `lastVerified`, `verifiedBasis`, `verifiedAtSha`, retired entries, the irregularity register) into the **existing** snapshot with no network call at all. It leaves `generated` and every API-derived field byte-identical, writes a separate `overlayRendered` timestamp, recomputes `proseStale` against the *recorded* head SHA, and refuses to run if a listed repository has no curated overlay entry — so it can never default a description into existence. Verified non-fabricating: re-rendering the `03:06:19Z` snapshot produced **0 differences across 44 sites × 16 API-derived fields**, with `accountsChecked`, `methodology` and all API-derived counts identical.

Use it to keep the narrative honest while blocked. It **cannot** refresh the snapshot, and its `proseStale` count means "behind as of the snapshot", not "behind now" — it prints that warning itself. A full `build_data.py` run is still required before publishing (`IRR-55`).

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
