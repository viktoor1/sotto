# Sotto #637: discovery and repair record

**Submission complete:** [PR #703](https://github.com/getsotto/sotto/pull/703) is open. The welcome workflow passed; main CI is awaiting maintainer approval. [Current submission record](PR-703.md). Earlier preparation/status paragraphs below are retained as the investigation record.

Status: review approved on 24 October 2026; repair committed with DCO sign-off as
`e879c71` and pushed to the contributor's fork. The evidence branch is published.
PR creation awaits the prefilled browser form in `OPEN-PR.md` after an API access
failure. The sections below preserve the original failing checkpoint;
[repair-review.md](repair-review.md) explains the final change and checks.

## Problem and source evidence

In `web/src/PayerTransferStart.tsx`, `PersonalTransferStart.chooseOrganisation`
(original source lines 101-113) clears the administrator choices before calling
`fetchMembers(orgId)`. A rejection sets the shared error and ends loading. The
selected organisation remains, but there are no administrator choices and the
review button is disabled. There is no retry control.

Original source snapshot: commit `07f32e5cbdc758ddebfbc8a431302b93d2daa98a`.
The [original analysis](visual-walkthrough.md) and
[interactive walkthrough](interactive-walkthrough.html) preserve the source
evidence and illustrative, unapplied proposal. Their recorded validation is
historical and separate from the new application regression below.

## Investigation path

1. Read the issue, contribution instructions, component, existing API mocks and
   organisation/member fixtures. The task journal records the original clean
   checkout and 12-test baseline, alongside a successful TypeScript check.
2. Trace organisation selection, dependency reset, asynchronous request, rejection
   and disabled review. Distinguish source observations from inferred behaviour.
3. Review a proposed recovery design: separate administrator error/loading state,
   a shared loader, an immediate request lock, and an explicitly labelled retry
   for the current organisation. Keep quote/submission errors separate.
4. Review the visual walkthrough with the human contributor. The contributor then
   requested continued implementation and a shareable activity/discovery record.
5. Recover the cloud connection after a platform executor timeout. Verify that the
   original source, journal, walkthrough and dependencies survived publication.
   See [cloud recovery evidence](cloud-recovery-20261024.md).
6. Add one regression to the existing payer-transfer test file, reusing its mocks
   and synthetic fixtures. Run it against the unchanged production component.

On 24 October, the public issue still showed OPEN with the same claim/assignment
discussion. Reviewed all 28 listed open PR titles across two pages; no obvious
administrator-discovery fix was identified. This title-level check does not
replace reviewing relevant PR changes or refreshing upstream before submission.

## Reproduction: expected failure observed

Command, from `web/` after activating the existing tool environment:

```sh
npm test -- --maxWorkers=1 src/__tests__/PayerTransferJourneys.test.tsx
```

Observed result: **12 existing tests passed; 1 new test failed**, exit code 1.
The failure is at the attempted retry:

```text
TestingLibraryElementError: Unable to find an accessible element with the role
"button" and name "Retry loading administrators"
```

Before that failure, the test verified the accessible service error, retained
`org-b` selection, blank administrator selection, disabled review button,
exactly one `fetchMembers("org-b")` request, and no quote/transfer requests.

The remaining assertions described the desired successful retry. They did not
execute on that failing run. They now pass after the repair. At that checkpoint,
the deferred-request tests for loading, overlap prevention, repeated failures,
empty results, selection changes and quote/submission error isolation were still
pending; their final results are in the repair review.

Full output:
[regression-before-repair.log](activity/20261024T131549557469Z-regression-before-repair.log).
The exact test patch and structured result are retained in
`stage-3-regression.patch` and `stage-3-reproduction.json`.

## Evidence and activity

- [Task journal](task-journal.md): decisions, failures, explanations and human checkpoints.
- [Activity ledger](activity.jsonl): timestamped command arguments, working directories,
  exit codes and links to complete captured outputs from the resumed coding stage.
- `activity/`: task-related command output and public issue/PR snapshots. Failed
  GitHub API reads are retained; successful public-page reads are recorded separately.
- Original onboarding and early walkthrough commands are summarised in the
  historical journal and their existing logs. They are not retroactively
  represented as newly captured raw commands.

The record uses synthetic test data and public issue source. It excludes unrelated
desktop activity, credentials and environment dumps. The shareable bundle
accompanies `solution.patch`, the final review and structured validation evidence.
The contributor approved submission after reviewing the repair and test limitation.
The pre-submission documents remain preserved under `review-checkpoint/`.
