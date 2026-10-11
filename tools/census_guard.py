#!/usr/bin/env python3
"""Census coverage guard for MasterSite — the cheap check that fails loudly.

T-010 (TASKS.md): between the 2026-10-01 and 2026-10-11 snapshots the account
grew from 108 to 146 public repositories and 38 public Pages sites were live on
the web with no directory entry, because nothing compared the live account
census to the published snapshot. This tool is that comparison. It is read-only,
makes only a handful of API calls (the two account profiles plus the paginated
repository lists — per-repository detail is not needed to detect a gap), and is
safe to run unattended on a schedule.

What it checks, against the official GitHub REST API only:

  1. Every public repository of buffedlizard55-lab is either listed in the
     published snapshot (data/sites.js sites[]) or on the exclusion list
     (overlay.json excluded[]). Anything else is a coverage gap: a live public
     repository the directory does not know about.
  2. The snapshot's counts.publicRepos agrees with the live account census, so a
     badly stale snapshot cannot pass silently either.
  3. kanlerxz87-cyber still reports 0 public repositories; the directory's scope
     note says exactly that, and a change must be curated, not missed.
  4. For every repository named in a failure, the official Pages endpoint is
     probed so the output separates "missing AND Pages-enabled" (a missing site)
     from "missing, no Pages" (a census change that still needs a decision).

Exit codes: 0 = coverage complete; 1 = coverage gap / census disagreement;
2 = API or environment failure (rate limit, auth, transport) — never treated as
a pass and never reported as a gap, because an unreachable API proves nothing
about coverage.

It writes no files and edits no data. Remediation is always the documented
workflow in AGENTS.md §4: curate tools/overlay.json from the repository's own
files, then re-run the build and the audits.
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "sites.js")
OVERLAY = os.path.join(ROOT, "tools", "overlay.json")
API = "https://api.github.com"
OWNER = "buffedlizard55-lab"
OTHER_ACCOUNT = "kanlerxz87-cyber"
ACCOUNTS = [OWNER, OTHER_ACCOUNT]

EXIT_OK, EXIT_GAP, EXIT_API = 0, 1, 2
REQUEST_PAUSE_SECONDS = 1.0  # secondary-rate-limit politeness floor; see verify_live.py


def fail_api(message):
    print("CENSUS-GUARD API FAILURE: %s" % message)
    print("An unreachable or blocked API proves nothing about coverage; not reporting a gap.")
    sys.exit(EXIT_API)


def api_get(path):
    req = urllib.request.Request(
        API + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "MasterSite-census-guard",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    time.sleep(REQUEST_PAUSE_SECONDS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:
            body = ""
        return e.code, {"message": body[:400]}
    except Exception as e:
        return 0, {"message": str(e)}


def paginate_repos(login):
    """Return the full public repository list for an account, or fail loudly."""
    out, page = [], 1
    while True:
        status, data = api_get(
            "/users/%s/repos?type=public&per_page=100&page=%d" % (login, page)
        )
        if status != 200 or not isinstance(data, list):
            fail_api(
                "GET /users/%s/repos page %d returned HTTP %s (%s)"
                % (login, page, status, data.get("message", "") if isinstance(data, dict) else "")
            )
        out.extend(data)
        if len(data) < 100:
            return out
        page += 1


def load_snapshot():
    """Read window.MASTERDATA out of data/sites.js via node (no parsing risk)."""
    script = (
        "global.window={};require(%r);"
        "process.stdout.write(JSON.stringify(window.MASTERDATA));" % DATA
    )
    try:
        out = subprocess.run(
            ["node", "-e", script], capture_output=True, text=True, check=True
        )
        return json.loads(out.stdout)
    except Exception as e:
        fail_api("cannot read data/sites.js via node: %s" % e)


def pages_probe(repo_name):
    """One official Pages probe so a gap report separates site from non-site."""
    status, data = api_get("/repos/%s/%s/pages" % (OWNER, repo_name))
    if status == 200:
        return "Pages: yes (status %s, %s)" % (
            data.get("status"), data.get("html_url", "no html_url"),
        )
    if status == 404:
        return "Pages: no (HTTP 404)"
    return "Pages: unknown (HTTP %s)" % status


def self_test():
    """Offline deterministic check of the guard's three verdict paths.

    No network: the API-reading functions are replaced with synthetic data
    derived from the real snapshot file, so CI (or a rate-limited sandbox) can
    prove the logic without touching api.github.com.
    """
    real = {
        "api_get": api_get,
        "paginate_repos": paginate_repos,
        "load_snapshot": load_snapshot,
        "pages_probe": pages_probe,
    }
    snapshot = real["load_snapshot"]()
    overlay = json.load(open(OVERLAY, encoding="utf-8"))
    excluded = set(overlay.get("excluded", []))
    listed = {s["repo"] for s in snapshot["sites"]}
    known = sorted(listed | excluded)
    profile = {"public_repos": len(known)}

    def run(scenario):
        calls = {"n": 0}

        def fake_api_get(path):
            calls["n"] += 1
            if path == "/users/%s" % OWNER:
                return 200, profile
            if path == "/users/%s" % OTHER_ACCOUNT:
                return 200, {"public_repos": 0}
            if path.startswith("/users/") and "/repos" in path:
                if scenario == "api_failure" and calls["n"] == 2:
                    return 403, {"message": "secondary rate limit (synthetic)"}
                if path.startswith("/users/%s/repos" % OTHER_ACCOUNT):
                    return 200, []
                repos = [{"name": n, "created_at": "2026-10-11T00:00:00Z"} for n in known]
                if scenario == "gap":
                    repos.append({"name": "SYNTHETIC-NEW-REPO", "created_at": "2026-10-11T00:00:00Z"})
                return 200, repos
            if path.startswith("/repos/") and path.endswith("/pages"):
                return 200, {"status": "built", "html_url": "https://example.invalid/"}
            raise AssertionError("unexpected path %s" % path)

        def fake_paginate(login):
            status, data = fake_api_get("/users/%s/repos?type=public" % login)
            if status != 200 or not isinstance(data, list):
                # Mirror the real paginate_repos contract: an API failure is a
                # loud exit-2, never a silently empty census.
                sys.exit(EXIT_API)
            return data

        def fake_pages_probe(name):
            return "Pages: yes (synthetic probe)"

        globals()["api_get"] = fake_api_get
        globals()["paginate_repos"] = fake_paginate
        globals()["pages_probe"] = fake_pages_probe
        try:
            run_guard()
            return EXIT_OK, None
        except SystemExit as e:
            return e.code, None
        finally:
            for k, v in real.items():
                globals()[k] = v

    results = {}
    for scenario, expected in (("complete", EXIT_OK), ("gap", EXIT_GAP), ("api_failure", EXIT_API)):
        code = run(scenario)[0]
        results[scenario] = code
        assert code == expected, "self-test %s: expected exit %s, got %s" % (scenario, expected, code)

    print("census_guard self-test: complete->%d (pass), gap->%d (loud failure), api_failure->%d (never a false gap)"
          % (results["complete"], results["gap"], results["api_failure"]))
    print("PASS: all three verdict paths behave as documented.")
    sys.exit(EXIT_OK)


def run_guard():
    snapshot = load_snapshot()
    overlay = json.load(open(OVERLAY, encoding="utf-8"))
    excluded = set(overlay.get("excluded", []))
    listed = {s["repo"] for s in snapshot.get("sites", [])}
    known = listed | excluded

    print("MasterSite census guard — comparing the live account census to the published snapshot")
    print("-" * 80)

    failures = []

    # Account 1: the owner. Every public repository must be known to the directory.
    status, profile = api_get("/users/%s" % OWNER)
    if status != 200:
        fail_api("GET /users/%s returned HTTP %s" % (OWNER, status))
    repos = paginate_repos(OWNER)
    api_names = {r["name"] for r in repos}
    if profile.get("public_repos") != len(repos):
        failures.append(
            "census disagreement: GET /users/%s reports public_repos=%s but the paginated "
            "repository list returned %d entries — re-run the full build before trusting "
            "either number"
            % (OWNER, profile.get("public_repos"), len(repos))
        )
    missing = sorted(api_names - known)
    if missing:
        lines = [
            "coverage gap: %d public repositories of %s are neither listed in data/sites.js "
            "nor on the overlay exclusion list:" % (len(missing), OWNER)
        ]
        for name in missing:
            created = next((r["created_at"] for r in repos if r["name"] == name), "unknown")
            lines.append(
                "  - %s (created %s; %s) — curate from its own files or exclude by owner "
                "instruction, then re-run the build"
                % (name, created, pages_probe(name))
            )
        failures.append("\n".join(lines))
    snapshot_public = (snapshot.get("counts") or {}).get("publicRepos")
    if snapshot_public != len(repos):
        failures.append(
            "snapshot is stale: counts.publicRepos=%s but the live census returns %d public "
            "repositories; re-run tools/build_data.py and the audits"
            % (snapshot_public, len(repos))
        )

    # Account 2: the scope note publishes "0 public repositories" — keep it true.
    status, other = api_get("/users/%s" % OTHER_ACCOUNT)
    if status != 200:
        fail_api("GET /users/%s returned HTTP %s" % (OTHER_ACCOUNT, status))
    other_repos = paginate_repos(OTHER_ACCOUNT)
    if other.get("public_repos", 0) or other_repos:
        lines = [
            "scope change: %s now reports %s public repositories (%d in the paginated list); "
            "the directory's account note says 0. Review and curate:"
            % (OTHER_ACCOUNT, other.get("public_repos"), len(other_repos))
        ]
        for r in sorted(other_repos, key=lambda x: x["name"]):
            lines.append(
                "  - %s (created %s; https://api.github.com/repos/%s/%s)"
                % (r["name"], r["created_at"], OTHER_ACCOUNT, r["name"])
            )
        failures.append("\n".join(lines))

    print(
        "  %-22s public_repos=%s pages-census=%d listed=%d excluded=%d"
        % (OWNER, profile.get("public_repos"), len(repos), len(listed), len(excluded))
    )
    print(
        "  %-22s public_repos=%s" % (OTHER_ACCOUNT, other.get("public_repos"))
    )

    if failures:
        print("-" * 80)
        for f in failures:
            print("FAIL: %s" % f)
            print()
        print(
            "Remediation: follow AGENTS.md §4 — curate tools/overlay.json from each "
            "repository's own files (never from its name), re-run tools/build_data.py, the "
            "audits, scripts/validate and tools/build_verification.py, and update the README "
            "current-audit-status table in the same change."
        )
        sys.exit(EXIT_GAP)

    print("-" * 80)
    print(
        "PASS: coverage complete — every public repository of both accounts is listed or "
        "explicitly excluded (%d listed + %d excluded = %d public repositories; %s still at 0)."
        % (len(listed), len(excluded), len(repos), OTHER_ACCOUNT)
    )
    sys.exit(EXIT_OK)


def main():
    if "--self-test" in sys.argv[1:]:
        self_test()
    run_guard()


if __name__ == "__main__":
    main()
