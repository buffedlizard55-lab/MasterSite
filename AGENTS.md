# AGENTS.md — Standing Instructions for MasterSite

Read this before editing, auditing, or regenerating anything in this repository.

> **Fresh snapshot: 2026-09-25 second pass (API snapshot `2026-09-25T00:10:26Z`, 72 listed / 73 account, all three verifiers clean).** The counts further down that echo the previous pass are superseded; the § 4 table is the expected state and everything else here is case-study history.

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

## 2. Do not "fix" the listed-vs-account count mismatch

The directory lists **72** sites while the account has **73** public GitHub Pages repositories. **Both numbers are correct**, and as of 2026-09-24 (second pass) the gap has **one component**: `ProjX`. The earlier second component (`PRICINGEXPERT`) is closed — it is now a listed research desk — and is kept below as the case study it is.

- **`ProjX` — permanently excluded by owner request. Never list it.** Not in `sites[]`, not in `VERIFICATION.md` § 2, not in the README counts, not in the exports, not in `tools/overlay.json → entries`. This half of the gap is deliberate and permanent (§ 1, § 6).
- **`PRICINGEXPERT` — withheld only procedurally at the time; LISTED by the 2026-09-23 build (`IRR-86` closed).** The durable rule it illustrated still stands: **narrative can be landed offline (via `--overlay-only`), listing cannot** — and do not delete a curated entry to make the accounting look tidy.
- Keep `accountsChecked[].publicRepos: 73` and `pagesSites: 73` at their verified API values — they describe the *account*, and are the auditable reason one entry is missing. **Re-read them from the API every pass; do not carry them forward by hand** — the 2026-09-23 pass began at 64 and ended at 69; this pass read **73**.
- Never lower those to 72, and never raise the directory to 73 by listing `ProjX`.
- `tools/build_data.py` asserts `len(sites) + len(unlisted) == pagesSites` at build time and records every withheld repository in `counts.unlisted` with a reason. If that assertion ever fires, the accounting is wrong — fix the accounting, do not loosen the assertion.
- These totals move every time the owner publishes a repository (73 as of 2026-09-24T23:54Z, up from 70 at the 00:39:08Z snapshot; growth history 41 → 45 → 50 → 53 → 63 → 64 → 69 → 70 → 73 across the passes). Always re-read them from the API rather than trusting this file.
- The gap is documented on purpose in three places so nobody "repairs" it: the `data/sites.js` header comment, `VERIFICATION.md` § 2a, and `IRR-08` in the irregularities register.

## 3. Unreachable entries: freeze, never silently delete

Repositories that were published in a previous audit — **or fully verified in the pass that discovered them** — but return **HTTP 404** (or any non-200) from the API go into the `unreachable` array: **not** into `sites[]`, and **not** into the bin. As of 2026-09-24 (second pass) there are **four**, and the Malta family widened the rule twice.

- `MALTA` was **new to the 2026-09-24 pass**, never published in any earlier audit. It was cloned at head `f0fb352` and verified in full — `tests/test_calculate.py` 53 OK, `tests/test_radio.py` 19 OK, `scripts/check_links.py` OK over 10 pages, `node --test` 36/36 — and then stopped existing: `GET /repos/buffedlizard55-lab/MALTA` returns 404 and no surviving repository carries its `created_at` of `2026-09-23T17:19:52Z`, so it was deleted rather than renamed. It is frozen with its last verified values (`IRR-109`). **The widened rule: whether a repository is frozen no longer depends on whether it was previously published.** If a pass has already done the work of reading it, the work is preserved and the disappearance is flagged for the owner rather than dropped.

- `MALTA-LAWS` and `MALTA2` were both **listed** in the 2026-09-24 first pass and both return HTTP 404 this pass (`IRR-110`): `MALTA-LAWS` (3 commits, head `18f3323`, verified by executing its own checks) and `MALTA2` (the 8-byte `# MALTA2` placeholder created minutes after `MALTA` vanished). Both are frozen with their last verified values. Counting `MALTA` itself, three of the four Malta-family repositories created on 2026-09-23/24 have now been deleted upstream within a day — only `MALTASUPPLEMENTAL` remains live.

