# T-029: completed real resumable API collection

**Result: BLOCKED_FINDINGS — no new snapshot published.**

Collection began `2026-10-12T02:31:05Z` and finished `2026-10-12T04:11:23Z` (UTC).

All six stages completed across bounded invocations and actual live-quota reset windows. The final both-account census is recorded below, independently of the initial builder census.

| Stage | Verdict | Actual HTTP requests | Original API read window (UTC) |
|---|---|---|---|
| `build_data` | **PASS** | 544 | `2026-10-12T02:31:06Z` → `2026-10-12T02:57:48Z` |
| `audit_kind` | **FINDINGS** | 310 | `2026-10-12T02:57:49Z` → `2026-10-12T03:02:58Z` |
| `audit_descriptions` | **FINDINGS** | 155 | `2026-10-12T03:02:59Z` → `2026-10-12T03:05:33Z` |
| `audit_provenance` | **PASS** | 1055 | `2026-10-12T03:05:34Z` → `2026-10-12T03:56:55Z` |
| `verify_live` | **PASS** | 862 | `2026-10-12T03:56:56Z` → `2026-10-12T04:11:18Z` |
| `coverage` | **PASS** | 5 | `2026-10-12T04:11:19Z` → `2026-10-12T04:11:23Z` |

## Completed audit results

- **Kind:** 155/155, two disagreements (`GEMSDOE67`, `GEMSDOE69`: curated `stub` versus an observed HTML entry point).
- **Numeric-token lint:** 155/155, one unresolved entry (`60GEMSDOE`), 42 documented exceptions. This is not semantic verification.
- **Provenance:** 155/155, 1,118 reproduced checks, zero hard findings. Five `{path}` citation templates remain disclosed (FL-18).
- **Live fields:** 2,049 checks, zero hard mismatches, 80 disclosed volatile drifts; no API/list set differences.
- **Actual HTTP requests:** 2,938 across seven invocations (7, 7, 438, 840, 692, 840, 114). This includes seven quota probes and one official rename redirect hop. The two live-reserve pauses waited for recorded resets at `02:55:20Z` and `03:55:22Z`; the two 840-request ceilings resumed without losing work.

## Publication was withheld

- audit_kind: kind disagreements require source review

Description lint is a separate source-review finding, not semantic verification:
- `60GEMSDOE`: numeric tokens not found in README — `0.00420`, `0.08623`.

The published snapshot remains `2026-10-12T00:11:29Z`. All 162 published data/export/audit/ledger hashes still match main `58e06ea`; no curated descriptions, exclusion, or frozen records were changed.

## Final public census

- `buffedlizard55-lab`: **156** public repositories. Official enumeration: <https://api.github.com/users/buffedlizard55-lab/repos?type=public>.
- `kanlerxz87-cyber`: **0** public repositories. Official enumeration: <https://api.github.com/users/kanlerxz87-cyber/repos?type=public>.
- Final coverage gaps: `[]`.

## Reproducible evidence and limits

- The [companion JSON](20261012T041123Z-v2-full-collection.json) records complete audit counts/findings/drifts, bounded attempts, code/curation fingerprints, original source URLs/times/statuses, final census names, staged-output checksums and unchanged publication hashes. The static master list changed only the original-read tooltip wording in the implementation; its dataset was not refreshed.
- Compressed raw responses and working files remain ignored in `.work/refresh-v2`; the preserved summary does not promise that another checkout has those local files.
- A legitimate official renamed-repository redirect replayed without spending requests or changing its original read time (separate `20261012T023224Z-v2-official-redirect-replay.json`).
- Historical version-1 collection artifacts remain explicitly incomplete. They were not relabeled or transplanted into version 2.
- Source-prose/classification work belongs to T-002. Review FL-21 before a new collection; changing curation invalidates this checkpoint on purpose.
- Pages build metadata and HTML-file existence do not establish uptime, browser functionality, visits, last use, or current semantic correctness. Volatile drift is disclosed, not silently made current.

A completed collection is a sequence of timestamped public API reads, not a simultaneous snapshot. Checkpoint replay retains the original read time. These checks do not establish semantic correctness, live-site uptime, browser functionality, visits, or last use.

## Later integration (not part of this collection)

PR #73/T-035 reached main while T-029 was finalizing. Rebase preserved its
`02:09:11Z` published dataset and source rereads, not this blocked staged dataset.
The unchanged hashes above are an **as-of-run comparison with main `58e06ea`**.
T-035 resolved the old-input kind mismatches; those are now historical FL-23
(formerly FL-21 on the unmerged T-029 branch). Main's FL-21 is GEMSDOE68 build
metadata; T-029 FL-22 was consolidated into it with the recorded recovery.
Changed inputs intentionally prevent resuming this checkpoint. Original API
read times, findings and BLOCKED_FINDINGS remain historical evidence, not new
verdicts against the revised curation.
