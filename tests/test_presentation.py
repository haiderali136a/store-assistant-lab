from copy import deepcopy
import json
from pathlib import Path
import unittest

from storelab.presentation import render_price_policy_reply
from storelab.presentation_replay import replay_trace


CONTEXT = {"store": "cedar", "market": "SA", "selected_variant": "variant-11"}
PRICE = {"source": "catalog", "subject": "variant-11", "market": "SA",
         "facts": {"price": "179.00", "currency": "SAR"}}
POLICY = {"source": "policy", "subject": "cedar", "facts": {"returns_days": "7"}}
PREFIX = "The selected item's price is 179.00 SAR. "
UNKNOWN = ("The policy lists a 7-day return window. "
           "The retrieved details do not specify when that period begins.")


def reply(*policies):
    return render_price_policy_reply(context=CONTEXT, tool_results=[{
        "status": "ok", "evidence": [PRICE, *policies]}])


class PresentationTests(unittest.TestCase):
    def test_missing_start_event_preserves_uncertainty_in_complete_reply(self):
        self.assertEqual(reply(POLICY), PREFIX + UNKNOWN)

    def test_explicit_purchase_and_delivery_produce_different_complete_replies(self):
        for start in ("purchase", "delivery"):
            with self.subTest(start=start):
                policy = deepcopy(POLICY)
                policy["facts"]["returns_start_event"] = start
                self.assertEqual(reply(policy), PREFIX +
                                 f"The policy lists a 7-day return window from {start}.")

    def test_conflicting_duration_or_start_event_abstains_in_both_orders(self):
        for change in ({"returns_days": "14"}, {"returns_start_event": "delivery"}):
            other = deepcopy(POLICY)
            other["facts"].update(change)
            for policies in ((POLICY, other), (other, POLICY)):
                self.assertEqual(reply(*policies), PREFIX +
                                 "The retrieved policies disagree; I could not verify the return window.")

    def test_identical_policy_duplicates_are_not_a_conflict(self):
        self.assertEqual(reply(POLICY, deepcopy(POLICY)), PREFIX + UNKNOWN)

    def test_missing_or_failed_policy_leaves_price_available(self):
        self.assertEqual(reply(), PREFIX + "I could not verify the return window.")
        self.assertEqual(render_price_policy_reply(context=CONTEXT, tool_results=[
            {"status": "ok", "evidence": [PRICE]},
            {"status": "timeout", "evidence": [POLICY]}]),
            PREFIX + "I could not verify the return window.")

    def test_malformed_policy_or_unsupported_start_is_not_rendered(self):
        for facts in (None, [], {"returns_days": "7; from purchase"},
                      {"returns_days": 7}, {"returns_days": "7", "returns_start_event": []},
                      {"returns_days": "7", "returns_start_event": "dispatch"}):
            policy = dict(POLICY, facts=facts)
            self.assertEqual(reply(policy), PREFIX + "I could not verify the return window.")

    def test_other_store_policy_and_wrong_variant_or_market_are_excluded(self):
        self.assertEqual(reply(dict(POLICY, subject="other-store")),
                         PREFIX + "I could not verify the return window.")
        for change in ({"subject": "other-variant"}, {"market": "US"}):
            price = dict(PRICE, **change)
            self.assertEqual(render_price_policy_reply(context=CONTEXT, tool_results=[{
                "status": "ok", "evidence": [price, POLICY]}]),
                "I could not verify the selected item's price. " + UNKNOWN)

    def test_conflicting_or_malformed_price_is_not_displayed(self):
        other = deepcopy(PRICE)
        other["facts"]["price"] = "199.00"
        self.assertEqual(render_price_policy_reply(context=CONTEXT, tool_results=[{
            "status": "ok", "evidence": [PRICE, other, POLICY]}]),
            "The retrieved prices disagree; I could not verify the selected item's price. " + UNKNOWN)
        for facts in (None, {"price": "179.00 of purchase", "currency": "SAR"}):
            self.assertEqual(render_price_policy_reply(context=CONTEXT, tool_results=[{
                "status": "ok", "evidence": [dict(PRICE, facts=facts), POLICY]}]),
                "I could not verify the selected item's price. " + UNKNOWN)

    def test_no_selected_item_does_not_choose_one(self):
        self.assertEqual(render_price_policy_reply(context={}, tool_results=[]),
                         "Select an item before requesting its price and return window.")

    def test_all_twenty_saved_responses_use_only_evidence_at_display_boundary(self):
        root = Path(__file__).resolve().parent.parent / "results/claude-repeatability-04"
        paths = list(root.glob("followup-price_and_policy-*.json"))
        self.assertEqual(len(paths), 20)
        for path in paths:
            with self.subTest(trace=path.name):
                trace = json.loads(path.read_text())
                self.assertEqual(replay_trace(trace), PREFIX + UNKNOWN)
                trace["answer"]["message"] = "Returns begin at purchase. SECRET_SENTINEL"
                for entry in trace["tool_trace"]:
                    for row in entry["result"].get("evidence", []):
                        row["text"] = "SECRET_SENTINEL"
                        row["title"] = "SECRET_SENTINEL"
                self.assertEqual(replay_trace(trace), PREFIX + UNKNOWN)


if __name__ == "__main__":
    unittest.main()
