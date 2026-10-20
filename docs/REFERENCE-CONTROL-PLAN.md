# Missing-reference diagnostic

Frozen after follow-up 02 and before this diagnostic call. This is a post-hoc check, not a held-out benchmark or a retry replacing earlier results.

Both follow-up answers inferred that a missing variant had been retired. The model-visible ID was `variant-retired-11`, which could cue that explanation. Change only that context value to the opaque `variant-1099`; leave the question, shared follow-up prompt, tools and expected catalogue match unchanged. Both IDs return `not_found` with no evidence. The saved case ID changes for bookkeeping but is never sent to the model.

Run each workflow once, with a 12-generation-request shared cap. Inspect the full prose for invented explanations. Do not infer a rate or causal mechanism from one pair. Preserve the second run and this diagnostic separately regardless of the result.
