# Sotto #637 contribution experiment

Started: 21 October 2026, Europe/Budapest.

Issue: https://github.com/getsotto/sotto/issues/637

Fork: https://github.com/viktoor1/sotto

This journal records the task's decisions, commands, results, failures, changes and user review checkpoints. Earlier conversation history is summarised below. New stages will be appended as they happen.

## Working agreement

- Work in small stages and explain the repair for a first-time contributor.
- Show proposed changes before editing the component.
- Demonstrate the regression test failing against the original code before repairing it.
- Keep the contribution within administrator discovery in `PersonalTransferStart`.
- Reuse the existing payer-transfer tests and synthetic fixtures.
- Keep this experiment's notes outside the contribution checkout.
- Do not push, post comments or open a pull request without the user's explicit approval after final review.
- Follow `CONTRIBUTING.md`, including British English and DCO sign-off when committing.

## Earlier environment preparation

The previous cloud onboarding prepared Rust, Node 22, Postgres 16, the React app and WASM tooling. It saved reusable installation and startup instructions. The final recorded validation was:

| Suite | Passed |
| --- | ---: |
| Native Rust | 565 |
| Python scripts | 381 |
| Frontend unit tests | 229 |
| Native/WASM compatibility | 8 |
| Browser integration | 29 |

These are historical setup results, not a new full-suite run for issue #637.

Relevant setup investigations were recorded in the previous conversation: the container needed an external child-process reaper for script tests, Binaryen was installed from a checksum-verified official archive, and a browser test was rerun after a concurrent production rebuild caused a temporary 404. The final onboarding checks passed and repository files were unchanged.

Retained setup instructions and logs are under `/workspace/.setup/`.

## Stage 1: checkout, issue and baseline checks

Recorded from the first walkthrough on 21 October 2026.

| Item | Observation |
| --- | --- |
| Checkout | `/workspace/sotto` |
| Local branch | `work` |
| HEAD | `07f32e5cbdc758ddebfbc8a431302b93d2daa98a` |
| Origin | `github.com/viktoor1/sotto.git` |
| Fork main | Same commit as the checkout when checked |
| Working tree | Clean: no tracked edits or untracked contribution files |
| Upstream main | `b802f1339e681af310758d87763b2e46024e97c3` when checked |
| Component upstream | `PayerTransferStart.tsx` matches the local file |
| Shared test file upstream | Contains newer, unrelated inbox tests to preserve when preparing the contribution branch |
| Tools | Node 22.23.3, npm 10.9.9, Rust 1.99.1, wasm-pack 0.15.0 |
| Frontend prerequisites | Installed dependencies and generated WASM bindings present |
| API readiness | Local `/health/ready` returned HTTP 200 and `ok` |
| Web/API proxy | Port 5173 `/server/info` returned HTTP 200 and self-hosted API JSON |

Existing checks run:

```sh
source /workspace/.setup/sotto-env.sh
cd /workspace/sotto/web
npm test -- --maxWorkers=1 src/__tests__/PayerTransferJourneys.test.tsx
npm run typecheck
```

Results: **12 existing tests passed; TypeScript checks passed.** The missing administrator-discovery regression has not been added yet. Baseline output: `/workspace/.setup/issue-637-baseline.log`.

Issue and overlap review:

- #637 is open and assigned to `viktoor1`.
- The user's existing comment volunteers to contribute and discloses AI assistance.
- The maintainer replied: "Sounds good, I've assigned it to you".
- No linked development PR or matching open fix was found during the review.
- Open PRs #650 and #651 concern other payer-transfer behaviour.
- GitHub CLI GraphQL access returned `Forbidden`; public GitHub pages provided the issue discussion and PR search results.
- This task has posted no comments or other external updates.

## Stage 2: current behaviour and proposed repair

The current `chooseOrganisation` clears the administrator selection, members and quote, then requests members. On failure it uses the shared quote/submission error state. The member list stays empty, the review button stays disabled and there is no retry control for the selected organisation.

Proposal presented to the user:

1. Add a separate administrator-loading error and loading state.
2. Extract `loadMembers(orgId)` so selection and retry share the same request path.
3. Add an immediate ref guard against overlapping member requests.
4. Keep the organisation unchanged during retry.
5. Show a labelled retry/loading control beside the accessible discovery error.
6. Preserve the existing quote/submission error path.
7. Treat an empty successful response as success.

