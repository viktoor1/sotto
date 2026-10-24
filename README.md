# Sotto #637 interactive investigation

Open **`interactive-walkthrough.html`** to explore the investigation. It is a self-contained HTML application: its styles, scripts, source excerpts, baseline evidence and selected journal checkpoints are embedded. It needs no npm installation or build step.

Contribution progress after that snapshot is recorded in [discovery-path.md](discovery-path.md), [task-journal.md](task-journal.md) and [activity.jsonl](activity.jsonl). The 24 October reproduction remains recorded as an expected failure against original production code. The contributor has reviewed and approved the repair; commit `e879c71` is signed off and pushed to the fork. Evidence publication and PR creation are in progress. [repair-review.md](repair-review.md) covers nine new regression cases and validation: 28 focused tests passed; TypeScript and build passed; the full web suite has one existing Base64 timeout reproduced on clean upstream. Earlier walkthrough validation reports remain unchanged and refer to their historical source snapshot.

If your browser blocks local file URLs, serve this folder:

```sh
python3 -m http.server 8763 --bind 127.0.0.1 --directory /workspace/scratch/sotto-637
```

Then open `http://127.0.0.1:8763/interactive-walkthrough.html` in the browser on that machine. If you downloaded only the HTML file, serve the directory containing it instead. Managed Chromium in this environment blocks `file://`, so validation used a local HTTP server.

## Explore

- Select a route, then click graph nodes or use **Back / Next**.
- **Current** shows exact checkout excerpts with real file line numbers.
- **Proposed** shows unapplied review excerpts. `P1`, `P2`, etc. are local excerpt numbers.
- **Diff** compares those excerpts using red removals and green additions. It is an explanatory comparison, not an apply-ready patch.
- The inspector highlights the selected expression and defaults to four surrounding lines. Click `… N unchanged lines` to open a context fold. Folds containing other changes show their addition/removal counts instead.
- **Expand full context** reveals the complete actual file in Current, or the full review excerpt in Proposed / Diff. Clicking the file path opens the complete actual source snapshot in any mode.
- Retained lines stay as context in Diff; proposed indentation is aligned for comparison. Existing organisation options are retained in the select-control example. The original illustrative snippets remain embedded unchanged.
- **Context / Evidence** traces the event, state transition and result. Expand evidence cards for recorded commands and outputs.
- **Journal** connects the selected step to recorded decisions and human review.
- Drag the graph to pan; use the wheel or `+`/`−` controls to zoom. **Fit** restores the full graph.
- **Copy** includes folded context without gutters. With full Current context expanded, it copies the complete source file. **Wrap** toggles soft wrapping.
- **Original analysis** contains the retained Markdown walkthrough.
- **Export evidence** downloads a task-specific JSON snapshot. Share the HTML itself for the complete interactive experience.

Keyboard: `←` / `→` step, `1` / `2` / `3` change views, `Home` / `End` jump to the first/last step, `F` fit, `+` / `−` zoom, `?` help, `Esc` close a dialog. Graph nodes and tabs also support keyboard focus.

Selection briefly traces the incoming edge, reveals the exact code highlight and animates previous → next state values. The sequence finishes within 295 ms, cancels on a new selection and respects the operating system's reduced-motion preference. Navigation brings the active code and graph node into view; **Fit** remains available for an overview.

## Evidence boundaries

- **OBSERVED:** source or journal evidence inspected directly.
- **INFERRED:** behaviour derived from code; not a new runtime reproduction.
- **PROPOSED:** unapplied code or planned behaviour.
- **VERIFIED:** a recorded baseline check with its stated scope.

The recorded baseline is **12 existing payer-transfer tests passed**, plus a successful TypeScript check. Administrator-retry regression coverage remains pending. This application illustrates the investigation; it does not run Sotto, apply the proposal, request a quote or start a transfer.

The animated state cards are explicitly labelled **INFERRED / PROPOSED STATE MODEL · ILLUSTRATIVE**. Their sample values explain the selected route; they are not captured runtime results.

