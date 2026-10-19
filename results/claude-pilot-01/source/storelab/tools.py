from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import re
from time import perf_counter

from .contracts import TOOL_ARGUMENTS, ToolCall
from .fixtures import catalog


class StoreTools:
    """Credentials/store scope are server-owned; model arguments cannot override them."""

    def __init__(self, context, world):
        self.context = deepcopy(context)
        self.world = deepcopy(world)
        self.store = deepcopy(catalog()[context["store"]])
        self.records = []

    def _variant(self, variant, evidence_id):
        market = self.context["market"]
        if market not in variant["prices"]:
            return None
        facts = {k: variant[k] for k in ("color", "size", "available_for_sale", "currently_not_in_stock")}
        facts.update(variant["prices"][market])
        if self.world.get("price_override") is not None:
            facts["price"] = self.world["price_override"]
        if self.world.get("available_override") is not None:
            facts["available_for_sale"] = self.world["available_override"]
        return {"subject": variant["id"], "title": variant["title"],
                "evidence_id": evidence_id, "source": "catalog", "market": market,
                "observed_at": "2026-01-01T12:00:00Z", "facts": {
                    k: str(v).lower() if isinstance(v, bool) else str(v) for k, v in facts.items()}}

    def _execute(self, call, evidence_id):
        args = TOOL_ARGUMENTS[call.name].model_validate(call.arguments)
        if call.name != "search_documents" and self.world.get("catalog_timeout"):
            return {"status": "timeout", "evidence": [], "detail": "Catalog lookup timed out."}
        if call.name == "search_documents":
            tokens = set(re.findall(r"\w+", args.query.lower()))
            evidence = []
            if tokens & {"return", "returns", "refund", "policy", "days"}:
                evidence.append({"subject": self.context["store"], "source": "policy",
                                 "evidence_id": evidence_id + "-policy", "facts": {
                                     "returns_days": self.store["returns_days"]},
                                 "text": "Fictional simplified policy: return within the stated days."})
            if tokens & {"drift", "tee", "price", "guide"}:
                evidence.append({"subject": "drift-guide", "source": "historical_copy",
                                 "evidence_id": evidence_id + "-guide", "facts": {},
                                 "text": "Old Drift Tee guide: advertised at 99 SAR. Not a current quote."})
            return {"status": "ok", "evidence": evidence}
        variants = self.store["variants"]
        if call.name == "get_variant":
            variants = [v for v in variants if v["id"] == args.variant_id]
        else:
            tokens = set(re.findall(r"\w+", args.query.lower()))
            variants = [v for v in variants if tokens & set(v["title"].lower().split())]
            if args.color:
                variants = [v for v in variants if v["color"].lower() == args.color.lower()]
            if args.size:
                variants = [v for v in variants if v["size"].lower() == args.size.lower()]
        evidence = [row for i, v in enumerate(variants)
                    if (row := self._variant(v, f"{evidence_id}-{i}")) is not None]
        return {"status": "ok" if evidence else "not_found", "evidence": evidence}

    def batch(self, calls: list[ToolCall]):
        offset = len(self.records)

        def invoke(item):
            i, call = item
            started = perf_counter()
            try:
                result = self._execute(call, f"e{offset + i + 1}")
            except (ValueError, KeyError) as exc:
                result = {"status": "invalid_arguments", "evidence": [], "detail": str(exc)}
            return {"call": call.model_dump(), "result": result,
                    "duration_ms": round((perf_counter() - started) * 1000, 3)}

        # Calls in the same batch must be independent. Results retain request order.
        with ThreadPoolExecutor(max_workers=4) as pool:
            records = list(pool.map(invoke, enumerate(calls)))
        self.records.extend(records)
        return records

    def evidence(self):
        return [e for record in self.records for e in record["result"]["evidence"]]