- `JobSearchSF` was listed on 2026-09-16 (68 commits, last main commit `f68c452`) and returned 404 on 2026-09-17. **Re-confirmed on nine consecutive audits through 2026-09-24 (second pass):** still HTTP 404, still `total_count 0` in the search API, still absent from the account's public list (now 73 repositories). It is frozen in `tools/overlay.json → retired[]` with its last verified values plus the endpoints that reproduce the 404.
- It renders on the site in the *Unreachable — Needs Owner Review* panel and in `VERIFICATION.md` § 2b.
- It is excluded from the live directory counts and from the `sites[]` array, but it **is** included in the CSV export with `Status = unreachable-404`.
- Only remove a frozen entry after the owner explicitly confirms it, or after the repository reappears (in which case move it back into `sites[]` with fresh API values).

## 4. Expected state of the directory

As of the **2026-09-25 second-pass** audit (API snapshot `2026-09-25T00:10:26Z`, with all three read-only tools run against that snapshot):

| Metric | Expected |
|---|---|
| `sites[]` entries in `data/sites.js` | 72 |
| `unreachable[]` entries | 4 (`JobSearchSF` since 2026-09-17; `MALTA` — deleted mid-pass 2026-09-24, `IRR-109`; `MALTA-LAWS` and `MALTA2` — deleted upstream since the 00:39Z snapshot, `IRR-110`) |
| `counts.unlisted[]` entries | 1 (`ProjX` — permanently excluded by owner request) |
| Ledger rows in `VERIFICATION.md` § 2 | 72, numbered 1–72 |
| Irregularities | 112 (`IRR-01` … `IRR-112`) — three registered this pass (`IRR-110` … `IRR-112`), of which 2 critical and 1 warn |
| Commits summed across listed sites | **4,017 at the shipping snapshot, and it will not hold.** Treat any number here as a timestamp, never a constant |
| Pages sites `built` | 72 / 72 at the shipping snapshot |
| Apps / doc stubs | 65 / 7 (stubs: `Leg3SeoulTrip`, `MLB-Prediction-model-backtest`, `NFL-PLAYER-PROP-SIM`, `NFLPRED`, `PFFNFL`, `RGENGY`, `StokEngineer`) |
| Public repos on account (API) | 73 |
| Pages sites on account (API) | 73 |
| Categories | 12 — Sports Data & Scoreboards (28), Markets & Trading Research (13), Travel & Korea Trip (11), SF Local Guides (7), Science & ML Research (3), Gaming & Guides (3), Directory & Meta (2), Reference & Archives (1), Travel & Event Dossiers (1), Elections & Civic Data (1), Health & Personal Guides (1), Social & Creator Data (1). *Reference & Archives* was created by this pass for `NOBEL-PRIZE`; **never hardcode a category count** — the UI chips are derived from the data |
| `counts.proseShaStamped` | 72 / 72 — and **verify the shape, not just the presence**: `IRR-108` proved that a stamp reading `AUTO:COUNTS` or `main` satisfies "is populated" while making the gate permanently unsatisfiable. Assert `^[0-9a-f]{7,40}$` |
| `counts.proseStale` | **26 — a work queue, not a failure.** Repositories are pushed to faster than they can be read, and this pass generated its own example: `TAXKALSHI` reversed from stub to app twice and `NOBEL-PRIZE` from placeholder to archive while work was in flight |
| Verifier results | **RUN against the shipping snapshot.** `verify_live.py`: 946 checks, 945 ok, 0 hard mismatches, 1 drift (`InjuryAlerTNFL` `pushedAt`, pushed after the snapshot). `audit_kind.py`: 72 checked, 0 disagreements. `audit_descriptions.py` (after `rm -rf tools/.readme-cache`): 35 accepted exceptions, **0 entries needing manual confirmation**. The Playwright contract runs in CI only — no browser binary or CDN access exists here, so no local run is claimed |

**`acceptedDescriptionExceptions` is a dict keyed by repository name; `descriptionNotes` is a flat array.** They are not the same shape — check before indexing either one.

**After any scripted edit to `tools/overlay.json`, assert every `entries[*].description` is a `str`.** A stray trailing comma in a Python edit silently writes a 1-element *list*; `build_data.py` will happily build it, and `tools/audit_descriptions.py` then dies with `TypeError: expected string or bytes-like object, got 'list'`. This happened to `DrugAnalysis` and `MLBComp` in the 2026-09-21 pass.

