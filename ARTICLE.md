# The Return-Policy Detail My Answer Checks Missed

A small LangGraph experiment on the gap between checked fields and the answer a customer reads.

In the first paired run of a small store-assistant experiment, both workflows returned the correct seven-day return window. Both also said it started at purchase, although the source never specified that. The automated checks passed because they verified the structured fields without checking every claim in the displayed answer.

While working on a multi-store Shopify assistant using LangGraph and pgvector retrieval, I built this separate experiment with fictional catalogue data. I originally wanted to compare a workflow with one round of tool use against one that could request further rounds. The return-policy answer gave me a more specific problem to investigate.

## What the source said, and what the customer would see

The test question asked for the current price and return window of an item already selected in the application's context. The policy tool returned the following information, alongside its source identifier:

```json
{
  "source": "policy",
  "facts": {"returns_days": "7"},
  "text": "Fictional simplified policy: return within the stated days."
}
```

In that initial run, both workflows included this sentence in their answers:

> The store's return policy allows returns within 7 days of purchase.

The source supplied the duration. It did not say whether the period began at purchase, delivery or another event. A customer could reasonably read that sentence as a complete deadline, even though the assistant did not have enough information to give one.

## Why the checks passed

Each model answer contained a customer-facing message and a list of factual claims. For the return window, the claim looked like this:

```json
{
  "subject": "cedar",
  "field": "returns_days",
  "value": "7",
  "evidence_id": "e2-policy"
}
```

`cedar` identifies the fictional store whose return policy was retrieved. The return window belongs to that store's policy.

The checker confirmed that the requested value matched the retrieved evidence. It also checked whether the assistant answered or correctly explained that it could not verify something. These are the lab's *structured assertions*: checks on specific output fields.

The seven-day claim passed correctly. But the message contained an additional claim about purchase, and the output had no field representing that start event. The checker never examined it.

An optional filter rejected unsupported structured claims using the same evidence matching. It left this sentence unchanged because it also did not check the prose.

There are two gaps here. The policy data is incomplete for stating a deadline, and the prose can say more than the fields being validated.

The rule I would use is that every factual claim in the displayed answer must either be rendered from verified fields or be included in the claims checked against evidence. Merely asking the model to list its claims does not establish that it listed everything it said.

## A narrow fix for the return-window summary

For this particular output, I added a small renderer that writes a policy summary from application-selected evidence. It keeps an unknown start event explicit:

```python
from storelab.cards import render_return_window

policy = {
    "source": "policy",
    "facts": {"returns_days": "7"},
}

print(render_return_window(policy))
# The policy lists a 7-day return window.
# The retrieved details do not specify when that period begins.
```

The renderer validates the duration. If the policy record explicitly supplies the optional field `returns_start_event: "delivery"`, it can say "from delivery". That field is an extension demonstrated by the renderer; the measured tool response did not contain it.

I chose ordinary code because this summary has a small number of supported fields and predictable wording. A stricter prompt is another option, but would need testing. Checking every assertion in free-form prose, possibly with another model, would cover a broader kind of answer and introduce its own validation work. I have not compared those approaches here.

The renderer needs no model request, and its regression test uses the policy evidence saved from the run. It was added afterwards as a separate example, so it is not counted as an improvement in the original workflow results.

This is a return-window summary, not a decision about eligibility. The application still needs the right merchant policy, its exclusions and current terms. Also, showing a correct card beside an unrestricted model answer would leave room for the same unsupported sentence elsewhere. The card only controls the text it renders.

## The experiment and repeated runs

Both workflows use LangGraph and Claude Sonnet 4.6 at temperature 0, with the same initial prompt, tools and fictional data. One can request a single batch of lookups before answering. The other can inspect the results and request another batch. The application's code sets the store and market used by the tools.

The initial six-case comparison covered product options, an old product reference, a changed price, price plus return policy, and a failed lookup. All twelve executions passed the structured checks.

I then repeated each case ten times per workflow, keeping the inputs and instructions unchanged. All 120 executions passed those checks and used two model requests each. Executing a tool is counted separately from calling the model.

For the return-policy question, the one-batch workflow added the unsupported purchase start in **9 of 10 answers**. The loop did so in **4 of 10**. The remaining answers gave seven days without stating a start event. All twenty policy answers passed the structured checks.

That difference belongs in the result. The shared checker left the assertion unchecked in both paths, but the paths produced it at different frequencies. These are repetitions of one synthetic question, and the workflows also differ in their final-step schemas and instructions; this does not establish a general architecture ranking or a production failure rate.

The repeatability run used 240 model requests and about $2.08 in estimated standard API usage, separate from the initial comparison's $0.21. The [repeatability review](results/claude-repeatability-04/REVIEW.md) records token usage, timings and the individual answer assessments.

These cases did not require a lookup whose input depended on an earlier result. Two model calls are not a minimum either: a known item and field may be fetched and displayed directly. The [companion README](README.md) explains the workflows and related work.

## I also had to review the tests

Another fixture used an old product ID containing the word `retired`. Both answers said the variant had been retired, although the lookup returned only `not_found`.

A separate diagnostic used an opaque ID. Neither workflow claimed retirement. The descriptive ID is a plausible contributor, although one paired run cannot establish the cause. That detail belongs in the review: the test itself gave the model a cue.

## Scope and reproduction

These synthetic cases were selected during development. There is no live Shopify integration or independent test set. The workflows use a custom JSON-schema protocol with different final-step schemas; this can affect their outputs. Temperature 0 does not guarantee identical repetitions.

The [answer review](results/claude-repeatability-04/POLICY-ANSWERS.md) preserves all twenty policy messages and identifies who assessed them. The experiment does not establish production reliability or validate live source freshness.

The [companion lab](README.md) contains the fixtures, raw traces, source snapshots and the [renderer](storelab/cards.py). After the README setup, the comparison can be rerun with:

```bash
python -m storelab.run \
  --provider anthropic --model claude-sonnet-4-6 \
  --env-file /path/to/private/.env --suite followup --repeat 10 \
  --max-requests 260 --output results/my-repeatability
```

This calls a paid API; the request cap limits attempts, not dollar spending. Existing results are preserved separately.

In this example, verifying "seven days" left "from purchase" unchecked. The renderer makes that missing information explicit in the summary. When reviewing another assistant, I would ask: which factual claims in the displayed answer are actually covered by its checks?
