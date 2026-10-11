# Scheduled audit layer — preserved measurements and reports (`T-022`)

This directory holds the evidence behind [`tools/scheduled_audit.py`](../../tools/scheduled_audit.py)
and [`.github/workflows/audit-schedule.yml`](../../.github/workflows/audit-schedule.yml): the measured
cost of each read-only audit, which is what makes the schedule honest about what it can and cannot cover.

## Why cost measurement is load-bearing

GitHub documents that the built-in Actions `GITHUB_TOKEN` is limited to **1,000 requests per hour per
repository** — "Primary rate limit for `GITHUB_TOKEN` in GitHub Actions",
<https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api> (fetched 2026-10-11).

A scheduled job that simply ran `verify_live.py`, `audit_kind.py`, `audit_descriptions.py` and
`audit_provenance.py` back to back would therefore abort mid-pass on HTTP 403 — the failure this
repository already recorded twice on 2026-10-11 (`IRR-139`, `IRR-140`). The measurements below are the
reason the runner plans a subset per weekday, holds a hard ceiling, and reports `NOT-RUN`/`PARTIAL`
instead of publishing a truncated pass as complete.

## Files

| File | What it is |
|---|---|
| [`2026-10-11T1735Z-measured-costs.md`](2026-10-11T1735Z-measured-costs.md) | Per-audit request counts, wall-clock and endpoint mix, measured by counting every HTTP request each tool made |
| [`raw/measure_costs.json`](raw/measure_costs.json) | Machine-readable summary of the same measurement |
| `raw/count-<tool>.json` | One URL per request, per tool (the raw evidence behind every number above) |
| [`raw/measure_costs.py`](raw/measure_costs.py) / [`raw/counting_shim/sitecustomize.py`](raw/counting_shim/sitecustomize.py) | The harness and the counting shim, so the measurement can be repeated (run it from a scratch clone) |

## Method (reproducible)

Each tool was run from a scratch copy of the repository with a `sitecustomize.py` on `PYTHONPATH` that
wraps `urllib.request.urlopen` and dumps every requested URL at process exit; wall-clock was measured
around each run. Nothing was written to the real checkout, and no published value was changed.

```
mkdir -p /tmp/measure/shim && git clone . /tmp/measure/repo \
  && cp reports/scheduled-audit/raw/counting_shim/sitecustomize.py /tmp/measure/shim/ \
  && cp reports/scheduled-audit/raw/measure_costs.py /tmp/measure/
GITHUB_TOKEN=... python3 /tmp/measure/measure_costs.py /tmp/measure
```

Run it from a scratch clone, never the real checkout: the audits rewrite their own `tools/last_*.json`
reports when they finish.

A `GET /rate_limit` delta was attempted first and **abandoned**: from this environment that endpoint
reported `remaining 5000 / used 0` even after confirmed HTTP 200 requests, which matches GitHub's own
note that counters vary between regions and that the response headers are the authoritative source.
Counting requests client-side is not affected by that.

## Caveats

- Counts are a **point-in-time** measurement (2026-10-11, 145 listed sites). They grow with the number
  of listed repositories and with repository commit counts (`verify_live.py` paginates every
  repository's commit list), so re-measure after a census refresh. The runner's `report.json` records
  the planned cost, the verdict and the exit code of every audit it attempted, but it does **not**
  meter the requests it actually spent — GitHub's remaining-quota reading is not trustworthy from that
  environment (see Method), which is why the budget is planned from these fixed, measured constants.
- The measurement ran **cold**: the scratch clone had no `tools/.readme-cache` (that directory is
  git-ignored, so a scheduled checkout is equally cold). Inside a single run the tools share that
  cache, so the counts already reflect whatever a later tool re-read from disk instead of the API.
- The sandbox token used for the measurement has a 5,000 requests/hour limit; the **Actions**
  `GITHUB_TOKEN` that runs the schedule is limited to 1,000/hour/repository. The measurement is about
  *cost*, not about which token pays it.
- A cost measurement says nothing about correctness: it is a count of requests, not a verification result.
