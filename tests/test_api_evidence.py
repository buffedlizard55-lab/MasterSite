"""Offline integrity tests for original API read times and per-record sources.

All dates and site values below are synthetic fixtures, not observations of a
public repository. Legacy snapshots without checkpoint metadata remain valid.
"""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import build_master_list as bml
from tools import build_sites_md as bsm
from tools import build_verification as bvg
from tools import export_site_records as esr

OWNER = "buffedlizard55-lab"
PREFIX = "https://api.github.com/repos/" + OWNER + "/Fixture"
START = "2026-10-12T01:00:00Z"
END = "2026-10-12T02:00:00Z"


def fixture():
    source = {"status": 200, "readAt": START}
    site = {"repo": "Fixture", "title": "Fixture site", "category": "Directory & Meta", "family": None,
            "kind": "app", "description": "A brief fixture description sourced from a fixture README.",
            "created": START, "firstCommit": START, "firstCommitSha": "aaaaaaa", "lastCommit": START,
            "lastCommitSha": "bbbbbbb", "pushedAt": START, "updatedAt": START, "commits": 2,
            "pagesStatus": "built", "pagesSource": "main /", "pagesUrl": "https://" + OWNER + ".github.io/Fixture/",
            "defaultBranch": "main", "sizeKb": 1, "flags": [], "lastVerified": START,
            "verifiedBasis": "README at " + PREFIX + "/readme?ref=bbbbbbb", "verifiedAtSha": "bbbbbbb",
            "headSha": "bbbbbbb", "proseStale": False,
            "apiSources": [{**source, "url": PREFIX}, {**source, "url": PREFIX + "/pages"},
                           {**source, "url": PREFIX + "/commits?sha=main&per_page=100&page=1"}]}
    return {"owner": OWNER, "generated": END, "auditDate": END[:10], "sites": [site], "unreachable": [],
            "apiCollection": {"startedAt": START, "completedAt": END, "oldestReadAt": START, "newestReadAt": START,
                              "requests": 3, "responses": 3, "checkpointReplaysThisInvocation": 3,
                              "caveat": "Checkpoint replay retains the original API read times."},
            "accountsChecked": [{"login": OWNER, "profile": "https://github.com/" + OWNER,
                                 "apiRepos": "https://api.github.com/users/" + OWNER + "/repos",
                                 "publicRepos": 1, "accountCreated": START, "pagesSites": 1, "note": "Fixture census."},
                                {"login": "kanlerxz87-cyber", "profile": "https://github.com/kanlerxz87-cyber",
                                 "apiRepos": "https://api.github.com/users/kanlerxz87-cyber/repos",
                                 "publicRepos": 0, "accountCreated": START, "pagesSites": 0, "note": "Fixture empty account."}],
            "counts": {"sites": 1, "apps": 1, "stubs": 0, "commits": 2, "pagesBuilt": 1,
                       "publicRepos": 1, "pagesSites": 1, "excluded": [], "unlisted": [], "unreachable": 0,
                       "proseStamped": 1, "proseShaStamped": 1, "proseUnstamped": 0, "proseStale": 0,
                       "proseStaleRepos": [], "proseReReadLatestPass": 1, "proseLatestPass": START,
                       "categories": {"Directory & Meta": 1}},
            "irregularities": [], "methodology": {"steps": ["Fixture official API read."], "caveats": ["Fixture, not live facts."]}}


