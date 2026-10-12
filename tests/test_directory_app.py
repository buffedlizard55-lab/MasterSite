"""Offline tests for index.html / app.js rendering (T-035).

The directory page is the owner's front door, and until now every assertion about
it lived in tests/directory.spec.js — a Playwright suite that needs browser
binaries this sandbox cannot download. These tests run the *same* app.js, against
the *same* committed data/sites.js, inside a minimal Node DOM stub, so the
guarantees below are checkable with `python3 -m unittest` and in CI without a
browser:

  1. Every card carries a stable `site-<slug>` anchor id and prints its live Pages
     address as text (the owner's brief: a directory of *links*).
  2. Every jump-bar chip points at an id that actually exists in the rendered
     grid — no chip can outlive the group it names.
  3. Chip counts equal the number of cards in the group they point at.
  4. The jump bar hides itself when the filtered list has fewer than two groups,
     because a nav with one destination is noise.
  5. Family and flat grouping each produce a bar for the groups they actually
     rendered, and the permanently excluded repository never appears anywhere.

Discovery note: CI runs `python3 -m unittest discover -s tests -p 'test_*.py'`,
which imports each module without its siblings, so nothing here may import
another test module.
"""

import html
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_JS = os.path.join(ROOT, "app.js")
DATA_JS = os.path.join(ROOT, "data", "sites.js")
OWNER = "buffedlizard55-lab"

HARNESS = r"""
const fs = require('node:fs');
const vm = require('node:vm');

const DATA_PATH = process.argv[2];
const SEED = JSON.parse(process.argv[3] || '{}');

function makeEl(id) {
  const classes = new Set();
  return {
    id,
    innerHTML: '',
    textContent: '',
    value: '',
    hidden: false,
    style: {},
    attrs: {},
    dataset: {},
    classList: {
      add(c) { classes.add(c); },
      remove(c) { classes.delete(c); },
      contains(c) { return classes.has(c); },
      toggle(c) { classes.has(c) ? classes.delete(c) : classes.add(c); }
    },
    listeners: {},
    addEventListener(t, fn) { (this.listeners[t] = this.listeners[t] || []).push(fn); },
    removeEventListener() {},
    setAttribute(k, v) { this.attrs[k] = String(v); },
    getAttribute(k) { return (k in this.attrs) ? this.attrs[k] : null; },
    removeAttribute(k) { delete this.attrs[k]; },
    focus() { this.focused = true; },
    click() {},
    appendChild() {},
    removeChild() {},
    querySelector() { return null; },
    closest() { return null; },
    getBoundingClientRect() { return { top: 0, left: 0, right: 0, bottom: 0, width: 0, height: 0 }; }
  };
}

const elements = {};
function byId(id) {
  if (!elements[id]) elements[id] = makeEl(id);
  return elements[id];
}

// The real page defines <option> elements in markup; the stub has to supply them
// because readURLState() validates the `sort` parameter against them.
byId('sortSelect').options = [
  { value: 'updated-desc' }, { value: 'updated-asc' }, { value: 'created-desc' },
  { value: 'created-asc' }, { value: 'name-asc' }, { value: 'name-desc' },
  { value: 'commits-desc' }, { value: 'verified-asc' }, { value: 'verified-desc' }
];

// syncControls() re-applies the active state to the filter chips, which the real
// DOM would find with querySelectorAll. Re-derive them from the markup app.js
// just wrote, so the stub exercises the same code path instead of skipping it.
function chipsFrom(containerId, attr) {
  const source = (elements[containerId] && elements[containerId].innerHTML) || '';
  const re = new RegExp('data-' + attr + '="([^"]*)"', 'g');
  const out = [];
  let m;
  while ((m = re.exec(source)) !== null) {
    const el = makeEl(attr + ':' + m[1]);
    el.dataset[attr] = m[1];
    out.push(el);
  }
  return out;
}

const store = Object.assign({}, SEED.localStorage || {});

const win = {
  MASTERDATA: null,
  location: { href: SEED.href || 'https://buffedlizard55-lab.github.io/MasterSite/' },
  history: { pushState() {}, replaceState() {} },
  localStorage: {
    getItem(k) { return (k in store) ? store[k] : null; },
    setItem(k, v) { store[k] = String(v); }
  },
  addEventListener() {},
  requestAnimationFrame() { return 0; },
  scrollTo() {},
  scrollY: 0
};

const doc = {
  getElementById: byId,
  querySelectorAll(sel) {
    if (sel === '[data-cat]') return chipsFrom('categoryChips', 'cat');
    if (sel === '[data-kind]') return chipsFrom('kindChips', 'kind');
    return [];
  },
  querySelector() { return null; },
  addEventListener() {},
  createElement() { return makeEl('created'); },
  documentElement: makeEl('html'),
  body: makeEl('body'),
  activeElement: null
};

const sandbox = {
  window: win,
  document: doc,
  navigator: { clipboard: null },
  console: { log() {}, warn() {}, error() {} },
  URL,
  Date,
  Math,
  JSON,
  Object,
  Array,
  String,
  Number,
  Boolean,
  RegExp,
  Error,
  parseInt,
  parseFloat,
  isNaN,
  encodeURIComponent,
  decodeURIComponent,
  setTimeout,
  clearTimeout
};
sandbox.globalThis = sandbox;

const context = vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(DATA_PATH, 'utf8'), context, { filename: 'data/sites.js' });
vm.runInContext(fs.readFileSync(process.env.APP_JS_PATH, 'utf8'), context, { filename: 'app.js' });

process.stdout.write(JSON.stringify({
  jumpNav: { hidden: byId('jumpNav').hidden, html: byId('jumpNav').innerHTML },
  grid: byId('sitesGrid').innerHTML,
  table: byId('sitesTableBody').innerHTML,
  resultCount: byId('resultCount').innerHTML,
  sites: (win.MASTERDATA && win.MASTERDATA.sites || []).length
}));
"""


