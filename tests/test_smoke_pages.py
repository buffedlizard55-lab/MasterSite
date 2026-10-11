"""Offline fixtures only: none of these test titles are published site facts."""
import json
from pathlib import Path
import tempfile
import unittest
import urllib.error

from tools import smoke_pages as smoke


class SmokeTests(unittest.TestCase):
    def setUp(self):
        self.record = {"owner": "buffedlizard55-lab", "repo": "Fixture",
                       "pagesUrl": "https://buffedlizard55-lab.github.io/Fixture/",
                       "pagesStatus": "built", "snapshot": "2026-10-11T00:00:00Z"}

    def observe(self, status=200, body=b"<title>Fixture &amp; Test</title>", content_type="text/html"):
        return smoke.observe(self.record, fetcher=lambda url, timeout: {
            "status": status, "body": body, "finalUrl": url,
            "contentType": content_type, "charset": "utf-8"})

    def test_success_is_separate_from_pages_api_status(self):
        self.record["pagesStatus"] = "errored"
        result = self.observe()
        self.assertEqual(result["httpStatus"], 200)
        self.assertEqual(result["outcome"], "ok")
        self.assertEqual(result["title"], "Fixture & Test")
        self.assertEqual(result["pagesApiStatusAtSnapshot"], "errored")
        self.assertEqual(result["sourceUrl"], self.record["pagesUrl"])
        self.assertIsNotNone(result["checkedAt"])
        self.assertEqual(result["unverifiedFields"], [])

    def test_http_error_is_not_api_build_error(self):
        result = self.observe(status=404)
        self.assertEqual(result["outcome"], "http-error")
        self.assertEqual(result["httpStatus"], 404)
        self.assertEqual(result["pagesApiStatusAtSnapshot"], "built")

    def test_transport_failure_leaves_unknown_values_null(self):
        def fail(url, timeout):
            raise urllib.error.URLError("fixture TLS failure")
        result = smoke.observe(self.record, fetcher=fail)
        self.assertEqual(result["outcome"], "transport-error")
        for field in ("httpStatus", "title", "finalUrl", "contentType"):
            self.assertIsNone(result[field])
            self.assertIn(field, result["unverifiedFields"])

    def test_missing_or_incomplete_title_is_review_not_down(self):
        for body in (b"<h1>Fixture</h1>", b"<title>incomplete", b"<title> </title>"):
            result = self.observe(body=body)
            self.assertEqual(result["outcome"], "review")
            self.assertIsNone(result["title"])
            self.assertEqual(result["unverifiedFields"], ["title"])

    def test_non_html_title_not_inferred(self):
        result = self.observe(content_type="application/json")
        self.assertEqual(result["outcome"], "review")
        self.assertIsNone(result["title"])

    def test_title_is_whitespace_normalized_first_complete_title(self):
        result = self.observe(body=b"<TITLE>  first\n title </TITLE><title>second</title>")
        self.assertEqual(result["title"], "first title")

    def test_truncated_body_does_not_fabricate_title(self):
        result = self.observe(body=b"x" * smoke.MAX_BODY + b"<title>late</title>")
        self.assertTrue(result["bodyTruncated"])
        self.assertIsNone(result["title"])

    def test_bad_charset_preserves_observed_status(self):
        result = smoke.observe(self.record, fetcher=lambda url, timeout: {
            "status": 200, "body": b"<title>fixture</title>", "finalUrl": url,
            "contentType": "text/html", "charset": "invalid-codec"})
        self.assertEqual(result["httpStatus"], 200)
        self.assertEqual(result["outcome"], "review")
        self.assertIsNone(result["title"])

    def test_markdown_escapes_remote_text(self):
        result = self.observe(body=b"<title>&lt;script&gt; | [link] `test`</title>")
        report = smoke.make_report([self.record], [result], smoke.utc_now(), "fixture")
        text = smoke.markdown(report)
        self.assertNotIn("<script>", text)
        self.assertIn("&#124;", text)
        self.assertIn("&#91;link&#93;", text)
        self.assertNotIn("Fixture |", smoke.markdown(report, only_flagged=True))

    def test_flagged_report_contains_exact_source_and_null(self):
        result = self.observe(body=b"fixture")
        text = smoke.markdown(smoke.make_report([self.record], [result], smoke.utc_now()), True)
        self.assertIn(self.record["pagesUrl"], text)
        self.assertIn("null", text)
        self.assertIn("requiring review", text)

    def test_load_records_refuses_empty_or_foreign_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            with self.assertRaises(ValueError):
                smoke.load_records(path)
            file = path / "buffedlizard55-lab__Fixture.json"
            file.write_text(json.dumps(self.record))
            self.assertEqual(len(smoke.load_records(path)), 1)
            self.record["pagesUrl"] = "https://example.com/"
            file.write_text(json.dumps(self.record))
            with self.assertRaises(ValueError):
                smoke.load_records(path)

    def test_failed_body_read_preserves_headers(self):
        result = smoke.observe(self.record, fetcher=lambda url, timeout: {
            "status": 200, "body": b"", "finalUrl": url,
            "contentType": "text/html", "charset": "utf-8", "readError": "fixture timeout"})
        self.assertEqual(result["httpStatus"], 200)
        self.assertEqual(result["outcome"], "review")
        self.assertIsNone(result["title"])

    def test_large_remote_title_cannot_overflow_comment_row(self):
        result = self.observe(body=b"<title>" + b"|" * 50000 + b"</title>")
        report = smoke.make_report([self.record], [result], smoke.utc_now())
        self.assertLess(len(smoke.markdown(report).encode('utf-8')), 12000)
        self.assertEqual(len(report["observations"][0]["title"]), 50000)

    def test_no_https_downgrade_or_credentials(self):
        for url in ("http://example.com/", "https://user:secret@example.com/"):
            with self.assertRaises(ValueError):
                smoke.safe_url(url)
        with self.assertRaises(ValueError):
            smoke.HTTPSRedirects().redirect_request(
                None, None, 302, "redirect", {}, "http://example.com/")


if __name__ == "__main__":
    unittest.main()
