#!/usr/bin/env python3
"""Read-only audit of the curated `kind` field in tools/overlay.json.

The data schema keeps the legacy values `app` and `stub`: `app` means an
index.html exists at the configured published path, while `stub` means it does
not. This check does not claim an HTML page is interactive or that the live URL
responds. The user-facing UI calls these HTML-entry-point sites and
README/documentation stubs.

This script re-derives the classification for every entry from the official
Pages and contents APIs and reports disagreements. It writes nothing except a
report.
"""
import json
import os
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.github.com"
OWNER = "buffedlizard55-lab"


def api_get(path, accept="application/vnd.github+json"):
    req = urllib.request.Request(API + path, headers={
        "Accept": accept, "User-Agent": "MasterSite-kind-audit",
        "X-GitHub-Api-Version": "2022-11-28"})
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if tok:
        req.add_header("Authorization", "Bearer " + tok)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8", "replace")
            try:
                return r.status, json.loads(raw)
            except json.JSONDecodeError:
                return r.status, raw
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8", "replace"))
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"message": str(e)}


def main():
    ov = json.load(open(os.path.join(ROOT, "tools", "overlay.json"), encoding="utf-8"))
    entries = ov["entries"]
    src = open(os.path.join(ROOT, "data", "sites.js"), encoding="utf-8").read()
    snapshot = json.loads(src.split("window.MASTERDATA = ", 1)[1].rstrip().rstrip(";"))
    snapshot_generated = snapshot.get("generated")
    print("kind audit — re-deriving 'app' vs 'stub' from the published path for all %d entries"
          % len(entries))
    print("-" * 96)
    disagreements, unresolved_details, derived, checked = [], [], 0, 0
    for repo in sorted(entries, key=str.lower):
        e = entries[repo]
        hardcoded = e.get("kind")
        st, pg = api_get("/repos/%s/%s/pages" % (OWNER, repo))
        if st != 200:
            message = pg.get("message") if isinstance(pg, dict) else str(pg)
            unresolved_details.append({"repo": repo, "field": "pages", "status": st,
                                       "message": message})
            print("  UNKNOWN  %-34s pages endpoint HTTP %s — cannot derive" % (repo, st))
            if st == 401 or (st == 403 and "rate limit" in (message or "").lower()):
                print("  stopping after the first API access error; the remaining entries were not checked")
                break
            continue
        src = pg.get("source", {}) or {}
        branch = src.get("branch") or "main"
        sub = src.get("path", "/")
        sub = "" if sub in ("/", "") else "/" + sub.strip("/")
        endpoint = "/repos/%s/%s/contents%s/index.html?ref=%s" % (OWNER, repo, sub, branch)
        ist, ibody = api_get(endpoint, accept="application/vnd.github.raw")
        if ist not in (200, 404):
            unresolved_details.append({"repo": repo, "field": "configured-path index.html",
                                       "status": ist, "pagesStatus": pg.get("status"),
                                       "source": "%s %s" % (branch, sub or "/")})
            print("  UNKNOWN  %-34s pages=%-7s source=%-12s configured-path index.html HTTP %s"
                  % (repo, pg.get("status"), "%s %s" % (branch, sub or "/"), ist))
            imessage = ibody.get("message", "") if isinstance(ibody, dict) else str(ibody)
            if ist == 401 or (ist == 403 and "rate limit" in imessage.lower()):
                print("  stopping after the first API access error; the remaining entries were not checked")
                break
            continue
        live = "app" if ist == 200 else "stub"
        checked += 1
        display_path = "%s %s" % (branch, sub or "/")
        file_path = (sub.rstrip("/") + "/" if sub else "/") + "index.html"
        if hardcoded is None:
            derived += 1
            tag, note = "DERIVED", "overlay has no `kind`; build_data.py will derive '%s'" % live
        elif hardcoded == live:
            tag, note = "ok", "published path `%s` -> HTTP %s" % (file_path, ist)
        else:
            tag, note = "MISMATCH", "overlay says '%s' but `%s` -> HTTP %s (derived '%s')" % (
                hardcoded, file_path, ist, live)
            disagreements.append((repo, hardcoded, live, ist, display_path))
        print("  %-8s %-34s pages=%-7s source=%-12s %s" % (tag, repo, pg.get("status"),
                                                            display_path, note))
    print("-" * 96)
    complete = checked == len(entries) and not unresolved_details
    print("checked: %d / %d   derived (no hardcoded kind): %d   disagreements: %d   unresolved: %d%s"
          % (checked, len(entries), derived, len(disagreements), len(unresolved_details),
             "" if complete else " (INCOMPLETE)"))
    for repo, hc, live, code, path in disagreements:
        print("  %-34s overlay='%s' live='%s' (%s/index.html HTTP %s)" % (repo, hc, live, path, code))
    out = os.path.join(ROOT, "tools", "last_kind_audit.json")
    json.dump({
        "snapshotGenerated": snapshot_generated,
        "totalEntries": len(entries),
        "checkedEntries": checked,
        "derivedEntries": derived,
        "complete": complete,
        "disagreements": [
            {"repo": repo, "overlayKind": hardcoded, "derivedKind": live,
             "httpStatus": code, "pagesSource": path}
            for repo, hardcoded, live, code, path in disagreements
        ],
        "unresolved": unresolved_details
    }, open(out, "w", encoding="utf-8"), indent=2)
    print("wrote %s" % os.path.relpath(out, ROOT))
    return 1 if disagreements or unresolved_details else 0


if __name__ == "__main__":
    raise SystemExit(main())