def run_app(data_path=None, href=None, family_group=None):
    """Run app.js against a data file and return the rendered containers."""
    seed = {}
    if href:
        seed["href"] = href
    if family_group:
        seed["localStorage"] = {"masterSite.familyGroup": family_group}
    with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False) as fh:
        fh.write(HARNESS)
        harness = fh.name
    env = dict(os.environ, APP_JS_PATH=APP_JS)
    try:
        proc = subprocess.run(
            ["node", harness, data_path or DATA_JS, json.dumps(seed)],
            capture_output=True, text=True, env=env, timeout=180)
    finally:
        os.unlink(harness)
    if proc.returncode != 0:
        raise AssertionError("app.js harness failed:\n%s" % proc.stderr[-4000:])
    return json.loads(proc.stdout)


CARD_ID_RE = re.compile(r'<article class="site-card[^"]*" id="([^"]+)"')
CARD_URL_RE = re.compile(r'<div class="card-url">\s*<a href="([^"]+)"')
SECTION_RE = re.compile(r'<section class="family-group" data-family="([^"]*)" id="([^"]+)">')
CHIP_RE = re.compile(
    r'<a class="jump-chip" href="#([^"]+)">'
    r'<span class="jump-chip-text">(.*?)</span>'
    r'<span class="jump-chip-count">(\d+)</span>'
    r'</a>')


def sections(grid_html):
    """Split the grid into (family_id, section_id, body) per family section."""
    out = []
    marks = [(m.start(), m.group(1), m.group(2)) for m in SECTION_RE.finditer(grid_html)]
    for i, (pos, fam, sid) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(grid_html)
        out.append((fam, sid, grid_html[pos:end]))
    return out


def slugify(value):
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", str(value).lower()))