The assistant paused before adding a regression test or editing production code. The user read the explanation and requested an experiment journal plus a more visual, coloured presentation of the snippets.

## Stage 2a: visual explanation and task logging

21 October 2026, 01:43 Europe/Budapest.

- Rechecked `git status --short --branch`: still clean on `work`.
- Created this journal and `visual-walkthrough.md` under `/workspace/scratch/sotto-637/`.
- The walkthrough uses coloured diff excerpts, a symbol legend and flow diagrams.
- The snippets are proposals for review; they have not been applied to the repository.
- No installation or test suite was repeated for this documentation step.

## Remaining stages

| Stage | Status |
| --- | --- |
| Prepare a focused contribution branch while preserving newer upstream work | Pending |
| Add regression coverage using existing fixtures and deferred promises | Pending |
| Observe the expected failure against the original component | Pending |
| Apply the focused repair and explain each change | Pending |
| Verify pending retry, repeated failure, success, empty success and selection changes | Pending |
| Verify quote/submission errors do not offer administrator retry | Pending |
| Verify retry calls neither quote nor transfer APIs | Pending |
| Run relevant checks and review the final diff together | Pending |
| Commit, push, comment or open a PR | No submission approval given |

## Future entry format

For each stage, append the user request, the change or decision, exact relevant commands, observed outcomes, evidence paths, any failure and its diagnosis, and the next review checkpoint. Keep proposed, applied and verified changes clearly labelled.


## Stage 2b: interactive investigation interface

21 October 2026, 02:09 CEST.

Request and scope:

- The user cancelled an incomplete prompt before implementation; that stop was honoured without file changes.
- The complete prompt authorised a self-contained interactive HTML investigation and interface validation.
- Sotto application source, application tests, Git commits, PRs and maintainer communication were outside this stage.

Delivered artifacts:

- `interactive-walkthrough.html`: one self-contained HTML file, with inline CSS/JavaScript and embedded task-specific evidence.
- `README.md`: usage, keyboard shortcuts, evidence boundaries and local-server instructions.
- `build_walkthrough.py` and `walkthrough-template.html`: reproducible authoring files outside the checkout.
- `evidence-manifest.json`: source commit and SHA-256 hashes for the inspected component, tests and API file.
- `validation-report.json`, `validation.log`, and desktop/mobile screenshots: interface validation evidence.
- The existing `visual-walkthrough.md` remains unchanged. This journal is preserved independently and extended by this entry.

Implemented interaction:

- Three responsive panels: Flow Graph, Code Inspector, Context / Evidence.
- Clickable connected nodes, seven routes and Current / Proposed / Diff views.
- Synchronized source excerpts, state traces, evidence badges and journal checkpoints.
- Back/Next, keyboard shortcuts, copy/wrap, zoom/pan, fit, selected-state restoration and task-specific evidence export.
- Proposed line numbers are marked P and never represented as repository line references.
- Mobile navigation focuses readable nodes; Fit still provides a complete graph overview.
- The original analysis is embedded for reference. The HTML includes only selected issue-specific journal checkpoints, not unrelated workspace logs or credentials.

Commands:

```sh
python3 /workspace/scratch/sotto-637/build_walkthrough.py
source /workspace/.setup/sotto-env.sh
node /workspace/scratch/sotto-637/validate-walkthrough.mjs
git -C /workspace/sotto status --short --branch
```

Observed obstacle and correction:

- Managed Chromium rejected direct `file://` navigation with `ERR_BLOCKED_BY_ADMINISTRATOR`.
- Validation used a temporary local HTTP server instead. No browser policy was disabled. The validator starts and closes its own server.
- Graph spacing and mobile focus were refined after visual inspection, then the interface checks were rerun.

Final interface validation: **12 validation groups passed** in Chromium 154.0.8037.57; zero script errors and zero external requests. Checks cover exact source/line mapping, every route and all three modes, synchronized state, copy, keyboard, zoom/pan/fit, retained analysis/journal checkpoints, export/reload and four responsive widths (1560, 1024, 768, 390 px).

