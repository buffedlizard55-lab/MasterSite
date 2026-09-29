#!/usr/bin/env python3
"""Regenerate VERIFICATION.md from the generated dataset in data/sites.js.

Run tools/build_data.py first, then this script. The ledger tables, the account
table and the irregularities register are rendered straight from the dataset so
the documentation can never drift from the data the site actually renders.

    python3 tools/build_data.py && python3 tools/build_verification.py
"""

import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "sites.js")
OVERLAY = os.path.join(ROOT, "tools", "overlay.json")
OUT = os.path.join(ROOT, "VERIFICATION.md")


def load_data():
    """Read window.MASTERDATA = {...}; out of data/sites.js via node (no parsing risk)."""
    script = (
        "global.window={};require(%r);"
        "process.stdout.write(JSON.stringify(window.MASTERDATA));" % DATA
    )
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def ts(iso):
    return (iso or "").replace("T", " ").replace("Z", "")


def load_report(name):
    try:
        with open(os.path.join(ROOT, "tools", name), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def main():
    d = load_data()
    ov = json.load(open(OVERLAY, encoding="utf-8"))
    owner = d["owner"]
    gen = d["generated"]
    audit = d.get("auditDate", gen[:10])
    sites = d["sites"]
    unreachable = d.get("unreachable", [])
    counts = d.get("counts", {})
    irr = d.get("irregularities", [])
    description_audit = load_report("last_description_audit.json")
    kind_audit = load_report("last_kind_audit.json")
    live_audit = load_report("last_live_verify.json")

    L = []
    A = L.append

    A("# MasterSite — API Snapshot, Source & Irregularities Ledger\n")
    A("**API Snapshot:** %s (UTC). Description-source stamps and stale states are reported per entry below." % gen)
    A("**Generated:** `%s` by `tools/build_data.py` + `tools/build_verification.py`; API telemetry is fetched automatically, while titles/categories/descriptions are curated from repository-owned files in `tools/overlay.json`. No user-supplied entry data was needed." % gen)
    A("**Audited Accounts:** `buffedlizard55-lab`, `kanlerxz87-cyber`")
    A("**Scope:** Public repositories and Pages deployments visible through GitHub's official API for both named accounts. Every discovered omission, permanent exclusion, or unreachable record is identified separately; private repositories are outside scope.")
    A("**Integrity Standard:** API-derived fields are tied to the recorded snapshot; the latest independent `verify_live.py`, kind, and numeric-token checks are reported below as complete, incomplete, blocked, or stale. Each curated description records its source basis and commit SHA; stale SHA stamps are exposed rather than called current. The numeric-token description audit is a lint, not semantic proof.\n")
    A("**Live Directory:** <https://%s.github.io/MasterSite/>\n" % owner)
    A("---\n")

    # ---------------- 1. Accounts ----------------
    A("## 1. Official Account Verification\n")
    A("| Account | GitHub Profile | Official API Endpoint | Account Created (UTC) | Public Repos | Pages Sites | Status & Review Notes |")
    A("|---|---|---|---|---|---|---|")
    for a in d["accountsChecked"]:
        prof = "[github.com/%s](https://github.com/%s)" % (a["login"], a["login"])
        api = "[`/users/%s`](%s)" % (a["login"], a["apiRepos"])
        ok = "✅ Verified" if a["login"] == owner else "✅ Verified (empty)"
        A("| `%s` | %s | %s | %s | %s | %s | %s: %s |" % (
            a["login"], prof, api, a["accountCreated"], a["publicRepos"], a["pagesSites"], ok, a["note"]))
    A("")
    A("> Both accounts were queried with `GET /users/{login}` and `GET /users/{login}/repos?per_page=100`. "
      "Pages-site counts are per-repository reads of `GET /repos/%s/{repo}/pages`, not a single aggregate field, "
      "so each one is independently checkable." % owner)
    A("")
    A("---\n")

    # ---------------- 2. Ledger ----------------
    A("## 2. Master Repository & GitHub Pages Audit Ledger (%d / %d Directory Entries Verified)\n"
      % (len(sites), len(sites)))
    A("Every line below was produced by these official reads:\n")
    A("- `GET https://api.github.com/users/%s/repos?per_page=100` (%s repositories returned)" % (owner, counts.get("publicRepos")))
    A("- `GET https://api.github.com/repos/%s/{repo}`" % owner)
    A("- `GET https://api.github.com/repos/%s/{repo}/pages`" % owner)
    A("- `GET https://api.github.com/repos/%s/{repo}/commits?sha={default_branch}&per_page=100` (paginated)" % owner)
    A("- `GET https://api.github.com/repos/%s/{repo}/contents/{published path}/index.html` (HTML entry point vs. README/documentation stub; not a test of interactivity)" % owner)
    A("- The exact description-source endpoint and commit are recorded per entry in `verifiedBasis`; narrative text is curated in `tools/overlay.json`, not generated by the metadata fetch.\n")

    A("| # | Repository | Category | Type | Pages Status | Source | Created (UTC) | First Commit (SHA) | Last Commit on Default Branch (UTC) | Latest SHA | Total Commits | Size (KB) | Description Last Verified | Live Site & Official Sources |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    latest_pass = counts.get("proseLatestPass")
    for i, s in enumerate(sites, 1):
        live = s.get("pagesUrl") or ("https://%s.github.io/%s/" % (owner, s["repo"]))
        links = " · ".join([
            "[Live](%s)" % live,
            "[Repo](https://github.com/%s/%s)" % (owner, s["repo"]),
            "[Pages API](https://api.github.com/repos/%s/%s/pages)" % (owner, s["repo"]),
            "[Commits API](https://api.github.com/repos/%s/%s/commits)" % (owner, s["repo"]),
            "[Settings](https://github.com/%s/%s/settings/pages)" % (owner, s["repo"]),
        ])
        lv = s.get("lastVerified")
        if not lv:
            verified = "⚠️ never stamped"
        elif latest_pass and lv == latest_pass:
            verified = "✅ re-read %s" % ts(lv)
        else:
            verified = "↪️ carried %s" % ts(lv)
        A("| %d | `%s` | %s | %s | %s | `%s` | %s | `%s` | %s | `%s` | %s | %s | %s | %s |" % (
            i,
            s["repo"],
            s["category"],
            "HTML entry-point site" if s["kind"] == "app" else "README/documentation stub",
            s["pagesStatus"],
            s["pagesSource"],
            ts(s["created"]),
            s["firstCommitSha"],
            ts(s["lastCommit"]),
            s["lastCommitSha"],
            s["commits"],
            s.get("sizeKb", 0),
            verified,
            links,
        ))
    A("")
    A("Totals across the %d listed entries: **%s commits on default branches**, **%s HTML entry points / %s README-documentation stubs**, "
      "**%s/%s Pages builds reporting `built`**.\n" % (
          len(sites), counts.get("commits"), counts.get("apps"), counts.get("stubs"),
          counts.get("pagesBuilt"), len(sites)))
    A("---\n")

    # ---------------- 2a. Exclusions ----------------
    A("## 2a. Repository Exclusions (Deliberately Omitted)\n")
    A("The account holds **%s** public GitHub Pages repositories, while this directory and `data/sites.js` publish "
      "**%s** entries. That difference is intentional and permanent — it is not a data gap to repair.\n" % (
          counts.get("pagesSites"), len(sites)))
    A("| Repository | Reason for Exclusion | Excluded Since | Rule |")
    A("|---|---|---|---|")
    A("| `ProjX` | Owner directive: this project must not be advertised, linked, or indexed by MasterSite | 2026-09-12 | "
      "**Do not re-add.** Omit from `data/sites.js`, from the Section 2 ledger table, from README counts, and from every "
      "regenerated export. |")
    A("")
    A("**Verification note:** only the *publication* of this repository is suppressed. The repository itself was never "
      "deleted, unpublished or modified, and no live link, API endpoint or Pages URL for it is printed anywhere in this "
      "repository. Account-wide totals (`publicRepos`, `pagesSites`) stay at their verified API values on purpose so the "
      "exclusion remains auditable; a refresh must filter excluded names *after* the API read rather than lowering those "
      "totals. See [`AGENTS.md`](AGENTS.md) → *Repository Exclusions*.\n")
    A("---\n")

    # ---------------- 2b. Unreachable ----------------
    A("## 2b. Unreachable Entries (Published Previously, Gone Today)\n")
    if unreachable:
        for u in unreachable:
            A("### `%s` — HTTP 404 on %s\n" % (u["repo"], u.get("retiredAt", "this audit")))
            A("**Finding.** %s\n" % u.get("retiredReason", ""))
            A("**Last independently verified state (frozen, not re-fetched):**\n")
            A("| Field | Last Verified Value |")
            A("|---|---|")
            for label, key in [
                ("Created (UTC)", "created"),
                ("First commit", "firstCommit"),
                ("First commit SHA", "firstCommitSha"),
                ("Last commit on main (UTC)", "lastCommit"),
                ("Last commit SHA", "lastCommitSha"),
                ("pushed_at", "pushedAt"),
                ("updated_at", "updatedAt"),
                ("Total commits", "commits"),
                ("Pages status", "pagesStatus"),
                ("Pages source", "pagesSource"),
                ("Repository size (KB)", "sizeKb"),
            ]:
                A("| %s | `%s` |" % (label, u.get(key, "—")))
            A("")
            A("**How to reproduce the 404:**\n")
            for e in u.get("retiredEvidence", []):
                A("- `%s`" % e)
            A("")
            A("This entry is kept in `data/sites.js` under `unreachable` and rendered on the site in the "
              "*Unreachable — Needs Owner Review* panel. It is excluded from the live directory counts and its links "
              "are expected to be dead until the repository is restored.\n")
    else:
        A("None. Every repository published in a previous audit still answers on the official GitHub API.\n")
    A("---\n")

    # ---------------- 3. Irregularities ----------------
    sev_label = {"critical": "Critical", "warn": "Warning", "info": "Info"}
    A("## 3. Flagged Irregularities Register (%d entries)\n" % len(irr))
    A("| ID | Severity | Title | Verifiable Finding & Resolution |")
    A("|---|---|---|---|")
    for it in irr:
        detail = it["detail"].replace("|", "\\|").replace("\n", " ")
        A("| **%s** | `%s` | %s | %s |" % (it["id"], sev_label.get(it["severity"], it["severity"]), it["title"].replace("|", "\\|"), detail))
    A("")
    A("---\n")

    # ---------------- 4. Description verification ----------------
    A("## 4. Description-Source Verification\n")
    A("Descriptions, titles, categories and flags are curated in `tools/overlay.json` from repository-owned README/source files. "
      "The metadata generator does not invent summaries. Each site's `verifiedBasis` names the evidence and recorded commit; "
      "the SHA ledger below distinguishes newly checked, carried, and stale prose. A matching SHA is provenance, not a guarantee "
      "that every sentence is true.\n")
    A("**Change log for the %s pass:**\n" % audit)
    for n in ov.get("descriptionNotes", []):
        A("- %s" % n)
    A("")
    if (description_audit and description_audit.get("snapshotGenerated") == gen
            and description_audit.get("complete")):
        A("**Automated numeric-token lint for this snapshot:** `tools/audit_descriptions.py` checked %s entries at their recorded `headSha`; "
          "it found %s entries needing review and has %s documented numeric-token exception records. This lint only checks whether "
          "numbers occur in the README; it cannot establish that they mean the same thing or verify non-numeric claims.\n" % (
              description_audit.get("checkedEntries", 0),
              len(description_audit.get("unresolved", [])),
              len(description_audit.get("accepted", {}))))
    elif description_audit and description_audit.get("snapshotGenerated") == gen:
        errors = description_audit.get("apiErrors", [])
        first = errors[0] if errors else {}
        A("**Automated numeric-token lint for this snapshot: INCOMPLETE.** It checked %s/%s entries before the API request failed%s. "
          "This is not a clean lint result; rerun after restoring GitHub API access. The lint is not semantic proof.\n" % (
              description_audit.get("checkedEntries", 0), description_audit.get("totalEntries", len(sites)),
              " (HTTP %s: %s)" % (first.get("status"), first.get("message") or first.get("endpoint"))
              if first else ""))
    else:
        A("**Automated numeric-token lint:** no description-audit report matching this API snapshot was available when this ledger was generated. The lint is not semantic proof.\n")
    A("---\n")

    # ---------------- 4a. Prose verification ledger ----------------
    A("## 4a. Description-Prose Verification Ledger (per entry)\n")
    A("`generated` (`%s`) records when the **API-derived fields** were read. It says nothing about the "
      "**description prose**, which is the part that has actually gone stale in every audit so far "
      "(IRR-25, IRR-33, IRR-42). Each entry therefore carries its own `lastVerified` stamp and a "
      "`verifiedBasis` string stating what was read and why carrying it forward is safe. This table is "
      "the audit trail for that distinction.\n" % gen)
    A("State key: **re-read** = the prose was checked against the repository's own files in the latest "
      "pass and the repository has not moved since · **carried** = the prose is from an earlier pass, the "
      "basis says why that is safe, and the repository has not moved since · **behind repo** = the recorded "
      "head SHA differs from the prose SHA, so the description needs re-reading; that difference alone does "
      "not prove the text is false · **unstamped** = the prose has never been re-read (a defect; there "
      "are currently %s).\n"
      "\nRows are ordered stale-first, because this table is the work queue for the next session: "
      "`verifiedAtSha` compared with the live head SHA makes that ordering a computation rather than a "
      "judgement call (IRR-50).\n"
      % counts.get("proseUnstamped", 0))
    A("| Repository | State | `lastVerified` (UTC) | Prose read at | Repo head now | Behind repo? | Basis |")
    A("|---|---|---|---|---|---|---|")
    # Stale entries first: they are the work queue, so they belong at the top.
    for s in sorted(sites, key=lambda x: (not x.get("proseStale"), x.get("lastVerified") or "",
                                          x["repo"].lower()), reverse=False):
        lv = s.get("lastVerified")
        if not lv or not s.get("verifiedAtSha"):
            state = "⚠️ unstamped"
        elif s.get("proseStale"):
            state = "🔴 behind repo"
        elif latest_pass and lv == latest_pass:
            state = "✅ re-read"
        else:
            state = "↪️ carried"
        basis = (s.get("verifiedBasis") or "—").replace("|", "\\|").replace("\n", " ")
        A("| `%s` | %s | %s | `%s` | `%s` | %s | %s |" % (
            s["repo"], state, ts(lv) if lv else "—",
            s.get("verifiedAtSha") or "—", s.get("headSha") or s.get("lastCommitSha") or "—",
            "**YES**" if s.get("proseStale") else "no", basis))
    A("")
    stale_list = counts.get("proseStaleRepos", [])
    A("Totals: **%s of %d** entries were re-read in the latest pass (`%s`); **%d** were carried forward "
      "with a stated reason; **%s** are unstamped; and **%s** are provably behind their repository%s.\n"
      % (counts.get("proseReReadLatestPass", 0), len(sites), ts(latest_pass),
         len(sites) - counts.get("proseReReadLatestPass", 0), counts.get("proseUnstamped", 0),
         counts.get("proseStale", 0),
         (" — " + ", ".join("`%s`" % r for r in stale_list)) if stale_list else ""))
    A("---\n")

    # ---------------- 4b. Independent audit status ----------------
    A("## 4b. Independent Audit Run Status\n")
    A("These summaries distinguish a completed check from a request that could not be made. Authorization and API rate-limit errors are not evidence that a repository field is wrong.\n")
    audit_rows = [
        ("`verify_live.py`", live_audit),
        ("`audit_kind.py`", kind_audit),
        ("`audit_descriptions.py`", description_audit),
    ]
    A("| Audit | Status for this snapshot | Result |")
    A("|---|---|---|")
    for label, report in audit_rows:
        if not report:
            status, result = "not available", "No machine-readable report found."
        elif report.get("snapshotGenerated") != gen:
            status = "stale report"
            result = "Report refers to `%s`, not `%s`." % (report.get("snapshotGenerated"), gen)
        elif report.get("status") in ("blocked_auth", "blocked_rate_limit"):
            http = (report.get("error") or {}).get("httpStatus", "?")
            status = "blocked — HTTP %s" % http
            action = "wait for the GitHub API rate limit to reset" if http == 403 else "restore GitHub authorization"
            result = "No completed field comparisons; %s and rerun this audit." % action
        elif report.get("complete"):
            status = "complete"
            if label == "`verify_live.py`":
                result = "%s checks; %s hard mismatches; %s drift." % (
                    report.get("checks", 0), report.get("hardMismatchCount", 0), report.get("driftCount", 0))
            elif label == "`audit_kind.py`":
                result = "%s/%s entries checked; %s disagreements; %s unresolved." % (
                    report.get("checkedEntries", 0), report.get("totalEntries", 0),
                    len(report.get("disagreements", [])), len(report.get("unresolved", [])))
            else:
                result = "%s/%s entries checked; %s needing review; %s API errors." % (
                    report.get("checkedEntries", 0), report.get("totalEntries", 0),
                    len(report.get("unresolved", [])), len(report.get("apiErrors", [])))
        else:
            status = "incomplete"
            errors = report.get("apiErrors", []) or report.get("unresolved", [])
            if report.get("error"):
                errors = [report["error"]]
            first = errors[0] if errors else {}
            http = first.get("httpStatus", first.get("status")) if isinstance(first, dict) else None
            reason = (first.get("message") or first.get("endpoint") or first.get("field")
                      if isinstance(first, dict) else str(first)) or "check did not finish"
            progress = "%s/%s attempted" % (report.get("checkedEntries", report.get("partialChecks", 0)),
                                              report.get("totalEntries", "?"))
            result = "%s; not a completed audit%s." % (
                progress, " (HTTP %s: %s)" % (http, reason) if http else " (%s)" % reason)
        A("| %s | **%s** | %s |" % (label, status, result.replace("|", "\\|")))
    A("")
    A("---\n")

    # ---------------- 5. Reproduction ----------------
    A("## 5. Reproduction Commands for Independent Manual Review\n")
    A("Any reviewer with the GitHub CLI (`gh`) or `curl` can re-derive every row above:\n")
    A("```bash")
    A("# 1. Verify the accounts")
    A("gh api /users/%s" % owner)
    A("gh api /users/kanlerxz87-cyber")
    A("")
    A("# 2. List every public repository (expected: %s for %s, 0 for kanlerxz87-cyber)" % (counts.get("publicRepos"), owner))
    A('gh api "/users/%s/repos?per_page=100" --jq \'.[].name\'' % owner)
    A('gh api "/users/kanlerxz87-cyber/repos?per_page=100"')
    A("")
    A("# 3. Verify Pages status and publish source for any repository")
    A("gh api /repos/%s/SFWeather/pages" % owner)
    A("")
    A("# 4. Verify exact commit history, first commit and latest commit")
    A('gh api "/repos/%s/SFWeather/commits?per_page=100" --jq \'.[0].sha, .[0].commit.committer.date\'' % owner)
    A("")
    A("# 5. Confirm the retired entry really is gone (expected: HTTP 404)")
    for u in unreachable:
        A("gh api /repos/%s/%s          # -> 404 Not Found" % (owner, u["repo"]))
    if not unreachable:
        A("# (no unreachable entries in this audit)")
    A("")
    A("# 6. Refresh API telemetry and render the source-curated directory")
    A("python3 tools/build_data.py && python3 tools/build_verification.py")
    A("")
    A("# 6b. Independently re-check every entry's app-vs-stub classification against the")
    A("#     published path (read-only; reports disagreements, writes nothing)")
    A("python3 tools/audit_kind.py")
    A("")
    A("# 7. Confirm the published totals against the data file")
    A('grep -c \'"repo":\' data/sites.js                      # expected %d' % len(sites))
    A("python3 -c \"import json,subprocess;d=json.loads(subprocess.run(['node','-e','global.window={};require(\\\"data/sites.js\\\");process.stdout.write(JSON.stringify(window.MASTERDATA))'],capture_output=True,text=True).stdout);print(d['counts'])\"")
    A("```\n")
    A("Expected values at `%s`:" % gen)
    A("")
    A("| Check | Expected |")
    A("|---|---|")
    A("| `\"repo\":` entries in `data/sites.js` | %d |" % len(sites))
    A("| Ledger rows in Section 2 | %d |" % len(sites))
    A("| HTML entry-point sites / README-documentation stubs | %s / %s |" % (counts.get("apps"), counts.get("stubs")))
    A("| Pages builds reporting `built` | %s / %d |" % (counts.get("pagesBuilt"), len(sites)))
    A("| Commits summed across listed sites | %s |" % counts.get("commits"))
    A("| Public repos on the account (API) | %s |" % counts.get("publicRepos"))
    A("| Pages sites on the account (API) | %s |" % counts.get("pagesSites"))
    A("| Permanently excluded repositories | %s |" % ", ".join("`%s`" % x for x in counts.get("excluded", [])))
    A("| Unreachable entries | %s |" % counts.get("unreachable"))
    A("| Categories | %s |" % ", ".join("%s (%d)" % (k, v) for k, v in sorted(counts.get("categories", {}).items())))
    A("| Irregularities registered | %d |" % len(irr))
    A("| Entries carrying a description-verification stamp (`lastVerified`) | %s of %d |"
      % (counts.get("proseStamped", 0), len(sites)))
    A("| Entries whose prose was re-read in the latest pass (`%s`) | %s |"
      % (ts(counts.get("proseLatestPass")), counts.get("proseReReadLatestPass", 0)))
    A("| Entries whose prose was carried forward (with a stated reason) | %d |"
      % (len(sites) - counts.get("proseReReadLatestPass", 0)))
    A("| Entries with no prose stamp at all | %s |" % counts.get("proseUnstamped", 0))
    A("| Entries carrying a `verifiedAtSha` commit stamp | %s of %d |"
      % (counts.get("proseShaStamped", 0), len(sites)))
    A("| Entries whose prose is provably behind their repository | %s%s |"
      % (counts.get("proseStale", 0),
         (" (" + ", ".join("`%s`" % r for r in counts.get("proseStaleRepos", [])) + ")")
         if counts.get("proseStaleRepos") else ""))
    A("")
    A("---\n")
    A("## 6. Known Limitations of This Audit\n")
    for c in d["methodology"]["caveats"]:
        A("- %s" % c)
    A("")
    A("---\n")
    A("*This file is generated. Edit `tools/overlay.json` for narrative content, or `tools/build_verification.py` "
      "for structure, then re-run the generator. Do not hand-edit the ledger tables.*")

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote %s (%d lines, %d ledger rows, %d irregularities)" % (
        os.path.relpath(OUT, ROOT), len(L), len(sites), len(irr)))


if __name__ == "__main__":
    main()
