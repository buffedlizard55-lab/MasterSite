#!/usr/bin/env python3
"""Render master-list.html — the whole directory as plain, static HTML.

Why this file exists (TASKS.md T-032, claimed as T-025). ``index.html`` and
``executive-summary.html`` build every row in the browser from ``data/sites.js``,
so a reader without JavaScript — a crawler, a print-out, ``curl``, an archived
copy, or anyone whose ``data/sites.js`` request fails — sees an empty shell.
``SITES.md`` is a Markdown file served as-is, not a page.

This generator renders the **same committed snapshot** (``data/sites.js``) as
static HTML with **no ``<script>`` element of any kind**. One block per published
Pages site, in a fixed order, each carrying the owner's five facts and the exact
official endpoints a reviewer needs:

    live URL · created · last default-branch commit · committed Pages build status
    · the sourced description with its stamp · the API endpoints to re-check it

Nothing here is a new fact. The tool makes **no network calls at all**: every
value is re-emitted from the snapshot the other tools wrote and audited, so it
cannot invent a datum and cannot touch the GitHub rate-limit budget the live
audits depend on. Two guarantees are enforced before anything is written:

  * **fail closed** — if a record is missing a field the row needs (live URL,
    created date, last commit, description, category, Pages status) or its live
    URL does not match the owner/repository pattern, the run aborts and writes
    nothing, rather than printing a blank or a guess;
  * **coverage balances** — ``counts.sites`` must equal the number of records and
    ``listed + unlisted`` must equal the account's Pages census, the same
    accounting ``tools/build_data.py`` asserts; anything in ``counts.unlisted``
    that is not the permanently excluded repository must be published or excluded
    first. A page that under-reports the portfolio must not be publishable.

A repository the owner permanently excluded is never named: the coverage section
states the excluded *count* only.

Usage:
    python3 tools/build_master_list.py            # write master-list.html
    python3 tools/build_master_list.py --check    # fail if it is out of sync
    python3 tools/build_master_list.py -o -       # print to stdout
"""

import argparse
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "sites.js")
OUT_PATH = os.path.join(ROOT, "master-list.html")
OWNER = "buffedlizard55-lab"
API = "https://api.github.com"

# What a row cannot be rendered without. Each of these is a fact the owner's
# brief asks for, or the link that lets a reviewer check the row by hand.
REQUIRED = (
    "repo", "title", "category", "kind", "description",
    "created", "lastCommit", "pagesUrl", "defaultBranch", "pagesStatus",
)

# Description handling. The published descriptions run from ~95 to ~4,400
# characters and are quoted evidence, so they are never rewritten or summarised.
# A long one is shown as a *quoted* prefix (cut at a sentence boundary when one
# is available) plus the full text behind a <details> element, which needs no
# JavaScript. The label always says exactly which cut was made.
PREVIEW_LIMIT = 300
FULL_LIMIT = 600

KIND_LABELS = {
    "app": "HTML entry point",
    "stub": "README / docs stub",
}
KIND_NOTES = {
    "app": "index.html present at the configured published path; this does not prove the page is interactive",
    "stub": "no index.html at the configured published path; the root URL renders the repository README",
}
SEVERITY_LABELS = {
    "critical": "Critical",
    "warn": "Warning",
    "warning": "Warning",
    "info": "Info",
}


class SnapshotError(Exception):
    """The snapshot cannot be rendered honestly — abort, write nothing."""


# --------------------------------------------------------------------------- #
# snapshot
# --------------------------------------------------------------------------- #

def load_snapshot(path=DATA):
    """Parse data/sites.js. Raises SnapshotError on a missing or truncated file."""
    if not os.path.isfile(path):
        raise SnapshotError("%s does not exist — run tools/build_data.py" % path)
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    marker = "window.MASTERDATA"
    if marker not in src:
        raise SnapshotError("%s has no window.MASTERDATA assignment" % path)
    body = src[src.index(marker) + len(marker):].lstrip()
    if not body.startswith("="):
        raise SnapshotError("%s: expected '=' after window.MASTERDATA" % path)
    body = body[1:].strip()
    if body.endswith(";"):
        body = body[:-1].strip()
    try:
        return json.loads(body)
    except ValueError as exc:  # truncated JSON is a hard failure, never a partial page
        raise SnapshotError("%s is not valid JSON: %s" % (path, exc))