This result validates the walkthrough interface. The previously recorded 12-test Sotto baseline remains historical; the administrator-retry regression test and production repair are still pending. The repository remains clean on `work`. No commits, pushes, PRs or external comments were made.

Human checkpoint: the interactive artifact is ready for review. The next contribution stage remains reproducing #637 with a failing component test.

Original journal prefix SHA-256 before this append: `cae359e37c3c35f26cce4f5041e8bed0f7fdea2dc95988417f22861c2ad75c45`.


## Stage 2c: repair the preview packaging

21 October 2026, 02:19 CEST.

- The user supplied a screenshot of the app preview error. Its selected tab was `walkthrough-template.html`.
- Inspection confirmed that this file contained the unresolved `__INVESTIGATION_DATA__` token and failed JSON parsing. The generated `interactive-walkthrough.html` had valid data for all 15 nodes. The previous interface validation had covered the generated page, but missed the previewable unbuilt template.
- Moved authoring source to `walkthrough-template.html.in`. Updated the builder so the old `.html` preview path becomes a fully generated compatibility copy, identical to the primary application. No runnable HTML file now contains the unresolved placeholder.
- Added validation of every previewable HTML file and the legacy tab path.
- Added a representative opaque-origin sandboxed iframe test: rendering, source/evidence synchronization, view switching, keyboard navigation and copy/manual fallback all pass. This is local embedded-browser evidence, not direct instrumentation of the user's ChatGPT preview host.
- Ran `python3 /workspace/scratch/sotto-637/build_walkthrough.py`, then `node /workspace/scratch/sotto-637/validate-walkthrough.mjs` with the existing workspace environment.
- Result: **14 interface validation groups passed**, zero script errors, zero external requests. Embedded screenshot: `walkthrough-embedded.png`.
- Sotto checkout remains clean. Original Markdown analysis is preserved; the journal continues independently. No Sotto repair or regression test was applied, and no submission action occurred.


## Stage 2d: human confirmation and direct browser inspection

21 October 2026, 02:21 CEST.

- The user confirmed that the interface works in their preview and supplied a screenshot showing the generated interactive walkthrough.
- Asked whether GPT can open and inspect it. Opened the saved HTML in local Chromium, selected **Load administrators / Diff**, exercised Next/Back and the Journal tab, and inspected a rendered screenshot.
- Source mapping: `web/src/PayerTransferStart.tsx`; function mapping: `PersonalTransferStart.chooseOrganisation → chooseOrganisation / loadMembers · proposal`. Next led to **GET organisation members**; 6 recorded journal checkpoints were visible; no script errors were observed.
- Evidence: `gpt-inspection.json` and `gpt-inspection.png`.
- The assistant inspected its browser instance of the saved artifact. The user's live preview selection and scroll state are not automatically mirrored into that instance.
- No application or walkthrough source was changed during this inspection. The contribution's regression test and repair remain pending.


## Stage 2e: refine the investigation for focused inspection

21 October 2026, 02:57 CEST.

- Human direction: refine the existing interface in place for minimal diffs, precise code focus, brief execution traces and smoother navigation. Preserve all evidence, routes, journal integration and offline operation; do not modify Sotto code or recorded test results.
- Archived the prior HTML, authoring template, builder, manifest, original analysis, validation report/log and journal under `history/before-focus-refinement-20261021-025128/` before refinement.
- Found that indentation differences between source and illustrative proposals made unchanged lines appear replaced. Aligned the presentation indentation before computing diffs. Preserved the original proposal text independently. The select example now retains actual existing options, as the original illustrative excerpt specified.
- Replaced full-block coloring with retained context, minimal line changes, inline change spans and exact-expression highlights. The default shows four surrounding lines. Context folds can be expanded individually; folds containing other changes state their addition/removal counts rather than calling them unchanged.
- Added full-context expansion, complete actual source snapshots with repository line numbers, auto-scroll to the active expression and copy including folded context. Proposed lines remain marked P and explicitly unapplied.
- Added interruptible selection motion: node emphasis, incoming-edge trace and code reveal. Individual animations last 170–200 ms; the final phase completes at 295 ms. Reduced-motion preference disables the execution animations. State cards show previous → next values and explicitly identify themselves as inferred/proposed illustrative models, not observed execution.
- Preserved all seven routes, Current / Proposed / Diff modes, source mappings, journal checkpoints, evidence labels, export, keyboard navigation and compatibility HTML path. Selected nodes remain readable and are brought into view; Fit still provides an overview.
- Authoring remains outside the checkout: `focus-refinement.js` and `focus-refinement.css` are embedded by `build_walkthrough.py`. The delivered HTML has no runtime dependencies or external assets.

