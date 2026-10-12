#!/usr/bin/env python3
"""One-shot curation patch: re-read GEMSDOE67 / GEMSDOE68 / GEMSDOE69 at their
current default-branch heads (session arena-808b253d, T-035).

Why: all three were published on 2026-10-11 as *title-only placeholders* (11-byte
README, one commit, size 0). By the 2026-10-12T02:08:52Z snapshot `audit_kind.py`
re-derived `app` for GEMSDOE67 and GEMSDOE69 (root `index.html` now 200) and the
repositories had grown to 235, 100 and 52 files. Their published descriptions
("the entire file is the heading … a single initial commit") had become false
statements on a page whose whole premise is that nothing is invented, so they are
rewritten here from the README actually served at each head, with the endpoints a
reviewer can open.

Run from the repository root. It rewrites `tools/overlay.json` in place and
prints what changed; it makes no network call, so the evidence it records was
read by hand before it ran (see the verifiedBasis strings for the endpoints).
"""

import collections
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OVERLAY = os.path.join(ROOT, "tools", "overlay.json")
FAMILIES = os.path.join(ROOT, "tools", "families.json")

READ_AT = "2026-10-12T02:38:00Z"
API = "https://api.github.com/repos/buffedlizard55-lab"

ENTRIES = {
    "GEMSDOE67": {
        "sha": "ddbe9a50ed53bca61512ab40401cedcbe7e1b02f",
        "commit_date": "2026-10-12T02:16:39Z",
        "kind": "app",
        "title": "GEMSDOE67 — three DOE GEMS lanes (OVTR, orientation/tip, and an independent re-run)",
        "category": "Science & ML Research",
        "description": (
            "One repository carrying three parallel lanes for the DrivenData DOE GEMS Prize "
            "fault-mapping challenge, described from its own README. The OVTR lane "
            "(orientation-voted evidence with a calibrated greedy kernel-cover) reports pooled "
            "HOLDOUT-DTI 0.2691 across 4 folds with 60,594 withheld pixels, passes 22/22 format "
            "checks and is labelled DOWNLOAD READY. Two independent implementations of the same "
            "orientation/tip brief both came out negative — 0.0344 joint / 0.0404 segmentation "
            "control for the first, 0.01368 pooled for the second — and the repository's policy "
            "offers no download for a negative lane. The README states that no competition slot "
            "has been used by either lane and that promotion into a slot is a separate decision."
        ),
        "flags": [
            "Three lanes with deliberately different verdicts share one repository, so the "
            "numbers on this card are per lane and are not comparable: the README's own status "
            "table is the authority and the directory quotes it rather than picking a headline "
            "figure.",
            "Published on 2026-10-11 as a title-only placeholder (11-byte README, one commit). At "
            "the 2026-10-12T02:08:52Z snapshot tools/audit_kind.py re-derived `app` because a "
            "root index.html now answers HTTP 200, and the tree had grown to 235 files with three "
            "merged lane branches; the entry was re-read at that evidence (IRR-146). The root "
            "index.html is a redirect that hands the reader to docs/index.html.",
        ],
    },
    "GEMSDOE68": {
        "sha": "e848bd18a7360e1bc48fd1aa44c622e5a21891ff",
        "commit_date": "2026-10-12T02:26:19Z",
        "kind": "stub",
        "title": "GEMSDOE68 — auto-context stacked refinement lane for the DOE GEMS Prize",
        "category": "Science & ML Research",
        "description": (
            "An auto-context stacked refinement lane for the DrivenData DOE GEMS Prize "
            "fault-mapping challenge. Its README compares three parallel candidates produced by "
            "pull requests #1\u2013#3, each scored from that candidate's own run card: #1 failed its "
            "own holdout gate (stage 2 0.00002 against stage 1 0.0082) and is marked do not "
            "submit; #2 records no holdout DTI or gate and is marked not evidenced, do not spend a "
            "slot; #3 passed (stage 3 0.1189 against stage 1 0.0816, a difference of +0.0373 with "
            "a [0.026, 0.048] interval) with a complete 23-raster registry check and is named as "
            "the file to submit. The repository has no index.html at the configured Pages root, so "
            "the published URL serves Jekyll's render of the README; `stub` records that, not that "
            "the URL is dead."
        ),
        "flags": [
            "The 2026-10-12T02:08:52Z snapshot recorded this entry's Pages status as `errored` "
            "after two consecutive failed builds at 01:45:53Z and 01:46:27Z; a hand re-read at "
            "02:33Z, after the 02:26:19Z push, returned `built` again. The snapshot value stands "
            "as read at its own timestamp and this note records the recovery (IRR-145).",
            "Published on 2026-10-11 as a title-only placeholder (11-byte README, one commit). By "
            "the 2026-10-12T02:08:52Z snapshot it held 100 files and a README documenting a full "
            "GEMS lane, so the placeholder description was withdrawn and the entry re-read at its "
            "head (IRR-147). It keeps `stub` because the configured Pages root still has no "
            "index.html.",
        ],
    },
    "GEMSDOE69": {
        "sha": "2fe0d9b3f8fd8e6c9d4b41b538d07f60516166ff",
        "commit_date": "2026-10-12T01:50:36Z",
        "kind": "app",
        "title": "GEMSDOE69 — auditable DOE GEMS fault-discovery workbench (release gate: negative)",
        "category": "Science & ML Research",
        "description": (
            "An auditable research workbench for the DOE GEMS / GeoDAWN fault-discovery brief. Its "
            "README opens with a release decision of NEGATIVE / NOT READY: there is no submission "
            "GeoTIFF in the repository, and it asks readers not to download or submit a "
            "placeholder. The method lane is a catalogue-geometry relay-ramp, pull-apart and "
            "displacement-transfer corridor approach built from catalogue fault polylines and "
            "their tips, ranked with multi-scale gravity and magnetic horizontal-gradient and tilt "
            "evidence, with corridor width searched across the project's 0.1\u201315 km interval and "
            "along-strike separation bounded at 3.5 times the corridor width. The published root "
            "index.html is a status page linking an executive summary, ranked hypotheses, a source "
            "register and a run card."
        ),
        "flags": [
            "The repository's own headline verdict is a refusal to offer a download, so the "
            "directory reports that verdict rather than describing results the repository does "
            "not claim.",
            "Published on 2026-10-11 as a title-only placeholder (11-byte README, one commit). At "
            "the 2026-10-12T02:08:52Z snapshot tools/audit_kind.py re-derived `app` because a root "
            "index.html now answers HTTP 200, and the tree had grown to 52 files of research "
            "documentation; the entry was re-read at that evidence (IRR-146).",
        ],
    },
}

