#!/usr/bin/env python3
"""Budgeted scheduled re-run of MasterSite's read-only audits (T-022).

Why this exists
---------------
`tools/census_guard.py` answers one question on a schedule — *is every public
repository listed?* (`T-010`). Nothing re-ran the four accuracy audits on a
schedule, so the audit layer could go stale, or stay access-blocked, without
anything saying so: the `2026-10-11T15:06:10Z` snapshot shipped with
`verify_live.py` and `audit_descriptions.py` INCOMPLETE (an HTTP 403 access
block) and that was only visible because a session wrote it into `HANDOFF.md`.

What it does
------------
Runs `tools/audit_kind.py`, `tools/audit_descriptions.py`, `tools/verify_live.py`
and `tools/audit_provenance.py` **against the published snapshot in this
checkout** (all four are read-only tools and never write `data/sites.js`), then
reports one verdict per audit with the official endpoint a reviewer can open by
hand.

Writes only into `--output-dir` (`.work/scheduled-audit/` by default: `report.md`,
`report.json`, `logs/<audit>.log`). It never edits a published file, but each
audit tool rewrites its own tracked `tools/last_*.json` report as it finishes —
in the workflow's throwaway checkout that is discarded, while a *local* run
leaves those files dirty; revert them unless you mean to publish that run.

Why it is budgeted rather than brute force
------------------------------------------
GitHub documents that the built-in `GITHUB_TOKEN` in Actions is limited to
**1,000 requests per hour per repository** ("Primary rate limit for
`GITHUB_TOKEN` in GitHub Actions",
<https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api>),
and one full pass of all four audits costs more than that (measured: see
`reports/scheduled-audit/`). A scheduled job that simply ran all four would
abort mid-pass on HTTP 403 — the failure this repository already recorded twice
(`IRR-139`, `IRR-140`). So the runner:

  * reads `GET /rate_limit` first (GitHub documents that calling it does **not**
    count against the primary rate limit) and also reads the authoritative
    `x-ratelimit-*` response headers;
  * holds a hard per-run ceiling (`--budget`, default 900) and a reserve
    (`--reserve`, default 60) it never plans to spend, so the workflow's own
    API calls and GitHub's documented region-to-region variation in reported
    counters cannot push the run over the edge;
  * covers a **scheduled subset per weekday** (`SLOT_PLAN`, overridable with
    `--audits`), so the whole suite is re-run across the week instead of dying
    inside one hour, and a run that cannot even finish its scheduled subset is
    reported as `PARTIAL` rather than quietly truncated.

Verdicts (per audit)
--------------------
  PASS       the tool exited 0, reported a complete run, and reported no finding
  FINDINGS   the tool completed and reported something for review
             (mismatch / disagreement / unresolved numeric token / citation)
  INCOMPLETE the tool could not finish — access block, API error, or a report
             that says `complete: false`. Never a pass.
  ERROR      the tool crashed, or wrote no fresh report for this run
  NOT-RUN    deliberately skipped: the budget did not cover it

Every audit the run was asked about appears in the report exactly once, whether it ran or was
skipped for budget; if the runner cannot account for one of them it fails closed instead of
publishing a report with a hole.

Outcomes for the run as a whole (the report carries the detail):
  CLEAN       every audit *scheduled for this run* ran, complete and clean
  FINDINGS    at least one audit completed with findings
  INCOMPLETE  at least one audit is incomplete / blocked / errored
  PARTIAL     no findings or blocks, but the run could not cover its own
              scheduled audits within the budget — reported, never hidden

Exit codes: 0 CLEAN · 1 FINDINGS · 2 INCOMPLETE · 3 PARTIAL.

A `CLEAN` outcome says "the audits scheduled for this run came back clean"; it
does not say the other audits ran. The report always prints exactly which
audits this run covered.

Usage
-----
    python3 tools/scheduled_audit.py --plan-only        # plan; spend nothing
    python3 tools/scheduled_audit.py                    # today's scheduled subset
    python3 tools/scheduled_audit.py --slot sunday      # the full-suite attempt
    python3 tools/scheduled_audit.py --audits verify_live
    python3 tools/scheduled_audit.py --self-test        # offline checks

Everything it writes goes to `--output-dir` (default `.work/scheduled-audit`,
git-ignored) plus the JSON reports the audit tools themselves write (their
normal output). It never edits `data/sites.js`, `VERIFICATION.md` or any
published record: publishing is a session's job, and a scheduled run must not
become a silent publisher.
"""

import argparse
import datetime
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import quote, urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.github.com"
OWNER = "buffedlizard55-lab"
DATA = os.path.join(ROOT, "data", "sites.js")

# Verdicts
PASS, FINDINGS, INCOMPLETE, ERROR, NOT_RUN = "PASS", "FINDINGS", "INCOMPLETE", "ERROR", "NOT-RUN"
# Outcomes
CLEAN, OUT_PARTIAL = "CLEAN", "PARTIAL"

# Exit codes
EXIT_CLEAN, EXIT_FINDINGS, EXIT_INCOMPLETE, EXIT_PARTIAL = 0, 1, 2, 3

# Per-run ceiling and unspent reserve. GitHub documents the built-in Actions
# `GITHUB_TOKEN` at 1,000 requests/hour/repository, so the run plans to spend at
# most 900 and holds back 60 for the workflow's own API calls (issue list,
# label, issue edit / PR comment) and for the documented region-to-region
# variation in reported counters. Spendable = 900 − 60 = 840: that is what lets
# a measured 812-request `verify_live` slot fit its own hour, and it is the most
# any plan can reach (the measured plans are 435 for kind+descriptions and 812
# for verify_live), so audits + the ≤60 workflow tail stay inside 1,000/hour.
DEFAULT_BUDGET = 900
DEFAULT_RESERVE = 60

# Expected request cost per audit, used for planning only. Measured on
# 2026-10-11 by counting every request each tool issues against the official API
# in a scratch checkout (see reports/scheduled-audit/ for the raw counts and the
# method): the numbers are counts, not estimates, and they grow with the number
# of listed repositories, so a refresh should re-measure them.
DEFAULT_COSTS = {
    "audit_kind": 290,          # 145 repositories x (Pages + configured-path index.html)
    "audit_descriptions": 145,  # one README read per entry
    "verify_live": 812,         # measured: 294 repository + 291 Pages + 220 paginated
                                # commit-list + 7 account reads (0 per_page=1 re-reads)
    "audit_provenance": 1000,   # measured 904 (382 commit-by-SHA, 270 contents, 118 Pages,
                                # 46 readme, 43 repository, 40 commit-list, 3 compare,
                                # 1 repository-by-id, 1 actions/runs) from a cold scratch
                                # checkout; plan 1,000 to leave headroom, since the count
                                # grows with the census and with cited endpoints
}