Commands and recorded outputs:

```sh
python3 /workspace/scratch/sotto-637/build_walkthrough.py
source /workspace/.setup/sotto-env.sh
node /workspace/scratch/sotto-637/validate-walkthrough.mjs > /workspace/scratch/sotto-637/refinement-validation.log 2>&1
# 21 interface validation groups passed
git -C /workspace/sotto status --short --branch
# ## work
git -C /workspace/sotto diff --exit-code
# Exit 0; no repository changes
```

- During validation, corrected two stale test assumptions: an old scope-wording assertion and a check that implicitly depended on Current mode left by earlier checks. The final run explicitly establishes its view/route before the synchronization assertion.
- Final results: **21 interface validation groups passed**, zero script errors and zero external requests in local Chromium. Checks include real source/line mapping, diff reconstruction on both sides, original evidence preservation, folds/full source, expression highlights, state labels, animation timing/interruption, reduced motion, every route in all modes, keyboard, copy, export, zoom/pan/fit, reload persistence and four responsive widths.
- New results are stored in `refinement-validation-report.json` and `refinement-validation.log`; prior `validation-report.json` and `validation.log` were preserved. Reviewed `walkthrough-refined-desktop.png` and `walkthrough-refined-mobile.png` visually; sandbox evidence is `walkthrough-refined-embedded.png`.
- Verified original Markdown equality, archived journal-prefix integrity, source hashes against the checkout and identical generated primary/compatibility HTML files. Updated `README.md` with focus controls, evidence boundaries and refinement validation instructions.
- Sotto remains clean at `07f32e5`; historical baseline remains 12 existing tests passed. No Sotto tests were rerun or changed, no retry regression test or production repair was applied, and no commit, push, PR or external comment occurred.

Human checkpoint: the refined walkthrough is ready for review. The contribution's next stage remains the failing regression test after the user's review.

Original journal prefix SHA-256 before this append: `5af99c43b85a7ba0c6e57e4c37ba086ccc188944e6eeef02fe597700439f18f6`.


## Stage 3: cloud recovery and a failing regression

24 October 2026, Europe/Budapest. Exact command timestamps are in UTC in
`activity.jsonl`.

Human review and direction:

- The contributor reviewed the refined walkthrough, asked to continue towards a
  contribution, and requested that the discovery path and task activity accompany
  the solution. Submission still requires final review and explicit approval.
- The assistant said it would demonstrate the failing regression and pause at
  that checkpoint before changing production code.

Cloud recovery:

- The environment initially remained `starting`; shell probes returned
  `No usable execution environment is available`. It subsequently reported a
  failure querying executor configuration capabilities.
- Read the saved configuration successfully. Sotto install/start instructions
  were present; no pending runtime or secret requirements were declared. No
  configuration was changed by the assistant during this diagnosis.
- The original wait ended with `exec-server connection attempt failed:
  environment unavailable: timed out recovering environment readiness from ERS`.
- The contributor supplied screenshots. The assistant clarified that the
  configuration panel and setup-review badge were not runtime status indicators.
  `Needs attention 1` opened a setup-instruction review card. Earlier suggestions
  about a visible Ready badge or restart controls were unconfirmed and corrected.
- After the contributor completed review/publication, a screenshot showed
  `Environment published`. The next environment wait returned `ready`, and shell
  access succeeded. The underlying cause of the executor timeout remains unknown;
  recovery following publication does not establish a causal diagnosis.
- Verified clean branch `work`, unchanged HEAD `07f32e5`, matching original source
  hashes, retained walkthrough/journal/reports and installed frontend dependencies.
  Node remains 22.23.3; npm remains 10.9.9. No reinstall was performed.
