# MasterSite — Verification Ledger

**Audit date:** 2026-09-12 (UTC) · **Auditor:** automated agent session, no manual input from the user
**Scope:** every GitHub Pages site under `buffedlizard55-lab` (and a check of the second account `kanlerxz87-cyber`)

Every fact in `data/sites.js` and `index.html` was read from the official GitHub REST API or by opening the live site directly. Nothing is remembered, estimated, or inferred. Where something could not be established, it is flagged instead of filled in.

---

## 1. Account verification

| Check | Official source | Result |
|---|---|---|
| Account exists | [github.com/buffedlizard55-lab](https://github.com/buffedlizard55-lab) · [API: users/buffedlizard55-lab](https://api.github.com/users/buffedlizard55-lab) | ✅ type `User`, created `2026-07-27T01:05:09Z`, `public_repos: 33` |
| Account exists | [github.com/kanlerxz87-cyber](https://github.com/kanlerxz87-cyber) · [API: users/kanlerxz87-cyber](https://api.github.com/users/kanlerxz87-cyber) | ✅ type `User`, created `2026-08-03T20:56:16Z`, **`public_repos: 0`** → nothing to list |

## 2. Repository enumeration

Method: `GET https://api.github.com/users/buffedlizard55-lab/repos` (paginated). Returned exactly **33 repositories**, all with `has_pages: true`, none forks. `GET /users/kanlerxz87-cyber/repos` returned **0**.

## 3. Pages configuration (per repo)

Method: `GET https://api.github.com/repos/buffedlizard55-lab/{repo}/pages`

| Result | Count | Repos |
|---|---|---|
| `status: built`, source `main /` | 32 | all except GOLD |
| `status: built`, source `main /docs` | 1 | GOLD |
| `status: building` (transient) | 1 observed | DrugAnalysis at first check (~00:21 UTC), `built` on re-check — consistent with its push at 00:20:34Z |
| Custom domains (CNAME) | 0 | all `cname: null` |

**Note:** `GET /repos/{owner}/{repo}/pages/deployments` returns 404 for all 33 repos. Expected: these are legacy “deploy from a branch” sites; deployment records exist only for Actions-based deployments.

## 4. Live-site reads (all 33 URLs opened and read directly)

| # | Site | Read result |
|---|---|---|
| 1 | https://buffedlizard55-lab.github.io/AirPremia/ | ✅ full app — refund playbook content |
| 2 | https://buffedlizard55-lab.github.io/BathTubOverflowSF/ | ✅ full app — decision brief + 301-record directory |
| 3 | https://buffedlizard55-lab.github.io/BusanL7HaeundaeLotteHotelStay/ | ✅ full app — itineraries & trip builder |
| 4 | https://buffedlizard55-lab.github.io/CruiseDeals/ | ✅ full app (root redirects to /docs/) — sailings table |
| 5 | https://buffedlizard55-lab.github.io/DrugAnalysis/ | ✅ full app — FDA decisions table |
| 6 | https://buffedlizard55-lab.github.io/GOLD/ | ✅ full app — ring directory (from /docs) |
| 7 | https://buffedlizard55-lab.github.io/HongdaeStay/ | ✅ full app — itineraries |
| 8 | https://buffedlizard55-lab.github.io/HotelSeoulRoughdraft1/ | ✅ full app — Korea Compass (draft) |
| 9 | https://buffedlizard55-lab.github.io/Insider-trades/ | ✅ full app — dashboard (empty-until-collected by design) |
| 10 | https://buffedlizard55-lab.github.io/Itinerary-Korea/ | ✅ full app — Korea Compass |
| 11 | https://buffedlizard55-lab.github.io/JobSearchSF/ | ✅ full app — 120-job table |
| 12 | https://buffedlizard55-lab.github.io/Korea/ | ✅ full app — deal registry |
| 13 | https://buffedlizard55-lab.github.io/Korea-emergency/ | ✅ full app — emergency guide |
| 14 | https://buffedlizard55-lab.github.io/KoreaHotels/ | ✅ full app — hotel tables |
| 15 | https://buffedlizard55-lab.github.io/Leg3SeoulTrip/ | ⚠️ README stub only (repo has only a README) |
| 16 | https://buffedlizard55-lab.github.io/MasterSite/ | ⚠️ README stub at audit time (this site now replaces it) |
| 17 | https://buffedlizard55-lab.github.io/MLB-Live-PBP/ | ✅ full app — live scoreboard rendering live games |
| 18 | https://buffedlizard55-lab.github.io/MLB-PBP/ | ✅ full app — game finder (root redirects to /docs/) |
| 19 | https://buffedlizard55-lab.github.io/MLB-Prediction-model-backtest/ | ⚠️ rendered README (code/research repo) |
| 20 | https://buffedlizard55-lab.github.io/Ncaa-football-alerts/ | ✅ full app — live scoreboard + alert booth |
| 21 | https://buffedlizard55-lab.github.io/NFL-scoreboard/ | ✅ full app — scoreboard |
| 22 | https://buffedlizard55-lab.github.io/NFLInjuryReport/ | ✅ full app — injury tables, all 32 clubs |
| 23 | https://buffedlizard55-lab.github.io/NFLPRED/ | ⚠️ README stub only |
| 24 | https://buffedlizard55-lab.github.io/PFFNFL/ | ⚠️ rendered README (code/research repo) |
| 25 | https://buffedlizard55-lab.github.io/PlumbingSF/ | ✅ full app (root redirects to /docs/) — plumber directory |
| 26 | https://buffedlizard55-lab.github.io/PriceKalshiHistorical/ | ✅ browser exchange build (root redirects to /docs/); collector is server-side |
| 27 | https://buffedlizard55-lab.github.io/ProjX/ | ✅ full app — verified directory |
| 28 | https://buffedlizard55-lab.github.io/ScheduleFreeTime/ | ✅ full app — free-time calendar |
| 29 | https://buffedlizard55-lab.github.io/SFLateNight/ | ✅ full app — venue directory |
| 30 | https://buffedlizard55-lab.github.io/SportsPred/ | ✅ full app — multi-sport hub |
| 31 | https://buffedlizard55-lab.github.io/StanfordStay/ | ✅ full app — Seoul itineraries |
| 32 | https://buffedlizard55-lab.github.io/TinoLunchSpecial/ | ✅ full app — lunch deals + transit plan |
| 33 | https://buffedlizard55-lab.github.io/Tradingview-pinescript-editor/ | ✅ full app — PinePilot |

## 5. Dates & commit facts

Method: `GET /repos/{owner}/{repo}` (created_at, pushed_at, updated_at) and `GET /repos/{owner}/{repo}/commits` (counts, first/last commit dates + SHAs).

- For **all 33 repositories**, the first commit's committer date is within **one second** of the repository `created_at` timestamp.
- `lastCommit` in the data file = newest commit on `main`; `pushedAt` = last push to any branch (GitHub can report a later pushed_at when a non-default branch was pushed afterwards — see IRR-10 for TinoLunchSpecial).
- Commit counts per repo range from 1 (Leg3SeoulTrip, NFLPRED, MasterSite at audit time) to 189 (SportsPred).

## 6. Descriptions

Every site description was derived from (a) the repository README read via `GET /repos/{owner}/{repo}/readme` and/or (b) the content read directly from the live site — see table above. No description was written from memory.

## 7. Irregularity register

The canonical, machine-readable list is `MASTERDATA.irregularities` in [`data/sites.js`](data/sites.js) (IRR-01 … IRR-11) and is rendered on the site's “Flagged irregularities” panel. Highlights:

- **IRR-01** — `kanlerxz87-cyber` has 0 public repos ⇒ 0 Pages sites.
- **IRR-02** — `Leg3SeoulTrip`, `NFLPRED` are README-only placeholders.
- **IRR-03** — `MLB-Prediction-model-backtest`, `PFFNFL` serve rendered READMEs (research repos).
- **IRR-05** — `DrugAnalysis` observed mid-build, then built.
- **IRR-06** — `GOLD` publishes from `/docs`; all others from `/`.
- **IRR-07** — `HotelSeoulRoughdraft1` duplicates `Itinerary-Korea` (draft).
- **IRR-08** — `StanfordStay` is Seoul content despite the name.
- **IRR-10** — `TinoLunchSpecial` pushed_at post-dates newest main commit (non-default branch push).
- **IRR-11** — No Pages deployment records (legacy branch builds).

## 8. Environment note

Direct outbound TCP from the audit sandbox to GitHub Pages IPs was blocked (TLS reset), so live-site reads were performed through the platform's page-fetch facility and the GitHub API rather than raw `curl`; both reach the same public endpoints. This is a sandbox limitation, not a site problem — every URL above is reproducible from any normal browser.
