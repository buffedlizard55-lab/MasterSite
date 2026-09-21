# MasterSite

The **master list and directory of the GitHub Pages sites published under** [`buffedlizard55-lab`](https://github.com/buffedlizard55-lab) (with a verified audit of [`kanlerxz87-cyber`](https://github.com/kanlerxz87-cyber)) — generated entirely from official GitHub REST API reads, with zero manual data entry and zero hallucinations. One repository is deliberately unpublished by owner request, and one previously listed site is frozen as unreachable because it no longer exists upstream.

**Live Directory:** <https://buffedlizard55-lab.github.io/MasterSite/>

---

## Audit status — 2026-09-21 (API snapshot `2026-09-21T23:07:59Z`)

| Metric | Value |
|---|---|
| GitHub Pages sites published in the directory | **52** |
| Interactive apps / documentation stubs | **46 / 6** |
| Pages builds reporting `built` | **52 / 52** |
| Descriptions stamped with the commit they were read at | **52 / 52** (`verifiedAtSha`) |
| Descriptions provably behind their repository head | **0** |
| Descriptions re-read in this pass / carried forward | **23 / 29** (the generator's `proseReReadLatestPass: 1` counts only entries sharing the single newest `lastVerified` timestamp, so it understates a multi-hour pass — the honest figure is the count of entries with a 2026-09-21 or later stamp) |
| Verifier results | **all three clean** — 686/686 live field checks (0 hard mismatches), 0 descriptions needing manual confirmation (16 documented exceptions), 52/52 `kind` re-derivations with 0 disagreements |
| Commits audited across the listed repositories | **2909** |
| Public repositories on the account (API) | **53** |
| Pages sites on the account (API) | **53** |
| Repositories withheld, each with a stated reason | **1** (`ProjX` — permanently excluded by owner request) |
| Unreachable entries (needs owner review) | **1** (`JobSearchSF` — HTTP 404, re-confirmed 2026-09-21) |
| Irregularities registered | **72** (`IRR-01` … `IRR-72`) |
| Categories | **10** — Sports Data & Scoreboards (18), Travel & Korea Trip (11), Markets & Trading Research (9), SF Local Guides (6), Directory & Meta (3), Elections & Civic Data (1), Gaming & Guides (1), Health & Personal Guides (1), Science & ML Research (1), Social & Creator Data (1) |

The generator proves its own arithmetic: `listed + withheld = Pages sites on the account` is asserted at build time (52 + 1 = 53), and every withheld repository is named with its reason in `data/sites.js → counts.unlisted`. There is no silent gap.

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

For each of the **52 GitHub Pages sites** in the directory:

- **Live Site Link** & **Repository Link**
- **Sourced Brief Description** — extracted line by line from the repository's own `README.md` and published file structure
- **Created Date** — GitHub `created_at`, with the first-commit timestamp and SHA shown alongside
- **Last Updated Date** — newest committer timestamp on the default branch, with the latest commit SHA, plus `pushed_at`
- **GitHub Pages Status & Build Source** — all 52 reporting `built`; 51 publishing from `main /` and 1 (`GOLD`) from `main /docs`
- **Total Commits on the Default Branch**, repository size, and app-vs-stub classification
- **Official Source Links for Manual Review** — live URL, repository, Pages API JSON, commits API, and Pages settings
- **Verification provenance per entry** — `lastVerified` (when the prose was read), `verifiedBasis` (what was read, and the exact command or endpoint that reproduces it) and `verifiedAtSha` (the commit it was read against, compared against the live head on every build)
- **Per-entry audit flags** and a **72-entry flagged irregularities register** (`IRR-01` … `IRR-72`), ordered by severity

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
| [`data/sites.js`](data/sites.js) | **Generated** verified dataset — 52 sites, 1 unreachable entry, 72 irregularities, 2 audited accounts, methodology |
| [`tools/overlay.json`](tools/overlay.json) | Hand-authored narrative: titles, categories, descriptions, flags, the irregularity register, the permanent exclusion list |
| [`tools/build_data.py`](tools/build_data.py) | **Generator** — reads the official GitHub API and writes `data/sites.js` |
| [`tools/build_verification.py`](tools/build_verification.py) | **Generator** — renders `VERIFICATION.md` from `data/sites.js` |
| [`AGENTS.md`](AGENTS.md) | Standing maintenance instructions for future sessions, including the permanent repository exclusion |
| [`VERIFICATION.md`](VERIFICATION.md) | **Generated** line-by-line audit ledger with official endpoints, commit SHAs and reproduction commands |
| [`tools/verify_live.py`](tools/verify_live.py) | **Read-only verifier** — re-reads every API-derived field of every entry and reports ok / mismatch / drift. Never writes the dataset |
| [`tools/audit_descriptions.py`](tools/audit_descriptions.py) | **Read-only verifier** — checks every numeric claim in a description against the repository's own README |
| [`tools/audit_kind.py`](tools/audit_kind.py) | **Read-only verifier** — re-derives each entry's app-vs-stub `kind` from the API and reports any disagreement with the committed value |

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
4. **Transparent Irregularity Reporting.** Every anomaly is catalogued with the endpoint needed to reproduce it, ordered by severity (`critical` → `warn` → `info`). This audit added nine (`IRR-64` … `IRR-72`), two of them `critical`.
5. **Nothing Is Silently Deleted.** Excluded and unreachable repositories are named, explained and preserved with their last verified values.
6. **Corrections Are Recorded, Not Hidden.** When a published description turns out to have been wrong, the entry is fixed *and* the mistake is registered with what it said, what it should have said, and how it was caught — see `IRR-25` through `IRR-29`.

---

## Repository Exclusions — Standing Instructions for Future Sessions

One repository on the account is **permanently excluded** from this site. Do not list it, link it, count it, or export it — in any future session, regeneration, or refresh of this directory.

| Excluded repository | Status | Instruction |
|---|---|---|
| `ProjX` | Still live on GitHub; intentionally unpublished **here** since 2026-09-12 by owner request | **Never add it back** to `data/sites.js`, the `VERIFICATION.md` ledger table, README counts, or the JSON/CSV exports. No live link, API endpoint or Pages URL for it is printed anywhere in this repository. Full rationale in [VERIFICATION.md § 2a](VERIFICATION.md#2a-repository-exclusions-deliberately-omitted). |

Because of this exclusion the directory shows **52** sites while the GitHub API reports **53** public Pages repositories. That mismatch is correct and expected: keep the account-level totals (`publicRepos: 53`, `pagesSites: 53`) at their verified API values and filter excluded names *after* the API read, instead of lowering those totals. `tools/build_data.py` applies the `excluded` list from `tools/overlay.json` automatically, records every withheld repository with its reason in `counts.unlisted`, and **asserts at build time** that `listed + withheld == pagesSites` so a silent gap is impossible.

---

## Unreachable Entries — Needs Owner Review

| Repository | Last verified | What happened | Owner action |
|---|---|---|---|
| `JobSearchSF` | `f68c452`, 2026-09-16T19:37:41Z, 68 commits | Re-confirmed 2026-09-21 (fourth consecutive audit): `GET /repos/buffedlizard55-lab/JobSearchSF` returns **HTTP 404** and the repository is absent from the account's 53-repository public list, so it was deleted or made private. Its Pages site is therefore no longer served. | **Restore it** (undelete / make public) so it can be re-listed, **or confirm it should stay retired** and the frozen entry can be dropped. Flagged as `IRR-01` (critical). |

The entry stays visible in the site's *Unreachable — Needs Owner Review* panel and in `VERIFICATION.md` § 2b with every value it last verified, plus the three commands that reproduce the 404.

---

## Known Limitations

These are the real obstacles, stated plainly. Several are the reason a claim can be "verified" today and wrong tomorrow.

1. **The prose is the fragile part, not the numbers — and 2026-09-21 proved it twice more.** Every timestamp, SHA, commit count and Pages status is read from `api.github.com` and re-checked by `tools/verify_live.py` (686/686 clean this pass). Descriptions are written prose, and this audit found **two published descriptions that were flatly false**: `MLBComp` described as a placeholder when it had become a full application (`IRR-64`), and `NFLComp` publishing a **+$2.43M profit that is actually a −$353K loss** (`IRR-65`). `verifiedAtSha` reliably told us *which* entries to re-read; it cannot tell us what they now say.
2. **A matching SHA proves the prose was read against those bytes, never that the prose is true — and a README-unchanged diff proves even less.** This pass, the README changed in only 13 of the 20 stale ranges, yet **four of the five sharpest findings came from ranges that touched no README at all** (`IRR-70`). A SHA-only re-stamp would have missed `IRR-68` entirely.
3. **Three upstream repositories contradict themselves, so "read the README" is not sufficient either.** `Elections` states 209 sources in one place and 189 in another while its file holds **229**, and claims 63 irregularities against a file holding **58** (`IRR-67`); `NBAInjuryReport`'s prose is two days behind its own regenerated data (`IRR-68`); `OLBG-Competition` says 262 tests where the test functions count 258. Where prose and file disagree, this directory now **publishes the counted file value and flags the prose** — but that policy has to be applied by hand, every time.
4. **Live page bodies are still not fetched over HTTP.** Pages liveness rests on two API facts — status `built` and a real `index.html` at the published path — not an HTTP 200 on the rendered page. Re-tested 2026-09-21: this sandbox still cannot reach `*.github.io` (`curl` returns `000`, an `SSL_ERROR_SYSCALL` on connect, while `api.github.com` returns 200), so the block is network egress, not configuration. A site can be `built` and still render a blank page. Every entry links its live URL for one-click manual review.
5. **Repositories move faster than the audit can snapshot — six changed state *during this pass*.** `MLBComp` changed twice (placeholder → app → source snapshot loaded, `IRR-72`), `DrugAnalysis` went v26 → v27 within the hour, and `Commodities`, `NFLComp`, `NFLInjuryReport` and `VacationSchedule` all moved mid-audit. **Six successive builds** were needed before the gate reached zero. Two repositories (`SelfLearn`, `MasterSelfLearn`) were created at 22:41Z while the audit was running (`IRR-71`).
6. **The youngest entries remain where every error comes from.** `MLBComp` and `NFLComp`, both critical findings this pass, were **under 48 hours old**. Four audits running, every stale-description defect has traced to a repository under two days old. Re-read the youngest entries first.
7. **Some upstream test suites cannot be executed here, so a few counts are of test *functions* rather than *assertions*.** `NHLComp`'s suite runs only with `PYTHONPATH=src` (231 tests, verified); `MLBComp`'s Python suite needs `pandas`, which is absent, so only its Node contract test was executed; `OLBG-Competition` has no `pytest` available, so its 258 is a `def test_` count that may differ from collected parametrised cases. Each of these is disclosed in the entry's own `verifiedBasis` rather than presented as a measured pass.
8. **Repository size is GitHub's asynchronously-recomputed field**, so size moves that do not line up with commit deltas are normal (`IRR-04`–`IRR-06`). `GEMSDOE` alone is ~400 MB because competition rasters are committed as git parts.
9. **`kanlerxz87-cyber` contributes nothing.** Verified to exist (`type: User`, created `2026-08-03T20:56:16Z`) with **0** public repositories (re-verified 2026-09-21). If it ever publishes, the generator picks it up automatically.
10. **One repository is permanently excluded by owner request** (`ProjX`), so the directory will always show one fewer site than the account totals. Deliberate; see [Repository Exclusions](#repository-exclusions--standing-instructions-for-future-sessions).
11. **`JobSearchSF` cannot be resolved from here** — HTTP 404 for a fourth consecutive audit. Owner decision only (`IRR-01`).
12. **Credentials can die mid-audit, and when they do the verifiers lie.** A uniform HTTP 401 across every entry means dead credentials, not 52 broken records (`IRR-55`). Check `gh auth status` before acting on any verifier output, and discard such a run rather than committing it.

---

## What Still Needs To Be Done

Ordered by what actually threatens the project's core promise. **Items 1 and 2 are the work for the next session.**

| # | Task | Why it matters | Effort |
|---|---|---|---|
| 1 | **Re-read every description against its repository, by hand, once per audit — and open the *data files*, not just the README.** The new rule this pass: where a repository generates its own counts into a JSON/CSV artifact, read that artifact and publish its value. | Still the only error class that has materially misled a reader, now across five consecutive audits, and this pass produced the worst instance yet — a headline PnL published with the wrong sign (`IRR-65`). `verifiedAtSha` turns an unbounded job into a work queue but cannot do the reading, and `IRR-70` shows a README-unchanged diff is not a safe shortcut. | **High — start here** |
| 2 | **Report the three self-contradiction defects upstream** (`Elections` 209/189/229 and 63/58, `NBAInjuryReport` 65/21 vs 94/70, `OLBG-Competition` 262/258) so the repositories fix their own prose instead of this directory carrying a permanent footnote. | A directory that grades other projects' verification should not need a standing workaround for their arithmetic. Each is a one-line fix at the source. | Owner / upstream |
| 3 | **Resolve `JobSearchSF` (`IRR-01`).** Restore the repository, or confirm it is retired so the frozen entry can be dropped. | The oldest open `critical` irregularity (2026-09-17), now in its fourth audit. No machine can resolve it. | Owner only |
| 4 | **Fetch live pages over HTTP from an environment with egress to `*.github.io`.** A GitHub Actions job in this repository would have that access even though the audit sandbox does not. | It is the difference between "GitHub says it built" and "it works". This is the single biggest *verifiable* gap left in the methodology, and it is now clearly solvable — the blocker is the sandbox, not the design. | **Medium — highest-value new capability** |
| 5 | **Describe `SelfLearn` and `MasterSelfLearn` properly once they contain something.** Both are one-line stubs created 2026-09-21T22:41Z; their descriptions deliberately say nothing about intent because the repositories say nothing (`IRR-71`). | Two of the six stub entries exist only to keep the accounting honest. The moment either gains content, its entry must be rewritten from that content. | Low |
| 6 | **Move `GEMSDOE`'s ~400 MB of rasters out of git** (Git LFS or a release asset). | Real operational cost; growth pattern documented in `IRR-04`. | Medium |
| 7 | **Decide whether overlapping entries should stay listed.** `HotelSeoulRoughdraft1` duplicates `Itinerary-Korea` (`IRR-14`); `MLB-PBP`/`MLB-Live-PBP` overlap, and `MLBRainDelay` is now explicitly built on `MLB-Live-PBP`'s design; `ScheduleFreeTime` and `VacationSchedule` overlap without naming each other (`IRR-48`). | A directory is more useful when it does not send readers to a superseded draft. Curation, not data. | Owner only |
| 8 | **Automate the audit on a schedule** (GitHub Actions running `build_data.py` + all three verifiers, opening a PR when the gate is non-zero). | Six repositories changed state *during* this one audit and two were created mid-run. A scheduled job would keep the window between snapshot and reality to hours instead of days — and combined with item 4, would run from an environment that can reach the live sites. | Medium |

**Closed this pass:** ~~the `IRR-43` class of finding ("built site lives in `docs/` but Pages publishes `main /`, so the live URL serves a Jekyll README render")~~ — **resolved for every affected repository.** `MLBComp`, `NHLComp` and `VacationSchedule` all now commit a root `index.html`, `audit_kind.py` reports **0 disagreements across 52 sites**, and the standing owner-action items asking for a Settings → Pages change are withdrawn.
