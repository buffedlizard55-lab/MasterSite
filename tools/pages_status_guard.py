#!/usr/bin/env python3
"""Pages status transition guard for MasterSite — the daily build-health watch.

T-026 (TASKS.md): `census_guard.py` compares the live repository *list* to the
published snapshot, but nothing watched `pagesStatus`, so `NFLInjuryReport`
going `built` -> `errored` was found only by a manual re-read (`FL-17`,
`IRR-141`, `IRR-132`), and `GEMSDOE53` has been stalled at `errored` since
2026-10-09 (`FL-05`) with nothing re-checking it between refreshes. This tool
is that watch: one read-only pass that compares every listed entry's live
Pages status to the published one and fails loudly on any entry that is not
`built`. It runs from the same daily workflow as the coverage guard
(`.github/workflows/census.yml`) but stays a separate tool on purpose: the
coverage guard answers "is every public repository listed?" in ~7 requests,
while this one answers "is every listed site still built?" and costs one
Pages read per listed entry (~150 requests) — different question, different
cost class, different issue label.

What it checks, against the official GitHub REST API only:

  1. For every site in the published snapshot (`data/sites.js` sites[]),
     `GET /repos/{owner}/{repo}/pages` must answer HTTP 200 and its `status`
     must equal the published `pagesStatus`.
  2. The live `status` must be `built`. An entry published as `errored` that
     is *still* `errored` matches the snapshot (no transition) but is still a
     finding: the task requires an issue for any entry that is not `built`,
     until it recovers.
  3. A transition in either direction is a finding — `built` -> `errored`
     (site may be down) and `errored` -> `built` (recovery; the published
     record is now stale and needs a refresh). The snapshot is never edited
     here; remediation is the documented rebuild in AGENTS.md §4.
  4. HTTP 404 on a listed entry's Pages endpoint is a finding (the repository
     or its Pages configuration is gone while the record still claims a
     site), not an API failure.

Exit codes: 0 = every listed entry is live `built` and matches the published
record; 1 = at least one finding (transition, not built, or unreadable);
2 = API or environment failure (rate limit, auth, transport) — never treated
as a pass and never reported as a finding, because an unreachable API proves
nothing about build health.

It writes no files and edits no data. Findings print with the exact endpoint
and the UTC read time so a reviewer can re-open each one by hand.

Offline gate: `--self-test` proves all verdict paths with a synthetic API
(no network): pass, transition, stable-errored, pages-404, and the rule that
an API failure is never a verdict.
"""

import io
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from contextlib import redirect_stdout
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "sites.js")
API = "https://api.github.com"
DEFAULT_OWNER = "buffedlizard55-lab"

EXIT_OK, EXIT_FINDING, EXIT_API = 0, 1, 2
REQUEST_PAUSE_SECONDS = 1.0  # secondary-rate-limit politeness floor; see census_guard.py


def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail_api(message):
    print("PAGES-STATUS-GUARD API FAILURE: %s" % message)
    print("An unreachable or blocked API proves nothing about build health; no verdict is reported.")
    sys.exit(EXIT_API)


