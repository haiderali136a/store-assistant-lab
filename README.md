# Store Assistant Lab

A small Python/LangGraph experiment comparing two ways to answer shopping questions. The store data is fictional. This directory contains no proprietary app implementation or merchant data.

The accompanying [article](https://medium.com/@haiderali136a/the-return-policy-claim-my-llm-checks-missed-a68ad6f0ee75), “The Return-Policy Claim My LLM Checks Missed”, focuses on an unsupported policy detail that passed the structured checks. Call counts provide background; the tested cases did not require a dependent lookup round.

**Status, 20 October 2026:** 48 offline tests pass. The ten-repeat follow-up completed 120 executions with 120 structured passes. Unsupported purchase-start wording appeared in 9/10 policy answers from the bounded workflow and 4/10 from the loop. All raw traces and per-answer reviews are saved. Start with the [article](https://medium.com/@haiderali136a/the-return-policy-claim-my-llm-checks-missed-a68ad6f0ee75), [repeatability results](results/claude-repeatability-04/REVIEW.md) or [review guide](REVIEW.md). These are synthetic results, not production failure rates.

## The question

Someone asks: "Do you have the Drift Tee in blue, size M? What does it cost?"

Does the model need to decide every next step, or can one tool batch provide enough evidence to answer? What changes when the price in the conversation is old, the size is missing, or the catalog lookup fails?

Both implementations use LangGraph, the same model, the same initial instructions, and the same tools. Both can finish in two model requests. This experiment does not assume that the looping agent is slower or more expensive.

| Implementation | Path |
| --- | --- |
| `bounded` | Model selects tools or answers directly; code executes one independent tool batch; model writes the answer. At most two model requests. |
| `tool_loop` | Model selects tools or answers; code executes the batch; model may request another batch. At most six model requests and twelve tool calls. |

The bounded version clarifies or abstains when its one batch is insufficient. The looping version can recover by choosing another tool. Whether that flexibility helps is the experiment.

This implementation uses a shared **JSON-schema tool protocol** through Ollama or Anthropic structured outputs. It does not use native provider function calling or a prebuilt ReAct agent. We compare the two custom workflows under that protocol; results will not establish performance for native tool calling or all agent frameworks.

## Run the tests

Python 3.11 or newer; the verified environment uses Python 3.13.7.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python -m unittest discover -s tests -v
```

The tests use prewritten model outputs. They check routing, accounting, evidence validation and failure handling, not model intelligence.

## Replay the complete price-and-policy reply offline

The [presentation function](storelab/presentation.py) builds the whole displayed reply for a known selected-item price/policy intent from store-scoped tool results. It does not include model prose. The [saved replay](results/presentation-replay-05/REVIEW.md) records twenty before/after responses; it is separate from the original model results.

```bash
.venv/bin/python -m storelab.presentation_replay \
  --input results/claude-repeatability-04 \
  --output results/my-presentation-replay
```

No API key or model request is needed. Use a new output directory. Tests also cover explicit purchase/delivery starts, missing and failed policy retrieval, conflicting fields, malformed values and scope mismatches. The policy’s start field is a synthetic contract extension in these tests, not information present in the measured tool responses. This is a complete response for one intent, not a general-purpose assistant or a live store integration.

## Run a real local pilot

Start Ollama with a locally installed model that supports structured outputs. No model downloads happen automatically. The prepared adapter uses `qwen3:8b`, disables thinking, sets temperature to zero, and records its model digest and Ollama version.

```bash
.venv/bin/python -m storelab.run \
  --case cedar-known \
  --case cedar-discovery \
  --case cedar-ambiguous \
  --case cedar-timeout \
  --output results/pilot-01
```

Use a new output directory for each run. Existing results are never overwritten. To run all thirty cases with three repetitions:

```bash
.venv/bin/python -m storelab.run --repeat 3 --output results/pilot-02
```

The complete run is 180 workflow executions, with a maximum of 720 model requests under the configured graph limits. It may take considerable time on a laptop. Start with the four-case pilot. For this default local command, the adapter talks only to `127.0.0.1:11434`; hosted LangSmith tracing is explicitly disabled. No cloud-tagged Ollama model is permitted.

## Optional Claude pilot

The Claude adapter sends synthetic prompts and tool results to Anthropic's Messages API. It reads only `ANTHROPIC_API_KEY` from an explicitly supplied environment file, or from the process environment when no file is supplied. It does not execute shell expressions, copy the environment file, record the credential, or follow API redirects. Do not commit an environment file or paste a key into a command.

```bash
.venv/bin/python -m storelab.run \
  --provider anthropic --model claude-sonnet-4-6 \
  --env-file /path/to/private/.env \
  --case cedar-known --case cedar-discovery \
  --case cedar-ambiguous --case cedar-timeout \
  --max-requests 32 --output results/claude-pilot-01
```

This is a paid API run. `--max-requests` is a run-wide generation-request cap, not a dollar cap. Output is limited to 1,200 tokens per request; there are no automatic retries. A provider failure stops the run and preserves completed traces. Model availability is checked with one metadata request before generating anything. Only the selected cases run.

The adapter simplifies unsupported JSON Schema length constraints for Anthropic and retains validation locally. Tool arguments use a closed union of the existing tool argument schemas. Claude does not accept this runner's Ollama seed option; repetitions are recorded without claiming determinism. See [Anthropic structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).

## Reproduce the follow-up

```bash
.venv/bin/python -m storelab.run \
  --provider anthropic --model claude-sonnet-4-6 \
  --env-file /path/to/private/.env --suite followup \
  --max-requests 40 --output results/my-followup
```

To repeat all six follow-up cases ten times, add `--repeat 10` and use `--max-requests 260` with a new output directory. The [repeatability plan](REPEATABILITY-PLAN.md) and [review](results/claude-repeatability-04/REVIEW.md) describe that paid run.

`--suite reference_control` runs the one-case neutral-ID diagnostic. Original defaults remain `--suite pilot1`. Each completed hosted run includes a hash-verified `source/` snapshot to reproduce its precise code version. Later presentation examples are not part of earlier measured runs. Results can vary across repetitions.

Read the [follow-up protocol](FOLLOWUP-PLAN.md), [follow-up review](results/claude-followup-02/REVIEW.md) and [diagnostic review](results/claude-reference-control-03/REVIEW.md). The first pilot remains available with its original grades.

## Results

Each execution saves every model request and tool response, the raw answer, errors, elapsed time, provider-reported token usage, and structured assertions. An optional evidence gate is applied equally to both outputs and reported separately. It is not credited as an orchestration improvement.

The traces let you inspect:

- Can both paths provide the requested supported facts?
- When does the loop make additional useful or redundant requests?
- Does the bounded path clarify or abstain unnecessarily?
- Do facts change correctly when the fixture changes?

Read [METHODOLOGY.md](METHODOLOGY.md) before interpreting output. A `structured_pass` does **not** certify the prose or the whole answer. Human review remains necessary.

## Files

- [workflows.py](storelab/workflows.py): the two graphs and their shared instructions.
- [tools.py](storelab/tools.py): synthetic catalog/document tools with server-owned store scope.
- [fixtures.py](storelab/fixtures.py): thirty original cases, six follow-up cases and one diagnostic case.
- [evaluation.py](storelab/evaluation.py): explicit factual assertions and optional evidence gate.
- [models.py](storelab/models.py): local Ollama adapter and test double.
- [claude.py](storelab/claude.py): optional Anthropic adapter with credential isolation and a run-wide request cap.
- [run.py](storelab/run.py): paired runner, manifest, traces and summary.
- [test_lab.py](tests/test_lab.py): offline harness tests.
- [cards.py](storelab/cards.py): deterministic return-window wording.
- [presentation.py](storelab/presentation.py): complete price/policy reply using tool evidence, without model prose.
- [presentation_replay.py](storelab/presentation_replay.py): offline before/after replay with trace and source hashes.
- [test_presentation.py](tests/test_presentation.py): final-response regression and policy-state cases.

This is an educational experiment, not a commerce-platform SDK or a deployed store assistant. There is no live store authentication, inventory connection, checkout, refund, or order access.

## Related work

Planning retrieval to reduce model round trips already exists in [Amazon REAPER](https://www.amazon.science/publications/reaper-reasoning-based-retrieval-planning-for-complex-rag-systems). [DoorDash](https://careersatdoordash.com/blog/building-ask-doordash-part-5-a-grounded-interface-for-shopping-agents/) describes shopping interfaces grounded in commerce data. [MACS](https://arxiv.org/abs/2608.14068) combines language tasks with deterministic catalog constraints. [RAG mutation testing](https://arxiv.org/abs/2607.26843) already studies behavior when source information changes.

This lab provides an inspectable applied comparison and an example of a gap between checked fields and displayed prose. It does not claim those techniques as inventions.

## Licence

[MIT](LICENSE).
