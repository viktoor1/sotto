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