def check_snapshot(snapshot):
    """Return a list of reasons the snapshot must not be published. Empty = ok."""
    problems = []
    sites = snapshot.get("sites")
    counts = snapshot.get("counts") or {}
    if not isinstance(sites, list) or not sites:
        return ["the snapshot has no sites[] array"]
    owner = snapshot.get("owner") or OWNER

    for site in sites:
        repo = site.get("repo") or "<missing repo>"
        for field in REQUIRED:
            if site.get(field) in (None, ""):
                problems.append("%s: required field %r is empty — no row can be "
                                "rendered for it" % (repo, field))
        url = site.get("pagesUrl") or ""
        expected = "https://%s.github.io/%s/" % (owner, repo)
        if url and url != expected:
            problems.append("%s: pagesUrl %r does not match the owner/repo Pages "
                            "pattern %r" % (repo, url, expected))
        if site.get("kind") not in KIND_LABELS:
            problems.append("%s: unknown kind %r (expected one of %s)"
                            % (repo, site.get("kind"), sorted(KIND_LABELS)))

    # Coverage accounting. tools/build_data.py asserts len(sites) + len(unlisted)
    # == the account's Pages count; the permanently excluded repository is carried
    # inside counts.unlisted rather than beside it, so it must not be added twice.
    listed = len(sites)
    excluded = counts.get("excluded") or []
    unlisted = counts.get("unlisted") or []
    public = counts.get("publicRepos")
    pages_sites = counts.get("pagesSites")
    if counts.get("sites") != listed:
        problems.append("counts.sites=%r disagrees with %d record(s)"
                        % (counts.get("sites"), listed))
    if unlisted and pages_sites is not None and listed + len(unlisted) != pages_sites:
        problems.append("coverage does not balance: %d listed + %d unlisted != %d Pages sites "
                        "on the account" % (listed, len(unlisted), pages_sites))
    if pages_sites is None:
        problems.append("counts.pagesSites is missing — coverage cannot be stated")
    if public is None:
        problems.append("counts.publicRepos is missing — coverage cannot be stated")
    elif pages_sites is not None and pages_sites > public:
        problems.append("counts.pagesSites=%d exceeds counts.publicRepos=%d"
                        % (pages_sites, public))
    # Anything in counts.unlisted that is not the permanently excluded repository is
    # a public Pages site the snapshot knows about but does not publish.
    stranded = [u.get("repo") for u in unlisted if u.get("repo") not in excluded]
    if stranded:
        problems.append("%s is/are public but neither listed nor excluded (%d item(s) in "
                        "counts.unlisted) — publish or exclude them first"
                        % (", ".join(sorted(str(s) for s in stranded)), len(stranded)))
    return problems


# --------------------------------------------------------------------------- #
# small formatting helpers
# --------------------------------------------------------------------------- #

def esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def fmt_date(iso):
    """'2026-09-12T18:46:56Z' -> '2026-09-12'. Returns None when unusable."""
    if not isinstance(iso, str) or len(iso) < 10 or not iso[:10].count("-") == 2:
        return None
    return iso[:10]


def fmt_num(value):
    if isinstance(value, int):
        return format(value, ",")
    return esc(value)


def time_tag(iso, label=None):
    """A <time> element, or an explicit dash when the value is not recorded."""
    day = fmt_date(iso)
    if not day:
        return '<span class="ml-none" title="not recorded in this snapshot">—</span>'
    return '<time datetime="%s" title="%s">%s</time>' % (esc(iso), esc(iso), esc(label or day))


def preview_of(text):
    """Return (prefix, cut_label) for a long description, else (None, None).

    Deterministic and purely mechanical: the prefix is a verbatim quotation of
    the description's own opening characters, never a rewrite. The label states
    which cut was actually made so the page never claims a tidy sentence break
    it did not find.
    """
    if len(text) <= FULL_LIMIT:
        return None, None
    window = text[:PREVIEW_LIMIT]
    best = -1
    for match in re.finditer(r"[.!?](?:\s|$)", window):
        best = match.end()
    if best > 0:
        return text[:best].rstrip(), "the first %d characters, cut at a sentence boundary" % best
    return text[:PREVIEW_LIMIT].rstrip(), ("the first %d characters, cut mid-sentence because "
                                          "no sentence boundary occurs that early" % PREVIEW_LIMIT)


def slug(repo):
    return re.sub(r"[^A-Za-z0-9_-]", "-", repo)


# --------------------------------------------------------------------------- #
# rendering
# --------------------------------------------------------------------------- #

def badge(text, css, title=None):
    t = ' title="%s"' % esc(title) if title else ""
    return '<span class="ml-badge %s"%s>%s</span>' % (css, t, esc(text))


def source_links(site, owner):
    """The official endpoints for one row — each one openable by hand."""
    repo = site["repo"]
    base = "%s/repos/%s/%s" % (API, owner, repo)
    branch = site.get("defaultBranch") or "main"
    stamp = site.get("verifiedAtSha") or ""
    links = [
        ("live site", site["pagesUrl"]),
        ("GET /repos/%s/%s" % (owner, repo), base),
        ("GET /repos/%s/%s/pages" % (owner, repo), base + "/pages"),
        ("GET /repos/%s/%s/commits?sha=%s" % (owner, repo, branch), base + "/commits?sha=" + branch),
    ]
    if stamp:
        links.append(("GET …/readme?ref=%s (the description stamp)" % stamp, base + "/readme?ref=" + stamp))
    return links


