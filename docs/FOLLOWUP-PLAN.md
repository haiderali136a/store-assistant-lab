# Follow-up protocol, frozen before the second hosted run

18 October 2026. Six authored cases, one paired execution per case, Claude Sonnet 4.6, at most 40 generation requests across the run. No retries or selective reruns. This is exploratory development following pilot 1, not an independent test set.

## Question

Does allowing another tool batch help with a missing product reference, when both workflows can use the customer's product description? Also check whether a better clarification contract permits useful, supported candidate prices.

## Cases

1. Blue Drift Tee, unspecified size, both sizes 179 SAR.
2. Same question, M at 179 SAR and L at 199 SAR.
3. Old selected variant ID no longer resolves. Customer supplies title, colour and size and explicitly requests a current catalogue search if needed.
4. A previously quoted price has changed.
5. Current price plus return policy, requiring two independent tools.
6. Catalogue lookup fails; no current price evidence is available.

The clarification cases may ask a question without quoting a price. If quoting candidates, each price needs supported currency, size and colour claims, with matching prose. The customer must not be treated as having selected a size. This is a stated application contract, not a universal rule for retail assistants.

The missing-reference case deliberately allows a successful first-batch search. Neither workflow is forced to try the stale ID alone. A current title/options match is not proof of identity continuity with the deleted variant. Review that distinction in the prose. Safe abstention can be reasonable but does not complete the customer's requested search.

## What changed

The shared prompt permits labelled candidate prices and describes a customer-authorised search after a missing reference. Both workflows receive exactly the same new instructions. The evaluator retains pilot 1's stricter rule for its original cases. The tools add fixture-specific variant price overrides. No new model, routing optimisation, production adapter or repair agent is introduced.

Pilot 1 outputs and grades remain unchanged; its original source has been copied to `results/claude-pilot-01/source` and verified against its manifest hashes. Do not compare aggregate pass counts across protocols as a measured architecture improvement.

## Review and reporting

Save every attempt, prompt, response, tool result and usage count. Review all customer messages against evidence. Report call counts and task outcomes per case, including ties and incomplete answers. Latency is descriptive only. These few authored cases cannot establish accuracy, production savings, store isolation, or a general architecture ranking.

If both paths solve the old-link case in one batch, report that result. Do not make tools less informative or hide customer information to manufacture an advantage for the loop.