Categories are derived from the data, so an empty one drops out on its own and the UI's filter chips follow — **never hardcode a category count.** (*Personal & Placeholders* vanished this way when `VacationSchedule` grew into a real project; *Social & Creator Data* appeared the same way.)

GitHub credentials have now expired mid-audit **four** times, and every outage has ended the same way — the owner restored them and the pass was finished rather than restarted. The first (~`2026-09-20T03:07Z`) came back about two hours later and the pass was rebuilt (`IRR-55`). The second (`~2026-09-22T23:55Z`) left a **hybrid** snapshot behind: its API-derived half was the full refresh that completed at `23:32:49Z`, and its narrative half was landed with `--overlay-only`, which is why that snapshot reported `counts.proseStale` 21 and no verifier results (`IRR-85`). Credentials returned at ~`2026-09-23T00:50Z` and the 2026-09-23 pass completed the blocked work: full `build_data.py` runs, all three verifiers, and the two repositories that `--overlay-only` could curate but not list. Then they died a **third** time at ~`2026-09-23T01:44Z`, roughly one minute after the last verifier succeeded and *after* the pass was committed, so the owner's requested PR and merge could not be executed and that snapshot became a hybrid (`IRR-93`). They came back at ~`02:24Z`, and the resume procedure — **re-run the full build and all three verifiers before publishing, never push an old snapshot** — caught a seventh stub→app reversal (`PRICINGEXPERT`, `IRR-94`) that the pre-outage snapshot would have published as an empty stub. They died a **fourth** time at ~`2026-09-25T00:16Z`, about one minute after the 2026-09-25 pass was pushed and PR #18 was created (head `ed77f09`), with CI already green — the exact `IRR-93` shape again, so **the push and PR succeeded and only the merge is outstanding**. The rules that survive all four outages are unchanged: **a blocked verifier is recorded as blocked, never as passed**; a full `build_data.py` plus all three verifiers is required before any state is called a completed pass; and **before publishing a snapshot that is more than minutes old, re-run everything**, because 73 actively-pushed repositories will have moved. Diagnosing the outage takes one call — `curl -s -o /dev/null -w '%{http_code}' https://api.github.com/rate_limit` returning **401 with no credentials offered** means the egress path is injecting a dead token, not that the endpoint is broken.

**Outstanding after the 2026-09-25 pass:** PR #18 (`arena/01a0d5b4-mastersite` → `main`, head `ed77f09`) is **open and unmerged** — the merge is the one task that could not run because credentials died right after the push. Next session, when credentials are back: `gh pr checks 18`, then `gh pr merge 18`; if the branch has new commits by then, `git push origin arena/01a0d5b4-mastersite` first (never any other branch) and re-check. A gitignored `.work/next-session-handoff.md` carries the per-entry handoff including the 26-item `PROSE-STALE` queue.

Counts drift every time a repository is pushed to — always re-read them from `data/sites.js → counts` after a refresh rather than trusting this table.

### What the second half of the 2026-09-23 pass established (28 re-reads, executed not quoted)

The second half of this pass re-read **all 28** `PROSE-STALE` entries at head and rewrote them from
**executed** evidence rather than quoted prose. For each repository a shallow clone at head was read file
by file — generated JSON, markdown and ledger artifacts loaded with `json.load` and counted, never
estimated — and the repository's own gates were run in the sandbox. Five durable lessons came out of it.

1. **A count quoted from a repository's own file must be counted, not measured by `len()` on the wrong
   container.** `Elections`' `master_sources.json` and `flagged_sources.json` are dicts holding a
   `sources` array plus metadata; `len(d['sources'])` gives **20** and **7**, while `len(d)` gives **6**
   and **4** — which is what the previous entry published, understating the directory by 17 sources
   (`IRR-95`). The repository's README was correct the whole time. Prefer counting over quoting wherever
   a number can be counted, and when counting, count the array.
2. **A repository's README banner is not its number of record — its generated artifacts are.** Five
   repositories this pass had a README figure that disagreed with a committed generated file at the same
   head: `Commodities` (`IRR-97`, 63/2,455/291 in prose against 74/2,736/337 in the artifacts),
   `Elections` (`IRR-96`, one universe count printed four different ways), `MLBComp` (`IRR-98`, `18`
   controls against an exported 22), `TradingViewTheLeap` (`IRR-101`, `29 of 60` intraday series against
   an index recording 60/60 equity), and `MLBRainDelay` (`IRR-103`, `67 assertions` and `100+ passing`
   against 109 executed). Publish both figures and register the divergence; never resolve it by picking
   the smaller number.
