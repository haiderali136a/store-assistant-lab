# The Return-Policy Detail My Answer Checks Missed

A small LangGraph experiment on the gap between checked fields and the answer a customer reads.

In twenty repeated answers to a synthetic return-policy question, the assistant said the window started at purchase in thirteen of them. All twenty answers passed the structured checks. Those checks verified the seven-day duration without checking every claim in the displayed answer.

While working on a multi-store AI assistant using LangGraph and pgvector retrieval, I built this separate experiment with sample catalogue data. I originally wanted to compare a workflow with one round of tool use against one that could request further rounds. The return-policy answer gave me a more specific problem to investigate.

## What the source said, and what the customer would see

The test question asked for the current price and return window of an item already selected in the application's context. The policy tool returned the following information, alongside its source identifier:

```json
{
  "source": "policy",
  "facts": {"returns_days": "7"},
  "text": "Fictional simplified policy: return within the stated days."
}
```

One of the repeated answers included this sentence:

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

`cedar` identifies the sample store whose return policy was retrieved.

The checker matched the required factual claims and their evidence references to the tool results. It also checked that the answer's `status` field matched the expected outcome, such as `answered` or `unavailable`. These are the lab's *structured assertions*: checks on specific output fields, not on the explanation written to the customer.

The seven-day claim passed correctly. But the message contained an additional claim about purchase, and the output had no field representing that start event. The checker never examined it.

An optional filter rejected unsupported structured claims using the same evidence matching. It left this sentence unchanged because it also did not check the prose.

There are two gaps here. The policy data is incomplete for stating a deadline, and the prose can say more than the fields being validated.

The rule I would use is that every factual claim in the displayed answer must either be rendered from verified fields or be included in the claims checked against evidence. Merely asking the model to list its claims does not establish that it listed everything it said.

## A narrow fix for the return-window summary

In a real store, I would first check the full policy. If it says the window starts at delivery but that detail is missing from the tool response, the fix belongs in retrieval or field extraction. If the policy itself is unclear, its owner needs to clarify the rule. The assistant should not choose a start event. The reply still needs to handle missing information explicitly until that detail is available.

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

A correct summary beside an unrestricted model answer would still leave the same failure possible. The application could show the careful summary and then repeat “of purchase” underneath it.

## Check the complete displayed reply

