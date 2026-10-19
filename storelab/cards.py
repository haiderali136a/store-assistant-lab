"""Narrow presentation example, separate from the measured model workflows."""
import re


def render_return_window(evidence):
    """Render one application-selected policy record, never model-written prose.

    The caller owns source selection, merchant scope, freshness and conflicts.
    Only renders a window; it does not decide eligibility or include exclusions.
    `returns_start_event` illustrates an optional extension to the tool contract.
    """
    if evidence.get("source") != "policy":
        return "I could not verify the return window."
    facts = evidence.get("facts", {})
    days = facts.get("returns_days")
    if not isinstance(days, str) or not re.fullmatch(r"[1-9][0-9]{0,2}", days):
        return "I could not verify the return window."
    start = {"purchase": "purchase", "delivery": "delivery"}.get(
        facts.get("returns_start_event"))
    if start:
        return f"The policy lists a {days}-day return window from {start}."
    return (f"The policy lists a {days}-day return window. "
            "The retrieved details do not specify when that period begins.")