- Root/repository/target-directory instruction-file checks found no applicable
  `AGENTS.md`. An initial broad search encountered unreadable Postgres/runtime
  directories and unrelated dependency instruction files; targeted checks then
  covered the actual edit paths. No configuration or repository membership
  discovery was attempted or inferred from that incomplete broad search.

Recording and contribution instructions:

- Added `record-command.py` outside the checkout. It records only explicitly run
  task commands, working directories, timestamps, exit codes and output files.
  It does not collect environment variables or credentials.
- Added `cloud-recovery-20261024.md` and `discovery-path.md` as shareable task
  narratives. Earlier stages remain historical summaries backed by existing logs;
  they are not misrepresented as new raw command capture.
- Re-read `CONTRIBUTING.md`: focused branch, existing tests, British English,
  current main before PR, required validation and DCO sign-off when committing.
  No commit or branch mutation has been performed.
- GitHub REST reads were rejected by the network proxy with HTTP 403. Retained
  those failures and used read-only public GitHub pages instead. The issue page
  returned HTTP 200 and still showed issue #637 open, with the contributor's
  original claim and the maintainer's assignment response. No new comment was
  posted. Public PR-page checks and pagination results are retained in activity
  outputs rather than inferring absence of a fix from an API failure.
- Reviewed all 28 currently listed open PR titles across two nonempty public
  pages. None explicitly mentions #637 or administrator discovery; related payer
  titles cover other flows. This is a title-level overlap check, not an audit of
  every PR diff, and must be refreshed before submission.
- The exploratory pagination command followed disabled next links beyond the
  final nonempty page and stopped at its configured bound. Diagnosed that mistake
  from saved pages, then explicitly reviewed the 25 + 3 PRs on pages 1 and 2.
  Both the failed exploration and the completed title review remain logged.

Regression added:

- File: `web/src/__tests__/PayerTransferJourneys.test.tsx`.
- Test: `retries administrator loading for the selected organisation without
  starting a transfer`.
- Reuses the existing API mocks, organisation `org-b`, and owner `admin-2`.
  Rejects the first members request with `Error("server error (503)")`; the
  existing default fixture would resolve the next request successfully.
- Before retry, verifies the accessible service error, preserved organisation,
  blank administrator selection, disabled review, one members request and no
  quote/transfer calls. Then attempts the desired labelled retry.
- Post-retry assertions specify returned administrator choices, removed recovery
  feedback and review enabled only after choosing an administrator. These latter
  assertions did not execute because the retry control is absent.

Command and result:

```sh
source /workspace/.setup/sotto-env.sh
cd /workspace/sotto/web
npm test -- --maxWorkers=1 src/__tests__/PayerTransferJourneys.test.tsx
# Exit 1: 1 failed | 12 passed (13)
# Unable to find an accessible element with the role "button" and name
# "Retry loading administrators"
```

Full output: `activity/20261024T131549557469Z-regression-before-repair.log`.
Duration: 1.37 seconds. This is an observed component regression using mocked
APIs, not a live browser or account test.

- `git diff --check` passed. `git diff --exit-code --
  web/src/PayerTransferStart.tsx` passed: production code remains unchanged.
- The only repository edit is the new regression test. Original walkthrough
  evidence, existing test results and historical baseline logs remain preserved.
- Deferred loading, duplicate prevention, repeated rejection, empty success,
  selection reset and quote/submission-isolation coverage remain pending.
- No quote, transfer or payment request was made against live services. No commit,
  push, PR, external comment or maintainer contact occurred.

Human checkpoint: the regression fails for the expected missing-retry reason.
The next small stage is applying the reviewed production repair and extending the
recovery tests. No recovery behaviour is claimed as verified yet.

Original journal prefix SHA-256 before this append:
`96b65f74be007a9d1ea804eb1d530c3f64ba81b4a1bd342dede0ef8ab5aef5c0`.


## Stage 4: focused repair, recovery coverage and current upstream

24 October 2026, Europe/Budapest. UTC command timestamps and complete outputs are
in `activity.jsonl` and `activity/`.

Human direction: the contributor approved proceeding with the repair and asked
for guidance after each step. Final submission still requires their review and
explicit approval. The assistant provided progress explanations of the red/green
test cycle, deferred promises, immediate request locking, fetching, branching and
the eventual commit/push/PR procedure.

Repair applied:

