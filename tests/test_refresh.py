"""Offline tests of the quota/checkpoint/publication contract (T-029).

All HTTP answers are synthetic fixtures, never live facts or published records.
The integration tests run the real builder and four audit modules in a temporary
checkout. No network, Git operation, or production file modification occurs.
"""

import contextlib
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
import urllib.error
import urllib.parse
from unittest.mock import patch

from tools import refresh as rf


class Response:
    def __init__(self, body, status=200, headers=None):
        self.status = status
        self.raw = body.encode() if isinstance(body, str) else json.dumps(body).encode()
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def read(self):
        return self.raw


class Network:
    def __init__(self, body=None):
        self.calls = []
        self.answer = body if body is not None else {"official": "fixture"}

    def __call__(self, request, timeout):
        self.calls.append(request)
        value = self.answer(request) if callable(self.answer) else self.answer
        if isinstance(value, Exception):
            raise value
        if isinstance(value, Response):
            return value
        return Response(value)


def quota(remaining=5000):
    return {"resources": {"core": {"remaining": remaining, "limit": 5000, "reset": 1791775000, "used": 0}}}


def error(status, message, headers=None):
    return urllib.error.HTTPError(rf.API + "/fixture", status, message, headers or {},
                                  io.BytesIO(json.dumps({"message": message}).encode()))


