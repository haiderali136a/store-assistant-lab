from copy import deepcopy
import unittest

from storelab.contracts import ToolCall
from storelab.evaluation import assess
from storelab.fixtures import followup_scenarios, input_for_model
from storelab.models import Scripted
from storelab.tools import StoreTools
from storelab.workflows import run_case


def case(name):
    return next(c for c in followup_scenarios() if c["family"] == name)


SEARCH = {"tool_calls": [{"name": "search_catalog", "arguments": {
    "query": "Drift Tee", "color": "blue"}}], "answer": None}


class FollowupTests(unittest.TestCase):
    def test_distinct_prices_are_scoped_to_variant_and_case(self):
        c = case("different_prices")
        tools = StoreTools(c["context"], c["world"])
        rows = tools.batch([ToolCall.model_validate(SEARCH["tool_calls"][0])])[0]["result"]["evidence"]
        self.assertEqual([(r["subject"], r["facts"]["price"]) for r in rows],
                         [("variant-11", "179.00"), ("variant-12", "199.00")])
        other = StoreTools(c["context"], {})
        rows = other.batch([ToolCall.model_validate(SEARCH["tool_calls"][0])])[0]["result"]["evidence"]
        self.assertEqual({r["facts"]["price"] for r in rows}, {"179.00"})

    def test_labelled_candidate_prices_pass_but_missing_options_fail(self):
        c = case("different_prices")
        value = {"status": "clarify", "message": "Blue M is 179 SAR and blue L is 199 SAR. Which size?",
                 "claims": []}
        for i, size, price in ((0, "M", "179.00"), (1, "L", "199.00")):
            for field, val in {"price": price, "currency": "SAR", "size": size, "color": "blue"}.items():
                value["claims"].append({"subject": f"variant-1{i+1}", "field": field,
                                        "value": val, "evidence_id": f"e1-{i}"})
        run = run_case(c, "bounded", Scripted([SEARCH, value]))
        self.assertTrue(assess(c, run)["structured_pass"])
        incomplete = deepcopy(run)
        incomplete["answer"]["claims"] = [x for x in value["claims"] if x["field"] != "size"]
        self.assertIn("candidate_price_missing_options_or_currency", assess(c, incomplete)["reasons"])
        wrong = deepcopy(run)
        wrong["answer"]["claims"][0]["value"] = "199.00"
        self.assertIn("unsupported_claims", assess(c, wrong)["reasons"])

    def test_retired_id_missing_but_customer_requested_match_exists(self):
        c = case("retired_reference")
        tools = StoreTools(c["context"], c["world"])
        missing = tools.batch([ToolCall(name="get_variant", arguments={
            "variant_id": c["context"]["selected_variant"]})])[0]
        self.assertEqual(missing["result"]["status"], "not_found")
        match = tools.batch([ToolCall(name="search_catalog", arguments={
            "query": "Drift Tee", "color": "blue", "size": "M"})])[0]
        self.assertEqual([e["subject"] for e in match["result"]["evidence"]], ["variant-11"])

    def test_suite_does_not_leak_updated_oracle(self):
        cases = followup_scenarios()
        self.assertEqual(len(cases), 6)
        self.assertEqual(len({c["id"] for c in cases}), 6)
        for c in cases:
            self.assertEqual(set(input_for_model(c)), {"context", "query", "history"})


if __name__ == "__main__":
    unittest.main()