3. **Run the repository's own test suite, not just its verifier.** Two repositories had a green gate and
   a red suite at the same head: `StokEngineer` (`IRR-100`, `pytest` 84 passed / 3 skipped / **1 FAILED**
   beside `cli verify` printing `OK`) and `GEMSDOE` (`IRR-102`, **1 FAILED** on
   `test_the_build_reproduces_the_committed_pages` — the committed site pages are not the pages the
   generator produces — while `STATUS.md` claims 445 passed / 1 skipped against an executed 467 / 32).
   Executing the suite is the only reason either is visible. Conversely, executing also produced the
   passes that let an entry state a number at all: `MasterSelfLearn` 350, `SelfLearn` 189,
   `StockPaperSim` 697 plus 5,513 audit checks with a 327-file byte-identical custody note,
   `NFLInjuryReport` 222, `VacationSchedule` 125, `PRICINGEXPERT` 1,198 verify checks and 39 tests,
   `TradingViewTheLeap` 444 checks.
4. **Withdraw a figure that cannot be re-derived; do not soften it.** Eleven figures the previous entries
   published were withdrawn this pass on exactly that basis — `StokEngineer`'s `38 sources` / `71,004
   bytes` / `155 badges` / `24-line claim log` / `7 flagged irregularities`, `TradingViewTheLeap`'s
   `$20.56` refutation margin and its `401 passed / 459-check / 94-unit-test` figures, `DrugAnalysis`'s
   v27 row counts, `VacationSchedule`'s 42 tests / 53 review items / 21 irregularities, `Coupons`'
   185/18/517, `SocialMediaComp`'s 60 entries, and `SelfLearn`'s 89 documents / 141 questions / 22
   failures / 35 irregularities / 156 tests. Each replacement was counted or executed in the same pass,
   and each `verifiedBasis` names the file it came from and the commit it was read at.
5. **`PROSE-STALE` is a treadmill, and the honest number is the one measured at the snapshot.** The
   rewrites took about two hours; the repositories pushed 18 times inside that window. The queue fell
   27 → 18 and then sat at 18. `AGENTS.md` already records the triage for repositories that commit their
   own output on a cron (`MasterSelfLearn`, `KalshiPaperSim`, `Elections`, `NFLInjuryReport`): a
   `PROSE-STALE` report against them is *expected*, and the check is to compare their own generated
   counters rather than to re-read every time.

**Environment limits recorded as limits, not as passes.** `MLB-Live-PBP`'s `smoke-test.mjs` fails here
only because it fetches live `statsapi.mlb.com`, which this sandbox cannot reach — 14 of its 15 offline
suites pass, and the failure is published as an environment limit rather than as a repository defect.
`GEMSDOE`'s suite would not even collect until `rasterio`, `scikit-image`, `torch`, `pyyaml` and `tqdm`
were installed. `OLBG-Competition`'s `pytest --collect-only -q | grep -c '::'` returns 0 because its
collection output uses a different format; the repo's own `tests/test_facts.py` pins **441 test
functions**, which pytest's parametrisation expands to **499 collected cases**. Two of the 28 entries
(`NFL-PLAYER-PROP-SIM`, `MasterSite`) are stubs or self-referential and were verified against exactly
that and nothing more.


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

1. **Uniform HTTP 401 means dead credentials, not broken data.** `verify_live.py` will report every entry as `MISMATCH ... committed=200 live=401`. Run `gh auth status` first and *discard* such a run — do not commit it. The second pass did exactly that and restored `tools/last_live_verify.json` from git rather than shipping 52 false mismatches (`IRR-55`); the fifth pass did not run the verifiers at all rather than manufacture 61 (`IRR-85`). Two details from `IRR-85` that cost time to discover: this sandbox's egress path **injects the expired token into every `api.github.com` request**, so a request with no `Authorization` header also returns 401 and the unauthenticated 60-request tier is *not* a fallback; and `git clone` dies with it (`could not read Username for 'https://github.com'`), so repository contents become unreadable too. `github.com` HTML still returns 200, which is how you tell this apart from a general network outage.
2. **`pagesStatus: 'building'` is a live deployment state, not a defect — but `errored` is a defect.** A repository pushed to seconds ago reports `building` until the deploy finishes, so a snapshot can read 51/52 built when all 52 are healthy. The generator now re-reads a non-`built` status up to four times at six-second intervals and still records a genuinely broken build (`IRR-53`). Re-read the endpoint before treating a low `pagesBuilt` as a finding. The retry loop has now earned its keep in both directions: `Elections` reported `errored` through **all four** re-reads, with `GET /pages/builds` showing `Page build failed.` for two consecutive builds after a successful one, so it was published as the only non-`built` entry of 63 (`IRR-83`) — and then recovered on its own push, closing the entry without deleting it. The 2026-09-23 pass produced the other direction twice: `SelfLearn` and then `NFLInjuryReport` were recorded `building` after all four re-reads, and `verify_live.py` reported each as a **hard mismatch** minutes later when the deploy finished. Both were cleared by re-running `build_data.py`, never by editing data. Record the state as-is; GitHub keeps serving the last successful build, so **do not infer that the live URL is dead, and do not infer that it is healthy.**
3. **A count quoted from a README may not match the file it describes.** `VacationSchedule`'s README says "16 flagged irregularities" while `docs/IRREGULARITIES.md` holds 21, because `IR-17`…`IR-21` were appended as `###` headings under a different section (`IRR-51`). Count headings at *both* levels, and prefer counting over quoting wherever a number can be counted.

