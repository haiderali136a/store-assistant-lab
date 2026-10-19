# Complete-response presentation replay

Completed 19 October 2026 (Asia/Riyadh). Offline application replay; zero new model requests.

## What changed

The original experiment checked structured claims but left model prose visible. A separate response path now constructs the complete displayed price/policy answer from the saved tool results and the original application context. It never appends the model message. The original graphs and recorded outputs have not been modified.

All twenty saved tool responses produced:

> The selected item's price is 179.00 SAR. The policy lists a 7-day return window. The retrieved details do not specify when that period begins.

Thirteen of the twenty original messages had added “of purchase”; the other seven had left the start unstated. The replay makes the missing start explicit in all twenty. This is one evidence situation repeated, not twenty distinct scenarios or a model accuracy improvement.

## Evidence and reproduction

[replay.json](replay.json) contains every before/after pair, the SHA-256 hash of each source trace, and hashes for the preserved presentation code in [source/storelab](source/storelab). The inputs are the original [repeatability traces](../claude-repeatability-04/REVIEW.md).

From the repository root after installation:

```bash
python -m storelab.presentation_replay \
  --input results/claude-repeatability-04 \
  --output results/my-presentation-replay
python -m unittest discover -s tests -v
```

The output directory must not exist. The complete suite passed 48 tests. The ten presentation test methods include missing, purchase and delivery starts; conflicting duration or start fields; duplicate records; missing and failed policy retrieval; malformed values; scope mismatches; and price conflicts. These are authored deterministic cases, not new model generations. The regression checks the full returned response for each saved trace, then replaces model prose and evidence text/title strings with sentinel text to verify that those strings do not enter the displayed answer.

## Boundaries

The caller selects this response path for a known price/policy intent and supplies authenticated context and store-scoped retrieval results. The function matches the selected variant and market, and policy subject to store; it is not an authentication boundary. Catalogue records in this lab do not themselves carry a store identifier, so upstream store scoping remains necessary.

The renderer supports only the stated price, currency and return-window fields. The optional purchase/delivery field exists in the authored tests; it was absent from the saved model-run evidence. Unknown or malformed start fields withhold the window. Disagreement between supplied window fields withholds it too, including one record omitting a start while another supplies one. That conservative rule is not a policy-precedence resolver.

The code does not establish source truth, freshness, correct field extraction, contradictions hidden in document prose, exclusions, eligibility, dates, taxes or delivery promises. It is a complete response for one lab intent, not a deployed assistant or a general solution to unsupported claims.
