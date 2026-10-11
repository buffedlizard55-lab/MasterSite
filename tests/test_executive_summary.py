"""Offline unit tests for executive-summary.html and executive-summary.js (T-026).

Executes executive-summary.js inside Node against the committed data/sites.js
snapshot and synthetic edge-case fixtures, verifying line-by-line that:
  1. Every published site row carries its live Pages URL, repository URL,
     official GitHub REST API links (Repo API, Pages API, Commits API), and
     per-site data/sites/<owner>__<repo>.json record.
  2. No prose-stale entry (including entries with flags=[]) or non-built /
     unstamped entry is ever badged '✓ No flags' (health-healthy).
  3. Audited accounts (buffedlizard55-lab, kanlerxz87-cyber) and the four
     frozen unreachable 404 records are surfaced with their official API links.
  4. Permanently excluded repositories never appear in any rendered element.
"""

import json
import os
import re
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(ROOT, "executive-summary.html")
JS_PATH = os.path.join(ROOT, "executive-summary.js")
DATA_PATH = os.path.join(ROOT, "data", "sites.js")
OVERLAY_PATH = os.path.join(ROOT, "tools", "overlay.json")


def run_exec_summary(custom_data_js=None, actions_js=""):
    """Run executive-summary.js in a minimal Node DOM harness and return state."""
    harness = r"""
const fs = require('node:fs');
const vm = require('node:vm');

const elements = {};
function makeEl(id) {
  return {
    id,
    innerHTML: '',
    textContent: '',
    value: '',
    hidden: false,
    style: {},
    listeners: {},
    addEventListener(type, fn) { this.listeners[type] = fn; },
    focus() { this.focused = true; }
  };
}
const ids = [
  'execTableBody', 'execKpis', 'execAuditDate', 'execGenerated',
  'execGenerated2', 'execGenStamp', 'execAccountsDate', 'execCategory',
  'execHealth', 'execSort', 'execSearch', 'execClearSearch',
  'execResultCount', 'execAccountsGrid', 'exec-unreachable-section',
  'execUnreachableList'
];
for (const id of ids) elements[id] = makeEl(id);

const sandbox = {
  window: {},
  document: {
    getElementById(id) {
      if (!elements[id]) elements[id] = makeEl(id);
      return elements[id];
    }
  },
  encodeURIComponent,
  Date,
  Math,
  String,
  Number,
  Boolean,
  Array,
  Object
};
sandbox.global = sandbox;

const dataSrc = process.env.CUSTOM_DATA_JS || fs.readFileSync(%r, 'utf8');
vm.runInNewContext(dataSrc, sandbox);
const appSrc = fs.readFileSync(%r, 'utf8');
vm.runInNewContext(appSrc, sandbox);
%s
process.stdout.write(JSON.stringify({
  elements,
  siteCount: sandbox.window.MASTERDATA ? sandbox.window.MASTERDATA.sites.length : 0,
  unreachableCount: sandbox.window.MASTERDATA ? (sandbox.window.MASTERDATA.unreachable || []).length : 0
}));
""" % (DATA_PATH, JS_PATH, actions_js)

    env = os.environ.copy()
    if custom_data_js is not None:
        env["CUSTOM_DATA_JS"] = custom_data_js
    proc = subprocess.run(
        ["node", "-e", harness],
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    return json.loads(proc.stdout)


def load_snapshot_and_overlay():
    script = (
        "global.window={};require(%r);"
        "process.stdout.write(JSON.stringify(window.MASTERDATA));" % DATA_PATH
    )
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True)
    with open(OVERLAY_PATH, encoding="utf-8") as fh:
        overlay = json.load(fh)
    return json.loads(out.stdout), overlay


class ExecutiveSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot, cls.overlay = load_snapshot_and_overlay()
        cls.rendered = run_exec_summary()

    def test_html_structure_contains_required_containers_and_links(self):
        with open(HTML_PATH, encoding="utf-8") as fh:
            html = fh.read()
        for required_id in (
            'id="execTable"',
            'id="execTableBody"',
            'id="execAccountsGrid"',
            'id="exec-unreachable-section"',
            'id="execUnreachableList"',
        ):
            self.assertIn(required_id, html)
        self.assertIn("https://github.com/buffedlizard55-lab", html)
        self.assertIn("https://github.com/kanlerxz87-cyber", html)
        self.assertIn("https://github.com/buffedlizard55-lab/MasterSite/blob/main/SITES.md", html)
        self.assertIn("https://github.com/buffedlizard55-lab/MasterSite/blob/main/VERIFICATION.md", html)
        self.assertIn("https://github.com/buffedlizard55-lab/MasterSite/blob/main/FLAGGED.md", html)

    def test_every_published_site_renders_nine_cells_and_official_source_links(self):
        tbody = self.rendered["elements"]["execTableBody"]["innerHTML"]
        rows = re.findall(r'<tr data-repo="([^"]+)">(.*?)</tr>', tbody, flags=re.S)
        self.assertEqual(len(rows), len(self.snapshot["sites"]))
        by_repo = dict(rows)

        owner = self.snapshot.get("owner") or "buffedlizard55-lab"
        for site in self.snapshot["sites"]:
            repo = site["repo"]
            self.assertIn(repo, by_repo, f"Missing row for {repo}")
            row_html = by_repo[repo]

            labels = re.findall(r'<td data-label="([^"]+)"', row_html)
            self.assertEqual(
                labels,
                [
                    "Website",
                    "Live link",
                    "Last commit",
                    "Category",
                    "Type",
                    "Build",
                    "Commits",
                    "Created",
                    "Review state",
                ],
                f"Unexpected cell labels for {repo}: {labels}",
            )

            expected_urls = (
                site["pagesUrl"],
                f"https://github.com/{owner}/{repo}",
                f"https://api.github.com/repos/{owner}/{repo}",
                f"https://api.github.com/repos/{owner}/{repo}/pages",
                f"https://api.github.com/repos/{owner}/{repo}/commits?sha={site.get('defaultBranch') or 'main'}",
                f"data/sites/{owner}__{repo}.json",
            )
            for u in expected_urls:
                self.assertIn(f'href="{u}"', row_html, f"{repo} row missing official link {u}")

            if site.get("verifiedAtSha"):
                self.assertIn(
                    f"prose: {site['verifiedAtSha'][:7]}",
                    row_html,
                    f"{repo} row missing description provenance SHA stamp",
                )

    def test_prose_stale_and_non_built_sites_never_render_as_no_flags(self):
        tbody = self.rendered["elements"]["execTableBody"]["innerHTML"]
        by_repo = dict(re.findall(r'<tr data-repo="([^"]+)">(.*?)</tr>', tbody, flags=re.S))

        stale_without_flags = [
            s["repo"]
            for s in self.snapshot["sites"]
            if s.get("proseStale") and not (s.get("flags") or [])
        ]
        self.assertGreaterEqual(
            len(stale_without_flags),
            10,
            "Expected at least the 10 known proseStale entries with empty flags[] in the snapshot",
        )

        for site in self.snapshot["sites"]:
            repo = site["repo"]
            row_html = by_repo[repo]
            must_review = (
                bool(site.get("flags"))
                or bool(site.get("proseStale"))
                or not site.get("lastVerified")
                or not site.get("verifiedAtSha")
                or (site.get("pagesStatus") or "unknown") != "built"
            )
            if must_review:
                self.assertIn("health-review", row_html, f"{repo} must be badged health-review")
                self.assertNotIn("health-healthy", row_html, f"{repo} must not be badged health-healthy")
                if site.get("proseStale"):
                    self.assertIn("PROSE-STALE:", row_html, f"{repo} must explain PROSE-STALE in review reasons")
            elif site.get("kind") == "stub":
                self.assertIn("health-stub", row_html)
            else:
                self.assertIn("health-healthy", row_html)

    def test_review_filter_separates_healthy_from_prose_stale_and_non_built(self):
        res_healthy = run_exec_summary(
            actions_js="""
elements.execHealth.value = 'healthy';
elements.execHealth.listeners.change({ target: elements.execHealth });
"""
        )
        healthy_tbody = res_healthy["elements"]["execTableBody"]["innerHTML"]
        healthy_repos = set(re.findall(r'<tr data-repo="([^"]+)">', healthy_tbody))

        for site in self.snapshot["sites"]:
            if (
                site.get("proseStale")
                or site.get("flags")
                or (site.get("pagesStatus") or "unknown") != "built"
                or site.get("kind") == "stub"
            ):
                self.assertNotIn(site["repo"], healthy_repos)
            else:
                self.assertIn(site["repo"], healthy_repos)

    def test_audited_accounts_and_unreachable_records_render_with_official_links(self):
        accounts_html = self.rendered["elements"]["execAccountsGrid"]["innerHTML"]
        self.assertIn("buffedlizard55-lab", accounts_html)
        self.assertIn("kanlerxz87-cyber", accounts_html)
        self.assertIn("https://api.github.com/users/buffedlizard55-lab", accounts_html)
        self.assertIn("https://api.github.com/users/kanlerxz87-cyber", accounts_html)

        unreachable_sec = self.rendered["elements"]["exec-unreachable-section"]
        self.assertFalse(unreachable_sec["hidden"])
        unreachable_html = self.rendered["elements"]["execUnreachableList"]["innerHTML"]
        for u in self.snapshot.get("unreachable", []):
            repo = u["repo"]
            self.assertIn(repo, unreachable_html)
            self.assertIn(f"https://api.github.com/repos/buffedlizard55-lab/{repo}", unreachable_html)
            self.assertIn(f"https://api.github.com/repos/buffedlizard55-lab/{repo}/pages", unreachable_html)

    def test_excluded_repositories_never_appear_in_rendered_output(self):
        dump = json.dumps(self.rendered["elements"])
        for excluded in self.overlay.get("excluded", []):
            self.assertNotIn(excluded, dump)

    def test_synthetic_edge_cases_escape_html_and_flag_errored_or_unstamped_sites(self):
        base = dict(self.snapshot["sites"][0])
        custom = {
            "owner": "buffedlizard55-lab",
            "generated": "2026-10-11T15:06:10Z",
            "auditDate": "2026-10-11",
            "accountsChecked": [],
            "unreachable": [],
            "sites": [
                {
                    **base,
                    "repo": "SyntheticErrored",
                    "title": "Synthetic <script>alert(1)</script>",
                    "description": "Desc & <img src=x onerror=alert(1)>",
                    "flags": [],
                    "proseStale": False,
                    "pagesStatus": "errored",
                    "lastVerified": "2026-10-11T00:00:00Z",
                    "verifiedAtSha": "abcdef1234567890",
                    "headSha": "abcdef1",
                },
                {
                    **base,
                    "repo": "SyntheticUnstamped",
                    "title": "Synthetic Unstamped",
                    "description": "Clean text",
                    "flags": [],
                    "proseStale": False,
                    "pagesStatus": "built",
                    "lastVerified": None,
                    "verifiedAtSha": None,
                    "headSha": "abcdef1",
                },
            ],
        }
        res = run_exec_summary(custom_data_js="window.MASTERDATA = " + json.dumps(custom) + ";")
        tbody = res["elements"]["execTableBody"]["innerHTML"]
        self.assertNotIn("<script>", tbody)
        self.assertNotIn("<img", tbody)
        self.assertIn("&lt;script&gt;", tbody)
        self.assertIn("Pages API status is &#39;errored&#39; at snapshot", tbody)
        self.assertIn("Missing description verification stamp", tbody)
        self.assertIn("prose: unstamped ⚠", tbody)


if __name__ == "__main__":
    unittest.main()