`verify_live.py` distinguishes a **hard mismatch** (committed value disagrees with the live value, unexplained — a defect, re-run the generator) from **drift** (a field GitHub recomputes asynchronously, or a repository pushed to *after* the snapshot was taken). A run is clean when there are **0 hard mismatches**; the 2026-09-20 *first* pass finished with 0 hard mismatches across 582 checks. The second pass could not re-run it at all (`IRR-55`) — that is recorded as **blocked, not passed**, and no artifact in this repository claims otherwise. Do not chase drift by re-running the generator in a loop — 64 actively-developed repositories will never hold still; one was created *while* the 2026-09-18 audit was running, another ten minutes before the 2026-09-20 audit generated its data, two during the 2026-09-21 pass, `PRICINGEXPERT` 31 minutes before the 2026-09-22 build that discovered it, and `MLB-Live-PBP` was pushed about a minute after the 2026-09-23 snapshot read it. Re-run the generator for **hard mismatches** (a transient `building` state is the usual cause); leave **drift** alone. Six full builds in the 2026-09-23 pass moved the account total 3,526 → 3,561 commits and the stale queue 21 → 24 without ever converging, which is the measurement behind `IRR-92` and the reason a stale count is published as a badge per entry rather than treated as a pass/fail gate.

### The prose is the fragile part

Every audit so far has found the same thing: the API-derived numbers are right and one or more *descriptions* have quietly stopped being true. The 2026-09-18 audit found five, including one that had become flatly false (`StockPaperSim` — see `IRR-25`); the 2026-09-20 first pass found six more, including a second false placeholder (`Elections` — see `IRR-33`); 2026-09-21 found two (`MLBComp` a placeholder that had become an application, `IRR-64`; `NFLComp` a **+$2.43M profit that is a −$353K loss**, `IRR-65`); and 2026-09-22 found two more published descriptions that had gone false — `SelfLearn` and `MasterSelfLearn`, both published as empty one-file placeholders and now research engines whose suites this audit executed (`IRR-84`) — plus one it caught *before* publication (`NFLPARLAYCOMP`, whose PnL changed sign mid-read, `IRR-82`). **"Published as a placeholder" is now the single most common false description in this directory: five occurrences across four passes (`IRR-42`, `IRR-64`, `IRR-71`→`IRR-84`).** Every critical error came from a repository less than 48 hours old — **re-read the youngest entries first.** `audit_descriptions.py` only narrows the search by flagging numeric tokens that no longer appear in the README; a figure that survives in an old changelog section will slip past it. **Re-read the descriptions by hand each cycle.** That is the single highest-value task in this repository.

### `verifiedAtSha`: staleness is now computed, not guessed

The second pass of 2026-09-20 added the missing half (`IRR-50`). Each entry records **`verifiedAtSha`** — the default-branch commit its description was actually read at — alongside `lastVerified` (when) and `verifiedBasis` (what was read, and why carrying it forward is safe). `build_data.py` compares `verifiedAtSha` with the live head SHA on every build and prints the result as its final line:

