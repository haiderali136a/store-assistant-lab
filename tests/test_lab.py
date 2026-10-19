from copy import deepcopy
import json
import unittest

from pydantic import ValidationError

from storelab.contracts import Decision, ToolCall
from storelab.evaluation import assess, evidence_gate
from storelab.fixtures import input_for_model, scenarios
from storelab.models import Scripted
from storelab.tools import StoreTools
from storelab.workflows import run_case


def case(name="cedar-known"):
    return next(c for c in scenarios() if c["id"] == name)


def lookup(variant="variant-11"):
    return {"tool_calls": [{"name": "get_variant", "arguments": {"variant_id": variant}}], "answer": None}


def answer(price="179.00", currency="SAR", subject="variant-11", evidence="e1-0"):
    return {"status": "answered", "message": f"The selected item costs {price} {currency}.",
            "claims": [{"subject": subject, "field": "price", "value": price, "evidence_id": evidence},
                       {"subject": subject, "field": "currency", "value": currency, "evidence_id": evidence}]}


def final(value):
    return {"tool_calls": [], "answer": value}


class LabTests(unittest.TestCase):
    def test_both_paths_can_answer_in_two_calls(self):
        for architecture in ("bounded", "tool_loop"):
            with self.subTest(architecture=architecture):
                value = answer()
                outputs = [lookup(), value if architecture == "bounded" else final(value)]
                run = run_case(case(), architecture, Scripted(outputs))
                self.assertEqual(run["model_calls"], 2)
                self.assertTrue(assess(case(), run)["structured_pass"])

    def test_bounded_model_can_clarify_without_tools(self):
        value = {"status": "clarify", "message": "Which size do you want?", "claims": []}
        run = run_case(case("cedar-ambiguous"), "bounded", Scripted([final(value)]))
        self.assertEqual(run["model_calls"], 1)
        self.assertEqual(run["tool_calls"], 0)

    def test_agent_can_recover_from_a_failed_search(self):
        search = {"tool_calls": [{"name": "search_catalog", "arguments": {"query": "unknown"}}], "answer": None}
        run = run_case(case(), "tool_loop", Scripted([search, lookup(), final(answer(evidence="e2-0"))]))
        self.assertEqual(run["model_calls"], 3)
        self.assertTrue(assess(case(), run)["structured_pass"])

    def test_model_loop_budget_is_enforced(self):
        run = run_case(case(), "tool_loop", Scripted([lookup()] * 10))
        self.assertEqual(run["model_calls"], 6)
        self.assertEqual(run["error"], "model_call_budget_exhausted")

    def test_tool_budget_is_enforced(self):
        batch = {"tool_calls": lookup()["tool_calls"] * 4, "answer": None}
        run = run_case(case(), "tool_loop", Scripted([batch] * 10))
        self.assertEqual(run["tool_calls"], 12)
        self.assertEqual(run["error"], "tool_budget_exhausted")

    def test_wrong_store_variant_is_not_returned(self):
        tools = StoreTools(case()["context"], {})
        record = tools.batch([ToolCall.model_validate(lookup("variant-21")["tool_calls"][0])])[0]
        self.assertEqual(record["result"]["status"], "not_found")
        self.assertEqual(record["result"]["evidence"], [])

    def test_scope_override_is_rejected(self):
        tools = StoreTools(case()["context"], {})
        record = tools.batch([ToolCall(name="get_variant", arguments={"variant_id": "variant-21", "store": "harbor"})])[0]
        self.assertEqual(record["result"]["status"], "invalid_arguments")

    def test_market_override_is_rejected(self):
        tools = StoreTools(case()["context"], {})
        record = tools.batch([ToolCall(name="get_variant", arguments={"variant_id": "variant-11", "market": "AE"})])[0]
        self.assertEqual(record["result"]["status"], "invalid_arguments")

    def test_market_currency_comes_from_request_context(self):
        c = case("cedar-market")
        run = run_case(c, "bounded", Scripted([lookup(), answer("169.00", "AED")]))
        self.assertTrue(assess(c, run)["structured_pass"])

    def test_changed_price_is_not_taken_from_history(self):
        c = case("cedar-changed")
        run = run_case(c, "bounded", Scripted([lookup(), answer("219.00")]))
        self.assertTrue(assess(c, run)["structured_pass"])
        wrong = deepcopy(run)
        wrong["answer"] = answer()
        self.assertFalse(assess(c, wrong)["structured_pass"])

    def test_timeout_does_not_expose_catalog_facts(self):
        c = case("cedar-timeout")
        value = {"status": "unavailable", "message": "I cannot verify the current price.", "claims": []}
        run = run_case(c, "bounded", Scripted([lookup(), value]))
        self.assertEqual(run["tool_trace"][0]["result"]["evidence"], [])
        self.assertTrue(assess(c, run)["structured_pass"])

    def test_guessed_correct_price_without_evidence_fails(self):
        run = run_case(case(), "bounded", Scripted([final(answer())]))
        self.assertIn("unsupported_claims", assess(case(), run)["reasons"])

    def test_abstaining_from_everything_is_not_success(self):
        value = {"status": "unavailable", "message": "I cannot help.", "claims": []}
        run = run_case(case(), "bounded", Scripted([final(value)]))
        self.assertFalse(assess(case(), run)["structured_pass"])

    def test_wrong_evidence_id_fails_even_with_correct_value(self):
        run = run_case(case(), "bounded", Scripted([lookup(), answer(evidence="invented")]))
        self.assertFalse(assess(case(), run)["structured_pass"])
        self.assertEqual(evidence_gate(run)["status"], "unavailable")

    def test_syntactically_valid_but_empty_decision_is_rejected(self):
        with self.assertRaises(ValidationError):
            Decision.model_validate({"tool_calls": [], "answer": None})

    def test_malformed_output_counts_as_a_model_call(self):
        run = run_case(case(), "bounded", Scripted(["not json"]))
        self.assertEqual(run["model_calls"], 1)
        self.assertIsNotNone(run["error"])

    def test_provider_failure_counts_as_an_attempt(self):
        run = run_case(case(), "bounded", Scripted([TimeoutError("model timeout")]))
        self.assertEqual(run["model_calls"], 1)
        self.assertIsNotNone(run["error"])

    def test_parallel_tools_do_not_add_model_calls(self):
        both = lookup()
        both["tool_calls"].append({"name": "search_documents", "arguments": {"query": "returns"}})
        value = answer()
        value["claims"].append({"subject": "cedar", "field": "returns_days", "value": "7", "evidence_id": "e2-policy"})
        run = run_case(case("cedar-mixed"), "bounded", Scripted([both, value]))
        self.assertEqual((run["model_calls"], run["tool_calls"]), (2, 2))
        self.assertTrue(assess(case("cedar-mixed"), run)["structured_pass"])

    def test_oracle_and_fault_controls_are_not_model_input(self):
        for c in scenarios():
            payload = input_for_model(c)
            self.assertEqual(set(payload), {"context", "query", "history"})
            self.assertNotIn("required_claims", json.dumps(payload))

    def test_fixture_count_unique_and_cross_store_prices_differ(self):
        cases = scenarios()
        self.assertEqual(len(cases), 30)
        self.assertEqual(len({c["id"] for c in cases}), 30)
        prices = [case(s + "-known")["expected"]["required_claims"][0][2]
                  for s in ("cedar", "harbor", "dune")]
        self.assertEqual(len(set(prices)), 3)

    def test_evaluator_does_not_claim_prose_validation(self):
        value = answer()
        value["message"] = "Incorrect prose can disagree with otherwise correct fields."
        run = run_case(case(), "bounded", Scripted([lookup(), value]))
        self.assertTrue(assess(case(), run)["human_review_required"])

    def test_gate_does_not_hide_provider_failure(self):
        c = case("cedar-timeout")
        run = run_case(c, "bounded", Scripted([TimeoutError("provider failed")]))
        run["answer"] = evidence_gate(run)
        self.assertFalse(assess(c, run)["structured_pass"])

    def test_unknown_product_has_no_price_evidence(self):
        tools = StoreTools(case()["context"], {})
        record = tools.batch([ToolCall(name="search_catalog", arguments={"query": "Unknown Jacket"})])[0]
        self.assertEqual(record["result"], {"status": "not_found", "evidence": []})

    def test_available_for_sale_does_not_imply_physical_stock(self):
        tools = StoreTools(case()["context"], {})
        tools.store["variants"][0]["currently_not_in_stock"] = True
        record = tools.batch([ToolCall.model_validate(lookup()["tool_calls"][0])])[0]
        facts = record["result"]["evidence"][0]["facts"]
        self.assertEqual(facts["available_for_sale"], "true")
        self.assertEqual(facts["currently_not_in_stock"], "true")

    def test_ambiguous_selection_cannot_pass_with_candidate_price(self):
        c = case("cedar-ambiguous")
        calls = {"tool_calls": [{"name": "search_catalog", "arguments": {"query": "Drift Tee", "color": "blue"}}], "answer": None}
        value = answer()
        value["status"] = "clarify"
        run = run_case(c, "bounded", Scripted([calls, value]))
        self.assertIn("premature_price_claim", assess(c, run)["reasons"])


if __name__ == "__main__":
    unittest.main()