class EvidenceValidationTests(unittest.TestCase):
    def test_complete_checkpoint_evidence_is_valid(self):
        self.assertEqual(esr.validate_api_evidence(fixture()), [])

    def test_legacy_snapshot_is_not_forced_to_invent_read_times(self):
        data = fixture()
        del data["apiCollection"]
        del data["sites"][0]["apiSources"]
        self.assertEqual(esr.validate_api_evidence(data), [])
        record = next(iter(esr.build_records(data).values()))
        self.assertNotIn("apiSources", record)
        self.assertNotIn("apiCollection", record)

    def test_losing_collection_while_keeping_sources_is_not_legacy(self):
        data = fixture()
        del data["apiCollection"]
        self.assertTrue(esr.validate_api_evidence(data))

    def test_losing_per_site_sources_fails_closed(self):
        data = fixture()
        del data["sites"][0]["apiSources"]
        self.assertTrue(esr.validate_api_evidence(data))

    def test_missing_invalid_and_non_utc_timestamps_are_not_filled(self):
        for value in (None, "", "yesterday", "2026-10-12T01:00:00+01:00", "2026-13-12T01:00:00Z", "2026-1-2T01:00:00Z"):
            with self.subTest(value=value):
                data = fixture()
                data["apiCollection"]["oldestReadAt"] = value
                self.assertTrue(esr.validate_api_evidence(data))

    def test_inverted_window_fails_closed(self):
        data = fixture()
        data["apiCollection"]["oldestReadAt"] = END
        self.assertTrue(esr.validate_api_evidence(data))

    def test_source_time_outside_window_fails_closed(self):
        for value in ("2026-10-11T01:00:00Z", END):
            with self.subTest(value=value):
                data = fixture()
                data["sites"][0]["apiSources"][0]["readAt"] = value
                self.assertTrue(esr.validate_api_evidence(data))

    def test_answer_newer_than_snapshot_completion_fails_closed(self):
        data = fixture()
        data["apiCollection"]["newestReadAt"] = "2026-10-12T03:00:00Z"
        data["apiCollection"]["completedAt"] = "2026-10-12T03:00:00Z"
        self.assertTrue(esr.validate_api_evidence(data))

    def test_source_urls_must_be_exact_official_endpoints_for_this_repository(self):
        for value in ("http://api.github.com/repos/" + OWNER + "/Fixture", PREFIX + "Other",
                      "https://api.github.com.evil.test/repos/" + OWNER + "/Fixture", "https://[broken",
                      "https://github.com/" + OWNER + "/Fixture", PREFIX + "#unrecorded"):
            with self.subTest(value=value):
                data = fixture()
                data["sites"][0]["apiSources"][0]["url"] = value
                self.assertTrue(esr.validate_api_evidence(data))

    def test_access_block_is_not_a_source_answer(self):
        for status in (None, 0, 401, 403, 429, 500, "200", True):
            with self.subTest(status=status):
                data = fixture()
                data["sites"][0]["apiSources"][0]["status"] = status
                self.assertTrue(esr.validate_api_evidence(data))

    def test_recorded_negative_file_read_is_legitimate_evidence(self):
        data = fixture()
        data["sites"][0]["apiSources"].append({"url": PREFIX + "/contents/absent.md?ref=bbbbbbb", "status": 404, "readAt": START})
        self.assertEqual(esr.validate_api_evidence(data), [])

    def test_metadata_pages_and_commits_each_require_http_200_evidence(self):
        for index in range(3):
            with self.subTest(index=index):
                data = fixture()
                del data["sites"][0]["apiSources"][index]
                self.assertTrue(esr.validate_api_evidence(data))

    def test_counters_and_caveat_cannot_be_omitted_or_guessed(self):
        for field in ("requests", "responses", "checkpointReplaysThisInvocation", "caveat"):
            with self.subTest(field=field):
                data = fixture()
                del data["apiCollection"][field]
                self.assertTrue(esr.validate_api_evidence(data))


