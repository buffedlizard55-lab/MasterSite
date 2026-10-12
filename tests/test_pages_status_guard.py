"""Offline unit tests for tools/pages_status_guard.py (T-026).

No network and no repository writes: every case feeds a synthetic official
Pages response into the pure classifier. The rules under test are the ones
that keep the daily watch honest:

  - a transition in either direction is a finding (stale record either way),
  - an entry that is live `errored` is a finding even when the published
    record already says `errored` (the task requires an issue for any entry
    that is not `built`, until it recovers),
  - an unreadable Pages endpoint (HTTP 404) on a listed entry is a finding,
  - an API status the tool does not understand produces no verdict here —
    `run_guard` turns it into exit 2 before classification,
  - every finding carries the exact official endpoint and the read timestamp
    so a reviewer can re-open it by hand.
"""
import unittest

from tools import pages_status_guard as psg

READ_AT = "2026-10-12T00:00:00Z"
OWNER = "buffedlizard55-lab"
REPO = "ExampleRepo"


def site(published, repo=REPO, owner=None):
    s = {"repo": repo, "pagesStatus": published}
    if owner is not None:
        s["owner"] = owner
    return s


def classify(published, http_status, payload, repo=REPO):
    return psg.classify_entry(site(published, repo), OWNER, http_status, payload, READ_AT)


class ClassifyTests(unittest.TestCase):
    def test_built_matching_published_is_clean(self):
        res = classify("built", 200, {"status": "built"})
        self.assertEqual(res["findings"], [])
        self.assertEqual(res["live"], "built")
        self.assertEqual(res["published"], "built")

    def test_built_to_errored_is_transition_and_not_built(self):
        res = classify("built", 200, {"status": "errored"})
        self.assertEqual(res["findings"], ["transition", "not-built"])

    def test_stable_errored_is_still_a_finding_even_when_it_matches(self):
        # Matches the published record (no transition) but is not built, and
        # T-026 requires a loud finding for every entry that is not built.
        res = classify("errored", 200, {"status": "errored"})
        self.assertEqual(res["findings"], ["not-built"])

    def test_recovery_to_built_is_a_transition_because_the_record_is_stale(self):
        res = classify("errored", 200, {"status": "built"})
        self.assertEqual(res["findings"], ["transition"])
        self.assertNotIn("not-built", res["findings"])

    def test_building_is_transition_and_not_built(self):
        res = classify("built", 200, {"status": "building"})
        self.assertEqual(res["findings"], ["transition", "not-built"])

    def test_http_404_is_unreadable_and_never_invents_a_live_status(self):
        res = classify("built", 404, {"message": "Not Found"})
        self.assertEqual(res["findings"], ["pages-unreadable"])
        self.assertIsNone(res["live"])

    def test_unrecognized_http_status_yields_no_verdict_here(self):
        # run_guard fail_api()s on anything outside 200/404 before classifying;
        # the classifier itself must not turn it into a finding or a pass.
        res = classify("built", 500, {"message": "server error"})
        self.assertEqual(res["findings"], [])
        self.assertIsNone(res["live"])
        self.assertEqual(res["http"], 500)

    def test_finding_carries_exact_official_endpoint_and_read_time(self):
        res = classify("built", 200, {"status": "errored"})
        self.assertEqual(
            res["source"],
            "https://api.github.com/repos/%s/%s/pages" % (OWNER, REPO),
        )
        self.assertEqual(res["readAt"], READ_AT)

    def test_missing_status_key_is_not_built_never_a_silent_pass(self):
        res = classify("built", 200, {})
        self.assertEqual(res["findings"], ["transition", "not-built"])
        self.assertIsNone(res["live"])


class OwnerResolutionTests(unittest.TestCase):
    def test_record_owner_wins(self):
        snap = {"owner": "snapshot-owner"}
        self.assertEqual(
            psg.site_owner(site("built", owner="record-owner"), snap), "record-owner"
        )

    def test_snapshot_owner_is_the_fallback(self):
        snap = {"owner": "snapshot-owner"}
        self.assertEqual(psg.site_owner(site("built"), snap), "snapshot-owner")

    def test_default_owner_is_the_last_resort(self):
        self.assertEqual(psg.site_owner(site("built"), {}), psg.DEFAULT_OWNER)


class SnapshotContractTests(unittest.TestCase):
    """The guard reads the committed snapshot; pin the shape it relies on."""

    def test_published_snapshot_has_sites_with_pages_status(self):
        snap = psg.load_snapshot()
        sites = snap.get("sites") or []
        self.assertGreater(len(sites), 0)
        for s in sites:
            self.assertIn("pagesStatus", s)
            self.assertIn("repo", s)

    def test_frozen_unreachable_records_are_not_listed_sites(self):
        # The four frozen 404 records live in snapshot.unreachable, not in
        # sites[] — the guard must never probe them as live entries (FL-03).
        snap = psg.load_snapshot()
        listed = {s["repo"] for s in snap.get("sites") or []}
        frozen = {u["repo"] for u in snap.get("unreachable") or []}
        self.assertEqual(listed & frozen, set())


if __name__ == "__main__":
    unittest.main()