- Added `membersError`, `membersLoading`, `membersInFlight` and `formBusy` inside
  `PersonalTransferStart` only. Kept quote/submission errors in existing `error`.
- Kept selection-reset work in `chooseOrganisation`, clearing old discovery
  errors and refusing selection changes while discovery is in flight.
- Added shared `loadMembers(orgId)`. It rejects blank/overlapping attempts, sets
  the ref before asynchronous work, clears the old error, calls `fetchMembers`,
  reports discovery errors and releases the lock/loading state in `finally`.
- Added the labelled retry/loading button. Retry passes the selected organisation
  directly to the loader and does not reset selection, request a quote or start
  a transfer. Existing controls disable during discovery or quote/submission work.
- A successful empty result removes recovery feedback and leaves review disabled
  without a selected administrator, rather than presenting a request failure.

Red/green and recovery checks on the original base:

- Ran the original failing regression after the repair: **13 passed**, exit 0.
- Added pending/rapid-click, repeated-failure/recovery, initial/retry empty result,
  change/clear selection and quote/submission error-isolation cases. Reused the
  existing synthetic organisation/member fixtures and the deferred-promise pattern
  from other repository tests. Result: **21 passed**, exit 0; nine added cases in
  total compared with the original twelve.
- Ran a controlled negative check: temporarily removed only the loader overlap
  guard. The rapid-click regression failed with three calls instead of two,
  proving that it catches the race. Its runner reported exit 1 with twenty other
  tests skipped. The supervising diagnostic succeeded because this was the expected
  failure, and restored the exact production source. See `request-lock-probe.json`.

Current-main preparation:

- Fetched upstream main without changing working files. Its current commit was
  `de5a0e477ff70ff8dcd2493ce2d9dcb4e90fd757`.
- Upstream had added initial organisation-list recovery to this component and
  seven payer-transfer tests, plus a deferred helper. Those changes address a
  different request from #637. The original member-selection loader was unchanged.
- Before switching bases, verified recoverable copies of both edited files and
  the full binary-capable diff in `before-upstream-update-20261024T132424Z/`.
- Created local branch `fix/637-administrator-retry` from current upstream, leaving
  `work` at `07f32e5`. Carried over only this repair and its nine tests. Reused the
  upstream helper rather than adding a duplicate. No contribution commit exists.
- Upstream changed Vite/Vitest dependency versions. Refreshed only web dependencies
  with lockfile-preserving `npm ci`, which installed 117 packages in five seconds.
  Node remained 22.23.3; the current test runner is Vitest 5.0.5. The contribution
  itself changes no dependency declaration or lockfile.
- Verified that sponsored transfers and upstream `loadInitial`/its effect remain
  byte-identical to the upstream base. Only the component and payer-transfer test
  file differ. Diff: 212 insertions, 8 deletions across those two files.

Final checks and the diagnosed wider-suite limitation:

| Check | Observed result |
| --- | --- |
| Final payer-transfer tests, current base | 28 passed, exit 0 |
| TypeScript, app and Node configurations | Passed, exit 0 |
| Production Vite build | Passed, exit 0; Vite 6.4.5 |
| Full configured component suite | 272 passed, 1 failed; 27 files passed, 1 failed; exit 1 |
| Isolated failing Base64 file | 8 passed, 1 timeout; exit 1 |
| Same file with clean upstream working tree | 8 passed, same timeout; runner exit 1 |
| Patch application and byte reconstruction | Passed |
| Whitespace and contribution-scope checks | Passed |

- The full-suite failure is the existing 1 MiB Base64 test exceeding its explicit
  15-second limit. The first run overlapped TypeScript checking. The assistant
  tested a possible contention explanation, but the isolated run also timed out,
  so concurrency alone was not established as the cause.
- For a stronger baseline, backed up the repair, restored both files to upstream
  HEAD, verified the working tree was clean, and reran the Base64 file. The same
  timeout reproduced. Restored the exact repair bytes and then reran the focused
  payer-transfer suite, which passed all 28 tests in 1.12 seconds. The underlying
  performance cause remains unresolved. See `upstream-baseline-probe.json`.
- No Base64 code, assertion, timeout, test selection or dependency declaration was
  changed to hide that result. The full web run is explicitly not wholly green.
