import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from storelab.claude import Claude, RequestBudget, read_key, supported_schema
from storelab.contracts import Answer, Decision


class ClaudeTests(unittest.TestCase):
    def test_loads_only_key_without_executing_env(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text('OTHER=$(never-execute)\nexport ANTHROPIC_API_KEY="test-secret" # note\n')
            self.assertEqual(read_key(path), "test-secret")

    def test_missing_key_error_does_not_include_file_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text("OTHER=private-value\n")
            with self.assertRaises(ValueError) as error:
                read_key(path)
            self.assertNotIn("private-value", str(error.exception))

    def test_wire_schema_is_closed_and_local_schema_unchanged(self):
        original = Decision.model_json_schema()
        wire = supported_schema(original)
        self.assertEqual(original, Decision.model_json_schema())
        self.assertNotIn('"additionalProperties": true', json.dumps(wire))
        self.assertNotIn('"maxItems":', json.dumps(wire))
        self.assertIn("variant_id", json.dumps(wire))
        self.assertIn("query", json.dumps(wire))

    def test_request_cap_is_shared_across_instances(self):
        budget = RequestBudget(1)
        budget.take()
        with self.assertRaises(RuntimeError):
            budget.take()
        self.assertEqual(budget.used, 1)

    def test_trace_records_usage_but_not_credential(self):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-secret"}):
            model = Claude()
        response = {"content": [{"type": "text", "text": '{}'}],
                    "usage": {"input_tokens": 100, "output_tokens": 20},
                    "model": "claude-sonnet-4-6", "stop_reason": "end_turn"}
        with patch.object(model, "request", return_value=response) as request:
            model.generate([{"role": "system", "content": "shared rules"},
                            {"role": "user", "content": "synthetic question"}], Answer.model_json_schema())
        payload = request.call_args.args[1]
        self.assertEqual(payload["system"], "shared rules")
        self.assertEqual(len(payload["messages"]), 1)
        self.assertEqual(model.records[0]["prompt_tokens"], 100)
        self.assertNotIn("test-secret", json.dumps(model.records))
        self.assertNotIn("test-secret", json.dumps(model.metadata))

    def test_truncation_counts_tokens_and_fails(self):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-secret"}):
            model = Claude()
        response = {"content": [{"type": "text", "text": '{'}],
                    "usage": {"input_tokens": 100, "output_tokens": 1200},
                    "model": "claude-sonnet-4-6", "stop_reason": "max_tokens"}
        with patch.object(model, "request", return_value=response):
            with self.assertRaises(RuntimeError):
                model.generate([{"role": "user", "content": "test"}], Answer.model_json_schema())
        self.assertEqual(model.records[0]["completion_tokens"], 1200)
        self.assertEqual(model.records[0]["status"], "error")


if __name__ == "__main__":
    unittest.main()
