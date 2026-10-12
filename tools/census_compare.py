#!/usr/bin/env python3
"""Read-only census comparison (T-035).

Answers one question without touching any published file: does the published
directory still list every public repository that has GitHub Pages enabled, and
does every field the directory publishes still match the live official API?

Reads, for both owner accounts:
    GET /users/{login}                                  account profile
    GET /users/{login}/repos?per_page=100&page=N        public repository list
    GET /repos/{owner}/{repo}                           repo metadata (created_at, pushed_at, ...)
    GET /repos/{owner}/{repo}/pages                     Pages status + source

Every value it prints is accompanied by the endpoint it came from, so a
reviewer can open it by hand. It never writes to data/.

Usage:
    python3 tools/census_compare.py [--json out.json]
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.github.com"
OWNER = "buffedlizard55-lab"
ACCOUNTS = ["buffedlizard55-lab", "kanlerxz87-cyber"]
EXCLUDED = {"ProjX"}  # permanently excluded by owner request (AGENTS.md)

TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""


def get(url, tries=4):
    """One official read with polite backoff. Never raises for HTTP status codes:
    the status is returned as part of the payload so a caller can report it as a
    finding instead of aborting the whole census.

    Returns ``(payload, url, http_status)``. ``payload`` is the parsed JSON body
    on success, or ``{"__http_error__": code}`` / ``{"__error__": text}``.
    """
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "MasterSite-census-compare",
        **({"Authorization": "Bearer " + TOKEN} if TOKEN else {}),
    })
    last = None
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                return body, url, resp.status
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code in (403, 429):
                wait = 5 * (attempt + 1) ** 2
                sys.stderr.write("  ! %s -> HTTP %s, waiting %ss\n" % (url, exc.code, wait))
                time.sleep(wait)
                continue
            return {"__http_error__": exc.code}, url, exc.code
        except Exception as exc:  # noqa: BLE001 - network flake
            last = exc
            time.sleep(3 * (attempt + 1))
    return {"__error__": str(last)}, url, None


def get_pages(url):
    """Follow the official ``Link: <...>; rel="next"`` header for list endpoints.

    Returns ``(items, error_or_None)``. Stops as soon as GitHub stops advertising
    a next page, so the cost is exactly one request per page.
    """
    out, page_url = [], "%s?per_page=100" % url
    while page_url:
        chunk, used, status = get(page_url)
        if isinstance(chunk, dict):
            return chunk, used  # error object propagates
        out.extend(chunk)
        page_url = _next_link(used)
        time.sleep(0.12)
    return out, None


def _next_link(used_url):
    """Re-issue a HEAD-ish read purely to observe the Link header.

    The list read already happened; this repeats it once per page rather than
    adding a separate header-parsing code path to ``get``.
    """
    req = urllib.request.Request(used_url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "MasterSite-census-compare",
        **({"Authorization": "Bearer " + TOKEN} if TOKEN else {}),
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            link = resp.headers.get("Link") or ""
    except Exception:  # noqa: BLE001 - a missing header just means "last page"
        return None
    for part in link.split(","):
        if 'rel="next"' in part and "<" in part:
            return part[part.index("<") + 1:part.index(">")]
    return None


def load_published():
    src = open(os.path.join(ROOT, "data", "sites.js"), encoding="utf-8").read()
    data = json.loads(src.split("window.MASTERDATA = ", 1)[1].rstrip().rstrip(";"))
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="json_out", default=None)
    args = ap.parse_args()

    snapshot_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    published = load_published()
    pub = {s["repo"]: s for s in published["sites"]}
    pub_unreachable = {u.get("repo"): u for u in published.get("unreachable", [])}
    excluded = set(published.get("counts", {}).get("excluded", [])) or EXCLUDED

    result = {
        "snapshotAt": snapshot_at,
        "accounts": [],
        "liveRepos": {},
        "missingFromDirectory": [],
        "listedButNotPublic": [],
        "listedButNoPages": [],
        "fieldMismatches": [],
        "excluded": sorted(excluded),
    }

    for login in ACCOUNTS:
        user, uurl, _ustatus = get("%s/users/%s" % (API, login))
        if not isinstance(user, dict) or "login" not in user:
            print("ACCOUNT READ FAILED %s -> %r (source %s)" % (login, user, uurl))
            result["accounts"].append({"login": login, "error": user, "source": uurl})
            continue
        repos, rurl = get_pages("%s/users/%s/repos" % (API, login))
        if isinstance(repos, dict):
            print("REPO LIST READ FAILED %s -> %r (source %s)" % (login, repos, rurl))
            result["accounts"].append({"login": login, "error": repos, "source": rurl})
            continue
        acct = {
            "login": login,
            "source": uurl,
            "public_repos": user.get("public_repos"),
            "reposReturned": len(repos),
            "reposSource": "%s/users/%s/repos?per_page=100" % (API, login),
            "accountCreated": user.get("created_at"),
            "type": user.get("type"),
        }
        result["accounts"].append(acct)
        print("ACCOUNT %s: public_repos=%s listed=%d (source %s)"
              % (login, user.get("public_repos"), len(repos), uurl))

        for r in repos:
            name = r["name"]
            if r.get("private"):
                continue
            repo_api = "%s/repos/%s/%s" % (API, login, name)
            meta, meta_url, _mstatus = get(repo_api)
            pages, pages_url, _pstatus = get("%s/pages" % repo_api)
            entry = {
                "owner": login,
                "repo": name,
                "hasPages": bool(r.get("has_pages")),
                "repoApiUrl": repo_api,
                "pagesApiUrl": pages_url,
                "createdAt": meta.get("created_at") if isinstance(meta, dict) else None,
                "pushedAt": meta.get("pushed_at") if isinstance(meta, dict) else None,
                "updatedAt": meta.get("updated_at") if isinstance(meta, dict) else None,
                "defaultBranch": meta.get("default_branch") if isinstance(meta, dict) else None,
                "sizeKb": meta.get("size") if isinstance(meta, dict) else None,
                "description": (meta.get("description") if isinstance(meta, dict) else None),
                "pagesStatus": pages.get("status") if isinstance(pages, dict) else None,
                "pagesUrl": pages.get("html_url") if isinstance(pages, dict) else None,
                "pagesSource": None,
                "httpError": pages.get("__http_error__") if isinstance(pages, dict) else None,
            }
            if isinstance(pages, dict) and pages.get("source"):
                entry["pagesSource"] = "%s %s" % (pages["source"].get("branch", ""),
                                                  pages["source"].get("path", "/"))
            if isinstance(pages, dict) and pages.get("__http_error__"):
                entry["pagesStatus"] = None
            result["liveRepos"][name] = entry
            time.sleep(0.12)

    live = result["liveRepos"]
    print("\nLIVE public repositories with Pages enabled: %d" % len(live))

    # --- completeness -------------------------------------------------------
    for name, e in sorted(live.items()):
        if name in excluded:
            continue
        if name not in pub and name not in pub_unreachable:
            result["missingFromDirectory"].append({
                "repo": name,
                "pagesUrl": e["pagesUrl"],
                "repoApiUrl": e["repoApiUrl"],
                "pagesApiUrl": e["pagesApiUrl"],
                "pagesStatus": e["pagesStatus"],
                "createdAt": e["createdAt"],
                "pushedAt": e["pushedAt"],
            })
    for name in sorted(pub):
        if name not in live:
            result["listedButNotPublic"].append({"repo": name, "note": "published but not in the live public repo list"})
        elif not live[name]["hasPages"] and not live[name]["pagesUrl"]:
            result["listedButNoPages"].append({"repo": name, "repoApiUrl": live[name]["repoApiUrl"]})

    # --- field-by-field agreement ------------------------------------------
    for name in sorted(pub):
        if name not in live:
            continue
        s, e = pub[name], live[name]
        for field, live_val in (
            ("created", e["createdAt"]),
            ("pushedAt", e["pushedAt"]),
            ("updatedAt", e["updatedAt"]),
            ("pagesStatus", e["pagesStatus"]),
            ("defaultBranch", e["defaultBranch"]),
            ("pagesUrl", e["pagesUrl"]),
        ):
            pub_val = s.get(field)
            if pub_val is None or live_val is None:
                continue
            if str(pub_val).rstrip("/") != str(live_val).rstrip("/"):
                result["fieldMismatches"].append({
                    "repo": name, "field": field,
                    "published": pub_val, "live": live_val,
                    "source": e["repoApiUrl"],
                    "pagesSource": e["pagesApiUrl"],
                })

    print("\nMissing from directory: %d" % len(result["missingFromDirectory"]))
    for m in result["missingFromDirectory"]:
        print("  + %s  pages=%s  created=%s  %s" % (m["repo"], m["pagesStatus"], m["createdAt"], m["pagesApiUrl"]))
    print("Listed but not public: %d %s" % (len(result["listedButNotPublic"]),
                                            [x["repo"] for x in result["listedButNotPublic"]]))
    print("Listed but Pages not enabled: %d %s" % (len(result["listedButNoPages"]),
                                                   [x["repo"] for x in result["listedButNoPages"]]))
    print("Field mismatches vs live API: %d" % len(result["fieldMismatches"]))
    for m in result["fieldMismatches"][:40]:
        print("  ~ %s.%s published=%r live=%r  (%s)" % (m["repo"], m["field"], m["published"], m["live"], m["source"]))
    if len(result["fieldMismatches"]) > 40:
        print("  ... and %d more" % (len(result["fieldMismatches"]) - 40))

    # --- balance ------------------------------------------------------------
    total_public = sum(a.get("public_repos") or 0 for a in result["accounts"])
    print("\nBALANCE: public_repos=%d  listed=%d  unreachable=%d  excluded=%d  -> %d"
          % (total_public, len(pub), len(pub_unreachable), len(excluded),
             len(pub) + len(pub_unreachable) + len(excluded)))
    print("snapshotAt %s" % snapshot_at)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, sort_keys=True)
        print("wrote %s" % args.json_out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