I added a [response function](https://github.com/haiderali136a/store-assistant-lab/blob/0a086ec268f745be9cb300a2e90f7b6d35703018/storelab/presentation.py) for this specific intent: the selected item’s price and return window. It builds the entire displayed reply from the tool results. It does not append the model’s message or interpolate document prose. The application supplies the store, market and selected item; retrieval must already be scoped to that store.

I replayed the twenty saved tool responses through this path. Each produced:

> The selected item's price is 179.00 SAR. The policy lists a 7-day return window. The retrieved details do not specify when that period begins.

The [before-and-after record](https://github.com/haiderali136a/store-assistant-lab/blob/0a086ec268f745be9cb300a2e90f7b6d35703018/results/presentation-replay-05/replay.json) preserves both messages and hashes of the source traces. This was an offline presentation change, with no new model requests. It does not change the original workflow results or demonstrate a more accurate model.

Repetition only tests the same missing information again. To exercise different decisions, the [response tests](https://github.com/haiderali136a/store-assistant-lab/blob/0a086ec268f745be9cb300a2e90f7b6d35703018/tests/test_presentation.py) also supply an explicit purchase start, an explicit delivery start, conflicting policy fields, and missing or failed policy retrieval. Supported starts are displayed as supplied. When policy fields conflict, the reply says: “The retrieved policies disagree; I could not verify the return window.” If policy retrieval fails, it keeps the supported price and says it could not verify the window. Malformed fields and an unrecognised start event also cause the function to withhold the window.

The regression checks the complete returned text. Replacing the saved model answer with an unsupported sentence does not change it. The response function never reads that message.

This trades flexible wording for control over a small response format. It is still not a return-eligibility decision. Upstream code must establish merchant scope, source freshness and accurate field extraction. Conflict checks compare the supplied fields; they cannot discover contradictions hidden in document prose. Exclusions and broader questions need their own handling.

## The experiment and repeated runs

Both workflows use LangGraph and Claude Sonnet 4.6 at temperature 0, with the same initial prompt, tools and sample data. One can request a single batch of lookups before answering. The other can inspect the results and request another batch. The application's code sets the store and market used by the tools.

The initial six-case comparison covered product options, an old product reference, a changed price, price plus return policy, and a failed lookup.

I then repeated each case ten times per workflow, keeping the inputs and instructions unchanged.

For the return-policy question, the one-batch workflow added the unsupported purchase start in **9 of 10 answers**. The loop did so in **4 of 10**. The remaining answers gave seven days without stating a start event. All twenty policy answers passed the structured checks.

The split is descriptive, not conclusive evidence that the loop is better. These are repeated generations for one question; nine bounded answers had exactly the same wording. The workflows also differ in their final-step schemas and instructions. The finding supported here is that the checker missed the added claim in both paths.

The [repeatability review](https://github.com/haiderali136a/store-assistant-lab/blob/0a086ec268f745be9cb300a2e90f7b6d35703018/results/claude-repeatability-04/REVIEW.md) records token usage, timings and the individual answer assessments.

These cases did not require a lookup whose input depended on an earlier result. A known item and field may also be fetched and displayed directly. The [companion README](https://github.com/haiderali136a/store-assistant-lab/blob/0a086ec268f745be9cb300a2e90f7b6d35703018/README.md) explains the workflows and related work.

## The same checking gap in a product lookup

Another case returned `not_found` for an old product ID. Several answers said “Your old link is no longer valid”, although the tool had looked up an ID, not tested the link itself. That stronger statement also passed the structured checks.

The ID contained the word `retired`. In the original paired run, both answers claimed the variant had been retired. Across twenty repeat executions with that same ID, only one did: the loop's final repetition. A separate paired diagnostic with an opaque ID produced no retirement claim. These observations do not establish that the descriptive ID caused the wording.

## Scope and reproduction

These synthetic cases were selected during development. There is no live store integration or independent set of customer questions. The workflows use a custom JSON-schema protocol. Temperature 0 does not guarantee identical repetitions, and the observed counts are not production failure rates.

I checked the twenty saved policy answers, grouped into seven exact wordings, against the retrieved policy in a [guided review](https://github.com/haiderali136a/store-assistant-lab/blob/0a086ec268f745be9cb300a2e90f7b6d35703018/results/claude-repeatability-04/HUMAN-REVIEW.md). These represent two behaviours: adding a purchase start or leaving the start unstated. The [review file](https://github.com/haiderali136a/store-assistant-lab/blob/0a086ec268f745be9cb300a2e90f7b6d35703018/results/claude-repeatability-04/POLICY-ANSWERS.md) preserves all twenty policy messages alongside the original Codex assessments. The experiment does not validate live source freshness.

The [companion lab](https://github.com/haiderali136a/store-assistant-lab/blob/0a086ec268f745be9cb300a2e90f7b6d35703018/README.md) contains the fixtures, raw traces, source snapshots and the [renderer](https://github.com/haiderali136a/store-assistant-lab/blob/0a086ec268f745be9cb300a2e90f7b6d35703018/storelab/cards.py). After the README setup, replay the saved responses locally without an API key:

```bash
python -m storelab.presentation_replay \
  --input results/claude-repeatability-04 \
  --output results/my-presentation-replay
```

Optional: rerun the original model comparison. This requires an Anthropic API key and incurs usage charges:

```bash
python -m storelab.run \
  --provider anthropic --model claude-sonnet-4-6 \
  --env-file /path/to/private/.env --suite followup --repeat 10 \
  --max-requests 260 --output results/my-repeatability
```

The request cap limits attempts, not dollar spending. Existing results are preserved separately.

In this example, verifying "seven days" left "from purchase" unchecked. Building the complete reply from supported fields makes that missing information explicit without reintroducing the unchecked sentence. When reviewing another assistant, I would ask: which factual claims in the displayed answer are actually covered by its checks?