```
prose: 11 re-read this pass, 50 carried, 61 stamped with a SHA, 21 provably behind their repo
PROSE-STALE <repo>   description read at <sha>, repository is now at <sha>
```

(The 2026-09-22 figures, and the first pass whose gate did **not** reach zero — see `IRR-85`. Note the wording: in `--overlay-only` mode the same line reads `N provably behind their snapshot head`, because that mode compares against the recorded head and cannot see commits made since. Read the difference; it is the whole distinction between the two modes.)

**`0 provably behind their repo` is the pass's completion gate.** A `PROSE-STALE` line is not an error — repositories are allowed to move — but it *is* a work item, and the entry must be re-read before publishing. `VERIFICATION.md` § 4a renders the same comparison as a ledger with rows ordered stale-first, so that table is literally the next session's work queue.

It earned its keep immediately, catching **five** repositories that moved *during* the second pass: `GEMSDOE` (`1b341d2`→`3093c6b`, session 18→19), `DrugAnalysis` (`6cb77f6`→`b6cdb8a`, v21→v21.1), `OLBG-Competition` (`a371b63`→`fee61ea`, a whole ice-hockey pipeline and 126→144 tests, `IRR-54`), `VacationSchedule` (`83663f7`→`6488222`, every recommended window changed, `IRR-52`), and `SFWeather` (`d5b1030`→`42f9892`). Note *which* it caught: `GEMSDOE`, `SFWeather` and `ShoulderPain` had been re-read minutes earlier in the same session, but `DrugAnalysis` and `OLBG-Competition` were **carried** entries — precisely the ones a human auditor would least think to re-check, and the ones whose prose had actually gone false. A timestamp stamp cannot make that distinction; a commit SHA can (`IRR-50`).

**The gate is necessary but not sufficient — read what the prose quotes.** `GEMSDOE` moved via a `[skip ci]` commit touching 6 evidence files at +1/−1 each, with `README.md` and `STATUS.md` both byte-identical, so no SHA comparison could ever have flagged the resulting problem: the published description quoted one replicate of a measurement that had fired twice, and `STATUS.md` says in terms that "quoting either one alone would overstate the precision" (`IRR-62`). Only opening the evidence files found it. Two rules follow. An evidence-only commit is **not** automatically benign — evidence is what a research description quotes, unlike a `data: refresh` commit, so open it. And a matching SHA proves the prose was read against those bytes, never that the prose is *true*.

**A README-unchanged compare justifies triage, never a silent re-stamp — this is the sharpest lesson of the 2026-09-21 pass.** Of the 20 stale ranges that pass, the README changed in only 13; yet **four of the five best findings came from ranges that touched no README at all** (`IRR-70`). Open the artifact the description actually quotes.

**Prefer the generated data file over the README when they disagree, and flag the disagreement.** Five upstream repositories contradict themselves: `Elections` (209 / 189 in prose vs **229** in the file; 63 vs **58** irregularities, `IRR-67`), `NBAInjuryReport` (prose two days behind its own regenerated `reporter_verify.json`, `IRR-68`), `OLBG-Competition` (262 in prose vs 258 `def test_`), `NFLPARLAYCOMP` (README says ~6.8 MB / ~1,050 bundle files; the committed tree measures **7.62 MB / 1,052**, `IRR-77`) and `SelfLearn` (`SUMMARY.md` says 91 documents / 5 experiments; `reports/site_data.json`, generated ten minutes earlier, holds **89 / 3**, `IRR-84`). Publish the counted file value, and register the mismatch as an `IRR` rather than quietly picking one.