`visual-walkthrough.md` is preserved. `task-journal.md` remains independent and includes the interactive-tool stage. The shareable HTML contains only selected issue-specific checkpoints, public source excerpts and the original issue-specific analysis. It contains no unrelated workspace logs, environment variables or credentials. It loads no external assets and makes no runtime API calls.

## Validation and maintenance

`validation-report.json` and `validation.log` preserve the previous browser validation unchanged. The refinement has its own **21 passing interface validation groups** in `refinement-validation-report.json` and `refinement-validation.log`, with `walkthrough-refined-desktop.png`, `walkthrough-refined-mobile.png` and `walkthrough-refined-embedded.png`. These results are separate from Sotto tests.

The pre-refinement artifacts and journal are archived under `history/before-focus-refinement-20261021-025128/`. The original analysis, source excerpts, proposal text, baseline output and recorded checkpoints remain preserved.

To rebuild from the retained proposal and the checked-out source:

```sh
python3 /workspace/scratch/sotto-637/build_walkthrough.py
```

To rerun the interface checks using the existing Playwright installation and system Chromium:

```sh
source /workspace/.setup/sotto-env.sh
node /workspace/scratch/sotto-637/validate-walkthrough.mjs > /workspace/scratch/sotto-637/refinement-validation.log 2>&1
```

The validation script starts and closes its own local static server. It checks source mapping and hashes, before/after diff reconstruction, original evidence preservation, folds/full context, exact expression highlights, state labels, interruptible motion, reduced motion, every route in all three modes, selection synchronization, keyboard navigation, copying, export, zoom/pan, reload persistence and responsive layouts. It checks for script errors and external requests. It does not run or modify Sotto application tests.

Authoring files are `walkthrough-template.html.in`, `focus-refinement.js`, `focus-refinement.css` and `build_walkthrough.py`. The builder embeds everything into the HTML; the generated file needs none of these companions at runtime.

The HTML is a snapshot of source commit `07f32e5cbdc758ddebfbc8a431302b93d2daa98a`. `evidence-manifest.json` records the source hashes. Rebuild and validate again when the contribution's source evidence changes.

## Preview compatibility

The authoring template is `walkthrough-template.html.in`; it is not a runnable page. Every `.html` file in this folder contains a fully built application. `walkthrough-template.html` is a generated compatibility copy for older preview tabs. Open `interactive-walkthrough.html` for the primary artifact.

The preview compatibility check validates every runnable HTML file and exercises the app inside an opaque-origin sandboxed iframe, including selection, view switching, keyboard navigation and copy/fallback behaviour. The original report retains 14 passing groups; the refinement report contains 21.

## Review and share the contribution

Start with `repair-review.md`, then inspect `solution.patch` and the two files in
`solution-files/`. `solution-manifest.json` records the current branch/base, file
hashes, validation results and linked command outputs. The local PR description
is in `pull-request-draft.md`; it has not been posted.

`/workspace/scratch/sotto-637-shareable.zip` packages this issue folder, including
historical walkthrough evidence, discovery/journal, captured activity and the
solution. `shareable-bundle-manifest.json` records file hashes and the ledger
cutoff. The bundle contains no user desktop screenshots or surrounding workspace
files. Early conversation stages remain historical summaries; raw commands are
captured from the resumed coding stage onward.

The live checkout already contains the repair. For another clean clone at
`de5a0e477ff70ff8dcd2493ce2d9dcb4e90fd757`, `git apply solution.patch` reconstructs
the reviewed change. Run `npm ci`, `npm run typecheck` and the recorded Vitest
commands from `web/` with a supported Node 22 runtime. The full suite's existing
Base64 timeout and its clean-upstream reproduction are documented, not hidden.

The contributor has completed review and approved submission. The signed-off
commit and push are complete. The remaining step is opening the PR with links
to this documentation; the contributor will write their own follow-up issue comment.
