# Policy-answer review worksheet

Status: completed through the guided chat questionnaire on 19 October 2026. See the [recorded decisions and review method](HUMAN-REVIEW.md). The blank prompts below are retained as the original worksheet; the responses are recorded separately.

## How to review

This checks one specific finding: whether the displayed answer adds a return-window start event that the retrieved policy does not supply. It does not ask you to audit the entire codebase or certify a real merchant’s policy.

1. Read the policy evidence below. It is identical in all twenty saved runs.
2. Read each of the seven distinct answers, A–G. Exact duplicates are grouped, with a link to every run they represent.
3. For each group, record whether the answer states when the seven-day period begins. If it does, quote the relevant words and say whether the policy supports them. Use “unsure” wherever needed.
4. Reply in chat with your A–G decisions, or fill in the blanks here. Flag any other claim you think the article misrepresents. Your decisions will be recorded separately from the existing Codex assessments.

You can inspect every individual message in the linked raw traces under `answer.message`; the retrieved evidence is under `tool_trace`. Grouping only removes exact text duplicates, not differences in wording or formatting.

## Question and evidence

The question was: “What is the selected item's current price and currency, and how many days for returns?”

The catalogue evidence identifies the selected item as the Drift Tee, blue, size M, with a price of 179.00 SAR. The complete retrieved policy evidence is:

```json
{
  "subject": "cedar",
  "source": "policy",
  "evidence_id": "e2-policy",
  "facts": {
    "returns_days": "7"
  },
  "text": "Fictional simplified policy: return within the stated days."
}
```

For this review, “start event” means the event from which the days are counted, such as purchase or delivery. A duration alone does not establish a complete deadline.

## Group A: 9 saved answers

> Your selected item, the Drift Tee (Blue, Size M), is currently priced at 179.00 SAR. The store's return policy allows returns within 7 days of purchase.

Runs: [bounded-r0](followup-price_and_policy-bounded-r0.json), [bounded-r1](followup-price_and_policy-bounded-r1.json), [bounded-r2](followup-price_and_policy-bounded-r2.json), [bounded-r3](followup-price_and_policy-bounded-r3.json), [bounded-r4](followup-price_and_policy-bounded-r4.json), [bounded-r5](followup-price_and_policy-bounded-r5.json), [bounded-r6](followup-price_and_policy-bounded-r6.json), [bounded-r7](followup-price_and_policy-bounded-r7.json), [bounded-r9](followup-price_and_policy-bounded-r9.json).

- Does this answer state a start event? **[Yes / No / Unsure]**
- If yes, which words state it? **[Your answer]**
- Does the retrieved policy support that start event? **[Yes / No / Not applicable / Unsure]**
- Any correction or other concern? **[Your notes]**

## Group B: 1 saved answer

> Your selected item, the Drift Tee (Blue, Size M), is currently priced at 179.00 SAR. The store's return policy allows returns within 7 days.

Runs: [bounded-r8](followup-price_and_policy-bounded-r8.json).

- Does this answer state a start event? **[Yes / No / Unsure]**
- If yes, which words state it? **[Your answer]**
- Does the retrieved policy support that start event? **[Yes / No / Not applicable / Unsure]**
- Any correction or other concern? **[Your notes]**

## Group C: 1 saved answer

> Your selected item, the **Drift Tee** (Blue, Size M), is currently priced at **179.00 SAR**. Returns are accepted within **7 days** of purchase.

Runs: [tool_loop-r0](followup-price_and_policy-tool_loop-r0.json).

- Does this answer state a start event? **[Yes / No / Unsure]**
- If yes, which words state it? **[Your answer]**
- Does the retrieved policy support that start event? **[Yes / No / Not applicable / Unsure]**
- Any correction or other concern? **[Your notes]**

## Group D: 5 saved answers

> Your selected item, the **Drift Tee** (Blue, Size M), is currently priced at **179.00 SAR**. The store's return policy allows returns within **7 days**.

Runs: [tool_loop-r1](followup-price_and_policy-tool_loop-r1.json), [tool_loop-r2](followup-price_and_policy-tool_loop-r2.json), [tool_loop-r3](followup-price_and_policy-tool_loop-r3.json), [tool_loop-r5](followup-price_and_policy-tool_loop-r5.json), [tool_loop-r7](followup-price_and_policy-tool_loop-r7.json).

- Does this answer state a start event? **[Yes / No / Unsure]**
- If yes, which words state it? **[Your answer]**
- Does the retrieved policy support that start event? **[Yes / No / Not applicable / Unsure]**
- Any correction or other concern? **[Your notes]**

## Group E: 2 saved answers

> The selected item — Drift Tee (Blue, Size M) — is currently priced at 179.00 SAR. The store's return policy allows returns within 7 days of purchase.

Runs: [tool_loop-r4](followup-price_and_policy-tool_loop-r4.json), [tool_loop-r6](followup-price_and_policy-tool_loop-r6.json).

- Does this answer state a start event? **[Yes / No / Unsure]**
- If yes, which words state it? **[Your answer]**
- Does the retrieved policy support that start event? **[Yes / No / Not applicable / Unsure]**
- Any correction or other concern? **[Your notes]**

## Group F: 1 saved answer

> Your selected item, the Drift Tee (Blue, Size M), is currently priced at 179.00 SAR. Returns are accepted within 7 days of purchase.

Runs: [tool_loop-r8](followup-price_and_policy-tool_loop-r8.json).

- Does this answer state a start event? **[Yes / No / Unsure]**
- If yes, which words state it? **[Your answer]**
- Does the retrieved policy support that start event? **[Yes / No / Not applicable / Unsure]**
- Any correction or other concern? **[Your notes]**

## Group G: 1 saved answer

> The selected item — Drift Tee (Blue, Size M) — is currently priced at **179.00 SAR**. The store's return policy allows returns within **7 days**.

Runs: [tool_loop-r9](followup-price_and_policy-tool_loop-r9.json).

- Does this answer state a start event? **[Yes / No / Unsure]**
- If yes, which words state it? **[Your answer]**
- Does the retrieved policy support that start event? **[Yes / No / Not applicable / Unsure]**
- Any correction or other concern? **[Your notes]**

## Recording your review

Reviewer: **[To be completed after review]**

Date completed: **[To be completed after review]**

After you submit your decisions, the article can describe exactly what you checked. For example, if completed: “I checked all seven distinct policy answers, covering twenty saved runs, against their retrieved evidence.” The existing Codex assessments will remain available as the earlier review.
