# AGENTS.md — MasterSite Maintenance Instructions

Read this before refreshing data or changing the directory. The public directory is a generated snapshot, not a live uptime or usage monitor.

## 1. Scope and current snapshot

- The directory covers public GitHub Pages repositories owned by `buffedlizard55-lab`; `kanlerxz87-cyber` is also queried and currently has no public repositories.
- The latest API snapshot (`2026-10-11T03:01:01Z`, narrative fields re-rendered `04:09:48Z`) contains **145 listed sites** from an account census of **146 public repositories / 146 Pages-enabled repositories**. The single difference is the permanent `ProjX` exclusion below. `kanlerxz87-cyber` has 0 public repositories. Four repositories returned HTTP 404 and remain preserved separately as unreachable records.
- **The account grew from 108 to 146 public repositories between 2026-10-01 and 2026-10-11, and 38 public Pages sites were live with no entry here until this refresh** (`IRR-131`). The generator skips any repository without a curated overlay entry, so the gap was silent. Task `T-010` in [`TASKS.md`](TASKS.md) proposes a scheduled census that fails loudly when `counts.publicRepos` exceeds listed + excluded. **Treat "the directory is complete" as a claim to re-verify every pass, not an assumption.**
- `kind: "app"` and `kind: "stub"` are legacy schema values. They mean only that the configured Pages source path does or does not contain `index.html`. They do **not** mean interactive/noninteractive, working/broken, or online/offline. The latest audit re-derived all 145 kinds: **135 apps, 10 stubs, 0 disagreements, 0 unresolved**.
- `pagesStatus: "built"` is GitHub API metadata, not a successful HTTP or browser check. At the latest snapshot **144 entries report `built` and one (`GEMSDOE53`) reports `errored`** (`IRR-132`). GitHub's public repository and Pages APIs do not expose site visits or last use; the UI's **Last commit** is the newest committer timestamp on the default branch.
- **40** description SHAs are behind their repositories' current heads (down from 47 after six were re-read, then 41 → 40 after `MALTASUPPLEMENTAL` was re-read to close `FL-12`). These entries must remain visibly flagged until their source prose is re-read; a changed SHA alone does not prove a description false. The latest prose pass read 46 entries: 38 new ones at `2026-10-11T02:54:23Z`, one re-read at `2026-10-11T03:01:21Z`, six re-reads at `2026-10-11T03:54:54Z`, and one re-read at `2026-10-11T04:09:42Z`.
- The independent live verifier completed **1,901 checks**: 0 hard mismatches and 3 volatile drifts (`59GEMSDOE.pushedAt`, `61GEMSDOE.sizeKb`, `KalshiPaperSim.sizeKb` — fields GitHub recomputes asynchronously). The numeric-token description lint checked all 145 entries with **0 unresolved items** and 42 documented exceptions; this is not semantic proof. The one open finding (`230` in `MALTASUPPLEMENTAL`, `FL-12`) was closed by re-reading the entry at the snapshot head and withdrawing the unsupported token.
- **A re-derivation caught six entries published as stubs after they had already become HTML entry points** (`GEMSDOE22`–`GEMSDOE27`, `IRR-138`): `contents/index.html?ref=<snapshot head>` returns HTTP 200 for all six at the recorded snapshot heads, so the stored label was false when published. Re-derive `kind` every pass — never trust a stored value. See `IRR-127`–`IRR-138` in `VERIFICATION.md`.
- **Protocol files exist and are binding.** [`TASKS.md`](TASKS.md) holds the claimable queue (claim one task per session, commit the claim alone, push immediately); [`FLAGGED.md`](FLAGGED.md) records fields that cannot be verified officially and items needing a human decision; [`HANDOFF.md`](HANDOFF.md) carries session context; `scripts/validate` is the mechanical gate (official source links per record, no unverified values, overlay-vs-published parity, counts, exclusions, and the per-record hand-review links in `VERIFICATION.md`). Run it before opening a PR.
- Local `npm run check` and Python syntax compilation pass. Playwright discovered 84 browser cases, but none ran: browser installation failed with `ECONNRESET` from `cdn.playwright.dev`. The PR workflow installs browsers; see README for the exact limitation. The `MasterSite` public-page fetch also hit sandbox TLS/SSL EOF, which does not prove the public site is down.

## 2. Hard repository rules

### Permanent exclusion

`ProjX` is publicly available upstream but is **permanently excluded from MasterSite by owner instruction**. Never add its title, repository URL, API URL, Pages URL, description, or metadata to the overlay, generated data, ledger, README counts, or exports. Keep API account totals unchanged and apply the exclusion after reading the official account API. The generator asserts that listed plus excluded Pages repositories balance to the account's Pages count.

### Unreachable repositories

`JobSearchSF`, `MALTA`, `MALTA-LAWS`, and `MALTA2` returned HTTP 404 in the latest live audit. Keep them in the frozen `unreachable` section of `data/sites.js`, `VERIFICATION.md`, and the UI's Unreachable panel with their last verified values. Do not silently delete them or infer whether they were intentionally retired; only the owner can resolve that. Recheck their official endpoints during a refresh.