AUDIT_ORDER = ["audit_kind", "audit_descriptions", "verify_live", "audit_provenance"]

# Weekday cover plan (0 = Monday). Cheapest and broadest first; every audit runs
# at least twice a week; Sunday attempts the full suite (2,151 requests measured),
# which cannot fit the built-in 1,000/hour however it is planned, so its report
# names what it did not cover instead of pretending it ran.
SLOT_PLAN = {
    0: ["audit_kind", "audit_descriptions"],   # Monday
    1: ["verify_live"],                        # Tuesday
    2: ["audit_provenance"],                   # Wednesday
    3: ["audit_kind", "audit_descriptions"],   # Thursday
    4: ["verify_live"],                        # Friday
    5: ["audit_provenance"],                   # Saturday
    6: list(AUDIT_ORDER),                      # Sunday — full-suite attempt
}
SLOT_NAMES = {0: "monday", 1: "tuesday", 2: "wednesday", 3: "thursday",
              4: "friday", 5: "saturday", 6: "sunday"}

AUDITS = {
    "audit_kind": {
        "script": ["tools/audit_kind.py"],
        "report": "tools/last_kind_audit.json",
        "what": "re-derives `app` vs `stub` from each repository's configured Pages path",
        "review": "https://api.github.com/repos/buffedlizard55-lab/{repo}/pages",
    },
    "audit_descriptions": {
        "script": ["tools/audit_descriptions.py"],
        "report": "tools/last_description_audit.json",
        "what": "numeric-token lint of every curated description against the README at the recorded stamp",
        "review": "https://api.github.com/repos/buffedlizard55-lab/{repo}/readme",
    },
    "verify_live": {
        "script": ["tools/verify_live.py"],
        "report": "tools/last_live_verify.json",
        "what": "line-by-line re-read of every API-derived field in the published snapshot",
        "review": "https://api.github.com/repos/buffedlizard55-lab/{repo}",
    },
    "audit_provenance": {
        "script": ["tools/audit_provenance.py"],
        "report": "tools/last_provenance_audit.json",
        "what": "re-opens every cited endpoint and re-resolves every recorded commit SHA",
        "review": "https://api.github.com/repos/buffedlizard55-lab/MasterSite/commits/main",
    },
}

REMEDY = ("The Actions `GITHUB_TOKEN` is capped at 1,000 requests/hour/repository and this run's "
          "`--budget` caps it further (900 − 60 reserve = 840 spendable). A full suite measured "
          "2,151 requests and `audit_provenance` alone measured 904, so covering them needs both a "
          "higher `--budget` (≥ 964 for `audit_provenance` at the default reserve) and a token with "
          "room to pay for it — an owner-provided fine-grained token (5,000/hour) exposed to this "
          "workflow as a secret.")

CAVEAT = (
    "These are mechanical re-reads of official endpoints against the published snapshot. They do "
    "not prove that a description is accurate or current, and they make no uptime, rendering, "
    "visit or usage claim."
)


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def token():
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def snapshot_generated():
    """The snapshot `data/sites.js` says it was generated from."""
    try:
        with open(DATA, encoding="utf-8") as fh:
            src = fh.read()
        return json.loads(src.split("window.MASTERDATA = ", 1)[1].rstrip().rstrip(";")).get("generated")
    except Exception:
        return None


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def api_get(path):
    """Return (status, body, headers). The caller decides what a status means."""
    req = urllib.request.Request(
        API + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "MasterSite-scheduled-audit",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    tok = token()
    if tok:
        req.add_header("Authorization", "Bearer " + tok)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8")), dict(resp.headers)
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read().decode("utf-8"))
        except Exception:
            body = {"message": getattr(exc, "reason", "")}
        return exc.code, body, dict(getattr(exc, "headers", {}) or {})
    except Exception as exc:  # transport: no status at all
        return 0, {"message": str(exc)}, {}


def read_quota():
    """Primary-quota reading from GET /rate_limit plus its response headers.

    GitHub documents that calling this endpoint does not count against the
    primary rate limit, and that the `x-ratelimit-*` headers are authoritative
    when they disagree with the body.
    """
    status, body, headers = api_get("/rate_limit")
    if status != 200 or not isinstance(body, dict):
        return {"ok": False, "status": status, "reason": (body or {}).get("message", "")}
    core = (body.get("resources") or {}).get("core") or {}
    header_remaining = _int(headers.get("x-ratelimit-remaining"))
    readings = [v for v in (core.get("remaining"), header_remaining) if isinstance(v, int)]
    return {
        "ok": True,
        "readAt": utc_now(),
        "body": {"limit": core.get("limit"), "remaining": core.get("remaining"),
                 "reset": core.get("reset"), "used": core.get("used")},
        "headers": {"limit": _int(headers.get("x-ratelimit-limit")), "remaining": header_remaining,
                    "reset": _int(headers.get("x-ratelimit-reset"))},
        # Conservative: when the two readings disagree, trust the smaller one.
        "effectiveRemaining": min(readings) if readings else core.get("limit"),
    }


# --------------------------------------------------------------------------
# planning (pure functions — covered by tests/test_scheduled_audit.py)
# --------------------------------------------------------------------------

def slot_audits(slot):
    """The audits scheduled for a weekday, from SLOT_PLAN."""
    if isinstance(slot, str):
        slot = {name: index for index, name in SLOT_NAMES.items()}[slot.strip().lower()]
    return list(SLOT_PLAN[int(slot) % 7])


def usable_budget(remaining, budget, reserve):
    """How much this run may plan to spend.

    `remaining` is the live quota reading (None when unreadable). An unreadable
    counter narrows the budget to the hard ceiling; it never widens it.
    """
    ceiling = max(int(budget) - int(reserve), 0)
    if remaining is None:
        return ceiling
    return max(min(int(remaining), int(budget)) - int(reserve), 0)


