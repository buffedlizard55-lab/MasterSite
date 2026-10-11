"""Offline unit tests for tools/scheduled_audit.py (T-022).

No network and no repository writes: every case builds a payload in memory.
The rules under test are the ones that keep a scheduled run honest — a budget
ceiling that cannot be exceeded, a weekday plan that really does cover every
audit, and the invariant that a run which could not cover its own scheduled
audits is never reported as clean.
"""
import os
import re
import unittest

from tools import scheduled_audit as sa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def result(name, verdict, reason="fixture"):
    return {"audit": name, "verdict": verdict, "reason": reason, "finishedAt": sa.utc_now(),
            "toolReport": sa.AUDITS[name]["report"], "reviewEndpoint": sa.AUDITS[name]["review"],
            "what": sa.AUDITS[name]["what"], "logFile": None, "seconds": 0}


class PlanningTests(unittest.TestCase):
    def setUp(self):
        self.order = list(sa.AUDIT_ORDER)
        self.costs = {self.order[0]: 300, self.order[1]: 600, self.order[2]: 150, self.order[3]: 1100}

    def test_plan_takes_what_fits_and_reports_what_did_not(self):
        planned, skipped, left = sa.plan_run(self.order, self.costs, 500)
        self.assertEqual(planned, [self.order[0], self.order[2]])
        self.assertEqual([s["audit"] for s in skipped], [self.order[1], self.order[3]])
        self.assertEqual(left, 50)

    def test_strict_plan_stops_at_the_first_audit_that_does_not_fit(self):
        planned, skipped, _ = sa.plan_run(self.order, self.costs, 500, skip_ahead=False)
        self.assertEqual(planned, [self.order[0]])
        self.assertEqual([s["audit"] for s in skipped], self.order[1:])

    def test_zero_budget_plans_nothing(self):
        self.assertEqual(sa.plan_run(self.order, self.costs, 0)[0], [])

    def test_a_missing_cost_entry_is_never_treated_as_free(self):
        planned, skipped, _ = sa.plan_run(["audit_provenance"], {}, 800)
        self.assertEqual(planned, [])
        self.assertEqual([s["audit"] for s in skipped], ["audit_provenance"])

    def test_an_unknown_slot_is_rejected_by_the_cli(self):
        with self.assertRaises(SystemExit) as raised:
            sa.main(["--slot", "funday"])
        self.assertEqual(raised.exception.code, 2)

    def test_usable_budget_never_spends_the_reserve_and_never_widens_the_ceiling(self):
        self.assertEqual(sa.usable_budget(1000, 900, 100), 800)
        self.assertEqual(sa.usable_budget(50, 900, 100), 0)
        self.assertEqual(sa.usable_budget(4000, 900, 100), 800)
        self.assertEqual(sa.usable_budget(None, 900, 100), 800)

    def test_expected_costs_come_from_the_measured_table(self):
        self.assertEqual(sa.expected_costs(["verify_live"])["verify_live"], sa.DEFAULT_COSTS["verify_live"])


