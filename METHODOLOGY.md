# Method and limitations

## Keep the comparison narrow

The independent variable is whether the model can select another tool batch after seeing the first batch's result. Both graphs share their initial instructions, tool schemas and store data. The bounded graph uses a final-answer schema after the tool batch; the loop retains a decision schema. That schema difference is part of the tested architecture and could affect quality or output tokens.

No extra agents, LLM graders, embeddings or rerankers run. Search is deliberately simple lexical lookup. A tool batch executes independent Python calls concurrently, but the synthetic services have no realistic network latency. Provider structured-output calls are real model requests when using Ollama or Anthropic; scripted tests are not. Compare architectures within the same provider/model run, not across providers as if inference conditions were equivalent.

## Scenarios

The thirty authored scenarios are ten families repeated across three fictional stores. They are **not thirty independent problem types**, a random customer sample, or a held-out benchmark. Store-specific prices and policies differ; product titles overlap intentionally.

Families: known variant, discovery with color/size, ambiguous variant, return-policy question, old product copy, changed price, different market, unavailable for sale, catalog timeout, and a mixed catalog/policy question.

The changed-price case includes a hand-authored earlier assistant message. It does not replay a model-generated multi-turn conversation. Each run gets an isolated synthetic store snapshot. The timestamp is a fixed fixture clock. The timeout is injected rather than a real delayed network request. These choices make the first comparison controlled but limit realism.

Model input contains only application context, the user question, and provided conversation history. Expected answers, scenario names, fault controls, and grading assertions stay outside the prompt. Catalog and policy data become visible only through tool results.

## Calls and timing

A generation request counts when attempted, including transport or parsing failures. There are no automatic retries. Model-selected tool calls are distinct from model requests. A batch of two tools can still require only one planning request and one answer request.

The bounded graph allows one batch and at most two model calls. The loop allows six calls and twelve tools. Exceeding a budget is an execution error, not a successful abstention. Both can answer or clarify in the first call, but unsupported guesses fail evidence checks.

Timing surrounds graph invocation and includes local inference and tools; it excludes graph construction and provider metadata probes. Record model load time separately. The runner alternates workflow order between cases and repetitions. There is no separate warmup. Cache reuse and laptop load can still bias timing. Do not publish a universal speedup from one paired pilot or calculate precise tail latency from a tiny sample.

Tokens come from the provider, not character estimates. Runtime versions, options, fixtures and source hashes are saved; Ollama also records its model digest. Local API cost is not estimated; electricity and hardware are not free. For Anthropic, record the returned model and separate cache usage. Any USD estimate uses published prices and provider-reported usage; it is not an invoice. The request cap bounds attempts, not dollar spending.

Anthropic's schema compilation can affect first-use latency. Its adapter removes unsupported string/array length constraints from the wire schema and validates them locally. The same conversion applies to both architectures. There is no configured prompt-cache control or thinking mode. The first pilot is too small to infer latency superiority, especially with separate final-answer and decision schemas.

## Assessment

The structured check requires the expected decision and all required facts, with matching evidence identifiers. A correct price guessed without retrieving evidence fails. Abstaining on an answerable price request fails. In the original pilot contract, returning a candidate's price while asking which variant the customer means also fails. The separately labelled follow-up permits supported candidate prices with currency, size and colour claims. It does not change original pilot scores.

The check does **not** read the prose for semantic correctness. A model could put a correct price in its claims and a different price in its message. Every answer therefore carries `human_review_required: true`.

Review each message for: agreement with claims; appropriate handling of variant ambiguity; no invented stock, reservation or delivery guarantees; truthful uncertainty; and sufficient usefulness. Save the review separately rather than silently overwriting model output.

The optional evidence gate catches unsupported structured claims, but does not certify intent, completeness, authorization of a production session, or prose accuracy. It is intentionally reported separately. An unavailable answer caused by a provider error cannot become a passing result just because the gate returns a polite fallback.

## Shopify boundary

These tools simulate a small catalog shape. They do not prove Shopify API compatibility. A current-price observation is not a reservation or a guaranteed checkout amount. `available_for_sale` and `currently_not_in_stock` remain distinct. The synthetic return policy omits real-world exclusions and conditions.

Before adding a live adapter, validate it against a disposable development store and a pinned Shopify API version. Keep server-owned store/market scope and credentials outside model-controlled arguments. See [ProductVariant](https://shopify.dev/docs/api/storefront/latest/objects/ProductVariant) and [contextual queries](https://shopify.dev/docs/storefronts/headless/building-with-the-storefront-api/in-context).

## Publication gate

Run and inspect the initial pilot before tuning. Preserve all failed and successful traces. Any prompt/schema changes require a separately labeled run with fresh source hashes. Freeze a new, independently phrased evaluation set before making broader claims; repeated store variants are not a substitute for that set.

The public article can report a tie, a limitation, or an advantage. It needs at least one useful observed result, reproducible traces, and completed prose review. It must distinguish authored fixtures from merchant traffic and hypothetical failures from production incidents. No article conclusion is established by the offline tests alone.

## Completed follow-up and diagnostic

The [follow-up protocol](docs/FOLLOWUP-PLAN.md) was written before its hosted run. Six authored cases received the same revised instructions in both architectures; all used the Cedar store. Cross-store isolation remains an offline harness check, not a claim from the hosted results. The [neutral-ID diagnostic](docs/REFERENCE-CONTROL-PLAN.md) was designed after inspecting the follow-up and changes only a model-visible context identifier. It is post-hoc, not held out.

All 22 saved workflow executions across the three runs used two model calls. This does not prove two calls suffice generally. The follow-up's twelve structured passes include four messages with unsupported wording: two explanations of a missing reference and two return-policy start events. The ID diagnostic removes the former wording in its single paired execution; this cannot establish a mechanism or frequency. Full messages were reviewed by the coding assistant; independent human review remains outstanding.

The `cards.py` renderer was added after all hosted runs. It consumes application-selected policy evidence and formats a restricted return-window statement. It is tested separately and is not a measured repair of the free-form model workflows. It cannot validate merchant scope, source freshness, conflicting policies, eligibility or neighbouring model prose.

## Ten-repeat confirmation check

Completed 18 October; reviewed 19 October 2026. The unchanged six-case follow-up was repeated ten times per workflow, with 120 structured passes in 120 executions and two model requests per execution. Policy prose added an unsupported purchase start in 9/10 bounded and 4/10 loop answers. This is consistency testing of a known synthetic example, not held-out traffic evaluation. See the [frozen plan](docs/REPEATABILITY-PLAN.md), [review](results/claude-repeatability-04/REVIEW.md) and [complete policy messages](results/claude-repeatability-04/POLICY-ANSWERS.md). The shared validation gap and different observed frequencies must both be reported.