class BudgetTests(unittest.TestCase):
    def test_probe_and_redirects_count_toward_the_ceiling(self):
        net = Network(lambda r: quota() if r.full_url.endswith("/rate_limit") else {"ok": True})
        b = rf.Budget(4, 1, net, gap=0)
        b.preflight()
        b.fetch(rf.API + "/repos/owner/a")
        b.fetch(rf.API + "/repos/owner/b")
        with self.assertRaises(rf.Paused):
            b.fetch(rf.API + "/repos/owner/c")
        self.assertEqual(b.used, 3)
        self.assertEqual(len(net.calls), 3)

    def test_conservative_quota_never_spends_reserve(self):
        net = Network(Response(quota(1000), headers={"X-RateLimit-Remaining": "2"}))
        b = rf.Budget(100, 2, net, gap=0)
        b.preflight()
        self.assertEqual(b.quota["effectiveRemaining"], 2)
        with self.assertRaises(rf.Paused):
            b.fetch(rf.API + "/repos/owner/a")
        self.assertEqual(len(net.calls), 1)

    def test_unknown_quota_is_not_a_license_to_spend(self):
        b = rf.Budget(100, 0, Network({"resources": {}}), gap=0)
        with self.assertRaisesRegex(rf.Paused, "could not verify"):
            b.preflight()

    def test_primary_header_can_shrink_budget_mid_phase(self):
        net = Network(Response({}, headers={"x-ratelimit-remaining": "0"}))
        b = rf.Budget(100, 0, net, gap=0)
        b.fetch(rf.API + "/repos/owner/a")
        with self.assertRaises(rf.Paused):
            b.fetch(rf.API + "/repos/owner/b")
        self.assertEqual(len(net.calls), 1)

    def test_auth_secondary_rate_and_server_blocks_never_become_answers(self):
        for status in (401, 403, 429, 500, 503):
            with self.subTest(status=status):
                net = Network(error(status, "blocked", {"Retry-After": "60"}))
                b = rf.Budget(100, 0, net, gap=0)
                with self.assertRaises(rf.Paused) as caught:
                    b.fetch(rf.API + "/repos/owner/a")
                self.assertEqual(caught.exception.detail["httpStatus"], status)
                self.assertTrue(caught.exception.detail["retrySuggestedAt"])
                with self.assertRaises(rf.Paused):
                    b.fetch(rf.API + "/repos/owner/b")
                self.assertEqual(len(net.calls), 1)

    def test_transport_failure_establishes_no_repo_verdict(self):
        b = rf.Budget(100, 0, Network(OSError("fixture TLS failure")), gap=0)
        with self.assertRaises(rf.Paused) as caught:
            b.fetch(rf.API + "/repos/owner/a")
        self.assertEqual(caught.exception.detail["httpStatus"], 0)
        self.assertIn("no repository verdict", str(caught.exception))

    def test_documented_negative_answers_can_be_reproduced(self):
        for status in (404, 409, 422):
            with self.subTest(status=status):
                b = rf.Budget(100, 0, Network(error(status, "documented negative")), gap=0)
                self.assertEqual(b.fetch(rf.API + "/repos/owner/a")["status"], status)

    def test_redirect_hops_each_spend_a_request(self):
        def answer(req):
            if req.full_url.endswith("/old"):
                return error(301, "renamed", {"Location": rf.API + "/new"})
            return {"ok": True}
        net = Network(answer)
        b = rf.Budget(10, 0, net, gap=0)
        result = b.fetch(rf.API + "/old")
        self.assertEqual(result["url"], rf.API + "/new")
        self.assertEqual(b.used, 2)

    def test_untrusted_redirect_is_never_followed_with_a_token(self):
        net = Network(error(302, "redirect", {"Location": "https://example.test/steal"}))
        b = rf.Budget(10, 0, net, gap=0)
        with patch.dict(os.environ, {"GH_TOKEN": "fixture-secret", "GITHUB_TOKEN": ""}):
            with self.assertRaises(rf.CheckpointError):
                b.fetch(rf.API + "/old")
        self.assertEqual(len(net.calls), 1)
        self.assertEqual(net.calls[0].get_header("Authorization"), "Bearer fixture-secret")

    def test_nonofficial_urls_and_query_credentials_are_refused(self):
        for url in ("http://api.github.com/a", "https://api.github.com.evil.test/a", "//evil.test/a",
                    "https://user:pass@api.github.com/a", rf.API + "/a?access_token=secret", rf.API + "/a#fragment"):
            with self.subTest(url=url), self.assertRaises(rf.CheckpointError):
                rf.official_url(url)

    def test_invalid_ceiling_is_refused(self):
        for budget, reserve in ((0, 0), (1, 0), (20, 20), (100, -1)):
            with self.subTest(budget=budget, reserve=reserve), self.assertRaises(rf.CheckpointError):
                rf.Budget(budget, reserve)


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.state = {"phases": {}}
        self.saves = []

    def tearDown(self):
        self.temp.cleanup()

    def client(self, network=None, stage="build_data", budget=100):
        net = network or Network()
        guard = rf.Budget(budget, 0, net, gap=0)
        return rf.Collection(self.directory, self.state, stage, guard,
                             lambda: self.saves.append(True)), guard, net

    def test_resume_replays_original_answer_without_spending_or_restamping(self):
        c, b, net = self.client()
        with patch.object(rf, "utc_now", return_value="2026-10-12T01:00:00Z"):
            self.assertEqual(c.get("/repos/owner/a")[0], 200)
        old = c.summary()["oldestReadAt"]
        resumed, budget, unused = self.client(Network(OSError("must not run")))
        self.assertEqual(resumed.get("/repos/owner/a"), (200, {"official": "fixture"}))
        self.assertEqual(budget.used, 0)
        self.assertEqual(len(unused.calls), 0)
        self.assertEqual(resumed.summary()["oldestReadAt"], old)
        self.assertEqual(resumed.replays, 1)

    def test_official_rename_redirect_replays_without_spending_or_restamping(self):
        def answer(request):
            if request.full_url == rf.API + "/repos/owner/old/readme?ref=abc1234":
                return error(301, "renamed", {"Location": rf.API + "/repositories/123/readme?ref=abc1234"})
            return {"official": "redirected fixture"}
        c, used, net = self.client(Network(answer), stage="audit_provenance")
        path = "/repos/owner/old/readme?ref=abc1234"
        with patch.object(rf, "utc_now", return_value="2026-10-12T01:00:00Z"):
            self.assertEqual(c.get(path), (200, {"official": "redirected fixture"}))
        self.assertEqual(used.used, 2)
        meta = next(iter(c.phase["responses"].values()))
        self.assertEqual(meta["requestUrl"], rf.API + path)
        self.assertNotEqual(meta["url"], meta["requestUrl"])
        resumed, budget, unused = self.client(Network(OSError("must not run")), stage="audit_provenance")
        self.assertEqual(resumed.get(path), (200, {"official": "redirected fixture"}))
        self.assertEqual(budget.used, 0)
        self.assertEqual(unused.calls, [])
        self.assertEqual(resumed.summary()["oldestReadAt"], "2026-10-12T01:00:00Z")

    def test_pinned_pagination_can_redirect_and_replay_the_same_wire_request(self):
        sha = "a" * 40
        base = "/repos/owner/old/commits?sha=main&per_page=100&page="
        def answer(request):
            parts = urllib.parse.urlsplit(request.full_url)
            q = urllib.parse.parse_qs(parts.query)
            if q.get("page") == ["1"]:
                return [{"sha": sha}]
            if parts.path.startswith("/repos/"):
                self.assertEqual(q["sha"], [sha])
                return error(301, "renamed", {"Location": rf.API + "/repositories/123/commits?" + parts.query})
            return []
        c, budget, _ = self.client(Network(answer))
        c.get(base + "1")
        c.get(base + "2")
        self.assertEqual(budget.used, 3)
        resumed, budget, unused = self.client(Network(OSError("must not run")))
        resumed.get(base + "1")
        self.assertEqual(resumed.get(base + "2"), (200, []))
        self.assertEqual(budget.used, 0)
        self.assertEqual(unused.calls, [])

    def test_original_wire_url_cannot_be_changed_in_metadata_alone(self):
        c, _, _ = self.client()
        c.get("/repos/owner/a")
        next(iter(c.phase["responses"].values()))["requestUrl"] = rf.API + "/repos/owner/other"
        resumed, budget, _ = self.client()
        with self.assertRaises(rf.CheckpointError):
            resumed.get("/repos/owner/a")
        self.assertEqual(budget.used, 0)

    def test_budget_pause_can_continue_without_recaching_a_block(self):
        c, b, net = self.client(budget=2)
        c.get("/repos/owner/a")
        c.get("/repos/owner/b")
        with self.assertRaises(rf.Paused):
            c.get("/repos/owner/c")
        self.assertEqual(len(c.phase["responses"]), 2)
        resumed, budget, net2 = self.client()
        resumed.get("/repos/owner/a")
        resumed.get("/repos/owner/b")
        resumed.get("/repos/owner/c")
        self.assertEqual(budget.used, 1)
        self.assertEqual(len(net2.calls), 1)
        self.assertEqual(c.phase["requests"], 3)

    def test_access_block_is_not_a_cache_hit_on_resume(self):
        c, _, _ = self.client(Network(error(403, "secondary rate limit")))
        with self.assertRaises(rf.Paused):
            c.get("/repos/owner/a")
        self.assertEqual(c.phase["responses"], {})
        resumed, b, _ = self.client()
        self.assertEqual(resumed.get("/repos/owner/a")[0], 200)
        self.assertEqual(b.used, 1)

    def test_new_audit_namespace_cannot_reuse_builder_evidence(self):
        c, _, _ = self.client()
        c.get("/repos/owner/a")
        audit, budget, _ = self.client(stage="verify_live")
        audit.get("/repos/owner/a")
        self.assertEqual(budget.used, 1)
        self.assertEqual(audit.replays, 0)

    def test_deliberate_reread_gets_a_distinct_official_answer(self):
        values = iter(({"status": "building"}, {"status": "built"}))
        c, _, _ = self.client(Network(lambda _: next(values)))
        self.assertEqual(c.get("/repos/owner/a/pages")[1]["status"], "building")
        self.assertEqual(c.get("/repos/owner/a/pages")[1]["status"], "built")
        resumed, budget, _ = self.client(Network(OSError("no network")))
        self.assertEqual(resumed.get("/repos/owner/a/pages")[1]["status"], "building")
        self.assertEqual(resumed.get("/repos/owner/a/pages")[1]["status"], "built")
        self.assertEqual(budget.used, 0)

    def test_accept_representation_is_part_of_the_key(self):
        c, budget, _ = self.client()
        c.get("/repos/owner/a/readme")
        c.get("/repos/owner/a/readme", accept="application/vnd.github.raw")
        self.assertEqual(budget.used, 2)
        self.assertEqual(len(c.phase["responses"]), 2)

    def test_response_mutation_does_not_change_official_checkpoint(self):
        c, _, _ = self.client()
        body = c.get("/repos/owner/a")[1]
        body["official"] = "invented"
        resumed, _, _ = self.client()
        self.assertEqual(resumed.get("/repos/owner/a")[1]["official"], "fixture")

    def test_corrupt_response_refuses_resume_instead_of_making_up_a_value(self):
        c, _, _ = self.client()
        c.get("/repos/owner/a")
        file = next((self.directory / "responses/build_data").glob("*.gz"))
        file.write_bytes(gzip.compress(b'{"body":"tampered"}'))
        resumed, budget, _ = self.client()
        with self.assertRaises(rf.CheckpointError):
            resumed.get("/repos/owner/a")
        self.assertEqual(budget.used, 0)

    def test_original_timestamp_cannot_be_changed_in_checkpoint_metadata_alone(self):
        c, _, _ = self.client()
        c.get("/repos/owner/a")
        next(iter(c.phase["responses"].values()))["readAt"] = "2030-01-01T00:00:00Z"
        resumed, budget, _ = self.client()
        with self.assertRaises(rf.CheckpointError):
            resumed.get("/repos/owner/a")
        self.assertEqual(budget.used, 0)

    def test_pagination_is_pinned_to_first_full_head_sha_and_survives_resume(self):
        sha = "a" * 40
        c, _, _ = self.client(Network([{"sha": sha}]))
        base = "/repos/owner/a/commits?sha=main&per_page=100&page="
        c.get(base + "1")
        resumed, budget, net = self.client(Network([]))
        resumed.get(base + "1")
        resumed.get(base + "2")
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(net.calls[0].full_url).query)
        self.assertEqual(query["sha"], [sha])
        self.assertEqual(budget.used, 1)
        self.assertIn("sha=" + sha, resumed.sources_for("owner", "a")[-1]["url"])

    def test_a_citation_audit_does_not_rewrite_its_cited_query(self):
        c, _, net = self.client(Network([{"sha": "a" * 40}]), stage="audit_provenance")
        c.get("/repos/owner/a/commits?sha=main&per_page=100&page=1")
        c.get("/repos/owner/a/commits?sha=main&per_page=100&page=2")
        self.assertIn("sha=main", net.calls[-1].full_url)

    def test_source_list_has_read_times_and_does_not_confuse_repo_prefixes(self):
        c, _, _ = self.client()
        c.get("/repos/owner/a")
        c.get("/repos/owner/aa")
        c.get("/repos/owner/a/pages")
        sources = c.sources_for("owner", "a")
        self.assertEqual(len(sources), 2)
        self.assertTrue(all(s["readAt"] and s["url"].startswith(rf.API) for s in sources))

    def test_checkpoint_never_contains_authorization_headers(self):
        net = Network(Response({}, headers={"Authorization": "private", "Set-Cookie": "private", "x-ratelimit-remaining": "5000"}))
        c, _, _ = self.client(net)
        with patch.dict(os.environ, {"GH_TOKEN": "fixture-secret", "GITHUB_TOKEN": ""}):
            c.get("/repos/owner/a")
        raw = gzip.decompress(next((self.directory / "responses/build_data").glob("*.gz")).read_bytes())
        self.assertNotIn(b"fixture-secret", raw)
        self.assertNotIn(b"private", raw)
        self.assertNotIn(b"Authorization", raw)


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.original_root = rf.ROOT
        for name in rf.INPUTS:
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(rf.ROOT / name, self.root / name)
        self.sha = "a" * 40
        self.readmes = {}
        entry = {"title": "Fixture site", "category": "Directory & Meta", "kind": "app",
                 "description": "Public fixture site documented in its README.", "flags": [],
                 "lastVerified": "2026-10-12T01:00:00Z", "verifiedAtSha": self.sha,
                 "verifiedBasis": "Read from https://api.github.com/repos/buffedlizard55-lab/{repo}/readme?ref=" + self.sha}
        self.overlay = {"entries": {name: {**entry, "verifiedBasis": entry["verifiedBasis"].format(repo=name)} for name in ("A", "B")},
                        "retired": [], "excluded": [], "irregularities": []}
        rf.write_json(self.root / "tools/overlay.json", self.overlay)
        rf.write_json(self.root / "tools/families.json", {"families": []})
        (self.root / "data").mkdir()
        (self.root / "data/sites.js").write_text("previous good snapshot\n")
        for name in rf.REPORTS.values():
            (self.root / name).write_text("previous audit report\n")
        self.initial = {p: (self.root / p).read_bytes() for p in ("data/sites.js", *rf.REPORTS.values())}
        self.net = Network(self.answer)
        self.root_patch = patch.object(rf, "ROOT", self.root)
        self.root_patch.start()
        real_budget = rf.Budget
        self.budget_patch = patch.object(rf, "Budget", side_effect=lambda *args: real_budget(*args, opener=self.net, gap=0))
        self.budget_patch.start()

    def tearDown(self):
        self.budget_patch.stop()
        self.root_patch.stop()
        self.temp.cleanup()

    def answer(self, req):
        parts = urllib.parse.urlsplit(req.full_url)
        path = parts.path
        if path == "/rate_limit":
            return quota()
        if path.startswith("/users/"):
            owner = path.split("/")[2]
            names = ["A", "B"] if owner == rf.ACCOUNTS[0] else []
            if path.endswith("/repos"):
                return [{"name": name, "private": False, "owner": {"login": owner}} for name in names]
            return {"login": owner, "public_repos": len(names), "created_at": "2026-01-01T00:00:00Z", "type": "User",
                    "html_url": "https://github.com/" + owner}
        repo = path.split("/")[3]
        if path.endswith("/pages"):
            return {"status": "built", "source": {"branch": "main", "path": "/"}, "html_url": "https://buffedlizard55-lab.github.io/%s/" % repo}
        if path.endswith("/commits"):
            return [{"sha": self.sha, "commit": {"committer": {"date": "2026-01-02T00:00:00Z"}}}]
        if "/commits/" in path:
            ref = path.rsplit("/", 1)[1]
            return {"sha": self.sha if self.sha.startswith(ref) else ref}
        if path.endswith("index.html"):
            return "<!doctype html><title>Fixture site</title>"
        if path.endswith("/readme") or path.endswith("README.md"):
            ref = urllib.parse.parse_qs(parts.query).get("ref", [""])[0]
            return self.readmes.get(ref, "# Fixture site\nPublic fixture site documented in its README.")
        return {"created_at": "2026-01-01T00:00:00Z", "pushed_at": "2026-01-02T00:00:00Z", "updated_at": "2026-01-02T00:00:00Z",
                "size": 1, "default_branch": "main", "name": repo, "private": False}

    def invoke(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return rf.main(["--budget", "10", "--reserve", "1", *args])

    def assert_unpublished(self):
        for name, body in self.initial.items():
            self.assertEqual((self.root / name).read_bytes(), body, name)

    def complete(self):
        code = self.invoke()
        for _ in range(30):
            self.assert_unpublished()
            if code != 2:
                return code
            code = self.invoke("--resume")
        self.fail("synthetic collection did not finish")

    def test_real_tools_resume_across_windows_and_only_explicitly_publish_at_end(self):
        self.assertEqual(self.complete(), 0)
        directory = self.root / ".work/refresh"
        state = json.loads((directory / "checkpoint.json").read_text())
        self.assertGreater(len(state["attempts"]), 1)
        self.assertTrue(all(a["requests"] <= 9 for a in state["attempts"]))
        self.assertEqual(sum(a["requests"] for a in state["attempts"]), len(self.net.calls))
        before = len(self.net.calls)
        self.assertEqual(self.invoke("--resume", "--publish"), 0)
        self.assertEqual(len(self.net.calls), before, "promoting completed evidence needs no new API request")
        published = rf.load_snapshot(self.root / "data/sites.js")
        self.assertEqual(len(published["sites"]), 2)
        self.assertEqual(published["apiCollection"]["responses"], len(state["phases"]["build_data"]["responses"]))
        self.assertTrue(all(s["apiSources"] for s in published["sites"]))
        for report in rf.REPORTS.values():
            payload = json.loads((self.root / report).read_text())
            self.assertTrue(payload["complete"])
            self.assertEqual(payload["snapshotGenerated"], published["generated"])
            self.assertIn("oldestReadAt", payload["apiCollection"])

    def test_real_audit_modules_resume_an_official_renamed_citation(self):
        old = rf.API + "/repos/buffedlizard55-lab/OldAlias/readme?ref=" + self.sha
        self.overlay["entries"]["A"]["verifiedBasis"] += "; Previous name: " + old
        rf.write_json(self.root / "tools/overlay.json", self.overlay)
        original = self.answer
        def redirected(request):
            if request.full_url == old:
                return error(301, "renamed", {"Location": rf.API + "/repositories/123/readme?ref=" + self.sha})
            return original(request)
        self.net.answer = redirected
        self.assertEqual(self.complete(), 0)
        state = json.loads((self.root / ".work/refresh/checkpoint.json").read_text())
        redirected_sources = [r for r in state["phases"]["audit_provenance"]["responses"].values()
                              if r["requestedUrl"] == old]
        self.assertEqual(len(redirected_sources), 1)
        self.assertEqual(redirected_sources[0]["url"], rf.API + "/repositories/123/readme?ref=" + self.sha)
        self.assertGreater(state["phases"]["audit_provenance"]["apiCollection"]["checkpointReplaysThisInvocation"], 0)
        self.assertEqual(self.invoke("--resume", "--publish"), 0)

    def test_paused_pass_is_incomplete_and_has_no_fabricated_audit_pass(self):
        self.assertEqual(self.invoke(), 2)
        self.assert_unpublished()
        report = json.loads((self.root / ".work/refresh/report.json").read_text())
        self.assertEqual(report["status"], "INCOMPLETE")
        self.assertTrue(report["publicationBlockers"])
        self.assertNotEqual(report["stages"][0]["verdict"], "PASS")
        self.assertTrue(all(p["verdict"] == "NOT-RUN" for p in report["stages"][1:]))

    def test_lint_findings_stay_findings_but_do_not_become_a_fake_access_block(self):
        old_sha = "b" * 40
        self.overlay["entries"]["A"].update({"description": "The older README claims 987654321 records.",
                                              "verifiedAtSha": old_sha,
                                              "verifiedBasis": rf.API + "/repos/buffedlizard55-lab/A/readme?ref=" + old_sha})
        self.readmes[old_sha] = "# Older fixture README\n987654321 records."
        rf.write_json(self.root / "tools/overlay.json", self.overlay)
        self.assertEqual(self.complete(), 1)
        state = json.loads((self.root / ".work/refresh/checkpoint.json").read_text())
        self.assertEqual(state["status"], "COMPLETE_WITH_REVIEW")
        self.assertEqual(len(state["phases"]["audit_descriptions"]["report"]["unresolved"]), 1)
        self.assertEqual(rf.publication_blockers(state), [])
        self.assertEqual(self.invoke("--resume", "--publish"), 1)
        published = rf.load_snapshot(self.root / "data/sites.js")
        self.assertTrue(published["sites"][0]["proseStale"])
        self.assertEqual(published["sites"][0]["verifiedAtSha"], old_sha)

    def test_changed_inputs_refuse_replay(self):
        self.assertEqual(self.invoke(), 2)
        self.overlay["entries"]["A"]["title"] = "Changed input"
        rf.write_json(self.root / "tools/overlay.json", self.overlay)
        before = len(self.net.calls)
        self.assertEqual(self.invoke("--resume"), 2)
        self.assertEqual(len(self.net.calls), before)
        self.assert_unpublished()

    def test_aged_checkpoint_cannot_be_relabelled_as_fresh(self):
        self.assertEqual(self.invoke(), 2)
        path = self.root / ".work/refresh/checkpoint.json"
        state = json.loads(path.read_text())
        state["startedAt"] = "2020-01-01T00:00:00Z"
        rf.write_json(path, state)
        before = len(self.net.calls)
        self.assertEqual(self.invoke("--resume"), 2)
        self.assertEqual(len(self.net.calls), before)
        self.assert_unpublished()

    def test_future_dated_checkpoint_is_not_a_fresh_collection(self):
        self.assertEqual(self.invoke(), 2)
        path = self.root / ".work/refresh/checkpoint.json"
        state = json.loads(path.read_text())
        state["startedAt"] = "2030-01-01T00:00:00Z"
        rf.write_json(path, state)
        before = len(self.net.calls)
        self.assertEqual(self.invoke("--resume"), 2)
        self.assertEqual(len(self.net.calls), before)
        self.assert_unpublished()

    def test_inputs_changed_after_prepare_cannot_be_promoted(self):
        self.assertEqual(self.complete(), 0)
        directory = self.root / ".work/refresh"
        state = json.loads((directory / "checkpoint.json").read_text())
        self.overlay["entries"]["A"]["title"] = "Changed after preparing the phase"
        rf.write_json(self.root / "tools/overlay.json", self.overlay)
        with self.assertRaises(rf.CheckpointError):
            rf.promote(directory, state)
        self.assert_unpublished()

    def test_output_tampering_refuses_all_promotion_not_just_the_bad_file(self):
        self.assertEqual(self.complete(), 0)
        path = self.root / ".work/refresh/staged/data/sites.js"
        path.write_text("hand edited staged output")
        self.assertEqual(self.invoke("--resume", "--publish"), 2)
        self.assert_unpublished()

    def test_parallel_process_cannot_take_the_same_checkpoint(self):
        directory = self.root / ".work/refresh"
        directory.mkdir(parents=True)
        with open(directory / "lock", "a") as lock:
            rf.fcntl.flock(lock, rf.fcntl.LOCK_EX | rf.fcntl.LOCK_NB)
            self.assertEqual(self.invoke(), 2)
        self.assertEqual(len(self.net.calls), 0)
        self.assert_unpublished()

    def test_initial_existing_checkpoint_requires_explicit_resume(self):
        self.assertEqual(self.invoke(), 2)
        before = len(self.net.calls)
        self.assertEqual(self.invoke(), 2)
        self.assertEqual(len(self.net.calls), before)

    def test_checkpoint_location_cannot_overwrite_repository_root(self):
        for directory in (".", ".git", "data", ".work", "../outside"):
            with self.subTest(directory=directory), self.assertRaises(SystemExit):
                self.invoke("--checkpoint", directory)


class PredicateTests(unittest.TestCase):
    def state(self):
        return {"phases": {name: {"complete": True, "report": {}} for name in rf.STAGES}}

    def test_any_incomplete_stage_blocks_promotion(self):
        state = self.state()
        for stage in rf.STAGES:
            with self.subTest(stage=stage):
                altered = json.loads(json.dumps(state))
                altered["phases"][stage]["complete"] = False
                self.assertTrue(rf.publication_blockers(altered))

    def test_all_nonlint_hard_findings_block_promotion(self):
        for stage, key, value in (("build_data", "coverageGaps", ["fixture"]), ("audit_kind", "disagreements", ["fixture"]),
                                  ("audit_provenance", "findings", ["fixture"]), ("verify_live", "hardMismatchCount", 1),
                                  ("coverage", "gaps", ["fixture"])):
            with self.subTest(stage=stage):
                state = self.state()
                state["phases"][stage]["report"][key] = value
                self.assertTrue(rf.publication_blockers(state))

    def test_verifier_set_difference_cannot_be_hidden_by_a_zero_mismatch_count(self):
        for field in ("unlistedInApi", "listedNotInApi", "hardMismatches"):
            with self.subTest(field=field):
                state = self.state()
                state["phases"]["verify_live"]["report"].update({"hardMismatchCount": 0, field: ["fixture"]})
                self.assertTrue(rf.publication_blockers(state))

    def test_lint_is_review_not_proof_and_volatile_drift_is_not_a_hard_finding(self):
        state = self.state()
        state["phases"]["audit_descriptions"]["report"]["unresolved"] = [{"repo": "fixture"}]
        state["phases"]["verify_live"]["report"]["driftCount"] = 10
        self.assertEqual(rf.publication_blockers(state), [])

    def test_final_census_rejects_private_or_mismatched_owner_data(self):
        class Fake:
            def get(self, path):
                if path.startswith("/users/") and "/repos?" not in path:
                    return 200, {"public_repos": 1}
                return 200, [{"name": "fixture", "private": True, "owner": {"login": rf.ACCOUNTS[0]}}]
        with self.assertRaises(rf.CheckpointError):
            rf.coverage(Fake(), {"sites": [], "counts": {"excluded": []}})

    def test_final_census_checks_second_account_instead_of_assuming_empty(self):
        class Fake:
            def get(self, path):
                owner = path.split("/")[2]
                if "/repos?" not in path:
                    return 200, {"public_repos": 0 if owner == rf.ACCOUNTS[0] else 1}
                return 200, [] if owner == rf.ACCOUNTS[0] else [{"name": "new", "private": False, "owner": {"login": owner}}]
        result = rf.coverage(Fake(), {"sites": [], "counts": {"excluded": []}})
        self.assertEqual(result["gaps"][0]["owner"], rf.ACCOUNTS[1])
        self.assertEqual(result["gaps"][0]["unlisted"], ["new"])


if __name__ == "__main__":
    unittest.main()
