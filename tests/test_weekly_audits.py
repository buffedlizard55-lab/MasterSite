"""Offline tests for the weekly audit coordinator's verdict rules."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from run_scheduled_audits import assess_audit, render_summary  # noqa: E402


class WeeklyAuditAssessmentTests(unittest.TestCase):
    def test_all_four_audits_can_pass_clean_reports(self):
        cases = {
            "verify_live": {
                "complete": True, "checks": 10, "hardMismatchCount": 0, "driftCount": 0,
                "hardMismatches": [], "volatileDrift": [], "unlistedInApi": [],
                "listedNotInApi": [],
            },
            "audit_kind": {
                "complete": True, "checkedEntries": 2, "totalEntries": 2,
                "disagreements": [], "unresolved": [],
            },
            "audit_descriptions": {
                "complete": True, "checkedEntries": 2, "totalEntries": 2,
                "unresolved": [], "apiErrors": [],
            },
            "audit_provenance": {
                "complete": True, "accessBlocked": False, "entriesAudited": 2,
                "entriesTotal": 2, "findings": [], "templateCitations": [],
            },
        }
        for name, report in cases.items():
            with self.subTest(audit=name):
                result = assess_audit(name, 0, report)
                self.assertEqual(result["status"], "pass")
                self.assertEqual(result["findings"], [])

    def test_volatile_drift_requires_refresh_review_but_is_not_called_a_defect(self):
        report = {
            "complete": True,
            "checks": 12,
            "hardMismatchCount": 0,
            "driftCount": 1,
            "hardMismatches": [],
            "volatileDrift": [{
                "entry": "sites[]/Example",
                "field": "pushedAt",
                "committed": "2026-10-01T00:00:00Z",
                "live": "2026-10-10T00:00:00Z",
            }],
            "unlistedInApi": [],
            "listedNotInApi": [],
        }
        result = assess_audit("verify_live", 0, report)
        self.assertEqual(result["status"], "review")
        self.assertIn("snapshot drift", result["findings"][0])
        self.assertIn("snapshot=2026-10-01T00:00:00Z", result["findings"][0])

    def test_provenance_url_templates_are_review_items(self):
        report = {
            "complete": True,
            "entriesAudited": 1,
            "entriesTotal": 1,
            "findings": [],
            "templateCitations": [{
                "repo": "Example",
                "endpoint": "https://api.github.com/repos/example/contents/{path}",
                "status": 404,
            }],
        }
        result = assess_audit("audit_provenance", 0, report)
        self.assertEqual(result["status"], "review")
        self.assertIn("concrete review URL", result["findings"][0])
        self.assertIn("contents/{path}", result["findings"][0])

    def test_incomplete_report_is_never_a_pass(self):
        result = assess_audit("audit_kind", 2, {
            "complete": False,
            "checkedEntries": 0,
            "totalEntries": 145,
            "unresolved": [{"repo": "Example", "status": 403}],
        })
        self.assertEqual(result["status"], "incomplete")
        self.assertTrue(any("incomplete" in item for item in result["findings"]))

    def test_missing_report_or_unexplained_nonzero_exit_is_incomplete(self):
        missing = assess_audit("audit_descriptions", 0, None)
        unexplained = assess_audit("audit_kind", 1, {
            "complete": True, "checkedEntries": 1, "totalEntries": 1,
            "disagreements": [], "unresolved": [],
        })
        self.assertEqual(missing["status"], "incomplete")
        self.assertEqual(unexplained["status"], "incomplete")

    def test_summary_surfaces_snapshot_and_run_link(self):
        text = render_summary({
            "startedAt": "2026-10-11T08:13:00Z",
            "snapshotGenerated": "2026-10-11T15:06:10Z",
            "reviewRequired": True,
            "audits": [{
                "name": "verify_live", "status": "review", "returnCode": 0,
                "metrics": "checks=10; drift=1", "findings": ["snapshot drift in Example"],
            }],
        }, "https://github.com/example/repo/actions/runs/123")
        self.assertIn("2026-10-11T15:06:10Z", text)
        self.assertIn("https://github.com/example/repo/actions/runs/123", text)
        self.assertIn("snapshot drift in Example", text)
        self.assertIn("do not prove", text)


if __name__ == "__main__":
    unittest.main()
