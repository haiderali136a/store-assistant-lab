# Review before publication

Start with [ARTICLE.md](ARTICLE.md). It is the complete article draft. [LINKEDIN-POST.md](LINKEDIN-POST.md) is the shorter accompanying post. Neither has been published.

## Main result

The repeatability check is complete: 120 executions, all passing the structured checks. In the return-policy case, the unsupported purchase start appeared in 9/10 bounded-workflow answers and 4/10 loop answers. The remaining seven messages gave the duration without asserting a start event. All twenty policy messages passed the field checks. These are repeated inputs for one authored question, not independent customer situations.

The article now reports the difference rather than treating both workflows as equally prone to the wording. Their shared checker misses this assertion in both paths. Their different final-step schemas and instructions prevent attributing the observed frequencies to one isolated cause.

The companion includes a restricted renderer and a saved-evidence regression test. The renderer was also exercised against all twenty policy responses. It controls its own summary and does not repair the measured model workflows or certify surrounding prose.

## What Haider should review

1. Read the opening and the seven-day-policy example. Can a backend engineer understand the problem and apply the lesson without reading the whole repository?
2. Check the suggested renderer's scope: a policy summary with an unknown start event, not a complete return-eligibility decision. The article should not imply more.
3. Read the old-reference diagnostic and limitations. The article makes no novelty, production-readiness, latency or broad accuracy claim. Confirm that this is the scope you want attached to your name.

The coding assistant has checked the implementation, numerical results and the 120 repeatability answers, grouping exact duplicate messages within each scenario. The twenty policy answers are collected in [POLICY-ANSWERS.md](results/claude-repeatability-04/POLICY-ANSWERS.md) for Haider to inspect. This is not an independent human audit. The last substantive review is the usefulness and interpretation of the examples, not whether the draft contains enough technical jargon.

## Evidence to inspect if needed

- [Ten-repeat check](results/claude-repeatability-04/REVIEW.md): 120 executions, per-answer notes and complete policy-answer excerpts.
- [Initial four-case pilot](results/claude-pilot-01/REVIEW.md): original ambiguity contract and preserved results.
- [Six-case follow-up](results/claude-followup-02/REVIEW.md): per-case table, prose review, usage and reproduction.
- [Neutral-ID diagnostic](results/claude-reference-control-03/REVIEW.md): why the retirement example needs qualification.
- [Policy renderer](storelab/cards.py) and [regression tests](tests/test_cards.py): the narrow code example derived from the finding.

All four runs preserve raw traces, fixtures, manifests and hash-verified source snapshots. Thirty-eight offline tests pass. Across all runs, 142 workflow executions made 284 generation requests. Combined estimated standard API usage is about $2.45; the repetition alone accounts for about $2.08. See individual reports for token counts and rates. These are synthetic examples, not Shopify API tests or customer data.

## Publication sequence

Finish the article review, then create the public GitHub companion and add its real URLs to the article. Publish the full article on Medium, with the code and evidence accessible in the repository, and use the shorter native LinkedIn post to introduce it. Keep the full article accessible where possible. This is an editorial recommendation, not a guarantee of distribution or engagement.

Before making the repository public, select an open-source licence and give the final package a disclosure review. The companion now has a local Git repository and no remote. It has not been uploaded. Relative article links must become public URLs when copied to Medium. The LinkedIn draft's last sentence assumes the write-up is available, so publish in that order. Add the article and repository URLs in a first comment when posting; do not invent placeholder URLs in public copy.

The historical local Ollama attempt remains unexecuted. The published evidence, if approved, must be attributed to Claude Sonnet 4.6.

## Revision after external review, 18 October 2026

The revised title is “The Return-Policy Detail My Answer Checks Missed”. The article and LinkedIn post use the supplied voice guide: plain language, connected paragraphs, British spelling, no em dashes or manufactured dramatic hooks.

Accepted changes: lead with the observed wording problem; define variant, tool batch and structured assertions; explain the renderer choice and its alternatives; state temperature and measured usage; consolidate general limitations; explain the store scope narrowly. Product motivation is described as work on a multi-store assistant, without claiming production deployment or disclosing proprietary implementation.

The companion already exists separately from the product repository. Its public URLs remain a publication task. Earlier drafts were preserved in the parent workspace's `docs/article-revisions/`. No model reruns, source changes or trace changes were needed for this editorial revision. No claim of an independent human review was added.

## Second review follow-up, 19 October 2026

Accepted: repeat all six cases ten times; explain Cedar as the fictional store; use “sets” for scope; identify the selected item as application context without inventing a prior chat turn; name the displayed-claim coverage rule; add the verified high-level Shopify/LangGraph/pgvector motivation; keep the closing question in first person.

The article moves review-method details to the linked evidence report. It does not claim Haider personally reviewed every answer. The LinkedIn draft counts executions, not individual assertions, and refers to synthetic responses rather than messages sent to real customers. No claim about LinkedIn outbound-link suppression was added. Public article and repository URLs are still a publication step.

## Final evidence review, 19 October 2026

The article and post now lead with thirteen unsupported start events in twenty repeated policy answers. The 9/10 versus 4/10 split remains in the article as descriptive evidence, with repeated exact wording and sampling limitations stated. The retirement section distinguishes the original two positive answers, one retirement claim in twenty repetitions with the same ID, and zero in the separate opaque-ID pair. It does not assert that the ID caused the wording. A separate sentence explains why an ID lookup returning `not_found` does not establish that an old link itself was tested and found invalid.

The article now explicitly attributes the recorded answer assessment to Codex. Haider's own confirmation is still pending; no reviewer identity or label has been silently changed. After Haider actually reads the twenty messages and states whether the labels are correct, record that review separately with its real date. Then the article can describe that completed review in first person. This pending editorial sentence is deliberately visible in the draft.

The LinkedIn draft includes a specific reader question. Actual article/repository URLs belong in the publication comment once those destinations exist. No outbound-link suppression claim or fake URL was added.
