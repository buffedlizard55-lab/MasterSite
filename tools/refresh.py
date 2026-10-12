#!/usr/bin/env python3
"""Quota-aware, resumable full API refresh (T-029).

Run the existing generator and all four independent audits in an ignored staging
area. Each actual HTTP request (including retries/redirects/quota probes) counts
against a hard per-invocation budget. Successful public API answers are saved,
with their original URLs and UTC read times, in a compressed checkpoint. A pause
never replaces the published snapshot or audit reports. --resume continues the
same collection; it does NOT relabel replayed answers as fresh reads.

    python3 tools/refresh.py --budget 900
    python3 tools/refresh.py --resume --budget 900
    python3 tools/refresh.py --resume --publish --budget 900

--publish is an explicit promotion of a completed, publication-safe collection.
Description-lint findings remain findings; a coverage gap, incomplete audit,
kind disagreement, API hard mismatch, or broken citation prevents promotion.
Generated exports/pages/ledger must then be rebuilt and scripts/validate run.
No Git operations, credentials in checkpoints, live-site calls, or prose edits.
"""

import argparse
import contextlib
import copy
import fcntl
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.github.com"
ACCOUNTS = ("buffedlizard55-lab", "kanlerxz87-cyber")
VERSION = 2
STAGES = ("build_data", "audit_kind", "audit_descriptions", "audit_provenance", "verify_live", "coverage")
REPORTS = {
    "audit_kind": "tools/last_kind_audit.json",
    "audit_descriptions": "tools/last_description_audit.json",
    "audit_provenance": "tools/last_provenance_audit.json",
    "verify_live": "tools/last_live_verify.json",
}
INPUTS = ("tools/overlay.json", "tools/families.json", "tools/refresh.py", "tools/build_data.py",
          "tools/audit_kind.py", "tools/audit_descriptions.py", "tools/audit_provenance.py", "tools/verify_live.py")
SAFE_HEADERS = ("x-ratelimit-limit", "x-ratelimit-remaining", "x-ratelimit-reset", "retry-after", "date")
CAVEAT = ("A completed collection is a sequence of timestamped public API reads, not a simultaneous snapshot. "
          "Checkpoint replay retains the original read time. These checks do not establish semantic correctness, "
          "live-site uptime, browser functionality, visits, or last use.")


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def epoch(stamp):
    return datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()


