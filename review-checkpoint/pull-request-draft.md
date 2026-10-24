Local draft only; not posted.

Title: fix(web): retry administrator loading in personal payer transfers

When administrator loading fails in Change who pays, the selected organisation
remains but there is no way to reload its administrators. Add a labelled retry
for that organisation, with separate discovery error/loading state and an immediate
request lock. Retry clears the old discovery error, handles repeated failures and
successful empty responses, and calls neither the quote nor transfer API.

Add nine component regression cases covering recovery, pending/duplicate requests,
selection reset, empty results and quote/submission error isolation. Preserve the
upstream organisation-list recovery flow and sponsored transfers.

Validation:

- Payer-transfer tests: 28 passed.
- TypeScript checks and production Vite build passed.
- Full configured web component suite: 272 passed, 1 failed. The existing 1 MiB
  Base64 test exceeded its 15-second limit; the same failure reproduced in isolation
  on clean upstream `de5a0e4`, with this repair removed. Its timeout and assertions
  are unchanged.
- The discovery record retains the original missing-retry failure and a negative
  control proving that the rapid-click regression detects removal of the lock.

Fixes #637.
