A return-policy answer passed my automated checks even though it added a condition the policy never stated.

This came from a LangGraph experiment alongside my work on a multi-store AI assistant. I was comparing two workflows using fictional store data.

One question asked for an item's price and how many days the customer had to return it. The retrieved policy supplied seven days. Several answers said "within 7 days of purchase".

The policy never said when those seven days began. Purchase and delivery can give a customer different deadlines.

The checks passed because they matched the seven-day value to the source. They didn't check the extra claim in the sentence. In twenty repetitions of this question across two workflows, thirteen answers added "of purchase".

For this price-and-policy reply, I used ordinary code to generate the whole answer from the retrieved fields. When the start is missing, the reply says: “The retrieved details do not specify when that period begins.” Showing a correct policy summary beside the original model answer would still leave the unsupported sentence on screen.

I replayed all twenty saved tool results through that code. Separate tests cover policies that explicitly start at purchase or delivery, conflicting records, and failed retrieval.

I've written up the example with the code and saved answers so others can inspect both the failure and the fix.
