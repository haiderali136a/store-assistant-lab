"""Thirty authored pilot cases, not a representative or held-out benchmark."""
from copy import deepcopy


def catalog():
    stores = {}
    for n, name in enumerate(("cedar", "harbor", "dune"), 1):
        variants = []
        for offset, color, size in ((1, "blue", "M"), (2, "blue", "L"), (3, "red", "M")):
            variants.append({
                "id": f"variant-{n}{offset}", "title": "Drift Tee", "color": color,
                "size": size, "available_for_sale": True,
                "currently_not_in_stock": False,
                "prices": {"SA": {"price": str(169 + n * 10) + ".00", "currency": "SAR"},
                           "AE": {"price": str(159 + n * 10) + ".00", "currency": "AED"}},
            })
        stores[name] = {"variants": variants, "returns_days": str(7 * n)}
    return stores


def scenarios():
    cases = []
    prompts = {
        "known": "What is the current price of the item I selected? Include its currency.",
        "discovery": "Do you have the Drift Tee in blue, size M? What does it cost?",
        "ambiguous": "How much is the blue Drift Tee?",
        "policy": "How many days do I have to return an item?",
        "stale_copy": "Your old Drift Tee guide says 99 SAR. What does my selected one cost now?",
        "changed": "Earlier you said it was cheaper. What is the price now, in the same currency?",
        "market": "How much is my selected item for this storefront's UAE market? Include currency.",
        "unavailable": "Can I buy the selected item right now?",
        "timeout": "What is the current price and currency of my selected item?",
        "mixed": "What is the selected item's current price and currency, and how many days for returns?",
    }
    for n, store in enumerate(("cedar", "harbor", "dune"), 1):
        variant = f"variant-{n}1"
        for family, query in prompts.items():
            known = None if family in ("discovery", "ambiguous", "policy") else variant
            market = "AE" if family == "market" else "SA"
            price = str((159 if market == "AE" else 169) + n * 10) + ".00"
            if family == "changed":
                price = str(209 + n * 10) + ".00"
            required = []
            status = "answered"
            if family not in ("ambiguous", "policy", "unavailable", "timeout"):
                required += [[variant, "price", price],
                             [variant, "currency", "AED" if market == "AE" else "SAR"]]
            if family in ("policy", "mixed"):
                required += [[store, "returns_days", str(7 * n)]]
            if family == "discovery":
                required += [[variant, "available_for_sale", "true"]]
            if family == "unavailable":
                required += [[variant, "available_for_sale", "false"]]
            if family == "ambiguous":
                status = "clarify"
            if family == "timeout":
                status = "unavailable"
            history = []
            if family == "changed":
                history = [{"role": "assistant", "content":
                            f"Previously observed price: {169 + n * 10}.00 SAR for {variant}."}]
            cases.append({
                "id": f"{store}-{family}", "family": family,
                "context": {"store": store, "market": market, "selected_variant": known},
                "query": query, "history": history,
                "world": {"price_override": price if family == "changed" else None,
                          "available_override": False if family == "unavailable" else None,
                          "catalog_timeout": family == "timeout"},
                "expected": {"status": status, "required_claims": required},
            })
    return cases


def input_for_model(case):
    """Never serialize expected answers, family labels or fault controls to the model."""
    return deepcopy({k: case[k] for k in ("context", "query", "history")})