def plan_run(order, costs, usable, skip_ahead=True):
    """Split the requested order into (planned, skipped) under a spend ceiling.

    `skip_ahead=False` stops at the first audit that does not fit — the stricter
    reading, kept for callers who prefer "no overtaking". The default lets a
    cheap audit use budget an expensive one could not.
    """
    planned, skipped, left = [], [], max(int(usable), 0)
    for index, name in enumerate(order):
        # A missing cost entry must never be read as "free": fall back to the
        # measured default, and to 0 only for an audit nobody has measured.
        need = int(costs.get(name, DEFAULT_COSTS.get(name, 0)))
        if need <= left:
            planned.append(name)
            left -= need
        else:
            skipped.append({"audit": name, "needed": need, "remainingBeforeSkip": left})
            if not skip_ahead:
                for later in order[index + 1:]:
                    skipped.append({"audit": later,
                                    "needed": int(costs.get(later, DEFAULT_COSTS.get(later, 0))),
                                    "remainingBeforeSkip": left})
                break
    return planned, skipped, left


def expected_costs(order=None):
    return {name: DEFAULT_COSTS.get(name, 0) for name in (order or AUDIT_ORDER)}


def access_block_reason(payload, exit_code, log_tail):
    """Say *why* an audit is incomplete, using the tool's own report first."""
    if isinstance(payload, dict):
        if payload.get("accessBlocked"):
            return payload.get("accessBlockReason") or "tool reported accessBlocked"
        errors = payload.get("apiErrors")
        if isinstance(errors, list) and errors:
            first = errors[0] if isinstance(errors[0], dict) else {}
            return "API error: HTTP %s %s" % (first.get("status"),
                                              first.get("message") or first.get("endpoint"))
        if payload.get("complete") is False:
            return "tool reported complete=false"
    for line in reversed((log_tail or "").splitlines()):
        low = line.lower()
        if "rate limit" in low or "http 403" in low or "http 401" in low or "api failure" in low:
            return line.strip()[:300]
    if exit_code == 2:
        return "tool exited 2 (API/environment failure)"
    return None


def verdict_for(name, exit_code, payload, fresh, log_tail=""):
    """Map one tool's exit code and report payload to a verdict + reason.

    `fresh` is True when this run wrote the report, False when the report on
    disk predates the run, and None when there is no report at all. A report
    this run did not write is never read as a verdict.
    """
    if fresh is None:
        return ERROR, "the tool wrote no report for this run"
    if payload is None:
        return ERROR, "the report this run wrote could not be read as JSON"
    if not fresh:
        return ERROR, "the report on disk is from an earlier run, not this one"
    if name == "verify_live":
        if payload.get("complete") is False or exit_code == 2:
            return INCOMPLETE, access_block_reason(payload, exit_code, log_tail) or "incomplete"
        hard = payload.get("hardMismatchCount")
        if isinstance(hard, int) and hard > 0:
            return FINDINGS, "%d hard mismatch(es) — re-run tools/build_data.py" % hard
        if payload.get("status") == "complete_with_mismatches":
            return FINDINGS, "report status complete_with_mismatches"
        if exit_code != 0:
            return INCOMPLETE, "tool exited %s while reporting no mismatch" % exit_code
        return PASS, "all API-derived fields match (volatile drift excluded)"
    if name == "audit_kind":
        if payload.get("unresolved"):
            return INCOMPLETE, access_block_reason(payload, exit_code, log_tail) or "unresolved entries"
        if payload.get("complete") is False:
            return INCOMPLETE, "tool reported complete=false"
        if payload.get("disagreements"):
            return FINDINGS, "%d kind disagreement(s)" % len(payload["disagreements"])
        if exit_code != 0:
            return INCOMPLETE, "tool exited %s" % exit_code
        return PASS, "%s/%s entries re-derived, 0 disagreements" % (
            payload.get("checkedEntries"), payload.get("totalEntries"))
    if name == "audit_descriptions":
        if payload.get("apiErrors"):
            return INCOMPLETE, access_block_reason(payload, exit_code, log_tail) or "API error"
        if payload.get("complete") is False:
            return INCOMPLETE, "tool reported complete=false"
        if payload.get("unresolved"):
            return FINDINGS, "%d description(s) need source review" % len(payload["unresolved"])
        if exit_code != 0:
            return INCOMPLETE, "tool exited %s" % exit_code
        return PASS, "%s/%s descriptions linted against their recorded README revision" % (
            payload.get("checkedEntries"), payload.get("totalEntries"))
    if name == "audit_provenance":
        if payload.get("accessBlocked") or payload.get("complete") is False:
            return INCOMPLETE, access_block_reason(payload, exit_code, log_tail) or "incomplete"
        findings = payload.get("findings") or []
        if findings:
            return FINDINGS, "%d citation finding(s)" % len(findings)
        if exit_code != 0:
            return INCOMPLETE, "tool exited %s" % exit_code
        return PASS, "%s/%s entries, %s citation checks, 0 findings" % (
            payload.get("entriesAudited"), payload.get("entriesTotal"), payload.get("checksPerformed"))
    return INCOMPLETE, "unregistered audit name"


def combined_results(ran, skipped):
    """Every audit this run touched, in report order: what ran, then what did not.

    A planned audit must never vanish from the report because another audit was
    skipped: the report is the only evidence of what a scheduled run actually
    covered, and a run that hides an `INCOMPLETE` behind a budget skip would
    understate exactly the failure this runner exists to surface.
    """
    results = list(ran)
    for item in skipped:
        results.append({
            "audit": item["audit"], "verdict": NOT_RUN,
            "needed": item["needed"], "remainingBeforeSkip": item["remainingBeforeSkip"],
            "reason": "not run: needs ~%s requests, budget left %s" % (item["needed"],
                                                                       item["remainingBeforeSkip"]),
            "seconds": 0, "toolReport": AUDITS[item["audit"]]["report"],
            "reviewEndpoint": AUDITS[item["audit"]]["review"], "what": AUDITS[item["audit"]]["what"],
            "logFile": None,
        })
    return results


def overall_outcome(results):
    """(outcome, exit code) for the run.

    A run that could not cover even its own scheduled audits is PARTIAL; an
    incomplete or errored audit always dominates; only a run in which every
    scheduled audit ran complete and clean is CLEAN.
    """
    verdicts = [r["verdict"] for r in results]
    if any(v in (INCOMPLETE, ERROR) for v in verdicts):
        return INCOMPLETE, EXIT_INCOMPLETE
    if any(v == FINDINGS for v in verdicts):
        return FINDINGS, EXIT_FINDINGS
    if not results or any(v == NOT_RUN for v in verdicts):
        return OUT_PARTIAL, EXIT_PARTIAL
    return CLEAN, EXIT_CLEAN


