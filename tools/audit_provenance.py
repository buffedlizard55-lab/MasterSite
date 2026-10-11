#!/usr/bin/env python3
"""Provenance reproducibility audit for MasterSite.

Every published record asserts *where* its facts came from: a provenance stamp
(`verifiedAtSha`), first/last commit SHAs, a snapshot head, and a `verifiedBasis`
sentence that cites the official endpoints it was read from. Until now nothing
mechanically re-opened those citations; `verify_live.py` re-reads the *current*
API values, and `audit_descriptions.py` lints numeric tokens against the README
at the recorded *head* only.

This tool is the line-by-line counterpart: for every published entry it asks the
official API to reproduce the citation itself.

  1. Provenance stamps — every recorded SHA (`verifiedAtSha`, `firstCommitSha`,
     `lastCommitSha`, `headSha`) must resolve to a real commit in that
     repository. A stamp that returns HTTP 404 is a hard finding: the prose
     claims to have been read at a commit that does not exist.
  2. Cited sources — every `https://api.github.com/...` URL inside the entry's
     own `verifiedBasis` is re-issued at the recorded ref.
       * `.../readme?ref=X`            must return 200
       * `.../contents/index.html?ref=X` must agree with the entry's `kind`
         (200 for `app`, 404 for `stub`)
       * `.../contents/?ref=X` (root)  must list `index.html` when `kind` is app
       * `.../pages`                   must report the entry's `pagesUrl`
  3. Description provenance — the numeric tokens of the curated description are
     re-checked against the README *at the recorded provenance SHA* (not at the
     head), which is the claim the record actually makes. Documented exceptions
     in `tools/overlay.json` → `acceptedDescriptionExceptions` are honoured, so
     this tool uses the same bar as `audit_descriptions.py`.

Transport, authorization and rate-limit failures abort the audit (exit 2) and
are never reported as data findings. The tool is read-only: it never writes
`data/sites.js`, and an INCOMPLETE run is never a pass.

Usage:
    python3 tools/audit_provenance.py            # audit every published entry
    python3 tools/audit_provenance.py --repo X   # audit one repository
    python3 tools/audit_provenance.py --no-report  # stdout + JSON only
"""

import argparse
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.github.com"
OWNER = "buffedlizard55-lab"
CACHE = os.path.join(ROOT, "tools", ".readme-cache")
REPORTS = os.path.join(ROOT, "reports", "provenance")
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
URL_RE = re.compile(r"https://api\.github\.com/[^\s`\"'<>\)\]]+")
NUM_RE = re.compile(r"\b\d[\d,]*(?:\.\d+)?\s*(?:%|x|k|K|KB|MB|GB)?\b")

# Set when GitHub refuses to serve the audit; turns the run into an access block.
API_FAILURE = None
API_FAILURE_STATUS = None
# Memo of path → (status, body) for this process. Several entries legitimately
# name the same endpoint (a shared provenance SHA, a repeated citation), and
# re-issuing it costs a politeness delay without adding evidence. No semantics
# change: the identical GET is simply answered from the first response.
_RESPONSE_CACHE = {}
_CACHE_LOCK = threading.Lock()
# Global spacing between request starts, shared by every worker. Concurrency
# here is bounded by the request count, not by impatience: the account census
# needs ~1,100 reads and GitHub's secondary (abuse-detection) limiter reacts to
# bursts, which is why the other read-only tools sleep between calls. A small
# worker pool with a global gap keeps the same average rate while removing the
# per-request latency serialization that made a 145-entry run take an hour.
_THROTTLE_LOCK = threading.Lock()
_LAST_REQUEST = [0.0]
_REQUEST_GAP = 0.45


def api_get(path, accept="application/vnd.github+json"):
    """GET an api.github.com path (memoized per process). Returns (status, body)."""
    key = accept + " " + path
    with _CACHE_LOCK:
        if key in _RESPONSE_CACHE:
            return _RESPONSE_CACHE[key]
    result = _api_get_uncached(path, accept)
    # Only stable answers are memoized: an access-block placeholder must not be
    # frozen into the cache for later calls.
    if not API_FAILURE:
        with _CACHE_LOCK:
            _RESPONSE_CACHE[key] = result
    return result