**Rebuild and re-read are one loop, not two steps.** The third pass needed four successive builds before the gate reached zero, and the fourth (2026-09-21) needed **eight**, opening at 20 stale entries and catching six repositories that moved mid-audit, catching seventeen gate reports across ten repositories; one entry (`SFWeather`) was re-read against five successive heads, and `ShoulderPain` moved again nine minutes after being rewritten. The fifth (2026-09-22) never closed the loop at all: it opened at 23 stale entries, cleared 2 by re-stamping and 2 by rewriting, and lost its credentials with 21 still queued (`IRR-85`). Its sharpest instance is `NFLPARLAYCOMP`, whose entire entry — 100 users, 32 trades, **+135.04** — was falsified by eight commits in 40 minutes and had to be discarded rather than patched, including a PnL that flipped to **−92,876.56** (`IRR-82`). One repository now churns on a schedule: `MasterSelfLearn` commits its own output every 30 minutes via cron, so a `PROSE-STALE` report against it is *expected* and its `verifiedBasis` carries the durable rule — compare cycle numbers in `README`'s `AUTO:COUNTS` and `STATUS.md`; a new cycle with the same schema is a re-stamp, a change in *which* quantities are reported is a rewrite. Any claim of the form "repository X is unchanged" has a shelf life of minutes (`IRR-61`). When a repository's churn is provably automated and data-only, record a durable rule in its `verifiedBasis` — `SFWeather`'s now states that a `data: refresh … [skip ci]` commit with `README_changed=false` warrants a re-stamp, while a session commit warrants a re-read — so the next session triages instead of re-deriving.

When you re-read an entry, update all three fields together, and record *why* a carried entry is still safe. Where the intervening commit is provably benign — an automated data refresh that does not touch `README.md`, confirmed via `GET /repos/{owner}/{repo}/compare/{base}...{head}` — say so in `verifiedBasis` and re-stamp the SHA; that is a verification, not a shortcut. Where the prose changed, rewrite the description and log an `IRR` entry with the compare endpoint that reproduces the finding.

**Two traps this pass hit, so you do not have to:**

- Never build overlay text with Python `%`-formatting. A literal `%` in the prose (`"96.7%"`) breaks the format string and the write fails silently-ish with a `TypeError`. Use concatenation or `.replace()`.
- After any scripted overlay edit, assert `isinstance(entry["description"], str)` for all entries. A stray trailing comma writes a 1-element *list*; the build succeeds and `audit_descriptions.py` then crashes with `TypeError: expected string or bytes-like object, got 'list'`.
- `rm -rf tools/.readme-cache` before re-running `audit_descriptions.py`, or it re-reads stale README text.
- `curl https://<owner>.github.io/...` returns HTTP `000` (`SSL_ERROR_SYSCALL`) from this sandbox. That is an **egress restriction, never evidence a site is down.** Use `GET /repos/{owner}/{repo}/pages` → `status: built`, or `tools/audit_kind.py`, which reaches published paths through the API.
- Use `git clone` for anything you intend to *execute*; `gh api .../contents/{path}` with `Accept: raw` yields files the runtime refuses to parse. Raw fetch is fine for merely *reading* a README.
- Never estimate diff statistics. A drafted irregularity claimed `+955/-884`; the API reported `+758/−977`. Pull additions/deletions from `gh api repos/{owner}/{repo}/compare/{base}...{head}`.

### `--overlay-only`: landing narrative work without network access

If `api.github.com` is unreachable or credentials have expired, `python3 tools/build_data.py --overlay-only` re-renders the narrative fields (title, category, description, flags, **`kind`**, `lastVerified`, `verifiedBasis`, `verifiedAtSha`, retired entries, the irregularity register) into the **existing** snapshot with no network call at all. It leaves `generated` and every API-derived field byte-identical, writes a separate `overlayRendered` timestamp, recomputes `proseStale` against the *recorded* head SHA, and refuses to run if a listed repository has no curated overlay entry — so it can never default a description into existence. Verified non-fabricating: re-rendering the `03:06:19Z` snapshot produced **0 differences across 44 sites × 16 API-derived fields**, with `accountsChecked`, `methodology` and all API-derived counts identical.

Use it to keep the narrative honest while blocked. It **cannot** refresh the snapshot, and its `proseStale` count means "behind as of the snapshot", not "behind now" — it prints that warning itself. A full `build_data.py` run is still required before publishing (`IRR-55`).

**Four limits, learned by hitting all four in the 2026-09-22 pass (`IRR-86`):**