class SlotPlanTests(unittest.TestCase):
    def test_every_audit_is_scheduled_at_least_twice_a_week(self):
        counts = {}
        for day in sa.SLOT_PLAN.values():
            for audit in day:
                counts[audit] = counts.get(audit, 0) + 1
        self.assertEqual(sorted(counts), sorted(sa.AUDIT_ORDER))
        for audit, count in counts.items():
            self.assertGreaterEqual(count, 2, "%s is scheduled only %d time(s) a week" % (audit, count))

    def test_sunday_attempts_the_whole_suite(self):
        self.assertEqual(sa.slot_audits("sunday"), list(sa.AUDIT_ORDER))
        self.assertEqual(sa.slot_audits(6), list(sa.AUDIT_ORDER))

    def test_slots_only_name_registered_audits(self):
        for day, audits in sa.SLOT_PLAN.items():
            for audit in audits:
                self.assertIn(audit, sa.AUDITS, "day %s names %s" % (day, audit))

    def test_slot_names_map_to_the_slot_table(self):
        for index, name in sa.SLOT_NAMES.items():
            self.assertEqual(sa.slot_audits(name), sa.slot_audits(index))

    def test_only_the_documented_slots_exceed_the_builtin_ceiling(self):
        """Which slots cannot fit 1,000/hour, measured, must be exactly these.

        The wednesday/saturday slot costs 1,000 planned (904 measured) and the
        full-suite slot 2,151 measured — both above the runner's 900 budget
        (840 spendable). Those are deliberate attempts
        that need an owner-provided larger token; README "Known Limitations"
        records that, and the runner reports them as NOT-RUN/PARTIAL instead of
        pretending they ran. Any *new* over-budget slot must fail this test so it
        cannot slip in silently.
        """
        over = {}
        for day, audits in sa.SLOT_PLAN.items():
            needed = sum(sa.DEFAULT_COSTS[a] for a in audits)
            if needed > sa.DEFAULT_BUDGET:
                over[sa.SLOT_NAMES[day]] = (audits, needed)
        self.assertEqual(sorted(over), ["saturday", "sunday", "wednesday"],
                         "unexpected over-budget slots: %s" % over)
        for day in ("wednesday", "saturday"):
            self.assertEqual(over[day][0], ["audit_provenance"])
        self.assertEqual(sorted(over["sunday"][0]), sorted(sa.AUDIT_ORDER))

    def test_slots_outside_those_attempts_fit_the_ceiling(self):
        for day, audits in sa.SLOT_PLAN.items():
            needed = sum(sa.DEFAULT_COSTS[a] for a in audits)
            if needed <= sa.DEFAULT_BUDGET:
                self.assertIn(sa.SLOT_NAMES[day],
                              ("monday", "tuesday", "thursday", "friday"),
                              "slot %s fits; is it scheduled as designed?" % sa.SLOT_NAMES[day])

    def test_the_runner_still_never_plans_more_than_the_ceiling(self):
        costs = sa.expected_costs()
        planned, skipped, _ = sa.plan_run(list(sa.AUDIT_ORDER), costs, sa.DEFAULT_BUDGET - sa.DEFAULT_RESERVE)
        self.assertLessEqual(sum(costs[a] for a in planned), sa.DEFAULT_BUDGET - sa.DEFAULT_RESERVE)
        self.assertIn("audit_provenance", [s["audit"] for s in skipped])


class VerdictTests(unittest.TestCase):
    def test_a_report_this_run_did_not_write_is_never_a_verdict(self):
        self.assertEqual(sa.verdict_for("audit_kind", 0, {"complete": True}, None)[0], sa.ERROR)
        self.assertEqual(sa.verdict_for("audit_kind", 0, {"complete": True}, False)[0], sa.ERROR)

    def test_audit_kind(self):
        self.assertEqual(sa.verdict_for("audit_kind", 0, {"complete": True, "checkedEntries": 145,
                                                          "totalEntries": 145, "disagreements": [],
                                                          "unresolved": []}, True)[0], sa.PASS)
        self.assertEqual(sa.verdict_for("audit_kind", 1, {"complete": True,
                                                          "disagreements": [{"repo": "X"}]}, True)[0],
                         sa.FINDINGS)
        self.assertEqual(sa.verdict_for("audit_kind", 0, {"complete": False,
                                                          "unresolved": [{"status": 500}]}, True)[0],
                         sa.INCOMPLETE)

    def test_audit_descriptions(self):
        self.assertEqual(sa.verdict_for("audit_descriptions", 0, {"complete": True,
                                                                  "unresolved": []}, True)[0], sa.PASS)
        self.assertEqual(sa.verdict_for("audit_descriptions", 1, {"complete": True,
                                                                  "unresolved": [{"repo": "X"}]}, True)[0],
                         sa.FINDINGS)
        self.assertEqual(sa.verdict_for("audit_descriptions", 2, {"complete": False,
                                                                  "apiErrors": [{"status": 403}]}, True)[0],
                         sa.INCOMPLETE)

    def test_verify_live(self):
        self.assertEqual(sa.verdict_for("verify_live", 0, {"status": "complete", "complete": True,
                                                           "hardMismatchCount": 0, "driftCount": 48},
                                        True)[0], sa.PASS)
        self.assertEqual(sa.verdict_for("verify_live", 1, {"complete": True, "hardMismatchCount": 3,
                                                           "status": "complete_with_mismatches"}, True)[0],
                         sa.FINDINGS)
        self.assertEqual(sa.verdict_for("verify_live", 2, {"complete": False}, True)[0], sa.INCOMPLETE)

    def test_audit_provenance(self):
        self.assertEqual(sa.verdict_for("audit_provenance", 0, {"complete": True, "accessBlocked": False,
                                                                 "findings": [], "entriesAudited": 145,
                                                                 "entriesTotal": 145}, True)[0], sa.PASS)
        self.assertEqual(sa.verdict_for("audit_provenance", 0, {"complete": True,
                                                                "findings": [{"citation": "x"}]}, True)[0],
                         sa.FINDINGS)
        self.assertEqual(sa.verdict_for("audit_provenance", 0, {"complete": False,
                                                                "accessBlocked": True,
                                                                "accessBlockReason": "HTTP 403 rate limit"},
                                        True)[0], sa.INCOMPLETE)

    def test_access_block_reason_prefers_the_tool_own_report(self):
        self.assertEqual(sa.access_block_reason({"accessBlocked": True,
                                                 "accessBlockReason": "HTTP 403 rate limit"}, 0, ""),
                         "HTTP 403 rate limit")
        reason = sa.access_block_reason({"apiErrors": [{"status": 401, "message": "Bad credentials"}]}, 2, "")
        self.assertIn("401", reason)
        self.assertIn("rate limit", sa.access_block_reason(None, 0, "line\nHTTP 403 rate limit exceeded"))
        self.assertTrue(sa.access_block_reason({"complete": False}, 2, "no hint here"))


