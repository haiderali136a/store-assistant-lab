# First Claude pilot: results and review

18 October 2026. This is a small diagnostic run, not a publishable architecture benchmark.

## What ran

Claude Sonnet 4.6 (`claude-sonnet-4-6`), four authored Cedar-store cases, two workflows, one execution per case/workflow. Temperature 0, output limit 1,200 tokens, no automatic retries, no prompt-cache control. The key was loaded from a private environment file; only synthetic inputs went to Anthropic.

The run completed: eight workflow executions, sixteen generation requests, no provider or parsing errors. Fifty-two of the sixty case/workflow combinations in the thirty-case suite remain untested. No Qwen comparison was run.

| Case | Bounded calls | Loop calls | Original structured check, both workflows |
| --- | ---: | ---: | --- |
| Known variant price | 2 | 2 | Pass |
| Discover blue Drift Tee in M | 2 | 2 | Pass |
| Blue Drift Tee without a size | 2 | 2 | Flagged by clarification-price rule |
| Catalog timeout | 2 | 2 | Pass |

Both paths made one catalog-tool call in each execution. The loop did not make redundant requests or retry the simulated timeout. There is no measured call-count saving in this pilot.

## Review of all eight answers

This was an automated prose review against the saved fixtures and traces. It is not independent human validation. The raw answer, original score and model/tool traces remain unchanged.

| Answer pair | Review |
| --- | --- |
| Known variant | Both gave 179.00 SAR for the selected Cedar variant and cited matching retrieved facts. |
| Discovery | Both searched with the requested color and size and returned 179.00 SAR with availability. The bounded answer also said the product was currently in stock and included `currently_not_in_stock=false`. That is consistent with the simplified fixture, but real Shopify stock semantics have not been contract-tested. |
| Ambiguous size | Both asked the customer to choose M or L. Both quoted 179.00 SAR, which was the price for each returned variant. Their claims were supported. They violated the prompt's explicit instruction not to give current-price claims during clarification, but this is not a demonstrated wrong-price or wrong-store failure. |
| Timeout | Both said details could not be retrieved because of the lookup timeout. Neither invented a price or returned factual claims. Their wording exposes the technical term "catalog lookup timeout"; a customer-facing version could say "I can't check the current price right now." |

The original automatic result is three passes out of four per workflow. **Do not describe this as 75% real-world accuracy.** The failed family exposes an overly broad evaluation policy as well as instruction noncompliance. The customer asked for a price, both candidate sizes had that same price, and both answers still clarified the size.

Before the next evaluation, decide which behavior the product actually needs: withholding every price until a variant is selected, or allowing clearly attributed candidate prices while asking for a choice. The latter is a reasonable default for a read-only shopping assistant. A future grader should distinguish candidate facts from a commitment to one selected variant. Preserve this run instead of silently changing its scores.

## Usage and timing

| Measurement | Bounded | Tool loop |
| --- | ---: | ---: |
| Model requests | 8 | 8 |
| Input tokens | 15,511 | 18,495 |
| Output tokens | 817 | 834 |
| Median complete-turn duration | 7.274 s | 5.783 s |

The bounded path's first execution took 11.129 seconds. Provider/network variance and first-use schema compilation may affect these timings; the pilot did not isolate those causes. Different decision/answer schemas also change token use. Do not present the latency medians or token difference as stable improvements.

Total usage was 34,006 input tokens and 1,651 output tokens, with zero reported cache-write/read tokens. At published Sonnet 4.6 standard rates of $3 per million input tokens and $15 per million output tokens, estimated API usage cost is **$0.126783**, approximately **$0.13**, before taxes or account-specific adjustments. This is a usage estimate, not an invoice. [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)

## Next experiment

Keep the same topic and the same two workflows. First refine the ambiguity contract, then freeze a small set of independently phrased cases that includes differently priced variants, changed prices, a market change, and a failed initial search that a second tool round can recover from. That tests where another model decision is useful rather than constructing a slow baseline.

Article status: not ready to claim an architecture improvement. The evidence currently supports a narrower observation: a well-equipped tool loop also finishes ordinary catalog questions in two model calls, and the evaluation must reflect acceptable customer-facing behavior.

Evidence: [manifest](manifest.json), [summary](summary.json), [fixtures](fixtures.json), [bounded ambiguity trace](cedar-ambiguous-bounded-r0.json), [loop ambiguity trace](cedar-ambiguous-tool_loop-r0.json).
