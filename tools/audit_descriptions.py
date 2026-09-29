#!/usr/bin/env python3
"""Numeric-token lint for MasterSite descriptions.

For every entry in data/sites.js, fetch that snapshot's README from the
repository's recorded head SHA through the official contents API and check
whether numeric tokens in the curated description also occur in the README.
Unmatched tokens are reported for review.

This is only a mechanical coverage check: it does not establish that a number
has the same meaning in both places, and it cannot prove non-numeric claims.
Source review and the per-entry verifiedBasis remain necessary. It never
rewrites data/sites.js.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import quote

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


def readme_for(repo, ref):
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    safe_ref = re.sub(r"[^A-Za-z0-9._-]", "_", ref or "default")
    path = os.path.join(CACHE, repo + "-" + safe_ref[:40] + ".md")
    if os.path.exists(path):
        return open(path, encoding="utf-8").read(), None
    quoted_ref = quote(ref or "main", safe="")
    last_error = None
    for name in ("README.md", "readme.md", "README.MD", "Readme.md"):
        endpoint = "/repos/%s/%s/contents/%s?ref=%s" % (OWNER, repo, name, quoted_ref)
        st, body = api_get(endpoint, accept="application/vnd.github.raw")
        if st == 200 and isinstance(body, str):
            open(path, "w", encoding="utf-8").write(body)
            return body, None
        if st == 404:
            continue
        last_error = {"status": st, "endpoint": endpoint,
                      "message": body.get("message") if isinstance(body, dict) else str(body)}
        # Authorization, rate limits, and server errors are not evidence that a
        # repository has no README. Stop rather than turning transport failures
        # into false source-review findings.
        return "", last_error
    return "", None


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
    problems = []
    api_errors = []
    readme_refs = {}
    checked = 0
    print("description audit — numeric-token lint against README at each recorded snapshot head")
    print("This does not prove semantic accuracy; see each entry's verifiedBasis and the audit caveats.")
    print("-" * 104)
    for site in data["sites"]:
        repo = site["repo"]
        if only and repo != only:
            continue
        ref = site.get("headSha") or site.get("defaultBranch") or "main"
        readme_refs[repo] = ref
        md, error = readme_for(repo, ref)
        if error:
            api_errors.append({"repo": repo, "ref": ref, **error})
            print("  API-ERROR %-34s ref=%-10s HTTP %s — %s"
                  % (repo, ref, error.get("status"), error.get("message") or error.get("endpoint")))
            # Stop on transport/auth failures. Continuing would only duplicate
            # the same error and could make an incomplete audit look complete.
            break
        checked += 1
        if not md:
            print("  NO-README %-34s ref=%-10s (no supported README name at this commit)" % (repo, ref))
            problems.append((repo, "no supported README name at snapshot head", []))
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
        print("  %s %-34s ref=%-10s readme=%6d chars  unmatched-tokens=%s%s"
              % (status, repo, ref, len(md), misses or "-", note))
        if misses and repo not in accepted:
            problems.append((repo, "numeric tokens not found in README", misses))

    print("-" * 104)
    complete = checked == len(data["sites"]) and not api_errors
    print("snapshot entries checked: %d / %d%s" % (
        checked, len(data["sites"]), "" if complete else " (INCOMPLETE)"))
    print("accepted numeric-token exceptions (documented in overlay.json): %d" % len(accepted))
    print("entries needing source/numeric review: %d" % len(problems))
    for repo, why, toks in problems:
        print("  %-34s %s %s" % (repo, why, toks))
    for error in api_errors:
        print("  API ERROR: %s ref=%s HTTP %s (%s)" % (
            error["repo"], error["ref"], error.get("status"), error.get("message") or error.get("endpoint")))
    out = os.path.join(ROOT, "tools", "last_description_audit.json")
    json.dump({
        "snapshotGenerated": data.get("generated"),
        "checkedEntries": checked,
        "totalEntries": len(data["sites"]),
        "complete": complete,
        "readmeRefs": readme_refs,
        "numericTokenLintOnly": True,
        "unresolved": [{"repo": r, "why": w, "tokens": t} for r, w, t in problems],
        "apiErrors": api_errors,
        "accepted": accepted
    }, open(out, "w", encoding="utf-8"), indent=2)
    print("wrote %s" % os.path.relpath(out, ROOT))
    return 0 if complete and not problems else (2 if api_errors else 1)


if __name__ == "__main__":
    raise SystemExit(main())
