"""A local-only Ollama adapter. No API keys, automatic downloads or retries."""
import json
from time import perf_counter
from urllib.request import ProxyHandler, Request, build_opener


class Ollama:
    kind = "real_local_model"

    def __init__(self, model="qwen3:8b", seed=42):
        self.model = model
        self.seed = seed
        self.records = []
        self.opener = build_opener(ProxyHandler({}))
        tags = self.request("/api/tags")
        matches = [m for m in tags["models"] if m["name"] == model]
        if not matches:
            raise ValueError(f"Local model {model!r} is not installed. No download attempted.")
        show = self.request("/api/show", {"model": model})
        if ":cloud" in model or show.get("remote_model") or show.get("remote_host"):
            raise ValueError("This pilot only permits locally installed, locally executed models.")
        self.metadata = {
            "model": model, "digest": matches[0]["digest"],
            "details": matches[0].get("details"),
            "ollama_version": self.request("/api/version")["version"],
            "options": {"temperature": 0, "seed": seed, "num_ctx": 8192, "num_predict": 1200},
            "think": False,
        }

    def request(self, path, data=None):
        body = None if data is None else json.dumps(data).encode()
        request = Request("http://127.0.0.1:11434" + path, data=body,
                          headers={"Content-Type": "application/json"})
        with self.opener.open(request, timeout=120) as response:
            return json.load(response)

    def generate(self, messages, schema):
        record = {"request_number": len(self.records) + 1, "messages": messages,
                  "schema": schema, "status": "started", "attempt": 1}
        self.records.append(record)
        started = perf_counter()
        try:
            response = self.request("/api/chat", {
                "model": self.model, "messages": messages, "format": schema,
                "stream": False, "think": False, "options": self.metadata["options"],
                "keep_alive": "5m",
            })
            record.update({"status": "ok", "response": response["message"]["content"],
                           "prompt_tokens": response.get("prompt_eval_count"),
                           "completion_tokens": response.get("eval_count"),
                           "load_duration_ns": response.get("load_duration"),
                           "done_reason": response.get("done_reason")})
            return response["message"]["content"]
        except Exception as exc:
            record.update({"status": "error", "error": f"{type(exc).__name__}: {exc}"})
            raise
        finally:
            record["duration_ms"] = round((perf_counter() - started) * 1000, 3)


class Scripted:
    """Prewritten outputs for harness tests. Never label these as model measurements."""
    kind = "scripted_test_double"
    metadata = {"model": "scripted", "warning": "Not an LLM"}

    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.records = []

    def generate(self, messages, schema):
        self.records.append({"messages": messages, "schema": schema, "status": "ok"})
        result = next(self.outputs)
        if isinstance(result, Exception):
            self.records[-1]["status"] = "error"
            raise result
        return json.dumps(result) if not isinstance(result, str) else result