def _api_get_uncached(path, accept):
    global API_FAILURE, API_FAILURE_STATUS
    if API_FAILURE:
        return API_FAILURE_STATUS, {"message": API_FAILURE}
    # Politeness floor, matching the other read-only tools: sustained unthrottled
    # bursts across a 146-repository census trip GitHub's secondary
    # (abuse-detection) rate limit, which answers HTTP 403 while the hourly quota
    # is untouched (observed 2026-10-11, see HANDOFF.md). No semantics change.
    with _THROTTLE_LOCK:
        wait = _REQUEST_GAP - (time.time() - _LAST_REQUEST[0])
        if wait > 0:
            time.sleep(wait)
        _LAST_REQUEST[0] = time.time()
    req = urllib.request.Request(
        API + path,
        headers={
            "Accept": accept,
            "User-Agent": "MasterSite-provenance-audit",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", "replace")
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as exc:
        body = {}
        try:
            body = json.loads(exc.read().decode("utf-8", "replace"))
        except Exception:
            body = {}
        if exc.code in (401, 403):
            message = body.get("message") if isinstance(body, dict) else ""
            # 403 "rate limit exceeded" is an access block, not field drift;
            # 401 is dead credentials. Both stop the audit.
            if exc.code == 401 or "rate limit" in (message or "").lower() or "abuse" in (message or "").lower():
                API_FAILURE = "HTTP %d — %s" % (exc.code, message or "authorization/rate-limit failure")
                API_FAILURE_STATUS = exc.code
        return exc.code, body
    except Exception as exc:  # transport error
        API_FAILURE = "transport error: %s" % exc
        API_FAILURE_STATUS = 0
        return 0, {"message": str(exc)}


def load_snapshot():
    src = open(os.path.join(ROOT, "data", "sites.js"), encoding="utf-8").read()
    return json.loads(src.split("window.MASTERDATA = ", 1)[1].rstrip().rstrip(";"))


def readme_at(repo, ref):
    """README text at `ref`, or (None, error). Cached on disk like the other audits."""
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", ref or "default")
    path = os.path.join(CACHE, repo + "-" + safe[:40] + ".md")
    if os.path.exists(path):
        return open(path, encoding="utf-8").read(), None
    quoted = urllib.parse.quote(ref or "main", safe="")
    for name in ("README.md", "readme.md", "README.MD", "Readme.md"):
        endpoint = "/repos/%s/%s/contents/%s?ref=%s" % (OWNER, repo, name, quoted)
        status, body = api_get(endpoint, accept="application/vnd.github.raw")
        if status == 200 and isinstance(body, str):
            open(path, "w", encoding="utf-8").write(body)
            return body, None
        if status == 404:
            continue
        return None, {"status": status, "endpoint": endpoint,
                      "message": body.get("message") if isinstance(body, dict) else str(body)}
    return None, None  # genuinely no supported README name at this ref


def numeric_tokens(text):
    out = []
    for match in NUM_RE.finditer(text or ""):
        token = match.group(0).strip()
        if not re.sub(r"[^\d]", "", token):
            continue
        if re.fullmatch(r"(19|20)\d\d", token):  # years, not claims
            continue
        out.append(token)
    return out


def cited_urls(basis):
    """Distinct official URLs cited inside a verifiedBasis sentence."""
    seen, out = set(), []
    for raw in URL_RE.findall(basis or ""):
        url = raw.rstrip(".,;:")
        if url in seen:
            continue
        seen.add(url)
        out.append(url)
    return out


DOCUMENTED_STATUS_RE = re.compile(r"(?:HTTP\s*|returns?\s+(?:HTTP\s*)?|status\s+(?:of\s+)?)([1-5]\d\d)")


def documented_status(basis, url):
    """The HTTP status this basis sentence states *for this URL*, if any.

    Curated prose is allowed — and on this repository is expected — to cite a
    negative result as evidence ("GET .../commits/03d8db1 returns 422 'No commit
    found'"). Re-issuing that URL therefore returns 422 by design, not because
    the record is wrong. Reading the asserted status out of the sentence turns
    a false failure into a checkable claim: the audit then requires the live
    status to match what the prose documents.
    """
    idx = basis.find(url)
    if idx < 0:
        return None
    start = max(basis.rfind(".", 0, idx) + 1, 0)
    window = basis[start:idx + len(url) + 80]
    # Only status codes attached to a status word count; bare numbers in prose
    # (counts, sizes, dates) must not be read as an expected HTTP status.
    matches = DOCUMENTED_STATUS_RE.findall(window)
    return int(matches[-1]) if matches else None


def check_citation(url):
    """Re-issue one cited API URL. Returns (status, note, blob_sha)."""
    parts = urllib.parse.urlsplit(url)
    if parts.netloc != "api.github.com":
        return None, "not an api.github.com citation", None
    path = parts.path
    query = dict(urllib.parse.parse_qsl(parts.query))
    ref = query.get("ref") or query.get("sha")
    full = path + ("?" + parts.query if parts.query else "")
    status, body = api_get(full)
    if API_FAILURE:
        return status, "access block", None
    note, blob = "", None
    if isinstance(body, dict):
        blob = body.get("sha")
        if "html_url" in body:
            note = body["html_url"]
    low = path.lower()
    if "/readme" in path or path.rstrip("/").endswith("readme"):
        kind = "readme"
    elif "/contents" in path:
        kind = "contents"
    elif path.rstrip("/").endswith("/pages"):
        kind = "pages"
    elif "/commits" in path:
        kind = "commits"
    elif "/git/trees" in path or "/git/refs" in path:
        kind = "git"
    else:
        kind = "other"
    return status, note, {"kind": kind, "ref": ref, "blob": blob, "endpoint": full, "body": body}


def audit_entry(site, accepted, index_root_listing_cache):
    repo = site["repo"]
    findings, checks, negative, templates = [], [], [], []

    # 1. provenance stamps resolve to real commits
    stamps = {
        "verifiedAtSha": site.get("verifiedAtSha"),
        "firstCommitSha": site.get("firstCommitSha"),
        "lastCommitSha": site.get("lastCommitSha"),
        "headSha": site.get("headSha"),
    }
    resolved = {}
    for field, sha in stamps.items():
        if not sha:
            resolved[field] = None
            continue
        if not SHA_RE.match(str(sha)):
            findings.append(("%s is not a commit SHA" % field, str(sha), ""))
            resolved[field] = None
            continue
        status, body = api_get("/repos/%s/%s/commits/%s" % (OWNER, repo, sha))
        if API_FAILURE:
            return None, findings, checks
        endpoint = "%s/repos/%s/%s/commits/%s" % (API, OWNER, repo, sha)
        checks.append({"check": field, "endpoint": endpoint, "status": status})
        if status != 200:
            findings.append(("%s does not resolve in this repository" % field, str(sha), endpoint))
            resolved[field] = None
            continue
        resolved[field] = body.get("sha")
        if resolved[field] != sha and not resolved[field].startswith(str(sha)):
            findings.append(("%s resolves to a different commit" % field, "%s → %s" % (sha, resolved[field]), endpoint))

    # 2. cited sources reproduce
    citations = cited_urls(site.get("verifiedBasis"))
    kind = site.get("kind")
    basis = site.get("verifiedBasis") or ""
    for url in citations:
        status, note, meta = check_citation(url)
        if API_FAILURE:
            return None, findings, checks
        checks.append({"check": "citation", "endpoint": url, "status": status})
        if meta is None:  # a non-api.github.com URL: recorded, not resolved here
            continue

        # A citation containing a {placeholder} is a reproduction *recipe*, not
        # an endpoint a reviewer can open. Five records close their basis with
        # "Reproduce: GET .../contents/{path}?ref=<sha>". The live 404 is
        # recorded (it proves the literal string is not openable), but the
        # record is not failed for the template itself: it is surfaced
        # separately so the reviewer sees exactly what to substitute.
        if "{" in url or "}" in url:
            templates.append({"endpoint": url, "status": status,
                              "documentedStatus": documented_status(basis, url)})
            checks.append({"check": "template-citation", "endpoint": url, "status": status})
            continue

        asserted = documented_status(basis, url)
        if status != 200:
            negative.append({"endpoint": url, "status": status,
                             "documentedStatus": asserted, "kind": meta["kind"]})
        # A non-200 citation is only a defect when the prose does not document
        # that status for this URL. When it does, the citation is reproducible
        # evidence and the documented value must equal the live value (2b).
        documents_negative = asserted is not None and asserted == status and status != 200

        # Kind agreement is itself a documented expectation: a stub is expected
        # to have no index.html at the configured path, an app is expected to
        # have one. Anything else must be visible.
        path = urllib.parse.urlsplit(url).path
        base = os.path.basename(path.rstrip("/")).lower()
        expected_by_kind = (meta["kind"] == "contents" and base == "index.html"
                            and ((kind == "app" and status == 200)
                                 or (kind == "stub" and status == 404)))

        if status != 200 and not documents_negative and not expected_by_kind:
            findings.append(("cited %s endpoint does not reproduce (HTTP %s)"
                             % (meta["kind"], status), "", url))
        if documents_negative:
            checks.append({"check": "documented-negative-citation", "endpoint": url, "status": status})

        if meta["kind"] == "contents":
            if base == "index.html":
                if kind == "app" and status != 200:
                    findings.append(("kind=app but the cited index.html read returns HTTP %s" % status, "", url))
                if kind == "stub" and status == 200:
                    findings.append(("kind=stub but the cited index.html read returns HTTP 200", "", url))
            elif path.rstrip("/").endswith("contents"):
                # root listing: an `app` entry must actually contain index.html there
                if status == 200 and kind == "app" and isinstance(meta["body"], list):
                    names = {str(item.get("name", "")).lower() for item in meta["body"]}
                    if "index.html" not in names:
                        findings.append(("kind=app but the cited root listing has no index.html", "", url))
        if meta["kind"] == "pages" and status == 200:
            html_url = (meta["body"] or {}).get("html_url") if isinstance(meta["body"], dict) else None
            if html_url and html_url.rstrip("/") != (site.get("pagesUrl") or "").rstrip("/"):
                findings.append(("published pagesUrl differs from the API's html_url",
                                 "%s ≠ %s" % (site.get("pagesUrl"), html_url), url))

    # 2b. a documented status that moved is a finding in its own right: the
    # prose asserts an observation and the API no longer reproduces it.
    for note in negative:
        asserted = note["documentedStatus"]
        if asserted is not None and asserted != note["status"]:
            findings.append(("basis documents HTTP %s for this URL but the API answered HTTP %s"
                             % (asserted, note["status"]), "", note["endpoint"]))

    # 3. the description's numbers must exist in the README at the *stamp* SHA
    stamp = site.get("verifiedAtSha")
    tokens_note = ""
    if stamp:
        text, error = readme_at(repo, stamp)
        if API_FAILURE:
            return None, findings, checks
        if error:
            findings.append(("README at the provenance SHA could not be read", "HTTP %s" % error.get("status"), error.get("endpoint")))
        elif text:
            misses = []
            for token in numeric_tokens(site.get("description")):
                digits = re.sub(r"[^\d]", "", token)
                if digits in re.sub(r"[^\d]", "", text):
                    continue
                if token.lower() in text.lower() or token.lower().replace(",", "") in text.lower():
                    continue
                misses.append(token)
            if misses and repo in accepted:
                tokens_note = "accepted exception"
            elif misses:
                tokens_note = "unmatched: " + ", ".join(misses)
                findings.append(("numeric tokens absent from the README at the provenance SHA",
                                 ", ".join(misses),
                                 "%s/repos/%s/%s/readme?ref=%s" % (API, OWNER, repo, stamp)))
            else:
                tokens_note = "all tokens present"
        else:
            tokens_note = "no supported README name at the provenance SHA"

    return {"repo": repo, "kind": kind, "stamp": stamp, "stampsResolved": resolved,
            "citationsChecked": len(citations), "readmeTokens": tokens_note,
            "negativeCitations": negative, "templateCitations": templates}, findings, checks


def main():
    parser = argparse.ArgumentParser(description="MasterSite provenance reproducibility audit")
    parser.add_argument("--repo", help="audit a single repository")
    parser.add_argument("--no-report", action="store_true", help="do not write the markdown report")
    parser.add_argument("--force-artifacts", action="store_true",
                        help="write the canonical artifacts even for a single-repo run (default: a --repo "
                             "spot check reports to stdout only, so a partial run can never overwrite a full one)")
    parser.add_argument("--workers", type=int, default=4, help="parallel entry checks (default 4)")
    parser.add_argument("--gap", type=float, default=0.45, help="global seconds between request starts")
    args = parser.parse_args()
    global _REQUEST_GAP
    _REQUEST_GAP = args.gap

    data = load_snapshot()
    overlay = json.load(open(os.path.join(ROOT, "tools", "overlay.json"), encoding="utf-8"))
    accepted = {k: v for k, v in overlay.get("acceptedDescriptionExceptions", {}).items()
                if not k.startswith("__")}

    sites = [s for s in data["sites"] if not args.repo or s["repo"] == args.repo]
    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print("provenance audit — re-resolving every published citation from api.github.com")
    print("snapshot %s · entries %d" % (data.get("generated"), len(sites)))
    print("This re-opens the sources the record cites; it does not establish that prose is current at head.")
    print("-" * 118)

    rows, all_findings, all_checks, incomplete = [], [], [], False

    def run(site):
        if API_FAILURE:  # a worker saw an access block: stop issuing requests
            return site, None, [], []
        result, findings, checks = audit_entry(site, accepted, None)
        return site, result, findings, checks

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        for site, result, findings, checks in pool.map(run, sites):
            if API_FAILURE and result is None:
                incomplete = True
                print("  ACCESS-BLOCKED at %s: %s" % (site["repo"], API_FAILURE))
                pool.shutdown(wait=False, cancel_futures=True)
                break
            all_checks.extend(checks)
            rows.append(result)
            for what, detail, url in findings:
                all_findings.append({"repo": site["repo"], "finding": what, "detail": detail, "source": url})
            flag = "FAIL" if findings else "ok  "
            print("  %s %-34s stamp=%-10s citations=%2d  %s"
                  % (flag, site["repo"], (result["stamp"] or "-")[:10], result["citationsChecked"],
                     result["readmeTokens"] or "-"))
            for what, detail, url in findings:
                print("       ↳ %s %s" % (what, ("[%s]" % detail) if detail else ""))
                if url:
                    print("         %s" % url)
    if API_FAILURE:
        incomplete = True

    complete = (len(rows) == len(sites)) and not incomplete
    print("-" * 118)
    print("entries audited: %d / %d%s" % (len(rows), len(sites), "" if complete else "  (INCOMPLETE — ACCESS BLOCK, NOT A PASS)"))
    print("reproduced checks: %d · hard findings: %d" % (len(all_checks), len(all_findings)))
    for finding in all_findings:
        print("  %-34s %s %s" % (finding["repo"], finding["finding"], ("[%s]" % finding["detail"]) if finding["detail"] else ""))

    artifact = {
        "tool": "tools/audit_provenance.py",
        "startedAt": started,
        "finishedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "snapshotGenerated": data.get("generated"),
        "entriesAudited": len(rows),
        "entriesTotal": len(sites),
        "complete": complete,
        "accessBlocked": incomplete,
        "accessBlockReason": API_FAILURE,
        "checksPerformed": len(all_checks),
        "documentedNegativeCitations": sum(len(row.get("negativeCitations") or []) for row in rows),
        "templateCitations": [{"repo": row["repo"], **t}
                              for row in rows for t in (row.get("templateCitations") or [])],
        "entriesWithDocumentedNegativeCitation": sorted(
            row["repo"] for row in rows if row.get("negativeCitations")),
        "findings": all_findings,
        "acceptedDescriptionExceptions": sorted(accepted),
        "entries": rows,
        "caveat": ("Citations are re-opened mechanically at the SHA the record names. This proves the cited "
                   "endpoints reproduce; it does not prove the prose is accurate or current, and it makes no "
                   "uptime, rendering or usage claim."),
    }
    spot_check = bool(args.repo) and not args.force_artifacts
    if spot_check:
        print("spot check (--repo): canonical artifacts NOT written — a partial run must never look like a full pass")
    else:
        out = os.path.join(ROOT, "tools", "last_provenance_audit.json")
        json.dump(artifact, open(out, "w", encoding="utf-8"), indent=2)
        print("wrote %s" % os.path.relpath(out, ROOT))
        if complete and not args.no_report:
            _write_report(artifact, all_checks)
    if incomplete:
        return 2
    return 1 if all_findings else 0


def _write_report(artifact, checks):
    os.makedirs(REPORTS, exist_ok=True)
    # Same naming convention as reports/landing-pages/ and reports/pages-smoke/:
    # 2026-10-11T160100Z.md
    stamp = artifact["startedAt"].replace(":", "")
    path = os.path.join(REPORTS, "%s.md" % stamp)
    lines = [
        "# Provenance reproducibility audit — %s" % artifact["startedAt"],
        "",
        "Generated by `tools/audit_provenance.py` against the published snapshot `%s`." % artifact["snapshotGenerated"],
        "Read-only: it re-issues the official API URLs each record cites and reports what came back.",
        "",
        "- Entries audited: **%d / %d**%s" % (artifact["entriesAudited"], artifact["entriesTotal"],
                                              "" if artifact["complete"] else " — **INCOMPLETE (access block)**"),
        "- Checks issued: **%d**" % artifact["checksPerformed"],
        "- Hard findings: **%d**" % len(artifact["findings"]),
        "",
        "## What was checked, per entry",
        "",
        "| Repository | Kind | Provenance SHA | SHA resolves | Citations re-issued | Readme numbers at that SHA |",
        "|---|---|---|---|---|---|",
    ]
    for row in artifact["entries"]:
        lines.append("| [`%s`](https://github.com/%s/%s) | %s | `%s` | %s | %d | %s |" % (
            row["repo"], OWNER, row["repo"], row["kind"] or "-", (row["stamp"] or "-")[:10],
            "yes" if row["stampsResolved"].get("verifiedAtSha") else "**no**",
            row["citationsChecked"], row["readmeTokens"] or "-"))
    lines += ["", "## Template citations (a recipe, not an openable endpoint)", ""]
    if artifact["templateCitations"]:
        lines += ["| Repository | Citation | Live status |",
                  "|---|---|---|"]
        for row in artifact["templateCitations"]:
            lines.append("| `%s` | `%s` | HTTP %s |" % (row["repo"], row["endpoint"], row["status"]))
        lines.append("")
        lines.append("These records close their basis with a `Reproduce:` line whose URL contains a `{path}` "
                     "placeholder. The literal string is not openable by a reviewer (the API answers 404), so the "
                     "five entries are registered for review in `FLAGGED.md` (`FL-18`); the surrounding sentences do "
                     "name concrete files. This audit does not rewrite prose.")
    else:
        lines.append("None: every citation is a concrete URL.")
    lines += ["", "## Findings", ""]
    if artifact["findings"]:
        lines += ["| Repository | Finding | Detail | Hand-review source |", "|---|---|---|---|"]
        for finding in artifact["findings"]:
            lines.append("| `%s` | %s | %s | %s |" % (
                finding["repo"], finding["finding"], finding["detail"] or "—", finding["source"] or "—"))
    else:
        lines.append("None: every recorded provenance SHA resolved to a real commit and every cited source "
                     "reproduced as described.")
    lines += [
        "",
        "## Limits (stated, not implied)",
        "",
        "- Reproducing a citation is not the same as verifying a sentence. This audit proves that the source the "
        "record names still answers at the SHA the record names; semantic accuracy, currency at head, uptime, "
        "rendering and usage remain outside it (`FL-01`, `FL-02`, `FL-10`).",
        "- Numeric-token matching is a lint, matching `tools/audit_descriptions.py`, not a meaning check.",
        "- An access block (401/403/transport failure) aborts the run and is reported as INCOMPLETE, never as a pass.",
        "",
        "## Reproduce",
        "",
        "```bash",
        "python3 tools/audit_provenance.py",
        "```",
        "",
    ]
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    print("wrote %s" % os.path.relpath(path, ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
