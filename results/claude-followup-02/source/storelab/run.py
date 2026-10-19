"""Run a paired pilot and keep every attempt, including failures."""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import statistics

from .evaluation import assess, evidence_gate
from .fixtures import scenarios, followup_scenarios
from .models import Ollama
from .claude import Claude, RequestBudget
from .workflows import run_case


def save(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def source_hashes():
    root = Path(__file__).resolve().parent.parent
    paths = list((root / "storelab").glob("*.py")) + [root / "pyproject.toml"]
    lock = root / "requirements.lock.txt"
    if lock.exists():
        paths.append(lock)
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def summarize(runs):
    summary = {}
    for architecture in ("bounded", "tool_loop"):
        rows = [r for r in runs if r["architecture"] == architecture]
        if not rows:
            continue
        usage = [entry for r in rows for entry in r["model_trace"]]
        tokens_known = all("prompt_tokens" in e and e["prompt_tokens"] is not None
                           and e.get("completion_tokens") is not None for e in usage)
        summary[architecture] = {
            "runs": len(rows), "structured_passes": sum(r["assessment"]["structured_pass"] for r in rows),
            "errors": sum(r["error"] is not None for r in rows),
            "model_calls_total": sum(r["model_calls"] for r in rows),
            "model_calls_mean": statistics.mean(r["model_calls"] for r in rows),
            "tool_calls_total": sum(r["tool_calls"] for r in rows),
            "elapsed_ms_median": statistics.median(r["elapsed_ms"] for r in rows),
            "prompt_tokens_total": sum(e["prompt_tokens"] for e in usage) if tokens_known else None,
            "completion_tokens_total": sum(e["completion_tokens"] for e in usage) if tokens_known else None,
        }
    return {"warning": "Exploratory pilot. Structured assertions are not full answer correctness. "
                       "Human review required. Local synthetic API; no Shopify integration tested.",
            "architectures": summary}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("ollama", "anthropic"), default="ollama")
    parser.add_argument("--model")
    parser.add_argument("--env-file", type=Path, help="Read only ANTHROPIC_API_KEY from this file")
    parser.add_argument("--max-requests", type=int, default=32, help="Run-wide Anthropic generation request cap")
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--suite", choices=("pilot1", "followup"), default="pilot1")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.repeat <= 10:
        parser.error("--repeat must be between 1 and 10")
    if not 1 <= args.max_requests <= 1000:
        parser.error("--max-requests must be between 1 and 1000")
    if args.output.exists():
        parser.error("Output directory already exists; choose a new directory")
    cases = followup_scenarios() if args.suite == "followup" else scenarios()
    unknown = set(args.case) - {c["id"] for c in cases}
    if unknown:
        parser.error(f"Unknown cases: {sorted(unknown)}")
    if args.case:
        cases = [c for c in cases if c["id"] in args.case]
    budget = RequestBudget(args.max_requests)
    model_name = args.model or ("qwen3:8b" if args.provider == "ollama" else "claude-sonnet-4-6")

    def new_provider(repeat=0):
        if args.provider == "anthropic":
            return Claude(model_name, args.env_file, budget)
        return Ollama(model_name, args.seed + repeat)

    provider = new_provider()
    if args.provider == "anthropic":
        provider.check_model()
        model_name = provider.model
    args.output.mkdir(parents=True, exist_ok=False)
    save(args.output / "fixtures.json", cases)
    manifest = {
        "started_at": datetime.now(timezone.utc).isoformat(), "status": "running",
        "python": platform.python_version(), "platform": platform.system(),
        "machine": platform.machine(), "langgraph": version("langgraph"),
        "pydantic": version("pydantic"), "source_sha256": source_hashes(),
        "model": provider.metadata, "case_ids": [c["id"] for c in cases],
        "suite": args.suite,
        "repeat": args.repeat, "order": "alternating architecture order by case and repeat",
        "network": ("api.anthropic.com; synthetic data only; hosted tracing disabled" if args.provider == "anthropic"
                    else "Ollama on 127.0.0.1 only; hosted tracing disabled"),
        "warmup": "No separate warmup; first-use provider/schema overhead may affect timings",
    }
    save(args.output / "manifest.json", manifest)
    runs = []
    try:
        for repeat in range(args.repeat):
            for i, case in enumerate(cases):
                order = ("bounded", "tool_loop") if (i + repeat) % 2 == 0 else ("tool_loop", "bounded")
                for architecture in order:
                    provider = new_provider(repeat)
                    result = run_case(case, architecture, provider)
                    result["repeat"] = repeat
                    result["assessment"] = assess(case, result)
                    result["gated_answer"] = evidence_gate(result)
                    gated = dict(result, answer=result["gated_answer"])
                    result["gated_assessment"] = assess(case, gated)
                    runs.append(result)
                    filename = f"{case['id']}-{architecture}-r{repeat}.json"
                    save(args.output / filename, result)
                    save(args.output / "summary.json", summarize(runs))
                    print(json.dumps({"case": case["id"], "architecture": architecture,
                                      "calls": result["model_calls"], "ms": result["elapsed_ms"],
                                      "pass": result["assessment"]["structured_pass"],
                                      "reasons": result["assessment"]["reasons"]}), flush=True)
                    if any(e["status"] == "error" for e in result["model_trace"]):
                        raise RuntimeError("Provider request failed; run stopped, trace preserved")
                    if args.provider == "anthropic" and budget.used >= budget.limit and result["error"]:
                        raise RuntimeError("Run request cap reached; partial results preserved")
        manifest["status"] = "complete"
    finally:
        if manifest["status"] == "running":
            manifest["status"] = "interrupted_or_failed"
        manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
        manifest["completed_runs"] = len(runs)
        save(args.output / "manifest.json", manifest)


if __name__ == "__main__":
    main()