IRREGULARITIES = [
    {
        "id": "IRR-145",
        "severity": "warn",
        "repo": "GEMSDOE68",
        "field": "pagesStatus (transient build failure, recovered)",
        "reason": (
            "Pages status moved `built` -> `errored` -> `built` inside an hour on 2026-10-12. The "
            "build list shows a successful build at commit a0ab16358c3b364b4f22544955472c9869497fc2 "
            "(2026-10-11T19:40:22Z), then two consecutive failures reported as `Page build failed.` "
            "at 2026-10-12T01:45:53Z (commit a2305758068495fc48d9e72dfa4848d207e64c07) and "
            "2026-10-12T01:46:27Z (commit 208f3bf7428c3184e5e7bbbf2ed3d5e4f3b1bb58); the public API "
            "returns no further build-error detail. The generator re-read the Pages endpoint four "
            "times with six-second gaps before recording `errored`, so this was not a mid-deploy "
            "transient at the time it was read. A hand re-read at 2026-10-12T02:33Z, after the "
            "02:26:19Z push, returned `built`. The snapshot records what the API said at "
            "02:08:52Z and the recovery is recorded here rather than silently substituted, because "
            "overwriting a read with a later one would make the ledger unauditable."
        ),
        "source": (
            "https://api.github.com/repos/buffedlizard55-lab/GEMSDOE68/pages ; "
            "https://api.github.com/repos/buffedlizard55-lab/GEMSDOE68/pages/builds ; "
            "https://api.github.com/repos/buffedlizard55-lab/GEMSDOE68"
        ),
        "status": "open",
    },
    {
        "id": "IRR-146",
        "severity": "warn",
        "repo": "GEMSDOE67, GEMSDOE69",
        "field": "kind / description (placeholder became a real lane)",
        "reason": (
            "Both were published on 2026-10-11 as title-only placeholders (one 11-byte README, a "
            "single commit, size 0). By the 2026-10-12T02:08:52Z snapshot each had grown a real "
            "project — GEMSDOE67 to 235 files across three merged lane branches, GEMSDOE69 to 52 "
            "files of fault-discovery research documentation — and tools/audit_kind.py re-derived "
            "`app` for both (root index.html answers HTTP 200) where the overlay still said `stub`. "
            "Both entries were re-read at their default-branch heads (ddbe9a50ed53bca61512ab40401cedcbe7e1b02f "
            "and 2fe0d9b3f8fd8e6c9d4b41b538d07f60516166ff), moved from `Unclassified & Placeholder` "
            "to `Science & ML Research`, and added to the curated GEMS family. The published "
            "placeholder descriptions were withdrawn because they had become false, not merely "
            "stale. This is the ninth and tenth placeholder-turned-project the directory has "
            "recorded (after IRR-144/62GEMSDOE)."
        ),
        "source": (
            "https://api.github.com/repos/buffedlizard55-lab/GEMSDOE67/contents/index.html?ref=ddbe9a50ed53bca61512ab40401cedcbe7e1b02f ; "
            "https://api.github.com/repos/buffedlizard55-lab/GEMSDOE69/contents/index.html?ref=2fe0d9b3f8fd8e6c9d4b41b538d07f60516166ff ; "
            "https://api.github.com/repos/buffedlizard55-lab/GEMSDOE67/git/trees/ddbe9a50ed53bca61512ab40401cedcbe7e1b02f?recursive=1 ; "
            "https://api.github.com/repos/buffedlizard55-lab/GEMSDOE69/git/trees/2fe0d9b3f8fd8e6c9d4b41b538d07f60516166ff?recursive=1"
        ),
        "status": "open",
    },
    {
        "id": "IRR-147",
        "severity": "warn",
        "repo": "GEMSDOE68",
        "field": "category / description (placeholder became a real lane, still no root index.html)",
        "reason": (
            "GEMSDOE68 was published on 2026-10-11 as a title-only placeholder. By the "
            "2026-10-12T02:08:52Z snapshot it held 100 files and a README documenting a full "
            "auto-context stacked refinement lane for the DOE GEMS Prize, so the placeholder "
            "description was withdrawn and the entry was re-read at head "
            "e848bd18a7360e1bc48fd1aa44c622e5a21891ff and moved to `Science & ML Research`. It "
            "keeps `kind: stub`, because the configured Pages root still returns HTTP 404 for "
            "index.html — the published URL serves Jekyll's render of the README. It is therefore "
            "a real project whose landing page is generated rather than authored, and it is now "
            "grouped with the other GEMS lanes while GEMSDOE70-GEMSDOE72 (still one commit each, "
            "size 0) remain ungrouped placeholders."
        ),
        "source": (
            "https://api.github.com/repos/buffedlizard55-lab/GEMSDOE68/readme?ref=e848bd18a7360e1bc48fd1aa44c622e5a21891ff ; "
            "https://api.github.com/repos/buffedlizard55-lab/GEMSDOE68/contents/index.html?ref=e848bd18a7360e1bc48fd1aa44c622e5a21891ff ; "
            "https://api.github.com/repos/buffedlizard55-lab/GEMSDOE68/git/trees/e848bd18a7360e1bc48fd1aa44c622e5a21891ff?recursive=1"
        ),
        "status": "open",
    },
]