def render_site(site, owner, number):
    repo = site["repo"]
    kind = site.get("kind")
    pages = site.get("pagesStatus") or ""
    out = []
    out.append('<article class="ml-site" id="site-%s">' % esc(slug(repo)))
    out.append("  <h3>")
    out.append('    <span class="ml-num" aria-hidden="true">%d</span>' % number)
    out.append('    <a class="ml-live" href="%s" target="_blank" rel="noopener">%s</a>'
               % (esc(site["pagesUrl"]), esc(site["title"])))
    out.append('    <span class="ml-live-hint">live GitHub Pages site ↗</span>')
    out.append("  </h3>")

    out.append('  <p class="ml-badges">')
    out.append(badge(KIND_LABELS.get(kind, kind or "?"),
                     "ml-kind-%s" % esc(kind or "unknown"),
                     KIND_NOTES.get(kind, "")))
    out.append(badge("Pages build: %s" % pages,
                     "ml-pages-ok" if pages == "built" else "ml-pages-warn",
                     "GitHub's recorded Pages build status inside this snapshot — build metadata, "
                     "not a live uptime check"))
    if site.get("family"):
        out.append(badge("Family: %s" % site["family"], "ml-family",
                         "Curated lane grouping (tools/families.json)"))
    if site.get("proseStale"):
        out.append(badge("Description stamp behind head — re-read queued", "ml-stale",
                         "The description was read at verifiedAtSha, which is behind the snapshot "
                         "head recorded at headSha; see FLAGGED.md FL-10"))
    out.append("  </p>")

    meta = [
        '<a href="https://github.com/%s/%s" target="_blank" rel="noopener">%s/%s</a>'
        % (esc(owner), esc(repo), esc(owner), esc(repo)),
        "Category: <strong>%s</strong>" % esc(site["category"]),
    ]
    if site.get("commits") is not None:
        meta.append("%s commits on %s" % (fmt_num(site["commits"]), esc(site.get("defaultBranch") or "?")))
    out.append('  <p class="ml-meta">%s</p>' % " · ".join(meta))

    rows = [
        ("Created", time_tag(site["created"]),
         "repository created_at, official REST API"),
        ("Last updated (last commit)", time_tag(site["lastCommit"]),
         "newest committer timestamp on the default branch. GitHub's public API exposes no "
         "site-visit or last-use date, so no 'last used' value is published (FLAGGED.md FL-01)"),
        ("First commit", time_tag(site["firstCommit"]), "oldest commit on the default branch"),
    ]
    out.append('  <dl class="ml-dates">')
    for label, value, note in rows:
        out.append('    <div><dt title="%s">%s</dt><dd>%s</dd></div>'
                   % (esc(note), esc(label), value))
    out.append("  </dl>")

    desc = site["description"]
    prefix, cut = preview_of(desc)
    if prefix is None:
        out.append('  <p class="ml-desc">%s</p>' % esc(desc))
    else:
        out.append('  <p class="ml-desc">%s…</p>' % esc(prefix))
        out.append('  <details class="ml-more">')
        out.append("    <summary>Quoted preview: %s. The full sourced description is %s "
                   "characters — expand to read every word published in the directory and "
                   "check it by hand.</summary>" % (esc(cut), fmt_num(len(desc))))
        out.append('    <p class="ml-desc ml-desc-full">%s</p>' % esc(desc))
        out.append("  </details>")

    stamp_bits = []
    if site.get("verifiedAtSha"):
        stamp_bits.append('read at <a href="%s/repos/%s/%s/commits/%s" target="_blank" rel="noopener">%s</a>'
                          % (API, esc(owner), esc(repo), esc(site["verifiedAtSha"]), esc(site["verifiedAtSha"])))
    if site.get("lastVerified"):
        stamp_bits.append("on %s" % time_tag(site["lastVerified"]))
    if site.get("headSha"):
        stamp_bits.append("default-branch head at snapshot: %s" % esc(site["headSha"]))
    out.append('  <p class="ml-stamp">Description stamp: %s</p>'
               % (" · ".join(stamp_bits) if stamp_bits else "not recorded"))

    links = " · ".join('<a href="%s" target="_blank" rel="noopener">%s</a>' % (esc(u), esc(t))
                       for t, u in source_links(site, owner))
    out.append('  <p class="ml-sources">Check this row by hand: %s</p>' % links)
    out.append("</article>")
    return "\n".join(out)