class EvidenceSurfaceTests(unittest.TestCase):
    def test_invalid_evidence_never_writes_or_removes_an_existing_record(self):
        data = fixture()
        del data["apiCollection"]
        for argv in (["export_site_records.py"], ["export_site_records.py", "--check"]):
            with self.subTest(argv=argv), tempfile.TemporaryDirectory() as directory:
                out = Path(directory) / "records"
                out.mkdir()
                original = out / "old_record.json"
                original.write_bytes(b'{"historical":"unchanged"}\n')
                with patch.object(esr, "OUTDIR", str(out)), patch.object(esr, "load_snapshot", return_value=data), \
                        patch.object(esr, "build_records", side_effect=AssertionError("must fail before record construction")), \
                        patch.object(esr.sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(esr.main(), 1)
                self.assertEqual(original.read_bytes(), b'{"historical":"unchanged"}\n')
                self.assertEqual(list(out.iterdir()), [original])

    def test_invalid_evidence_does_not_create_an_output_directory(self):
        data = fixture()
        data["apiCollection"]["newestReadAt"] = "yesterday"
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "must_not_exist"
            with patch.object(esr, "OUTDIR", str(out)), patch.object(esr, "load_snapshot", return_value=data), \
                    patch.object(esr.sys, "argv", ["export_site_records.py"]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(esr.main(), 1)
            self.assertFalse(out.exists())

    def test_export_preserves_original_times_and_exact_pagination_url(self):
        data = fixture()
        record = next(iter(esr.build_records(data).values()))
        self.assertEqual(record["apiSources"], data["sites"][0]["apiSources"])
        self.assertEqual(record["apiSources"][0]["readAt"], START)
        self.assertNotEqual(record["apiSources"][0]["readAt"], record["snapshot"])
        self.assertIn(PREFIX + "/commits?sha=main&per_page=100&page=1", record["sourceLinks"])
        self.assertEqual(record["apiCollection"], data["apiCollection"])

    def test_api_refresh_cannot_turn_stale_prose_into_verified_prose(self):
        data = fixture()
        data["sites"][0].update({"verifiedAtSha": "ccccccc", "proseStale": True})
        record = next(iter(esr.build_records(data).values()))
        self.assertFalse(record["verified"])
        self.assertEqual(record["verifiedAtSha"], "ccccccc")
        self.assertEqual(record["verifiedAt"], START)

    def test_static_html_exposes_read_window_without_scripts(self):
        html = bml.render_html(fixture())
        self.assertIn("Original API read window:", html)
        self.assertIn(START, html)
        self.assertIn("checkpoint replay", html.lower())
        self.assertNotIn("<script", html.lower())

    def test_static_html_refuses_to_render_untrusted_timestamp_markup(self):
        data = fixture()
        data["apiCollection"]["oldestReadAt"] = '<script>alert("x")</script>'
        html = bml.render_html(data)
        self.assertNotIn("<script", html.lower())
        self.assertNotIn('alert("x")', html)
        self.assertIn('Original API read window:</strong> <span class="ml-none"', html)

    def test_plain_list_exposes_the_original_window(self):
        text = bsm.render(fixture())
        self.assertIn("| Original API read window |", text)
        self.assertIn(START, text)
        self.assertIn("retains original read times", text)

    def test_generated_ledger_exposes_builder_and_independent_audit_windows(self):
        data = fixture()
        report = {"snapshotGenerated": END, "complete": True, "status": "complete", "checks": 13,
                  "hardMismatchCount": 0, "driftCount": 0, "apiCollection": data["apiCollection"]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            overlay = root / "overlay.json"
            overlay.write_text(json.dumps({"entries": {}, "descriptionNotes": [], "acceptedDescriptionExceptions": {}}))
            out = root / "VERIFICATION.md"
            with patch.object(bvg, "ROOT", directory), patch.object(bvg, "OUT", str(out)), patch.object(bvg, "OVERLAY", str(overlay)), \
                    patch.object(bvg, "load_data", return_value=data), patch.object(bvg, "load_report", return_value=report), \
                    patch.object(bvg, "load_scheduled_audit_history", return_value=[]), contextlib.redirect_stdout(io.StringIO()):
                bvg.main()
            text = out.read_text()
        self.assertIn("**API read window:**", text)
        self.assertIn("Independent audit read windows (UTC)", text)
        self.assertIn("none reuses the builder's answers", text)
        self.assertIn(START, text)
        self.assertIn("checkpoint replay retains original", text.lower())


if __name__ == "__main__":
    unittest.main()