## 3. Source and claim policy

- Use GitHub's official REST API for account/repository metadata, Pages settings/status, configured publish path, and default-branch commits. `verify_live.py` is the independent snapshot check.
- Curated titles, categories, descriptions, and flags belong in `tools/overlay.json`. Base every factual phrase on repository-owned README/source files, preferably at the current default-branch head. Record the exact source path, full commit SHA, and reproducible official endpoint in `verifiedBasis`.
- Keep summaries brief and conservative. Do not infer behavior from a repository name, badge, topic, or a root `index.html`; do not convert a claim in project prose into an independently established result. If repository files conflict, retain the caveat and add a reproducible irregularity rather than smoothing it over.
- A `verifiedAtSha` value must be a 7–40 character lowercase commit SHA. The generator accepts full SHAs and compares them with the current head (including supported short-prefix stamps). Before carrying a short stamp, verify the referenced commit resolves and explain why the intervening changes do not affect the description. A matching SHA is provenance, not proof that each sentence is correct.
- When a description is re-read, update `description`, `lastVerified`, `verifiedBasis`, and `verifiedAtSha` together. Entries touched in one pass should share a pass-completion timestamp. If source content changes materially, log the correction in `descriptionNotes` and add an `IRR` record when useful for future review.
- Never claim “zero hallucinations,” exhaustive verification, site uptime, interactivity, or last site use. Say what the source supports and disclose what was not tested.

## 4. Data and audit workflow

Run from the repository root:

```bash
python3 tools/build_data.py
python3 tools/verify_live.py
python3 tools/audit_kind.py
rm -rf tools/.readme-cache
python3 tools/audit_descriptions.py
npm run check
python3 -m py_compile tools/build_data.py tools/build_verification.py \
  tools/audit_descriptions.py tools/audit_kind.py tools/verify_live.py
npm test
python3 tools/build_verification.py
```

Run `build_verification.py` **after** the audit commands so the generated ledger cites reports for the same snapshot. Its audit-status table distinguishes completed, stale, incomplete, authorization-blocked, and rate-limit-blocked reports. Re-read any `PROSE-STALE` entry whose description will be presented as current; never clear the queue by changing only its SHA. If a repository moves during the pass, refresh and rerun the independent checks. `verify_live.py` mismatches are not repaired by hand in generated data—refresh the generator and recheck. HTTP 401 is an authorization failure, not a repository mismatch or a missing README; reconnect GitHub and rerun. HTTP 403 whose body identifies an API rate limit is an access block, not 403 field drift; rerun after the documented reset rather than treating it as a data mismatch.

- `tools/verify_live.py` is read-only and compares API fields to the generated snapshot.
- `tools/audit_kind.py` is read-only. HTTP 200 at the configured `index.html` path means HTML entry point; HTTP 404 means no entry point. Other status codes are unresolved, **not** stubs, and the audit must fail so an API problem cannot silently change a classification.
- `tools/audit_descriptions.py` is read-only. It checks whether numeric tokens in each description occur in that repository's README at the snapshot head. This is only a lint: it cannot establish what a number means or validate non-numeric claims. Any exceptions must be individually justified in `acceptedDescriptionExceptions`; do not add exceptions just to silence a finding.
- `audit_descriptions.py` caches fetched READMEs in `tools/.readme-cache`; clear that directory before relying on fresh source content.
- The generated `data/sites.js` and `VERIFICATION.md` must not be hand-edited. Edit the overlay and rerun their generators.

If GitHub API access is unavailable, `python3 tools/build_data.py --overlay-only` can render curated narrative fields into the existing snapshot without network access. It cannot add repositories or refresh API fields, and it cannot see commits since the snapshot. Do not present an overlay-only render as a fresh API audit or publish it as a replacement for a full build.

## 5. Documentation and test expectations

- Update the **current** README snapshot counts, audit results, unresolved queue, and limitations after a final refresh. Historical pass notes should be clearly dated and kept separate from current claims.
- Regenerate `VERIFICATION.md`; it contains the per-entry dates, SHAs, live/repository/API/settings links, exclusions, unreachable records, and irregularity register.
- Run `npm run check` and the Playwright suite when browser binaries are available. `.github/workflows/test.yml` installs Chromium, Firefox, and WebKit and runs the suite on pull requests. A sandbox browser-download failure is a blocked test, not a pass; report it accurately.
- The deployed app is static (`index.html`, CSS, JavaScript, and `data/sites.js`). Do not hardcode repository lists in UI markup/scripts.
- Preserve the table DOM contract asserted by `tests/directory.spec.js`: fixed cell count/order, row repository slug, Pages status position, and matching empty-state colspan. Responsive layout should remain CSS-driven.
- Density is a local reading preference, not a filter or URL parameter. Keep URL state limited to the documented search/category/type/prose/sort/view fields, and keep JSON/CSV output independent of density.

For the latest counts, status, source limits, and remaining review work, see [`README.md`](README.md).
