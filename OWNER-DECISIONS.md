# Owner decision records

This file records decisions that cannot be inferred from GitHub's public API. It is deliberately
separate from the generated site snapshot: an API response can establish what is publicly visible,
but it cannot establish why an owner deleted a repository, made it private, or intends to restore it.

## T-004 — four frozen repositories that currently return 404

**Recorded:** 2026-10-11 (UTC)

**Owner decision:** **Pending explicit owner confirmation.** No current official source says whether
these repositories were intentionally retired, made private, or should be restored.

**Directory operational decision:** **Keep all four records frozen and visible in the Unreachable
panel until the owner decides.** This preserves the last sourced values without presenting them as
current public repositories. It is a conservative directory-maintenance choice, not a claim that the
owner chose retirement.

### Current official re-check

At `2026-10-11T15:38:12Z`–`15:38:15Z`, the official repository and Pages endpoints returned HTTP
404 for every repository below. The corresponding public-repository list pages also contained none
of the four exact names; the account profile reported `public_repos: 146`.

| Repository | Repository API | Pages API | Public-list review |
|---|---|---|---|
| `JobSearchSF` | [GET `/repos/.../JobSearchSF`](https://api.github.com/repos/buffedlizard55-lab/JobSearchSF) — HTTP 404 | [GET `/repos/.../JobSearchSF/pages`](https://api.github.com/repos/buffedlizard55-lab/JobSearchSF/pages) — HTTP 404 | [Page 1](https://api.github.com/users/buffedlizard55-lab/repos?type=public&per_page=100&page=1) · [page 2](https://api.github.com/users/buffedlizard55-lab/repos?type=public&per_page=100&page=2) |
| `MALTA` | [GET `/repos/.../MALTA`](https://api.github.com/repos/buffedlizard55-lab/MALTA) — HTTP 404 | [GET `/repos/.../MALTA/pages`](https://api.github.com/repos/buffedlizard55-lab/MALTA/pages) — HTTP 404 | [Page 1](https://api.github.com/users/buffedlizard55-lab/repos?type=public&per_page=100&page=1) · [page 2](https://api.github.com/users/buffedlizard55-lab/repos?type=public&per_page=100&page=2) |
| `MALTA-LAWS` | [GET `/repos/.../MALTA-LAWS`](https://api.github.com/repos/buffedlizard55-lab/MALTA-LAWS) — HTTP 404 | [GET `/repos/.../MALTA-LAWS/pages`](https://api.github.com/repos/buffedlizard55-lab/MALTA-LAWS/pages) — HTTP 404 | [Page 1](https://api.github.com/users/buffedlizard55-lab/repos?type=public&per_page=100&page=1) · [page 2](https://api.github.com/users/buffedlizard55-lab/repos?type=public&per_page=100&page=2) |
| `MALTA2` | [GET `/repos/.../MALTA2`](https://api.github.com/repos/buffedlizard55-lab/MALTA2) — HTTP 404 | [GET `/repos/.../MALTA2/pages`](https://api.github.com/repos/buffedlizard55-lab/MALTA2/pages) — HTTP 404 | [Page 1](https://api.github.com/users/buffedlizard55-lab/repos?type=public&per_page=100&page=1) · [page 2](https://api.github.com/users/buffedlizard55-lab/repos?type=public&per_page=100&page=2) |

The profile total is independently reviewable at [`GET /users/buffedlizard55-lab`](https://api.github.com/users/buffedlizard55-lab).
The four 404 results do **not** distinguish deletion from a visibility change, and a missing Pages
record does not establish whether a replacement site exists elsewhere. No such intent is inferred
here. The historical values remain in [`tools/overlay.json`](tools/overlay.json) and are rendered
into the generated snapshot and directory UI.

### Safe next action for each possible owner decision

1. **Keep frozen** — no data change is needed. The daily census continues to exclude these 404
   records from the live count while retaining them for review.
2. **Restore or make public** — do not manually revive the historical record. Let the next official
   census re-read the repository metadata, Pages settings/status, default-branch commits and
   configured entry point; then regenerate the snapshot from those API responses.
3. **Confirm retirement** — record the owner's confirmation and the date here first. Only then may a
   future maintenance task decide whether historical records should remain in the ledger or be
   archived; they must not be silently deleted from the audit trail.

Until one of those owner decisions is documented, `FL-03` remains open and the four records remain
frozen. This is the only conclusion supported by the current official sources.

## Owner question (2026-10-11) — scope of "all public sites"

**Recorded:** 2026-10-11 (UTC), session `arena-7c23badb`.

The owner brief asks for a complete list of all public GitHub Pages sites. The live census (`GET /users/buffedlizard55-lab/repos?type=public`, then `GET /repos/{owner}/{repo}/pages` per repo) finds 146 public Pages repositories; 145 are listed and one is excluded by the standing owner instruction recorded in AGENTS.md §2. `kanlerxz87-cyber` has 0 public repositories.

**Decision needed:** keep the standing exclusion (no change), or lift it and publish the excluded repository. Until the owner answers, the exclusion stays in force, and the excluded repository's details are intentionally not repeated here.

## T-006 — the GEMS consolidation conflict (IRR-119 / FL-08)

**Recorded:** 2026-10-11 (UTC), session `arena-e36a3025`.

**Owner decision:** **Pending explicit owner confirmation.** Two public repositories owned by the
account publish mutually exclusive instructions about the same competition's repository portfolio:
[`6GEMSDOE`](https://github.com/buffedlizard55-lab/6GEMSDOE) designates itself the single canonical
entry and recommends deleting the other GEMS-named repositories, while
[`GEMSDOE4`](https://github.com/buffedlizard55-lab/GEMSDOE4) records a standing request that *more*
sites be created for more submissions. Which repositories, competition registrations and submissions
to retain is an intent question about the account holder's own plans; GitHub's public API can
verify what is published (below) but cannot settle intent, and MasterSite does not infer it.

**Directory operational decision:** **List every public GEMS-named repository, delete nothing, and
take no position.** The directory publishes each repository's own stated verdict, quotes both
positions verbatim in `VERIFICATION.md` (irregularities `IRR-119` and `IRR-135`) and flags the
conflict (`FL-08`) for the owner. This is a conservative directory-maintenance choice, not an
endorsement of either repository's recommendation — the same no-position rule the T-004 record
applied to the frozen 404 repositories.

### The conflict, quoted from the repositories' own files (re-read at current heads)

Re-read 2026-10-11T18:25:04Z–18:25:51Z, session `arena-e36a3025`. Each row was fetched from the
official Contents API at the repository's **current** default-branch head, not at the SHAs the
original `IRR-119` record cited.

| Source | Current head (read 2026-10-11) | What it says | Hand-review |
|---|---|---|---|
| `6GEMSDOE/ACCOUNT_STATUS.md` | `e2fe3f41c6f5dd2dcb2fc91958ee67698f114ada` (default branch `main`; **unchanged** since 2026-09-26T04:28:31Z — the same head `IRR-119` cites) | Counts **eleven** GEMS-named repositories with Pages built on all eleven; designates `6GEMSDOE` "the single canonical repository and the single published site"; recommends: "Keep `6GEMSDOE` (this repo) as the only entry and the only published site … the account holder can now safely archive or delete the other ten GEMS-named repositories (GEMSDOE, GEMSDOE2, GEMSDOE3, GEMSDOE4, 5GEMSDOE, 7GEMSDOE, 8GEMSDOE, GEMSDOE9, GEMSDOE10, 11GEMSDOE) from the GitHub web UI". Its own "Unknowns" section states: "How many of the eleven repositories are deliberate … Only the account holder can say; this audit reports the state, it does not guess intent." | [Contents API](https://api.github.com/repos/buffedlizard55-lab/6GEMSDOE/contents/ACCOUNT_STATUS.md?ref=e2fe3f41c6f5dd2dcb2fc91958ee67698f114ada) · [blob](https://github.com/buffedlizard55-lab/6GEMSDOE/blob/e2fe3f41c6f5dd2dcb2fc91958ee67698f114ada/ACCOUNT_STATUS.md) |
| `GEMSDOE4/README.md` | `5dc28f67a096c511b0aafbf06c235146c5dcf50e` (head **moved** from the `198a121` stamp `IRR-119` cites; last push 2026-10-05T14:47:36Z) | Charter row #1 still records, as a completed standing request: "Copy the entire repo and site from GEMSDOE (the site that scored 0.1563) into this repo, **because more sites are being created for more submissions**." The multi-site submission plan is therefore still live at the current head, directly contradicting the deletion recommendation above. | [Contents API](https://api.github.com/repos/buffedlizard55-lab/GEMSDOE4/contents/README.md?ref=5dc28f67a096c511b0aafbf06c235146c5dcf50e) · [blob](https://github.com/buffedlizard55-lab/GEMSDOE4/blob/5dc28f67a096c511b0aafbf06c235146c5dcf50e/README.md) |
| `12GEMSDOE/docs/sibling-audit.md` | `33e756015afdaadb29b38d8ac7f6d544dc032f0f` (head **moved** from the `c98d77b` stamp; last push 2026-10-11T11:23:49Z — the repository is actively maintained) | Still documents shared submission artifacts across sibling repositories (generated 2026-09-28): "48 unique published artifacts across 12 repositories", including one identical submission file (same SHA-256, 570,890 bytes) "committed in six places across five repositories". Measured file relationships, not MasterSite claims. | [Contents API](https://api.github.com/repos/buffedlizard55-lab/12GEMSDOE/contents/docs/sibling-audit.md?ref=33e756015afdaadb29b38d8ac7f6d544dc032f0f) · [blob](https://github.com/buffedlizard55-lab/12GEMSDOE/blob/33e756015afdaadb29b38d8ac7f6d544dc032f0f/docs/sibling-audit.md) |

### Current official re-check (2026-10-11T18:25Z)

- Account profile: [`GET /users/buffedlizard55-lab`](https://api.github.com/users/buffedlizard55-lab)
  → `public_repos: 146` (read 2026-10-11T18:25:37Z).
- Public repository list ([page 1](https://api.github.com/users/buffedlizard55-lab/repos?type=public&per_page=100&page=1)
  · [page 2](https://api.github.com/users/buffedlizard55-lab/repos?type=public&per_page=100&page=2))
  → 146 names, of which **63 contain "GEMS" case-insensitively**: the 62 curated members of the
  `gems-prize-lanes` family ([`tools/families.json`](tools/families.json)) plus `62GEMSDOE`, which
  the family file lists under `ungroupedByDesign`. None has been deleted or made private.
- **All ten repositories the `6GEMSDOE` recommendation names for deletion are still public**
  (per-repository endpoint returned HTTP 200 for each at 2026-10-11T18:25:51Z):
  [`GEMSDOE`](https://api.github.com/repos/buffedlizard55-lab/GEMSDOE),
  [`GEMSDOE2`](https://api.github.com/repos/buffedlizard55-lab/GEMSDOE2),
  [`GEMSDOE3`](https://api.github.com/repos/buffedlizard55-lab/GEMSDOE3),
  [`GEMSDOE4`](https://api.github.com/repos/buffedlizard55-lab/GEMSDOE4),
  [`5GEMSDOE`](https://api.github.com/repos/buffedlizard55-lab/5GEMSDOE),
  [`7GEMSDOE`](https://api.github.com/repos/buffedlizard55-lab/7GEMSDOE),
  [`8GEMSDOE`](https://api.github.com/repos/buffedlizard55-lab/8GEMSDOE),
  [`GEMSDOE9`](https://api.github.com/repos/buffedlizard55-lab/GEMSDOE9),
  [`GEMSDOE10`](https://api.github.com/repos/buffedlizard55-lab/GEMSDOE10),
  [`11GEMSDOE`](https://api.github.com/repos/buffedlizard55-lab/11GEMSDOE).
- **The recommendation's own inventory is stale.** `ACCOUNT_STATUS.md` audited **eleven** GEMS
  repositories on 2026-09-26; the account now publishes **63** GEMS-named repositories (33
  GEMSDOE-family lanes were created 2026-10-02–2026-10-08 alone, `IRR-135`). If the owner ever acts
  on the consolidation recommendation, its "delete the other ten" list no longer describes the
  account: the same reasoning would now concern 62 sibling repositories. This is a measured
  observation about the document's census, not a judgment about the plan itself, and is the reason
  `IRR-119`'s title includes "the 6GEMSDOE account census is stale".

### What GitHub's public API can and cannot settle here

Verified above, from the API alone: existence, visibility, creation/push dates, file contents at
exact heads, Pages configuration. **Not verifiable from any GitHub source:** why the repositories
exist, which DrivenData registration (if any) is the official entry, whether any submission was
uploaded, or how many lanes the owner intends to keep. Those live outside GitHub entirely; the
`6GEMSDOE` audit itself lists them as owner-only unknowns. No session can resolve them, and this
record does not try.

### Decision menu and the safe next action for each possible owner decision

1. **Keep all lanes (status quo — the current default).** No data change is needed. The directory
   keeps listing every lane with its own verdict, `FL-08`/`IRR-119`/`IRR-135` stay open, and the
   daily census guard (`tools/census_guard.py`) keeps detecting any growth or removal automatically.
2. **Consolidate per the `6GEMSDOE` recommendation.** Record the confirmation and its date in this
   file **first**, then delete or archive repositories in the GitHub web UI — MasterSite never
   deletes anything on the owner's behalf. The next census will detect the removals through the
   official API; per the audit-trail rule in [`TASKS.md`](TASKS.md), removed records must not be
   silently erased from the ledger — they would join the frozen-unreachable class with a dated
   owner-confirmation note, exactly as T-004 prescribes for the existing 404 records. A refreshed
   `6GEMSDOE/ACCOUNT_STATUS.md` re-audit (its census is stale at 11 of 63) should accompany any such
   pass so the repository's own document matches the account again.
3. **Consolidate around a different lane, or partially.** Same mechanics as option 2: the owner
   records the chosen canonical repository and the lane list here first, then acts in the GitHub UI.
   The directory still takes no position on *which* lane is correct; it only records what exists.
4. **Mixed or other intent** (e.g. some lanes deliberate, some artifacts). Record the split here;
   the census guard and the frozen-record rule handle the rest without any manual list editing.

Until one of those owner decisions is documented here, `FL-08` remains open, `IRR-119` and
`IRR-135` remain in the irregularity register, and all 63 GEMS-named public repositories remain
listed. This is the only conclusion supported by the current official sources.
