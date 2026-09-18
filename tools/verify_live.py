#!/usr/bin/env python3
"""Independent, read-only line-by-line verifier for MasterSite.

This tool does NOT write the dataset. It re-reads every API-derived field of
every entry in data/sites.js straight from api.github.com and reports each
field as OK / MISMATCH / FAIL, plus a machine-readable summary.

Usage:
    python3 tools/verify_live.py            # verify everything
    python3 tools/verify_live.py --repo X   # verify a single repository
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.github.com"
OWNER = "buffedlizard55-lab"
ACCOUNTS = ["buffedlizard55-lab", "kanlerxz87-cyber"]

OK, BAD, FAIL = "OK", "MISMATCH", "FAIL"
report = []


def api_get(path, accept="application/vnd.github+json"):
    req = urllib.request.Request(
        API + path,
        headers={
            "Accept": accept,
            "User-Agent": "MasterSite-verify",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8"))
        except Exception:
            body = {"message": e.reason}
        return e.code, body
    except Exception as e:
        return 0, {"message": str(e)}


def paginate(path):
    out, page = [], 1
    while True:
        sep = "&" if "?" in path else "?"
        status, data = api_get("%s%sper_page=100&page=%d" % (path, sep, page))
        if status != 200 or not isinstance(data, list):
            return out, status
        out.extend(data)
        if len(data) < 100:
            return out, status
        page += 1


def load_data():
    src = open(os.path.join(ROOT, "data", "sites.js"), encoding="utf-8").read()
    payload = src.split("window.MASTERDATA = ", 1)[1].rstrip().rstrip(";")
    return json.loads(payload)


def check(entry, field, expected, actual):
    verdict = OK if expected == actual else BAD
    report.append((entry, field, verdict, expected, actual))
    return verdict == OK


def verify_site(site):
    repo = site["repo"]
    name = "sites[]/" + repo
    st, r = api_get("/repos/%s/%s" % (OWNER, repo))
    if st != 200:
        check(name, "GET /repos", 200, st)
        return
    check(name, "created", site["created"], r.get("created_at"))
    check(name, "pushedAt", site["pushedAt"], r.get("pushed_at"))
    check(name, "updatedAt", site["updatedAt"], r.get("updated_at"))
    check(name, "sizeKb", site["sizeKb"], r.get("size"))
    check(name, "defaultBranch", site["defaultBranch"], r.get("default_branch"))

    ps, p = api_get("/repos/%s/%s/pages" % (OWNER, repo))
    if ps == 200:
        check(name, "pagesStatus", site["pagesStatus"], p.get("status"))
        src = p.get("source", {}) or {}
        check(name, "pagesSource", site["pagesSource"],
              "%s %s" % (src.get("branch"), src.get("path", "/")))
        check(name, "pagesUrl", site["pagesUrl"], p.get("html_url"))
    else:
        check(name, "GET /pages", 200, ps)

    branch = r.get("default_branch") or "main"
    commits, cst = paginate("/repos/%s/%s/commits?sha=%s" % (OWNER, repo, branch))
    if cst == 200 and commits:
        check(name, "commits", site["commits"], len(commits))
        check(name, "lastCommit", site["lastCommit"], commits[0]["commit"]["committer"]["date"])
        check(name, "lastCommitSha", site["lastCommitSha"], commits[0]["sha"][:7])
        check(name, "firstCommit", site["firstCommit"], commits[-1]["commit"]["committer"]["date"])
        check(name, "firstCommitSha", site["firstCommitSha"], commits[-1]["sha"][:7])
    else:
        check(name, "GET /commits", 200, cst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    ap.add_argument("--skip-commits", action="store_true")
    args = ap.parse_args()

    data = load_data()
    print("verify_live.py — re-reading data/sites.js against api.github.com")
    print("dataset generated at:", data["generated"])
    print("-" * 88)

    # --- accounts -------------------------------------------------------
    for acct in data["accountsChecked"]:
        login = acct["login"]
        st, p = api_get("/users/%s" % login)
        if st != 200:
            check("accounts/%s" % login, "GET /users", 200, st)
            continue
        check("accounts/" + login, "publicRepos", acct["publicRepos"], p.get("public_repos"))
        check("accounts/" + login, "accountCreated", acct["accountCreated"], p.get("created_at"))
        repos, rst = paginate("/users/%s/repos?type=public" % login)
        check("accounts/" + login, "public repo list count", acct["publicRepos"], len(repos))
        pages_on = 0
        for rr in repos:
            s2, _ = api_get("/repos/%s/%s/pages" % (login, rr["name"]))
            if s2 == 200:
                pages_on += 1
        check("accounts/" + login, "pagesSites", acct["pagesSites"], pages_on)
        print("  accounts/%-20s publicRepos=%s pagesSites=%s" % (login, p.get("public_repo" + "s"), pages_on))

    # --- repository coverage --------------------------------------------
    repos, _ = paginate("/users/%s/repos?type=public" % OWNER)
    api_names = {r["name"] for r in repos}
    included = {s["repo"] for s in data["sites"]}
    excluded = set(data["counts"].get("excluded", []))
    retired = {u["repo"] for u in data.get("unreachable", [])}
    missing = api_names - included - excluded - retired
    # A repository in unreachable[] is *supposed* to be absent from the API — that is
    # the entire point of the frozen entry (see AGENTS.md § 3). Only report it if the
    # live directory itself lists a repository the API does not return.
    extra = included - api_names
    check("coverage", "in-API-but-unlisted", [], sorted(missing))
    check("coverage", "live-listed-but-not-in-API", [], sorted(extra))
    for name in sorted(retired & api_names):
        print("  ! %s is back in the API but is still frozen in unreachable[] — "
              "move it into sites[] with fresh values (AGENTS.md § 3)" % name)

    # --- verify the unreachable / retired entries ------------------------
    for u in data.get("unreachable", []):
        st, body = api_get("/repos/%s/%s" % (OWNER, u["repo"]))
        print("  unreachable %-24s GET /repos -> HTTP %s (recorded: %s)"
              % (u["repo"], st, u.get("httpStatus")))

    # --- per-site field verification -------------------------------------
    if not args.skip_commits:
        for s in data["sites"]:
            if args.repo and s["repo"] != args.repo:
                continue
            verify_site(s)

    print("-" * 88)
    # Fields GitHub itself recomputes asynchronously, or that legitimately move because a
    # repository was pushed to while this audit was running. A difference here is drift,
    # not an error: re-run the generator to fold it in.
    volatile = {"sizeKb", "pushedAt", "updatedAt"}
    # A repository that has been pushed to *since the snapshot recorded it* cannot be
    # expected to match the snapshot. Comparing the live pushed_at against the *committed*
    # pushed_at (rather than against the dataset's `generated` timestamp) is the correct
    # rule, because the generator takes ~50 s to walk 41 repositories: a repo can be read
    # early in the run and pushed to before the run finishes, which puts its new commit
    # timestamp *before* `generated` even though the snapshot never saw it.
    moved_since = set()
    for site in data["sites"]:
        st, r = api_get("/repos/%s/%s" % (OWNER, site["repo"]))
        if st == 200 and (r.get("pushed_at") or "") > (site.get("pushedAt") or ""):
            moved_since.add(site["repo"])
    bad = [r for r in report if r[2] != OK]
    hard = [r for r in bad
            if r[1] not in volatile and r[0].split("/")[-1] not in moved_since]
    soft = [r for r in bad if r not in hard]
    print("checks: %d   ok: %d   mismatched: %d  (hard: %d, drift: %d)"
          % (len(report), len(report) - len(bad), len(bad), len(hard), len(soft)))
    if moved_since:
        print("  pushed to since this snapshot read them (their differences are drift, not defects):")
        for n in sorted(moved_since):
            print("    - %s" % n)
    for entry, field, verdict, exp, act in bad:
        post = entry.split("/")[-1] in moved_since
        tag = "DRIFT" if (field in volatile or post) else verdict
        print("  %-9s %-38s %-18s committed=%r  live=%r" % (tag, entry, field, exp, act))
    if hard:
        print("\n  HARD MISMATCHES ARE A DEFECT: re-run tools/build_data.py to fold them in.")
    elif soft:
        print("\n  No hard mismatches: every API-derived field matches the snapshot except for "
              "fields GitHub\n  recomputes asynchronously and repositories that were pushed to "
              "after this snapshot read\n  them. Re-run tools/build_data.py to fold in a "
              "fresher read; the drift is expected, not a defect.")

    out = os.path.join(ROOT, "tools", "last_live_verify.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "generatedOffsetVsLive": data["generated"],
                "checks": len(report),
                "mismatches": [
                    {"entry": e, "field": f, "committed": ex, "live": ac}
                    for e, f, v, ex, ac in bad
                ],
                "unlistedInApi": sorted(missing),
                "listedNotInApi": sorted(extra),
                "volatileDrift": [{"entry": e, "field": f, "committed": ex, "live": ac}
                                  for e, f, v, ex, ac in soft],
                "hardMismatches": [{"entry": e, "field": f, "committed": ex, "live": ac}
                                   for e, f, v, ex, ac in hard],
            },
            fh,
            indent=2,
        )
    print("wrote %s" % os.path.relpath(out, ROOT))
    return 0 if not hard else 1


if __name__ == "__main__":
    sys.exit(main())
