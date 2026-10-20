# Follow-up: equal call counts, incomplete answer checks

Run completed 18 October 2026 using Claude Sonnet 4.6. Six authored cases, two workflows, one execution per pairing. This follows pilot 1 and uses a revised shared prompt and clarification contract. It is not a held-out evaluation.

## Measured result

| Case | Bounded LLM calls / tools | Loop LLM calls / tools | Structured check | Prose review |
| --- | --- | --- | --- | --- |
| Same candidate prices | 2 / 1 | 2 / 1 | Both pass | Both label the two sizes, quote supported prices and ask for a choice. |
| Different candidate prices | 2 / 1 | 2 / 1 | Both pass | Both correctly show M at 179 SAR and L at 199 SAR while clarifying. |
| Missing old reference | 2 / 2 | 2 / 2 | Both pass | Both find the requested match but infer that the old variant was retired. Tool evidence does not establish that reason. |
| Changed price | 2 / 1 | 2 / 1 | Both pass | Both use current 219 SAR rather than historical 179 SAR. The explanations are unnecessarily technical for customers. |
| Price and return policy | 2 / 2 | 2 / 2 | Both pass | Both add an unsupported start event: “within 7 days of purchase.” Source gives only seven days. |
| Catalogue timeout | 2 / 1 | 2 / 1 | Both pass | Both abstain without a price and explain a temporary issue. |

An automated prose review assessed all twelve messages against the saved evidence. This is not independent human review. Twelve structured passes must not be described as twelve fully correct answers. The optional evidence gate also leaves the problematic prose unchanged because its scope is structured claims.

Both paths used twelve model calls and eight tool calls across their six executions. The loop never needed a second tool batch. In the missing-reference case, both proactively requested the old-ID lookup and the independent title/options search together. There is no observed call-count saving or adaptive-recovery advantage here.

## Review details

**Clarification:** candidate prices are useful when they are attached to the relevant options. The new contract permits this but still asks the customer to choose. Requiring a choice for a price-only question is an application policy, not a universal correctness rule. The earlier aggregate grades cannot be compared with these as an architecture improvement.

**Missing reference:** `get_variant` returns `not_found`, with no evidence. Both messages say the variant “has been retired.” The input identifier is `variant-retired-11`, an avoidable cue. It does not authorise an explanation of catalogue state. A separate [neutral-ID diagnostic](../claude-reference-control-03/REVIEW.md) checks this without replacing these results.

**Return policy:** the retrieved facts contain `returns_days: "7"`; the text is “Fictional simplified policy: return within the stated days.” Neither supplies purchase, delivery, receipt or another start event. Both model messages add “of purchase.” The structured claims contain the correct seven-day number, so the checker passes them. This demonstrates a specific gap between the checked fields and the displayed prose under an incomplete source contract.

**Stock wording:** the old-reference answers also say “in stock,” using `available_for_sale: true` and `currently_not_in_stock: false`. Those are both present in the fixture. No live Shopify inventory interpretation has been validated. Avoid turning this into a physical-stock or delivery guarantee in a real adapter.

**Time wording:** the models use “current” or “today,” while the tool timestamp is a fixed synthetic clock. The lab has no staleness threshold or real-time freshness guarantee. The frozen snapshot is treated as current within each scenario only.

## Usage

| Workflow | Input tokens | Output tokens | Median elapsed seconds |
| --- | ---: | ---: | ---: |
| Bounded | 24,964 | 1,468 | 7.531 |
| Loop | 29,434 | 1,521 | 9.059 |

Total: 54,398 input tokens, 2,989 output tokens, 24 generation requests, no provider errors. No cache tokens were reported. At the published Sonnet 4.6 standard rates of $3 per million input tokens and $15 per million output tokens, estimated usage is **$0.208029, about $0.21**. This is not an invoice and excludes tax or account-specific pricing. [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing), checked 18 October 2026.

The schemas and final-step instructions differ between architectures. That can affect token usage and behaviour. Provider/schema warmup, request order and one execution per case prevent a reliable latency ranking. Do not promote these medians as a speedup.

## Reproduction and next use

Original source is in `source/`, verified against this run's `manifest.json`. Fixtures and raw traces are preserved. From that source snapshot, use the README environment setup, then run:

```bash
python -m storelab.run --provider anthropic --model claude-sonnet-4-6 \
  --env-file /path/to/private/.env --suite followup \
  --max-requests 40 --output /path/to/new-results-directory
```

A fresh run can vary. No automatic retries or selective reruns were used.

The subsequent `storelab/cards.py` example renders a return window from application-selected policy evidence. It is an additional deterministic presentation example, not part of this measured run. Its regression test reuses the actual saved policy response. It prevents the specific invented start-date wording within that card; it does not solve unrestricted answer grounding or policy eligibility.
