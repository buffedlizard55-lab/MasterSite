# MasterSite

MasterSite is a source-linked directory of public GitHub Pages repositories for [`buffedlizard55-lab`](https://github.com/buffedlizard55-lab), with a public-account census for [`kanlerxz87-cyber`](https://github.com/kanlerxz87-cyber). Each listed site has a repository and Pages link, a short description curated from repository-owned files, its creation date, its latest default-branch commit timestamp, and official links for review. Per-entry source SHAs, snapshot telemetry, and flagged findings are in [`VERIFICATION.md`](VERIFICATION.md).

**Live directory:** <https://buffedlizard55-lab.github.io/MasterSite/>

> **How to read the dates and status:** GitHub's public repository/Pages APIs do not expose site visits or last use. “Last commit” is the newest committer timestamp on the default branch, not evidence of site use. The “HTML entry point” label means `index.html` exists at the configured Pages source path; it does not establish that the page is interactive, works in a browser, or is reachable over HTTP. Pages status `built` is GitHub API metadata, not an uptime check.
>
> **Scope:** `ProjX` is deliberately excluded under a standing owner instruction. Four previously listed repositories returned HTTP 404 in the latest live API audit; they remain visible in the Unreachable panel and ledger with their last verified values rather than being silently dropped. Private repositories are outside the public API census.

## Current audit status — 2026-09-29 (API snapshot `2026-09-29T23:15:11Z` UTC)

| Metric | Snapshot result |
|---|---|
| Sites listed | **100** |
| HTML entry points / README-documentation stubs | **87 / 13**; based only on the configured `index.html` path |
| Pages API status | **100 / 100 report `built`** at the snapshot; this is not an uptime or behavior test |
| Default-branch commits | **5,903** across the listed repositories |
| `buffedlizard55-lab` public repositories / Pages-enabled repositories | **101 / 101**; 100 are listed and `ProjX` is excluded by owner instruction |
| `kanlerxz87-cyber` public repositories / Pages-enabled repositories | **0 / 0** |
| Description provenance | **100 / 100** entries have a source commit SHA; **35** stamps are behind the snapshot head and remain a visible re-read queue, not proof the prose is false |
| Latest prose stamp | **1 re-read / 99 carried** at `2026-09-29T23:12:23Z` |
| `verify_live.py` | **1,316 checks; 1,316 OK; 0 mismatches; 0 drift** |
| `audit_kind.py` | **100 checked; 0 disagreements; 0 unresolved** |
| `audit_descriptions.py` | **100 checked; 0 needing review; 42 documented numeric-token exceptions**. This is a lint, not semantic proof |
| Local code checks | `npm run check`, Python syntax compilation, and Playwright test discovery (84 tests) pass. Browser tests remain unexecuted because browser binaries are unavailable; a prior Playwright CDN download failed. The PR workflow installs browsers and is expected to run the suite |
| Irregularities / description notes | **126 / 24** (`IRR-01` … `IRR-126`) |
| Categories | **12** — Sports Data & Scoreboards (34), Science & ML Research (24), Markets & Trading Research (13), Travel & Korea Trip (11), SF Local Guides (8), Gaming & Guides (3), Directory & Meta (2), plus five single-entry categories |
| Pages source paths | **99** from `main /`; **1** (`GOLD`) from `main /docs` |
| Previously listed but unreachable | **4** (`JobSearchSF`, `MALTA`, `MALTA-LAWS`, `MALTA2`); all returned HTTP 404 in the latest live API verification |

### 2026-09-29 audit follow-up

- The API census found and curated **15 previously unlisted Pages repositories**: `12GEMSDOE`, `13GEMSDOE`, `14GEMSDOE`, `15GEMSDOE`, `16GEMSDOE`, `17GEMSDOE`, `18GEMSDOE`, `19GEMSDOE`, `20GEMSDOE`, `based-loaded-MLB-alert-system`, `GRANTWRITING`, `LEARNGEMSDOE`, `LiveScoringErrors`, `POSTSEASONMLBALERTS`, and `RADIOSF`. Nine have a configured-path `index.html`; six (`13GEMSDOE` and `16GEMSDOE`–`20GEMSDOE`) lack one and are classified as README/documentation stubs. Their source basis and current SHAs are recorded per entry.
- A later kind audit found **five older GEMS entries had changed since the prior snapshot**: `11GEMSDOE`, `7GEMSDOE`, `8GEMSDOE`, `GEMSDOE9`, and `GEMSDOE10` now have a configured-path `index.html`. Their current README and HTML entry points were re-read, summaries revised, and kinds reclassified (`IRR-124`). Root redirect pages are described as entry points, not as independently tested apps.
- `based-loaded-MLB-alert-system` advanced during the first refresh; its README and API evidence were re-read at the newer head `d06dc48` before this snapshot. The description is limited to the documented alert rules and controls; no complete historical replay is claimed (`IRR-125`).
- **`16GEMSDOE` changed materially after the first census.** At head `8354839`, its README now describes the H16-1 DOE GEMS submission and links to a documentation hub and download variants. The Pages API still reports `built` from `main /`, but the configured root has no `index.html`; the README's nested `docs/index.html` is not the root landing page. The summary was re-read and narrowed, and the source-path distinction is flagged as `IRR-126`; reported model scores are not independently validated here.
- The final refresh incorporated later heads for `NBASCOREBOARD`, `NFLInjuryReport`, and `NHL-SCOREBOARD`. The independent live check then matched the refreshed snapshot, including a final default-branch-head recheck for repositories that moved during verification.
- **35 descriptions still need a current-head source review.** They are flagged by `verifiedAtSha`/`proseStale` in the UI and stale-first in the ledger. A changed commit is a prompt to re-read, not automatic proof that the description is wrong; no stale entry is silently re-stamped.

## Historical audit journal (through 2026-09-26)

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

For each listed site, the directory shows:

- **Site and repository links**, plus a short summary curated from the repository's own README or source files. The exact source basis and commit are recorded in `tools/overlay.json` and `VERIFICATION.md`.
- **Created date (UTC)** from GitHub repository metadata, with first-commit timestamp and SHA in the inspector/ledger.
- **Last commit (UTC)** from the newest committer timestamp on the default branch, plus its commit SHA. GitHub's public APIs do not expose the last time a site was visited or used.
- **Pages status and deployment source** as returned by GitHub at the snapshot. `built` is not a live uptime result.
- **Site type** derived from whether `index.html` exists at the configured Pages source path. It does not mean the page is interactive or functional.
- **Default-branch commit count, repository size, description-verification state, and per-entry flags.** Thirty-five description stamps are behind the current repository head in this snapshot; those entries are explicitly marked for review.
- **Official manual-review links** — live URL, repository, Pages API, commits API, Pages settings, and the recorded README/source reference as applicable.
- **Unreachable history and irregularities** — four currently missing repositories remain visible with their last recorded state; the 124-item irregularities register includes reproduction details and source links.

---

## User Interface Features

- **Search and filters** by repository, description, category, flags, HTML-entry-point/stub type, and prose-verification state.
- **Shareable views** — search, category, type, prose state, sort, and layout are encoded in the URL; Back/Forward, reset, and export preserve the documented state contract.
- **Snapshot-aware indicators** — recorded Pages status, prose SHA status, and audit flags are shown as snapshot data, not live health checks.
- **Card and table views** with a per-browser compact/roomy density preference.
- **Responsive table layout** re-stacks fields below the narrow-screen breakpoint. Browser layout and keyboard behavior are covered by Playwright tests, which could not run in this sandbox because browser downloads were blocked.
- **Sort** by last default-branch commit, creation date, name, or commit count.
- **Inspector modal** with timestamps, SHAs, size, branch, Pages source, description basis, official links, and raw record.
- **Unreachable panel** retaining missing entries and last verified values; **irregularities register** ordered by critical, warning, and informational severity.
- **JSON and CSV exports**, including unreachable rows.
- **Static deployment** — plain HTML, CSS, JavaScript, and generated data; no runtime framework or dependency.

---

## File Architecture

| File | Purpose |
|---|---|
| [`index.html`](index.html) | Accessible directory markup, filters, cards, table, panels, and inspector |
| [`styles.css`](styles.css) | Responsive visual styles |
| [`app.js`](app.js) | Search, filtering, sorting, exports, inspector, and status copy |
| [`data/sites.js`](data/sites.js) | **Generated** 100-site snapshot, four unreachable records, 124 irregularities, account totals, and methodology |
| [`tools/overlay.json`](tools/overlay.json) | Curated titles, categories, descriptions, flags, source stamps, exclusions, and irregularity register |
| [`tools/build_data.py`](tools/build_data.py) | **Generator** — reads GitHub's official API and writes `data/sites.js` |
| [`tools/build_verification.py`](tools/build_verification.py) | **Generator** — renders `VERIFICATION.md` from the snapshot and current audit reports |
| [`AGENTS.md`](AGENTS.md) | Current maintenance rules, exclusions, source-verification workflow, and known constraints |
| [`VERIFICATION.md`](VERIFICATION.md) | **Generated** API snapshot, per-entry source ledger, exclusion/unreachable records, irregularities, and reproduction commands |
| [`tools/verify_live.py`](tools/verify_live.py) | **Read-only verifier** — compares snapshot API fields against GitHub; never writes the dataset |
| [`tools/audit_descriptions.py`](tools/audit_descriptions.py) | **Read-only numeric-token lint** — checks whether description numbers occur in the README; not semantic proof |
| [`tools/audit_kind.py`](tools/audit_kind.py) | **Read-only verifier** — checks for `index.html` at each configured Pages path; only HTTP 200/404 resolve type, other responses are unresolved |

### Testing the interface

The deployed site runs from static files. Node.js and Python are needed only for
development checks; Playwright is a pinned dev dependency and is not part of the
deployed application.

```bash
npm ci
npm run check
npx playwright install --with-deps chromium firefox webkit
npm test                          # Chromium, Firefox, WebKit, and mobile Chromium
npm run test:chromium             # desktop Chromium only
```

Tests use a local static server and synthetic browser fixtures; they do not
replace the independent API/prose/kind audits or check upstream Pages uptime.
`.github/workflows/test.yml` runs the browser suite on pull requests and pushes
to `main`. Failure traces are uploaded by CI.

### Refreshing the directory

```bash
python3 tools/build_data.py              # refreshes official API metadata and data/sites.js
python3 tools/verify_live.py              # independent read-only API comparison
python3 tools/audit_kind.py               # re-derives configured-path index.html classification
rm -rf tools/.readme-cache               # ensure the next read uses current pinned README text
python3 tools/audit_descriptions.py       # numeric-token lint; review is still semantic
python3 tools/build_verification.py       # regenerate VERIFICATION.md after the audit reports
npm run check
npm test                                  # requires installed Playwright browsers
```

The generator prints a `PROSE-STALE` queue for descriptions whose recorded
`verifiedAtSha` no longer matches the current default-branch head. That is a
reason to re-read the cited repository files and update the description/source
basis; the mismatch alone does not prove the prose is false. If a repository
moves while the audit is in progress, refresh and rerun the independent checks
before publishing. A successful numeric-token lint is not a semantic audit.

If GitHub API access is blocked, `python3 tools/build_data.py --overlay-only`
can re-render curated narrative into the **existing** snapshot without network
access. It cannot discover new repositories, refresh API metadata, or see commits
made after that snapshot, so it is not a substitute for a full refresh before
publication. `tools/audit_descriptions.py` caches README bodies in
`tools/.readme-cache`; remove that cache before an audit when source freshness
matters.

`verify_live.py` distinguishes mismatches from fields that may drift because of
GitHub's asynchronous metadata updates. Authentication or network failures are
not evidence that entries are missing or sites are down; discard an incomplete
run and retry after access is restored. The sandbox could not fetch Playwright
browser binaries from its CDN during this pass, so the browser suite is left to
CI rather than reported as passed.

---

## Verification & Source Policy

1. **Use sources, not inference.** API-derived fields come from GitHub's official
   REST API. Titles, categories, short descriptions, and flags are curated from
   repository-owned files and record their evidence and commit in
   `tools/overlay.json`. Do not infer a project's behavior from its name, badge,
   topic, or an `index.html` alone.
2. **Keep snapshot and prose provenance separate.** API metadata is refreshed
   by `tools/build_data.py`; description provenance uses `lastVerified`,
   `verifiedAtSha`, and `verifiedBasis`. A matching SHA records what was read,
   not proof that every sentence is true. Stale stamps remain visible until the
   source is reviewed; never re-stamp to hide a mismatch.
3. **Run independent read-only checks.** `verify_live.py` checks API fields,
   `audit_kind.py` checks the configured Pages entry point, and
   `audit_descriptions.py` performs a numeric-token lint against the README.
   The latter cannot establish meaning or verify non-numeric claims.
4. **State limits and irregularities plainly.** Pages status `built` is not an
   uptime test; an HTML entry point is not proof of interactivity; commit dates
   do not show site use. Keep exclusions and unreachable records in the audit
   trail, and register reproducible irregularities rather than smoothing them
   over.
5. **Do not claim zero hallucinations or exhaustive defect detection.** Verify
   each concrete statement from an official or otherwise identified source and
   describe what could not be checked.

---

## Repository Exclusions — Standing Instruction

`ProjX` remains public upstream but is permanently excluded from this directory by
owner request. Do not add it to the overlay, generated dataset, ledger table, or
exports. At the current snapshot the account API reports **101** public
repositories and **101** Pages-enabled repositories; the directory lists **100**
and records `ProjX` as the single deliberate omission. `kanlerxz87-cyber` has
**0** public repositories and **0** Pages-enabled repositories. The generator
filters the exclusion after the official API read and asserts that listed plus
excluded Pages repositories match the account total.

---

## Unreachable Entries — Owner Review Required

The live API audit on 2026-09-29 returned HTTP 404 for all four repositories
below. They are excluded from active site counts but retained with their last
verified data in the Unreachable panel and `VERIFICATION.md` § 2b.

| Repository | Last recorded head / commit count | Last Pages status | Current finding | Follow-up |
|---|---:|---|---|---|
| `JobSearchSF` | `f68c452` / 68 | `built` | Repository API returns 404 | Owner: restore it or confirm retirement |
| `MALTA` | `f0fb352` / 40 | `built` | Repository API returns 404 | Owner: confirm deletion and whether its dossier survives elsewhere |
| `MALTA-LAWS` | `18f3323` / 3 | `built` | Repository API returns 404 | Owner: restore it or confirm retirement |
| `MALTA2` | `e806c87` / 1 | `built` | Repository API returns 404 | Owner: confirm the Malta-family deletions were intentional |

The frozen Pages URLs are expected to be unavailable until the repositories are
restored. The API check establishes the repository 404, not the intention behind
the deletion or privacy change.

---

## Known Limitations

1. **Thirty-five descriptions are behind their recorded repository head.** The
   UI and ledger mark these entries as a re-read queue. A new commit does not by
   itself prove a description is false, but this status is not a current-head
   semantic verification. Review the cited repository files before carrying or
   rewriting each description.
2. **Pages metadata is not runtime monitoring.** This sandbox cannot establish
   that all published URLs return working page bodies in a browser. GitHub's
   Pages API status (`built`) and the existence of a configured-path
   `index.html` are structural metadata only. Manual live links are provided;
   an automated HTTP check would need to run from an environment with access to
   `*.github.io`.
3. **GitHub does not expose last site use through the public repository/Pages
   API.** The displayed “Last commit” is only the newest committer timestamp on
   the default branch. Usage data would require a separate analytics source and
   is not inferred here.
4. **The `HTML entry point` label is intentionally narrow.** It means a
   configured-path `index.html` exists. It does not guarantee interactivity,
   valid assets, accessibility, or a successful browser render. Likewise,
   `built` does not guarantee the live page is healthy.
5. **The description audit is a numeric-token lint.** It detects numbers not
   found in the README and has 42 documented exceptions for source numbers that
   live elsewhere or are measured independently. A clean lint does not prove
   semantic accuracy; repository files can contradict their own README, and the
   irregularities register records known cases without claiming exhaustiveness.
6. **The account can change during and after a snapshot.** Current API values
   are independently checked, and 35 prose stamps already lag the current head.
   Re-run the refresh and audits before relying on a later reading.
7. **Four previously listed repositories are currently 404** and await owner
   review, while `ProjX` remains intentionally excluded. The other named
   account currently has no public repositories.
8. **Browser tests were not completed in this sandbox.** `npm run check` and
   Python syntax checks pass, but Playwright browser binaries could not be
   downloaded because the browser CDN connection reset. CI is configured to
   install Chromium, Firefox, and WebKit and run the full suite.

---

## Remaining Work and Suggestions

| Priority | Follow-up | Why |
|---|---|---|
| High | Re-read the **35 stale descriptions** against current repository-owned files, prioritize the newest/moving repositories, and update `verifiedAtSha` only after review | Removes the largest remaining provenance gap without treating commit movement alone as proof of an error |
| High | Confirm the pull-request browser workflow passes; if it fails, inspect the CI trace and fix the defect before merging | Local browser binaries were unavailable in this sandbox |
| Owner review | Resolve `JobSearchSF`, `MALTA`, `MALTA-LAWS`, and `MALTA2` (restore or confirm retirement) | Their repositories currently return HTTP 404; only the owner can establish intent |
| Medium | Add scheduled API/prose/kind audits that open a review PR when results drift | The catalog changes over time; a repeatable schedule shortens the snapshot-to-review interval |
| Medium | Run a live HTTP check from an environment that can reach `*.github.io` | Would verify rendered page responses beyond Pages API metadata and configured-path files |
| Optional | Decide how to present overlapping or sibling projects | Some repositories describe related, copied, or draft work; the directory preserves them as separate repositories and does not infer consolidation intent |
| Optional | Add an explicit analytics source only if site-use dates are required | The GitHub API cannot supply last visit/usage timestamps |