def summarize(name, payload):
    """Only the fields the report needs — never invent what a tool did not say."""
    keys = {
        "audit_kind": ("complete", "checkedEntries", "totalEntries", "derivedEntries"),
        "audit_descriptions": ("complete", "checkedEntries", "totalEntries"),
        "verify_live": ("status", "complete", "checks", "okCount", "driftCount", "hardMismatchCount"),
        "audit_provenance": ("complete", "accessBlocked", "entriesAudited", "entriesTotal",
                             "checksPerformed", "acceptedDescriptionExceptions"),
    }.get(name, ("complete",))
    summary = {k: payload.get(k) for k in keys if k in payload}
    # Counts keep the summary compact; review_items() carries the actual rows.
    for field in ("disagreements", "unresolved", "findings", "apiErrors", "hardMismatches",
                  "volatileDrift", "templateCitations", "unlistedInApi", "listedNotInApi"):
        if isinstance(payload.get(field), list):
            summary[field + "Count"] = len(payload[field])
    return summary


def _repo_api_url(repo, suffix=""):
    """A concrete official API URL for one repository, or None if it is unknown."""
    if not isinstance(repo, str) or not repo:
        return None
    return "%s/repos/%s/%s%s" % (API, OWNER, quote(repo, safe="-._~"), suffix)


def _owner_repos_url(owner=OWNER):
    return "%s/users/%s/repos?type=public&per_page=100&page=1" % (
        API, quote(str(owner), safe="-._~"))


def _configured_index_url(repo, source):
    """Recreate audit_kind's configured-path contents endpoint from its report."""
    if not isinstance(source, str) or not source.strip():
        return None
    parts = source.strip().split(None, 1)
    if len(parts) != 2:
        return None
    branch, path = parts
    subpath = path.strip("/")
    content_path = "/%s" % quote(subpath, safe="/") if subpath else ""
    ref = quote(branch, safe="-._~")
    return _repo_api_url(repo, "/contents%s/index.html?ref=%s" % (content_path, ref))


def _verify_live_source(entry, field):
    """Map verify_live's recorded field name to the REST resource it checks."""
    entry = str(entry or "")
    field = str(field or "")
    if entry.startswith("accounts/"):
        login = entry.split("/", 1)[1]
        if field in ("public repo list count", "pagesSites"):
            return _owner_repos_url(login)
        return "%s/users/%s" % (API, quote(login, safe="-._~"))
    if entry == "coverage":
        return _owner_repos_url()
    if entry.startswith("unreachable[]/"):
        return _repo_api_url(entry.split("/", 1)[1])
    if entry.startswith("sites[]/"):
        repo = entry.split("/", 1)[1]
        if field in ("pagesStatus", "pagesSource", "pagesUrl", "GET /pages"):
            return _repo_api_url(repo, "/pages")
        if field in ("commits", "firstCommit", "firstCommitSha", "lastCommit", "lastCommitSha",
                     "finalHeadSha", "finalLastCommit", "GET /commits",
                     "GET /commits final-head recheck"):
            per_page = "1" if field in ("finalHeadSha", "finalLastCommit",
                                         "GET /commits final-head recheck") else "100"
            return _repo_api_url(repo, "/commits?per_page=%s" % per_page)
        return _repo_api_url(repo)
    return None


