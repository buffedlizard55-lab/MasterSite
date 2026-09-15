# MasterSite — Comprehensive Line-by-Line Verification Ledger

**Audit Date:** 2026-09-15 (UTC) — full re-verification refresh (prior baseline audit: 2026-09-12)
**Auditor:** Automated Verification Agent (Arena.ai Agent Mode) — Autonomous execution with zero manual input
**Audited Accounts:** `buffedlizard55-lab`, `kanlerxz87-cyber`
**Scope:** 100% of public repositories and GitHub Pages deployments hosted under both accounts
**Integrity Standard:** Zero hallucinations. Every metric, date, commit SHA, file structure, and description is verified directly against official GitHub REST API endpoints and repository source files.

---

## 1. Official Account Verification

| Account | GitHub Profile | Official API Endpoint | Type | Account Created (UTC) | Public Repos | Pages Sites | Status & Review Notes |
|---|---|---|---|---|---|---|---|
| `buffedlizard55-lab` | [github.com/buffedlizard55-lab](https://github.com/buffedlizard55-lab) | [`/users/buffedlizard55-lab`](https://api.github.com/users/buffedlizard55-lab) | User | 2026-07-27T01:05:09Z | 35 | 35 | ✅ Verified: All 35 repositories have GitHub Pages enabled and built. This directory publishes 34 of them — see [Section 2a. Repository Exclusions](#2a-repository-exclusions-deliberately-omitted). |
| `kanlerxz87-cyber` | [github.com/kanlerxz87-cyber](https://github.com/kanlerxz87-cyber) | [`/users/kanlerxz87-cyber`](https://api.github.com/users/kanlerxz87-cyber) | User | 2026-08-03T20:56:16Z | 0 | 0 | ✅ Verified: Account exists but contains 0 public repositories and 0 Pages sites. Flagged as `IRR-01`. |

---

## 2. Master Repository & GitHub Pages Audit Ledger (34 / 34 Directory Entries Verified)

Every line below was queried directly via GitHub REST API endpoints:
- `GET https://api.github.com/users/buffedlizard55-lab/repos?per_page=100` (35 repositories returned; 1 is excluded from this directory, see Section 2a)
- `GET https://api.github.com/repos/buffedlizard55-lab/{repo}`
- `GET https://api.github.com/repos/buffedlizard55-lab/{repo}/pages`
- `GET https://api.github.com/repos/buffedlizard55-lab/{repo}/commits?per_page=100` (paginated)
- `GET https://api.github.com/repos/buffedlizard55-lab/{repo}/readme`

| # | Repository | Category | Type | Pages Status | Source | Created (UTC) | First Commit | Last Commit on Main (UTC) | Latest SHA | Total Commits | Live Site & Official Sources |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `AirPremia` | Travel & Korea Trip | Live App | built | `main /` | 2026-09-11 19:07:00 | `ea66715` | 2026-09-11 21:01:59 | `af7f167` | 7 | [Live Site](https://buffedlizard55-lab.github.io/AirPremia/) · [Repo](https://github.com/buffedlizard55-lab/AirPremia) · [API](https://api.github.com/repos/buffedlizard55-lab/AirPremia/pages) |
| 2 | `BathTubOverflowSF` | SF Local Guides | Live App | built | `main /` | 2026-09-10 21:23:42 | `822af8c` | 2026-09-15 04:39:32 | `45854a5` | 41 | [Live Site](https://buffedlizard55-lab.github.io/BathTubOverflowSF/) · [Repo](https://github.com/buffedlizard55-lab/BathTubOverflowSF) · [API](https://api.github.com/repos/buffedlizard55-lab/BathTubOverflowSF/pages) |
| 3 | `BusanL7HaeundaeLotteHotelStay` | Travel & Korea Trip | Live App | built | `main /` | 2026-08-30 19:42:20 | `6b266f3` | 2026-09-01 23:58:50 | `a3545e6` | 17 | [Live Site](https://buffedlizard55-lab.github.io/BusanL7HaeundaeLotteHotelStay/) · [Repo](https://github.com/buffedlizard55-lab/BusanL7HaeundaeLotteHotelStay) · [API](https://api.github.com/repos/buffedlizard55-lab/BusanL7HaeundaeLotteHotelStay/pages) |
| 4 | `CruiseDeals` | Travel & Korea Trip | Live App | built | `main /` | 2026-08-26 18:59:54 | `b1bf188` | 2026-08-30 02:00:30 | `8b6fad8` | 33 | [Live Site](https://buffedlizard55-lab.github.io/CruiseDeals/) · [Repo](https://github.com/buffedlizard55-lab/CruiseDeals) · [API](https://api.github.com/repos/buffedlizard55-lab/CruiseDeals/pages) |
| 5 | `DrugAnalysis` | Markets & Trading Research | Live App | built | `main /` | 2026-09-10 21:10:50 | `3c4c4c8` | 2026-09-13 03:47:09 | `6714ac6` | 46 | [Live Site](https://buffedlizard55-lab.github.io/DrugAnalysis/) · [Repo](https://github.com/buffedlizard55-lab/DrugAnalysis) · [API](https://api.github.com/repos/buffedlizard55-lab/DrugAnalysis/pages) |
| 6 | `GEMSDOE` | Science & ML Research | Live App | built | `main /` | 2026-09-12 18:46:56 | `10585e5` | 2026-09-15 04:43:14 | `fa40c51` | 47 | [Live Site](https://buffedlizard55-lab.github.io/GEMSDOE/) · [Repo](https://github.com/buffedlizard55-lab/GEMSDOE) · [API](https://api.github.com/repos/buffedlizard55-lab/GEMSDOE/pages) |
| 7 | `GOLD` | Markets & Trading Research | Live App | built | `main /docs` | 2026-08-17 21:05:38 | `46e0343` | 2026-08-28 20:50:02 | `3e6f149` | 52 | [Live Site](https://buffedlizard55-lab.github.io/GOLD/) · [Repo](https://github.com/buffedlizard55-lab/GOLD) · [API](https://api.github.com/repos/buffedlizard55-lab/GOLD/pages) |
| 8 | `HongdaeStay` | Travel & Korea Trip | Live App | built | `main /` | 2026-09-01 04:32:20 | `e0c3911` | 2026-09-02 02:00:48 | `72e1225` | 15 | [Live Site](https://buffedlizard55-lab.github.io/HongdaeStay/) · [Repo](https://github.com/buffedlizard55-lab/HongdaeStay) · [API](https://api.github.com/repos/buffedlizard55-lab/HongdaeStay/pages) |
| 9 | `HotelSeoulRoughdraft1` | Travel & Korea Trip | Live App | built | `main /` | 2026-08-10 03:27:08 | `5f25755` | 2026-08-18 22:12:49 | `765c2ca` | 17 | [Live Site](https://buffedlizard55-lab.github.io/HotelSeoulRoughdraft1/) · [Repo](https://github.com/buffedlizard55-lab/HotelSeoulRoughdraft1) · [API](https://api.github.com/repos/buffedlizard55-lab/HotelSeoulRoughdraft1/pages) |
| 10 | `Insider-trades` | Markets & Trading Research | Live App | built | `main /` | 2026-08-07 00:24:35 | `3c5fa64` | 2026-08-19 17:06:22 | `34c3ac2` | 17 | [Live Site](https://buffedlizard55-lab.github.io/Insider-trades/) · [Repo](https://github.com/buffedlizard55-lab/Insider-trades) · [API](https://api.github.com/repos/buffedlizard55-lab/Insider-trades/pages) |
| 11 | `Itinerary-Korea` | Travel & Korea Trip | Live App | built | `main /` | 2026-08-10 01:58:52 | `49fd9b8` | 2026-08-18 20:40:06 | `7f4a6b7` | 9 | [Live Site](https://buffedlizard55-lab.github.io/Itinerary-Korea/) · [Repo](https://github.com/buffedlizard55-lab/Itinerary-Korea) · [API](https://api.github.com/repos/buffedlizard55-lab/Itinerary-Korea/pages) |
| 12 | `JobSearchSF` | SF Local Guides | Live App | built | `main /` | 2026-09-09 19:11:20 | `2f69a19` | 2026-09-15 04:13:42 | `2ebfa37` | 23 | [Live Site](https://buffedlizard55-lab.github.io/JobSearchSF/) · [Repo](https://github.com/buffedlizard55-lab/JobSearchSF) · [API](https://api.github.com/repos/buffedlizard55-lab/JobSearchSF/pages) |
| 13 | `Korea` | Travel & Korea Trip | Live App | built | `main /` | 2026-08-03 18:16:02 | `57de541` | 2026-08-29 01:04:54 | `bfabd46` | 65 | [Live Site](https://buffedlizard55-lab.github.io/Korea/) · [Repo](https://github.com/buffedlizard55-lab/Korea) · [API](https://api.github.com/repos/buffedlizard55-lab/Korea/pages) |
| 14 | `Korea-emergency` | Travel & Korea Trip | Live App | built | `main /` | 2026-08-05 17:04:39 | `aa05f31` | 2026-08-21 22:41:38 | `ac15af6` | 20 | [Live Site](https://buffedlizard55-lab.github.io/Korea-emergency/) · [Repo](https://github.com/buffedlizard55-lab/Korea-emergency) · [API](https://api.github.com/repos/buffedlizard55-lab/Korea-emergency/pages) |
| 15 | `KoreaHotels` | Travel & Korea Trip | Live App | built | `main /` | 2026-08-10 02:13:22 | `b8ee533` | 2026-08-30 17:52:06 | `a42e222` | 89 | [Live Site](https://buffedlizard55-lab.github.io/KoreaHotels/) · [Repo](https://github.com/buffedlizard55-lab/KoreaHotels) · [API](https://api.github.com/repos/buffedlizard55-lab/KoreaHotels/pages) |
| 16 | `Leg3SeoulTrip` | Travel & Korea Trip | Doc Stub | built | `main /` | 2026-08-30 23:59:40 | `e325587` | 2026-08-30 23:59:40 | `e325587` | 1 | [Live Site](https://buffedlizard55-lab.github.io/Leg3SeoulTrip/) · [Repo](https://github.com/buffedlizard55-lab/Leg3SeoulTrip) · [API](https://api.github.com/repos/buffedlizard55-lab/Leg3SeoulTrip/pages) |
| 17 | `MLB-Live-PBP` | Sports Data & Scoreboards | Live App | built | `main /` | 2026-08-07 00:18:05 | `cc9a58c` | 2026-09-05 04:31:12 | `6d61092` | 66 | [Live Site](https://buffedlizard55-lab.github.io/MLB-Live-PBP/) · [Repo](https://github.com/buffedlizard55-lab/MLB-Live-PBP) · [API](https://api.github.com/repos/buffedlizard55-lab/MLB-Live-PBP/pages) |
| 18 | `MLB-PBP` | Sports Data & Scoreboards | Live App | built | `main /` | 2026-08-11 08:36:07 | `ebbb946` | 2026-08-11 17:13:16 | `704e609` | 7 | [Live Site](https://buffedlizard55-lab.github.io/MLB-PBP/) · [Repo](https://github.com/buffedlizard55-lab/MLB-PBP) · [API](https://api.github.com/repos/buffedlizard55-lab/MLB-PBP/pages) |
| 19 | `MLB-Prediction-model-backtest` | Sports Data & Scoreboards | Doc Stub | built | `main /` | 2026-08-17 07:21:43 | `c842c95` | 2026-08-17 23:49:33 | `0e36573` | 73 | [Live Site](https://buffedlizard55-lab.github.io/MLB-Prediction-model-backtest/) · [Repo](https://github.com/buffedlizard55-lab/MLB-Prediction-model-backtest) · [API](https://api.github.com/repos/buffedlizard55-lab/MLB-Prediction-model-backtest/pages) |
| 20 | `MasterSite` | Directory & Meta | Live App | built | `main /` | 2026-09-12 00:16:13 | `f724b59` | 2026-09-12 01:20:59 | `6da28b0` | 8 | [Live Site](https://buffedlizard55-lab.github.io/MasterSite/) · [Repo](https://github.com/buffedlizard55-lab/MasterSite) · [API](https://api.github.com/repos/buffedlizard55-lab/MasterSite/pages) |
| 21 | `NFL-scoreboard` | Sports Data & Scoreboards | Live App | built | `main /` | 2026-08-21 08:42:57 | `e60408c` | 2026-09-10 17:41:32 | `fce4afc` | 40 | [Live Site](https://buffedlizard55-lab.github.io/NFL-scoreboard/) · [Repo](https://github.com/buffedlizard55-lab/NFL-scoreboard) · [API](https://api.github.com/repos/buffedlizard55-lab/NFL-scoreboard/pages) |
| 22 | `NFLInjuryReport` | Sports Data & Scoreboards | Live App | built | `main /` | 2026-09-10 21:59:35 | `5d8a07f` | 2026-09-15 22:10:28 | `e5ba704` | 57 | [Live Site](https://buffedlizard55-lab.github.io/NFLInjuryReport/) · [Repo](https://github.com/buffedlizard55-lab/NFLInjuryReport) · [API](https://api.github.com/repos/buffedlizard55-lab/NFLInjuryReport/pages) |
| 23 | `NFLPRED` | Sports Data & Scoreboards | Doc Stub | built | `main /` | 2026-08-17 21:26:42 | `44b7961` | 2026-08-17 21:26:43 | `44b7961` | 1 | [Live Site](https://buffedlizard55-lab.github.io/NFLPRED/) · [Repo](https://github.com/buffedlizard55-lab/NFLPRED) · [API](https://api.github.com/repos/buffedlizard55-lab/NFLPRED/pages) |
| 24 | `Ncaa-football-alerts` | Sports Data & Scoreboards | Live App | built | `main /` | 2026-08-25 07:59:11 | `0385a4f` | 2026-09-06 00:31:01 | `a41566c` | 42 | [Live Site](https://buffedlizard55-lab.github.io/Ncaa-football-alerts/) · [Repo](https://github.com/buffedlizard55-lab/Ncaa-football-alerts) · [API](https://api.github.com/repos/buffedlizard55-lab/Ncaa-football-alerts/pages) |
| 25 | `PFFNFL` | Sports Data & Scoreboards | Doc Stub | built | `main /` | 2026-08-17 16:29:40 | `7a913c7` | 2026-08-17 21:12:44 | `0f00b26` | 3 | [Live Site](https://buffedlizard55-lab.github.io/PFFNFL/) · [Repo](https://github.com/buffedlizard55-lab/PFFNFL) · [API](https://api.github.com/repos/buffedlizard55-lab/PFFNFL/pages) |
| 26 | `PlumbingSF` | SF Local Guides | Live App | built | `main /` | 2026-09-03 23:18:30 | `35e2994` | 2026-09-04 20:12:24 | `bae59fe` | 19 | [Live Site](https://buffedlizard55-lab.github.io/PlumbingSF/) · [Repo](https://github.com/buffedlizard55-lab/PlumbingSF) · [API](https://api.github.com/repos/buffedlizard55-lab/PlumbingSF/pages) |
| 27 | `PriceKalshiHistorical` | Markets & Trading Research | Live App | built | `main /` | 2026-08-17 21:27:55 | `542ddd8` | 2026-08-19 17:06:23 | `96ff13c` | 5 | [Live Site](https://buffedlizard55-lab.github.io/PriceKalshiHistorical/) · [Repo](https://github.com/buffedlizard55-lab/PriceKalshiHistorical) · [API](https://api.github.com/repos/buffedlizard55-lab/PriceKalshiHistorical/pages) |
| 28 | `SFLateNight` | SF Local Guides | Live App | built | `main /` | 2026-09-05 20:58:20 | `5b1933c` | 2026-09-06 04:26:17 | `509a1ad` | 30 | [Live Site](https://buffedlizard55-lab.github.io/SFLateNight/) · [Repo](https://github.com/buffedlizard55-lab/SFLateNight) · [API](https://api.github.com/repos/buffedlizard55-lab/SFLateNight/pages) |
| 29 | `ScheduleFreeTime` | Sports Data & Scoreboards | Live App | built | `main /` | 2026-08-27 20:17:13 | `f941565` | 2026-09-15 04:39:31 | `2446f62` | 14 | [Live Site](https://buffedlizard55-lab.github.io/ScheduleFreeTime/) · [Repo](https://github.com/buffedlizard55-lab/ScheduleFreeTime) · [API](https://api.github.com/repos/buffedlizard55-lab/ScheduleFreeTime/pages) |
| 30 | `SportsPred` | Sports Data & Scoreboards | Live App | built | `main /` | 2026-08-31 00:01:45 | `66eb2bb` | 2026-09-05 08:23:55 | `aa3b1fe` | 189 | [Live Site](https://buffedlizard55-lab.github.io/SportsPred/) · [Repo](https://github.com/buffedlizard55-lab/SportsPred) · [API](https://api.github.com/repos/buffedlizard55-lab/SportsPred/pages) |
| 31 | `StanfordStay` | Travel & Korea Trip | Live App | built | `main /` | 2026-08-20 05:35:20 | `5bc9062` | 2026-08-22 08:46:46 | `499fb0a` | 18 | [Live Site](https://buffedlizard55-lab.github.io/StanfordStay/) · [Repo](https://github.com/buffedlizard55-lab/StanfordStay) · [API](https://api.github.com/repos/buffedlizard55-lab/StanfordStay/pages) |
| 32 | `TinoLunchSpecial` | SF Local Guides | Live App | built | `main /` | 2026-09-07 19:05:24 | `c7bd9eb` | 2026-09-15 22:40:52 | `ea33795` | 47 | [Live Site](https://buffedlizard55-lab.github.io/TinoLunchSpecial/) · [Repo](https://github.com/buffedlizard55-lab/TinoLunchSpecial) · [API](https://api.github.com/repos/buffedlizard55-lab/TinoLunchSpecial/pages) |
| 33 | `Tradingview-pinescript-editor` | Markets & Trading Research | Live App | built | `main /` | 2026-08-08 18:27:58 | `351fa6f` | 2026-08-10 01:43:17 | `834312c` | 13 | [Live Site](https://buffedlizard55-lab.github.io/Tradingview-pinescript-editor/) · [Repo](https://github.com/buffedlizard55-lab/Tradingview-pinescript-editor) · [API](https://api.github.com/repos/buffedlizard55-lab/Tradingview-pinescript-editor/pages) |
| 34 | `VapePods` | SF Local Guides | Live App | built | `main /` | 2026-09-14 17:26:14 | `4c2867d` | 2026-09-15 22:43:19 | `b545ce7` | 12 | [Live Site](https://buffedlizard55-lab.github.io/VapePods/) · [Repo](https://github.com/buffedlizard55-lab/VapePods) · [API](https://api.github.com/repos/buffedlizard55-lab/VapePods/pages) |

## 2a. Repository Exclusions (Deliberately Omitted)

The audited account holds **35** public GitHub Pages repositories, while this directory and `data/sites.js` publish **34** entries. That difference is intentional and permanent — it is not a data gap to repair.

| Repository | Pages Status (API) | Reason for Exclusion | Excluded Since | Rule |
|---|---|---|---|---|
| `ProjX` | `built` — repository remains live and untouched on GitHub | Owner directive: this project must not be advertised, linked, or indexed by MasterSite | 2026-09-12 | **Do not re-add.** Omit from `data/sites.js`, from the Section 2 ledger table, from README counts, and from every regenerated export. |

**Verification note:** the repository was audited and its Pages build was confirmed healthy on 2026-09-15 (`status: built`, source `main /`); only its publication in this directory is suppressed. Account-wide totals (35 public repos / 35 Pages sites in `accountsChecked`) stay at their verified API values on purpose so the exclusion stays auditable. Regenerators must therefore filter excluded names *after* the API read instead of lowering the account totals. See [`AGENTS.md`](AGENTS.md) → *Repository Exclusions* for the standing instruction to future sessions.

---

## 3. Flagged Irregularities Register (14 entries: IRR-01 … IRR-14)

| ID | Severity | Title | Verifiable Finding & Resolution |
|---|---|---|---|
| **IRR-01** | `Info` | Second account `kanlerxz87-cyber` has 0 public repositories | Official GitHub API query `GET /users/kanlerxz87-cyber/repos` returns `[]` (empty list). Account exists but contains 0 repositories and therefore 0 GitHub Pages sites. All 34 sites listed in this directory belong to `buffedlizard55-lab`. |
| **IRR-02** | `Warning` | Two repositories are single-commit README-only stubs | `Leg3SeoulTrip` and `NFLPRED` each contain only a single initial commit containing `README.md` and no web app assets (`index.html`). GitHub Pages API reports `status: built` because Jekyll builds the markdown, but only the raw title is rendered. |
| **IRR-03** | `Warning` | Two repositories serve README documentation via Pages | `MLB-Prediction-model-backtest` and `PFFNFL` are Python machine-learning and data scraping research repositories. GitHub Pages is configured to publish from `/`, which serves their documentation READMEs rather than interactive client web apps. |
| **IRR-04** | `Info` | `MasterSite` upgraded from stub to directory app | Prior to the 2026-09-12 deployment, `MasterSite` contained only a single placeholder `README.md`. It has been transformed into the static master directory for the organization (8 commits on `main` as of this audit). |
| **IRR-05** | `Info` | `DrugAnalysis` transient build state during 2026-09-12 push | During the 2026-09-12 audit at ~00:20 UTC, `DrugAnalysis` was being actively pushed to, momentarily returning `status: building` from `/pages` before settling into `built`. Re-verified `built` on 2026-09-15. |
| **IRR-06** | `Info` | `GOLD` publishes from `/docs` folder | 33 of the 34 directory repositories publish Pages from root (`main /`), whereas `GOLD` publishes from `main /docs`. The repository root `index.html` contains an automatic redirect to `/docs/`. |
| **IRR-07** | `Info` | `HotelSeoulRoughdraft1` duplicates `Itinerary-Korea` | `HotelSeoulRoughdraft1` is an earlier rough draft of the Korea Compass planner. Its own `README.md` explicitly designates `Itinerary-Korea` as the production release. |
| **IRR-08** | `Info` | `StanfordStay` geographic scope vs. name | Despite the name `StanfordStay`, the site contains zero content about Stanford, California. It is a dedicated travel itinerary system for the Stanford Hotel Myeongdong in Seoul, South Korea. |
| **IRR-09** | `Info` | `PriceKalshiHistorical` browser simulation vs. backend collector | The automated market data collector and backtester is a Python CLI/daemon tool; GitHub Pages hosts the static in-browser exchange orderbook simulation UI from `/docs`. |
| **IRR-10** | `Info` | Multi-branch `pushed_at` timestamps | In repositories with active `arena/*` session branches (such as `TinoLunchSpecial`, `BathTubOverflowSF`, `GEMSDOE`, and `DrugAnalysis`), `pushed_at` reflects the latest branch activity, while `lastCommit` strictly records the latest committer date on branch `main`. `GEMSDOE` `pushed_at` (2026-09-15T04:50:28Z) is ~7 min later than its latest `main` commit (`fa40c51`, 04:43:14Z); `DrugAnalysis` `pushed_at` (2026-09-13T03:48:27Z) is later than both its latest `main` commit (03:47:09Z) and its `updated_at` (03:47:16Z). |
| **IRR-11** | `Info` | No GitHub Actions deployment records (standard Pages behavior) | `GET /repos/{owner}/{repo}/pages/deployments` returns HTTP 404 for all 34 repositories listed in this directory. This is expected: all sites use standard branch-based Pages publishing (`deploy from a branch`), which does not generate Actions deployment objects. |
| **IRR-12** | `Info` | 1 account repository is intentionally omitted from this directory | The account has 35 Pages-enabled repositories while the directory publishes 34. The missing entry was removed by owner request on 2026-09-12 and is permanently excluded (Section 2a). The count difference is expected; do not re-add the repository to reconcile it. |
| **IRR-13** | `Info` | `GEMSDOE` canonical site lives in `docs/` behind a root redirect | `GEMSDOE` publishes from `main /`, but its root `index.html` is a meta-refresh + JS redirect to `./docs/index.html` (added via merge `fa40c51`, PR #8, 2026-09-15T04:43:14Z) because legacy Jekyll publishing serves the repo root. The generated multi-page evidence site (Overview, Data, Metric, Method, Results, Sources, Reproduce) lives in `docs/`. |
| **IRR-14** | `Info` | 2026-09-15 refresh: 2 new repositories, 7 updated entries | Since the 2026-09-12 audit the account grew from 33 to 35 public Pages repositories (`GEMSDOE` created 2026-09-12, `VapePods` created 2026-09-14; both verified `built`). 7 entries gained new `main`-branch commits (`DrugAnalysis` 8→46, `NFLInjuryReport` 31→57, `BathTubOverflowSF` 27→41, `TinoLunchSpecial` 41→47, `JobSearchSF` 16→23, `ScheduleFreeTime` 12→14, `MasterSite` 4→8). The other 25 listed repositories re-verified identical (same latest SHA, same commit count). |
---

## 4. Line-by-Line Description Verification

All descriptions in `data/sites.js` and `index.html` were formulated directly from the parsed contents of each repository's `README.md` and live application structure. No description was generated from unverified external memory or speculation.

Refresh notes for 2026-09-15: descriptions for `BathTubOverflowSF` (601 records / 12 waves), `DrugAnalysis` (624 FDA decisions), `JobSearchSF` (140 openings, pass 9), `ScheduleFreeTime` (Warriors/Sharks/Westwood One layers), and `TinoLunchSpecial` (850 lunch entries) were updated to match their current verified READMEs. New descriptions for `GEMSDOE` and `VapePods` were sourced line by line from their READMEs, root file listings, and latest merge-commit messages.

---

## 5. Reproduction Commands for Independent Manual Review

Any reviewer with the GitHub CLI (`gh`) or standard `curl` can independently verify any row in this audit:

```bash
# Verify user accounts
gh api /users/buffedlizard55-lab
gh api /users/kanlerxz87-cyber

# List all repositories (expected: 35 for buffedlizard55-lab, 0 for kanlerxz87-cyber)
gh api "/users/buffedlizard55-lab/repos?per_page=100" --jq '.[].name'
gh api "/users/kanlerxz87-cyber/repos?per_page=100"

# Verify Pages status for any repository (e.g. VapePods)
gh api /repos/buffedlizard55-lab/VapePods/pages

# Verify exact commit history and dates
gh api "/repos/buffedlizard55-lab/VapePods/commits?per_page=100"

# Confirm the directory entry count (expected: 34, not 35 — see Section 2a)
grep -c '"repo":' data/sites.js

# Confirm the audited commit total (expected: 1143)
python3 -c "import json; d=json.loads(open('data/sites.js').read().split('=',1)[1].rsplit(';',1)[0]); print(sum(s['commits'] for s in d['sites']))"

# The excluded repository is still live on GitHub; only its directory listing is suppressed
gh api /repos/buffedlizard55-lab/ProjX/pages
```
