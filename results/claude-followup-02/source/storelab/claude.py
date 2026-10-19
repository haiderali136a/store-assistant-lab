"""Anthropic Messages adapter. Loads one credential, never the entire environment file."""
from copy import deepcopy
import json
import os
from pathlib import Path
import re
from time import perf_counter
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from .contracts import TOOL_ARGUMENTS


def read_key(env_file=None):
    if env_file is None:
        value = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    else:
        value = ""
        for line in Path(env_file).read_text().splitlines():
            match = re.match(r"^\s*(?:export\s+)?ANTHROPIC_API_KEY\s*=\s*(.*)$", line)
            if match:
                raw = match[1].strip()
                if raw.startswith(("'", '"')):
                    quote = raw[0]
                    end = raw.find(quote, 1)
                    if end < 0 or (raw[end + 1:].strip() and not raw[end + 1:].strip().startswith("#")):
                        raise ValueError("Invalid quoted ANTHROPIC_API_KEY entry")
                    value = raw[1:end]
                else:
                    value = raw.split(" #", 1)[0].strip()
    if not value or any(c.isspace() for c in value) or "$" in value:
        raise ValueError("ANTHROPIC_API_KEY is absent or invalid; no credential value is logged")
    return value


def supported_schema(schema):
    """Preserve local Pydantic validation, simplify unsupported wire constraints."""
    result = deepcopy(schema)
    tool_call = result.get("$defs", {}).get("ToolCall")
    if tool_call:
        # The local dict accepts validated tool arguments; the wire schema must be closed.
        tool_call["properties"]["arguments"] = {
            "anyOf": [cls.model_json_schema() for cls in TOOL_ARGUMENTS.values()]}

    def visit(node):
        if isinstance(node, dict):
            removed = {k: node.pop(k) for k in ("minLength", "maxLength", "maxItems") if k in node}
            if removed:
                node["description"] = (node.get("description", "") +
                                       " Locally enforced constraints: " + json.dumps(removed)).strip()
            if node.get("type") == "object":
                node["additionalProperties"] = False
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)
    visit(result)
    return result


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("Anthropic API redirect refused")


class RequestBudget:
    """Shared across cases. Failed attempts consume the request allowance too."""
    def __init__(self, limit=32):
        self.limit = limit
        self.used = 0

    def take(self):
        if self.used >= self.limit:
            raise RuntimeError("Run-wide Anthropic request limit reached")
        self.used += 1


class Claude:
    kind = "real_anthropic_model"

    def __init__(self, model="claude-sonnet-4-6", env_file=None, budget=None):
        self._key = read_key(env_file)
        self.model = model
        self.budget = budget if budget is not None else RequestBudget()
        self.records = []
        self.opener = build_opener(ProxyHandler({}), NoRedirect())
        self.metadata = {"provider": "anthropic", "model": model,
                         "options": {"temperature": 0, "max_tokens": 1200},
                         "seed": None, "automatic_retries": 0,
                         "run_request_limit": self.budget.limit,
                         "structured_output": "output_config.format JSON schema"}

    def request(self, path, payload=None):
        body = None if payload is None else json.dumps(payload).encode()
        request = Request("https://api.anthropic.com" + path, data=body, headers={
            "x-api-key": self._key, "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"})
        try:
            with self.opener.open(request, timeout=90) as response:
                return json.load(response)
        except HTTPError as exc:
            # Never persist response bodies/headers, which could echo request material.
            raise RuntimeError(f"Anthropic API HTTP {exc.code}; no automatic retry") from None
        except URLError:
            raise RuntimeError("Anthropic API connection failed; no automatic retry") from None

    def check_model(self):
        response = self.request("/v1/models/" + self.model)
        if response.get("id"):
            self.model = response["id"]
            self.metadata["model"] = self.model
        return self.metadata

    def generate(self, messages, schema):
        wire_schema = supported_schema(schema)
        payload = {"model": self.model, "max_tokens": 1200, "temperature": 0,
                   "system": "\n\n".join(m["content"] for m in messages if m["role"] == "system"),
                   "messages": [m for m in messages if m["role"] != "system"],
                   "output_config": {"format": {"type": "json_schema", "schema": wire_schema}}}
        # Bound input growth; this is a payload guard, not an exact billing estimate.
        if len(json.dumps(payload).encode()) > 60000:
            raise RuntimeError("Anthropic request exceeds the pilot's 60 KB payload limit")
        self.budget.take()
        record = {"request_number": len(self.records) + 1, "run_request_number": self.budget.used,
                  "messages": deepcopy(messages), "schema": wire_schema,
                  "status": "started", "attempt": 1}
        self.records.append(record)
        started = perf_counter()
        try:
            response = self.request("/v1/messages", payload)
            text = "".join(block["text"] for block in response["content"] if block["type"] == "text")
            usage = response["usage"]
            record.update({"status": "ok", "response": text,
                           "prompt_tokens": usage["input_tokens"],
                           "completion_tokens": usage["output_tokens"],
                           "cache_creation_input_tokens": usage.get("cache_creation_input_tokens", 0),
                           "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0),
                           "returned_model": response["model"],
                           "done_reason": response.get("stop_reason")})
            if response.get("stop_reason") != "end_turn":
                raise RuntimeError("Anthropic response did not finish normally: " + str(response.get("stop_reason")))
            return text
        except Exception as exc:
            record.update({"status": "error", "error": f"{type(exc).__name__}: {exc}"})
            raise
        finally:
            record["duration_ms"] = round((perf_counter() - started) * 1000, 3)
