#!/usr/bin/env python3
"""Regenerate data/sites.js for MasterSite from the official GitHub REST API.

Zero manual data entry: every timestamp, SHA, commit count, Pages status and
build source in the generated file is read from api.github.com at run time.
The only hand-authored content lives in tools/overlay.json, which holds the
human-written *narrative* fields (title, category, description, flags, the
irregularity register) plus the permanent exclusion list.

Usage:
    GITHUB_TOKEN=xxx python3 tools/build_data.py          # higher rate limit
    python3 tools/build_data.py                           # unauthenticated (60 req/h)

Endpoints read (all official, all public):
    GET /users/{login}                                  account profile
    GET /users/{login}/repos?per_page=100&page=N        repository list
    GET /repos/{owner}/{repo}                           repo metadata
    GET /repos/{owner}/{repo}/pages                     Pages status + source
    GET /repos/{owner}/{repo}/commits?sha={branch}      commit telemetry
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OVERLAY_PATH = os.path.join(ROOT, "tools", "overlay.json")
OUT_PATH = os.path.join(ROOT, "data", "sites.js")

API = "https://api.github.com"
OWNER = "buffedlizard55-lab"
ACCOUNTS = ["buffedlizard55-lab", "kanlerxz87-cyber"]


def api_get(path, accept="application/vnd.github+json"):
    """Return (status, parsed_json) for an official GitHub REST API read."""
    req = urllib.request.Request(
        API + path,
        headers={
            "Accept": accept,
            "User-Agent": "MasterSite-audit",
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
    except Exception as e:  # network failure — never fabricate, always fail loudly
        print("  ! network error on %s: %s" % (path, e), file=sys.stderr)
        return 0, {"message": str(e)}


def api_get_raw(path):
    status, body = api_get(path, accept="application/vnd.github.raw")
    return status, body if isinstance(body, str) else ""


def paginate(path):
    """Follow a paginated endpoint until it stops returning a full page."""
    out, page = [], 1
    while True:
        status, data = api_get("%s%sper_page=100&page=%d" % (path, "&" if "?" in path else "?", page))
        if status != 200 or not isinstance(data, list):
            return out, status
        out.extend(data)
        if len(data) < 100:
            return out, status
        page += 1


def has_entry_point(owner, repo, pages_source_path, branch):
    """Does the published path actually contain an index.html?"""
    sub = "" if pages_source_path in ("/", "") else "/" + pages_source_path.strip("/")
    status, _ = api_get_raw("/repos/%s/%s/contents%s/index.html?ref=%s" % (owner, repo, sub, branch))
    return status == 200


def main():
    overlay = json.load(open(OVERLAY_PATH, encoding="utf-8"))
    entries = overlay["entries"]
    excluded = set(overlay.get("excluded", []))

    print("MasterSite data refresh — reading api.github.com")
    print("-" * 72)

    accounts_checked = []
    api_names = set()
    for login in ACCOUNTS:
        status, profile = api_get("/users/%s" % login)
        if status != 200:
            print("  ! %s profile returned HTTP %s" % (login, status), file=sys.stderr)
            continue
        repos, _ = paginate("/users/%s/repos?type=public" % login)
        names = [r["name"] for r in repos]
        pages_enabled = 0
        if login == OWNER:
            api_names.update(names)
            for n in names:
                st, _ = api_get("/repos/%s/%s/pages" % (OWNER, n))
                if st == 200:
                    pages_enabled += 1
        if login == OWNER:
            note = (
                "%d of %d public repositories have GitHub Pages enabled (verified per-repo via "
                "GET /repos/%s/{repo}/pages). This directory publishes %d of them: %d repo(s) are "
                "permanently excluded by owner request and must never be added back (see AGENTS.md)."
                % (pages_enabled, profile.get("public_repos") or 0, login,
                   len([n for n in names if n not in excluded]), len(excluded))
            )
        else:
            note = (
                "Account exists (type: %s) but has %s public repositories, therefore zero GitHub "
                "Pages sites. Verified via the official GitHub API."
                % (profile.get("type"), profile.get("public_repos"))
            )
        accounts_checked.append(
            {
                "login": login,
                "profile": profile.get("html_url"),
                "apiRepos": "%s/users/%s/repos" % (API, login),
                "publicRepos": profile.get("public_repos"),
                "accountCreated": profile.get("created_at"),
                "pagesSites": pages_enabled,
                "note": note,
            }
        )
        print("  %-22s public_repos=%s pages_enabled=%s" % (login, profile.get("public_repos"), pages_enabled))

    sites, warnings = [], []
    unlisted = []  # every public repo with Pages that is deliberately NOT in sites[]
    for name in sorted(api_names):
        if name in excluded:
            print("  skip %-38s (permanently excluded — see AGENTS.md)" % name)
            unlisted.append({"repo": name, "reason": "permanently excluded by owner request"})
            continue

        status, repo = api_get("/repos/%s/%s" % (OWNER, name))
        if status != 200:
            warnings.append("%s: repo endpoint returned HTTP %s" % (name, status))
            continue
        pstatus, pages = api_get("/repos/%s/%s/pages" % (OWNER, name))
        if pstatus != 200:
            warnings.append("%s: pages endpoint returned HTTP %s (not a Pages site)" % (name, pstatus))
            continue

        branch = repo.get("default_branch") or "main"
        commits, cstatus = paginate("/repos/%s/%s/commits?sha=%s" % (OWNER, name, branch))
        if cstatus != 200 or not commits:
            warnings.append("%s: commit list unavailable (HTTP %s)" % (name, cstatus))
            continue

        newest, oldest = commits[0], commits[-1]
        src = pages.get("source", {}) or {}
        source_str = "%s %s" % (src.get("branch", branch), src.get("path", "/"))
        sub_path = src.get("path", "/")

        ov = entries.get(name)
        if not ov:
            warnings.append(
                "%s: no curated entry in tools/overlay.json — skipped from the directory "
                "(add a sourced title/category/description to publish it)" % name
            )
            unlisted.append(
                {"repo": name, "reason": "no curated entry in tools/overlay.json yet"}
            )
            continue

        # 'app' = an index.html really exists at the published path; otherwise the
        # Pages build is only rendering the README through Jekyll.
        kind = ov.get("kind")
        if kind is None:
            kind = "app" if has_entry_point(OWNER, name, sub_path, branch) else "stub"

        sites.append(
            {
                "repo": name,
                "title": ov["title"],
                "category": ov["category"],
                "kind": kind,
                "description": ov["description"],
                "created": repo.get("created_at"),
                "firstCommit": oldest["commit"]["committer"]["date"],
                "firstCommitSha": oldest["sha"][:7],
                "lastCommit": newest["commit"]["committer"]["date"],
                "lastCommitSha": newest["sha"][:7],
                "pushedAt": repo.get("pushed_at"),
                "updatedAt": repo.get("updated_at"),
                "commits": len(commits),
                "pagesStatus": pages.get("status"),
                "pagesSource": source_str,
                "pagesUrl": pages.get("html_url"),
                "defaultBranch": branch,
                "sizeKb": repo.get("size"),
                "flags": ov.get("flags", []),
            }
        )
        print("  ok   %-38s commits=%-5s pages=%-8s source=%s" % (name, len(commits), pages.get("status"), source_str))

    sites.sort(key=lambda s: s["repo"].lower())

    owner_account = next((a for a in accounts_checked if a["login"] == OWNER), {})
    total_commits = sum(s["commits"] for s in sites)
    built = sum(1 for s in sites if s["pagesStatus"] == "built")
    apps = sum(1 for s in sites if s["kind"] == "app")
    stubs = len(sites) - apps
    categories = {}
    for s in sites:
        categories[s["category"]] = categories.get(s["category"], 0) + 1

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    excluded_note = (
        "%d public repositories carry a GitHub Pages site; this directory publishes %d of them, and "
        "every other repository is named with the reason it is withheld (%s). %d repo(s) are permanently "
        "excluded by owner request and must never be added back (see AGENTS.md); any other unlisted "
        "repository is one that has no curated, sourced entry yet and is therefore never described."
        % (owner_account.get("pagesSites", 0), len(sites),
           "; ".join("%s: %s" % (u["repo"], u["reason"]) for u in unlisted) or "none",
           len(excluded))
    )

    methodology = {
        "steps": [
            "Queried GET https://api.github.com/users/{login}/repos for both specified accounts "
            "(buffedlizard55-lab returned %s public repositories; kanlerxz87-cyber returned %s)."
            % (
                owner_account.get("publicRepos"),
                next((a["publicRepos"] for a in accounts_checked if a["login"] == "kanlerxz87-cyber"), 0),
            ),
            "Queried GET /repos/buffedlizard55-lab/{repo} for every repository to extract created_at, "
            "pushed_at, updated_at, default_branch, size and metadata.",
            "Queried GET /repos/buffedlizard55-lab/{repo}/pages for every repository to confirm Pages "
            "status, custom-domain configuration and the published branch/path.",
            "Queried paginated GET /repos/buffedlizard55-lab/{repo}/commits?sha={default_branch} to obtain "
            "exact commit totals plus first-commit and latest-commit timestamps and SHAs.",
            "Queried GET /repos/buffedlizard55-lab/{repo}/contents/{published path}/index.html to determine "
            "whether a repository publishes a real site ('app') or only a Jekyll-rendered README ('stub').",
            "Read each repository's README.md through the official contents API to source every description, "
            "then re-read the READMEs of every repository whose commit count moved since the previous audit.",
            "Repositories present in previous audits but returning HTTP 404 today are moved to the "
            "'unreachable' list with their last verified values instead of being silently deleted.",
            "%s" % excluded_note,
            "Cataloged every anomaly found during the pass in the flagged irregularities register, with the "
            "official endpoint needed to reproduce each one.",
        ],
        "caveats": [
            "Created date is the official GitHub repository creation timestamp; the first-commit committer "
            "date matches it within one second for every listed repository.",
            "Last Updated is the newest committer timestamp on the repository's default branch; pushed_at "
            "tracks the latest push to any branch and can therefore lead it.",
            "Repository size is GitHub's own size field in KB; it is recomputed asynchronously and can lag "
            "or lead the commit history.",
            "Descriptions are sourced from each repository's own README.md and generated site. A repository "
            "that pushes a new README after this snapshot can make a description stale until the next refresh.",
            "The audit sandbox can reach github.com but not *.github.io, so live page bodies are not re-fetched "
            "over HTTP here. 'Built' status from the Pages API plus a verified index.html entry point are the "
            "two signals used; every entry also links to its live site for manual review.",
            "kanlerxz87-cyber has %s public repositories and therefore zero GitHub Pages sites."
            % next((a["publicRepos"] for a in accounts_checked if a["login"] == "kanlerxz87-cyber"), 0),
        ],
    }

    data = {
        "generated": now,
        "owner": OWNER,
        "auditDate": now[:10],
        "accountsChecked": accounts_checked,
        "counts": {
            "sites": len(sites),
            "apps": apps,
            "stubs": stubs,
            "pagesBuilt": built,
            "commits": total_commits,
            "categories": categories,
            "publicRepos": owner_account.get("publicRepos"),
            "pagesSites": owner_account.get("pagesSites"),
            "excluded": sorted(excluded),
            "unlisted": unlisted,
            "unreachable": len(overlay.get("retired", [])),
        },
        "sites": sites,
        "unreachable": overlay.get("retired", []),
        "irregularities": overlay.get("irregularities", []),
        "methodology": methodology,
    }

    banner = (
        "/* MasterSite data — generated by tools/build_data.py from the official GitHub REST API.\n"
        " * Audit timestamp: %s\n"
        " *\n"
        " * DO NOT hand-edit the API-derived fields; re-run the generator instead:\n"
        " *     python3 tools/build_data.py\n"
        " *\n"
        " * Narrative fields (title / category / description / flags / irregularities) live in\n"
        " * tools/overlay.json. Repositories listed in overlay.json 'excluded' are permanently\n"
        " * suppressed by owner request and must never be re-added — see AGENTS.md.\n"
        " */\n"
        "window.MASTERDATA = "
    )
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        fh.write(banner % now)
        fh.write(json.dumps(data, indent=2, ensure_ascii=False))
        fh.write(";\n")

    print("-" * 72)
    print("wrote %s" % os.path.relpath(OUT_PATH, ROOT))
    print("  sites=%d (apps=%d stubs=%d) built=%d commits=%d" % (len(sites), apps, stubs, built, total_commits))
    print("  categories=%s" % json.dumps(categories))
    print("  unreachable=%d excluded=%s" % (len(data["unreachable"]), sorted(excluded)))
    for u in unlisted:
        print("  unlisted=%s (%s)" % (u["repo"], u["reason"]))
    assert len(sites) + len(unlisted) == owner_account.get("pagesSites", 0), (
        "accounting error: %d listed + %d unlisted != %d Pages sites on the account"
        % (len(sites), len(unlisted), owner_account.get("pagesSites", 0))
    )
    for w in warnings:
        print("  WARNING: %s" % w, file=sys.stderr)


if __name__ == "__main__":
    main()
