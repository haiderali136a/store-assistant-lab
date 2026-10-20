# Repeatability check, frozen before execution

18 October 2026. Repeat the unchanged six-case `followup` suite ten times per workflow using Claude Sonnet 4.6, temperature 0. This produces 120 workflow executions. The original twelve-execution follow-up remains separate.

No prompt, schema, tool, fixture or scoring changes. Alternate architecture order as implemented by the runner. Use fresh model and tool state per execution. Do not retry or discard unfavourable answers. Stop on a provider failure and preserve partial results.

The previous run suggests about 240 generation requests and $2.08 in standard usage for this check. Set a shared 260-request cap. This limits attempted requests, not dollar spending. The expected cost is an estimate, not a guaranteed charge.

## Question and review rule

For the price-and-policy case, does the displayed answer assert a start event for the seven-day window that the retrieved policy never supplies?

Review all twenty new price-and-policy messages against their tool evidence. Count an unsupported start event only when the message asserts purchase, delivery, receipt or another event as the period's start. A question about the start event or an explicit statement that it is unknown does not count. Preserve exact excerpts and per-execution decisions. Do not rely on substring counts as a semantic grader. Review the other hundred messages for conflicting facts, unsupported explanations and misleading abstentions, separately from their structured scores.

Report the two workflows separately with denominators, including errors or missing answers. Record structured checks, model and tool counts, token usage, and estimated cost. Do not change the output-contract evaluator after seeing results. The post-hoc prose review is explicitly performed by the coding assistant, not independently by Haider.

## Interpretation

Ten repetitions of the same authored fixture measure consistency under these inputs. They are not ten independent customer situations or evidence of a production failure rate. The two workflows share prompt, model, evidence and claim schema. A shared observed mistake does not isolate orchestration as irrelevant or identify the model's internal cause. No remediation comparison is included in this run.

This protocol was written after the original finding, so the repetition is a confirmation check on a known example, not a new held-out benchmark.
