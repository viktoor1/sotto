When administrator loading fails in Change who pays, the organisation stays selected
but there is no way to reload its administrators. Add a labelled retry for that
organisation, with separate discovery error/loading state and an immediate request
lock. Retry clears the old discovery error and calls neither the quote nor transfer API.

Add nine regression cases covering recovery, pending/duplicate requests, repeated
failure, empty results, selection reset and quote/submission error isolation. Preserve
the upstream organisation-list recovery flow and sponsored transfers.

Validation:

- Payer-transfer component suite: **28 passed**.
- TypeScript checks and production Vite build passed.
- Full configured web component suite: **272 passed, 1 failed**. The existing 1 MiB
  Base64 test exceeded its 15-second limit; the same timeout reproduced in isolation
  on clean upstream `de5a0e4`, with this repair removed. Its timeout and assertions
  are unchanged.

Investigation documentation is available separately from the focused code diff:

- [Discovery path and repair review](https://github.com/viktoor1/sotto/blob/evidence/637-investigation/repair-review.md)
- [Interactive HTML walkthrough](https://github.com/viktoor1/sotto/blob/evidence/637-investigation/interactive-walkthrough.html) - download and open locally; this preserves the original investigation snapshot and proposed-code labels.
- [Task journal and recorded activity](https://github.com/viktoor1/sotto/blob/evidence/637-investigation/task-journal.md)
- [Download the complete evidence branch](https://github.com/viktoor1/sotto/archive/refs/heads/evidence/637-investigation.zip)

The records retain the original missing-retry failure, the successful recovery
tests, a negative control demonstrating the duplicate-request check, and the
unchanged-upstream timeout evidence.

Fixes #637.