class OutcomeTests(unittest.TestCase):
    def test_a_complete_clean_slot_is_clean(self):
        self.assertEqual(sa.overall_outcome([result(n, sa.PASS) for n in sa.AUDIT_ORDER]),
                         (sa.CLEAN, sa.EXIT_CLEAN))
        self.assertEqual(sa.overall_outcome([result(sa.AUDIT_ORDER[0], sa.PASS),
                                             result(sa.AUDIT_ORDER[1], sa.PASS)]),
                         (sa.CLEAN, sa.EXIT_CLEAN))

    def test_a_skipped_audit_is_partial_and_never_clean(self):
        outcome, code = sa.overall_outcome([result(sa.AUDIT_ORDER[0], sa.PASS),
                                            result(sa.AUDIT_ORDER[1], sa.NOT_RUN)])
        self.assertEqual((outcome, code), (sa.OUT_PARTIAL, sa.EXIT_PARTIAL))
        self.assertNotEqual(code, 0)

    def test_incomplete_dominates_findings_which_dominate_partial(self):
        self.assertEqual(sa.overall_outcome([result(sa.AUDIT_ORDER[0], sa.PASS),
                                             result(sa.AUDIT_ORDER[1], sa.INCOMPLETE)])[0], "INCOMPLETE")
        self.assertEqual(sa.overall_outcome([result(sa.AUDIT_ORDER[0], sa.PASS),
                                             result(sa.AUDIT_ORDER[1], sa.FINDINGS)])[0], "FINDINGS")
        self.assertEqual(sa.overall_outcome([result(sa.AUDIT_ORDER[0], sa.FINDINGS),
                                             result(sa.AUDIT_ORDER[1], sa.INCOMPLETE)])[0], "INCOMPLETE")

    def test_error_is_never_clean(self):
        self.assertEqual(sa.overall_outcome([result(sa.AUDIT_ORDER[0], sa.PASS),
                                             result(sa.AUDIT_ORDER[1], sa.ERROR)])[0], "INCOMPLETE")

    def test_an_empty_run_is_not_clean(self):
        self.assertEqual(sa.overall_outcome([])[0], sa.OUT_PARTIAL)


class SelfTestTests(unittest.TestCase):
    def test_self_test_passes(self):
        self.assertEqual(sa.self_test(), [])

    def test_main_self_test_exits_zero(self):
        self.assertEqual(sa.main(["--self-test"]), 0)

    def test_unknown_audit_is_rejected_without_running_anything(self):
        self.assertEqual(sa.main(["--audits", "not_an_audit"]), sa.EXIT_INCOMPLETE)


