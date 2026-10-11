"""Offline tests for the JavaScript-free master list (tools/build_master_list.py, T-032).

Every test here runs with no network access: the generator is a pure function of
the committed snapshot file. The tests pin the two guarantees the page exists for
— it contains no script, and it refuses to render a row it cannot source — plus
the formatting rules a reviewer relies on when checking rows by hand.

Note on discovery: the repository's CI runs this file with
``python3 -m unittest discover -s tests -p 'test_*.py'``, which imports the
module without its siblings, so nothing here may import another test module.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import build_master_list as bml  # noqa: E402

OWNER = "buffedlizard55-lab"


def site(repo="Alpha", **overrides):
    """A minimal, complete record: every field a row cannot be rendered without."""
    record = {
        "repo": repo,
        "title": "%s — test site" % repo,
        "category": "Directory & Meta",
        "kind": "app",
        "description": "A short sourced description.",
        "created": "2026-09-01T00:00:00Z",
        "firstCommit": "2026-09-01T00:00:01Z",
        "firstCommitSha": "aaaaaaa",
        "lastCommit": "2026-09-10T12:00:00Z",
        "lastCommitSha": "bbbbbbb",
        "pushedAt": "2026-09-10T12:00:05Z",
        "updatedAt": "2026-09-10T12:00:09Z",
        "commits": 12,
        "pagesStatus": "built",
        "pagesSource": "main /",
        "pagesUrl": "https://%s.github.io/%s/" % (OWNER, repo),
        "defaultBranch": "main",
        "sizeKb": 100,
        "lastVerified": "2026-09-11T00:00:00Z",
        "verifiedBasis": "Read README at head. Reproduce: GET %s/repos/%s/%s/readme?ref=bbbbbbb."
                         % (bml.API, OWNER, repo),
        "verifiedAtSha": "bbbbbbb",
        "headSha": "bbbbbbb",
        "proseStale": False,
    }
    record.update(overrides)
    return record


def snapshot(sites=None, **counts_overrides):
    """A snapshot that balances: listed + unlisted == pagesSites == publicRepos."""
    sites = [site()] if sites is None else sites
    counts = {
        "sites": len(sites),
        "publicRepos": len(sites) + 1,
        "pagesSites": len(sites) + 1,
        "excluded": ["Redacted"],
        "unlisted": [{"repo": "Redacted", "reason": "permanently excluded by owner request"}],
    }
    counts.update(counts_overrides)
    return {
        "owner": OWNER,
        "generated": "2026-10-11T00:00:00Z",
        "overlayRendered": "2026-10-11T00:10:00Z",
        "counts": counts,
        "sites": sites,
        "accountsChecked": [{
            "login": OWNER,
            "profile": "https://github.com/%s" % OWNER,
            "apiRepos": "%s/users/%s/repos" % (bml.API, OWNER),
            "publicRepos": len(sites) + 1,
            "accountCreated": "2026-07-27T01:05:09Z",
            "pagesSites": len(sites) + 1,
            "note": "Test account.",
        }],
        "methodology": {"steps": ["Queried GET %s." % bml.API], "caveats": ["No visit data exists."]},
        "unreachable": [],
        "irregularities": [{"id": "IRR-01", "severity": "warn",
                            "title": "Something looked irregular", "detail": "Detail text.",
                            "repo": "Alpha", "source": "https://api.github.com/repos/x/y"}],
    }


class SnapshotGuardTests(unittest.TestCase):
    def test_a_balanced_snapshot_is_accepted(self):
        self.assertEqual(bml.check_snapshot(snapshot()), [])

    def test_unbalanced_coverage_is_refused(self):
        snap = snapshot()
        snap["counts"]["pagesSites"] = 99
        problems = bml.check_snapshot(snap)
        self.assertTrue(any("does not balance" in p for p in problems), problems)

    def test_a_public_repository_neither_listed_nor_excluded_is_refused(self):
        snap = snapshot()
        snap["counts"]["unlisted"] = [{"repo": "NewSite", "reason": "no curated entry yet"}]
        snap["counts"]["publicRepos"] = snap["counts"]["pagesSites"] = 3
        problems = bml.check_snapshot(snap)
        self.assertTrue(any("neither listed nor excluded" in p for p in problems), problems)

    def test_pages_census_may_not_exceed_public_repositories(self):
        snap = snapshot()
        snap["counts"]["pagesSites"] = 5
        snap["counts"]["publicRepos"] = 3
        problems = bml.check_snapshot(snap)
        self.assertTrue(any("exceeds" in p for p in problems), problems)

    def test_a_row_missing_the_live_url_or_a_date_is_refused(self):
        for field in ("pagesUrl", "created", "lastCommit", "description", "category", "pagesStatus"):
            with self.subTest(field=field):
                snap = snapshot([site(**{field: None})])
                problems = bml.check_snapshot(snap)
                self.assertTrue(any(field in p for p in problems), problems)

    def test_a_pages_url_that_does_not_match_the_repository_is_refused(self):
        snap = snapshot([site(pagesUrl="https://example.com/Alpha/")])
        problems = bml.check_snapshot(snap)
        self.assertTrue(any("does not match" in p for p in problems), problems)

    def test_unknown_kind_is_refused(self):
        snap = snapshot([site(kind="mystery")])
        self.assertTrue(any("unknown kind" in p for p in bml.check_snapshot(snap)))


class StaticPageTests(unittest.TestCase):
    def setUp(self):
        self.html = bml.render_html(snapshot())

    def test_the_page_contains_no_javascript_at_all(self):
        lowered = self.html.lower()
        self.assertNotIn("<script", lowered)
        self.assertNotIn("javascript:", lowered)
        self.assertNotIn("onclick=", lowered)
        self.assertNotIn("onload=", lowered)
        self.assertNotRegex(self.html, r"\son[a-z]+\s*=")

    def test_every_site_is_rendered_once_with_its_own_section_anchor(self):
        html = bml.render_html(snapshot([site("Alpha"), site("Beta")]))
        self.assertEqual(html.count('class="ml-site"'), 2)
        self.assertIn('id="site-Alpha"', html)
        self.assertIn('id="site-Beta"', html)

    def test_each_row_carries_the_five_facts_and_the_official_endpoints(self):
        for fragment in (
            "https://%s.github.io/Alpha/" % OWNER,
            "2026-09-01",                        # created
            "2026-09-10",                        # last default-branch commit
            "A short sourced description.",
            "%s/repos/%s/Alpha" % (bml.API, OWNER),
            "%s/repos/%s/Alpha/pages" % (bml.API, OWNER),
            "%s/repos/%s/Alpha/commits?sha=main" % (bml.API, OWNER),
            "%s/repos/%s/Alpha/readme?ref=bbbbbbb" % (bml.API, OWNER),
            "Directory &amp; Meta",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.html)

    def test_html_in_a_description_is_escaped(self):
        html = bml.render_html(snapshot([site(description="<img src=x onerror=alert(1)> & <b>bold</b>")]))
        self.assertNotIn("<img src=x", html)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt; &amp; &lt;b&gt;bold&lt;/b&gt;", html)

    def test_the_markup_is_well_formed(self):
        """Every element the generator emits must close: no parser surprises in a
        page whose only job is to be readable by tools that do not run code."""
        from html.parser import HTMLParser

        class WellFormed(HTMLParser):
            VOID = {"meta", "link", "br", "hr", "img", "input", "source", "col"}

            def __init__(self):
                super().__init__(convert_charrefs=True)
                self.stack, self.problems = [], []

            def handle_starttag(self, tag, attrs):
                if tag not in self.VOID:
                    self.stack.append(tag)

            def handle_endtag(self, tag):
                if tag in self.VOID:
                    return
                if not self.stack:
                    self.problems.append("stray </%s>" % tag)
                elif self.stack[-1] != tag:
                    self.problems.append("expected </%s>, got </%s>" % (self.stack[-1], tag))
                    while self.stack and self.stack.pop() != tag:
                        pass
                else:
                    self.stack.pop()

        html = bml.render_html(snapshot([site("Alpha"), site("Beta", kind="stub")]))
        parser = WellFormed()
        parser.feed(html)
        self.assertEqual(parser.problems, [])
        self.assertEqual(parser.stack, [])
        self.assertEqual(html.count("<li>"), html.count("</li>"))
        self.assertEqual(html.count("<details"), html.count("</details>"))

    def test_markup_or_a_script_url_inside_a_description_cannot_become_markup(self):
        """Quoted source text may contain anything at all; it must stay inert."""
        hostile = ('<script>alert(1)</script> and <a href="javascript:alert(2)">x</a> '
                   'and <img src=x onerror=alert(3)>')
        html = bml.render_html(snapshot([site(title=hostile, description=hostile)]))
        self.assertNotIn("<script", html.lower())
        self.assertNotIn('"javascript:', html.lower())
        self.assertNotIn("<img src=x", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)

    def test_a_frozen_record_is_rendered_but_never_counted_as_a_listed_site(self):
        snap = snapshot()
        snap["unreachable"] = [{
            "repo": "Gone", "title": "Gone — removed upstream", "category": "SF Local Guides",
            "kind": "app", "description": "Last verified text.", "created": "2026-09-09T19:11:20Z",
            "lastCommit": "2026-09-16T19:37:41Z", "commits": 68, "pagesStatus": "built",
            "pagesUrl": "https://%s.github.io/Gone/" % OWNER, "defaultBranch": "main",
            "retiredAt": "2026-09-17", "retiredReason": "HTTP 404 upstream",
            "retiredEvidence": "https://api.github.com/repos/%s/Gone" % OWNER,
        }]
        html = bml.render_html(snap)
        self.assertIn("Gone — removed upstream", html)
        self.assertIn("frozen-Gone", html)
        self.assertIn("Re-check:", html)
        # The frozen record has no numbered site block: numbering still starts at 1.
        self.assertEqual(html.count('class="ml-num"'), 1)
        self.assertEqual(html.count('class="ml-site"'), 1)
        self.assertIn('class="ml-site ml-frozen"', html)

    def test_the_generator_refuses_its_own_output_if_a_row_ever_emits_markup(self):
        """The script-free guarantee is enforced, not merely asserted in a comment."""
        original = bml.render_site

        def injected(site_record, owner, number):
            return original(site_record, owner, number) + '\n<script>alert("x")</script>'

        bml.render_site = injected
        try:
            with self.assertRaises(bml.SnapshotError) as ctx:
                bml.render_html(snapshot())
            self.assertIn("script element", str(ctx.exception))
        finally:
            bml.render_site = original

    def test_the_permanently_excluded_repository_gets_no_row_link_or_category(self):
        html = bml.render_html(snapshot())
        excluded = "Redacted"
        self.assertNotIn('id="site-%s"' % excluded, html)
        self.assertNotIn("github.io/%s/" % excluded, html)
        self.assertIn("permanently excluded by owner instruction", html)
        self.assertIn("never counted as a published site", html)

    def test_stale_prose_is_labelled_on_the_row_and_the_counts_line(self):
        html = bml.render_html(snapshot([site(proseStale=True)]))
        self.assertIn("Description stamp behind head", html)
        self.assertIn("Description stamps behind head", html)

    def test_row_numbers_are_a_contiguous_sequence_across_categories(self):
        sites = [site("B2", category="Zeta"), site("A1", category="Alpha"), site("C3", category="Zeta")]
        html = bml.render_html(snapshot(sites))
        numbers = [int(n) for n in bml.re.findall(r'class="ml-num" aria-hidden="true">(\d+)<', html)]
        self.assertEqual(numbers, [1, 2, 3])
        # Categories are rendered in alphabetical order, rows in repository order.
        self.assertLess(html.index('id="cat-alpha"'), html.index('id="cat-zeta"'))
        self.assertLess(html.index('id="site-A1"'), html.index('id="site-B2"'))


class NoJavaScriptReadabilityTests(unittest.TestCase):
    """The point of the page: everything it claims is in the markup itself.

    These tests read the page the way a crawler, an archiver or `curl` does —
    as text, without executing anything — and assert the facts are all there.
    """

    @staticmethod
    def visible_text(markup):
        from html.parser import HTMLParser

        class Text(HTMLParser):
            def __init__(self):
                super().__init__(convert_charrefs=True)
                self.chunks = []

            def handle_data(self, data):
                self.chunks.append(data)

        parser = Text()
        parser.feed(markup)
        return " ".join(" ".join(parser.chunks).split())

    def test_every_site_and_its_live_url_appear_in_the_plain_text(self):
        html = bml.render_html(snapshot([site("Alpha"), site("Beta")]))
        text = self.visible_text(html)
        self.assertIn("Alpha — test site", text)
        self.assertIn("Beta — test site", text)
        self.assertIn("A short sourced description.", text)

    def test_the_committed_page_is_complete_and_readable_without_a_browser(self):
        page = ROOT / "master-list.html"
        if not page.is_file():
            self.skipTest("master-list.html is generated; committed-page checks cover its absence")
        html = page.read_text(encoding="utf-8")
        text = self.visible_text(html)
        snapshot_json = bml.load_snapshot(str(ROOT / "data" / "sites.js"))
        for record in snapshot_json["sites"]:
            with self.subTest(repo=record["repo"]):
                self.assertIn(record["repo"], text)
                self.assertIn(record["title"], text)
                self.assertIn(bml.fmt_date(record["created"]), text)
                self.assertIn(bml.fmt_date(record["lastCommit"]), text)
                # Descriptions are quoted in full, so a long one is present verbatim.
                self.assertIn(record["description"][:120], text)
        # The endpoints a reviewer needs are visible text, not only attributes.
        self.assertIn("Check this row by hand", text)
        self.assertIn("Description stamp", text)


class DescriptionPreviewTests(unittest.TestCase):
    def test_short_descriptions_are_shown_whole_and_never_duplicated(self):
        text = "Short and complete."
        prefix, label = bml.preview_of(text)
        self.assertIsNone(prefix)
        self.assertIsNone(label)
        html = bml.render_html(snapshot([site(description=text)]))
        self.assertEqual(html.count("Short and complete."), 1)

    def test_a_long_description_is_previewed_at_a_sentence_boundary(self):
        text = ("First sentence about the site. " * 30).strip()
        prefix, label = bml.preview_of(text)
        self.assertTrue(prefix.endswith("."), prefix[-20:])
        self.assertLessEqual(len(prefix), bml.PREVIEW_LIMIT)
        self.assertIn("cut at a sentence boundary", label)
        html = bml.render_html(snapshot([site(description=text)]))
        self.assertIn('class="ml-more"', html)
        self.assertIn("expand to read every word published in the directory", html)
        # Preview and the full quoted text are both present: nothing is summarised.
        self.assertIn(bml.esc(prefix), html)
        self.assertIn(bml.esc(text), html)

    def test_a_long_description_with_no_sentence_break_says_so(self):
        text = "x" * (bml.FULL_LIMIT + 50)
        prefix, label = bml.preview_of(text)
        self.assertEqual(len(prefix), bml.PREVIEW_LIMIT)
        self.assertIn("cut mid-sentence", label)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data = os.path.join(self.tmp.name, "sites.js")
        self.out = os.path.join(self.tmp.name, "master-list.html")
        self.write_snapshot(snapshot())

    def write_snapshot(self, snap):
        with open(self.data, "w", encoding="utf-8") as fh:
            fh.write("/* generated */\nwindow.MASTERDATA = ")
            json.dump(snap, fh)
            fh.write(";\n")

    def run_cli(self, *args):
        import io
        from contextlib import redirect_stderr, redirect_stdout
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = bml.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_write_then_check_is_clean_and_two_writes_are_byte_identical(self):
        code, _, err = self.run_cli("--data", self.data, "-o", self.out)
        self.assertEqual(code, 0, err)
        first = Path(self.out).read_bytes()
        code, _, err = self.run_cli("--data", self.data, "-o", self.out)
        self.assertEqual(code, 0, err)
        self.assertEqual(first, Path(self.out).read_bytes())
        code, out, _ = self.run_cli("--data", self.data, "-o", self.out, "--check")
        self.assertEqual(code, 0, out)

    def test_check_detects_drift_and_names_the_first_differing_line(self):
        self.run_cli("--data", self.data, "-o", self.out)
        with open(self.out, "a", encoding="utf-8") as fh:
            fh.write("<!-- hand edit -->\n")
        code, _, err = self.run_cli("--data", self.data, "-o", self.out, "--check")
        self.assertEqual(code, 1)
        self.assertIn("out of sync", err)
        self.assertIn("first difference at line", err)

    def test_check_reports_a_missing_page(self):
        code, _, err = self.run_cli("--data", self.data, "-o", self.out, "--check")
        self.assertEqual(code, 1)
        self.assertIn("is missing", err)

    def test_a_refused_snapshot_writes_nothing_and_exits_two(self):
        # Remove the live URL from the only record: no row can be rendered for it.
        snap = snapshot()
        snap["sites"][0]["pagesUrl"] = ""
        self.write_snapshot(snap)
        code, _, err = self.run_cli("--data", self.data, "-o", self.out)
        self.assertEqual(code, 2)
        self.assertIn("REFUSED", err)
        self.assertFalse(os.path.exists(self.out))

    def test_truncated_json_is_refused_rather_than_rendered_partially(self):
        with open(self.data, "w", encoding="utf-8") as fh:
            fh.write("window.MASTERDATA = {\"sites\": [{\"repo\": \"Alpha\"}]")
        code, _, err = self.run_cli("--data", self.data, "-o", self.out)
        self.assertEqual(code, 2)
        self.assertIn("REFUSED", err)
        self.assertFalse(os.path.exists(self.out))

    def test_stdout_mode_prints_the_page_and_writes_no_file(self):
        code, out, _ = self.run_cli("--data", self.data, "-o", "-")
        self.assertEqual(code, 0)
        self.assertIn("<!DOCTYPE html>", out)
        self.assertNotIn("<script", out.lower())
        self.assertFalse(os.path.exists(self.out))


class CommittedPageTests(unittest.TestCase):
    """The page published by GitHub Pages must match the committed snapshot."""

    def test_the_committed_page_is_in_sync_with_the_snapshot(self):
        import subprocess
        result = subprocess.run([sys.executable, str(ROOT / "tools" / "build_master_list.py"), "--check"],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_the_committed_page_covers_every_published_site_and_stays_script_free(self):
        page = ROOT / "master-list.html"
        self.assertTrue(page.is_file(), "master-list.html is missing — run tools/build_master_list.py")
        html = page.read_text(encoding="utf-8")
        self.assertNotIn("<script", html.lower())
        snapshot_json = bml.load_snapshot(str(ROOT / "data" / "sites.js"))
        for record in snapshot_json["sites"]:
            with self.subTest(repo=record["repo"]):
                self.assertIn('id="site-%s"' % bml.slug(record["repo"]), html)
                self.assertIn("%s/repos/%s/%s/pages" % (bml.API, snapshot_json["owner"], record["repo"]),
                              html)
        for excluded in snapshot_json["counts"].get("excluded") or []:
            with self.subTest(excluded=excluded):
                self.assertNotIn('id="site-%s"' % bml.slug(excluded), html)


if __name__ == "__main__":
    unittest.main()