def review_items(name, payload):
    """Copy report-level findings and drift into a compact, source-linked form.

    This is presentation only: it does not change an audit verdict, run any
    extra requests, infer a missing value, or turn provenance templates into
    hard findings. A `{path}` citation is retained verbatim and shown as a
    literal-placeholder response when that is what the audit reported.
    """
    if not isinstance(payload, dict):
        return []
    items = []

    if name == "audit_kind":
        for row in payload.get("disagreements", []) or []:
            if not isinstance(row, dict):
                continue
            repo = row.get("repo")
            sources = [_repo_api_url(repo, "/pages"),
                       _configured_index_url(repo, row.get("pagesSource"))]
            items.append({
                "type": "kind disagreement", "repo": repo, "field": "kind",
                "expected": row.get("overlayKind"), "observed": row.get("derivedKind"),
                "detail": "configured path %s; index.html HTTP %s" % (
                    row.get("pagesSource") or "not recorded", row.get("httpStatus", "unknown")),
                "sources": [source for source in sources if source],
            })
        for row in payload.get("unresolved", []) or []:
            if not isinstance(row, dict):
                continue
            repo = row.get("repo")
            sources = [_repo_api_url(repo, "/pages")]
            index_url = _configured_index_url(repo, row.get("source"))
            if index_url:
                sources.append(index_url)
            items.append({
                "type": "unresolved kind check", "repo": repo, "field": row.get("field"),
                "status": row.get("status"), "detail": row.get("message") or row.get("source"),
                "sources": [source for source in sources if source],
            })

    elif name == "audit_descriptions":
        readme_refs = payload.get("readmeRefs") if isinstance(payload.get("readmeRefs"), dict) else {}
        for row in payload.get("unresolved", []) or []:
            if not isinstance(row, dict):
                continue
            repo = row.get("repo")
            ref = readme_refs.get(repo)
            source = (_repo_api_url(repo, "/readme?ref=%s" % quote(str(ref), safe="-._~"))
                      if isinstance(ref, str) and ref else None)
            items.append({
                "type": "description source review", "repo": repo, "field": "numeric-token lint",
                "detail": row.get("why"), "tokens": row.get("tokens"), "ref": ref, "source": source,
            })
        for row in payload.get("apiErrors", []) or []:
            if not isinstance(row, dict):
                continue
            items.append({
                "type": "description API error", "repo": row.get("repo"), "field": "README read",
                "status": row.get("status"), "ref": row.get("ref"),
                "detail": row.get("message") or "API error reported without a message",
                "source": row.get("endpoint"),
            })

    elif name == "verify_live":
        def add_mismatch_rows(rows, item_type):
            for row in rows or []:
                if not isinstance(row, dict):
                    continue
                entry = str(row.get("entry") or "")
                repo = entry.split("/", 1)[1] if entry.startswith(("sites[]/", "unreachable[]/")) else None
                account = entry.split("/", 1)[1] if entry.startswith("accounts/") else None
                field = row.get("field")
                source_note = None
                if account and field == "pagesSites":
                    source_note = ("The verifier derives this count by reading each listed repository's /pages endpoint; "
                                   "the audit report does not retain all per-repository URLs.")
                items.append({
                    "type": item_type, "repo": repo, "account": account,
                    "field": field, "expected": row.get("committed"),
                    "observed": row.get("live"), "source": _verify_live_source(entry, field),
                    "sourceNote": source_note,
                })

        hard = payload.get("hardMismatches") if isinstance(payload.get("hardMismatches"), list) else []
        drift = payload.get("volatileDrift") if isinstance(payload.get("volatileDrift"), list) else []
        add_mismatch_rows(hard, "hard mismatch")
        add_mismatch_rows(drift, "snapshot drift (volatile; not automatically a defect)")

        def mismatch_key(row):
            return tuple(json.dumps(row.get(key), ensure_ascii=False, sort_keys=True, default=str)
                         for key in ("entry", "field", "committed", "live"))

        classified = {mismatch_key(row) for row in hard + drift if isinstance(row, dict)}
        for row in payload.get("mismatches", []) or []:
            if isinstance(row, dict) and mismatch_key(row) not in classified:
                add_mismatch_rows([row], "reported mismatch (classification unavailable)")

        for key, kind, detail in (
            ("unlistedInApi", "public repository missing from the directory",
             "reported by the public-repository API list"),
            ("listedNotInApi", "directory repository absent from the public API list",
             "reported by the public-repository API list"),
        ):
            for repo in payload.get(key, []) or []:
                items.append({"type": kind, "repo": repo, "field": key,
                              "detail": detail, "source": _owner_repos_url()})

        error = payload.get("error")
        if isinstance(error, dict):
            items.append({
                "type": "verification access block", "field": "API read",
                "status": error.get("httpStatus"), "detail": error.get("message"),
                # The blocked report does not retain the failed endpoint. Do not
                # guess one; the general review endpoint remains in Verdict detail.
                "source": None,
            })

    elif name == "audit_provenance":
        for row in payload.get("findings", []) or []:
            if not isinstance(row, dict):
                continue
            items.append({
                "type": "provenance finding", "repo": row.get("repo"),
                "field": row.get("finding"), "detail": row.get("detail"),
                "source": row.get("source") or None,
            })

        templates = payload.get("templateCitations")
        if not isinstance(templates, list):
            templates = []
        if not templates:
            entries = payload.get("entries") if isinstance(payload.get("entries"), list) else []
            templates = [{"repo": entry.get("repo"), **citation}
                         for entry in entries if isinstance(entry, dict)
                         for citation in (entry.get("templateCitations") or [])
                         if isinstance(citation, dict)]
        seen_templates = set()
        for row in templates:
            if not isinstance(row, dict):
                continue
            key = (row.get("repo"), row.get("endpoint"), row.get("status"), row.get("documentedStatus"))
            if key in seen_templates:
                continue
            seen_templates.add(key)
            endpoint = row.get("endpoint")
            detail = ("literal {path} placeholder request returned HTTP %s; this is not a concrete file citation"
                      % row.get("status", "unknown") if isinstance(endpoint, str) and "{path}" in endpoint
                      else "placeholder citation recorded by the provenance audit")
            items.append({
                "type": "provenance template citation", "repo": row.get("repo"),
                "field": "citation endpoint", "status": row.get("status"),
                "documentedStatus": row.get("documentedStatus"), "detail": detail,
                "source": endpoint,
            })

        if payload.get("accessBlocked") or payload.get("complete") is False:
            items.append({
                "type": "incomplete provenance coverage", "field": "entries audited",
                "expected": payload.get("entriesTotal"), "observed": payload.get("entriesAudited"),
                "detail": payload.get("accessBlockReason") or "the provenance report says complete=false",
                "source": None,
            })

    return items


# --------------------------------------------------------------------------
# running the audits
# --------------------------------------------------------------------------

def run_audit(name, out_dir, snapshot):
    spec = AUDITS[name]
    report_path = os.path.join(ROOT, spec["report"])
    before_mtime = os.path.getmtime(report_path) if os.path.exists(report_path) else None
    log_path = os.path.join(out_dir, "logs", "%s.log" % name)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    started_at = utc_now()
    started = time.time()
    with open(log_path, "w", encoding="utf-8") as log:  # output dir only, never a published file
        proc = subprocess.run([sys.executable] + spec["script"], cwd=ROOT,
                              stdout=log, stderr=subprocess.STDOUT)
    seconds = round(time.time() - started, 1)
    with open(log_path, encoding="utf-8", errors="replace") as fh:
        log_tail = fh.read()[-4000:]

    # A report from a previous run must never be read as this run's verdict.
    fresh = None
    payload = None
    if os.path.exists(report_path):
        after_mtime = os.path.getmtime(report_path)
        fresh = after_mtime != before_mtime or after_mtime >= started - 1
        try:
            with open(report_path, encoding="utf-8") as fh:
                payload = json.load(fh)
        except Exception:
            payload = None
    verdict, reason = verdict_for(name, proc.returncode, payload, fresh, log_tail)
    result = {
        "audit": name,
        "verdict": verdict,
        "reason": reason,
        "exitCode": proc.returncode,
        "seconds": seconds,
        "startedAt": started_at,
        "finishedAt": utc_now(),
        "toolReport": spec["report"],
        "logFile": os.path.relpath(log_path, out_dir),
        "reviewEndpoint": spec["review"],
        "what": spec["what"],
    }
    if isinstance(payload, dict):
        result["toolSummary"] = summarize(name, payload)
        if fresh:
            result["reviewItems"] = review_items(name, payload)
        if snapshot and payload.get("snapshotGenerated") and payload["snapshotGenerated"] != snapshot:
            result["snapshotMismatch"] = payload["snapshotGenerated"]
    return result


# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------

def _inline_code(value):
    """Render one JSON/text value as a safe, single-line Markdown code span."""
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    text = text.replace("\r", " ").replace("\n", " ")
    longest = run = 0
    for char in text:
        if char == "`":
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    fence = "`" * (longest + 1)
    pad = " " if text.startswith("`") or text.endswith("`") else ""
    return fence + pad + text + pad + fence


def _json_code(value):
    return _inline_code(json.dumps(value, ensure_ascii=False, sort_keys=True, default=str))


