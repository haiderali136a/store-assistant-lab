from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class ToolCall(StrictModel):
    name: Literal["search_catalog", "get_variant", "search_documents"]
    arguments: dict


class Claim(StrictModel):
    subject: str
    field: Literal[
        "price", "currency", "available_for_sale", "currently_not_in_stock",
        "color", "size", "returns_days",
    ]
    value: str
    evidence_id: str


class Answer(StrictModel):
    status: Literal["answered", "clarify", "unavailable", "not_found"]
    message: str = Field(min_length=1, max_length=1500)
    claims: list[Claim] = Field(max_length=16)


class Decision(StrictModel):
    tool_calls: list[ToolCall] = Field(max_length=4)
    answer: Answer | None

    @model_validator(mode="after")
    def exactly_one_kind(self):
        if bool(self.tool_calls) == (self.answer is not None):
            raise ValueError("Return tools OR an answer, not both or neither")
        return self


class SearchArgs(StrictModel):
    query: str = Field(min_length=1, max_length=100)
    color: str | None = None
    size: str | None = None


class VariantArgs(StrictModel):
    variant_id: str


class DocumentArgs(StrictModel):
    query: str = Field(min_length=1, max_length=100)


TOOL_ARGUMENTS = {
    "search_catalog": SearchArgs,
    "get_variant": VariantArgs,
    "search_documents": DocumentArgs,
}

TOOL_DESCRIPTIONS = {
    "search_catalog": (
        "Search this store's catalog by product title, optional color and size. "
        "Use a product title rather than the entire question. Returns matching "
        "variants with current market price and sale availability. No extra "
        "get_variant call is needed for facts already in the response."
    ),
    "get_variant": "Fetch a known variant ID from this store in the current market.",
    "search_documents": (
        "Retrieve this store's policy and descriptive documents using lexical search. "
        "Historical product copy is not evidence for current price or stock."
    ),
}


def tool_contracts():
    return {name: {"description": TOOL_DESCRIPTIONS[name],
                   "arguments": args.model_json_schema()}
            for name, args in TOOL_ARGUMENTS.items()}