class ResultsAssemblyTests(unittest.TestCase):
    """A real 2026-10-11 run reported an access block as a budget skip.

    `audit_kind` and `audit_descriptions` both returned INCOMPLETE (HTTP 403) and
    were missing from `report.md` / `report.json`, because the planned audits
    were never appended to the result list: the run reported `PARTIAL` (exit 3)
    instead of `INCOMPLETE` (exit 2) and showed no evidence that two audits had
    run at all. These cases pin the assembly so it cannot regress.
    """

    def skipped_item(self, name, needed=812, left=405):
        return {"audit": name, "needed": needed, "remainingBeforeSkip": left}

    def test_an_audit_that_ran_survives_a_budget_skip(self):
        ran = [result(sa.AUDIT_ORDER[0], sa.INCOMPLETE, "HTTP 403")]
        combined = sa.combined_results(ran, [self.skipped_item(sa.AUDIT_ORDER[2])])
        self.assertEqual([r["audit"] for r in combined],
                         [sa.AUDIT_ORDER[0], sa.AUDIT_ORDER[2]])
        self.assertEqual(combined[0]["verdict"], sa.INCOMPLETE)
        self.assertEqual(combined[1]["verdict"], sa.NOT_RUN)

    def test_a_skip_row_still_carries_what_a_reviewer_needs(self):
        combined = sa.combined_results([], [self.skipped_item(sa.AUDIT_ORDER[1], 812, 405)])
        row = combined[0]
        self.assertEqual(row["needed"], 812)
        self.assertEqual(row["remainingBeforeSkip"], 405)
        self.assertIn("812", row["reason"])
        self.assertEqual(row["toolReport"], sa.AUDITS[sa.AUDIT_ORDER[1]]["report"])
        self.assertEqual(row["reviewEndpoint"], sa.AUDITS[sa.AUDIT_ORDER[1]]["review"])

    def test_an_access_block_plus_a_skip_is_incomplete_not_partial(self):
        ran = [result(sa.AUDIT_ORDER[0], sa.INCOMPLETE, "capability gap")]
        combined = sa.combined_results(ran, [self.skipped_item(sa.AUDIT_ORDER[2])])
        outcome, code = sa.overall_outcome(combined)
        self.assertEqual(outcome, sa.INCOMPLETE)
        self.assertEqual(code, sa.EXIT_INCOMPLETE)

    def test_every_requested_audit_reaches_the_report_exactly_once(self):
        for day, audits in sa.SLOT_PLAN.items():
            for usable in (0, 435, 840, 100000):
                planned, skipped, _ = sa.plan_run(audits, sa.DEFAULT_COSTS, usable)
                ran = [result(a, sa.PASS) for a in planned]
                names = [r["audit"] for r in sa.combined_results(ran, skipped)]
                self.assertEqual(sorted(names), sorted(audits),
                                 "slot %s at usable %s lost or duplicated an audit"
                                 % (sa.SLOT_NAMES[day], usable))
                self.assertEqual(len(names), len(set(names)))

    def test_the_runner_loop_keeps_every_audit_it_ran(self):
        """Source guard for the exact 2026-10-11 defect: the planned loop ran
        `audit_kind` and `audit_descriptions`, printed both verdicts, and never
        appended them, so the report could not show them."""
        src = open(os.path.join(ROOT, "tools", "scheduled_audit.py"), encoding="utf-8").read()
        self.assertIn("ran = []", src)
        self.assertIn("ran.append(result)", src)
        self.assertIn("results = combined_results(ran, skipped)", src)
        self.assertIn("refusing to publish a report with a", src)
        loop = src[src.index("ran = []"):src.index("results = combined_results(ran, skipped)")]
        self.assertIn("ran.append(result)", loop)

    def test_the_report_names_the_audits_that_ran(self):
        ran = [result(sa.AUDIT_ORDER[0], sa.INCOMPLETE, "HTTP 403 access block")]
        combined = sa.combined_results(ran, [self.skipped_item(sa.AUDIT_ORDER[2])])
        run = {"finishedAt": sa.utc_now(), "outcome": sa.INCOMPLETE,
               "exitCode": sa.EXIT_INCOMPLETE, "slot": "sunday", "revision": "abc1234",
               "runUrl": "https://example.invalid/run", "snapshot": "2026-10-11T15:06:10Z",
               "budget": 900, "reserve": 60, "usable": 840}
        quota = {"ok": True, "body": {"limit": 1000, "remaining": 1000, "reset": 1},
                 "headers": {"limit": 1000, "remaining": 1000}, "effectiveRemaining": 1000}
        md = sa.render_report(run, combined, quota, [sa.AUDIT_ORDER[0]])
        self.assertIn("1 of the 4 audits", md)
        self.assertIn(sa.AUDIT_ORDER[0], md)
        self.assertIn("HTTP 403 access block", md)