def _markdown_api_url(source):
    """Link only HTTPS GitHub REST API URLs; encode braces in literal templates."""
    if not isinstance(source, str):
        return None
    parts = urlsplit(source)
    if parts.scheme != "https" or parts.netloc.lower() != "api.github.com":
        return None
    return quote(source, safe=":/?=&%#-._~!$'()*+,;@")


def _render_review_source(source, item):
    if not isinstance(source, str) or not source:
        return "no source URL was included in the audit report; no link was inferred"
    url = _markdown_api_url(source)
    if not url:
        return "%s (not linked: the audit report did not provide a GitHub REST API URL)" % _inline_code(source)
    if "{path}" in source:
        status = item.get("status")
        status_note = "HTTP `%s`" % status if status is not None else "HTTP status not recorded"
        flagged = ("; see [FLAGGED.md (FL-18)](<https://github.com/buffedlizard55-lab/MasterSite/blob/main/FLAGGED.md>)"
                   if status == 404 else "")
        return ("%s — literal-placeholder probe (%s): [open API response](<%s>); "
                "not a concrete file citation%s" % (_inline_code(source), status_note, url, flagged))
    return "[%s](<%s>)" % (_inline_code(source), url)


def _render_review_item(item):
    heading = " · ".join(_inline_code(value) for value in
                         (item.get("repo"), item.get("account"), item.get("field")) if value is not None)
    first = "- **%s**" % item.get("type", "review item")
    if heading:
        first += " — " + heading
    lines = [first]
    if "expected" in item or "observed" in item:
        lines.append("  - recorded/expected: %s; API observation: %s" % (
            _json_code(item.get("expected")), _json_code(item.get("observed"))))
    if "tokens" in item:
        lines.append("  - numeric tokens: %s" % _json_code(item.get("tokens")))
    if item.get("ref") is not None:
        lines.append("  - README ref: %s" % _inline_code(item.get("ref")))
    if item.get("status") is not None:
        lines.append("  - HTTP status: %s" % _inline_code(item.get("status")))
    if "documentedStatus" in item:
        lines.append("  - status documented in basis: %s" % _json_code(item.get("documentedStatus")))
    if item.get("detail"):
        lines.append("  - detail: %s" % _inline_code(item.get("detail")))
    if item.get("sourceNote"):
        lines.append("  - source note: %s" % _inline_code(item.get("sourceNote")))
    sources = item.get("sources")
    if not isinstance(sources, list):
        sources = [item.get("source")]
    links = [_render_review_source(source, item) for source in sources if source]
    lines.append("  - source: %s" % (" · ".join(links) if links else _render_review_source(None, item)))
    return lines


def render_report(run, results, quota, planned):
    lines = []
    lines.append("# Scheduled read-only audit — %s" % run["finishedAt"])
    lines.append("")
    lines.append("**Outcome: `%s`** (exit %s) · schedule slot `%s` · revision `%s` · [run](%s)"
                 % (run["outcome"], run["exitCode"], run["slot"], run["revision"] or "unknown",
                    run["runUrl"] or "n/a"))
    lines.append("")
    lines.append("Published snapshot audited: `%s`" % (run["snapshot"] or "unknown"))
    lines.append("")
    lines.append("Coverage this run: **%s of the 4 audits** (%s); the weekday schedule covers the rest "
                 "of the week (`tools/scheduled_audit.py --slot <day>`)."
                 % (len([r for r in results if r["verdict"] != NOT_RUN]), ",".join(
                     "`%s`" % r["audit"] for r in results if r["verdict"] != NOT_RUN) or "none"))
    lines.append("")
    lines.append("| Audit | Verdict | Requests | Seconds | What it re-read | Tool report |")
    lines.append("|---|---|---|---|---|---|")
    for result in results:
        lines.append("| `%s` | **%s** | %s | %s | %s | `%s` |"
                     % (result["audit"], result["verdict"],
                        result.get("requestsObserved") if result.get("requestsObserved") is not None else "n/a",
                        result["seconds"], result["what"], result["toolReport"]))
    lines.append("")
    not_run = [r for r in results if r["verdict"] == NOT_RUN]
    if not_run:
        lines.append("## Not run in this run (budget)")
        lines.append("")
        lines.append("| Audit | Requests it needs | Budget left when skipped |")
        lines.append("|---|---|---|")
        for result in not_run:
            lines.append("| `%s` | %s | %s |" % (result["audit"], result.get("needed", "?"),
                                                  result.get("remainingBeforeSkip", "?")))
        lines.append("")
        lines.append("These are **not** reported as checked. %s" % REMEDY)
        lines.append("")
    lines.append("## Verdict detail")
    lines.append("")
    for result in results:
        lines.append("- **`%s` — %s** · %s" % (result["audit"], result["verdict"], result["reason"]))
        if result.get("toolSummary"):
            lines.append("  - tool report: `%s`" % json.dumps(result["toolSummary"], sort_keys=True))
        if result.get("snapshotMismatch"):
            lines.append("  - ⚠ the tool audited snapshot `%s`, not the checkout's `%s`"
                         % (result["snapshotMismatch"], run["snapshot"]))
        lines.append("  - hand review, one official endpoint per row: `%s`" % result["reviewEndpoint"])
        lines.append("  - log: `%s`" % result["logFile"])
    lines.append("")
    lines.append("## Individual review items")
    lines.append("")
    lines.append("Rows below are copied from the audit reports. Volatile drift is not automatically a defect; "
                 "`{path}` templates remain non-concrete citations and are not promoted to hard findings.")
    lines.append("")
    review_results = [result for result in results if result.get("reviewItems")]
    if review_results:
        for result in review_results:
            items = result["reviewItems"]
            lines.append("### `%s` — %d item(s)" % (result["audit"], len(items)))
            lines.append("")
            for item in items:
                lines.extend(_render_review_item(item))
            lines.append("")
    else:
        lines.append("No item-level findings, mismatches, drift rows or template citations were emitted by "
                     "the reports available in this run. Audits marked `NOT-RUN` remain unchecked.")
        lines.append("")
    lines.append("## API budget")
    lines.append("")
    if quota.get("ok"):
        lines.append("- live reading: limit %s, remaining %s, reset %s (body) · headers: limit %s, remaining %s"
                     % (quota["body"]["limit"], quota["body"]["remaining"], quota["body"]["reset"],
                        quota["headers"]["limit"], quota["headers"]["remaining"]))
        lines.append("- effective remaining used for planning: **%s**" % quota["effectiveRemaining"])
    else:
        lines.append("- live quota could not be read (HTTP %s%s) — planning fell back to the hard ceiling"
                     % (quota.get("status"), ": %s" % quota["reason"] if quota.get("reason") else ""))
    lines.append("- planned spend ceiling: %s (budget %s − reserve %s), planned: %s"
                 % (run["usable"], run["budget"], run["reserve"],
                    ", ".join("`%s`" % n for n in planned) or "nothing"))
    lines.append("- why a hard ceiling at all: the built-in Actions `GITHUB_TOKEN` is limited to "
                 "1,000 requests/hour/repository "
                 "(<https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api>) "
                 "and a full pass costs more than that.")
    lines.append("")
    lines.append("## Caveats")
    lines.append("")
    lines.append("- %s" % CAVEAT)
    lines.append("- An `INCOMPLETE` verdict means the audit could not finish — most often an API access "
                 "block. It is never a pass, and it says nothing about the sites themselves.")
    lines.append("- `NOT-RUN` audits were skipped for budget; `CLEAN` means the audits scheduled for "
                 "*this run* came back clean, not that the whole suite ran.")
    lines.append("- This job is read-only: it publishes no data and commits nothing.")
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# offline checks (no network, no writes)
# --------------------------------------------------------------------------

