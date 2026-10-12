"""Offline tests for scheduled-audit status rendering in VERIFICATION.md.

The ledger must repeat only verdicts preserved by the scheduled runner. These
fixtures deliberately include a partial run with budget skips so the tests pin
that NOT-RUN is not mistaken for a clean pass and that an older PASS remains a
last-clean timestamp rather than being presented as current.
"""
import os
import unittest

from tools import build_verification as bv


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def report(path, finished, snapshot, outcome, results, requested=None, run_url=""):
    return {
        "path": path,
        "payload": {
            "runner": "tools/scheduled_audit.py",
            "run": {
                "finishedAt": finished,
                "outcome": outcome,
                "requested": requested or list(bv.SCHEDULED_AUDITS),
                "snapshot": snapshot,
                "runUrl": run_url,
            },
            "results": results,
        },
    }


def result(audit, verdict, finished=None, reason="fixture"):
    row = {"audit": audit, "verdict": verdict, "reason": reason}
    if finished:
        row["finishedAt"] = finished
    return row


class ScheduledSummaryTests(unittest.TestCase):
    def test_latest_report_and_last_clean_are_separate_facts(self):
        history = [
            report(
                "reports/scheduled-audit/old.json",
                "2026-10-11T10:00:00Z",
                "2026-10-11T09:00:00Z",
                "CLEAN",
                [result(a, "PASS", "2026-10-11T10:00:00Z") for a in bv.SCHEDULED_AUDITS],
            ),
            report(
                "reports/scheduled-audit/latest.json",
                "2026-10-11T17:00:00Z",
                "2026-10-11T15:00:00Z",
                "PARTIAL",
                [
                    result("audit_kind", "PASS", "2026-10-11T16:59:00Z"),
                    result("audit_descriptions", "NOT-RUN", reason="budget"),
                    result("verify_live", "NOT-RUN", reason="budget"),
                    result("audit_provenance", "NOT-RUN", reason="budget"),
                ],
            ),
        ]
        summary = bv.scheduled_audit_summary(history)
        self.assertEqual(summary["latest"]["path"], "reports/scheduled-audit/latest.json")
        self.assertEqual(summary["latestByAudit"]["audit_descriptions"]["result"]["verdict"], "NOT-RUN")
        self.assertEqual(
            summary["lastCleanByAudit"]["audit_descriptions"]["report"]["path"],
            "reports/scheduled-audit/old.json",
        )
        self.assertEqual(
            summary["lastCleanByAudit"]["audit_provenance"]["result"]["verdict"],
            "PASS",
        )

    def test_summary_never_invents_a_clean_pass_for_missing_or_not_run_audit(self):
        latest = report(
            "reports/scheduled-audit/partial.json",
            "2026-10-11T17:00:00Z",
            "2026-10-11T15:00:00Z",
            "PARTIAL",
            [result("verify_live", "NOT-RUN", reason="budget")],
            requested=["verify_live"],
        )
        summary = bv.scheduled_audit_summary([latest])
        self.assertNotIn("verify_live", summary["lastCleanByAudit"])
        self.assertNotIn("audit_kind", summary["latestByAudit"])


class ScheduledRenderingTests(unittest.TestCase):
    def test_rendering_surfaces_partial_not_run_and_last_clean_with_evidence_links(self):
        history = [
            report(
                "reports/scheduled-audit/latest.json",
                "2026-10-11T17:00:00Z",
                "2026-10-11T15:00:00Z",
                "PARTIAL",
                [
                    result("audit_kind", "PASS", "2026-10-11T16:59:00Z", "145/145 checked"),
                    result("audit_descriptions", "NOT-RUN", reason="needs ~145 requests"),
                    result("verify_live", "NOT-RUN", reason="needs ~812 requests"),
                    result("audit_provenance", "NOT-RUN", reason="needs ~1000 requests"),
                ],
            ),
        ]
        text = bv.render_scheduled_audit_section(
            bv.scheduled_audit_summary(history), "2026-10-11T19:28:51Z"
        )
        self.assertIn("## 4c. Scheduled Audit Layer", text)
        self.assertIn("outcome **`PARTIAL`**", text)
        self.assertIn("`NOT-RUN`: `audit_descriptions`, `verify_live`, `audit_provenance`", text)
        self.assertIn("**NOT-RUN**", text)
        self.assertIn("Last recorded clean pass (`PASS`)", text)
        self.assertIn("2026-10-11T16:59:00Z", text)
        self.assertIn("reports/scheduled-audit/latest.json", text)
        self.assertIn("historical evidence", text)

    def test_no_report_is_explicitly_not_a_verdict(self):
        text = bv.render_scheduled_audit_section(
            bv.scheduled_audit_summary([]), "2026-10-11T19:28:51Z"
        )
        self.assertIn("No committed scheduled-audit report is available", text)
        self.assertNotIn("PASS", text)
        self.assertNotIn("CLEAN", text)

    def test_committed_history_loader_ignores_non_run_json(self):
        history = bv.load_scheduled_audit_history()
        self.assertTrue(history)
        self.assertTrue(all(item["path"].startswith("reports/scheduled-audit/") for item in history))
        self.assertTrue(all(item["payload"].get("run", {}).get("finishedAt") for item in history))


if __name__ == "__main__":
    unittest.main()