- The Vite build used the existing generated WASM bindings and
  `VITE_STATUS_URL=https://status.example.test`, the established local build fixture.
  It completed in 1.47 seconds. No live billing/provider/browser journey was run.
- The configured Vitest include selects `.test.tsx` component files; these results
  do not claim the `.test.ts` suites, Rust suites or browser integrations ran.

Review and shareable evidence:

- Saved `solution.patch` against the current upstream base. Applied it in a
  temporary directory containing the two original upstream files and verified
  it reconstructed the actual edited files byte-for-byte.
- Added `repair-review.md` to guide review in small steps and explain remaining
  limitations, and a local `pull-request-draft.md` with the actual final scope and
  validation results. Neither has been posted.
- Updated the discovery index and README with current progress. One documentation
  patch initially failed to match its context, made no changes, and was reapplied
  with the correct context. This did not affect repository source.
- Preserved the original Markdown analysis, interactive HTML, historical manifests
  and prior validation results as snapshots of their original commit. They were
  not relabelled as fresh verification of the repaired branch.
- Preparing the shareable archive from task-specific records only: discovery path,
  journal, command/output ledger, original and final patches, relevant public source
  evidence and generated walkthrough artifacts. User desktop screenshots and
  unrelated private activity are not included.

Human checkpoint: review the two-file repair, its regression cases and the explicit
Base64 baseline limitation. No commit, sign-off, push, pull request, external comment
or maintainer contact has occurred. After approval, the next steps are DCO-signed
commit, push to the fork and a PR with the reviewed evidence.

Packaging result: created and verified
`/workspace/scratch/sotto-637-shareable.zip` from this task folder. It includes the
review, exact solution patch/source snapshots, discovery narrative, journal,
captured command outputs, original red result, recovery checks, negative control,
upstream-baseline timeout evidence and historical walkthrough artifacts. ZIP
integrity and byte equality were checked. The archive is regenerated after this
entry so its journal and ledger include the packaging checkpoint; its manifest
states the exact activity-record cutoff. Creating a local archive did not upload it.


## Stage 5: approved submission and accompanying investigation records

24 October 2026, Europe/Budapest. This entry is appended after final human review.

- The contributor read the repair review, asked about the full-suite limitation,
  received an explanation of the unchanged-upstream Base64 timeout, then explicitly
  said to proceed. They also requested inclusion of the interactive HTML (interpreting
  their word `hatl` in context), discovery path and surrounding documentation, and
  said they would write their own follow-up issue comment. No issue comment is
  being posted by the assistant.
- Rechecked reviewed source hashes, clean staged index, exact two-file scope, Git
  identity, unused remote branch name and unchanged upstream main. All passed.
- Created commit `e879c71f0e5a5d1b9e3d1219a89f80e7c5c040b8` with the configured
  contributor identity and required DCO sign-off. The commit contains only the
  component repair and its nine regression cases: 212 insertions, 8 deletions.
- Pushed `fix/637-administrator-retry` to `viktoor1/sotto`; verified the remote
  branch points at that exact commit. Local working tree is clean. Upstream main
  remained `de5a0e477ff70ff8dcd2493ce2d9dcb4e90fd757` at submission preflight.
- Preserved the pre-submission review documents under `review-checkpoint/` before
  updating the current status pages. Historical tests, walkthrough and journal
  entries remain unchanged.
- A GitHub API permission probe (`gh api user`) returned `Forbidden`. CLI auth
  status alone also reported an unusable token, but that does not establish that
  proxy-backed Git credentials are missing: native Git read and push succeeded.
  No credential values were inspected, copied or requested. No network policy or
  authentication configuration has been changed during this stage.
- Prepared `pr-body.md` with the verified test results, explicit Base64 limitation,
  issue linkage and documentation links. Publishing the investigation separately
  on `evidence/637-investigation` keeps the application PR focused on two files.
  PR creation will be attempted after the linked records are accessible.
- The first evidence-publication attempt stopped before committing because a
  whitespace check was applied to raw downloaded HTML, captured logs and patch
  files, whose exact whitespace is part of the evidence. Preserved those bytes
  and scoped the documentation check to authored entry pages and the publisher.
  The application contribution had already passed its own full diff check.