def self_test():
    """Deterministic checks of the load-bearing rules. Returns a failure count."""
    failures = []

    def expect(condition, message):
        if not condition:
            failures.append(message)

    costs = {AUDIT_ORDER[0]: 300, AUDIT_ORDER[1]: 600, AUDIT_ORDER[2]: 150, AUDIT_ORDER[3]: 1100}
    order = list(AUDIT_ORDER)
    planned, skipped, left = plan_run(order, costs, 500)
    expect(planned == [order[0], order[2]] and [s["audit"] for s in skipped] == [order[1], order[3]],
           "plan should take the audits that fit and skip the rest, got %s / %s" % (planned, skipped))
    expect(left == 50, "budget left should be 50, got %s" % left)
    planned, skipped, _ = plan_run(order, costs, 500, skip_ahead=False)
    expect(planned == [order[0]] and [s["audit"] for s in skipped] == order[1:],
           "strict plan must stop at the first audit that does not fit")
    expect(plan_run(order, costs, 0)[0] == [], "a zero budget must plan nothing")
    expect(usable_budget(None, 900, 100) == 800, "unreadable quota falls back to the ceiling")
    expect(usable_budget(50, 900, 100) == 0, "the reserve must never be planned for spending")
    expect(usable_budget(4000, 900, 100) == 800, "a bigger live quota must not widen the ceiling")
    expect(slot_audits("sunday") == order, "Sunday must attempt the full suite")
    weekly = {}
    for day in SLOT_PLAN.values():
        for audit in day:
            weekly[audit] = weekly.get(audit, 0) + 1
    expect(sorted(weekly) == sorted(order), "every audit must appear in the weekly plan")
    expect(all(count >= 2 for count in weekly.values()),
           "every audit must be scheduled at least twice a week, got %s" % weekly)
    expect(all(set(day) <= set(order) for day in SLOT_PLAN.values()),
           "the slot plan may only name registered audits")

    v, _ = verdict_for("audit_kind", 0, {"complete": True, "checkedEntries": 145, "totalEntries": 145,
                                         "disagreements": [], "unresolved": []}, True)
    expect(v == PASS, "clean kind audit must pass")
    expect(verdict_for("audit_kind", 1, {"complete": True, "disagreements": [{"repo": "X"}]}, True)[0]
           == FINDINGS, "a kind disagreement must be FINDINGS")
    expect(verdict_for("audit_kind", 0, {"complete": False, "unresolved": [{"status": 500}]}, True)[0]
           == INCOMPLETE, "unresolved kind entries must be INCOMPLETE")
    expect(verdict_for("verify_live", 2, {"complete": False}, True)[0] == INCOMPLETE,
           "a blocked verify_live must be INCOMPLETE")
    expect(verdict_for("verify_live", 0, {"complete": True, "hardMismatchCount": 3}, True)[0]
           == FINDINGS, "hard mismatches must be FINDINGS")
    expect(verdict_for("audit_descriptions", 0, {"complete": True, "unresolved": []}, True)[0] == PASS,
           "a clean description audit must pass")
    expect(verdict_for("audit_descriptions", 2, {"complete": False, "apiErrors": [{"status": 403}]}, True)[0]
           == INCOMPLETE, "a description API error must be INCOMPLETE")
    expect(verdict_for("audit_provenance", 0, {"complete": True, "accessBlocked": False,
                                               "findings": []}, True)[0] == PASS,
           "a clean provenance audit must pass")
    expect(verdict_for("audit_provenance", 0, {"complete": True, "findings": [{"c": 1}]}, True)[0]
           == FINDINGS, "a provenance finding must be FINDINGS")
    expect(verdict_for("audit_kind", 0, {"complete": True}, None)[0] == ERROR,
           "a report this run did not write must never become a verdict")
    expect(verdict_for("audit_kind", 0, {"complete": True}, False)[0] == ERROR,
           "a stale report must never become a verdict")

    expect(overall_outcome([{"verdict": PASS}] * 4) == (CLEAN, EXIT_CLEAN),
           "all four scheduled audits passing is CLEAN")
    expect(overall_outcome([{"verdict": PASS}, {"verdict": PASS}]) == (CLEAN, EXIT_CLEAN),
           "a two-audit weekday slot that both passed is CLEAN for that slot")
    expect(overall_outcome([{"verdict": PASS}, {"verdict": NOT_RUN}])[0] == OUT_PARTIAL,
           "a skipped audit must make the run PARTIAL")
    expect(overall_outcome([{"verdict": PASS}, {"verdict": INCOMPLETE}])[0] == INCOMPLETE,
           "an incomplete audit must dominate")
    expect(overall_outcome([{"verdict": PASS}, {"verdict": FINDINGS}])[0] == FINDINGS,
           "findings must be reported")
    expect(overall_outcome([])[0] == OUT_PARTIAL, "a run with no results is not CLEAN")
    expect([r["audit"] for r in combined_results(
        [{"audit": AUDIT_ORDER[0], "verdict": INCOMPLETE}],
        [{"audit": AUDIT_ORDER[1], "needed": DEFAULT_COSTS[AUDIT_ORDER[1]],
          "remainingBeforeSkip": 0}])] == [AUDIT_ORDER[0], AUDIT_ORDER[1]],
        "an audit that ran must not be dropped when a later audit is skipped")
    expect(overall_outcome(combined_results(
        [{"audit": AUDIT_ORDER[0], "verdict": INCOMPLETE}],
        [{"audit": AUDIT_ORDER[1], "needed": DEFAULT_COSTS[AUDIT_ORDER[1]],
          "remainingBeforeSkip": 0}]))[0] == INCOMPLETE,
        "an access block must dominate a budget skip, not be reported as PARTIAL")
    expect(bool(access_block_reason({"complete": False}, 2, "")),
           "an unexplained incomplete run must still get a reason")
    expect(bool(access_block_reason(None, 2, "")),
           "an exit-code-2 run with no report must still get a reason")
    expect("zero hallucinations" not in CAVEAT.lower(), "the caveat must not overclaim")
    return failures


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output-dir", default=os.path.join(ROOT, ".work", "scheduled-audit"))
    parser.add_argument("--slot", default="today",
                        help="weekday slot: today (default), a weekday name, or 0-6 with 0=Monday")
    parser.add_argument("--audits", help="explicit comma-separated subset, overriding --slot")
    parser.add_argument("--budget", type=int, default=DEFAULT_BUDGET,
                        help="hard per-run request ceiling (default %d)" % DEFAULT_BUDGET)
    parser.add_argument("--reserve", type=int, default=DEFAULT_RESERVE,
                        help="requests never planned for spending (default %d)" % DEFAULT_RESERVE)
    parser.add_argument("--plan-only", action="store_true",
                        help="read the quota, print the plan, run nothing")
    parser.add_argument("--run-url", default="", help="the workflow run URL, for the report")
    parser.add_argument("--revision", default="", help="commit being audited")
    parser.add_argument("--self-test", action="store_true", help="run the offline checks and exit")
    args = parser.parse_args(argv)

    if args.self_test:
        failures = self_test()
        for failure in failures:
            print("SELF-TEST FAIL: %s" % failure)
        print("self-test: %d checks failed" % len(failures))
        return 1 if failures else 0

    today = datetime.datetime.now(datetime.timezone.utc).weekday()
    slot = SLOT_NAMES[today] if args.slot == "today" else args.slot
    try:
        requested = ([a.strip() for a in args.audits.split(",")] if args.audits
                     else slot_audits(slot))
    except (KeyError, ValueError):
        parser.error("unknown slot or audit: %s / %s" % (slot, args.audits))
    unknown = [a for a in requested if a not in AUDITS]
    if unknown:
        print("unknown audit(s) %s; known: %s" % (", ".join(unknown), ", ".join(AUDIT_ORDER)))
        return EXIT_INCOMPLETE

    out_dir = args.output_dir
    os.makedirs(out_dir, exist_ok=True)
    snapshot = snapshot_generated()
    costs = expected_costs(requested)
    quota = read_quota()
    usable = usable_budget(quota.get("effectiveRemaining") if quota.get("ok") else None,
                           args.budget, args.reserve)
    planned, skipped, left = plan_run(requested, costs, usable)

    print("published snapshot: %s" % snapshot)
    print("schedule slot: %s → %s" % (slot, ", ".join(requested)))
    print("quota: %s" % ("limit=%s remaining=%s (headers remaining=%s)"
                         % (quota["body"]["limit"], quota["body"]["remaining"], quota["headers"]["remaining"])
                         if quota.get("ok") else "unreadable (HTTP %s) — ceiling only" % quota.get("status")))
    print("budget: usable %s (budget %s − reserve %s) → planned %s"
          % (usable, args.budget, args.reserve, ", ".join(planned) or "nothing"))
    for item in skipped:
        print("skip: %s needs ~%s, budget left %s — %s" % (item["audit"], item["needed"],
                                                           item["remainingBeforeSkip"], REMEDY))

    if args.plan_only:
        return EXIT_CLEAN if not skipped else EXIT_PARTIAL

    ran = []
    for name in planned:
        before = read_quota()
        result = run_audit(name, out_dir, snapshot)
        after = read_quota()
        for reading, key in ((before, "remainingBefore"), (after, "remainingAfter")):
            if reading.get("ok"):
                result[key] = reading["effectiveRemaining"]
        if result.get("remainingBefore") is not None and result.get("remainingAfter") is not None:
            spent = result["remainingBefore"] - result["remainingAfter"]
            # Region-to-region variation makes a negative delta meaningless; a
            # zero delta is reported as not observable, never as "free".
            if spent > 0:
                result["requestsObserved"] = spent
        print("%-20s %-10s %6ss  %s" % (name, result["verdict"], result["seconds"], result["reason"]))
        ran.append(result)

    results = combined_results(ran, skipped)
    # Fail closed if the report would have a hole: every requested audit must
    # appear, whichever way it went. A silent hole is the one outcome worse than
    # a red run, because the report is what a reviewer reads.
    named = set(r["audit"] for r in results)
    if named != set(requested):
        print("internal error: no verdict recorded for %s — refusing to publish a report with a "
              "hole" % ", ".join(sorted(set(requested) - named)))
        return EXIT_INCOMPLETE

    outcome, exit_code = overall_outcome(results)
    run = {
        "startedAt": min([r.get("startedAt") or utc_now() for r in results] or [utc_now()]),
        "finishedAt": utc_now(),
        "outcome": outcome,
        "exitCode": exit_code,
        "slot": slot,
        "requested": requested,
        "revision": args.revision,
        "runUrl": args.run_url,
        "snapshot": snapshot,
        "budget": args.budget,
        "reserve": args.reserve,
        "usable": usable,
        "quota": quota,
        "remedy": REMEDY,
        "caveat": CAVEAT,
    }
    report_md = render_report(run, results, quota, planned)
    report_json = {"runner": "tools/scheduled_audit.py", "run": run, "results": results,
                   "skipped": skipped}
    with open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8") as fh:
        fh.write(report_md)
    with open(os.path.join(out_dir, "report.json"), "w", encoding="utf-8") as fh:
        json.dump(report_json, fh, indent=2, sort_keys=True)

    print("outcome: %s (exit %s) — report: %s" % (outcome, exit_code,
                                                  os.path.join(out_dir, "report.md")))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