class ReportTests(unittest.TestCase):
    def build(self):
        not_run = result(sa.AUDIT_ORDER[1], sa.NOT_RUN, "not run: needs ~812 requests, budget left 405")
        not_run.update({"needed": 812, "remainingBeforeSkip": 405})
        results = [result(sa.AUDIT_ORDER[0], sa.PASS, "clean"), not_run]
        run = {"finishedAt": sa.utc_now(), "outcome": sa.OUT_PARTIAL, "exitCode": sa.EXIT_PARTIAL,
               "slot": "monday", "revision": "abc1234", "runUrl": "https://example.invalid/run",
               "snapshot": "2026-10-11T15:06:10Z", "budget": 900, "reserve": 60, "usable": 840}
        quota = {"ok": True, "body": {"limit": 1000, "remaining": 1000, "reset": 1},
                 "headers": {"limit": 1000, "remaining": 1000}, "effectiveRemaining": 1000}
        return run, results, quota

    def test_report_names_every_audit_including_the_ones_that_did_not_run(self):
        run, results, quota = self.build()
        text = sa.render_report(run, results, quota, [sa.AUDIT_ORDER[0]])
        self.assertIn("`PARTIAL`", text)
        self.assertIn("`%s`" % sa.AUDIT_ORDER[0], text)
        self.assertIn("`%s`" % sa.AUDIT_ORDER[1], text)
        self.assertIn(sa.AUDITS[sa.AUDIT_ORDER[0]]["review"], text)

    def test_report_states_its_coverage_and_what_did_not_run(self):
        run, results, quota = self.build()
        text = sa.render_report(run, results, quota, [sa.AUDIT_ORDER[0]])
        self.assertIn("Coverage this run", text)
        self.assertIn("Not run in this run (budget)", text)
        self.assertIn("not reported as checked", text.replace("**", ""))
        self.assertIn("1,000 requests/hour/repository", text)

    def test_report_states_the_budget_arithmetic_and_the_documented_cap(self):
        run, results, quota = self.build()
        text = sa.render_report(run, results, quota, [sa.AUDIT_ORDER[0]])
        self.assertIn("900", text)
        self.assertIn("rate-limits-for-the-rest-api", text)

    def test_report_does_not_overclaim(self):
        run, results, quota = self.build()
        text = sa.render_report(run, results, quota, [sa.AUDIT_ORDER[0]]).lower()
        for overclaim in ("zero hallucinations", "guaranteed", "site uptime is", "exhaustively verified",
                          "all sites are up"):
            self.assertNotIn(overclaim, text)

    def test_unreadable_quota_is_stated_not_hidden(self):
        run, results, _ = self.build()
        text = sa.render_report(run, results, {"ok": False, "status": 403, "reason": "rate limit"}, [])
        self.assertIn("could not be read", text)
        self.assertIn("hard ceiling", text)

    def test_caveat_never_promises_accuracy_or_usage(self):
        self.assertIn("do not prove", sa.CAVEAT)
        self.assertIn("usage claim", sa.CAVEAT)


class RepositoryInvariantTests(unittest.TestCase):
    """The scheduled runner must never become a publisher."""

    def source(self):
        with open(os.path.join(ROOT, "tools", "scheduled_audit.py"), encoding="utf-8") as fh:
            return fh.read()

    def test_every_write_mode_open_targets_the_runners_own_output(self):
        published = ("data/sites.js", "VERIFICATION.md", "README.md", "SITES.md", "TASKS.md",
                     "FLAGGED.md", "HANDOFF.md", "data/sites/")
        calls = re.findall(r"open\(([^)]*)\)", self.source())
        write_calls = [c for c in calls if re.search(r'["\'](w|a|w\+|a\+|x)["\']', c)]
        self.assertTrue(write_calls, "expected the runner to write its own report")
        for call in write_calls:
            for name in published:
                self.assertNotIn(name, call, "runner must never write a published file: %s" % call)
        self.assertNotIn("git push", self.source())

    def test_runner_only_invokes_the_registered_audits(self):
        src = self.source()
        for name in sa.AUDIT_ORDER:
            self.assertIn(sa.AUDITS[name]["script"][0], src)

    def test_every_registered_audit_has_a_report_and_a_review_endpoint(self):
        for name, spec in sa.AUDITS.items():
            self.assertTrue(spec["report"].endswith(".json"), name)
            self.assertTrue(spec["review"].startswith("https://api.github.com/"), name)


class WorkflowTests(unittest.TestCase):
    PATH = os.path.join(ROOT, ".github", "workflows", "audit-schedule.yml")

    def setUp(self):
        if not os.path.exists(self.PATH):
            self.skipTest("workflow not added yet")
        with open(self.PATH, encoding="utf-8") as fh:
            self.text = fh.read()

    def test_workflow_is_scheduled_and_runs_the_runner(self):
        self.assertIn("cron:", self.text)
        self.assertIn("tools/scheduled_audit.py", self.text)

    def test_workflow_is_read_only_and_never_pushes(self):
        self.assertIn("contents: read", self.text)
        self.assertNotIn("contents: write", self.text)
        self.assertNotIn("git push", self.text)
        # A real trigger key, not the word in a comment warning about it.
        self.assertIsNone(re.search(r"^\s*pull_request_target\s*:", self.text, re.M))

    def test_workflow_publishes_a_verdict_where_a_human_will_see_it(self):
        self.assertIn("issues: write", self.text)
        self.assertIn("GITHUB_STEP_SUMMARY", self.text)
        self.assertIn("report.json", self.text)


if __name__ == "__main__":
    unittest.main()
