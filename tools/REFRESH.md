# Quota-aware full API refresh (T-029)

`refresh.py` coordinates the existing builder and four independent audit tools.
It collects official GitHub REST responses in an **ignored staging directory**;
neither a budget pause nor an API-access block replaces the published snapshot.
It makes no prose edits, live-site requests, or Git operations.

## Run, pause, resume, then publish

From the repository root, with the existing GitHub environment authentication:

```sh
# Initial bounded collection; it does not publish by default.
python3 tools/refresh.py --checkpoint .work/refresh --budget 900 --reserve 60

# Repeat only when the recorded quota/access window permits it.
python3 tools/refresh.py --checkpoint .work/refresh --resume --budget 900 --reserve 60

# Explicitly promote only a completed, eligible collection.
# This can also continue an incomplete collection, subject to the same gates.
python3 tools/refresh.py --checkpoint .work/refresh --resume --publish --budget 900 --reserve 60

# These are offline generators. Do not hand-edit their output.
python3 tools/export_site_records.py
python3 tools/build_sites_md.py
python3 tools/build_master_list.py
python3 tools/build_verification.py
# Sync the README's headline and audit claims with the actual reports, then:
python3 scripts/validate
npm run check
```

Use a new directory, such as `.work/refresh-next`, for a new collection. An
existing checkpoint is never silently discarded. `--checkpoint` must stay under
`.work/`. Do not edit checkpoint fingerprints or timestamps to force a resume.

Exit **2** means incomplete/access-blocked or checkpoint-integrity failure,
**1** means the collection completed with findings, and **0** means the collection
completed without blocking or lint findings. Exit 0 without `--publish` does **not**
mean data was published. Check `publishedAt` and `publicationBlockers` in the report.
A completed description-lint finding can coexist with publication eligibility;
it remains a finding, must stay disclosed, and does not renew any prose stamp.

## What is bounded and saved

- **One hard per-invocation ceiling:** budget minus reserve (default 900 − 60 =
  **840** actual HTTP requests). The quota probe, failed requests, and redirect
  hops count too. Completed phase replays do not spend requests.
- `/rate_limit` is probed before pending work, then response headers can only
  reduce the available quota. The smaller advertised value is used and the
  reserve remains unspent. This is not a global reservation against other users
  of the same token. A real 403 takes precedence over an optimistic quota probe.
- Requests start at least **one second apart**, with one worker. Access errors
  (401/403/429), server errors, and transport failures stop immediately; they
  are never missing-repository or missing-file verdicts. The report preserves an
  API-supplied retry/reset time when available. A budget pause is not an API error.
- Stages run in order: builder → kind → numeric-token lint → provenance → live
  field verifier → final **both-account public census**. Each stage has a separate
  response namespace, so the verifier cannot pass by reading the builder's cache.
  Provenance retains its own ordinary per-process memoization.
- Successful answers and ordinary negative answers (for example a real file 404)
  are compressed and checksummed, with exact logical-request, initial-wire and
  final-response URLs, representation, status, safe quota headers, and the
  **original UTC read time**. Version 2 binds replay to the initial wire request,
  allowing legitimate official renamed-repository redirects while still enforcing
  pinned commit queries. Credentials are passed only in the request header and
  are not written to the checkpoint.
- Commit-list pagination after the first page is pinned to that page's full head
  SHA, including on resume. A moving branch cannot change the later pages of that
  particular history read.
- Input-code and curated-input fingerprints, a per-checkpoint process lock, a
  default **24-hour maximum collection age** (`--max-age` in seconds), cached
  metadata/body consistency, and sealed completed outputs prevent mixed-version,
  corrupt, concurrent, or relabeled collections. Inputs are rechecked before each
  phase and before promotion. A changed/expired collection needs a new checkpoint.

## Review artifacts and publication gates

The checkpoint directory contains `checkpoint.json`, `report.json`, `report.md`,
per-stage `logs/`, compressed `responses/`, and `staged/` outputs. Keep payloads
ignored; preserve the compact summary and relevant audit reports for a PR or
handoff. No resumability is implied after deleting the checkpoint. Scheduled
Actions currently use a different subset runner: **this change does not upload or
restore checkpoints between Actions jobs**.

Incomplete stages, missing entries, final census differences (including any new
public repository on the second account), kind disagreements, live hard
mismatches/set differences, or broken provenance block promotion. Completed
staged files are all checked before replacement; each file is atomically replaced
and the snapshot is replaced last. This is **not** a filesystem-wide transaction
or Git commit. After an interrupted promotion, rerun the same eligible checkpoint
and the offline generators, then validate before committing.

The snapshot and each exported site record retain `apiCollection`; each active
site additionally has exact `apiSources` (`url`, HTTP `status`, original `readAt`).
The exporter refuses malformed/lost source-window evidence before writing records;
legacy snapshots without this new evidence are supported without inventing read
times. The directory legend, `SITES.md`, static master list, and generated ledger
separate snapshot completion from original reads. Each independent audit has its
own window. Replayed responses never become fresh field-by-field verification.

A completed collection remains a sequence of observations, not a simultaneous
snapshot, exhaustive semantic verification, uptime, rendering, visits, or last
use. Prose behind its recorded head stays queued for its claimed owner to reread.
The permanent exclusion and four frozen unreachable records remain unchanged.

## Offline regression gates

```sh
python3 -m unittest tests.test_refresh tests.test_api_evidence -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m py_compile tools/refresh.py tools/build_data.py tools/export_site_records.py
```

Fixtures are synthetic and never production facts. They exercise real staged
builder/audit modules across pauses and cache replay, ceiling/headers/403/429,
independent namespaces, pinned pagination, lock contention, changed/expired inputs,
source timestamps, publication blockers, and all-output integrity before promotion.
