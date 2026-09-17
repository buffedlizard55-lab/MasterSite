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

    L = []
    A = L.append

    A("# MasterSite — Comprehensive Line-by-Line Verification Ledger\n")
    A("**Audit Date:** %s (UTC) — full re-verification refresh (prior baselines: 2026-09-16, 2026-09-15, 2026-09-12)" % audit)
    A("**Generated:** `%s` by `tools/build_data.py` + `tools/build_verification.py` — autonomous execution, zero manual data entry" % gen)
    A("**Audited Accounts:** `buffedlizard55-lab`, `kanlerxz87-cyber`")
    A("**Scope:** 100% of public repositories and GitHub Pages deployments hosted under both accounts")
    A("**Integrity Standard:** Zero hallucinations. Every metric, date, commit SHA, Pages status and description is read "
      "directly from official GitHub REST API endpoints and each repository's own source files.\n")
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
    A("- `GET https://api.github.com/repos/%s/{repo}/contents/{published path}/index.html` (app vs. doc-stub classification)" % owner)
    A("- `GET https://api.github.com/repos/%s/{repo}/readme` (description sourcing)\n" % owner)

    A("| # | Repository | Category | Type | Pages Status | Source | Created (UTC) | First Commit (SHA) | Last Commit on Main (UTC) | Latest SHA | Total Commits | Size (KB) | Live Site & Official Sources |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for i, s in enumerate(sites, 1):
        live = s.get("pagesUrl") or ("https://%s.github.io/%s/" % (owner, s["repo"]))
        links = " · ".join([
            "[Live](%s)" % live,
            "[Repo](https://github.com/%s/%s)" % (owner, s["repo"]),
            "[Pages API](https://api.github.com/repos/%s/%s/pages)" % (owner, s["repo"]),
            "[Commits API](https://api.github.com/repos/%s/%s/commits)" % (owner, s["repo"]),
            "[Settings](https://github.com/%s/%s/settings/pages)" % (owner, s["repo"]),
        ])
        A("| %d | `%s` | %s | %s | %s | `%s` | %s | `%s` | %s | `%s` | %s | %s | %s |" % (
            i,
            s["repo"],
            s["category"],
            "Live App" if s["kind"] == "app" else "Doc Stub",
            s["pagesStatus"],
            s["pagesSource"],
            ts(s["created"]),
            s["firstCommitSha"],
            ts(s["lastCommit"]),
            s["lastCommitSha"],
            s["commits"],
            s.get("sizeKb", 0),
            links,
        ))
    A("")
    A("Totals across the %d listed entries: **%s commits on default branches**, **%s apps / %s doc stubs**, "
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
    A("## 4. Line-by-Line Description Verification\n")
    A("Every description in `data/sites.js` is derived from the repository's own `README.md` and published file "
      "structure, fetched through the official contents API. Nothing is written from memory or inference.\n")
    A("**Change log for the %s pass:**\n" % audit)
    for n in ov.get("descriptionNotes", []):
        A("- %s" % n)
    A("")
    A("**Automated cross-check:** a pass over all %d entries extracted every numeric claim from each description and "
      "searched the repository's README for it; claims that no longer appear in the README were re-read by hand and "
      "either re-sourced or removed. That is how the stale `TradingViewTheLeap` \"203-check verifier\", the "
      "`GEMSDOE` \"19/19 rules\" figure and the `BathTubOverflowSF` wave/record counts were caught.\n" % len(sites))
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
    A("# 6. Re-derive the directory from scratch, with zero manual entry")
    A("python3 tools/build_data.py && python3 tools/build_verification.py")
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
    A("| Apps / doc stubs | %s / %s |" % (counts.get("apps"), counts.get("stubs")))
    A("| Pages builds reporting `built` | %s / %d |" % (counts.get("pagesBuilt"), len(sites)))
    A("| Commits summed across listed sites | %s |" % counts.get("commits"))
    A("| Public repos on the account (API) | %s |" % counts.get("publicRepos"))
    A("| Pages sites on the account (API) | %s |" % counts.get("pagesSites"))
    A("| Permanently excluded repositories | %s |" % ", ".join("`%s`" % x for x in counts.get("excluded", [])))
    A("| Unreachable entries | %s |" % counts.get("unreachable"))
    A("| Categories | %s |" % ", ".join("%s (%d)" % (k, v) for k, v in sorted(counts.get("categories", {}).items())))
    A("| Irregularities registered | %d |" % len(irr))
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
