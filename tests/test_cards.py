import json
from pathlib import Path
import unittest

from storelab.cards import render_return_window


class PolicyCardTests(unittest.TestCase):
    def test_real_saved_policy_evidence_does_not_gain_a_start_date(self):
        path = Path(__file__).resolve().parent.parent / "results/claude-followup-02/followup-price_and_policy-bounded-r0.json"
        trace = json.loads(path.read_text())
        evidence = next(e for t in trace["tool_trace"] for e in t["result"]["evidence"]
                        if e["source"] == "policy")
        text = render_return_window(evidence)
        self.assertEqual(text, "The policy lists a 7-day return window. "
                         "The retrieved details do not specify when that period begins.")
        self.assertNotIn("purchase", text)
        self.assertNotIn("delivery", text)

    def test_supported_start_is_rendered_without_changing_it(self):
        for start in ("purchase", "delivery"):
            evidence = {"source": "policy", "facts": {
                "returns_days": "14", "returns_start_event": start}}
            self.assertEqual(render_return_window(evidence),
                             f"The policy lists a 14-day return window from {start}.")

    def test_missing_invalid_and_unrecognised_fields_do_not_get_guessed(self):
        for days in (None, 7, "7 days", "0", "-1", "7; from purchase"):
            self.assertEqual(render_return_window({"source": "policy", "facts": {
                "returns_days": days}}), "I could not verify the return window.")
        self.assertEqual(render_return_window({"source": "historical_copy", "facts": {
            "returns_days": "7"}}), "I could not verify the return window.")
        text = render_return_window({"source": "policy", "facts": {
            "returns_days": "7", "returns_start_event": "unknown_event"}})
        self.assertIn("do not specify", text)


if __name__ == "__main__":
    unittest.main()
