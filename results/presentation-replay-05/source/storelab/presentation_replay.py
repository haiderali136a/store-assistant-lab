"""Replay saved price/policy tool responses without making model requests."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from storelab.presentation import render_price_policy_reply


def replay_trace(trace):
    if trace["case_id"] != "followup-price_and_policy":
        raise ValueError("This replay supports only the selected-item price/policy case")
    request = next(m for m in trace["model_trace"][0]["messages"]
                   if m["role"] == "user")
    # Replay the recorded application context, never a model-generated context.
    context = json.loads(request["content"])["context"]
    return render_price_policy_reply(
        context=context,
        tool_results=[entry["result"] for entry in trace["tool_trace"]])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = sorted(args.input.glob("followup-price_and_policy-*.json"))
    if not paths:
        parser.error("No saved price/policy traces found")
    rows = []
    for path in paths:
        data = path.read_bytes()
        trace = json.loads(data)
        rows.append({"trace": path.name,
                     "trace_sha256": hashlib.sha256(data).hexdigest(),
                     "before": trace["answer"]["message"],
                     "after": replay_trace(trace)})
    args.output.mkdir(parents=True, exist_ok=False)
    source = args.output / "source" / "storelab"
    source.mkdir(parents=True)
    hashes = {}
    for name in ("__init__.py", "cards.py", "presentation.py", "presentation_replay.py"):
        original = Path(__file__).parent / name
        shutil.copyfile(original, source / name)
        hashes[name] = hashlib.sha256(original.read_bytes()).hexdigest()
    report = {"kind": "offline_presentation_replay", "model_requests": 0,
              "input_directory": args.input.name,
              "source_sha256": hashes, "answers": rows}
    (args.output / "replay.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Saved {len(rows)} before/after responses; no model requests.")


if __name__ == "__main__":
    main()
