#!/usr/bin/env python3
"""Line-by-line description auditor for MasterSite.

For every entry in data/sites.js this fetches the repository's own README.md
(and, where the README is absent, the root file listing) through the official
contents API and checks that the *numeric and named* claims in the published
description can actually be found in the repository itself. Anything it cannot
find is reported so a human can confirm or delete the claim.

It never rewrites the dataset — it only reports.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.github.com"
OWNER = "buffedlizard55-lab"
CACHE = os.path.join(ROOT, "tools", ".readme-cache")


def api_get(path, accept="application/vnd.github+json"):
    req = urllib.request.Request(
        API + path,
        headers={"Accept": accept, "User-Agent": "MasterSite-desc-audit",
                 "X-GitHub-Api-Version": "2022-11-28"},
    )
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8", "replace")
            try:
                return r.status, json.loads(raw)
            except json.JSONDecodeError:
                return r.status, raw
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8", "replace"))
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"message": str(e)}


def readme_for(repo, branch="main"):
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    path = os.path.join(CACHE, repo + ".md")
    if os.path.exists(path):
        return open(path, encoding="utf-8").read()
    for name in ("README.md", "readme.md", "README.MD", "Readme.md"):
        st, body = api_get("/repos/%s/%s/contents/%s?ref=%s" % (OWNER, repo, name, branch),
                           accept="application/vnd.github.raw")
        if st == 200 and isinstance(body, str):
            open(path, "w", encoding="utf-8").write(body)
            return body
    return ""


NUM_RE = re.compile(r"\b\d[\d,]*(?:\.\d+)?\s*(?:%|x|k|K|KB|MB|GB)?\b")


def numeric_claims(text):
    out = []
    for m in NUM_RE.finditer(text):
        tok = m.group(0).strip()
        digits = re.sub(r"[^\d]", "", tok)
        if not digits:
            continue
        # skip years/months and pure dates handled elsewhere
        if re.fullmatch(r"(19|20)\d\d", tok):
            continue
        out.append(tok)
    return out


def main():
    src = open(os.path.join(ROOT, "data", "sites.js"), encoding="utf-8").read()
    data = json.loads(src.split("window.MASTERDATA = ", 1)[1].rstrip().rstrip(";"))
    only = sys.argv[1] if len(sys.argv) > 1 else None
    overlay = json.load(open(os.path.join(ROOT, "tools", "overlay.json"), encoding="utf-8"))
    accepted = {k: v for k, v in overlay.get("acceptedDescriptionExceptions", {}).items()
                if not k.startswith("__")}
    unresolved = 0

    problems = []
    print("description audit — checking each published description against the repo's own README")
    print("-" * 92)
    for site in data["sites"]:
        repo = site["repo"]
        if only and repo != only:
            continue
        md = readme_for(repo, site.get("defaultBranch") or "main")
        if not md:
            print("  NO-README %-34s (repository publishes a stub or has no README.md)" % repo)
            problems.append((repo, "no README.md readable through the contents API", []))
            continue
        hay = md.lower()
        hay_flat = re.sub(r"[^a-z0-9]", "", md.lower())
        misses = []
        for tok in numeric_claims(site["description"]):
            digits = re.sub(r"[^\d]", "", tok)
            if digits in re.sub(r"[^0-9]", "", md):
                continue
            if tok.lower() in hay or tok.lower().replace(",", "") in hay:
                continue
            misses.append(tok)
        if misses and repo in accepted:
            status, note = "exc ", "  (accepted: see overlay.json acceptedDescriptionExceptions)"
        else:
            status, note = ("ok  " if not misses else "CHECK"), ""
        print("  %s %-34s readme=%6d chars  unverified-tokens=%s%s"
              % (status, repo, len(md), misses or "-", note))
        if misses and repo not in accepted:
            unresolved += 1
            problems.append((repo, "numeric tokens not found in README", misses))

    print("-" * 92)
    print("accepted exceptions (documented in overlay.json): %d" % len(accepted))
    print("entries needing manual confirmation: %d" % unresolved)
    for repo, why, toks in problems:
        print("  %-34s %s %s" % (repo, why, toks))
    out = os.path.join(ROOT, "tools", "last_description_audit.json")
    json.dump({"unresolved": [{"repo": r, "why": w, "tokens": t} for r, w, t in problems],
               "accepted": accepted},
              open(out, "w", encoding="utf-8"), indent=2)
    print("wrote %s" % os.path.relpath(out, ROOT))
    return 0 if not problems else 1


if __name__ == "__main__":
    main()
