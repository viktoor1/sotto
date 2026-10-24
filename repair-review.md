# Sotto #637: repair ready for review

**Submission complete:** [PR #703](https://github.com/getsotto/sotto/pull/703) is open. The welcome workflow passed; main CI is awaiting maintainer approval. [Current submission record](PR-703.md). Earlier preparation/status paragraphs below are retained as the investigation record.

The contributor approved this review and its documented test limitation on
24 October 2026. The repair is committed as `e879c71` with DCO sign-off and pushed
to the fork. The evidence is published separately; API access blocked PR creation,
so the prepared browser form awaits the contributor's final click. See `OPEN-PR.md`.
The only contribution changes are
`web/src/PayerTransferStart.tsx` and
`web/src/__tests__/PayerTransferJourneys.test.tsx`.

Branch: `fix/637-administrator-retry`.
Upstream base: `de5a0e477ff70ff8dcd2493ce2d9dcb4e90fd757`.

## 1. Reproduce before repairing

The original regression made `fetchMembers("org-b")` fail with a synthetic 503.
It confirmed the error, preserved organisation, empty administrator selection,
disabled review and absence of quote/transfer calls. It then failed because the
retry button was missing. The original run was **12 passed, 1 failed**, exit 1.
Its exact output and patch remain in the Stage 3 evidence.

This is the red part of a red/green workflow: demonstrate that the test catches
the real missing behaviour before relying on a passing result.

## 2. Separate selection from administrator loading

`chooseOrganisation` still resets values dependent on the selected organisation.
It also clears the old administrator error, then calls `loadMembers`. Retry calls
the loader directly with `destinationOrgId`, preserving the organisation rather
than running the selection reset again.

The actual guard and state updates in `PayerTransferStart.tsx`, lines 162-166:

```tsx
  async function loadMembers(orgId: string) {
    if (orgId === "" || membersInFlight.current) return;
    membersInFlight.current = true;
    setMembersLoading(true);
    setMembersError(null);
```

The ref changes immediately, before React renders a disabled button. Loading state
drives the UI. `finally` releases both on success and failure. The selection
handler also checks the ref before changing dependent state.

`membersError` belongs to member discovery. Existing `error` remains for quote and
submission failures. `formBusy = busy || membersLoading` disables the form during
either operation. The upstream organisation-list loader and sponsored-transfer
component remain unchanged by this contribution.

## 3. Give each result the right recovery state

| Administrator request | Visible result |
| --- | --- |
| Fails | Accessible error and enabled Retry loading administrators button |
| Retry starts | Old error cleared, loading button and form controls disabled |
| Fails again | Error and enabled retry return for the same organisation |
| Returns an owner/admin | Administrator choices return; retry/error disappear |
| Returns `[]` | No request error or retry; review stays disabled without an administrator |
| Organisation changes or is cleared | Recovery state from the old selection is cleared |
| Quote/submission fails | Existing error shown; no administrator retry offered |

Retry's handler is `onClick={() => void loadMembers(destinationOrgId)}`. The loader
calls `fetchMembers` only. Tests assert that retries call neither
`quotePayerTransfer` nor `beginPayerTransfer`.

## 4. Verify the repair and test quality

The new regression passed immediately after the repair: **13/13** tests on the
original checkout. Adding the recovery matrix produced **21/21**, comprising
the original 12 tests and nine new regression cases.

A negative control temporarily removed only the loader guard. The rapid-click
test failed because the mock received three calls rather than two. The exact
repair was restored. This proves that the test catches the request race, rather
than merely checking a disabled appearance.

Current upstream had added seven other payer-transfer tests and a deferred-promise
helper. Those were preserved and the existing helper reused. On the updated
branch the focused suite is **28/28**, including those upstream tests.

| Final check | Result |
| --- | --- |
| Payer-transfer suite | 28 passed |
| TypeScript, both configurations | Passed |
| Vite production build | Passed |
| Full configured web component suite | 272 passed, 1 failed |
| Failing full-suite case | Existing 1 MiB Base64 test exceeded its fixed 15-second limit |
| Same Base64 case on clean upstream | Same timeout reproduced with our changes removed |
| Patch application/reconstruction | Passed against the recorded upstream base |
| Whitespace/scope checks | Passed; only the two intended files differ |

The full web suite is not wholly green. The Base64 timeout reproduced in isolation
and with a clean upstream working tree, so competing TypeScript work alone does
not explain it and the #637 repair is not required for it to occur. Its underlying
performance cause remains unresolved. No assertion, timeout, dependency declaration
or Base64 source was changed for this contribution.

These are mocked component tests, static checks and a production build. They do
not establish a live account journey, real billing/provider behaviour or browser
integration results. The Vitest configuration selects `.test.tsx` component files;
this run does not claim the `.test.ts` suites executed.

## 5. Review and submission procedure

Review the component and the tests, or read `solution.patch` for the exact diff.
The patch applies to the upstream commit recorded above. The live checkout already
contains it. `solution-manifest.json` records source hashes and command evidence.

The contributor approved submission. The procedure is:

1. Create a signed-off commit. A commit records the reviewed changes in Git;
   DCO sign-off is the contributor's certification required by this repository.
2. Push that branch to `viktoor1/sotto`. Pushing uploads the branch to the fork.
3. Open a pull request to `getsotto/sotto`. A PR asks the maintainer to review and
   merge it; it is not a deployment. Include the full-suite timeout limitation.
4. Accompany the solution with the discovery summary and reviewed evidence bundle.

The signed-off commit, code push and evidence publication are complete. PR creation
is still pending because the API request returned Forbidden; `OPEN-PR.md` provides
the prefilled browser route.
The PR description is prepared locally. The historical interactive walkthrough
continues to show its original source snapshot and illustrative proposal; its old
verification labels have not been retroactively rewritten.