1. **It cannot add a site.** It iterates the `sites[]` already in the snapshot, so a repository curated *after* the last full build stays unlisted no matter how complete its overlay entry is. `PRICINGEXPERT` is in exactly that state.
2. **It cannot refresh `counts.unlisted`.** That block is generated, so a repository whose reason was "no curated entry yet" keeps publishing that reason after the entry exists. Do not hand-edit it — it is corrected by the next full build, and the discrepancy is recorded rather than hidden.
3. **It used to be unable to correct `kind`** — `OVERLAY_FIELDS` omitted it even though `main()` sources `kind` from the overlay (`kind = ov.get("kind")`, falling back to an API `index.html` probe only when the overlay is silent). Left unfixed, that meant republishing `stub` for three repositories the same audit had already proved were apps. `kind` is now rendered, and `counts.apps` / `counts.stubs` are recomputed beside the category tally because `build_verification.py` quotes both into `VERIFICATION.md`.
4. **It reports an entry that is *ahead* of the snapshot as stale.** `MasterSelfLearn` was read at `eda549e` while the snapshot recorded `fe488ed`, so `proseStale` is true for an entry whose prose is newer than the snapshot knows about. That is the conservative output and it must be left alone: re-stamping backwards to silence the gate would claim the prose was read at a commit it was not read at.

## 5. Repo conventions

- **The data file is generated.** Run `python3 tools/build_data.py` to rewrite `data/sites.js` from the API, then `python3 tools/build_verification.py` to rewrite `VERIFICATION.md`. Do not hand-edit the API-derived fields in either file.
- **Narrative lives in `tools/overlay.json`** — `entries` (title / category / description / flags per repo), `retired` (unreachable entries), `irregularities`, `excluded`, and `descriptionNotes`. A repository with no `entries` block is skipped with a warning, so a new site can never land in the directory with an invented description. New categories are picked up automatically by the UI (the chips are built from the data), so adding one needs no HTML change.
- **Two read-only verifiers exist; use them and do not "improve" them into writers.** `tools/verify_live.py` and `tools/audit_descriptions.py` must never modify `data/sites.js`. Their whole value is that they are independent of the generator.
- **New repositories are not auto-published.** `build_data.py` skips any repo with no curated `entries` block and prints a warning, so a fresh repo cannot land in the directory with an invented description. Add a sourced entry to `tools/overlay.json` first.
- Pure static site: `index.html` + `styles.css` + `app.js`, zero build step, zero dependencies. `data/sites.js` sets `window.MASTERDATA`; everything in the UI (stats, chips, cards, table, modal, exports) is derived from it at runtime. There are **no** hardcoded repository lists in the HTML/JS.
- **Stamp every entry a pass touches with one pass-completion timestamp** (`entries[*].lastVerified`). `counts.proseReReadLatestPass`, the "Descriptions at Latest Prose Stamp" stat and each entry's *Prose re-read* / *Prose carried* badge are all computed as "shares the newest `lastVerified`", so a pass that stamps as it goes under-reports its own work and badges entries it authored an hour earlier as *carried from an earlier pass*. Per-entry read instants belong in `verifiedBasis`, which is where the detail lives anyway (`IRR-87`).
- **Run an upstream test suite from a clean checkout.** `NFLPARLAYCOMP`'s suite rewrites `docs/site_data/` and `data/competition/verification_report.json` in the working tree, so counting files before `git status --porcelain` is empty measures regenerated output rather than committed state (`IRR-82`).
- **The table's DOM is a contract; the CSS is free.** Nine `<td>` per row in a fixed order, `colspan="9"` on the empty-state row, the repository slug in `span.table-repo`, and the recorded Pages status inside the fourth cell — `tests/directory.spec.js` asserts all four, and the exports are built from the same records. The narrow-screen layout therefore re-stacks those nine cells with CSS alone (`@media (max-width: 900px)` in `styles.css`), printing each field's `data-label` instead of hiding columns, and keeps `<thead>` visually hidden rather than `display: none` so the `<th>` associations survive. **Never drop or reorder a cell to make a layout work.**
- **Row density is a preference, not state.** Compact is the default; the Density button writes `localStorage["masterSite.density"]` and sets `data-density` on `<html>`, and the inline script in `index.html` applies it before first paint. It must never become a URL parameter or a filter: shared links, Back/Forward and **Reset filters** are asserted to produce exactly `{q, category, kind, prose, sort, view}`, and both exports must be byte-identical whichever density is active.
- Published via GitHub Pages from branch `main`, path `/` (`.nojekyll` present).
- The project's core promise is **"zero hallucinations"**. If a claim cannot be re-verified from a repository's own files, delete it — do not soften it into a still-unsupported number.

## 6. If the owner later reverses an exclusion

Only re-list `ProjX` on an explicit, current instruction from the owner in-session. Then: add a `tools/overlay.json → entries` block with API-verified values, re-run both generators, update README counts, and delete the exclusion section from this file.