def api_get(path):
    req = urllib.request.Request(
        API + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "MasterSite-pages-status-guard",
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


def site_owner(site, snapshot):
    """Owner of one listed site: the record's own owner, else the snapshot's."""
    return site.get("owner") or snapshot.get("owner") or DEFAULT_OWNER


def classify_entry(site, owner, http_status, payload, read_at):
    """Classify one official Pages read against the published record.

    Pure function (no I/O): returns a dict describing the entry and every
    finding it carries. `findings` is a list of kinds:
      - "transition":        live status != published pagesStatus
      - "not-built":         live status != "built"
      - "pages-unreadable":  HTTP 404 (no readable Pages configuration)
    """
    repo = site.get("repo")
    source = "%s/repos/%s/%s/pages" % (API, owner, repo)
    result = {
        "repo": repo,
        "owner": owner,
        "published": site.get("pagesStatus"),
        "live": None,
        "http": http_status,
        "source": source,
        "readAt": read_at,
        "findings": [],
    }
    if http_status == 404:
        result["findings"].append("pages-unreadable")
        return result
    if http_status != 200:
        # Anything else is an API problem; run_guard converts it to exit 2.
        return result
    live = payload.get("status") if isinstance(payload, dict) else None
    result["live"] = live
    if live != result["published"]:
        result["findings"].append("transition")
    if live != "built":
        result["findings"].append("not-built")
    return result


def run_guard():
    snapshot = load_snapshot()
    sites = snapshot.get("sites") or []
    if not sites:
        fail_api("snapshot contains no sites[] entries — refusing to pass on an empty list")

    read_at = now_utc()
    print(
        "MasterSite Pages status guard (T-026) — every listed entry's live Pages status "
        "vs the published snapshot"
    )
    print("-" * 88)
    print(
        "snapshot: generated %s | %d listed sites | published by %s"
        % (snapshot.get("generated"), len(sites), snapshot.get("owner"))
    )
    print("read at: %s (one GET /repos/{owner}/{repo}/pages per entry)" % read_at)

    results = []
    for site in sites:
        owner = site_owner(site, snapshot)
        status, data = api_get("/repos/%s/%s/pages" % (owner, site.get("repo")))
        if status not in (200, 404):
            fail_api(
                "GET /repos/%s/%s/pages returned HTTP %s (%s)"
                % (owner, site.get("repo"), status,
                   data.get("message", "") if isinstance(data, dict) else "")
            )
        res = classify_entry(site, owner, status, data, read_at)
        results.append(res)
        if res["findings"]:
            detail = ", ".join(res["findings"])
            live = res["live"] if res["live"] is not None else "HTTP %s" % res["http"]
            print(
                "  FINDING  %-24s published=%-8s live=%-8s [%s]"
                "  %s  (read %s)"
                % (res["repo"], res["published"], live, detail, res["source"], read_at)
            )
        else:
            print(
                "  ok       %-24s published=%-8s live=%-8s  %s"
                % (res["repo"], res["published"], res["live"], res["source"])
            )

    unreachable = snapshot.get("unreachable") or []
    if unreachable:
        print(
            "note: %d frozen unreachable record(s) (%s) are not probed — they are "
            "historical records outside the live census (FL-03 / T-004), not listed sites."
            % (len(unreachable), ", ".join(u.get("repo", "?") for u in unreachable))
        )
    excluded = ((snapshot.get("counts") or {}).get("excluded")) or []
    if excluded:
        print("note: excluded repositories are never probed: %s" % ", ".join(excluded))

    transitions = [r for r in results if "transition" in r["findings"]]
    not_built = [r for r in results if "not-built" in r["findings"]]
    unreadable = [r for r in results if "pages-unreadable" in r["findings"]]
    clean = len(results) - len({id(r) for r in transitions + not_built + unreadable})

    print("-" * 88)
    print(
        "checked %d listed entries at %s: %d clean, %d transition(s), %d not built, %d unreadable"
        % (len(results), read_at, clean, len(transitions), len(not_built), len(unreadable))
    )

    if transitions or not_built or unreadable:
        print()
        for r in transitions:
            print(
                "FAIL: transition — %s published %r but the API just read %r; the published "
                "record is stale. Re-run the documented refresh (AGENTS.md §4). Source: %s (read %s)"
                % (r["repo"], r["published"], r["live"], r["source"], r["readAt"])
            )
        for r in not_built:
            if "transition" in r["findings"]:
                continue  # already reported above with the same source
            print(
                "FAIL: not built — %s live status is %r (matches the published record, but the "
                "site is not built). Recovery needs a new push or an owner-initiated rebuild; "
                "see the entry's FLAGGED.md row. Source: %s (read %s)"
                % (r["repo"], r["live"], r["source"], r["readAt"])
            )
        for r in unreadable:
            print(
                "FAIL: unreadable — %s has no readable Pages endpoint (HTTP 404) while the "
                "directory still lists it. Source: %s (read %s)"
                % (r["repo"], r["source"], r["readAt"])
            )
        print()
        print(
            "Remediation: never edit data/sites.js by hand — after a status recovers or a "
            "record goes stale, follow AGENTS.md §4 (re-run tools/build_data.py, the audits, "
            "scripts/validate, tools/build_verification.py). A Pages status is a live state: "
            "always publish it with the timestamp it was read at."
        )
        sys.exit(EXIT_FINDING)

    print(
        "PASS: every listed entry is live `built` and matches the published record "
        "(%d entries, read %s)." % (len(results), read_at)
    )
    sys.exit(EXIT_OK)


def self_test():
    """Offline deterministic check of the guard's verdict paths. No network.

    The real snapshot supplies repository names and structure, but every
    published `pagesStatus` used by a scenario is synthesized here, so the
    self-test stays valid after future refreshes (e.g. when `GEMSDOE53`
    finally recovers to `built` and the published record follows).
    """
    real = {"api_get": api_get, "load_snapshot": load_snapshot}
    base = real["load_snapshot"]()
    sites = base.get("sites") or []
    assert sites, "self-test needs a non-empty published snapshot"
    first = sites[0].get("repo")

    def variant(published_status):
        """A snapshot copy where every entry is published with one status."""
        snap = json.loads(json.dumps(base))
        for s in snap["sites"]:
            s["pagesStatus"] = published_status
        return snap

    def run(scenario):
        calls = {"n": 0}
        snap = variant("built")
        if scenario in ("stable-errored", "recovery"):
            # Only the first entry is published as errored; every other entry
            # stays published=built so scenario findings stay single-entry.
            snap["sites"][0]["pagesStatus"] = "errored"
        first_repo = snap["sites"][0]["repo"]

        def fake_api_get(path):
            calls["n"] += 1
            assert path.startswith("/repos/") and path.endswith("/pages"), (
                "unexpected path %s" % path
            )
            repo = path[len("/repos/"):-len("/pages")].split("/", 1)[1]
            if scenario == "api_failure" and calls["n"] == 3:
                return 403, {"message": "secondary rate limit (synthetic)"}
            if scenario == "transition" and repo == first_repo:
                return 200, {"status": "building"}
            if scenario == "stable-errored" and repo == first_repo:
                return 200, {"status": "errored"}
            if scenario == "recovery" and repo == first_repo:
                return 200, {"status": "built"}
            if scenario == "pages-404" and repo == first_repo:
                return 404, {"message": "Not Found"}
            return 200, {"status": "built"}

        globals()["api_get"] = fake_api_get
        globals()["load_snapshot"] = lambda: snap
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                run_guard()
            return EXIT_OK, buf.getvalue()
        except SystemExit as e:
            return e.code, buf.getvalue()
        finally:
            globals()["api_get"] = real["api_get"]
            globals()["load_snapshot"] = real["load_snapshot"]

    expectations = (
        ("all-built", EXIT_OK, ["PASS:"], []),
        ("transition", EXIT_FINDING, ["FINDING", "transition", "building"], []),
        ("stable-errored", EXIT_FINDING, ["not built", "errored"], ["FAIL: transition"]),
        ("pages-404", EXIT_FINDING, ["unreadable", "HTTP 404"], []),
        ("recovery", EXIT_FINDING, ["FAIL: transition", "stale"], ["FAIL: not built"]),
        ("api_failure", EXIT_API, ["API FAILURE"], []),
    )
    results = {}
    for scenario, expected, tokens, absent in expectations:
        code, out = run(scenario)
        results[scenario] = code
        assert code == expected, (
            "self-test %s: expected exit %s, got %s\n%s" % (scenario, expected, code, out)
        )
        for token in tokens:
            assert token in out, "self-test %s: output missing %r\n%s" % (scenario, token, out)
        for token in absent:
            assert token not in out, "self-test %s: output must not contain %r\n%s" % (
                scenario, token, out,
            )
    assert first == sites[0].get("repo")  # structure sanity: sites[] stayed intact

    print(
        "pages_status_guard self-test: "
        + ", ".join("%s->%d" % (k, v) for k, v in results.items())
    )
    print(
        "PASS: pass / transition / stable-non-built / pages-404 / recovery-stale / "
        "api-failure-never-a-verdict all behave as documented."
    )
    sys.exit(EXIT_OK)


def main():
    if "--self-test" in sys.argv[1:]:
        self_test()
    run_guard()


if __name__ == "__main__":
    main()
