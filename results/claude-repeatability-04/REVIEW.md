# Repeatability check: the policy detail varies, the checking gap remains

Run completed 18 October 2026; answer review completed 19 October 2026. Ten fresh executions of each of the six follow-up cases per workflow, Claude Sonnet 4.6, temperature 0. Original follow-up results remain separate. The [plan](../../REPEATABILITY-PLAN.md) was frozen before this run; prompts, schemas, tools and grading rules were unchanged.

## Result

| Measurement | Bounded workflow | Tool loop |
| --- | ---: | ---: |
| Workflow executions | 60 | 60 |
| Structured passes | 60 | 60 |
| Provider/execution errors | 0 | 0 |
| Model requests | 120 | 120 |
| Tool calls | 80 | 80 |
| Return-policy executions | 10 | 10 |
| Unsupported purchase start in policy prose | **9 / 10** | **4 / 10** |
| Policy answers with no start event asserted | 1 / 10 | 6 / 10 |

All 120 executions used two model requests. The twenty policy answers all retrieved the same policy: `returns_days: "7"`, with text that says only to return within the stated days. No policy response supplied purchase or another start event. Thirteen policy messages nevertheless asserted purchase as the start. The other seven stated the duration without asserting a start event; they still did not establish a complete return deadline.

The original two policy answers both contained the unsupported detail. This repetition shows that the behaviour is not uniform: 9/10 versus 4/10, rather than 10/10 in each path. These are counts for one repeated synthetic question, not production failure rates.

The shared checker does not validate that prose assertion in either workflow. The observed frequency difference must also be reported. The workflows differ in final-step schema and instructions, and repeated generation can vary. This run does not isolate why their counts differ or establish that orchestration cannot influence answer wording. It does not demonstrate a general advantage for an agent loop.

## Statistical interpretation and repeated text

The twenty policy outputs contain seven distinct exact messages. Nine of ten bounded outputs (repeats 0–7 and 9) are identical. This is repeated generation on the same question, not twenty independent customer examples. Identical text alone does not establish statistical dependence between requests; the run does not establish independent random sampling from customer traffic either.

For the 2-by-2 table `[[9, 1], [4, 6]]`, a conventional two-sided Fisher exact calculation gives **p = 0.05727554179566564**. This conditional calculation assumes an appropriate independent-observation model; it does not fix the experiment's sampling limitations or isolate a causal effect of orchestration. It is not conclusive evidence of a general architecture advantage, nor proof that the architectures are equivalent. The article reports descriptive counts and does not present a significance claim.

The value was calculated by summing hypergeometric table probabilities no greater than the observed table's probability, with margins fixed at thirteen unsupported-start answers, seven without one, and ten observations per workflow. No additional model calls were made.

## Answer review

The Codex coding assistant read every distinct displayed message and mapped each execution to its text. Exact duplicates were grouped only within the same scenario. Every row was checked against the saved scenario and tool evidence, including re-evaluation of structured assertions. This is not an independent human audit and is not attributed to Haider.

- [POLICY-ANSWERS.md](POLICY-ANSWERS.md): all twenty policy messages, individual labels and raw-trace links.
- [answer-review.json](answer-review.json): all 120 execution records, displayed messages, review notes and counts.

Other findings: the catalogue facts and changed prices agree with the fixtures; clarification messages distinguish sizes and prices; timeout answers abstain. Some missing-reference messages overstate an absent lookup as a definitively invalid or inactive link. The loop's repeat 9 explicitly claims retirement without evidence of that reason. Stock and “today/live” wording remains limited by the synthetic snapshot and unvalidated Shopify semantics. Structured passes are not full-answer correctness certificates.

The existing return-window renderer was exercised against all twenty saved policy records and produced its missing-start-event statement each time. This is a deterministic presentation check, not a repair run of the full model workflows. No prompt was tuned or response discarded after seeing the repetitions.

## Usage and reproducibility

| Workflow | Input tokens | Output tokens | Median elapsed seconds |
| --- | ---: | ---: | ---: |
| Bounded | 249,596 | 14,481 | 6.715 |
| Loop | 294,362 | 15,552 | 6.564 |

Total: **240 generation requests**, **543,958 input tokens**, **30,033 output tokens**, no reported cache tokens. Estimated standard usage is **$2.082369**, about **$2.08**, at $3 per million input tokens and $15 per million output tokens. This is not an invoice and excludes account-specific pricing or taxes. [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing), rates checked 18 October 2026.

Times are descriptive. This run used a fixed scenario schedule and no controlled warmup or network-load conditions. The small difference between medians is not a speed claim.

The complete source snapshot in `source/` matches every hash in `manifest.json`. To reproduce after installing the pinned dependencies, run from that source directory with a new output path:

```bash
python -m storelab.run --provider anthropic --model claude-sonnet-4-6 \
  --env-file /path/to/private/.env --suite followup --repeat 10 \
  --max-requests 260 --output /path/to/new-results-directory
```

The cap limits attempted generation requests, not dollar spending. No automatic retries were used. The run completed within the cap and preserved all attempts.