def render_frozen(entry, owner):
    repo = entry.get("repo") or "?"
    out = ['<article class="ml-site ml-frozen" id="frozen-%s">' % esc(slug(repo))]
    out.append("  <h3><span class=\"ml-frozen-mark\" aria-hidden=\"true\">×</span> %s</h3>"
               % esc(entry.get("title") or repo))
    out.append('  <p class="ml-badges">%s%s</p>'
               % (badge("Removed upstream — frozen record", "ml-pages-warn",
                        "The repository no longer resolves through the official API; the last "
                        "verified values are preserved instead of deleted (TASKS.md T-004)"),
                  badge("Excluded from live counts", "ml-family", "")))
    facts = [
        ("Last verified values", "created %s · last commit %s · %s commits · recorded Pages build %s"
         % (fmt_date(entry.get("created")) or "—", fmt_date(entry.get("lastCommit")) or "—",
            fmt_num(entry.get("commits")), esc(entry.get("pagesStatus") or "—"))),
    ]
    if entry.get("retiredAt"):
        facts.append(("Recorded unreachable at", esc(entry["retiredAt"])))
    if entry.get("retiredReason"):
        facts.append(("Reason on record", esc(entry["retiredReason"])))
    out.append('  <dl class="ml-dates">')
    for label, value in facts:
        out.append("    <div><dt>%s</dt><dd>%s</dd></div>" % (esc(label), value))
    out.append("  </dl>")
    if entry.get("description"):
        out.append('  <p class="ml-desc">%s</p>' % esc(entry["description"]))
    evidence = entry.get("retiredEvidence")
    ev_links = []
    if isinstance(evidence, str) and evidence.startswith("http"):
        ev_links.append(('<a href="%s" target="_blank" rel="noopener">retirement evidence</a>' % esc(evidence)))
    ev_links.append('<a href="%s/repos/%s/%s" target="_blank" rel="noopener">GET /repos/%s/%s (current answer)</a>'
                    % (API, esc(owner), esc(repo), esc(owner), esc(repo)))
    ev_links.append('<a href="%s/repos/%s/%s/pages" target="_blank" rel="noopener">GET …/%s/pages</a>'
                    % (API, esc(owner), esc(repo), esc(repo)))
    out.append('  <p class="ml-sources">Re-check: %s</p>' % " · ".join(ev_links))
    out.append("</article>")
    return "\n".join(out)


def render_category(category, sites, owner, start_number):
    anchor = "cat-" + slug(category).lower()
    out = ['<section class="ml-category" id="%s">' % esc(anchor),
           "  <h2>%s <span class=\"ml-count\">%d site%s</span></h2>"
           % (esc(category), len(sites), "" if len(sites) == 1 else "s")]
    number = start_number
    for site in sites:
        out.append(render_site(site, owner, number))
        number += 1
    out.append("</section>")
    return "\n".join(out), number


def render_irregularities(snapshot, known_repos, owner):
    irregularities = snapshot.get("irregularities") or []
    if not irregularities:
        return ""
    counts = {}
    for item in irregularities:
        counts[item.get("severity")] = counts.get(item.get("severity"), 0) + 1
    summary = " · ".join("%s %d" % (SEVERITY_LABELS.get(k, k), counts[k])
                         for k in sorted(counts, key=lambda k: -counts[k]))
    out = ['<section class="ml-panel" id="irregularities">',
           "  <h2>Flagged irregularities and discrepancies <span class=\"ml-count\">%d open register rows</span></h2>"
           % len(irregularities),
           '  <p class="ml-panel-sub">%s. Every row below is a recorded irregularity from the '
           "snapshot's own register; the directory takes no position on unresolved ones and the "
           'reviewer-facing register lives in <a href="https://github.com/%s/MasterSite/blob/main/FLAGGED.md" '
           'target="_blank" rel="noopener">FLAGGED.md</a>.</p>' % (esc(summary), esc(owner)),
           '  <div class="ml-table-wrap">',
           '    <table class="ml-table">',
           "      <caption>Snapshot irregularity register, rendered without JavaScript</caption>",
           "      <thead><tr><th scope=\"col\">ID</th><th scope=\"col\">Severity</th>"
           "<th scope=\"col\">Repository / area</th><th scope=\"col\">Finding</th>"
           "<th scope=\"col\">Status</th><th scope=\"col\">Source</th></tr></thead>",
           "      <tbody>"]
    for item in irregularities:
        sev = item.get("severity") or "info"
        repo = item.get("repo") or ""
        area = esc(repo) if repo else '<span class="ml-none">—</span>'
        if repo in known_repos:
            area = ('<a href="https://github.com/%s/%s" target="_blank" rel="noopener">%s</a>'
                    % (esc(owner), esc(repo), esc(repo)))
        heading = item.get("title") or item.get("reason") or item.get("field") or ""
        detail = item.get("detail") or ""
        finding = esc(heading)
        if detail:
            finding += ('<details class="ml-more"><summary>Full recorded detail</summary>'
                        '<p class="ml-desc">%s</p></details>' % esc(detail))
        source = item.get("source")
        if isinstance(source, str) and source.startswith("http"):
            source_cell = ('<a href="%s" target="_blank" rel="noopener">recorded source</a>' % esc(source))
        elif repo in known_repos:
            source_cell = ('<a href="%s/repos/%s/%s" target="_blank" rel="noopener">repo</a> · '
                           '<a href="%s/repos/%s/%s/pages" target="_blank" rel="noopener">pages</a>'
                           % (API, esc(owner), esc(repo), API, esc(owner), esc(repo)))
        else:
            source_cell = '<span class="ml-none">—</span>'
        out.append("        <tr><td class=\"ml-nowrap\">%s</td><td class=\"ml-nowrap\">%s</td>"
                   "<td>%s</td><td>%s</td><td class=\"ml-nowrap\">%s</td><td class=\"ml-nowrap\">%s</td></tr>"
                   % (esc(item.get("id") or "?"),
                      esc(SEVERITY_LABELS.get(sev, sev)),
                      area, finding,
                      esc(item.get("status") or "open"),
                      source_cell))
    out += ["      </tbody>", "    </table>", "  </div>", "</section>"]
    return "\n".join(out)


