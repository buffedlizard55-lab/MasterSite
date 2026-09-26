# MasterSite

The **master list and directory of the GitHub Pages sites published under** [`buffedlizard55-lab`](https://github.com/buffedlizard55-lab) (with a verified audit of [`kanlerxz87-cyber`](https://github.com/kanlerxz87-cyber)) — generated entirely from official GitHub REST API reads, with zero manual data entry and zero hallucinations. One repository is deliberately unpublished by owner request, and four previously verified repositories are frozen as unreachable because they no longer exist upstream.

**Live Directory:** <https://buffedlizard55-lab.github.io/MasterSite/>

---

## Audit status — 2026-09-26 (API snapshot `2026-09-26T00:28:59Z`; **all three read-only verifiers run against that snapshot**)

| Metric | Value |
|---|---|
| GitHub Pages sites published in the directory | **85** |
| Interactive apps / documentation stubs | **73 / 12** — stubs: `11GEMSDOE`, `7GEMSDOE`, `8GEMSDOE`, `GEMSDOE9`, `GEMSDOE10`, `Leg3SeoulTrip`, `MLB-Prediction-model-backtest`, `NFL-PLAYER-PROP-SIM`, `NFLPRED`, `PFFNFL`, `RGENGY` and `StokEngineer` |
| Pages builds reporting `built` | **85 / 85** at the shipping snapshot |
| Descriptions stamped with the commit they were read at | **85 / 85** (`verifiedAtSha`) |
| Descriptions provably behind their repository head *at the snapshot* | **24** — a measured work queue, not a failed verification; the owner pushes to these repositories continuously (`VERIFICATION.md` § 4a) |
| Descriptions re-read in this pass / carried forward | **19 / 66** — eleven new sites read at head plus eight dangling stamps re-read at their live heads; every stamp was then matched against the live head before publication |
| Verifier results | **RUN against the shipping snapshot.** `verify_live.py`: **1115 checks, 1114 ok, 0 hard mismatches, 1 drift** (an asynchronously recomputed size field). `audit_kind.py`: **85 checked, 0 disagreements**. `audit_descriptions.py` with a cleared README cache: **42 accepted exceptions, 0 entries needing manual confirmation**. `npm run check` passed locally; the Playwright browser contract runs in PR CI, not in this sandbox |
| Commits audited across the listed repositories | **4595** at the API snapshot, not a permanent count |
| Public repositories / Pages sites on the account (API) | **86 / 86** |
| Repositories withheld, each with a stated reason | **1** (`ProjX` — permanently excluded by owner request). `listed + withheld = 85 + 1 = 86` is asserted at build time |
| Unreachable entries (needs owner review) | **4** (`JobSearchSF`, `MALTA`, `MALTA-LAWS`, `MALTA2` — previously verified, now HTTP 404) |
| Irregularities registered | **122** (`IRR-01` … `IRR-122`); new this pass: `IRR-115`–`IRR-122` (1 critical, 5 warn, 2 info) |
| Accepted description exceptions / description notes | **42 / 20** |
| Categories | **12** — Sports Data & Scoreboards (31), Science & ML Research (13), Markets & Trading Research (13), Travel & Korea Trip (11), SF Local Guides (7), Gaming & Guides (3), Directory & Meta (2), Reference & Archives (1), Travel & Event Dossiers (1), Elections & Civic Data (1), Health & Personal Guides (1), Social & Creator Data (1) |
| Pages publish sources | **84** from `main /`, **1** (`GOLD`) from `main /docs` |

### What changed in the 2026-09-26 pass — **eleven new sites listed, eight dangling SHA stamps caught and re-read, and one GEMS repository recommending the deletion of the other ten**

The account grew from **75 to 86 public Pages repositories** since the previous snapshot. All eleven newcomers, created 2026-09-25, were curated from their own files and confirmed as built on `main /`: six apps (`5GEMSDOE`, `6GEMSDOE`, `GEMSDOE4`, `NBASCOREBOARD`, `NFLMAIN`, `NHL-SCOREBOARD`) and five single-commit README-only stubs (`7GEMSDOE`, `8GEMSDOE`, `GEMSDOE9`, `GEMSDOE10`, `11GEMSDOE`) (`IRR-116`):

- **Eight `verifiedAtSha` stamps were dangling — the commits no longer exist upstream — and all eight entries were re-read at their live heads before publication (`IRR-115`, critical).** Five of the eight repository heads are byte-identical to the previous snapshot, so those mains moved backwards (force-push, reset or branch recreation) before this pass began; the other three had moved and were rewritten from executed evidence. Every stamp in the shipping snapshot was matched against the live API head.
- **`6GEMSDOE` designates itself the only legitimate GEMS entry and recommends archiving then deleting the other ten GEMS repositories; `GEMSDOE4`'s charter instead plans more sites for more submissions (`IRR-119`, warn).** Both positions are quoted from the repositories' own files; MasterSite lists all eleven and takes no position. Owner decision required.
- **`GEMSDOE4` moved mid-pass and was re-read at its new head.** The adopted candidate is now the k=2-of-5 union at proxy DTI **0.1897** (vs 0.1747 for the 4-member union it replaces, P=0.957 over 9 blocks), but the charter's summary row still reports the retired 0.1864 figure while §0.2 reports 0.1897 — an internal README inconsistency, published with the newer figure and the contradiction flagged rather than hidden.
- **Three README-vs-file divergences found by counting, not quoting.** `5GEMSDOE` commits a failing pytest log for the same stale-committed-pages test class as `GEMSDOE` and `GEMSDOE2` — the third occurrence (`IRR-117`). `NBASCOREBOARD` says "two year-count maps" but the tree holds eight; the README's other three counts match exactly, so the map count alone is stale prose (`IRR-118`). `OLBG-Competition` says twelve of thirteen PnL desks lose, but its own `FACTS.md` shows two positive desks (`IRR-120`). `NBAInjuryReport`'s JS suites fail at head on data decay (167+4, 237+1) while its Python suite passes — the repo's own freshness guards firing, published as-is (`IRR-121`).
- **The verifiers were run against the shipping snapshot and the one finding they reported was resolved, not silenced.** `audit_descriptions.py` flagged `NBAInjScoreboard`'s `403` token as absent from its live README; the claim is still true at head but moved to `LIMITATIONS.md`, so it became the 42nd accepted exception with the move documented. `verify_live.py`'s single drift item is an asynchronously recomputed size field.

### What changed in the 2026-09-25 third pass — two recently published GEMS sites added

The account grew from **73 to 75 public Pages repositories** since the previous snapshot. Both new repositories were curated from their own files, confirmed as built on `main /`, and independently classified as apps (`IRR-113`):

- **`GEMSDOE2`** is a fault-mapping and submission workspace. Its root redirects to a docs/ site with a direct fusion GeoTIFF/ZIP download and a separate browser builder for an earlier ensemble field. The two downloads are **not the same candidate**; the local surrogate score is not an official competition result. Its latest committed upstream Tests log at verified head `9d1aea9` reports **523 passed, 3 skipped, 1 failed**: four committed HTML pages do not reproduce from the generator. Pages is still `built`; the failed test and the ambiguous candidate choice are registered for owner review (`IRR-114`).
- **`GEMSDOE3` (Riftline)** is a separate GEMS fault-mapping research workspace with direct and browser-generated candidate downloads, an executive guide, experiments and a dated source-health feed. Its submission manifest at verified head `9d7c47f` says **unsubmitted; score unknown**. Hosted Riftline verification and Pages deployment both passed for that head. No hidden-label performance is asserted.
- The directory now lists **74 / 75** published Pages repositories; the deliberate `ProjX` exclusion is unchanged and four deleted repositories remain frozen rather than discarded. GitHub's new-repository size field still reads 0 KB for the two new sites at this snapshot despite their nonempty Git trees; it is recorded as asynchronous API metadata, not evidence of empty sites (`IRR-113`).

### What changed in the 2026-09-24 second pass — **five new Pages sites listed, one false placeholder description rewritten, and two listed sites that vanished upstream frozen rather than dropped**

The account moved **70 → 73 public repositories** between the `00:39:08Z` snapshot and this pass. Five new repositories appeared and are now listed, each read in full from its own README and each `kind` re-derived from the published path: `MLBSCORINGCHANGE` (a working copy of the MLB Live PBP replay feed with a 0–100 scoring-change model), `NBAInjScoreboard` (live NBA scoreboard plus an in-game injury desk and replay room), `SIM-COMP-NOBEL-PRIZE` (Nobel Prize record plus a 2,011-participant simulated Kalshi competition), `TAXKALSHI` (a sourced desk for how Kalshi earnings are taxed in California/federal, with a sliding $10k–$200k calculator) and `THUNDERPICKCOMP` (Thunderpick WC 2026 CS2 prediction, ledger and backtesting hub — the sister project to `THUNDERPICK-WC-2026`).

- **`NOBEL-PRIZE` was rewritten from an empty-placeholder stub to a real archive site (`IRR-112`, critical).** The previous snapshot described it as a one-commit, 13-byte-README placeholder. It now holds 12 commits to head `dfd8253`, a root `index.html`, a 4,382 KB tree, and a committed `data/verification-report.json` recording **682 prize records (633 awarded, 49 not awarded), 1,018 laureate entities and 1,026 award slots**. `tools/audit_kind.py` independently re-derived `kind` as `app`. This is the fifth occurrence of the "published as a placeholder" class this directory has caught (`IRR-42`, `IRR-64`, `IRR-71`, `IRR-84`), and the description was rewritten at head rather than patched.
- **Both sites listed in the previous snapshot that no longer exist were frozen, not dropped (`IRR-110`, critical).** `MALTA-LAWS` (3 commits, head `18f3323`, fully verified last pass by executing its own checks) and `MALTA2` (the 8-byte placeholder created minutes after `MALTA` vanished) now both return HTTP 404 and are absent from the account's 73-repository list, so they moved into the *Unreachable — Needs Owner Review* panel with their last verified values, per the standing freeze policy. Counting `MALTA` itself, three of the four Malta-family repositories created on 2026-09-23/24 have now been deleted upstream.
- **`TAXKALSHI` reversed from stub to app while this pass was reading it (`IRR-111`, warn).** At `0a565bb` (23:03:19Z) it was an 11-byte `# TAXKALSHI` README; at `779d4dc` (23:39:45Z), about 36 minutes later, it was a five-commit research desk with `index.html`, a calculator and a ledger. It was withheld from being published as a stub while it grew, the same discipline applied to `PRICINGEXPERT` last pass (`IRR-94`).
- **The three read-only verifiers were run against the shipping snapshot and reported a clean pass.** `verify_live.py`: 946 checks, 0 hard mismatches. `audit_kind.py`: 72 checked, 0 disagreements. `audit_descriptions.py`: 0 entries needing manual confirmation. The Playwright browser contract still runs in CI only.

### What changed in the 2026-09-24 pass — **five newly published repositories listed and read in full, two non-SHA stamps resolved, five irregularities registered, and a repository deleted while the pass was running**

The account gained five published repositories and lost one during this pass. The five that were added — `MALTA`, `MALTA-LAWS`, `MALTASUPPLEMENTAL`, `THUNDERPICK-WC-2026` and `InjuryAlerTNFL` — were each cloned at head and read file by file, and every check the repository ships was executed before anything was written about it. The sixth, `MALTA2`, is an empty placeholder created mid-pass and is listed as exactly that.

- **Five new entries, each written from executed evidence rather than from README prose.** `MALTA` (40 commits): `tests/test_calculate.py` 53 OK, `tests/test_radio.py` 19 OK, `scripts/check_links.py` OK over 10 pages, `node --test` 36/36. `MALTA-LAWS` (3 commits): `unittest discover` 15 OK, `tests/test_site.py` OK over 14 pages. `MALTASUPPLEMENTAL` (9 commits): nothing executable, which is itself the entry's first flag. `THUNDERPICK-WC-2026` (7 commits): `scripts/verify_site.py` OK — 8 teams, 40 players, 8 coaches, 20 ledger entries. `InjuryAlerTNFL` (27 commits): 18 unittest tests OK, 6 node tests OK, 80 incidents and 154 dated claims counted out of `data/archive.json`.
- **The two entries whose `verifiedAtSha` was not a commit SHA are fixed (`IRR-108`).** `KalshiPaperSim` held `AUTO:COUNTS` and `MasterSite` held `main` — auto-generated block labels and branch names that had leaked into a field defined as a commit, making the staleness gate permanently unsatisfiable for exactly the two entries that move most. `KalshiPaperSim` was re-read at head `8a359bd` with its suite executed (**157 tests, 157 pass**) and `MasterSite` is stamped `b1c9765` with the reason recorded in its `verifiedBasis`, including why a self-describing entry necessarily reports stale after its own merge.
- **A repository was deleted while the pass was running and an empty one appeared seconds later (`IRR-109`).** `MALTA` was new to this pass, cloned at head `f0fb352` and verified in full — and then stopped resolving: `GET /repos/buffedlizard55-lab/MALTA` returns 404 and no surviving repository carries its `created_at` of `2026-09-23T17:19:52Z`, so it was deleted rather than renamed. The evidence is in this pass's own output: the build at `00:17:06Z` reported 68 sites and 3,793 commits, and the build at `00:23:27Z` reported 67 sites and 3,753 — exactly MALTA's 40 commits. `MALTA2` was created at `00:22:26Z` with one commit and an 8-byte README. MALTA is **frozen, not deleted from the dataset**, per the policy that keeps `JobSearchSF`.
- **Three cross-repository contradictions and one falsified claim were found by reading the repositories rather than trusting them.** Three Malta-family repositories disagree about whether `community.hotspawn.com` was up on 2026-09-23, and two of them disagree about whether the outage was in the morning or the evening (`IRR-105`). `InjuryAlerTNFL`'s README states its cron has produced *zero* schedule events; the Actions API records one, created 44 minutes **before** that README's own head commit, and it was cancelled (`IRR-106`). `KalshiPaperSim`'s README contradicts its own generated artifact, and the repository's headline honesty claim has reversed from **0 in-play ladders to 2** (`IRR-107`).
- **`KalshiPaperSim` was re-read at head and three of its figures were withdrawn rather than restated.** The Python pipeline the previous entry described no longer exists — `find . -name '*.py'` returns nothing at head `8a359bd`, `scripts/verify.py` and `scripts/trade.py` are gone, and there is no `*/30 * * * *` cron in any of the nine workflows — so its "five PASS / 47 FAIL gates" figure cannot be reproduced. The previous entry's hourly-store totals (436/53/282/23,522), micro-store totals (421/47/283/13,347) and the 19-template/24-code-driven/18-synthetic breakdown were removed because no committed summary block for them could be located, which is this repository's standing rule: **withdraw a figure that cannot be re-derived, never soften it.**
- **The verifiers were run against the shipping snapshot, and the one hard mismatch they reported was handled the prescribed way.** `THUNDERPICK-WC-2026` read `building` through all four of the generator's re-reads and was published as-is; `verify_live.py` then reported it as a hard mismatch; re-running the generator cleared it. Nothing was edited by hand to make a gate pass.

### What changed in the 2026-09-23 pass, second half — **28 stale entries rewritten from executed evidence, all four read-only tools clean, `IRR-91` closed, 10 new irregularities registered**

The first half of this pass is summarised below it. The second half did the thing the first half left open: it re-read **all 28** `PROSE-STALE` entries at head and rewrote them from executed evidence rather than quoted prose. For each one a shallow clone at head was read file by file — generated JSON, markdown and ledger artifacts were loaded with `json.load` and counted, never estimated — and the repository's own gates were run in this sandbox: `pytest`, `unittest`, `node --test`, and each project's `verify.py` / audit script. It closes with **18 entries provably behind their repositories**, `IRR-91` closed, and all four read-only tools clean on the shipping snapshot. **The 18 are the measurement, not a failure:** the rewrites took about two hours, and in those two hours the repositories pushed 18 times. The queue fell 27 → 18 and would have fallen further had the repositories been still.

- **Two more repositories listed: `NFL-PLAYER-PROP-SIM` and `PRICINGEXPERT` (`IRR-88`, `IRR-86`).** `NFL-PLAYER-PROP-SIM` was created at `2026-09-22T23:52:54Z` — four minutes before credentials died — with one commit, a 21-byte README containing only its own heading, and no `index.html` (`GET .../contents/index.html` → HTTP 404). It is described from exactly that and from nothing else: no inference from its name, in a directory that has now watched ten repositories grow engines within hours of being created as stubs. `PRICINGEXPERT`, curated offline an hour earlier, was listed by the first full build. The directory went 61 → **63**; the account 63 → **64**.
- **`LSTARENGY` was published as a four-file documentation stub and is now a 60-file research site (`IRR-90`, critical).** Three commits and 60 files at +18,628/−7,768 after the stamp. Its `npm run check` was **executed** in a clean clone rather than quoted, and passed all three gates: `1..72 / # pass 72 / # fail 0` on Node v22.22.3, `Traceability valid: 36 capabilities, 30 sources, 62 legacy review groups`, and `Verified 22 deterministic site assets. Both main:/ and main:/docs entrypoints are supported.` Every register count was then counted a second time in `docs/data/catalogue.json` and `docs/data/legacy-audit.json`. The repository's own corrections section also **withdrew a price this directory had published as fact** — the entry said "239.99 USD per year" where the vendor's web page and its US app listing display two different dated offers ($239.99 and $269.99). `tools/audit_kind.py` caught the reclassification; the prose gate caught the README change. Only the kind verifier would have caught it had the site been built without touching the README, which is the `IRR-70` case and the reason that tool exists separately.
- **`NFLPARLAYCOMP` transformed a second time *during* this pass (`IRR-89`, critical).** Re-read at `fef877f`, its `total_pnl` now reports `0.00` while its own bankroll rows sum to **−81,924.29** — a headline figure and its components disagreeing inside the repository's own data. Both are published, with the disagreement flagged rather than resolved by picking one.
- **`Elections` rewritten at `c41cc79`, and its Pages build recovered (`IRR-83` closed).** `errored` after two consecutive `Page build failed.` builds for more than five hours, now `built` with a successful build above the two failures — the first Pages failure this directory caught and the first it watched recover, which is evidence the four-read retry loop distinguishes broken from in-progress in both directions. All **63** entries now report `built`.
- **One open description CHECK, left open on purpose (`IRR-91`).** `TradingViewTheLeap`'s `$20.56` forward miss and `196`-date roll schedule are verbatim in the README audit banner at the stamped commit `5b14c89` and absent from it at head `d09a594`, which 14 commits of the automated lane moved past them. Superseded, not fabricated. No `acceptedDescriptionException` was added, because an exception would permanently silence a signal that is genuinely informative, and the figures were not deleted, because they are re-verifiable at the ref the entry cites and they record a pre-registered hypothesis (`C23`/`H43`) that was refuted on its first full-pool run. The description now says in-line that both come from the banner at `5b14c89` and have been superseded.
- **The stale queue grew while it was being worked (21 → 24 over six full builds).** Account commits read 3,526 → 3,533 → 3,540 → 3,543 → 3,545 → 3,559 → 3,561 across the pass; `MLB-Live-PBP` was pushed at `01:20:19Z`, about a minute after the snapshot read it. Two `building` states produced the only hard mismatches `verify_live.py` reported all pass, and both were cleared the prescribed way — re-running the generator — rather than by editing data. The largest open movers are `NBAComp` (58 commits ahead of its prose), `KalshiPaperSim` (48), `Commodities` (34) and `OLBG-Competition` (22). Each is badged in the UI with the SHA its prose was read at and the SHA the repository is now at.
- **`PRICINGEXPERT` was an empty stub when it was curated and is now a 72-file Kalshi research desk whose green verification gate has never seen a trade (`IRR-94`, critical).** The `01:37:24Z` snapshot read `main` at `49a5625`: one commit, a 15-byte README, no `index.html`. That was accurate — the project was on a branch, and three PR merges put it on `main` at `02:25:30Z`, `02:27:41Z` and `02:28:34Z`, 48 minutes later. Both gates were **executed** in a clean clone: `pytest tests/ -q` reported **19 passed**, and `scripts/verify.py` exited 0 with **42 passing checks and 0 errors**. Decomposing those 42 by code prefix shows what they cover — V1 hash 6, V2 manifest 7, V5 cash 10, V10 rule-implemented 10, V11 season 3, V13 ledger hygiene 6 — and what they do not: **six of the thirteen check families (V3, V4, V6, V7, V8, V9) recorded nothing at all**, because `trades.jsonl`, `intents.jsonl` and `marks.jsonl` are each 0 lines, there are 0 cycle directories and 0 captured order books, and the leaderboard the site publishes reports `cycles_completed 0` with all ten personas on exactly $10,000.00. The gate is real and green; its trading-mechanics half is unexercised, and the entry says so. Two reporting traps are recorded with it: `verify.py`'s pass messages are phrased as the failures they did *not* find (so `passed: 42` prints beside strings like `V1: hash mismatch exchange-status.json`), and it writes `data/site/link-audit.json` as a side effect — byte-identically in a clean clone, so `git status` stayed empty.
- **Credentials died a third time, between finishing the toolchain and publishing it — and the resume procedure caught a real defect (`IRR-93`).** `git push` failed at `01:44Z`, about one minute after the last verifier succeeded; `gh auth status` reported the `GH_TOKEN` invalid, `gh api` returned `Bad credentials`, and `/rate_limit` returned HTTP 401 **with no `Authorization` header** — the `IRR-85` egress signature. Nothing was pushed and nothing was claimed as published; the narrative was landed offline with `build_data.py --overlay-only`, which makes no network call, so every API-derived field kept reporting the `01:37:24Z` read rather than a guess. Credentials returned at ~`02:24Z`, and the recorded resume procedure — *re-run everything, because the snapshot will be old* — was followed exactly instead of pushing the 47-minute-old work. That re-run is what caught `PRICINGEXPERT`'s reclassification above: **shipping the pre-outage snapshot would have published a 72-file research desk as an empty stub.** Nine full builds later, all three gates were clean on the snapshot that shipped.
### The 28 re-reads, and what they found (2026-09-23, second half of the pass)

Every entry below was rewritten because its prose no longer matched its repository head. The rule applied
throughout was the owner's: **if a figure cannot be re-derived from the current tree it is withdrawn, not
softened.** Eleven figures the previous entries published were withdrawn on exactly that basis.

**Central claims that were simply false at head.**

- **`MLBComp` — the headline fact reversed.** The previous entry reported `settled_bets` still `0` and
  `total_simulated_pnl` still `null`, and that all 144,098 records resolved to `EVAL` and `PROPOSED`. At head
  `c6332b9` the repository's own `data/summary.json` reads `settled_bets` **33,143** and
  `total_simulated_pnl` **−$96,903.05**, because the gate requiring a verified timestamped quote has since
  been satisfied by the `bettingtools` and `cesar-dx` historical moneyline files. The six
  `environment_breakdown` figures sum exactly to the headline (−78,399.80 − 14,352.65 − 3,537.48 + 3,065.35
  − 4,420.41 + 741.94), and the audit control `no_unverified_pnl` still reports 0 unverified rows with
  non-zero PnL — so every one of those settlements carries a verified price. The source it did find is still
  `PARTIALLY_VERIFIED` and still ineligible for wager eligibility specifically because `cesar-dx` carries no
  `observed_at` / `available_at` timestamps.
- **`NFLComp` — the named top performer is gone.** The previous entry reported `@AltSpread_Value_v2` at
  +27.15% ROI and +$145,992.37. At head `7ec80df` the repository's own table lists that strategy as
  `n/a (open)` with **0 bets**, and the top performer is `@AnalyticsCoach_ATS_v1` at +$3,839.32 / +4.16%.
  The simulated ledger is 97,218 wagers at −$531,192.71, not 134,255 at −$353,618.85, and the roster is 70
  personas across 17 categories, not 60.
- **`Commodities` — the README and its own artifacts disagree.** The README's archive-backtest banner reads
  `63 markets · 2,455 verified bars · 291 trades`; the committed files it describes read **74 markets, 2,736
  verified bars and 337 trade rows** across 266 distinct ids (`IRR-97`). Both are published, with the
  generated files as the number of record.

**A defect in this directory's own previous entry.**

- **`Elections` — the source counts were mis-counted by us, not by the repository (`IRR-95`, critical).**
  The previous entry published "6 live-only and 4 excluded sources". That is `len()` of each file's
  top-level dict, not of its `sources` array. The arrays hold **20** and **7**. The repository's own README
  said so the whole time — `data/master_sources.json — 20 live-only entries`, `data/flagged_sources.json — 7
  excluded with reasons`. So the directory understated itself by 17 sources while the README it was
  checking against was correct. Corrected in this pass, and recorded because it is the same class of error
  `audit_descriptions.py` exists to catch.
- **`Elections` — one quantity, four figures (`IRR-96`).** The captured open universe file holds
  **24,141** markets from 4,226 of 4,226 eligible series with `complete: true`; the README's file table
  says 24,150, its canonical-list section says 24,102 and its All Markets paragraph says 24,139.

**Repositories whose own documentation is stale against their own generated files.**

- **`TradingViewTheLeap` (`IRR-101`)** — the README's limitations section still states
  `data/intraday/ currently holds 29 of 60 stock series ({15m: 15, 1h: 9, 1d: 5})`, a September 19 state.
  Its own `intraday_index.json` at the same head records **60 equity series** over 20 symbols × {15m, 1h, 1d}
  plus 20 futures captures, with `captured_count 61`, `failed_count 9` and `not_attempted_count 10` — so
  the equity matrix is complete and only 1 of 20 futures series landed.
- **`NFLInjuryReport` (`IRR-104`)** — the README says data is refreshed **every 10 minutes**; the workflow
  at the same head carries four staggered cron entries at a five-minute cadence and its own comments record
  an observed gap of **188 minutes** and a worst of **412**, because GitHub throttles and queues scheduled
  workflows on free runners.
- **`MLBRainDelay` (`IRR-103`)** — `docs/verification.md` prints `67 assertions across four suites (26 + 24
  + 11 + 6)` and the README prints `100+ passing assertions`. Executing the suites gives **32 / 25 / 9** for
  the three the entry names, plus 25 and 18 for two more — 109 in total. The three figures the previous
  entry published (26 / 24 / 6) are superseded.
- **`MLBComp` (`IRR-98`)** — the README's rebuild note still says `18 adversarial controls` where the
  exported audit file holds **22**, all passing.
- **`GEMSDOE` (`IRR-102`, critical)** — `python3 -m pytest tests -q` gives **467 passed, 32 skipped, 1
  FAILED**, the failure being `test_the_build_reproduces_the_committed_pages` — the committed site pages
  are not the pages the generator produces. `STATUS.md` session 23 claims `445 passed, 1 skipped`, which
  matches neither the executed pass count nor the executed skip count.
- **`StokEngineer` (`IRR-100`, critical)** — `pytest` reports **84 passed, 3 skipped, 1 FAILED**
  (`test_stack_constraint_produces_a_qb_stack`, raising `_BudgetedOut: no legal lineup exists under these
  constraints`), while `python -m src.stokengineer.cli verify` prints `verify: OK`. The suite disagrees with
  the gate the repository points readers at.

**A bookkeeping contradiction published rather than resolved.**

- **`NHLComp` (`IRR-99`, critical).** `docs/data/competition.json` (generated 2026-09-23T02:03:46Z) records
  the FORWARD TEST phase as **0 bets, 0 settled, 0 open, PnL 0.0, ROI null**. The same repository's
  `docs/data/bets.json`, loaded in full, holds **127 FORWARD TEST rows**, every one `result: OPEN` with
  `pnl: null`, and the leaderboard's forward rows additionally carry 1 preseason settled bet of +$53.26
  explicitly flagged `scored_in_competition: false`. The two artifacts disagree on whether the forward book
  has activity. Both are published. The likely explanation — the forward ledger is not the table the
  roll-up reads — is an inference and is therefore not asserted.

**Figures withdrawn because they are not re-derivable at head.** The previous entries' `38 sources` / `71,004
bytes` / `155 badges` / `24-line claim log` / `7 flagged irregularities` for `StokEngineer`; its
`24-line` framing of what is now an 89-line mechanism description with the claim log moved to
`src/data/claims.json`; `TradingViewTheLeap`'s `$20.56` refutation margin and its
`401 passed / 459-check / 94-unit-test` figures; `DrugAnalysis`'s v27 row counts (1,000 new decisions, 2,969
openFDA decisions, the 1,933-row analysis table, the 485-row scorecard, the 2,848-row price index, the
`90.6% Phase 1→2 on n=1453` base rates); `VacationSchedule`'s 42 tests, 53 review items and 21
irregularities; `Coupons`' 185/18/517 and `SocialMediaComp`'s 60 entries in four batches of 15;
`SelfLearn`'s 89 documents, 141 questions, 22 failures, 35 irregularities and 156 tests. Each replacement
figure was counted or executed in this pass, and each `verifiedBasis` names the file it came from and the
commit it was read at.

**What the executed gates turned up that the prose did not.** Running the repositories' own test and
verifier commands is the only reason several of the above are visible at all, and it also produced the
passes: `MasterSelfLearn` **350 passed in 13.40s**; `SelfLearn` **189 passed**; `StockPaperSim` **697
passed** plus `independent_audit_season2.py` at **5,513 checks, 5,513 passed, 0 failed** with a custody note
of **327 files byte-identical**, and `independent_audit.py` at **763 and 611** (1,374 total);
`OLBG-Competition`'s suite green at **499 collected cases** from **441 test functions**; `GEMSDOE`'s
`validate_submission.py` passing all 8 checks on a freshly written submission whose sha256 matched the
committed artifact byte for byte; `NFLComp`'s **33 of 33** audit controls; `NFLInjuryReport`'s **222** tests
across 15 modules; `VacationSchedule`'s **125**; `MLB-PBP`'s 6 Python tests plus 15 Node tests; `SABERENGY`'s
10 core tests passing and its NFL suite skipping 2 for want of a reachable weekly file; `PRICINGEXPERT`'s
`verify.py` at **1,198 passed, 0 errors** with 39 pytest tests, against 42 and 19 at the previous read; and
`TradingViewTheLeap`'s `verify.py` at **444 passed, 0 failed, 1 warning**. Two gates could not be exercised
and are recorded as limits rather than passes: `MLB-Live-PBP`'s `smoke-test.mjs` fails here only because it
fetches live `statsapi.mlb.com`, which this sandbox cannot reach, and `GEMSDOE`'s suite needed
`rasterio`, `scikit-image`, `torch`, `pyyaml` and `tqdm` installed before it would even collect.

- **Interface work from the previous pass is unchanged and still unexercised by a browser here.** Compact-by-default rows, the per-browser Density toggle and the sub-900px stacked table are documented below; the four tests added for them run in `.github/workflows/test.yml`, including `mobile-chromium`. The DOM contract was verified offline in jsdom (39 checks); layout is only observable in a real browser, so no local Playwright run is claimed.

### What changed in the 2026-09-22 pass — **61 sites listed, 10 new repositories, 21 provably stale, verifiers blocked**

The account grew **53 → 63 public repositories in about 23 hours**, the fastest growth this directory has tracked. Nine of the ten new ones are listed; the tenth is fully curated and waiting on a build.

- **`IRR-80` — ten new repositories, the third time one appeared *while* the audit was running.** `Coupons`, `FLABSENGY`, `FUTURESCOMMODITIES`, `LSTARENGY`, `NFLPARLAYCOMP`, `ParlaySports`, `RGENGY`, `SABERENGY` and `StokEngineer` were each described from their own files, never from their names. `PRICINGEXPERT` was created at `23:01:18Z`, discovered by the `23:32:49Z` build, correctly withheld for want of a curated entry, and then curated — but `--overlay-only` cannot add a site, so it is the one entry in `overlay.json` with no row in the directory (`IRR-86`).
- **`IRR-82` (critical) — `NFLPARLAYCOMP` changed almost every published figure, including the sign of its headline PnL, in the 40 minutes between being read and being written.** Read at `241d392`: 100 users, 32 ledger lines, 32 trades, **+135.04**. Re-read at `84f138f`: 1,000 users, 2,705 ledger lines, 1,623 trades, **−92,876.56**, 2,975 `UNVERIFIED_DATA` flags and a new root `index.html` forwarder. The whole entry was discarded rather than patched. This is the `IRR-65` failure class reached *without* shipping the wrong number, because the staleness gate fired first.
- **`IRR-84` (critical) — `SelfLearn` and `MasterSelfLearn` were published as empty one-file placeholders and are now research engines.** 31 commits / 234 files and 42 commits / 111 files respectively; both test suites were **executed**, not quoted (`Ran 156 tests … OK`, `Ran 350 tests … OK`). `MasterSelfLearn` commits its own output on a `*/30` cron, so its entry now carries a durable rule: a `PROSE-STALE` report against it is expected, and the triage is to compare cycle numbers. Fourth and fifth occurrence of the `IRR-42`/`IRR-64` class.
- **`IRR-83` — `Elections`' GitHub Pages build is failing.** `/pages` reports `errored` and build `1232488579` reads `Page build failed.`; it persisted through four automatic re-reads, so it is recorded as a defect rather than a transient `building` state (`IRR-53`). It is the only non-`built` entry of the 63. GitHub serves the last successful build, so nothing here infers the live URL is dead — or healthy.
- **Three entries reclassified `stub` → `app`** (`NFLPARLAYCOMP`, `SelfLearn`, `MasterSelfLearn`), taking the split to **54 / 7**. Each was re-derived from `GET /repos/{owner}/{repo}/contents/index.html` at the commit the entry was read at, not carried.
- **`IRR-85` (critical) — credentials expired mid-pass, and the three verifiers are recorded as blocked, not passed.** `api.github.com` returns HTTP 401 `Bad credentials` *even with no `Authorization` header*, because the sandbox egress path injects the expired token, so the unauthenticated tier is not a fallback; `raw.githubusercontent.com` returns HTTP 000 and `git clone` fails outright. A full `build_data.py` refresh had already completed at `23:32:49Z` with live credentials, so every API-derived field in the snapshot is from that read. The narrative work after it was landed with `--overlay-only`, which makes no network call.
- **`IRR-86` — landing offline exposed a real defect in `--overlay-only`: it could not render `kind`.** `main()` sources `kind` from the overlay, so it is a curated field, but `OVERLAY_FIELDS` omitted it — which meant the mode would have republished `stub` for three repositories this audit had already proved were apps. `kind` is now rendered, and `counts.apps` / `counts.stubs` are recomputed beside the category tally because `build_verification.py` quotes both.
- **`IRR-87` — the prose counter measured the wrong thing.** `counts.proseReReadLatestPass` counts entries sharing the single newest `lastVerified`, so a pass that stamps as it goes under-reports its own work (this one printed `2` for 12 entries) and the UI then badges brand-new entries as "Prose carried", which `VERIFICATION.md` §4a defines as *from an earlier pass*. The twelve stamps were normalized to the pass stamp instead of redefining the counter, which would have needed a pass boundary the data does not carry.
- **The interface became readable at both ends of the screen.** The table is **compact by default** — tighter rows, a fixed-width name column with the curated title clipped to one line (the longest is 78 characters) and the repository slug beside it — with a **Density** toggle that restores the padded layout and is remembered per browser. Under 900px the same nine cells re-stack into labelled lines per entry, so a phone gets a card per site instead of a ~1,000px table behind a scrollbar. Density lives in `localStorage` and never in the URL, so shared links and **Reset filters** still produce exactly `{q, category, kind, prose, sort, view}`.

**Not done, and not claimed:** the 21-entry staleness queue was not triaged, because triage needs a compare endpoint and a README read per entry and both were unavailable after `23:55Z`. `MasterSelfLearn` is one of the 21 for an unusual reason — its prose was read at `eda549e`, which is *newer* than the `fe488ed` head the snapshot recorded, so the gate reports an entry that is ahead of its own snapshot. Re-stamping it backwards to silence the gate would mean claiming the prose was read at a commit it was not read at (`IRR-86`).

### What changed in the 2026-09-21 pass — **52 sites, 0 stale, 3 verifiers clean**

This pass opened with **20 of 50 entries reporting `PROSE-STALE`** and closed at zero. It found **two false published descriptions**, both critical, and **three upstream repositories whose own README disagrees with their own data files**.

- **`IRR-64` (critical) — `MLBComp` was published as a "placeholder repository".** True at `8191096`; by `179c599` the repository had 11 commits, a root `index.html`, a 68-strategy catalog and a full site. Worse, the repository had *withdrawn its own fabricated data* in between (`d069579` "Withdraw fabricated competition data", `5d3c73e` "Remove fabricated claims left in the site's static HTML"), reverting an interim state that advertised 58 strategies across 17 categories. Rewritten from its own files.
- **`IRR-65` (critical) — `NFLComp`'s published PnL had changed sign.** The directory claimed **+$2,434,194.80** profit, 28 personas and 55,974 wagers. `data/summary.json` reports **−$353,618.85**, 60 personas and 134,255 wagers, with a different top strategy. A sign error on a headline financial figure is the worst class of stale prose this directory can carry.
- **`IRR-72` — `MLBComp` then changed again *during* the audit,** from `data_mode: NO_SOURCE_SNAPSHOT` to `SOURCE_SNAPSHOT` (0 → 144,098 ledger records), forcing a second rewrite of a description written an hour earlier. Its honesty property survived: `settled_bets` is still 0 and PnL still `null`, because the quote gate resolves all 144,098 records to 118,214 `EVAL` and 25,884 `PROPOSED`.
- **`IRR-67`, `IRR-68` — two repositories whose README is older than their own data.** `Elections` says "209 sources" in one place and "189 verified entries" in another; the file holds **229**. It says 63 irregularities; the file holds **58**. `NBAInjuryReport`'s README quotes a reporter sweep "re-measured 2026-09-19" at 65/21/47/18, while `data/live/reporter_verify.json`, regenerated 2026-09-21T15:53Z, reports **94 handles checked, 70 ok, 24 dormant**. In both cases this directory publishes the **counted file values** and flags the prose.
- **`IRR-66` — three entries moved `stub` → `app`** (`MLBComp`, `NHLComp`, `VacationSchedule`), each having added a root `index.html`. The long-standing `IRR-43`-class finding ("built site lives in `docs/` but Pages publishes `main /`") is now **resolved for every affected repository**. `VacationSchedule` was rebuilt so completely that its description was replaced wholesale and three unverifiable numeric claims were **withdrawn rather than softened**.
- **`IRR-69`, `IRR-71` — three new repositories, one of them substantial.** `MLBRainDelay` (created 2026-09-21T02:00Z) was verified by **executing its test suites**, not quoting them: 26 + 24 + 6 = 56 assertions passed on Node v22.22.3, and its captured `gameStatus` registry was parsed to count exactly **210** rows. `SelfLearn` and `MasterSelfLearn` were created **22:41Z, while this audit was running**, and are genuine one-line stubs — described from their contents, with the obvious inference from their names deliberately **not** published.
- **`IRR-70` — the methodological finding of this pass: the README changed in only 13 of the 20 stale ranges, yet four of the five sharpest findings came from ranges that touched no README at all.** `GEMSDOE` had a whole session in `STATUS.md`; `NBAInjuryReport` produced `IRR-68`; `SFWeather` added an entirely new published tier; `TradingViewTheLeap` moved its audit banner past our prose. **A README-unchanged compare justifies triage, never a silent re-stamp.**

Six repositories changed state *during* this audit (`MLBComp` twice, `DrugAnalysis` v26 → v27, `NFLComp`, `NFLInjuryReport`, `Commodities`, `VacationSchedule` twice), requiring six successive builds before the gate reached zero.

---

<details>
<summary>Earlier audit passes (2026-09-20 and before)</summary>

**What changed in the fourth pass of 2026-09-20** (`05:15:50Z` → `22:33:11Z`): **49 sites, 0 stale, 3 verifiers clean**

- **Account grew 45 → 50 public repositories, all 50 Pages `built` (verified per-repo via GET /repos/buffedlizard55-lab/{repo}/pages).** Five new repos appeared between the third and fourth pass: `MLBComp` (created 2026-09-20T18:36:45Z, 1 commit, size 0, placeholder README '# MLBComp', stub), `NBAComp` (created 2026-09-20T18:37:59Z, 22 commits, 132 KB, autonomous NBA betting-strategy lab with 14 strategies $1,000 each, window 2026-09-20→2027-09-19, app), `NFLComp` (created 2026-09-20T18:37:22Z, 6 commits, 2256 KB, autonomous NFL research with 28 personas across 14 disciplines and 55,974 wagers, app), `NHLComp` (created 2026-09-20T18:37:41Z, 3 commits, 1268 KB, autonomous NHL paper-betting research platform with 66 unit tests and standard library only, built site in docs/ but Pages publishes main / with no root index.html so stub — same class as VacationSchedule IRR-43), `SocialMediaComp` (created 2026-09-20T17:01:27Z, 7 commits, 32 KB, competition-style leaderboard of 40 high-reach social accounts across TikTok/Instagram/Facebook/Reddit with cited sources, app). All five had no curated overlay entry, so generator withheld them with warning until described from their own README — anti-hallucination behavior (`IRR-63`).
- **13 stale entries detected and refreshed.** `Commodities` baf0ff0→1f1637d (7 commits, forward desk data), `DrugAnalysis` b6cdb8a→8fc95a4 (v21.1→v21.x, 147 commits), `Elections` facd343→52f177d, `GEMSDOE` 0ca1466→66450f7 (206 commits, size 400,408 KB), `KalshiPaperSim` f37eeaa→27f5a4e (142 commits, moved twice during build — b4f3cc2→27f5a4e is data-only chore), `MasterSite` f2aa71e→be500b6 (22 commits), `NBAInjuryReport` 190b052→39d7ac5 (255 commits), `OLBG-Competition` 8b0bd8c→bee5457 (32 commits), `SFWeather` a599aa6→c39264a (166 commits, automated data refresh), `ShoulderPain` 06eec87→1076d10 (26 commits), `StockPaperSim` 560efa8→9618a43 (119 commits), `TradingViewTheLeap` 6d8f0ef→e418756 (165 commits), `VacationSchedule` 6488222→aad0fdd (9 commits). Descriptions re-verified via tools/audit_descriptions.py — 0 unresolved, 7 accepted exceptions — and stamps updated.
- **New category:** `Social & Creator Data` (1) for SocialMediaComp. Sports Data & Scoreboards grew 13→17. Total categories 9→10.
- **Verifier results:** `verify_live.py` 647/647 checks 0 hard 0 drift; `audit_descriptions.py` 0 needing manual confirmation (7 documented exceptions); `audit_kind.py` 49 checked 0 disagreements (VacationSchedule now has hardcoded kind stub).
- **Gate:** final build reports `prose: 1 re-read this pass, 48 carried, 49 stamped with a SHA, 0 provably behind their repo` — completion gate.

**What changed in the third pass of 2026-09-20** (`03:06:19Z` → `05:15:50Z`, after GitHub credentials were restored):

- **The rebuild was run first, exactly as `IRR-55` prescribed — and it was necessary.** The gate immediately reported **4 entries behind** (`Commodities`, `KalshiPaperSim`, `ShoulderPain`, `TradingViewTheLeap`); commits had moved 2,360 → 2,398. All four were re-read and rewritten. The *next* build reported **4 different entries** behind (`OLBG-Competition`, `SFWeather`, `ShoulderPain` again, `StockPaperSim`) — nine minutes after they had been re-read (`IRR-61`). After those were triaged, a further build caught `GEMSDOE` and `SFWeather` a fifth time. **The gate fired 17 times across 7 builds on 10 distinct repositories before the eighth reported `0 provably behind their repo`** — `SFWeather` alone was re-read against five successive heads.
- **`IRR-62`: the re-read found a defect in *this directory's own* prose.** `GEMSDOE` moved via a `[skip ci]` commit touching 6 evidence files at +1/−1 each, with `README.md` and `STATUS.md` both unchanged — so no SHA comparison could ever have flagged the problem. Opening the evidence anyway showed `fold0_two_population_contrast.json` now reports a *different* verdict (`GAIN_ON_THE_COMBINED_SURROGATE`, proxy +0.0677 / catalogue −0.1079) than the one published here (`TRADE_OFF_PROXY_GAINS_CATALOGUE_LOSSES`, +0.1036 / −0.0874). `STATUS.md` documents **both** fires and states plainly that "quoting either one alone would overstate the precision" — which is precisely what the published description did. Corrected to carry both fires, the ~0.036 replicate swing, the scope sign-flip on the union and the P = 0.916 reading against the rule's own P ≥ 0.95 bar.
- **`ShoulderPain` reversed its own method** (`IRR-57`): 56 sources → **20**, four review passes → three, 32 logged corrections → 8 source irregularities, a 32-row irregularity table → 6 rows, and it gained a real build/test pipeline. Its stated reason is quoted on the entry: *"Further expansion should improve evidence rather than inflate a count."* A directory that counted sources as a quality proxy would have scored this as a regression. Nine minutes later it moved again (`IRR-61`) and its ledger count went 89 → 90, confirmed by re-fetching `data/claims.json`.
- **`Commodities` replaced its browser-runtime desk with an unattended collector** (`IRR-56`): 20 personas trading on paper twice an hour from GitHub Actions, committing every fill, intent, mark and order book back into the repo. **`KalshiPaperSim`'s `AUTO:COUNTS` moved for the third consecutive audit** (`IRR-58`): 101→104 facts, 43→48 strategies, 125→128 tests, leaderboard 28→32 ranked. **`StockPaperSim`** landed a real SEC Form 4 lane (65 filings / 99 transactions, 634→648 tests). **`TradingViewTheLeap`** completed its 60/60 matrix — but only in the README *banner*; `C22`, `C19-A`, `H41`, `H42` appear nowhere in its body (`IRR-59`).
- **`IRR-60`: a sibling repository audits *this* directory.** `KalshiPaperSim` keeps a signal-source ledger that reviewed MasterSite site by site on 2026-09-18. Three of its claims were checked: no coverage gap (`PriceKalshiHistorical`, `PFFNFL`, `NFLPRED` all listed), one corroboration (`NFLPRED` a stub — its root holds a single 9-byte `README.md`), and one finding against us that has since been fixed twice over. Its `PinePilot` row, however, cites a repository that returns **HTTP 404**.
- **All three verifiers finally ran clean**: `verify_live.py` 582/582 checks with **0 hard mismatches and 0 drift**; `audit_descriptions.py` **0 entries needing manual confirmation** against 7 documented exceptions; `audit_kind.py` 44/44 re-derived with **0 disagreements**. The blocked second-pass artifacts were replaced by real runs.

**What changed in the second pass of 2026-09-20** (`01:17:26Z` → `03:06:19Z`, every item re-read against the repository's own files):

- **Prose staleness is now a computation, not a judgement call.** Each entry records `verifiedAtSha` — the default-branch commit its description was actually read at — and the generator compares it with the live head SHA at build time, printing `PROSE-STALE` lines and refusing to finish silently. The pass ended at **44/44 stamped and 0 provably behind** (`IRR-50`).
- **The detector immediately proved itself, catching five repositories that moved *during* the audit.** `GEMSDOE` (`1b341d2`→`3093c6b`, session 18→19: fold scores, union population and test count all moved — description rewritten), `DrugAnalysis` (`6cb77f6`→`b6cdb8a`, v21→v21.1 — rewritten), `OLBG-Competition` (`a371b63`→`fee61ea`, an entire ice-hockey pipeline added and 126→144 tests — rewritten, `IRR-54`), `VacationSchedule` (`83663f7`→`6488222`, **every** recommended window changed — rewritten twice, `IRR-52`), plus `SFWeather` (`d5b1030`→`42f9892`) and `ShoulderPain` (`10e62a4`→`e1c63c4`), both confirmed benign by line-by-line README diff. The two that mattered most — `DrugAnalysis` and `OLBG-Competition` — were *carried* entries a human auditor would least think to re-check.
- **`VacationSchedule` is no longer a placeholder.** Ten minutes old and 18 bytes at the first pass, it is now a full project, and its own numbers moved twice inside two hours: review items 50→53, tests 39→42, parity dates 94→95, and the strict-reading windows from 11/4/5/7 days to 11/8/8/8 with 2027 shifting from Feb 15-18 to Feb 1-8. Its 2027 MLB schedule is now VERIFIED rather than ESTIMATED.
- **Two new irregularities found by counting rather than reading.** `VacationSchedule`'s README claims "16 flagged irregularities" while its register actually holds **21** — `IR-17`…`IR-21` were appended as `###` headings, and they include the resolution of the HIGH-severity item the README still describes as open (`IRR-51`). Its 42 tests were independently confirmed as 35 + 5 + 2 `def test_` methods rather than taken on trust.
- **A transient Pages status was caught and handled.** One build recorded 43/44 `built` because `SFWeather` reported `status: 'building'` seconds after its own automated data refresh; a re-read 12 s later showed all 44 `built`. `status` is a live deployment state, not a repository property, so the generator now re-reads a non-`built` status up to four times before recording it, and still records a genuinely broken build (`IRR-53`).
- **12 descriptions re-read, 32 carried** with a stated basis, and 6 documented description exceptions (5 entries plus the register's own `__doc__`).
- **This pass could not be pushed.** GitHub credentials expired at ~`03:07Z`, one minute after the successful snapshot: every API read returns HTTP 401 (including unauthenticated ones) and `git push` has no credentials. The final live re-verification, the description audit and the pull request are therefore outstanding (`IRR-55`, critical).

**What changed since the 2026-09-18 audit** (every item re-verified line by line against the API):

- **4 new Pages sites added, all created after the last audit:** `OLBG-Competition` (created **2026-09-19T18:11:58Z** — the "Northstar" tipster paper-trading lab), `ShoulderPain` (**2026-09-19T21:41:43Z** — a nine-page sourced shoulder-pain/ergonomics guide), `Commodities` (**2026-09-19T21:42:20Z** — a Kalshi research exchange with a hash-bound season memory) and `VacationSchedule` (**2026-09-20T00:48:59Z** — created *roughly ten minutes before this snapshot's data was generated*, an 18-byte README placeholder listed from its file listing alone, `IRR-41`). The account grew 41 → 45 public repositories; all 45 report Pages `built` (`IRR-32`).
- **`Elections` had to be rewritten again — the same error class as `IRR-25`.** The 2026-09-18 audit listed it truthfully as a single-commit 11-byte placeholder. Two days later it holds 46 commits, an ~18.6 KB README and a full verification-first election-intelligence project (125 verified sources, 39-market 2024 backtest, 24,367-market live capture). The old description was not wrong when written; it was false by this audit. Registered as `IRR-33`, reclassified stub → app, moved to its own `Elections & Civic Data` category.
- **8 more entries updated with new default-branch commits:** `DrugAnalysis` 103→125, `GEMSDOE` 167→199, `KalshiPaperSim` 70→108, `NBAInjuryReport` 160→250, `SFWeather` 112→145, `StockPaperSim` 87→112, `TradingViewTheLeap` 85→134, `WoWForever` 13→51 — and every one of their descriptions needed editing after re-reading the repository (`IRR-34` … `IRR-40`).
- **6 stale descriptions corrected:** `KalshiPaperSim` (AUTO:COUNTS moved on every figure for the *second* audit in a row — `IRR-34`), `NBAInjuryReport` (the quoted test counts 212/80/71/25/24/47 no longer appear *anywhere* in its README; they were deleted, not restated — `IRR-35`), `TradingViewTheLeap` (five research passes behind; R9's 96,707 participants superseded by R10's 99,663 — `IRR-36`), `StockPaperSim` (Season 2 roster 14→19 — `IRR-37`), `WoWForever` (9→14 pages, C001–C110 → 183 claims, I-7 → I-24 — `IRR-38`), and `DrugAnalysis` (v14 → v21: Phase 3 registry 4,212→10,664 studies, snapshots 979→2,848 rows, pre-1980 table back to 1965 — `IRR-40`). `GEMSDOE`'s description now follows `STATUS.md` (sessions 9 → 18) because its README declares its own body partly superseded (`IRR-39`).
- **30 entries re-verified byte-identical** (same latest SHA, same commit count) and 2 more with moved pointers whose descriptions still read true (`SFWeather`, `MasterSite`).
- **`JobSearchSF` re-confirmed gone for a third audit:** still HTTP 404, still `total_count 0` in the search API, still absent from the account's now-45-repository public list (`IRR-01`).
- **Verifier results (first pass, `01:17:26Z`):** `tools/verify_live.py` — 582 field checks, **0 hard mismatches** (1 asynchronous `size` drift, folded in on the next refresh); `tools/audit_descriptions.py` — 44/44 entries pass, 0 unresolved claims. See [Verification & Integrity Policy](#verification--integrity-policy).
- **Verifier results (second pass): NOT RUN — blocked, not passed; superseded by the third pass below.** The `03:06:19Z` build completed and its internal prose-staleness gate reported 0/44 behind, but GitHub auth failed at ~`03:07Z` before either read-only verifier could be re-run. `tools/last_live_verify.json` is the **`01:17:26Z`** result restored from git: a run attempted after the expiry returned 51 checks that were all `committed=200 live=401`, which is an artifact of dead credentials and **not** a finding about the data, so it was discarded rather than committed. `tools/last_description_audit.json` is a labelled **PARTIAL** artifact — its `accepted` block is regenerated deterministically from `overlay.json` (a local filter needing no network) while its `unresolved` list is the `02:42Z` run, preserved verbatim and not recomputed. `tools/audit_kind.py` likewise returned HTTP 401 for all 44. See `IRR-55`.

</details>

---

## Directory Overview

For each of the **72 GitHub Pages sites** in the directory:

- **Live Site Link** & **Repository Link**
- **Sourced Brief Description** — extracted line by line from the repository's own `README.md` and published file structure
- **Created Date** — GitHub `created_at`, with the first-commit timestamp and SHA shown alongside
- **Last Updated Date** — newest committer timestamp on the default branch, with the latest commit SHA, plus `pushed_at`
- **GitHub Pages Status & Build Source** — **72 / 72 reporting `built`** at the shipping snapshot, each recorded as-is rather than assumed healthy, and any non-`built` state published rather than hidden; 71 publishing from `main /` and 1 (`GOLD`) from `main /docs`
- **Total Commits on the Default Branch**, repository size, and app-vs-stub classification
- **Official Source Links for Manual Review** — live URL, repository, Pages API JSON, commits API, and Pages settings
- **Verification provenance per entry** — `lastVerified` (when the prose was read), `verifiedBasis` (what was read, and the exact command or endpoint that reproduces it) and `verifiedAtSha` (the commit it was read against, compared against the live head on every build)
- **Per-entry audit flags** and a **112-entry flagged irregularities register** (`IRR-01` … `IRR-112`), ordered by severity

---

## User Interface Features

- **Instant Search & Multi-Filter** — search by title, repository, description, category or flags, combined with category and type filter chips showing live counts.
- **Shareable Directory Views** — search, category, type, prose state, sort and layout are encoded in the URL. Copy a view link, reload it, or use Back/Forward to revisit filter changes. Invalid filter values fall back to defaults; unrelated query parameters and anchors are preserved. Search edits replace the current history entry rather than adding one per keystroke.
- **Prose Review Filter** — narrow the directory to behind-recorded-head, missing-stamp, latest-stamp or carried entries, using the same state as each card’s badge. “Latest” means the exact newest `lastVerified` timestamp in the snapshot, not all work in a multi-hour audit. **Reset filters** clears search/category/type/prose while retaining sort and layout.
- **Snapshot-Aware Status** — both layouts display the recorded Pages status (including building, errors or unknown) rather than assuming every deployment is built. Matching prose/head SHAs describe the recorded snapshot, not a live check or proof of description accuracy.
- **Dual View Modes** — responsive **card grid** and a dense **table view**, both retuned by the density preference below.
- **Row Density** — the table is **compact by default**, because its job is to let a reader compare many entries on one screen: rows drop from ~60px to ~29px, the name column is fixed-width with the curated title clipped to one line (the longest in the snapshot is 78 characters, and the full title stays in the anchor's `title` attribute, the card view and the inspector) and the repository slug sits beside it. The **Density** button restores the padded "Roomy" layout and is remembered per browser in `localStorage`. It is deliberately **not** a URL parameter and **not** a filter: shared links, Back/Forward and **Reset filters** all behave exactly as before, and neither export changes.
- **Narrow-Screen Table** — below 900px the table re-stacks into one labelled line per field, so a phone reads a card per site instead of scrolling a ~1,000px table sideways. This is **CSS only**: the DOM keeps the same nine cells in the same order on every screen size, the column headings stay in the accessibility tree, and the `colspan="9"` empty state, the `.table-repo` slug and the recorded Pages status in the fourth cell are all unchanged. Touch targets get their own size there, independent of the density preference.
- **Sort** by last updated, date created, name or commit count.
- **Site Inspector Modal** — full telemetry, timestamps, commit SHAs, size, branch, Pages source and the raw verified JSON record for any entry.
- **Unreachable Panel** — retired entries kept visible with their last verified state and the exact commands that reproduce the 404.
- **Severity-Ordered Irregularities** — critical → warn → info, each with a reproduction endpoint.
- **Client-Side Export** — download the verified master list as JSON or CSV in one click (CSV marks retired rows instead of dropping them).
- **Accessibility** — skip link, ARIA live regions, focus-preserving filter chips, visible keyboard focus and a native inspector dialog with inert background, Tab/Shift+Tab containment, Escape to close and focus return to the opener. The density button carries its state in `aria-pressed` and names both options in its tooltip. Narrow-screen cards wrap long content, stacked table cells break long values instead of overflowing, and the controls stop sticking on mobile so they do not cover the directory.
- **No build step, no runtime dependencies, no framework** — plain `index.html` + `styles.css` + `app.js` plus one data file.

---

## File Architecture

| File | Purpose |
|---|---|
| [`index.html`](index.html) | Semantic, accessible directory markup (grid, table, panels, inspector modal) |
| [`styles.css`](styles.css) | Responsive design system — CSS custom properties, cards, tables, badges |
| [`app.js`](app.js) | Zero-dependency application logic (search, filter, sort, export, inspector, toast) |
| [`data/sites.js`](data/sites.js) | **Generated** verified dataset — 72 sites, 4 unreachable entries, 112 irregularities, 2 audited accounts, methodology |
| [`tools/overlay.json`](tools/overlay.json) | Hand-authored narrative: titles, categories, descriptions, flags, the irregularity register, the permanent exclusion list |
| [`tools/build_data.py`](tools/build_data.py) | **Generator** — reads the official GitHub API and writes `data/sites.js` |
| [`tools/build_verification.py`](tools/build_verification.py) | **Generator** — renders `VERIFICATION.md` from `data/sites.js` |
| [`AGENTS.md`](AGENTS.md) | Standing maintenance instructions for future sessions, including the permanent repository exclusion |
| [`VERIFICATION.md`](VERIFICATION.md) | **Generated** line-by-line audit ledger with official endpoints, commit SHAs and reproduction commands |
| [`tools/verify_live.py`](tools/verify_live.py) | **Read-only verifier** — re-reads every API-derived field of every entry and reports ok / mismatch / drift. Never writes the dataset |
| [`tools/audit_descriptions.py`](tools/audit_descriptions.py) | **Read-only verifier** — checks every numeric claim in a description against the repository's own README |
| [`tools/audit_kind.py`](tools/audit_kind.py) | **Read-only verifier** — re-derives each entry's app-vs-stub `kind` from the API and reports any disagreement with the committed value |

### Testing the interface (no API access)

The site still runs directly from its static files. Node.js 22 and Python 3 are
needed only for development tests; Playwright is a pinned **dev dependency**, not
part of the deployed application.

```bash
npm ci
npm run check
npx playwright install --with-deps chromium firefox webkit
npm test                          # Chromium, Firefox, WebKit and mobile Chromium
npm run test:chromium             # desktop Chromium only
```

Tests read the committed snapshot without rewriting it. Synthetic browser-only
fixtures exercise non-built statuses, all four prose states, URL validation and
escaping, combined filters, history, reset, copying, keyboard focus and the
inspector. Other tests check the actual snapshot's listing/accounting/exclusion
invariants, complete JSON/CSV exports (including frozen unreachable rows), and
narrow-screen layout. `.github/workflows/test.yml` runs these on PRs and pushes
to `main`. Failure traces are uploaded for diagnosis; caches/results are ignored.

For an already running static server, set `TEST_BASE_URL`; for an installed
Chromium executable, set `CHROMIUM_PATH` and run the Chromium projects. These
are test-runner settings only, never browser-facing service URLs.

**Scope of the 2026-09-22 interface update:** no API refresh or repository prose
re-audit was performed. The audit snapshot, overlay and ledger below remain at
their recorded timestamps. UI regression tests do not replace the independent
live/prose/kind verifiers required for a data refresh.

### Refreshing the directory

```bash
export GITHUB_TOKEN=...                  # optional, raises the rate limit; 5,250 requests/h were
                                         # available unauthenticated in this audit sandbox
python3 tools/build_data.py              # reads api.github.com, rewrites data/sites.js
python3 tools/build_verification.py      # rewrites VERIFICATION.md from the new data

# then verify what you just generated, independently of the generator:
python3 tools/verify_live.py             # 686 field checks — expect 0 hard mismatches
python3 tools/audit_descriptions.py      # every numeric claim vs the repo's own README
python3 tools/audit_kind.py              # re-derives app-vs-stub from the API — expect 0 disagreements
```

**Read the generator's last line before you trust the build.** It prints a prose-staleness gate:

```
prose: 1 re-read this pass, 51 carried, 52 stamped with a SHA, 0 provably behind their repo
```

Any `PROSE-STALE <repo> description read at <sha>, repository is now at <sha>` line means that
entry's description was read at a commit that is no longer the default branch's head, so it is
*provably* out of date and must be re-read before publishing. Repositories in this account commit
continuously — **six repositories moved during the 2026-09-21 pass, forcing six successive builds
before the gate reached zero** — so this line, not the timestamp, is the pass's completion gate
(`IRR-50`, `IRR-61`, `IRR-72`). Treat re-reading and rebuilding as one loop that repeats until it
prints `0 provably behind their repo`; a `PROSE-STALE` range whose README did not change still
requires triage, never a silent re-stamp (`IRR-70`).

If `api.github.com` is unreachable or the credentials have expired, `--overlay-only` re-renders the
narrative fields (descriptions, categories, flags, the irregularity register) into the **existing**
snapshot without a single network call:

```bash
python3 tools/build_data.py --overlay-only   # narrative only; API fields carried forward verbatim
```

It leaves `generated` and every API-derived field byte-identical, writes a separate
`overlayRendered` timestamp, and prints a warning that it cannot detect commits made since the
snapshot. It refuses to run if a listed repository has no curated overlay entry, so it can never
default a description into existence. Verified non-fabricating: re-rendering the `03:06:19Z`
snapshot produced **0 differences across 44 sites × 16 API-derived fields**.

Every timestamp, SHA, commit count, Pages status, build source and size in the output comes from an API read at that moment — nothing is carried over from memory. Repositories that vanish are moved into the `unreachable` list instead of disappearing.

`verify_live.py` separates two kinds of difference. A **hard mismatch** means the committed value and the live value disagree with no explanation, and is a defect: re-run the generator. **Drift** means the field is one GitHub recomputes asynchronously (`size`, `pushed_at`, `updated_at`) or the repository was pushed to *after* the snapshot was taken — expected, and folded in by the next refresh. The 2026-09-21 pass finished at **0 hard mismatches across 686 checks**, with 3 volatile-field drifts (all `pushedAt`, pushed after the snapshot read).

A third failure mode is worth naming because it looks like a data defect and is not: **dead credentials**. When the token expires, `verify_live.py` reports every entry as `MISMATCH ... committed=200 live=401`. That is an authentication failure, not 52 broken records. Check `gh auth status` before reading any verifier output, and discard a run whose mismatches are uniformly 401 — the second pass did exactly that and restored the last valid artifact from git rather than committing a false result.

---

## Verification & Integrity Policy

1. **Zero Hallucinations.** Every field is read from `api.github.com` or from the repository's own files. Where a claim could not be re-verified it was **deleted or corrected, never softened** — for example `TradingViewTheLeap`'s "203-check verifier" and `GEMSDOE`'s "19/19 rules" figures no longer appear in those repositories and were removed rather than restated, and this audit removed `DrugAnalysis`'s superseded "1,038 core rows".
2. **Autonomous Execution.** No manual data entry, no owner prompts during the audit. The only hand-authored content is narrative prose in `tools/overlay.json`.
3. **Independent Re-Verification, Not Restatement.** `tools/verify_live.py` re-reads every API-derived field of every entry straight from GitHub and prints each one as ok, mismatch or drift. It is deliberately read-only — it reports, it never repairs. `tools/audit_descriptions.py` checks each description's numeric claims against the repository's own README. Run both after any refresh:
   ```bash
   python3 tools/verify_live.py           # 686 field checks across 52 entries + both accounts
   python3 tools/audit_descriptions.py    # every numeric claim vs the repo's own README
   ```
4. **Transparent Irregularity Reporting.** Every anomaly is catalogued with the endpoint needed to reproduce it, ordered by severity (`critical` → `warn` → `info`). The 2026-09-22 audit added fifteen (`IRR-73` … `IRR-87`), three of them `critical`; the 2026-09-21 audit added nine (`IRR-64` … `IRR-72`), two of them `critical`.
5. **Nothing Is Silently Deleted.** Excluded and unreachable repositories are named, explained and preserved with their last verified values.
6. **Corrections Are Recorded, Not Hidden.** When a published description turns out to have been wrong, the entry is fixed *and* the mistake is registered with what it said, what it should have said, and how it was caught — see `IRR-25` through `IRR-29`.

---

## Repository Exclusions — Standing Instructions for Future Sessions

One repository on the account is **permanently excluded** from this site. Do not list it, link it, count it, or export it — in any future session, regeneration, or refresh of this directory.

| Excluded repository | Status | Instruction |
|---|---|---|
| `ProjX` | Still live on GitHub; intentionally unpublished **here** since 2026-09-12 by owner request | **Never add it back** to `data/sites.js`, the `VERIFICATION.md` ledger table, README counts, or the JSON/CSV exports. No live link, API endpoint or Pages URL for it is printed anywhere in this repository. Full rationale in [VERIFICATION.md § 2a](VERIFICATION.md#2a-repository-exclusions-deliberately-omitted). |

Because of this exclusion the directory shows **72** sites while the GitHub API reports **73** public Pages repositories. That mismatch is correct and expected: keep the account-level totals (`publicRepos: 73`, `pagesSites: 73`) at their verified API values and filter excluded names *after* the API read, instead of lowering those totals. `tools/build_data.py` applies the `excluded` list from `tools/overlay.json` automatically, records every withheld repository with its reason in `counts.unlisted`, and **asserts at build time** that `listed + withheld == pagesSites` so a silent gap is impossible.

---

## Unreachable Entries — Needs Owner Review

| Repository | Last verified | What happened | Owner action |
|---|---|---|---|
| `JobSearchSF` | `f68c452`, 2026-09-16T19:37:41Z, 68 commits | Re-confirmed 2026-09-24 (ninth consecutive audit): `GET /repos/buffedlizard55-lab/JobSearchSF` returns **HTTP 404** and the repository is absent from the account's 73-repository public list, so it was deleted or made private. Its Pages site is therefore no longer served. | **Restore it** (undelete / make public) so it can be re-listed, **or confirm it should stay retired** and the frozen entry can be dropped. Flagged as `IRR-01` (critical). |
| `MALTA` | `f0fb352`, 2026-09-23T22:54:46Z, 40 commits | **Deleted mid-pass on 2026-09-24.** It was new to this pass, was cloned at head and fully verified — all four of its own checks executed clean — and then `GET /repos/buffedlizard55-lab/MALTA` returned **HTTP 404** with no surviving repository carrying its `created_at`. Its short-lived replacement `MALTA2` has itself since been deleted upstream (both are frozen as separate entries). Measured in this pass's own builds: 68 sites / 3,793 commits at `00:17:06Z`, then 67 sites / 3,753 at `00:23:27Z`. | **Confirm whether deleting a complete 40-commit dossier was intentional**, and whether its content survives anywhere. Flagged as `IRR-109` (critical). |
| `MALTA-LAWS` | `18f3323`, 2026-09-23T23:12:07Z, 3 commits | Listed 2026-09-24 and fully verified by executing its own checks (`unittest discover` 15 OK; `tests/test_site.py` OK over 14 pages). Now `GET /repos/buffedlizard55-lab/MALTA-LAWS` returns **HTTP 404** and the name is absent from the account's 73-repository public list. | **Restore it, or confirm it is retired.** Flagged as `IRR-110` (critical). |
| `MALTA2` | `e806c87`, 2026-09-24T00:22:27Z, 1 commit | An 8-byte `# MALTA2` placeholder created minutes after `MALTA` vanished; it never held more than one commit and has now itself been deleted upstream (HTTP 404). Frozen per the standing policy. | **Confirm the Malta-family deletions were intentional.** Flagged as `IRR-110` (critical). |

The entry stays visible in the site's *Unreachable — Needs Owner Review* panel and in `VERIFICATION.md` § 2b with every value it last verified, plus the three commands that reproduce the 404.

---

## Known Limitations

These are the real obstacles, stated plainly. Several are the reason a claim can be "verified" today and wrong tomorrow.

1. **The prose is the fragile part, not the numbers — and it failed again this pass.** Every timestamp, SHA, commit count and Pages status is read from `api.github.com`, and this pass re-ran the full live check cleanly (946/946 field checks, 0 hard mismatches). Descriptions are written prose, and the false-description class struck a fifth time: `NOBEL-PRIZE` was published as an empty one-file placeholder and is now a 12-commit archive site (`IRR-112`), the same class as `SelfLearn`/`MasterSelfLearn` (`IRR-84`), `NFLComp`'s sign-flipped PnL (`IRR-65`) and `NFLPARLAYCOMP`'s mid-read flip (`IRR-82`). `verifiedAtSha` reliably tells us *which* entries to re-read; it cannot tell us what they now say.
2. **A matching SHA proves the prose was read against those bytes, never that the prose is true — and a README-unchanged diff proves even less.** This pass, the README changed in only 13 of the 20 stale ranges, yet **four of the five sharpest findings came from ranges that touched no README at all** (`IRR-70`). A SHA-only re-stamp would have missed `IRR-68` entirely.
3. **Five upstream repositories contradict themselves, so "read the README" is not sufficient either.** `Elections` states 209 sources in one place and 189 in another while its file holds **229**, and claims 63 irregularities against a file holding **58** (`IRR-67`); `NBAInjuryReport`'s prose is two days behind its own regenerated data (`IRR-68`); `OLBG-Competition` says 262 tests where the test functions count 258. This pass added two: `NFLPARLAYCOMP`'s README describes its site bundles as ~6.8 MB / ~1,050 files where the committed tree measures **7.62 MB / 1,052 files**, and `SelfLearn`'s `SUMMARY.md` reports 91 documents and 5 experiments while its own `reports/site_data.json`, generated ten minutes earlier, holds **89 and 3** (`IRR-77`, `IRR-84`). Where prose and file disagree, this directory **publishes the counted file value and flags the prose** — but that policy has to be applied by hand, every time.
4. **Live page bodies are still not fetched over HTTP.** Pages liveness rests on two API facts — status `built` and a real `index.html` at the published path — not an HTTP 200 on the rendered page. Re-tested 2026-09-22: this sandbox still cannot reach `*.github.io` **or `raw.githubusercontent.com`** (`curl` returns `000`, an `SSL_ERROR_SYSCALL` on connect, while `github.com` HTML returns 200), so the block is network egress, not configuration. `IRR-83` is exactly the case this gap hides: `Elections` reports `errored`, and from here there is no way to see what its URL actually serves. A site can be `built` and still render a blank page. Every entry links its live URL for one-click manual review.
5. **Repositories move faster than the audit can snapshot — the account gained ten repositories in 23 hours and four changed state *during this pass*.** `NFLPARLAYCOMP` was rewritten wholesale 40 minutes after being read (`IRR-82`); `SelfLearn` and `MasterSelfLearn` grew from one-file placeholders into engines with 156 and 350 passing tests (`IRR-84`); `PRICINGEXPERT` was created at `23:01:18Z` and discovered by a build already in progress (`IRR-80`); and `MasterSelfLearn` commits its own output on a `*/30` cron, so it moved from `fe488ed` to `eda549e` *while this audit was reading it* and will report `PROSE-STALE` forever unless triaged by cycle number. The 2026-09-21 pass needed **eight successive builds** before its gate reached zero; this pass's gate never reached zero at all, because credentials died with 21 entries still queued (`IRR-85`).
6. **The youngest entries remain where every error comes from.** Every critical finding of this pass is a repository under 48 hours old or under two days of active development: `NFLPARLAYCOMP`, `SelfLearn`, `MasterSelfLearn`, `PRICINGEXPERT`. Five audits running, every stale-description defect has traced to a repository under two days old. Re-read the youngest entries first — and note that `MasterSelfLearn` is now the extreme case, being rewritten by its own cron every 30 minutes.
7. **Some upstream test suites cannot be executed here, so a few counts are of test *functions* rather than *assertions*.** `NHLComp`'s suite runs only with `PYTHONPATH=src` (231 tests, verified); `MLBComp`'s Python suite needs `pandas`, which is absent, so only its Node contract test was executed; `OLBG-Competition` has no `pytest` available, so its 258 is a `def test_` count that may differ from collected parametrised cases. This pass *did* execute four more suites (`SelfLearn` 156, `MasterSelfLearn` 350, `NFLPARLAYCOMP` 103, `FLABSENGY` 79) and hit a new trap doing it: **`NFLPARLAYCOMP`'s suite rewrites `docs/site_data/` and `data/competition/verification_report.json` in the working tree**, so its counts must be taken from a clean checkout (`git status --porcelain` empty) or they measure regenerated files (`IRR-82`). Each of these is disclosed in the entry's own `verifiedBasis` rather than presented as a measured pass.
8. **Repository size is GitHub's asynchronously-recomputed field**, so size moves that do not line up with commit deltas are normal (`IRR-04`–`IRR-06`). `GEMSDOE` alone is ~400 MB because competition rasters are committed as git parts.
9. **`kanlerxz87-cyber` contributes nothing.** Verified to exist (`type: User`, created `2026-08-03T20:56:16Z`) with **0** public repositories (re-verified `2026-09-24T23:54Z`). If it ever publishes, the generator picks it up automatically.
10. **One repository is withheld, permanently, by owner request.** `ProjX` is the only withheld repository, so the directory will always show one fewer site than the account totals — deliberate, and never to be "fixed"; see [Repository Exclusions](#repository-exclusions--standing-instructions-for-future-sessions). The earlier procedural hold on `PRICINGEXPERT` was resolved when a full `build_data.py` run listed it (`IRR-86`): narrative can be landed offline, but listing cannot, and it is now a listed 72-file research desk.
11. **The four unreachable repositories cannot be resolved from here** — `JobSearchSF` has returned HTTP 404 for a ninth consecutive audit (`IRR-01`), and the Malta family (`MALTA`, `MALTA-LAWS`, `MALTA2`) was deleted upstream around this pass (`IRR-109`, `IRR-110`). Owner decision only.
12. **Credentials can die mid-audit, and when they do the verifiers lie — this pass they died with the queue uncleared.** A uniform HTTP 401 across every entry means dead credentials, not 61 broken records (`IRR-55`). Check `gh auth status` before acting on any verifier output, and discard such a run rather than committing it. `IRR-85` adds two details worth knowing: the sandbox egress path injects the token into **every** `api.github.com` request, so a request with no `Authorization` header also returns 401 and the unauthenticated 60-request tier is not a fallback; and `git clone` dies with it ("could not read Username"), so repository contents become unreadable too, not just API metadata. The recovery path is `--overlay-only`, which lands narrative work with no network at all.

---

## What Still Needs To Be Done

Ordered by what actually threatens the project's core promise. **Items 1, 2 and 3 are the work for the next session.** Item 1 is now done for this pass (the toolchain ran clean against the shipping snapshot) and has been replaced by the two things that pass exposed.

| # | Task | Why it matters | Effort |
|---|---|---|---|
| 1 | **Add the `verifiedAtSha` shape guard to `build_data.py`** — warn when an entry sets the field to anything that is not `^[0-9a-f]{7,40}$`. | `IRR-108` was invisible for two passes because a non-SHA stamp looks populated: `KalshiPaperSim` held `AUTO:COUNTS` and `MasterSite` held `main`, so the staleness gate reported both stale on every build forever and the badge in the UI read "read at AUTO:COUNTS". The field is now correct by hand; the guard stops the next leak, whose cost was two permanently false work items. | **Low effort — start here** |
| 2 | **Clear the 26-entry `PROSE-STALE` queue by re-reading each description against its repository — and open the *data files*, not just the README.** The queue is printed by every build and rendered stale-first in `VERIFICATION.md` §4a. | Still the only error class that has materially misled a reader, now across seven consecutive audits; the previous passes produced a headline PnL that changed **sign** mid-audit (`IRR-82`) and a placeholder that became an archive site (`IRR-112`). `verifiedAtSha` turns an unbounded job into a work queue but cannot do the reading, and `IRR-70` shows a README-unchanged diff is not a safe shortcut. Several entries carry durable triage rules in their `verifiedBasis` (e.g. `SFWeather`, `MasterSelfLearn`) — use them instead of re-deriving. | **High — the real work** |
| 2a | **Re-read the youngest entries first.** This pass's two sharpest findings — `NFLPARLAYCOMP`'s sign flip and `NOBEL-PRIZE`'s stub→app reversal (`IRR-112`), and `TAXKALSHI`'s stub→app reversal *mid-read* (`IRR-111`) — are all repositories under 48 hours old. Six audits running, every stale-description defect has traced to a repository under two days old. | The youngest repositories are where every critical error comes from, and they churn fastest. | Part of item 2 |
| 3 | **Run the interface test suite in an environment that has a browser.** The DOM contract was verified offline (jsdom), but layout — `scrollWidth ≤ innerWidth` at 375×812, touch-target heights — is only observable in a real browser. | The published site's readability on a phone is a claim this repository cannot currently evidence from the sandbox. `.github/workflows/test.yml` runs all four projects, including `mobile-chromium`. | Low — CI does it on push |
| 4 | **Resolve the four deleted repositories upstream: `MALTA` (`IRR-109`), `MALTA-LAWS` / `MALTA2` (`IRR-110`) and `JobSearchSF` (`IRR-01`).** | Three of the four Malta-family repositories created on 2026-09-23/24 have now been deleted upstream within a day; `JobSearchSF` has been 404 for nine audits. A directory cannot distinguish "deliberately replaced" from "accidentally deleted", and only the owner can. | Owner only |
| 5 | **Report the self-contradiction defects upstream** (`Elections` 209/189/229 and 63/58, `NBAInjuryReport` 65/21 vs 94/70, `OLBG-Competition` 262/258, and the Malta-family outage contradiction `IRR-105`) so the repositories fix their own prose instead of this directory carrying a permanent footnote. | A directory that grades other projects' verification should not need a standing workaround for their arithmetic. Each is a one-line fix at the source. | Owner / upstream |
| 6 | **Resolve `JobSearchSF` (`IRR-01`).** Restore the repository, or confirm it is retired so the frozen entry can be dropped. | The oldest open `critical` irregularity (2026-09-17), now in its ninth audit. No machine can resolve it. | Owner only |
| 7 | **Fetch live pages over HTTP from an environment with egress to `*.github.io`.** A GitHub Actions job in this repository would have that access even though the audit sandbox does not. | It is the difference between "GitHub says it built" and "it works". The blocker is the sandbox, not the design. | **Medium — highest-value new capability** |
| 8 | **Move `GEMSDOE`'s ~400 MB of rasters out of git** (Git LFS or a release asset). | Real operational cost; growth pattern documented in `IRR-04`. | Medium |
| 9 | **Decide whether overlapping entries should stay listed.** `HotelSeoulRoughdraft1` duplicates `Itinerary-Korea` (`IRR-14`); `MLB-PBP`/`MLB-Live-PBP` overlap (and `MLBSCORINGCHANGE` is now an explicit working copy of `MLB-Live-PBP`); `ScheduleFreeTime` and `VacationSchedule` overlap; `NFLPARLAYCOMP` and `ParlaySports` both cover NFL parlay paper-trading; `SelfLearn`/`MasterSelfLearn` are two engines over the same claim graph; and `THUNDERPICK-WC-2026`/`THUNDERPICKCOMP` and `NOBEL-PRIZE`/`SIM-COMP-NOBEL-PRIZE` are explicit design-copy / source pairs. | A directory is more useful when it does not send readers to a superseded draft, and 72 repositories is past the point where a reader can tell the relationships out themselves. Curation, not data. | Owner only |
| 10 | **Automate the audit on a schedule** (GitHub Actions running `build_data.py` + all three verifiers, opening a PR when the gate is non-zero). | Repositories appear and change state *during* every audit; a scheduled job would keep the window between snapshot and reality to hours instead of days — and, unlike this sandbox, it would hold working credentials and reach the live sites (items 1, 3 and 7). | Medium |
| 11 | **Verify the two `TAXKALSHI` and `NOBEL-PRIZE` reversals stay true after their first live Pages builds.** Both were read at head during rapid growth and are the youngest entries in the directory. | Their descriptions were written from heads read minutes apart; a `PROSE-STALE` re-read is near-certain next pass. | Low |
| 12 | **Settle `IRR-105` (the Malta/hotspawn outage contradiction) once egress is available.** | Three repositories describe the same host's availability that day in three different ways. From this sandbox, `curl` to anything except `api.github.com` returns HTTP `000`. | **Medium — blocked on egress, not effort** |

**Closed this pass:**

- ~~**`NOBEL-PRIZE` was published as an empty placeholder while the repository had become a 12-commit archive site.**~~ Rewritten in full at head `dfd8253`; the placeholder description was withdrawn and `kind` re-derived `app` (`IRR-112`).
- ~~**`MALTA-LAWS` and `MALTA2` had been deleted upstream since the last snapshot.**~~ Both are frozen in the Unreachable panel with their last verified values rather than dropped (`IRR-110`).
- ~~**`TAXKALSHI` would have been published as an empty stub while it grew.**~~ Withheld from publication until a full build read it at 5 commits with a real `index.html` (`IRR-111`).
- ~~**`PRICINGEXPERT` was withheld pending a full `build_data.py` run.**~~ It is now a listed 72-file research desk; the earlier "withheld procedurally" limitation no longer applies (`IRR-86`).

**Closed in the 2026-09-21 pass:** the `IRR-43` class of finding ("built site lives in `docs/` but Pages publishes `main /`, so the live URL serves a Jekyll README render") — **resolved for every affected repository.** `MLBComp`, `NHLComp` and `VacationSchedule` all now commit a root `index.html`, `audit_kind.py` reported **0 disagreements across 52 sites**, and the standing owner-action items asking for a Settings → Pages change are withdrawn. (`NFLPARLAYCOMP` re-opened a variant of it this pass: its root `index.html` is a forwarder to `docs/`, because switching the Pages source to Actions returns 403 — see `IRR-76`.)
