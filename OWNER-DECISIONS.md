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
