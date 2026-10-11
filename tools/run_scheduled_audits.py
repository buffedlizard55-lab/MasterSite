#!/usr/bin/env python3
"""Run and summarize the four read-only snapshot audits in a safe sequence.

The weekly GitHub Actions workflow invokes this coordinator on a clean checkout.
It runs each existing audit serially (their API clients deliberately throttle
requests), captures stdout/stderr and copies each JSON report into an ignored
artifact directory. It never rebuilds or edits the published site data.

A passing process exit code is not sufficient on its own: incomplete reports,
structured findings, and reported snapshot drift all require review. The
provenance auditor's openable-source templates are also surfaced as review
items (currently tracked by FL-18), even though that auditor distinguishes them
from hard provenance failures.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = Path(".work/weekly-audits")
DEFAULT_TIMEOUT_SECONDS = 90 * 60
MAX_REVIEW_DETAILS = 80
MAX_DETAIL_CHARS = 500

AUDIT_SPECS = (
    ("verify_live", "tools/verify_live.py", "tools/last_live_verify.json"),
    ("audit_kind", "tools/audit_kind.py", "tools/last_kind_audit.json"),
    ("audit_descriptions", "tools/audit_descriptions.py", "tools/last_description_audit.json"),
    ("audit_provenance", "tools/audit_provenance.py", "tools/last_provenance_audit.json"),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_snapshot_timestamp() -> str | None:
    """Read the exact generated timestamp from the committed static snapshot."""
    data_path = ROOT / "data" / "sites.js"
    try:
        source = data_path.read_text(encoding="utf-8")
        payload = source.split("window.MASTERDATA = ", 1)[1].rstrip().rstrip(";")
        return json.loads(payload).get("generated")
    except (OSError, IndexError, json.JSONDecodeError, TypeError):
        return None


def _array(report: dict[str, Any], key: str) -> list[Any]:
    value = report.get(key)
    return value if isinstance(value, list) else []


def _item_label(item: Any) -> str:
    if not isinstance(item, dict):
        return str(item)
    parts = []
    repo = item.get("repo")
    entry = item.get("entry")
    if repo:
        parts.append(str(repo))
    elif entry:
        parts.append(str(entry))
    field = item.get("field")
    if field:
        parts.append(str(field))
    finding = item.get("finding") or item.get("why") or item.get("message")
    detail = item.get("detail")
    if finding:
        parts.append(str(finding))
    if detail:
        parts.append("[%s]" % detail)
    if "committed" in item or "live" in item:
        parts.append("snapshot=%s live=%s" % (item.get("committed"), item.get("live")))
    if "overlayKind" in item or "derivedKind" in item:
        parts.append("overlay=%s derived=%s" % (item.get("overlayKind"), item.get("derivedKind")))
    if "tokens" in item and item.get("tokens"):
        parts.append("tokens=%s" % item.get("tokens"))
    if item.get("status") is not None:
        parts.append("HTTP/status=%s" % item.get("status"))
    source = item.get("source") or item.get("endpoint")
    if source:
        parts.append("source=%s" % source)
    return ": ".join(parts) if parts else json.dumps(item, ensure_ascii=False, sort_keys=True)


def _count(report: dict[str, Any], array_key: str, count_key: str) -> int:
    values = report.get(array_key)
    if isinstance(values, list):
        return len(values)
    try:
        return max(0, int(report.get(count_key, 0)))
    except (TypeError, ValueError):
        return 0


def findings_for(name: str, report: dict[str, Any]) -> list[str]:
    """Extract actionable review items, preserving per-record/source detail."""
    details: list[str] = []

    if name == "verify_live":
        hard = _array(report, "hardMismatches")
        drift = _array(report, "volatileDrift")
        details.extend("hard mismatch: " + _item_label(item) for item in hard)
        details.extend("snapshot drift: " + _item_label(item) for item in drift)
        if not hard and report.get("hardMismatchCount"):
            details.append("%s hard API mismatch(es)" % report["hardMismatchCount"])
        if not drift and report.get("driftCount"):
            details.append(
                "%s volatile drift(s); refresh the snapshot after review (not by itself a data defect)"
                % report["driftCount"]
            )
        for repo in _array(report, "unlistedInApi"):
            details.append("repository listed by API but absent from snapshot: " + str(repo))
        for repo in _array(report, "listedNotInApi"):
            details.append("repository in snapshot but absent from live API: " + str(repo))
        # Compatibility with an older report shape that only had `mismatches`.
        if not hard and not drift and not details:
            details.extend("API mismatch: " + _item_label(item) for item in _array(report, "mismatches"))

    elif name == "audit_kind":
        details.extend("kind disagreement: " + _item_label(item)
                       for item in _array(report, "disagreements"))
        details.extend("unresolved kind check: " + _item_label(item)
                       for item in _array(report, "unresolved"))

    elif name == "audit_descriptions":
        details.extend("description/source review: " + _item_label(item)
                       for item in _array(report, "unresolved"))
        details.extend("README/API access error: " + _item_label(item)
                       for item in _array(report, "apiErrors"))

    elif name == "audit_provenance":
        details.extend("provenance finding: " + _item_label(item)
                       for item in _array(report, "findings"))
        # The provenance tool deliberately reports URL templates separately from
        # hard findings. They still need human repair before every citation is
        # independently openable, so keep them visible to the review queue.
        details.extend("citation template needs a concrete review URL: " + _item_label(item)
                       for item in _array(report, "templateCitations"))

    return details


def metrics_for(name: str, report: dict[str, Any] | None) -> str:
    if report is None:
        return "no machine-readable report was produced"
    if name == "verify_live":
        return "checks=%s; hard mismatches=%s; volatile drift=%s" % (
            report.get("checks", report.get("partialChecks", "?")),
            report.get("hardMismatchCount", len(_array(report, "hardMismatches"))),
            report.get("driftCount", len(_array(report, "volatileDrift"))),
        )
    if name == "audit_kind":
        return "checked=%s/%s; disagreements=%s; unresolved=%s" % (
            report.get("checkedEntries", "?"), report.get("totalEntries", "?"),
            len(_array(report, "disagreements")), len(_array(report, "unresolved")),
        )
    if name == "audit_descriptions":
        return "checked=%s/%s; source/numeric review items=%s; API errors=%s" % (
            report.get("checkedEntries", "?"), report.get("totalEntries", "?"),
            len(_array(report, "unresolved")), len(_array(report, "apiErrors")),
        )
    if name == "audit_provenance":
        return "entries=%s/%s; reproduced checks=%s; hard findings=%s; citation templates=%s" % (
            report.get("entriesAudited", "?"), report.get("entriesTotal", "?"),
            report.get("checksPerformed", "?"), len(_array(report, "findings")),
            len(_array(report, "templateCitations")),
        )
    return "report produced"


def assess_audit(
    name: str,
    return_code: int | None,
    report: dict[str, Any] | None,
    execution_error: str | None = None,
) -> dict[str, Any]:
    """Classify one tool result without treating access failures as a pass."""
    details = findings_for(name, report or {})
    complete = bool(report is not None and report.get("complete") is True)
    incomplete_reasons = []

    if execution_error:
        incomplete_reasons.append(execution_error)
    if report is None:
        incomplete_reasons.append("the auditor did not produce a fresh JSON report")
    elif not complete:
        incomplete_reasons.append("the report is marked incomplete")
        error = report.get("error") or report.get("accessBlockReason")
        if error:
            if isinstance(error, dict):
                error = error.get("message") or json.dumps(error, ensure_ascii=False)
            incomplete_reasons.append("reported access/error reason: %s" % error)
    if return_code not in (None, 0) and not details and complete and not execution_error:
        incomplete_reasons.append("auditor exited %s without a structured finding" % return_code)
    if return_code is None:
        incomplete_reasons.append("auditor process did not return an exit code")

    if incomplete_reasons:
        status = "incomplete"
        details.extend("incomplete: " + reason for reason in incomplete_reasons)
    elif details:
        status = "review"
    else:
        status = "pass"

    return {
        "name": name,
        "status": status,
        "complete": complete,
        "returnCode": return_code,
        "metrics": metrics_for(name, report),
        "findings": details,
        "executionError": execution_error,
    }


def _short_detail(text: str) -> str:
    text = " ".join(str(text).split())
    if len(text) > MAX_DETAIL_CHARS:
        return text[:MAX_DETAIL_CHARS - 1] + "…"
    return text


def render_summary(summary: dict[str, Any], run_url: str | None = None) -> str:
    """Create a bounded, issue-safe Markdown report with the evidence location."""
    review_required = bool(summary.get("reviewRequired"))
    overall = "REVIEW REQUIRED" if review_required else "PASS — no review findings"
    lines = [
        "# Weekly read-only API audit — %s" % summary.get("startedAt", "unknown time"),
        "",
        "- **Overall:** %s" % overall,
        "- **Published snapshot:** `%s`" % (summary.get("snapshotGenerated") or "unknown"),
        "- **Audits:** %d" % len(summary.get("audits", [])),
    ]
    if run_url:
        lines.append("- **Workflow run and retained evidence artifact:** %s" % run_url)
    lines += [
        "",
        "| Audit | Result | Exit | Summary |",
        "|---|---|---:|---|",
    ]
    for audit in summary.get("audits", []):
        metrics = str(audit.get("metrics", "")).replace("|", "\\|")
        lines.append("| `%s` | **%s** | %s | %s |" % (
            audit.get("name", "unknown"), audit.get("status", "incomplete"),
            audit.get("returnCode", "—"), metrics,
        ))

    all_details = [
        (audit.get("name", "audit"), detail)
        for audit in summary.get("audits", [])
        for detail in audit.get("findings", [])
    ]
    if all_details:
        lines += ["", "## Findings and review items", ""]
        for name, detail in all_details[:MAX_REVIEW_DETAILS]:
            lines.append("- **%s:** %s" % (name, _short_detail(detail)))
        if len(all_details) > MAX_REVIEW_DETAILS:
            lines.append("- _%d additional detail row(s) are in the attached workflow artifact._" %
                         (len(all_details) - MAX_REVIEW_DETAILS))
    else:
        lines += ["", "No incomplete audit, API mismatch, snapshot drift, or unresolved citation item was reported."]

    lines += [
        "",
        "## What these checks do not prove",
        "",
        "- `audit_descriptions.py` is a numeric-token lint, not semantic proof of prose.",
        "- `audit_provenance.py` reproduces cited endpoints at recorded refs; it does not establish that prose is current at repository head.",
        "- API metadata does not establish site uptime, browser functionality, or when a site was visited or last used.",
        "- Volatile field drift is shown for refresh review; it is not automatically a semantic/data defect.",
        "",
    ]
    return "\n".join(lines)


def _write_github_outputs(review_required: bool, overall_status: str, markdown: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as handle:
            handle.write("review_required=%s\n" % str(review_required).lower())
            handle.write("overall_status=%s\n" % overall_status)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write(markdown)


def _run_one(
    name: str,
    script: str,
    report_rel: str,
    output_dir: Path,
    timeout_seconds: int,
    env: dict[str, str],
) -> dict[str, Any]:
    log_path = output_dir / (name + ".log")
    evidence_dir = output_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    report_path = ROOT / report_rel
    report_path.unlink(missing_ok=True)

    if name == "audit_descriptions":
        # Do not let a prior local/runner cache turn an API fetch into an old
        # observation. Keys are content-addressed, but this is a fresh scheduled pass.
        shutil.rmtree(ROOT / "tools" / ".readme-cache", ignore_errors=True)

    command = [sys.executable, str(ROOT / script)]
    execution_error = None
    return_code: int | None = None
    with log_path.open("w", encoding="utf-8") as log:
        log.write("$ %s\n\n" % " ".join(command))
        log.flush()
        try:
            result = subprocess.run(
                command,
                cwd=ROOT,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=timeout_seconds,
                check=False,
            )
            return_code = result.returncode
        except subprocess.TimeoutExpired:
            return_code = 124
            execution_error = "auditor exceeded its %d-second timeout" % timeout_seconds
            log.write("\n\nSCHEDULED AUDIT TIMEOUT after %d seconds\n" % timeout_seconds)
        except OSError as exc:
            return_code = 127
            execution_error = "could not start auditor: %s" % exc
            log.write("\n\nSCHEDULED AUDIT START ERROR: %s\n" % exc)

    report: dict[str, Any] | None = None
    evidence_report: str | None = None
    if report_path.is_file():
        try:
            loaded = json.loads(report_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                report = loaded
                destination = evidence_dir / (name + ".json")
                shutil.copy2(report_path, destination)
                evidence_report = str(destination.relative_to(output_dir))
            else:
                execution_error = "auditor JSON report is not an object"
        except (OSError, json.JSONDecodeError) as exc:
            execution_error = "could not read auditor JSON report: %s" % exc

    provenance_markdown: str | None = None
    if name == "audit_provenance" and report:
        started = report.get("startedAt")
        if isinstance(started, str):
            candidate = ROOT / "reports" / "provenance" / (started.replace(":", "") + ".md")
            if candidate.is_file():
                destination = evidence_dir / "audit_provenance.md"
                shutil.copy2(candidate, destination)
                provenance_markdown = str(destination.relative_to(output_dir))

    assessment = assess_audit(name, return_code, report, execution_error)
    assessment.update({
        "tool": script,
        "log": str(log_path.relative_to(output_dir)),
        "report": evidence_report,
        "provenanceMarkdown": provenance_markdown,
    })

    # Keep enough process context in the Actions log for a fast triage; full
    # output is retained in the artifact and linked by the issue body.
    print("[%s] %s (exit %s) — %s" % (
        name, assessment["status"], return_code, assessment["metrics"]))
    if assessment["status"] != "pass":
        for finding in assessment["findings"][:8]:
            print("  - %s" % _short_detail(finding))
    return assessment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR),
                        help="ignored directory for logs and copied reports")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS,
                        help="per-auditor timeout (default: 90 minutes)")
    args = parser.parse_args(argv)
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")

    output_dir_arg = Path(args.output_dir)
    output_dir = output_dir_arg if output_dir_arg.is_absolute() else ROOT / output_dir_arg
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir = output_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    for child in evidence_dir.iterdir():
        if child.is_file():
            child.unlink()
        elif child.is_dir():
            shutil.rmtree(child)

    started_at = utc_now()
    snapshot_generated = load_snapshot_timestamp()
    env = os.environ.copy()
    audits = []
    for name, script, report in AUDIT_SPECS:
        audits.append(_run_one(name, script, report, output_dir, args.timeout_seconds, env))

    finished_at = utc_now()
    review_required = any(audit["status"] != "pass" for audit in audits)
    summary = {
        "schemaVersion": 1,
        "startedAt": started_at,
        "finishedAt": finished_at,
        "snapshotGenerated": snapshot_generated,
        "reviewRequired": review_required,
        "overallStatus": "review-required" if review_required else "pass",
        "audits": audits,
    }
    markdown = render_summary(summary, os.environ.get("RUN_URL"))
    (output_dir / "summary.md").write_text(markdown, encoding="utf-8")
    (output_dir / "run.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_github_outputs(
        review_required,
        summary["overallStatus"],
        markdown,
    )
    print("Weekly read-only audits: %s" % summary["overallStatus"])
    print("Full logs and captured JSON reports: %s" % output_dir.relative_to(ROOT)
          if output_dir.is_relative_to(ROOT) else str(output_dir))
    return 1 if review_required else 0


if __name__ == "__main__":
    raise SystemExit(main())
