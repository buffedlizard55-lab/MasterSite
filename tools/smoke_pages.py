#!/usr/bin/env python3
"""Observe published Pages URLs, separately from the generated API snapshot.

No GitHub token is sent, no source records are changed, and no JavaScript is
executed. A 2xx HTML response with a title is a point-in-time HTTP observation,
not evidence of uptime, app functionality, source accuracy, or last use.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from http.client import HTTPException
import json
from pathlib import Path
import re
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OWNERS = {"buffedlizard55-lab", "kanlerxz87-cyber"}
MAX_BODY = 2 * 1024 * 1024


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.inside = False
        self.finished = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "title" and not self.finished:
            self.inside = True

    def handle_endtag(self, tag):
        if tag == "title" and self.inside:
            self.inside = False
            self.finished = True

    def handle_data(self, data):
        if self.inside:
            self.parts.append(data)

    def title(self):
        # An incomplete title is not a verified title, even if some bytes arrived.
        if not self.finished:
            return None
        return " ".join("".join(self.parts).split()) or None


def safe_url(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Only credential-free HTTPS URLs can be observed")
    return url


class HTTPSRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        safe_url(newurl)
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        return redirected


def load_records(directory):
    records, seen = [], set()
    for path in sorted(directory.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        owner, repo = record["owner"], record["repo"]
        url = safe_url(record["pagesUrl"])
        if owner not in OWNERS or not re.fullmatch(r"[A-Za-z0-9_.-]+", repo):
            raise ValueError("Unsupported owner or repository in %s" % path.name)
        if path.name != "%s__%s.json" % (owner, repo):
            raise ValueError("Record filename disagrees with owner/repo: %s" % path.name)
        if urllib.parse.urlsplit(url).hostname != owner.lower() + ".github.io":
            raise ValueError("Not the owner's official Pages host in %s" % path.name)
        if (owner, repo) in seen:
            raise ValueError("Duplicate owner/repo")
        seen.add((owner, repo))
        records.append(record)
    if not records:
        raise ValueError("No published site records found; refusing an empty successful audit")
    return records


def fetch(url, timeout):
    request = urllib.request.Request(safe_url(url), headers={
        "User-Agent": "MasterSite-Pages-smoke/1.0",
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.1",
    })
    opener = urllib.request.build_opener(HTTPSRedirects())
    try:
        response = opener.open(request, timeout=timeout)
    except urllib.error.HTTPError as error:
        # An HTTP failure is still a response with an exact status and source URL.
        response = error
    with response:
        observed = {
            "status": response.code,
            "finalUrl": response.geturl(),
            "contentType": response.headers.get_content_type(),
            "charset": response.headers.get_content_charset() or "utf-8",
            "body": b"", "readError": None,
        }
        try:
            observed["body"] = response.read(MAX_BODY + 1)
        except (OSError, ValueError, HTTPException) as error:
            observed["readError"] = "%s: %s" % (type(error).__name__, error)
        return observed


def observe(record, timeout=15, fetcher=fetch):
    result = {
        "owner": record["owner"], "repo": record["repo"],
        "sourceUrl": record["pagesUrl"],
        "recordSnapshot": record.get("snapshot"),
        "pagesApiStatusAtSnapshot": record.get("pagesStatus"),
        "startedAt": utc_now(), "checkedAt": None,
        "httpStatus": None, "finalUrl": None, "contentType": None,
        "title": None, "bodyTruncated": None, "outcome": None,
        "unverifiedFields": [], "reason": None,
    }
    started = time.monotonic()
    try:
        response = fetcher(result["sourceUrl"], timeout)
        result.update(httpStatus=response["status"], finalUrl=response["finalUrl"],
                      contentType=response["contentType"],
                      bodyTruncated=len(response["body"]) > MAX_BODY)
        html = response["contentType"] in ("text/html", "application/xhtml+xml")
        if html:
            parser = TitleParser()
            parser.feed(response["body"][:MAX_BODY].decode(response["charset"], errors="replace"))
            result["title"] = parser.title()
        if response.get("readError"):
            result.update(outcome="review", reason="Response headers observed, body read failed: " + response["readError"])
        elif not 200 <= response["status"] < 300:
            result.update(outcome="http-error", reason="Final HTTP response is not 2xx")
        elif not html or not result["title"]:
            result.update(outcome="review", reason="No complete HTML title observed; not evidence the site is down")
        else:
            result["outcome"] = "ok"
        if result["title"] is None:
            result["unverifiedFields"].append("title")
    except (urllib.error.URLError, OSError, ValueError, LookupError, socket.timeout, ssl.SSLError, HTTPException) as error:
        result.update(outcome="transport-error" if result["httpStatus"] is None else "review",
                      reason="%s: %s" % (type(error).__name__, str(error)),
                      unverifiedFields=[key for key in ("httpStatus", "finalUrl", "contentType", "title")
                                        if result[key] is None])
    result["checkedAt"] = utc_now()
    result["elapsedSeconds"] = round(time.monotonic() - started, 3)
    return result


def make_report(records, observations, started, revision=None, run_url=None):
    counts = {key: sum(row["outcome"] == key for row in observations)
              for key in ("ok", "http-error", "transport-error", "review")}
    return {
        "schemaVersion": 1, "startedAt": started, "completedAt": utc_now(),
        "revision": revision, "runUrl": run_url,
        "recordSnapshots": sorted({r["snapshot"] for r in records if r.get("snapshot")}),
        "counts": {"total": len(observations), **counts},
        "limitations": "One GET per published URL; no JS or meta-refresh execution, no retries, "
                        "at most 2 MiB of response body. Status and title are observations, not uptime, "
                        "rendering, functionality, description verification, or last-use evidence. "
                        "Transport failures do not establish that a site is down. Frozen and excluded "
                        "repositories are not in this audit. Pages API status is unchanged snapshot metadata.",
        "observations": observations,
    }


def cell(value):
    if value is None:
        return "null"
    # Remote titles are untrusted text: escape Markdown, HTML, and line breaks.
    text = " ".join(str(value).split())
    if len(text) > 800:
        text = text[:800] + " … (display truncated; full value in report.json)"
    return "".join("&#%d;" % ord(c) if c in "&<>|`[]!*_\\" else c for c in text)


def markdown(report, only_flagged=False):
    counts = report["counts"]
    lines = ["# Live Pages HTTP smoke audit", "",
             "Completed: `%s` (UTC). Source revision: `%s`." % (report["completedAt"], report["revision"]),
             "", "Observed **%d** published URLs: **%d** 2xx HTML responses with titles, "
             "**%d** HTTP errors, **%d** transport errors, **%d** requiring review." %
             (counts["total"], counts["ok"], counts["http-error"], counts["transport-error"], counts["review"]),
             "", report["limitations"], ""]
    if only_flagged:
        lines += ["## Flagged observations (null fields were not guessed)", ""]
    lines += ["| Repository | Checked (UTC) | HTTP | Title | Outcome / reason | Exact requested source | Final response URL |",
              "|---|---|---|---|---|---|---|"]
    for row in report["observations"]:
        if only_flagged and row["outcome"] == "ok":
            continue
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % tuple(cell(v) for v in (
            row["owner"] + "/" + row["repo"], row["checkedAt"], row["httpStatus"], row["title"],
            row["outcome"] + (": " + row["reason"] if row["reason"] else ""),
            row["sourceUrl"], row["finalUrl"])))
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path, default=ROOT / "data" / "sites")
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".work" / "pages-smoke")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=15)
    parser.add_argument("--revision")
    parser.add_argument("--run-url")
    args = parser.parse_args()
    if not 1 <= args.workers <= 4 or not 0 < args.timeout <= 30:
        parser.error("workers must be 1–4 and timeout must be >0 and <=30 seconds")
    started = utc_now()
    try:
        records = load_records(args.records)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, "Input failure (not a successful URL audit): %s\n" % error)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        observations = list(pool.map(lambda r: observe(r, args.timeout), records))
    report = make_report(records, observations, started, args.revision, args.run_url)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n")
    (args.output_dir / "report.md").write_text(markdown(report), encoding="utf-8")
    (args.output_dir / "FLAGGED.md").write_text(markdown(report, only_flagged=True), encoding="utf-8")
    print(markdown(report))
    return 0 if report["counts"]["ok"] == len(records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
