In a store-assistant experiment, an unsupported purchase start date appeared in 13 of 20 answers to the same return-policy question. All twenty passed the structured checks.

The source said seven days. The answers added “of purchase”, although nothing specified when the period began. The checks verified the duration and evidence reference without checking every claim in the displayed answer.

These were repeated synthetic inputs across two workflows, not customer traffic or a production failure rate. The article includes the per-workflow counts and their limitations.

I added a small renderer that writes the policy summary from verified fields and says when the start event is missing. Its regression test uses the saved tool response. It controls that summary; surrounding free-form prose still needs checking.

This came from a separate LangGraph experiment alongside my work on a multi-store Shopify assistant. The write-up includes the code, traces and answer assessments recorded by Codex.

Which factual claims in your assistant's displayed answer are actually covered by its checks?