class DirectoryRenderingTests(unittest.TestCase):
    """Guarantees about the markup app.js emits, checked with no browser."""

    @classmethod
    def setUpClass(cls):
        if not os.path.isfile(DATA_JS):
            raise unittest.SkipTest("data/sites.js is missing")
        cls.family = run_app(family_group="family")
        cls.flat = run_app(family_group="flat")

    # ---- 1. every card is addressable and prints its live address ----------
    def test_every_card_has_a_stable_anchor_id(self):
        ids = CARD_ID_RE.findall(self.family["grid"])
        self.assertEqual(len(ids), self.family["sites"],
                         "every published site must render one addressable card")
        self.assertEqual(len(ids), len(set(ids)), "card ids must be unique")

    def test_every_card_prints_its_live_pages_address(self):
        urls = CARD_URL_RE.findall(self.family["grid"])
        self.assertEqual(len(urls), self.family["sites"])
        for url in urls:
            self.assertTrue(url.startswith("https://%s.github.io/" % OWNER),
                            "card url is not a Pages address: %r" % url)

    def test_card_urls_match_the_committed_snapshot(self):
        with open(DATA_JS, encoding="utf-8") as fh:
            src = fh.read()
        data = json.loads(src.split("window.MASTERDATA = ", 1)[1].rstrip().rstrip(";"))
        expected = [s["pagesUrl"] for s in data["sites"]]
        found = CARD_URL_RE.findall(self.family["grid"])
        self.assertEqual(sorted(expected), sorted(found))

    def test_excluded_repository_never_renders(self):
        for surface in ("grid", "table"):
            self.assertNotIn("ProjX", self.family[surface],
                             "the permanently excluded repository leaked into %s" % surface)

    # ---- 2/3. jump bar targets and counts ----------------------------------
    def _assert_bar_matches_grid(self, rendered):
        grid, nav = rendered["grid"], rendered["jumpNav"]
        self.assertFalse(nav["hidden"], "the jump bar should be visible for a grouped list")
        chips = CHIP_RE.findall(nav["html"])
        self.assertGreaterEqual(len(chips), 2)
        grid_ids = set(CARD_ID_RE.findall(grid)) | {sid for _f, sid, _b in sections(grid)}
        for target, _label, count in chips:
            self.assertIn(target, grid_ids,
                          "jump chip points at #%s, which is not in the grid" % target)
        return chips

    def test_family_grouping_bar_targets_every_section(self):
        rendered = self.family
        chips = self._assert_bar_matches_grid(rendered)
        secs = sections(rendered["grid"])
        self.assertEqual(len(chips), len(secs),
                         "one chip per rendered family section")
        for (fam, sid, body), (target, label, count) in zip(secs, chips):
            # The anchor is derived from the family *id* (stable, curated); the chip
            # shows the family *label* (human-facing). They are deliberately not the
            # same string, so the test checks the id, not the label.
            # Ungrouped sites land in a trailing section whose family is empty;
            # app.js names that anchor "other" rather than an empty slug.
            self.assertEqual(sid, "grp-" + (slugify(fam) if fam else "other"))
            self.assertEqual(target, sid)
            self.assertEqual(int(count), len(CARD_ID_RE.findall(body)),
                             "chip count disagrees with the cards in %r" % html.unescape(label))

    def test_flat_grouping_bar_targets_each_category_card(self):
        rendered = self.flat
        chips = self._assert_bar_matches_grid(rendered)
        cards = CARD_ID_RE.findall(rendered["grid"])
        # Flat mode emits no <section>, so every target must be a card anchor.
        for target, _label, _count in chips:
            self.assertIn(target, cards,
                          "flat-mode chip must anchor on a card, got #%s" % target)
        total = sum(int(c) for _t, _l, c in chips)
        self.assertEqual(total, len(cards),
                         "category counts must cover every rendered card exactly once")

    def test_family_and_flat_bars_render_the_same_number_of_cards(self):
        self.assertEqual(len(CARD_ID_RE.findall(self.family["grid"])),
                         len(CARD_ID_RE.findall(self.flat["grid"])),
                         "grouping is presentation only — it must not add or drop sites")

    # ---- 4. the bar hides itself when it has nothing to offer --------------
    def test_bar_hidden_when_only_one_group_exists(self):
        with open(DATA_JS, encoding="utf-8") as fh:
            src = fh.read()
        data = json.loads(src.split("window.MASTERDATA = ", 1)[1].rstrip().rstrip(";"))
        single = dict(data)
        sites = [dict(s, category="Only Category", family=None) for s in data["sites"][:5]]
        single["sites"] = sites
        single["counts"] = dict(data["counts"], sites=len(sites))
        single["families"] = []
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
            fh.write("window.MASTERDATA = " + json.dumps(single) + ";\n")
            path = fh.name
        try:
            rendered = run_app(data_path=path, family_group="family")
        finally:
            os.unlink(path)
        self.assertTrue(rendered["jumpNav"]["hidden"],
                        "a single-group list must not render a jump bar")
        self.assertEqual(rendered["jumpNav"]["html"], "")

    def test_bar_hidden_when_a_filter_leaves_one_site(self):
        rendered = run_app(href="https://example.invalid/?q=" + "zzz-no-such-site")
        self.assertTrue(rendered["jumpNav"]["hidden"])

    # ---- URL-driven filters keep the bar honest ----------------------------
    def test_category_filter_bar_still_resolves(self):
        with open(DATA_JS, encoding="utf-8") as fh:
            src = fh.read()
        data = json.loads(src.split("window.MASTERDATA = ", 1)[1].rstrip().rstrip(";"))
        category = data["counts"]["categories"]
        biggest = max(category, key=category.get)
        rendered = run_app(href="https://example.invalid/?category=" + biggest.replace(" ", "+"),
                           family_group="family")
        chips = CHIP_RE.findall(rendered["jumpNav"]["html"])
        grid_ids = set(CARD_ID_RE.findall(rendered["grid"])) | {sid for _f, sid, _b in sections(rendered["grid"])}
        for target, _label, _count in chips:
            self.assertIn(target, grid_ids)


if __name__ == "__main__":
    unittest.main(verbosity=2)