def basis(repo, info):
    sha = info["sha"]
    return (
        "READ {read_at} at current default-branch head {sha} (latest commit timestamp {commit_date} "
        "as returned by the official commits API). README.md at this head is the source of every "
        "sentence in the description; the directory repeats the repository's own status wording and "
        "makes no independent claim about research validity, competition acceptance, or any score. "
        "Reproduce: GET {api}/{repo}/readme?ref={sha} . Official sources: "
        "GET {api}/{repo}/readme?ref={sha} ; "
        "GET {api}/{repo}/git/trees/{sha}?recursive=1 ; "
        "GET {api}/{repo}/contents/index.html?ref={sha} ; "
        "GET {api}/{repo}/pages ; "
        "GET {api}/{repo} (created_at as recorded in the snapshot)."
    ).format(read_at=READ_AT, sha=sha, commit_date=info["commit_date"], api=API, repo=repo)


def main():
    with open(OVERLAY, encoding="utf-8") as fh:
        overlay = json.load(fh, object_pairs_hook=collections.OrderedDict)

    for repo, info in ENTRIES.items():
        entry = overlay["entries"].get(repo)
        if entry is None:
            raise SystemExit("no overlay entry for %s" % repo)
        entry["title"] = info["title"]
        entry["category"] = info["category"]
        entry["kind"] = info["kind"]
        entry["description"] = info["description"]
        entry["flags"] = info["flags"]
        entry["lastVerified"] = READ_AT
        entry["verifiedAtSha"] = info["sha"]
        entry["verifiedBasis"] = basis(repo, info)
        print("rewrote overlay entry %s (kind=%s, category=%s, stamp=%s)"
              % (repo, info["kind"], info["category"], info["sha"]))

    ids = {i["id"] for i in overlay["irregularities"]}
    for irr in IRREGULARITIES:
        if irr["id"] in ids:
            raise SystemExit("irregularity %s already present" % irr["id"])
        overlay["irregularities"].append(irr)
        print("added %s (%s)" % (irr["id"], irr["repo"]))

    with open(OVERLAY, "w", encoding="utf-8") as fh:
        json.dump(overlay, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("wrote tools/overlay.json (%d irregularities)" % len(overlay["irregularities"]))

    # Family membership: 67/68/69 now document DOE GEMS work in their own READMEs, so
    # they join the curated lane family; 70-72 are still one-commit placeholders.
    with open(FAMILIES, encoding="utf-8") as fh:
        fam = json.load(fh, object_pairs_hook=collections.OrderedDict)
    promoted = ["GEMSDOE67", "GEMSDOE68", "GEMSDOE69"]
    family = fam["families"][0]
    for repo in promoted:
        if repo in fam["ungroupedByDesign"]:
            fam["ungroupedByDesign"].remove(repo)
        if repo not in family["repos"]:
            family["repos"].append(repo)
    family["repos"] = sorted(family["repos"])
    family["basis"] = (
        "Membership is curated from each member's own README at the SHA recorded in its "
        "verifiedBasis: every member description documents DOE GEMS Prize Challenge work (lanes, "
        "submissions, fault-discovery research, forks/copies of a GEMS lane with a new strategy, or "
        "a research library for the competition). Sources are per entry in VERIFICATION.md and "
        "data/sites/. GEMSDOE70-GEMSDOE72 are excluded because their READMEs are title-only and "
        "document no purpose; GEMSDOE67, GEMSDOE68 and GEMSDOE69 were added on 2026-10-12 after "
        "their READMEs grew from a heading into a documented lane (IRR-146, IRR-147), and GEMSDOE68 "
        "is a member despite `kind: stub` because membership follows documented purpose, not the "
        "presence of a root index.html."
    )
    fam["families"][0] = family
    with open(FAMILIES, "w", encoding="utf-8") as fh:
        json.dump(fam, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("family %s now has %d members; ungroupedByDesign=%s"
          % (family["id"], len(family["repos"]), fam["ungroupedByDesign"]))


if __name__ == "__main__":
    main()
