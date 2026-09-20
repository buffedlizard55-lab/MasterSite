#!/usr/bin/env python3
"""Read-only audit of the hand-authored `kind` field in tools/overlay.json.

`kind` is defined by tools/build_data.py as: 'app' if an index.html really exists
at the *published path*, else 'stub' (the Pages build is only rendering the README
through Jekyll). 43 of 44 entries hardcode it in overlay.json, so the derivation
never runs for them and the value has never been independently re-checked.

This script re-derives it for every entry from the official API and reports any
disagreement. It writes nothing except a report.
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
    print("kind audit — re-deriving 'app' vs 'stub' from the published path for all %d entries"
          % len(entries))
    print("-" * 96)
    disagreements, derived, checked = [], 0, 0
    for repo in sorted(entries, key=str.lower):
        e = entries[repo]
        hardcoded = e.get("kind")
        st, pg = api_get("/repos/%s/%s/pages" % (OWNER, repo))
        if st != 200:
            print("  ??   %-34s pages endpoint HTTP %s — cannot derive" % (repo, st))
            continue
        src = pg.get("source", {}) or {}
        branch = src.get("branch") or "main"
        sub = src.get("path", "/")
        sub = "" if sub in ("/", "") else "/" + sub.strip("/")
        ist, _ = api_get("/repos/%s/%s/contents%s/index.html?ref=%s" % (OWNER, repo, sub, branch),
                         accept="application/vnd.github.raw")
        live = "app" if ist == 200 else "stub"
        checked += 1
        if hardcoded is None:
            derived += 1
            tag, note = "DERIVED", "overlay has no `kind`; build_data.py will derive '%s'" % live
        elif hardcoded == live:
            tag, note = "ok", "published path `%s%s/index.html` -> HTTP %s" % (branch, sub or "/", ist)
        else:
            tag, note = "MISMATCH", "overlay says '%s' but %s%s/index.html -> HTTP %s (derived '%s')" % (
                hardcoded, branch, sub or "/", ist, live)
            disagreements.append((repo, hardcoded, live, ist, "%s%s" % (branch, sub or "/")))
        print("  %-8s %-34s pages=%-7s source=%-12s %s" % (tag, repo, pg.get("status"),
                                                            "%s %s" % (branch, sub or "/"), note))
    print("-" * 96)
    print("checked: %d   derived (no hardcoded kind): %d   disagreements: %d"
          % (checked, derived, len(disagreements)))
    for repo, hc, live, code, path in disagreements:
        print("  %-34s overlay='%s' live='%s' (%s/index.html HTTP %s)" % (repo, hc, live, path, code))
    return 1 if disagreements else 0


if __name__ == "__main__":
    raise SystemExit(main())
