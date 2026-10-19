All 120 runs of my store-assistant experiment passed the structured checks. Some answers still added a return-policy detail the source never supplied.

The source said seven days. The answers added “of purchase”, although nothing specified when the period began. The checks verified the duration and evidence reference without checking every claim in the displayed answer.

I repeated the same policy question ten times per workflow. The unsupported start appeared in 9 of 10 answers from the single-batch workflow and 4 of 10 from the loop. These are repeated synthetic inputs, not customer traffic or production failure rates.

I added a small renderer that writes the policy summary from verified fields and says when the start event is missing. Its regression test uses the saved tool response. It controls that summary; surrounding free-form prose still needs checking.

This came from a separate LangGraph experiment alongside my work on a multi-store Shopify assistant. The write-up includes the code, traces and the individual answer review.

The question I would carry into another project is which factual claims in the displayed answer are actually covered by its checks.