def render_accounts(snapshot, owner):
    accounts = snapshot.get("accountsChecked") or []
    if not accounts:
        return ""
    out = ['<section class="ml-panel" id="accounts">',
           "  <h2>Audited GitHub accounts</h2>",
           '  <p class="ml-panel-sub">Both accounts in scope, read through the official GitHub REST API. '
           "A login with zero public repositories contributes zero public Pages sites; private "
           "repositories are outside this directory's scope and are not enumerated.</p>",
           '  <div class="ml-table-wrap">',
           '    <table class="ml-table">',
           "      <caption>Accounts covered by this snapshot</caption>",
           "      <thead><tr><th scope=\"col\">Account</th><th scope=\"col\">Public repositories</th>"
           "<th scope=\"col\">Pages sites</th><th scope=\"col\">Account created</th>"
           "<th scope=\"col\">Official endpoint</th></tr></thead>",
           "      <tbody>"]
    for acc in accounts:
        login = acc.get("login") or "?"
        profile = acc.get("profile") or ("https://github.com/" + login)
        endpoint = acc.get("apiRepos") or ("%s/users/%s/repos" % (API, login))
        out.append("        <tr><td><a href=\"%s\" target=\"_blank\" rel=\"noopener\">%s</a></td>"
                   "<td>%s</td><td>%s</td><td>%s</td>"
                   "<td><a href=\"%s\" target=\"_blank\" rel=\"noopener\">GET /users/%s/repos</a></td></tr>"
                   % (esc(profile), esc(login),
                      fmt_num(acc.get("publicRepos")),
                      fmt_num(acc.get("pagesSites")),
                      time_tag(acc.get("accountCreated")),
                      esc(endpoint), esc(login)))
        note = acc.get("note")
        if note:
            out.append('        <tr class="ml-account-note"><td colspan="5">%s</td></tr>' % esc(note))
    out += ["      </tbody>", "    </table>", "  </div>", "</section>"]
    return "\n".join(out)


