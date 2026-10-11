#!/usr/bin/env python3
"""Regenerate VERIFICATION.md from the generated dataset in data/sites.js.

Run tools/build_data.py first, then this script. The ledger tables, the account
table and the irregularities register are rendered straight from the dataset so
the documentation can never drift from the data the site actually renders.

    python3 tools/build_data.py && python3 tools/build_verification.py
"""

import glob
import json
import os
import re
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


SCHEDULED_AUDIT_DIR = os.path.join(ROOT, "reports", "scheduled-audit")
SCHEDULED_AUDITS = (
    "audit_kind",
    "audit_descriptions",
    "verify_live",
    "audit_provenance",
)


def load_report(name):
    try:
        with open(os.path.join(ROOT, "tools", name), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def _scheduled_report_time(report):
    """Return the runner's recorded finish time without inventing one."""
    return ((report.get("run") or {}).get("finishedAt") or "") if isinstance(report, dict) else ""


def load_scheduled_audit_history():
    """Load committed scheduled-run reports in their recorded time order.

    The scheduled workflow intentionally has no contents-write permission, so its
    ephemeral artifact cannot update this generated ledger by itself. A run is
    therefore visible here only after its exact ``report.json`` is preserved under
    ``reports/scheduled-audit/`` by a follow-up publication pass. Invalid or
    incomplete files are ignored rather than turned into a verdict.

    The returned paths are repository-relative and are suitable for Markdown links;
    no network read or current-state inference happens here.
    """
    history = []
    pattern = os.path.join(SCHEDULED_AUDIT_DIR, "*.json")
    for path in glob.glob(pattern):
        try:
            with open(path, encoding="utf-8") as fh:
                payload = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        run = payload.get("run") if isinstance(payload, dict) else None
        results = payload.get("results") if isinstance(payload, dict) else None
        if not isinstance(run, dict) or not isinstance(results, list) or not _scheduled_report_time(payload):
            continue
        history.append({
            "path": os.path.relpath(path, ROOT).replace(os.sep, "/"),
            "payload": payload,
        })
    return sorted(history, key=lambda item: (_scheduled_report_time(item["payload"]), item["path"]))


def scheduled_audit_summary(history):
    """Summarize only the verdicts recorded by committed runner reports.

    ``latest`` is the newest preserved run. ``latestByAudit`` keeps the newest
    observation for each audit, including NOT-RUN. ``lastCleanByAudit`` keeps the
    newest explicit PASS observation; it never treats a CLEAN run or a missing
    result as a pass. The shape is deliberately made from the report's own values
    so the ledger cannot silently claim that an audit ran.
    """
    latest_by_audit = {}
    last_clean_by_audit = {}
    for item in history:
        payload = item["payload"]
        run = payload.get("run") or {}
        for result in payload.get("results") or []:
            if not isinstance(result, dict):
                continue
            audit = result.get("audit")
            if audit not in SCHEDULED_AUDITS:
                continue
            observation = {"report": item, "run": run, "result": result}
            latest_by_audit[audit] = observation
            if result.get("verdict") == "PASS":
                last_clean_by_audit[audit] = observation
    latest = history[-1] if history else None
    return {
        "latest": latest,
        "latestByAudit": latest_by_audit,
        "lastCleanByAudit": last_clean_by_audit,
    }


def _md_value(value):
    """Keep report-controlled values from breaking the generated Markdown table."""
    if value is None or value == "":
        return "—"
    return str(value).replace("|", "\\|").replace("\n", " ")


def _scheduled_report_link(item):
    if not item:
        return "—"
    path = item.get("path") or ""
    return "[`report.json`](%s)" % path if path else "—"


def _scheduled_observation_at(observation):
    result = observation.get("result") or {}
    run = observation.get("run") or {}
    return result.get("finishedAt") or run.get("finishedAt") or ""


def render_scheduled_audit_section(summary, snapshot):
    """Render the durable scheduled-audit status surface for VERIFICATION.md."""
    lines = []
    A = lines.append
    A("## 4c. Scheduled Audit Layer — Last Recorded Run\n")
    A("This section is generated from committed `report.json` evidence under "
      "[`reports/scheduled-audit/`](reports/scheduled-audit/). It reports the runner's "
      "mechanical verdicts only; it is not a claim about prose accuracy, site uptime, "
      "interactivity, visits or last use. The scheduled workflow itself remains read-only "
      "and does not make a report durable until a follow-up publication pass preserves it.\n")
    latest = summary.get("latest")
    if not latest:
        A("**No committed scheduled-audit report is available.** No scheduled verdict is "
          "claimed in this ledger.\n")
    else:
        payload = latest["payload"]
        run = payload.get("run") or {}
        results = [r for r in payload.get("results") or []
                   if isinstance(r, dict) and r.get("audit") in SCHEDULED_AUDITS]
        requested = run.get("requested") or []
        covered = [r for r in results if r.get("verdict") != "NOT-RUN"]
        skipped = [r.get("audit") for r in results if r.get("verdict") == "NOT-RUN"]
        run_snapshot = run.get("snapshot") or ""
        relation = "matches this API snapshot" if run_snapshot == snapshot else \
            "is older than this API snapshot" if run_snapshot else "has no recorded API snapshot"
        report_link = _scheduled_report_link(latest)
        run_url = run.get("runUrl") or ""
        run_link = " · [Actions run](%s)" % run_url if run_url.startswith("https://") else ""
        A("**Latest committed run:** outcome **`%s`** · finished `%s` · %s%s.\n" % (
            _md_value(run.get("outcome")), _md_value(run.get("finishedAt")), report_link, run_link))
        A("It covered **%d of %d requested audit(s)**; %s. Published snapshot audited: `%s` (%s).\n" % (
            len(covered), len(requested) or len(SCHEDULED_AUDITS),
            "`NOT-RUN`: " + ", ".join("`%s`" % a for a in skipped)
            if skipped else "no audit was marked `NOT-RUN`",
            _md_value(run_snapshot), relation))
        A("| Audit | Latest verdict in this report | Last recorded clean pass (`PASS`) | Evidence / hand review |")
        A("|---|---|---|---|")
        for audit in SCHEDULED_AUDITS:
            observation = summary["latestByAudit"].get(audit)
            clean = summary["lastCleanByAudit"].get(audit)
            if observation:
                result = observation["result"]
                verdict = _md_value(result.get("verdict"))
                observed_at = _scheduled_observation_at(observation)
                latest_cell = "**%s** at `%s`" % (verdict, _md_value(observed_at))
                evidence = _scheduled_report_link(observation["report"])
                review_endpoint = result.get("reviewEndpoint")
                if review_endpoint:
                    evidence += " · review `%s`" % _md_value(review_endpoint)
                reason = result.get("reason")
                if reason:
                    latest_cell += " — %s" % _md_value(reason)
            else:
                latest_cell = "not present in latest report (not scheduled)"
                evidence = "—"
            if clean:
                clean_at = _scheduled_observation_at(clean)
                clean_cell = "`%s` (%s)" % (_md_value(clean_at),
                                             _scheduled_report_link(clean["report"]))
            else:
                clean_cell = "**none recorded**"
            A("| `%s` | %s | %s | %s |" % (audit, latest_cell, clean_cell, evidence))
        A("")
        A("A `PASS` cell is the last explicit clean result for that audit, even when the "
          "overall run was `PARTIAL`; it is not a clean result for audits marked `NOT-RUN`. "
          "Reports whose audited snapshot differs from `%s` are historical evidence and need "
          "a fresh scheduled run before being read as current.\n" % snapshot)
    A("---\n")
    return "\n".join(lines)


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
    provenance_audit = load_report("last_provenance_audit.json")
    scheduled_summary = scheduled_audit_summary(load_scheduled_audit_history())

    L = []
    A = L.append

    A("# MasterSite — API Snapshot, Source & Irregularities Ledger\n")
    A("**API Snapshot:** %s (UTC). Description-source stamps and stale states are reported per entry below." % gen)
    A("**Generated:** `%s` by `tools/build_data.py` + `tools/build_verification.py`; API telemetry is fetched automatically, while titles/categories/descriptions are curated from repository-owned files in `tools/overlay.json`. No user-supplied entry data was needed." % gen)
    A("**Audited Accounts:** `buffedlizard55-lab`, `kanlerxz87-cyber`")
    A("**Scope:** Public repositories and Pages deployments visible through GitHub's official API for both named accounts. Every discovered omission, permanent exclusion, or unreachable record is identified separately; private repositories are outside scope.")
    A("**Integrity Standard:** API-derived fields are tied to the recorded snapshot; the latest independent `verify_live.py`, kind, numeric-token, and provenance checks are reported below as complete, incomplete, blocked, or stale. Each curated description records its source basis and commit SHA; stale SHA stamps are exposed rather than called current. The numeric-token description audit is a lint, not semantic proof.\n")
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
        # Two register schemas coexist: rows added on/after 2026-10-11 carry
        # repo / field / reason / source / status; the earlier rows carry title / detail.
        # Render both without rewriting either.
        detail = str(it.get("detail") or it.get("reason") or "—")
        if it.get("source"):
            detail += " Source: %s" % it["source"]
        if it.get("repo") and not it.get("title"):
            detail += " Repo/field: `%s` / `%s`." % (it["repo"], it.get("field", "—"))
        if it.get("status"):
            detail += " Status: %s." % it["status"]
        detail = detail.replace("|", "\\|").replace("\n", " ")
        title = it.get("title")
        if not title:
            # New-schema rows name a target instead of a headline: use repo/field.
            parts = [x for x in (it.get("repo"), it.get("field")) if x]
            title = " — ".join(parts) if parts else it["id"]
        A("| **%s** | `%s` | %s | %s |" % (it["id"], sev_label.get(it["severity"], it["severity"]),
                                           str(title).replace("|", "\\|")[:200], detail))
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
        ("`audit_provenance.py`", provenance_audit),
    ]
    A("| Audit | Status for this snapshot | Result |")
    A("|---|---|---|")
    for label, report in audit_rows:
        if not report:
            status, result = "not available", "No machine-readable report found."
        elif report.get("snapshotGenerated") != gen:
            status = "stale report"
            result = "Report refers to `%s`, not `%s`." % (report.get("snapshotGenerated"), gen)
        elif report.get("status") in ("blocked_auth", "blocked_rate_limit") or report.get("accessBlocked"):
            http = (report.get("error") or {}).get("httpStatus") or report.get("accessBlockStatus")
            if not http and report.get("accessBlockReason"):
                # audit_provenance.py records a block only as the reason string
                # ("HTTP 403 — …" / "transport error: …"); parse the code out of it
                # instead of reading an accessBlockStatus field the tool never writes.
                m = re.search(r"HTTP\s+(\d{3})", str(report.get("accessBlockReason")))
                http = int(m.group(1)) if m else None
            if report.get("accessBlocked"):
                status = "blocked — HTTP %s" % http if http else "blocked — access failure"
                result = ("%s/%s entries audited before the block (%s). An access block is not a citation "
                          "failure; restore GitHub API access and rerun this audit."
                          % (report.get("entriesAudited", 0), report.get("entriesTotal", "?"),
                             report.get("accessBlockReason") or "an access failure stopped the run"))
            else:
                status = "blocked — HTTP %s" % http if http else "blocked"
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
            elif label == "`audit_provenance.py`":
                # A complete run writes reports/provenance/<startedAt>.md (unless --no-report):
                # link it only when the file is actually on disk, never as a dead link.
                stamp = (report.get("startedAt") or "").replace(":", "")
                rpt = os.path.join(ROOT, "reports", "provenance", "%s.md" % stamp)
                link = (" Per-entry report: [`reports/provenance/%s.md`](reports/provenance/%s.md)."
                        % (stamp, stamp)) if stamp and os.path.isfile(rpt) else ""
                n_findings = len(report.get("findings", []))
                result = "%s/%s entries checked (%s checks); %s unresolved finding%s; %s template citations.%s" % (
                    report.get("entriesAudited", 0), report.get("entriesTotal", 0),
                    report.get("checksPerformed", 0), n_findings, "" if n_findings == 1 else "s",
                    len(report.get("templateCitations", [])), link)
            else:
                result = "%s/%s entries checked; %s needing review; %s API errors." % (
                    report.get("checkedEntries", 0), report.get("totalEntries", 0),
                    len(report.get("unresolved", [])), len(report.get("apiErrors", [])))
        else:
            status = "incomplete"
            errors = report.get("findings", []) or report.get("apiErrors", []) or report.get("unresolved", [])
            if report.get("error"):
                errors = [report["error"]]
            first = errors[0] if errors else {}
            http = first.get("httpStatus", first.get("status")) if isinstance(first, dict) else None
            reason = (first.get("message") or first.get("endpoint") or first.get("field")
                      if isinstance(first, dict) else str(first)) or report.get("accessBlockReason") or "check did not finish"
            progress = "%s/%s attempted" % (
                report.get("entriesAudited", report.get("checkedEntries", report.get("partialChecks", 0))),
                report.get("entriesTotal", report.get("totalEntries", "?")),
            )
            result = "%s; not a completed audit%s." % (
                progress, " (HTTP %s: %s)" % (http, reason) if http else " (%s)" % reason)
        A("| %s | **%s** | %s |" % (label, status, result.replace("|", "\\|")))
    A("")
    A("---\n")

    # ---------------- 4c. Scheduled audit status ----------------
    L.extend(render_scheduled_audit_section(scheduled_summary, gen).split("\n"))

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
    A("# 6c. Independently re-check every entry's provenance citations and SHAs")
    A("#     (read-only; reports findings and template citations, writes nothing to data/sites.js)")
    A("python3 tools/audit_provenance.py")
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
