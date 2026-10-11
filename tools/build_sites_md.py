#!/usr/bin/env python3
"""Render SITES.md — the plain, line-by-line master list of published Pages sites.

Why this file exists (owner brief, 2026-10-11): the directory page and the JSON
records are the audit surface, but the owner also asked for one organized,
easy-to-read list where every site is a single line carrying the site's live
link, a brief description of what it is, the date it was created and the date it
was last updated — with the official endpoint that proves each row, so a
reviewer can work down the list and check row after row by hand.

Provenance rules (unchanged from the rest of this repository):

  * Every value comes from `data/sites.js`, which is generated from the GitHub
    REST API by `tools/build_data.py`, or from the curated prose in
    `tools/overlay.json`. Nothing is invented here and nothing is fetched.
  * The description text is the curated wording already published by the
    directory; this script never rewrites or summarizes it.
  * `Created` is GitHub's repository `created_at`. `Last updated` is the newest
    committer timestamp on the default branch. GitHub's public API exposes no
    site-visit or last-use date, so no last-use value is published (FL-01).
  * `built` is Pages build metadata, not a live uptime check (FL-02 / FL-15).

Usage:

    python3 tools/build_sites_md.py            # write SITES.md
    python3 tools/build_sites_md.py --check    # fail if SITES.md is out of sync
    python3 tools/build_sites_md.py -o -       # print to stdout

The output is deterministic: it carries the snapshot timestamp already stored in
`data/sites.js`, never the wall clock, so `--check` is byte-exact and safe to run
in `scripts/validate` and in CI.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "sites.js")
OUT_PATH = os.path.join(ROOT, "SITES.md")
RECORD_DIR = "data/sites"
API = "https://api.github.com"

LEGEND = """\
## How to read this list