def render_html(snapshot):
    owner = snapshot.get("owner") or OWNER
    sites = snapshot["sites"]
    counts = snapshot.get("counts") or {}
    accounts = snapshot.get("accountsChecked") or []
    methodology = snapshot.get("methodology") or {}
    generated = snapshot.get("generated") or ""
    overlay_rendered = snapshot.get("overlayRendered") or ""
    known_repos = {s["repo"] for s in sites}

    ordered = sorted(sites, key=lambda s: (s["category"].casefold(), s["repo"].casefold()))
    categories = {}
    for site in ordered:
        categories.setdefault(site["category"], []).append(site)
    cat_order = sorted(categories, key=lambda c: (c.casefold(),))

    stale = sum(1 for s in sites if s.get("proseStale"))
    built = sum(1 for s in sites if s.get("pagesStatus") == "built")
    other = len(sites) - built
    apps = sum(1 for s in sites if s.get("kind") == "app")
    stubs = len(sites) - apps
    excluded = counts.get("excluded") or []
    unlisted = counts.get("unlisted") or []

    second = next((a for a in accounts if a.get("login") != owner), None)

    tiles = [
        ("Listed public Pages sites", fmt_num(len(sites)),
         "one block per repository in this page"),
        ("Public repositories", fmt_num(counts.get("publicRepos")),
         "%d listed + %d permanently excluded by owner instruction + %d unlisted"
         % (len(sites), len(excluded), len(unlisted))),
        ("HTML entry point / stub", "%s / %s" % (fmt_num(apps), fmt_num(stubs)),
         "presence of index.html at the configured published path"),
        ("Pages build status", "%s built · %s other" % (fmt_num(built), fmt_num(other)),
         "as recorded in this snapshot — build metadata, not a live check"),
        ("Commits across all sites", fmt_num(counts.get("commits")),
         "sum of default-branch commit counts at the snapshot"),
        ("Description stamps behind head", fmt_num(stale),
         "queued for re-reading at the current head (FLAGGED.md FL-10)"),
    ]

    out = []
    add = out.append
    add("<!DOCTYPE html>")
    add('<html lang="en">')
    add("<head>")
    add('  <meta charset="UTF-8">')
    add('  <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    add("  <title>Master List — every public GitHub Pages site · MasterSite</title>")
    add('  <meta name="description" content="Static, JavaScript-free master list of every public '
        "GitHub Pages site of %s and %s: live link, category, sourced description, creation date, "
        'last default-branch commit and the official API endpoints to check each row by hand.">'
        % (esc(owner), esc(second.get("login") if second else "kanlerxz87-cyber")))
    add('  <link rel="canonical" href="https://%s.github.io/MasterSite/master-list.html">' % esc(owner))
    add('  <link rel="stylesheet" href="styles.css">')
    add('  <link rel="stylesheet" href="master-list.css">')
    add('  <link rel="icon" href="data:image/svg+xml,<svg xmlns=\'http://www.w3.org/2000/svg\' '
        "viewBox='0 0 100 100'><text y='0.9em' font-size='90'>📄</text></svg>\">")
    add("</head>")
    add('<body class="ml-body">')
    add('<a class="skip-link" href="#master-list">Skip to the master list</a>')

    add('<header class="ml-hero">')
    add('  <div class="wrap">')
    add('    <nav class="ml-nav" aria-label="Breadcrumb">'
        '<a href="index.html">← Full directory</a>'
        '<span class="ml-sep" aria-hidden="true">·</span>'
        '<a href="executive-summary.html">Executive summary</a>'
        '<span class="ml-sep" aria-hidden="true">·</span>'
        '<a href="https://github.com/%s/MasterSite/blob/main/SITES.md" target="_blank" rel="noopener">'
        "Plain list on GitHub (SITES.md)</a></nav>" % esc(owner))
    add('    <div class="ml-badge-row">')
    add(badge("✓ No JavaScript — this page is static HTML", "ml-kind-app",
              "The page contains no script element; every value is in the markup you are reading"))
    add(badge("Snapshot %s UTC" % esc(generated or "—"), "ml-family",
              "Snapshot generation/completion time, not a simultaneous read of every API field"))
    add(badge("Public Pages sites only", "ml-family",
              "Private repositories are out of scope and are not enumerated"))
    add('    </div>')
    add("    <h1>Master list — every public GitHub Pages site</h1>")
    if snapshot.get("apiCollection"):
        collection = snapshot["apiCollection"]
        add('    <p class="ml-panel-sub"><strong>Original API read window:</strong> %s → %s (UTC). '
            'The snapshot stamp marks completion, not the time of every read. Checkpoint replay keeps '
            'the original read times in each per-site record.</p>'
            % (time_tag(collection.get("oldestReadAt"), label=collection.get("oldestReadAt")),
               time_tag(collection.get("newestReadAt"), label=collection.get("newestReadAt"))))
    add('    <p class="ml-tagline">One block per site, in a fixed order: the <strong>live link</strong>, '
        "a <strong>description quoted from the repository's own files</strong>, the <strong>date "
        "created</strong>, the <strong>date of the last default-branch commit</strong>, the "
        "<strong>recorded Pages build status</strong>, and the exact <strong>official endpoints</strong> "
        "to re-check that row by hand. Nothing is invented here: every value is re-emitted from the "
        "committed snapshot by <code>tools/build_master_list.py</code>, and the page loads no data "
        "and runs no code.</p>")
    add('    <div class="ml-tiles">')
    for label, value, note in tiles:
        add('      <div class="ml-tile"><span class="ml-tile-label">%s</span>'
            '<span class="ml-tile-value">%s</span><span class="ml-tile-note">%s</span></div>'
            % (esc(label), value, esc(note)))
    add("    </div>")
    add("  </div>")
    add("</header>")

    add('<main class="wrap" id="master-list">')

    # ---- coverage -------------------------------------------------------- #
    add('<section class="ml-panel" id="coverage">')
    add("  <h2>What this list covers</h2>")
    add('  <ul class="ml-bullets">')
    add("    <li><strong>%s</strong> public repositories were read through the official API for "
        "<code>%s</code> at the snapshot below.</li>"
        % (fmt_num(counts.get("publicRepos")), esc(owner)))
    add("    <li><strong>%s</strong> of them have GitHub Pages enabled and are the census this list "
        "must account for.</li>" % fmt_num(counts.get("pagesSites")))
    add("    <li><strong>%s</strong> are published below, one block each.</li>"
        % fmt_num(len(sites)))
    add("    <li><strong>%d</strong> %s permanently excluded by owner instruction: %s no row, no "
        "link, no description and no category on this page, and %s never counted as a published site.</li>"
        % (len(excluded), "repository is" if len(excluded) == 1 else "repositories are",
           "it has" if len(excluded) == 1 else "they have",
           "it is" if len(excluded) == 1 else "they are"))
    add("    <li>The accounting balances: <strong>%s listed + %s not published = %s Pages sites = "
        "%s public repositories</strong>. This generator refuses to write the page when that sum "
        "stops balancing or when a repository is public but neither published nor excluded, so a "
        "stale or partial snapshot cannot be presented as a complete list.</li>"
        % (fmt_num(len(sites)), fmt_num(len(unlisted)),
           fmt_num(counts.get("pagesSites")), fmt_num(counts.get("publicRepos"))))
    if second:
        add("    <li><strong>%s</strong> reports <strong>%s</strong> public repositories, therefore "
            "zero public Pages sites; that result comes from "
            '<a href="%s/users/%s" target="_blank" rel="noopener">GET /users/%s</a>.</li>'
            % (esc(second.get("login")), fmt_num(second.get("publicRepos")),
               API, esc(second.get("login")), esc(second.get("login"))))
    else:
        add("    <li>The second account in scope, <strong>kanlerxz87-cyber</strong>, reports 0 public "
            "repositories (see the accounts table below).</li>")
    add("    <li>Private repositories are out of scope: the public API cannot enumerate them, so no "
        "claim is made about them.</li>")
    add("  </ul>")
    add("</section>")

    add(render_accounts(snapshot, owner))

    # ---- how to verify --------------------------------------------------- #
    add('<section class="ml-panel" id="how-to-verify">')
    add("  <h2>How to check any row by hand</h2>")
    add('  <p class="ml-panel-sub">Every block on this page links the endpoints it was built from. '
        "Open them in order and the row can be reproduced without trusting this page or the "
        "generator.</p>")
    steps = methodology.get("steps") or []
    if steps:
        add('  <ol class="ml-bullets">')
        for step in steps:
            add("    <li>%s</li>" % esc(step))
        add("  </ol>")
    add('  <h3 class="ml-sub">Limits a reviewer should keep in mind</h3>')
    caveats = methodology.get("caveats") or []
    if caveats:
        add('  <ul class="ml-bullets ml-caveats">')
        for caveat in caveats:
            add("    <li>%s</li>" % esc(caveat))
        add("  </ul>")
    else:
        add('  <p class="ml-panel-sub">The snapshot carries no caveat list — treat the page as '
            "unfinished rather than complete.</p>")
    add("</section>")

    # ---- per-category master list --------------------------------------- #
    add('<nav class="ml-toc" aria-label="Categories">')
    add("  <h2>Jump to a category</h2>")
    add('  <ul class="ml-toc-list">')
    for category in cat_order:
        members = categories[category]
        add('    <li><a href="#cat-%s">%s</a> <span class="ml-count">%d</span></li>'
            % (esc(slug(category).lower()), esc(category), len(members)))
    add("  </ul>")
    add("</nav>")

    number = 1
    for category in cat_order:
        block, number = render_category(category, categories[category], owner, number)
        add(block)

    # ---- frozen records -------------------------------------------------- #
    frozen = snapshot.get("unreachable") or []
    if frozen:
        add('<section class="ml-panel ml-panel-frozen" id="frozen">')
        add("  <h2>Frozen records — removed upstream, kept for the record "
            '<span class="ml-count">%d</span></h2>' % len(frozen))
        add('  <p class="ml-panel-sub">These repositories no longer resolve through the official API. '
            "Their last verified values are preserved instead of being deleted, they are excluded "
            "from every live count above, and whether they were retired on purpose is an open "
            "question for the owner (<code>OWNER-DECISIONS.md</code>). They are listed here so the "
            "list cannot quietly lose them.</p>")
        for entry in frozen:
            add(render_frozen(entry, owner))
        add("</section>")

    add(render_irregularities(snapshot, known_repos, owner))

    # ---- provenance ------------------------------------------------------ #
    add('<section class="ml-panel" id="provenance">')
    add("  <h2>Where every value on this page came from</h2>")
    add('  <ul class="ml-bullets">')
    add("    <li>API snapshot: <code>%s</code>; curated overlay re-render: <code>%s</code>.</li>"
        % (esc(generated or "—"), esc(overlay_rendered or "—")))
    add("    <li>The four endpoints one row is built from are "
        "<code>GET %s/repos/%s/{repo}</code>, <code>GET %s/repos/%s/{repo}/pages</code>, "
        "<code>GET %s/repos/%s/{repo}/commits?sha={default_branch}</code>, plus the live Pages URL. "
        'They are linked in full on every row above and in <a href="SITES.md">SITES.md</a>.</li>'
        % (API, esc(owner), API, esc(owner), API, esc(owner)))
    add("    <li>Account-level reads: %s.</li>"
        % " · ".join('<a href="%s" target="_blank" rel="noopener">GET /users/%s/repos</a>'
                     % (esc(a.get("apiRepos") or "%s/users/%s/repos" % (API, a.get("login"))), esc(a.get("login")))
                     for a in accounts) or "not recorded")
    add("    <li>Descriptions are curated in <code>tools/overlay.json</code> from each repository's "
        "own files and carry a stamp (<code>verifiedAtSha</code>) plus the endpoint that was read; "
        'a stamp behind the snapshot head is flagged on the row and queued in <a href="FLAGGED.md">FLAGGED.md</a>.</li>')
    add("    <li>Generated by <code>tools/build_master_list.py</code>; <code>scripts/validate</code> "
        "§M fails when this page drifts from the snapshot or a row loses its official link.</li>")
    add("  </ul>")
    add("</section>")

    add("</main>")

    add('<footer class="ml-footer">')
    add('  <div class="wrap">')
    add("    <p><strong>MasterSite master list</strong> · rendered from the committed snapshot "
        "<code>%s</code> · no JavaScript, no third-party requests, no tracking.</p>" % esc(generated or "—"))
    add('    <p class="ml-footer-sub">Repository: '
        '<a href="https://github.com/%s/MasterSite" target="_blank" rel="noopener">%s/MasterSite</a> · '
        '<a href="https://github.com/%s/MasterSite/blob/main/VERIFICATION.md" target="_blank" rel="noopener">'
        "Per-entry evidence ledger</a> · "
        '<a href="https://github.com/%s/MasterSite/blob/main/FLAGGED.md" target="_blank" rel="noopener">'
        "Flagged items</a> · "
        '<a href="https://github.com/%s/MasterSite/blob/main/AGENTS.md" target="_blank" rel="noopener">'
        "Scope and source policy</a></p>" % (esc(owner), esc(owner), esc(owner), esc(owner), esc(owner)))
    add("  </div>")
    add("</footer>")
    add("</body>")
    add("</html>")
    result = "\n".join(out) + "\n"

    # The whole point of the page: prove it, do not just claim it. Both patterns
    # require real markup, so a *description* that quotes an event handler or the
    # string "javascript:" as plain (escaped) text stays publishable while a real
    # element or URL scheme is refused.
    if re.search(r"<script\b", result, re.I):
        raise SnapshotError("refusing to write: the static page contains a script element")
    if re.search(r"<\s*[a-z][^>]*\son[a-z]+\s*=", result, re.I):
        raise SnapshotError("refusing to write: the static page contains an inline event handler")
    if re.search(r"\b(?:href|src)\s*=\s*[\"']?\s*javascript:", result, re.I):
        raise SnapshotError("refusing to write: the static page contains a javascript: URL")
    return result


# --------------------------------------------------------------------------- #
# entry point
# --------------------------------------------------------------------------- #

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero if the committed master-list.html is not in sync")
    parser.add_argument("-o", "--out", default=OUT_PATH,
                        help="output path ('-' for stdout); default master-list.html")
    parser.add_argument("--data", default=DATA, help="snapshot to render (default data/sites.js)")
    args = parser.parse_args(argv)

    try:
        snapshot = load_snapshot(args.data)
        problems = check_snapshot(snapshot)
        if problems:
            raise SnapshotError("; ".join(problems))
        rendered = render_html(snapshot)
    except SnapshotError as exc:
        print("master-list: REFUSED — %s" % exc, file=sys.stderr)
        print("master-list: nothing was written.", file=sys.stderr)
        return 2

    if args.out == "-":
        sys.stdout.write(rendered)
        return 0

    if args.check:
        if not os.path.isfile(args.out):
            print("master-list: %s is missing — run python3 tools/build_master_list.py"
                  % os.path.relpath(args.out, ROOT), file=sys.stderr)
            return 1
        with open(args.out, encoding="utf-8") as fh:
            current = fh.read()
        if current != rendered:
            old = current.splitlines()
            new = rendered.splitlines()
            where = next((i for i, (a, b) in enumerate(zip(old, new), 1) if a != b),
                         min(len(old), len(new)) + 1)
            print("master-list: %s is out of sync with %s (first difference at line %d; %d vs %d lines) "
                  "— run python3 tools/build_master_list.py"
                  % (os.path.relpath(args.out, ROOT), os.path.relpath(args.data, ROOT), where,
                     len(old), len(new)), file=sys.stderr)
            return 1
        print("master-list: %s is in sync with %s (%d site blocks)."
              % (os.path.relpath(args.out, ROOT), os.path.relpath(args.data, ROOT),
                 len(snapshot["sites"])))
        return 0

    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(rendered)
    print("master-list: wrote %s (%d bytes, %d site blocks, no script elements)."
          % (os.path.relpath(args.out, ROOT), len(rendered.encode("utf-8")), len(snapshot["sites"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