def atomic_write(path, raw):
    """Same-directory replacement; never truncate the previous good file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as fh:
        fh.write(raw)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def write_json(path, value):
    atomic_write(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode())


def load_snapshot(path):
    text = Path(path).read_text(encoding="utf-8")
    return json.loads(text.split("window.MASTERDATA = ", 1)[1].rstrip().rstrip(";"))


def fingerprint(root):
    return {name: hashlib.sha256((Path(root) / name).read_bytes()).hexdigest() for name in INPUTS}


class CheckpointError(Exception):
    pass


class Paused(Exception):
    def __init__(self, reason, url=None, status=None, retry_at=None):
        super().__init__(reason)
        self.detail = {"reason": reason, "source": url, "httpStatus": status, "retrySuggestedAt": retry_at}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    # Follow redirects ourselves, so every hop counts and credentials can never
    # be forwarded to an untrusted host by urllib's default redirect handler.
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def official_url(path):
    url = API + path if path.startswith("/") and not path.startswith("//") else path
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.netloc != "api.github.com" or parts.fragment:
        raise CheckpointError("only HTTPS api.github.com GET endpoints are permitted")
    if any(key.lower() in ("token", "access_token", "client_secret")
           for key, _ in urllib.parse.parse_qsl(parts.query)):
        raise CheckpointError("credentials in source URLs are not permitted")
    return url


class Budget:
    """One ceiling across every stage, including the initial quota probe."""
    def __init__(self, budget, reserve, opener=None, gap=1.0):
        if reserve < 0 or budget <= reserve + 1:
            raise CheckpointError("budget must exceed reserve by at least two requests")
        self.ceiling = budget - reserve
        self.reserve = reserve
        self.used = 0
        self.remaining = None
        self.quota = None
        self.paused = None
        self.lock = threading.Lock()
        self.opener = opener or urllib.request.build_opener(NoRedirect()).open
        self.gap = gap
        self.last_start = None

    def stop(self, reason, url=None, status=None, headers=None):
        retry_at = None
        headers = headers or {}
        retry = headers.get("retry-after")
        reset = headers.get("x-ratelimit-reset")
        try:
            if retry is not None:
                retry_at = datetime.fromtimestamp(time.time() + int(retry), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            elif reset is not None and int(headers.get("x-ratelimit-remaining", "-1")) == 0:
                retry_at = datetime.fromtimestamp(int(reset), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, OverflowError):
            pass
        self.paused = Paused(reason, url, status, retry_at)
        raise self.paused

    def fetch(self, url, accept="application/vnd.github+json", redirects=0):
        url = official_url(url)
        with self.lock:
            if self.paused:
                raise self.paused
            if self.used >= self.ceiling:
                self.stop("request budget exhausted; no further request was sent", url)
            if self.remaining is not None and self.remaining <= self.reserve:
                self.stop("live primary quota has reached the unspent reserve", url)
            if self.last_start is not None:
                wait = self.gap - (time.monotonic() - self.last_start)
                if wait > 0:
                    time.sleep(wait)
            self.last_start = time.monotonic()
            self.used += 1
            if self.remaining is not None:
                self.remaining -= 1
        req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "MasterSite-resumable-refresh",
                                                  "X-GitHub-Api-Version": "2022-11-28"})
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if token:
            req.add_header("Authorization", "Bearer " + token)
        try:
            with self.opener(req, timeout=30) as resp:
                status, raw, headers = resp.status, resp.read(), dict(resp.headers)
        except urllib.error.HTTPError as exc:
            status, raw, headers = exc.code, exc.read(), dict(exc.headers or {})
        except Exception as exc:
            with self.lock:
                self.stop("transport failure: %s (no repository verdict)" % exc, url, 0)
        headers = {k.lower(): v for k, v in headers.items()}
        with self.lock:
            try:
                observed = int(headers["x-ratelimit-remaining"])
                self.remaining = observed if self.remaining is None else min(self.remaining, observed)
            except (KeyError, ValueError):
                pass
        if status in (301, 302, 303, 307, 308):
            if redirects >= 5 or not headers.get("location"):
                self.stop("invalid or excessive API redirect", url, status)
            target = official_url(urllib.parse.urljoin(url, headers["location"]))
            return self.fetch(target, accept, redirects + 1)
        text = raw.decode("utf-8", "replace")
        try:
            body = json.loads(text)
        except json.JSONDecodeError:
            body = text
        if status in (401, 403, 429) or status >= 500:
            message = body.get("message", "") if isinstance(body, dict) else text[:200]
            with self.lock:
                self.stop("API access/server block: HTTP %s %s (not a data finding)" % (status, message),
                          url, status, headers)
        return {"url": url, "status": status, "body": body, "readAt": utc_now(),
                "headers": {k: headers[k] for k in SAFE_HEADERS if k in headers}}

    def preflight(self):
        response = self.fetch(API + "/rate_limit")
        body = response["body"]
        core = body.get("resources", {}).get("core", {}) if isinstance(body, dict) else {}
        remaining = core.get("remaining")
        if response["status"] != 200 or not isinstance(remaining, int) or remaining < 0:
            self.stop("could not verify primary API quota; refusing an unbudgeted pass", API + "/rate_limit")
        self.remaining = remaining if self.remaining is None else min(remaining, self.remaining)
        self.quota = {"source": API + "/rate_limit", "readAt": response["readAt"], "core": core,
                      "headers": response["headers"], "effectiveRemaining": self.remaining}


class Collection:
    """Replay a phase's own answers, never a different audit's answers.

    The occurrence number matters: a deliberate Pages-status re-read remains a
    new observation, not a memoized copy of the first response. Commit-history
    pagination in build_data/verify_live pins later pages to the first page's
    full head SHA, so a moving branch cannot duplicate/drop commits mid-list.
    """
    def __init__(self, directory, state, stage, budget, save):
        self.directory = Path(directory)
        self.state = state
        self.stage = stage
        self.budget = budget
        self.save = save
        self.phase = state["phases"].setdefault(stage, {"startedAt": utc_now(), "responses": {}, "requests": 0})
        self.ordinal = {}
        self.pins = {}
        self.replays = 0
        self.lock = threading.Lock()

    def get(self, path, accept="application/vnd.github+json"):
        requested = official_url(path)
        parts = urllib.parse.urlsplit(requested)
        query = dict(urllib.parse.parse_qsl(parts.query))
        paginated = (self.stage in ("build_data", "verify_live") and parts.path.endswith("/commits")
                     and query.get("per_page") == "100" and "page" in query)
        pin_key = (parts.path, query.get("sha"), accept)
        with self.lock:
            if paginated and query["page"] != "1" and pin_key in self.pins:
                query["sha"] = self.pins[pin_key]
                url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, urllib.parse.urlencode(query), ""))
            else:
                url = requested
            seq_key = accept + " " + requested
            ordinal = self.ordinal.get(seq_key, 0)
            self.ordinal[seq_key] = ordinal + 1
        key = hashlib.sha256((seq_key + " #" + str(ordinal)).encode()).hexdigest()
        cached = self.phase["responses"].get(key)
        if cached:
            file = self.directory / "responses" / self.stage / (key + ".json.gz")
            try:
                raw = gzip.decompress(file.read_bytes())
                if hashlib.sha256(raw).hexdigest() != cached["sha256"]:
                    raise ValueError("body checksum mismatch")
                response = json.loads(raw)
                # A legitimate GitHub rename can redirect to /repositories/{id}.
                # Bind replay to the original wire request (including pinned SHA),
                # not to a final URL that correctly differs after that redirect.
                if response["requestedUrl"] != requested or response["requestUrl"] != url or response["accept"] != accept:
                    raise ValueError("cached URL/representation mismatch")
                official_url(response["url"])
                for field in ("url", "requestedUrl", "requestUrl", "status", "readAt"):
                    if response[field] != cached[field]:
                        raise ValueError("cached evidence metadata disagrees with the original response")
                if response["status"] in (401, 403, 429) or response["status"] >= 500:
                    raise ValueError("an access block must never be cached")
                epoch(response["readAt"])
            except (OSError, ValueError, KeyError, TypeError) as exc:
                raise CheckpointError("unreadable/corrupt checkpoint response: %s" % exc) from exc
            self.replays += 1
        else:
            before = self.budget.used
            try:
                response = self.budget.fetch(url, accept)
            finally:
                with self.lock:
                    self.phase["requests"] += self.budget.used - before
            response.update({"requestedUrl": requested, "requestUrl": url, "accept": accept})
            raw = json.dumps(response, ensure_ascii=False, separators=(",", ":")).encode()
            file = self.directory / "responses" / self.stage / (key + ".json.gz")
            atomic_write(file, gzip.compress(raw, mtime=0))
            with self.lock:
                self.phase["responses"][key] = {"sha256": hashlib.sha256(raw).hexdigest(), "url": response["url"],
                                                "requestedUrl": requested, "requestUrl": url, "status": response["status"],
                                                "readAt": response["readAt"]}
                self.save()
        body = response["body"]
        if paginated and query["page"] == "1" and response["status"] == 200 and isinstance(body, list) and body:
            sha = body[0].get("sha")
            if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
                raise CheckpointError("commit-history head is not a full official commit SHA")
            self.pins[pin_key] = sha
        # Callers must not be able to mutate a saved official response in memory.
        return response["status"], copy.deepcopy(body)

    def summary(self):
        responses = list(self.phase["responses"].values())
        stamps = [r["readAt"] for r in responses]
        return {"startedAt": self.phase["startedAt"], "completedAt": utc_now(),
                "oldestReadAt": min(stamps) if stamps else None, "newestReadAt": max(stamps) if stamps else None,
                "requests": self.phase["requests"], "responses": len(responses),
                "checkpointReplaysThisInvocation": self.replays, "caveat": CAVEAT}

    def sources_for(self, owner, repo):
        prefix = API + "/repos/%s/%s" % (owner, repo)
        return [{"url": r["url"], "status": r["status"], "readAt": r["readAt"]}
                for r in self.phase["responses"].values()
                if r["requestedUrl"].split("?", 1)[0] == prefix
                or r["requestedUrl"].startswith(prefix + "/")]


def publication_blockers(state):
    """A description lint finding is reviewable, never silently turned into PASS."""
    blockers = []
    for stage in STAGES:
        phase = state.get("phases", {}).get(stage, {})
        if not phase.get("complete"):
            blockers.append(stage + ": collection incomplete")
            continue
        report = phase.get("report", {})
        if stage == "build_data" and report.get("coverageGaps"):
            blockers.append(stage + ": public Pages repositories lack sourced entries")
        elif stage == "audit_kind" and report.get("disagreements"):
            blockers.append(stage + ": kind disagreements require source review")
        elif stage == "audit_provenance" and report.get("findings"):
            blockers.append(stage + ": citations have hard findings")
        elif stage == "verify_live" and (report.get("hardMismatchCount", 0) or report.get("hardMismatches")
                                         or report.get("unlistedInApi") or report.get("listedNotInApi")):
            blockers.append(stage + ": live API has hard mismatches or a coverage difference")
        elif stage == "coverage" and report.get("gaps"):
            blockers.append(stage + ": final live census differs from the staged directory")
    return blockers


def fresh_module(name, root):
    spec = importlib.util.spec_from_file_location("_refresh_" + name, ROOT / "tools" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = str(root)
    for attr, rel in (("OVERLAY_PATH", "tools/overlay.json"), ("OUT_PATH", "data/sites.js"),
                      ("FAMILIES_PATH", "tools/families.json"), ("CACHE", "tools/.readme-cache"),
                      ("REPORTS", "reports/provenance")):
        if hasattr(module, attr):
            setattr(module, attr, str(root / rel))
    return module


def coverage(collection, snapshot):
    """Fresh phase, separate from the builder: recheck BOTH public account sets."""
    listed = {ACCOUNTS[0]: {s["repo"] for s in snapshot["sites"]}, ACCOUNTS[1]: set()}
    excluded = {ACCOUNTS[0]: set(snapshot["counts"].get("excluded", [])), ACCOUNTS[1]: set()}
    accounts, gaps = [], []
    for owner in ACCOUNTS:
        endpoint = "/users/" + owner
        status, profile = collection.get(endpoint)
        if status != 200 or not isinstance(profile, dict):
            raise CheckpointError("final account read did not return an official profile")
        repos, page = [], 1
        while True:
            source = "/users/%s/repos?type=public&per_page=100&page=%d" % (owner, page)
            status, data = collection.get(source)
            if status != 200 or not isinstance(data, list):
                raise CheckpointError("final public repository census is incomplete")
            if any(r.get("private") is not False or r.get("owner", {}).get("login", "").lower() != owner.lower()
                   for r in data):
                raise CheckpointError("final public repository census contains an unexpected owner/private record")
            repos.extend(data)
            if len(data) < 100:
                break
            page += 1
        names = {r["name"] for r in repos}
        if len(names) != len(repos) or profile.get("public_repos") != len(names):
            raise CheckpointError("account profile/list disagree; repeat the census rather than guessing")
        missing = sorted(names - listed[owner] - excluded[owner])
        vanished = sorted(listed[owner] - names)
        if missing or vanished:
            gaps.append({"owner": owner, "unlisted": missing, "listedNotPublic": vanished, "source": API + endpoint + "/repos?type=public"})
        accounts.append({"owner": owner, "publicRepos": len(names), "source": API + endpoint + "/repos?type=public"})
    return {"accounts": accounts, "gaps": gaps}


def run_stage(stage, collection, stage_root):
    if stage == "coverage":
        return coverage(collection, load_snapshot(stage_root / "data/sites.js")), True
    module = fresh_module(stage, stage_root)
    if stage == "audit_provenance":
        # Keep that tool's per-process memoization: repeated identical citations
        # share one observation, while independent stages still never share it.
        module._api_get_uncached = collection.get
    else:
        module.api_get = collection.get
    # A single worker keeps checkpoint replay deterministic and stops immediately
    # at the ceiling. Audit tools themselves remain usable unchanged outside here.
    argv = [str(ROOT / "tools" / (stage + ".py"))]
    if stage == "audit_provenance":
        argv += ["--workers", "1"]
    # Avoid unstamped disk README cache hits: every phase has its own API evidence.
    if stage in ("audit_descriptions", "audit_provenance"):
        cache = stage_root / "tools/.readme-cache"
        if cache.is_dir():
            shutil.rmtree(cache)
    old_argv = sys.argv
    sys.argv = argv
    try:
        if stage == "build_data":
            module.main(api_context=collection)
        else:
            code = module.main()
    finally:
        sys.argv = old_argv
    if stage == "build_data":
        data = load_snapshot(stage_root / "data/sites.js")
        gaps = [r for r in data["counts"].get("unlisted", []) if r["repo"] not in data["counts"].get("excluded", [])]
        return {"snapshot": data["generated"], "sites": len(data["sites"]), "coverageGaps": gaps}, True
    report = json.loads((stage_root / REPORTS[stage]).read_text())
    complete = report.get("complete") is True and code in (0, 1)
    complete = complete and report.get("snapshotGenerated") == load_snapshot(stage_root / "data/sites.js")["generated"]
    if stage == "verify_live":
        complete = complete and report.get("status") in ("complete", "complete_with_mismatches")
        complete = complete and isinstance(report.get("hardMismatchCount"), int)
    elif stage == "audit_kind":
        complete = complete and report.get("checkedEntries") == report.get("totalEntries") and not report.get("unresolved")
    elif stage == "audit_descriptions":
        complete = complete and report.get("checkedEntries") == report.get("totalEntries") and not report.get("apiErrors")
    elif stage == "audit_provenance":
        complete = complete and report.get("entriesAudited") == report.get("entriesTotal") and not report.get("accessBlocked")
    report["apiCollection"] = collection.summary()
    write_json(stage_root / REPORTS[stage], report)
    return report, complete


def prepare(directory, resume, max_age):
    state_path = directory / "checkpoint.json"
    if state_path.exists():
        if not resume:
            raise CheckpointError("checkpoint already exists; use --resume or choose a new --checkpoint directory")
        try:
            state = json.loads(state_path.read_text())
            if state.get("version") != VERSION or state.get("inputs") != fingerprint(ROOT):
                raise CheckpointError("checkpoint inputs/version changed; start a new collection (do not mix source versions)")
            age = time.time() - epoch(state["startedAt"])
            if age > max_age or age < -60:
                raise CheckpointError("checkpoint exceeds --max-age or is future-dated; start a new collection rather than relabel mutable answers")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise CheckpointError("unreadable checkpoint: %s" % exc) from exc
        return state
    if resume:
        raise CheckpointError("no checkpoint to resume")
    stage_root = directory / "staged"
    (stage_root / "data").mkdir(parents=True, exist_ok=True)
    (stage_root / "tools").mkdir(parents=True, exist_ok=True)
    for name in ("tools/overlay.json", "tools/families.json"):
        shutil.copyfile(ROOT / name, stage_root / name)
    state = {"version": VERSION, "inputs": fingerprint(ROOT), "startedAt": utc_now(), "phases": {},
             "attempts": [], "status": "INCOMPLETE", "caveat": CAVEAT}
    write_json(state_path, state)
    return state


def promote(directory, state):
    if state.get("inputs") != fingerprint(ROOT):
        raise CheckpointError("publication refused: inputs changed during collection")
    blockers = publication_blockers(state)
    if blockers:
        raise CheckpointError("publication refused: " + "; ".join(blockers))
    stage_root = directory / "staged"
    paths = list(REPORTS.values())
    paths += [str(p.relative_to(stage_root)) for p in sorted((stage_root / "reports/provenance").glob("*.md"))]
    paths.append("data/sites.js")
    # Verify every output exists and still matches the completed phase BEFORE
    # replacing anything. A hand-edited/corrupt staged file is never evidence.
    raw = {name: (stage_root / name).read_bytes() for name in paths}
    seals = {name: digest for phase in state["phases"].values() for name, digest in phase.get("outputs", {}).items()}
    for name, body in raw.items():
        if seals.get(name) != hashlib.sha256(body).hexdigest():
            raise CheckpointError("staged output changed or is unsealed: " + name)
    for name, body in raw.items():
        atomic_write(ROOT / name, body)
    state["publishedAt"] = utc_now()
    print("Promoted complete snapshot and independent audit reports. Rebuild exports/pages/ledger, sync README, then scripts/validate.")


def write_summary(directory, state):
    phases = []
    for name in STAGES:
        phase = state.get("phases", {}).get(name, {})
        report = phase.get("report", {})
        verdict = "NOT-RUN" if not phase else "INCOMPLETE"
        if phase.get("complete"):
            findings = (report.get("coverageGaps") or report.get("disagreements") or report.get("unresolved")
                        or report.get("findings") or report.get("hardMismatchCount") or report.get("gaps"))
            verdict = "FINDINGS" if findings else "PASS"
        phases.append({"stage": name, "verdict": verdict, "apiCollection": phase.get("apiCollection"),
                       "requests": phase.get("requests", 0), "report": REPORTS.get(name),
                       "review": {k: report[k] for k in ("coverageGaps", "disagreements", "unresolved", "findings", "hardMismatches", "gaps") if report.get(k)}})
    summary = {"startedAt": state["startedAt"], "finishedAt": state.get("finishedAt"), "status": state["status"],
               "publishedAt": state.get("publishedAt"), "pause": state.get("pause"), "attempts": state["attempts"],
               "stages": phases, "publicationBlockers": publication_blockers(state), "caveat": CAVEAT}
    write_json(directory / "report.json", summary)
    lines = ["# Resumable full API refresh", "", "**Status:** %s. Collection began `%s`." % (state["status"], state["startedAt"]), "", CAVEAT, "",
             "| Stage | Verdict | Actual HTTP requests across attempts | Original API read window (UTC) |", "|---|---|---|---|"]
    for phase in phases:
        span = phase.get("apiCollection") or {}
        lines.append("| `%s` | **%s** | %s | %s → %s |" % (phase["stage"], phase["verdict"], phase["requests"],
                                                          span.get("oldestReadAt") or "unreported", span.get("newestReadAt") or "unreported"))
    if state.get("pause"):
        lines += ["", "**Paused, not verified:** " + state["pause"]["reason"]]
    for phase in phases:
        if phase["review"]:
            lines += ["", "## `%s` review items" % phase["stage"], "", "```json", json.dumps(phase["review"], indent=2), "```"]
    atomic_write(directory / "report.md", ("\n".join(lines) + "\n").encode())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--checkpoint", default=".work/refresh", help="ignored directory under .work/; contains compressed public API evidence")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--publish", action="store_true", help="promote only a complete, publication-safe collection")
    ap.add_argument("--budget", type=int, default=900, help="hard HTTP request ceiling for this invocation (default 900)")
    ap.add_argument("--reserve", type=int, default=60, help="unspent requests for other sessions/workflow operations (default 60)")
    ap.add_argument("--max-age", type=int, default=86400, help="maximum collection age in seconds (default 86400; never over 24h)")
    args = ap.parse_args(argv)
    directory = (ROOT / args.checkpoint).resolve()
    if not directory.is_relative_to((ROOT / ".work").resolve()) or directory == (ROOT / ".work").resolve():
        ap.error("--checkpoint must be a child directory of the ignored .work/ directory")
    if not 0 < args.max_age <= 86400:
        ap.error("--max-age must be between 1 and 86400 seconds")
    directory.mkdir(parents=True, exist_ok=True)
    try:
        budget = Budget(args.budget, args.reserve)
        with open(directory / "lock", "a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise CheckpointError("another process owns this checkpoint; do not run parallel refreshes")
            state = prepare(directory, args.resume, args.max_age)
            save = lambda: write_json(directory / "checkpoint.json", state)
            attempt = {"startedAt": utc_now(), "budget": args.budget, "reserve": args.reserve}
            state["attempts"].append(attempt)
            state.pop("pause", None)
            save()
            code = 0
            try:
                pending = [s for s in STAGES if not state["phases"].get(s, {}).get("complete")]
                if pending:
                    budget.preflight()
                for stage in pending:
                    if state["inputs"] != fingerprint(ROOT):
                        raise CheckpointError("inputs changed during collection; no mixed-source pass is permitted")
                    print("\n=== %s (ceiling %s, used %s) ===" % (stage, budget.ceiling, budget.used), flush=True)
                    collection = Collection(directory, state, stage, budget, save)
                    log = directory / "logs" / (stage + ".log")
                    log.parent.mkdir(exist_ok=True)
                    with open(log, "a", encoding="utf-8") as fh, contextlib.redirect_stdout(fh), contextlib.redirect_stderr(fh):
                        report, complete = run_stage(stage, collection, directory / "staged")
                    phase = state["phases"][stage]
                    outputs = []
                    if stage == "build_data":
                        outputs = ["data/sites.js"]
                    elif stage in REPORTS:
                        outputs = [REPORTS[stage]]
                    if stage == "audit_provenance":
                        outputs += [str(p.relative_to(directory / "staged"))
                                    for p in sorted((directory / "staged/reports/provenance").glob("*.md"))]
                    phase.update({"report": report, "complete": complete, "apiCollection": collection.summary(),
                                  "outputs": {name: hashlib.sha256((directory / "staged" / name).read_bytes()).hexdigest()
                                              for name in outputs}})
                    save()
                    if not complete:
                        raise CheckpointError("%s did not complete; its report is not a pass" % stage)
                state["finishedAt"] = utc_now()
                blockers = publication_blockers(state)
                lint = state["phases"].get("audit_descriptions", {}).get("report", {}).get("unresolved")
                state["status"] = "BLOCKED_FINDINGS" if blockers else ("COMPLETE_WITH_REVIEW" if lint else "COMPLETE")
                if blockers:
                    print("Publication blocked:", "; ".join(blockers))
                    code = 1
                elif args.publish:
                    promote(directory, state)
                else:
                    print("Collection complete. Use --resume --publish to explicitly promote it; nothing published yet.")
                if lint:
                    print("Description lint has source-review findings; retain/record them in FLAGGED.md, never silently fix stamps.")
                    code = 1
            except Paused as exc:
                state.update({"status": "INCOMPLETE", "pause": {**exc.detail, "pausedAt": utc_now()}})
                print("PAUSED (published files unchanged):", exc)
                print("Continue the same collection with --resume after the API window permits it.")
                code = 2
            except (CheckpointError, SystemExit, AssertionError, OSError, ValueError, KeyError, TypeError) as exc:
                state.update({"status": "INCOMPLETE", "pause": {"reason": str(exc), "pausedAt": utc_now()}})
                print("REFRESH BLOCKED (no partial snapshot promoted):", exc, file=sys.stderr)
                code = 2
            finally:
                attempt.update({"finishedAt": utc_now(), "requests": budget.used, "quota": budget.quota})
                for phase in state["phases"].values():
                    stamps = [r["readAt"] for r in phase.get("responses", {}).values()]
                    if stamps and not phase.get("complete"):
                        phase["apiCollection"] = {"oldestReadAt": min(stamps), "newestReadAt": max(stamps)}
                save()
                write_summary(directory, state)
            print("Full refresh status:", state["status"], "· report:", directory / "report.md")
            return code
    except CheckpointError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