| Field | Official source | Note |
|---|---|---|
| **Site** | `GET /repos/{owner}/{repo}/pages` → `html_url` | Live Pages URL. Listed here for review; no response is claimed by this page. |
| **Description** | The repository's own README/source files, curated in `tools/overlay.json` | The commit each description was read at is in the **Description source** column. A `⚠` means the repository head has moved since that read (`PROSE-STALE`) — the text is unverified at the newer head, not proved wrong. |
| **Created (UTC)** | Repository `created_at` | The first commit is a separate timestamp and can differ; the ledger records both. |
| **Last updated (UTC)** | Newest committer timestamp on the default branch | *Last updated* is the last commit, **not** the last time the site was visited or used — GitHub's public API exposes no visit/usage data (`FL-01`). |
| **Commits** | Paginated `GET /repos/{owner}/{repo}/commits?sha={branch}` | Exact default-branch commit total at the snapshot. |
| **Pages** | `GET /repos/{owner}/{repo}/pages` → `status` | Build metadata only. `built` is **not** an uptime or browser check (`FL-02`). |
| **Review links** | — | The exact official endpoints to open by hand for that row: live URL, repository, repository API, Pages API, and default-branch commit history. The machine-readable per-site record (`data/sites/<owner>__<repo>.json`) is linked from **Description source** and carries the recorded source basis. |
"""


def load_snapshot():
    """Read window.MASTERDATA from the generated data/sites.js without executing it."""
    with open(DATA, encoding="utf-8") as handle:
        src = handle.read()
    start = src.index("{")
    text = src[start:].rstrip().rstrip(";")
    return json.loads(text)


def esc(value):
    """Escape a value for a Markdown table cell; never fabricate an empty one."""
    if value is None:
        return "—"
    text = str(value).replace("\r", " ").replace("\n", " ").replace("|", "\\|").strip()
    return text if text else "—"


def day(iso):
    """ISO instant → UTC calendar day (`YYYY-MM-DD`), or an em dash when absent."""
    if not isinstance(iso, str) or len(iso) < 10:
        return "—"
    return iso[:10]


def short_sha(sha):
    return sha[:7] if isinstance(sha, str) and sha else None


def review_links(owner, repo, site):
    """The official endpoints a reviewer opens by hand for one row."""
    branch = site.get("defaultBranch") or "main"
    links = [
        ("live", site.get("pagesUrl")),
        ("repo", "https://github.com/%s/%s" % (owner, repo)),
        ("repo API", "%s/repos/%s/%s" % (API, owner, repo)),
        ("Pages API", "%s/repos/%s/%s/pages" % (API, owner, repo)),
        ("commits", "%s/repos/%s/%s/commits?sha=%s" % (API, owner, repo, branch)),
    ]
    return " · ".join("[%s](%s)" % (label, url) for label, url in links if url)


def description_source(owner, repo, site):
    """Link the row to the record that holds the recorded description basis."""
    read = day(site.get("lastVerified"))
    sha = short_sha(site.get("verifiedAtSha"))
    stamp = "read %s at %s" % (read, sha) if sha else ("read %s" % read if read != "—" else "no stamp")
    link = "[%s](%s/%s__%s.json)" % (stamp, RECORD_DIR, owner, repo)
    if site.get("proseStale") is True:
        return "%s ⚠ behind head" % link
    if site.get("lastVerified"):
        return link
    return "%s — unverified" % link


def site_rows(owner, sites):
    lines = []
    for index, site in enumerate(sites, start=1):
        repo = site.get("repo") or ""
        live = site.get("pagesUrl") or ""
        name = site.get("title") or repo
        name = re.sub(r"\s+", " ", str(name)).strip()
        site_cell = "[%s](%s)" % (esc(name), live) if live else esc(name)
        flags = site.get("flags") or []
        if flags:
            site_cell += " ⚑"
        lines.append(
            "| %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |"
            % (
                index,
                site_cell,
                esc(site.get("category")),
                esc(site.get("description")),
                day(site.get("created")),
                day(site.get("lastCommit")),
                site.get("commits") if isinstance(site.get("commits"), int) else "—",
                esc(site.get("pagesStatus")),
                description_source(owner, repo, site),
                review_links(owner, repo, site),
            )
        )
    return lines


def unreachable_section(owner, records):
    if not records:
        return []
    out = [
        "## Frozen records — repository no longer answers (owner review required)",
        "",
        "These entries were published before their repositories stopped answering the official API. "
        "They are preserved with their last verified values and are **not** counted as live sites; "
        "whether the repositories were retired, renamed, or made private is unknown and is not guessed here "
        "(`FL-03`, `T-004`).",
        "",
        "| Repository | Last known description | Created (UTC) | Last commit (UTC) | Last known Pages URL | Official re-check |",
        "|---|---|---|---|---|---|",
    ]
    for record in records:
        repo = record.get("repo") or ""
        out.append(
            "| %s | %s | %s | %s | [%s](%s) | [API 404 check](%s/repos/%s/%s) |"
            % (
                esc(repo),
                esc(record.get("description")),
                day(record.get("created")),
                day(record.get("lastCommit")),
                esc(record.get("pagesUrl") or repo),
                record.get("pagesUrl") or "",
                API,
                owner,
                repo,
            )
        )
    return out


def render(data):
    owner = data.get("owner") or "buffedlizard55-lab"
    sites = data.get("sites") or []
    counts = data.get("counts") or {}
    accounts = data.get("accountsChecked") or []
    generated = data.get("generated") or "—"
    excluded = counts.get("excluded") or []
    unlisted = counts.get("unlisted") or []

    listed = counts.get("sites", len(sites))
    public_repos = counts.get("publicRepos")
    pages_sites = counts.get("pagesSites")
    other = next((a for a in accounts if a.get("login") != owner), {})

    out = []
    out.append("# SITES.md — master list of every public GitHub Pages site")
    out.append("")
    out.append(
        "**Generated** by [`tools/build_sites_md.py`](tools/build_sites_md.py) from "
        "[`data/sites.js`](data/sites.js) (GitHub REST API snapshot) and the curated prose in "
        "[`tools/overlay.json`](tools/overlay.json). **Never hand-edit this file** — rerun the generator. "
        "Human-facing equivalents: the [directory page](https://buffedlizard55-lab.github.io/MasterSite/) "
        "and the [executive summary](https://buffedlizard55-lab.github.io/MasterSite/executive-summary.html)."
    )
    out.append("")
    out.append("| | |")
    out.append("|---|---|")
    out.append("| API snapshot | `%s` (UTC) |" % generated)
    out.append("| Accounts covered | `%s` — %s public repositories, %s with GitHub Pages; `%s` — %s public repositories |"
               % (owner, public_repos if public_repos is not None else "—",
                  pages_sites if pages_sites is not None else "—",
                  other.get("login", "kanlerxz87-cyber"),
                  other.get("publicRepos", "—")))
    out.append("| Sites listed below | **%s** |" % listed)
    out.append("| Repository census | %s public repositories = %s listed + %s excluded by owner request |"
               % (public_repos if public_repos is not None else "—", listed, len(excluded)))
    out.append("| Coverage check | `python3 tools/census_guard.py` (fails if any public repository is neither listed nor excluded) |")
    out.append("| Open review items | [`FLAGGED.md`](FLAGGED.md) · [`TASKS.md`](TASKS.md) · per-entry ledger [`VERIFICATION.md`](VERIFICATION.md) |")
    out.append("")
    if unlisted:
        out.append(
            "> **Withheld repositories:** "
            + "; ".join("`%s` — %s" % (esc(u.get("repo")), esc(u.get("reason"))) for u in unlisted)
            + ". Nothing about them is repeated here (see `AGENTS.md` §2)."
        )
        out.append("")
    out.append(LEGEND)
    out.append("## Every listed site, A → Z")
    out.append("")
    out.append(
        "One row per site: **%s** public GitHub Pages sites, each with the live URL, a brief description taken "
        "from the repository's own files, the creation date, the last default-branch commit, and the official "
        "endpoints to verify that row by hand. `⚑` marks an entry with review flags; `⚠` marks a description "
        "that has not been re-read at the repository's current head." % listed
    )
    out.append("")
    out.append("| # | Site | Category | Description (from the repository's own files) | Created (UTC) | Last updated (UTC) | Commits | Pages | Description source | Review links |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    out.extend(site_rows(owner, sites))
    out.append("")
    unreachable = unreachable_section(owner, data.get("unreachable") or [])
    if unreachable:
        out.extend(unreachable)
        out.append("")
    out.append("## Reproduce this list")
    out.append("")
    out.append("```bash")
    out.append("python3 tools/build_data.py            # re-read the GitHub REST API census (writes data/sites.js)")
    out.append("python3 tools/export_site_records.py   # rewrite data/sites/<owner>__<repo>.json")
    out.append("python3 tools/build_sites_md.py        # rewrite this file from the snapshot above")
    out.append("python3 tools/build_sites_md.py --check  # verify this file is in sync")
    out.append("python3 tools/census_guard.py          # verify no public repository is missing here")
    out.append("```")
    out.append("")
    out.append(
        "Rows are ordered by repository name, exactly as published in `data/sites.js`. Dates are UTC calendar "
        "days of the timestamps recorded in that snapshot; the full timestamps, SHAs, and per-entry source basis "
        "are in [`VERIFICATION.md`](VERIFICATION.md) and `data/sites/`."
    )
    out.append("")
    return "\n".join(out)


def main(argv):
    check = "--check" in argv
    out_path = OUT_PATH
    if "-o" in argv:
        out_path = argv[argv.index("-o") + 1]

    data = load_snapshot()
    rendered = render(data)

    if out_path == "-":
        sys.stdout.write(rendered)
        return 0

    if check:
        if not os.path.exists(out_path):
            print("SITES.md is missing — run python3 tools/build_sites_md.py")
            return 1
        with open(out_path, encoding="utf-8") as handle:
            committed = handle.read()
        if committed != rendered:
            print(
                "SITES.md is out of sync with data/sites.js — run python3 tools/build_sites_md.py "
                "(the snapshot, the curated prose, or the site list changed since it was written)"
            )
            return 1
        print("SITES.md is in sync with data/sites.js (%d site rows)." % len(data.get("sites") or []))
        return 0

    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(rendered)
    print("wrote %s (%d site rows, %d unreachable records)"
          % (os.path.relpath(out_path, ROOT), len(data.get("sites") or []),
             len(data.get("unreachable") or [])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
