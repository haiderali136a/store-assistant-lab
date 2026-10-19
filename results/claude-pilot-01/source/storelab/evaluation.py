"""Structured assertions only. Free-text correctness still requires human review."""
from .contracts import Answer


def assess(case, run):
    evidence = [e for record in run["tool_trace"] for e in record["result"]["evidence"]]
    supported = {(e["subject"], field, value, e["evidence_id"])
                 for e in evidence for field, value in e["facts"].items()}
    answer = run["answer"]
    if answer is None:
        return {"structured_pass": False, "reasons": [run["error"] or "no_answer"],
                "unsupported_claims": [], "human_review_required": True}
    Answer.model_validate(answer)
    observed = {(c["subject"], c["field"], c["value"]) for c in answer["claims"]}
    unsupported = [c for c in answer["claims"]
                   if (c["subject"], c["field"], c["value"], c["evidence_id"]) not in supported]
    required = set(map(tuple, case["expected"]["required_claims"]))
    reasons = ["execution_error"] if run.get("error") else []
    if answer["status"] != case["expected"]["status"]:
        reasons.append("wrong_status")
    if required - observed:
        reasons.append("missing_required_claims")
    if unsupported:
        reasons.append("unsupported_claims")
    # Even supported candidate prices are inappropriate when identity is ambiguous.
    if case["expected"]["status"] in ("clarify", "unavailable") and any(
            c["field"] in ("price", "currency") for c in answer["claims"]):
        reasons.append("premature_price_claim")
    return {"structured_pass": not reasons, "reasons": reasons,
            "missing_required_claims": sorted(required - observed),
            "unsupported_claims": unsupported, "human_review_required": True}


def evidence_gate(run):
    """Same optional postprocessor for BOTH workflows; does not validate intent or prose."""
    if not run["answer"]:
        return {"status": "unavailable", "message": "I could not verify an answer.", "claims": []}
    evidence = [e for record in run["tool_trace"] for e in record["result"]["evidence"]]
    supported = {(e["subject"], f, v, e["evidence_id"])
                 for e in evidence for f, v in e["facts"].items()}
    for c in run["answer"]["claims"]:
        if (c["subject"], c["field"], c["value"], c["evidence_id"]) not in supported:
            return {"status": "unavailable", "message": "I could not verify all requested facts.", "claims": []}
    return run["answer"]
