"""Complete display response for one application-selected price/policy intent.

The caller supplies authenticated context and tool results already scoped to that
store. This is not an intent classifier, freshness check or eligibility engine.
Model prose, document prose and product titles are never interpolated.
"""
import re

from storelab.cards import render_return_window


def render_price_policy_reply(*, context: dict, tool_results: list) -> str:
    """Return the entire displayed reply, not a card appended to model prose."""
    if not all(isinstance(context.get(k), str) and context[k]
               for k in ("store", "market", "selected_variant")):
        return "Select an item before requesting its price and return window."

    evidence = []
    for result in tool_results:
        if not isinstance(result, dict) or result.get("status") != "ok":
            continue
        rows = result.get("evidence", [])
        if isinstance(rows, list):
            evidence.extend(row for row in rows if isinstance(row, dict))

    prices = [row for row in evidence if row.get("source") == "catalog"
              and row.get("subject") == context["selected_variant"]
              and row.get("market") == context["market"]]
    policies = [row for row in evidence if row.get("source") == "policy"
                and row.get("subject") == context["store"]]
    return _price_text(prices) + " " + _policy_text(policies)


def _price_text(rows):
    values = set()
    for row in rows:
        facts = row.get("facts")
        if not isinstance(facts, dict):
            return "I could not verify the selected item's price."
        price, currency = facts.get("price"), facts.get("currency")
        if (not isinstance(price, str)
                or not re.fullmatch(r"(?:0|[1-9][0-9]{0,8})\.[0-9]{2}", price)
                or not isinstance(currency, str)
                or not re.fullmatch(r"[A-Z]{3}", currency)):
            return "I could not verify the selected item's price."
        values.add((price, currency))
    if not values:
        return "I could not verify the selected item's price."
    if len(values) != 1:
        return "The retrieved prices disagree; I could not verify the selected item's price."
    price, currency = next(iter(values))
    return f"The selected item's price is {price} {currency}."


def _policy_text(rows):
    values = set()
    for row in rows:
        facts = row.get("facts")
        if not isinstance(facts, dict):
            return "I could not verify the return window."
        days, start = facts.get("returns_days"), facts.get("returns_start_event")
        if (not isinstance(days, str)
                or not re.fullmatch(r"[1-9][0-9]{0,2}", days)
                or (start is not None and (
                    not isinstance(start, str) or start not in ("purchase", "delivery")))):
            return "I could not verify the return window."
        values.add((days, start))
    if not values:
        return "I could not verify the return window."
    if len(values) != 1:
        return "The retrieved policies disagree; I could not verify the return window."
    days, start = next(iter(values))
    return render_return_window({"source": "policy", "facts": {
        "returns_days": days, "returns_start_event": start}})
