# FLAGGED.md — irregularities and unverified items awaiting review

One line per open item: `repo | field | reason | source link`. Items resolved in a session
move to the Resolved section with the fixing PR/commit. This file supplements (does not
replace) the `IRR-*` register in `VERIFICATION.md`; anything material is also registered there.

## Open

- (none beyond the standing items already tracked in `VERIFICATION.md`: the 4 unreachable
  repos (T-04) and the stale-description queue (T-02)).

## Resolved

- README drift | "Known Limitations" said **35** stale descriptions while the audit table said **38** for the same `2026-10-01T23:59:25Z` snapshot; one of the two was stale prose. Source: `README.md` vs `data/sites.js` `counts.proseStale` (2026-10-01). Being superseded: T-01 rewrites both sections from the fresh snapshot.

## Verification notes (not defects)

- `kanlerxz87-cyber` — 0 public repositories re-confirmed live on 2026-10-11 via
  <https://api.github.com/users/kanlerxz87-cyber> (`public_repos: 0`); census
  <https://api.github.com/users/kanlerxz87-cyber/repos> returns an empty list. Zero Pages sites follow from this; no repo-level Pages check was needed because there are no repos.
