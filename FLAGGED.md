# FLAGGED.md — unresolved items needing review

Every row is a field that could **not** be verified from an official source, or a value that looks
irregular. Rows are never removed by a later session without a source link proving the item is
resolved; strike it through and add the resolving evidence instead.

**Legend.** *Repo* — affected repository. *Field* — the field or claim in question. *Reason* —
why it is not verifiable as stated. *Source* — the exact endpoint or page to open by hand.
*Owner decision?* — `yes` when only the repository owner can settle it.

## A. Fields left null (never guessed)

| # | Repo | Field | Reason | Source | Owner decision? |
|---|---|---|---|---|---|
| FL-01 | all listed sites | `lastUsed` / site visits | GitHub's public REST API exposes no visit, view or "last used" counter; no official source exists, so the field is not published at all. The UI publishes repository `created_at`, the newest default-branch committer timestamp, `pushed_at` and `updated_at` as the closest official substitutes and labels them as such. | <https://docs.github.com/en/rest/repos/repos> (no usage fields); <https://api.github.com/repos/buffedlizard55-lab/MasterSite> | no |
| FL-02 | all listed sites | live HTTP status / rendered output | No official GitHub API field reports whether a Pages URL currently serves or renders. `pagesStatus: built` is build metadata, not uptime. | <https://docs.github.com/en/rest/pages/pages> | no |
| FL-03 | `JobSearchSF`, `MALTA`, `MALTA-LAWS`, `MALTA2` | every field (frozen) | `GET /repos/buffedlizard55-lab/{repo}` returns HTTP 404: the repositories are no longer public. Their last verified values are preserved as historical records and are excluded from live counts; whether they were retired on purpose is unknown. | <https://api.github.com/repos/buffedlizard55-lab/JobSearchSF> · <https://api.github.com/repos/buffedlizard55-lab/MALTA> · <https://api.github.com/repos/buffedlizard55-lab/MALTA-LAWS> · <https://api.github.com/repos/buffedlizard55-lab/MALTA2> | yes (T-004) |
| FL-04 | every listed site | organizer score / competition placement | Public leaderboard scores and submission receipts live on DrivenData, not in the GitHub API, and are never re-read by this directory. Descriptions quote a repository's *own* stated verdict and label unverified numbers as the repository's claim. | repository README + `VERIFICATION.md` per-entry row | no |

## B. Irregularities requiring review

Irregularity IDs `IRR-01`… are the machine-readable register in `tools/overlay.json`
(`irregularities[]`), rendered into `VERIFICATION.md` and the site's Irregularities panel. Rows here
are the ones needing a human or owner decision, not a code fix.

| # | Repo | Field | Reason | Source | Owner decision? |
|---|---|---|---|---|---|
| FL-05 | `GEMSDOE53` | Pages status | GitHub reports Pages status `errored` for this repository (read 2026-10-11T02:52Z). The repository's own README states its file is `OK TO SUBMIT`, so the published landing page may not be reachable while the artifact is fine. The directory records the API value as-is and makes no reachability claim. | <https://api.github.com/repos/buffedlizard55-lab/GEMSDOE53/pages> · <https://github.com/buffedlizard55-lab/GEMSDOE53/actions> | yes (T-005) |
| FL-06 | `MALTASUPPLEMENTAL` | Pages status | **Closed 2026-10-11.** A mid-session census read saw `building`, minutes after a push at `2026-10-11T02:51:09Z`; the final build recorded **`built`** and that is what the published snapshot contains. Retained as a worked example of why a status needs a timestamp: `building` was true at 02:5xZ and false at 03:01Z. | <https://api.github.com/repos/buffedlizard55-lab/MALTASUPPLEMENTAL/pages> · `IRR-133` | no |
| FL-07 | `62GEMSDOE`, `GEMSDOE42`, `GEMSDOE44` | Pages landing page | The configured Pages source is `main /` and `GET .../contents/index.html` at the recorded head returns HTTP 404, so the mechanical kind is `stub` (no HTML entry point at the configured path). `GEMSDOE42` and `GEMSDOE44` nevertheless commit full documentation sites at `docs/index.html` and their READMEs link that path directly; `62GEMSDOE` contains only a one-line README. Whether the root URL serves a usable page cannot be checked from this sandbox. | <https://api.github.com/repos/buffedlizard55-lab/GEMSDOE42/contents/index.html> · <https://api.github.com/repos/buffedlizard55-lab/GEMSDOE44/contents/index.html> · <https://api.github.com/repos/buffedlizard55-lab/62GEMSDOE/git/trees/97305e3?recursive=1> | yes (T-008) |
| FL-08 | `6GEMSDOE` (and the GEMS family) | mutually exclusive instructions | `6GEMSDOE` designates itself the only legitimate GEMS entry and recommends deleting the other GEMS repositories, while the other GEMS charters plan further sites. The directory lists every repository and takes no position. | `tools/overlay.json` → `irregularities[]` → `IRR-119`, `IRR-135` | yes (T-006) |
| FL-09 | `kanlerxz87-cyber` | entire account | `GET /users/kanlerxz87-cyber` reports `public_repos: 0`, so the account contributes zero Pages sites. This is a verified result, not a failure to look — but if repositories exist as private or under another login, the public API cannot show them. | <https://api.github.com/users/kanlerxz87-cyber> | no |
| FL-10 | 40 entries at the 2026-10-11 snapshot | description provenance | Their `verifiedAtSha` is behind the current default-branch head, so the prose was written against an older commit (40 of 145 in the published snapshot; it was 41 before `MALTASUPPLEMENTAL` was re-read at its snapshot head under `FL-12`, 47 before the six `GEMSDOE22`–`GEMSDOE27` re-reads under `IRR-138`, and 38 of 107 at the previous snapshot). A changed SHA alone is not proof the prose is false; it means the text has not been re-read at head. | see the `PROSE-STALE` list in `VERIFICATION.md` | no (T-002) |
| FL-11 | 38 sites added 2026-10-11 | coverage gap | Between the 2026-10-01 snapshot and this refresh the account went from 108 to 146 public repositories and 38 public Pages sites were live on the web with no entry here. They are now published with prose read at their head SHAs, but the gap existed for up to 9 days and nothing in the repository would have detected it without a manual census. A scheduled refresh (T-010) would close the detection gap. | <https://api.github.com/users/buffedlizard55-lab/repos?per_page=100&page=2> · `IRR-131` | no (T-010) |
| ~~FL-12~~ | `MALTASUPPLEMENTAL` | description numeric token | **Closed 2026-10-11 (session 96e82e25).** The entry was re-read at the snapshot head `81930befa7315968559c266fdf10ad0932aabfa0` and the description was rewritten from the README at that ref (8,385 bytes, already the rewritten “Malta Trip Guide”): the twelve-page count, the `230` voltage token and the seven-transport-mode list were **withdrawn** because they are not re-derivable from the current README, and the `PROSE-STALE` flag cleared because the stamp now equals the snapshot head. Resolving evidence: <https://api.github.com/repos/buffedlizard55-lab/MALTASUPPLEMENTAL/readme?ref=81930be> · `tools/last_description_audit.json` (re-run below) · `tools/overlay.json` → `descriptionNotes` |

## How to close a row

1. Open the source link and confirm the current official value by hand.
2. Update `tools/overlay.json` (prose, flags, irregularity) — never `data/sites.js` directly.
3. Re-run the data build and the audit commands in [`AGENTS.md`](AGENTS.md) §4.
4. Replace the row here with a strikethrough plus the resolving source URL and date, or delete it if
   the field is now published and verified.
