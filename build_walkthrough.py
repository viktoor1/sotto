#!/usr/bin/env python3
"""Build the offline investigation from real source and the retained proposal."""
import difflib
import hashlib
import json
import re
import subprocess
import textwrap
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
REPO = Path('/workspace/sotto')
COMPONENT = 'web/src/PayerTransferStart.tsx'
TESTS = 'web/src/__tests__/PayerTransferJourneys.test.tsx'
API = 'web/src/api.ts'
notes = (ROOT / 'visual-walkthrough.md').read_text()
journal = (ROOT / 'task-journal.md').read_text()
baseline_path = Path('/workspace/.setup/issue-637-baseline.log')
baseline = baseline_path.read_text()
files = {name: (REPO / name).read_text() for name in (COMPONENT, TESTS, API)}
commit = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()


def excerpt(path, start, end, function):
    lines = files[path].splitlines()[start - 1:end]
    assert len(lines) == end - start + 1
    return dict(path=path, start=start, end=end, function=function, text='\n'.join(lines))


def proposal(text, function):
    return dict(path=COMPONENT, start=None, end=None, function=function, text=text.strip('\n'))


fences = re.findall(r'```diff\n(.*?)\n```', notes, re.S)
helper_diff = next(block for block in fences if block.startswith('+async function loadMembers'))
helper = '\n'.join(line[1:] for line in helper_diff.splitlines())
selection_diff = next(block for block in fences if 'async function chooseOrganisation' in block)
selection = '\n'.join(line[1:] for line in selection_diff.splitlines() if not line.startswith('-'))
render_diff = next(block for block in fences if block.startswith('+{membersError'))
rendering = '\n'.join(line[1:] for line in render_diff.splitlines())
state_diff = next(block for block in fences if 'const [membersError' in block)
state = '\n'.join(line[1:] for line in state_diff.splitlines())

checkpoints = [
    dict(id='inspection', title='Checkout and source inspection', when='21 Oct 2026 · stage 1', status='OBSERVED',
         detail='Clean checkout on work at 07f32e5. Component matches the upstream snapshot inspected in stage 1.',
         command='git status --short --branch\ngit rev-parse HEAD', output='## work\n07f32e5cbdc758ddebfbc8a431302b93d2daa98a', anchor='Stage 1'),
    dict(id='baseline', title='Existing payer-transfer baseline', when='21 Oct 2026 · recorded baseline', status='VERIFIED',
         detail='12 existing component tests passed. This result does not cover the missing retry path.',
         command='npm test -- --maxWorkers=1 src/__tests__/PayerTransferJourneys.test.tsx',
         output='Test Files  1 passed (1)\nTests       12 passed (12)\nDuration    1.25s', anchor='Stage 1'),
    dict(id='types', title='TypeScript baseline', when='21 Oct 2026 · stage 1', status='VERIFIED',
         detail='The recorded npm run typecheck command completed successfully before any repair.',
         command='npm run typecheck', output='tsc -p tsconfig.json && tsc -p tsconfig.node.json\nExit status: 0 (recorded)', anchor='Stage 1'),
    dict(id='review', title='Human review checkpoint', when='21 Oct 2026 · stages 2 / 2a', status='OBSERVED',
         detail='The contributor read the proposal and requested visual diffs and a task journal. Production code and regression tests remain unchanged.',
         command=None, output='Review-first workflow retained. No submission approval recorded.', anchor='Stage 2 / Stage 2a'),
    dict(id='proposal', title='Focused recovery proposal', when='21 Oct 2026 · stage 2', status='PROPOSED',
         detail='Separate discovery state, a guarded shared loader and a labelled retry control. The snippets are retained from visual-walkthrough.md.',
         command=None, output='Not applied. Not regression-tested.', anchor='Stage 2'),
    dict(id='regression', title='Reproduce before repairing', when='Next contribution stage', status='PROPOSED',
         detail='Use the existing organisation/member fixtures and deferred promises. Observe the missing retry control failing against the original component first.',
         command=None, output='Pending: no new regression test has been written or executed.', anchor='Remaining stages'),
]


def node(id, title, subtitle, kind, current, proposed, explanation, event, transition, result, evidence, checkpoints_, highlights=(), proposed_only=False):
    return dict(id=id, title=title, subtitle=subtitle, kind=kind, current=current, proposed=proposed,
                explanation=explanation, event=event, transition=transition, result=result,
                evidence=evidence, checkpoints=checkpoints_, highlights=list(highlights), proposedOnly=proposed_only)


nodes = [
    node('select', 'Choose an organisation', 'UI event · onChange', 'neutral', excerpt(COMPONENT,158,163,'PersonalTransferStart · organisation select'),
         proposal('<select value={destinationOrgId}\n  onChange={(event) => void chooseOrganisation(event.target.value)}\n  disabled={formBusy}>\n  {/* Existing organisation options are retained. */}\n</select>', 'PersonalTransferStart · proposed select excerpt'),
         'The organisation selector passes its new value into chooseOrganisation. The proposal keeps this event and uses a combined loading flag to disable the form during discovery.',
         'Change Organisation to org-b', 'destinationOrgId will be set by chooseOrganisation', 'The same selection handler is entered.', 'OBSERVED', ['inspection','review'], [159]),
    node('reset', 'Reset dependent state', 'State transition · selection', 'neutral', excerpt(COMPONENT,101,107,'PersonalTransferStart.chooseOrganisation'),
         proposal(selection, 'PersonalTransferStart.chooseOrganisation · proposal'),
         'Changing the organisation clears the previous administrator, members, quote and shared error. The proposal also clears the old discovery error and refuses a selection change while a members request is already in flight.',
         'chooseOrganisation("org-b")', 'counterpartyId=""; members=[]; quote=null', 'No administrator from the previous organisation remains selected.', 'OBSERVED', ['inspection','proposal'], [102,103,104,105,106,107]),
    node('request', 'Load administrators', 'Async boundary · fetchMembers', 'pending', excerpt(COMPONENT,108,112,'PersonalTransferStart.chooseOrganisation'),
         proposal(helper, 'loadMembers · proposed helper'),
         'The current handler awaits fetchMembers and uses busy for loading. The proposed helper awaits the same API, tracks discovery loading separately and acquires a ref lock before starting the request.',
         'fetchMembers(orgId)', 'Current: busy=true. Proposed: membersLoading=true; lock=true.', 'The form waits for an asynchronous result.', 'OBSERVED', ['inspection','proposal'], [108,110]),
    node('error', 'Administrator request fails', 'Failure branch · catch', 'failure', excerpt(COMPONENT,108,112,'PersonalTransferStart.chooseOrganisation'),
         proposal(helper, 'loadMembers · proposed error handling'),
         'The catch reports the failure through the shared error state. Because the list was already cleared, it stays empty. This path is inferred from the code and described in the issue; a new local regression reproduction remains pending.',
         'The members promise rejects', 'Current: error=message(e); busy=false; members=[].', 'An accessible error appears. The proposal would store it in membersError instead.', 'INFERRED', ['inspection','proposal','regression'], [111,112]),
    node('blocked', 'No way to retry', 'Observable result · blocked form', 'failure', excerpt(COMPONENT,164,168,'PersonalTransferStart · error and review controls'),
         proposal(rendering, 'PersonalTransferStart · proposed recovery controls'),
         'With no administrator selected, Review payer transfer remains disabled. The existing JSX offers no administrator retry action. Clearing and reselecting the organisation is the indirect workaround described in #637.',
         'The failed request has settled', 'counterpartyId=""; members=[]; selected organisation retained', 'Review is disabled, and no explicit retry control exists.', 'INFERRED', ['inspection','regression'], [164,165,168]),
    node('retry', 'Retry the same organisation', 'Proposed UI event · retry', 'recovery', excerpt(COMPONENT,164,168,'PersonalTransferStart · existing controls'),
         proposal(rendering, 'PersonalTransferStart · proposed retry control'),
         'A labelled button calls loadMembers(destinationOrgId). It uses the existing organisation ID instead of changing the selection or rerunning the selection-reset handler. This recovery control is not in the checkout.',
         'Click Retry loading administrators', 'destinationOrgId remains org-b', 'Only the members API is requested; the error is cleared for the new attempt.', 'PROPOSED', ['proposal','review','regression'], [], True),
    node('pending', 'Wait with an immediate lock', 'Proposed async state · one request', 'pending', excerpt(COMPONENT,108,112,'PersonalTransferStart · existing loading handling'),
         proposal(helper, 'loadMembers · proposed in-flight guard'),
         'The ref is checked and set synchronously, before awaiting the API. React loading state keeps the control visible but disabled after the old error is cleared. finally releases the lock whether the attempt succeeds or fails.',
         'A retry is pending; a second attempt is made', 'membersInFlight=true; membersLoading=true; membersError=null', 'The guard returns before a duplicate members request can start. This behaviour still needs regression tests.', 'PROPOSED', ['proposal','regression'], [], True),
    node('success', 'Members become available', 'Response branch · owner/admin', 'recovery', excerpt(COMPONENT,62,68,'CounterpartySelect'),
         proposal('setMembers(await fetchMembers(orgId));\n// CounterpartySelect keeps its existing owner/admin filtering.\n// finally clears membersLoading; membersError remains null.', 'loadMembers · proposed success excerpt'),
         'The existing selector filters members to eligible owners/admins. The recorded happy-path test returns admin-2 as an owner. A successful retry would reuse that same selector and remove the recovery feedback.',
         'The members promise resolves with the existing owner fixture', 'members contains admin-2; no discovery error', 'Eligible administrator choices appear. Retry-specific success is still proposed.', 'VERIFIED', ['baseline','proposal','regression'], [62,63,67,68]),
    node('empty', 'An empty response is success', 'Response branch · empty array', 'recovery', excerpt(COMPONENT,62,68,'CounterpartySelect'),
         proposal(helper, 'loadMembers · proposed empty-success handling'),
         'Resolving with [] follows the successful try path, not catch. The proposal clears loading and leaves membersError null, removing the recovery control. The administrator selector remains empty, so review stays unavailable. This acceptance case has not been tested yet.',
         'fetchMembers resolves with []', 'members=[]; membersError=null; membersLoading=false', 'No failure message or retry control is shown for a successful empty response.', 'PROPOSED', ['proposal','regression'], [63,66]),
    node('review', 'Review remains an explicit action', 'Existing flow · quote then submit', 'neutral', excerpt(TESTS,143,158,'existing personal payer happy-path test'),
         proposal('onClick={() => void requestQuote()}\n// Retry continues to call loadMembers(destinationOrgId).\n// Only the existing review action calls quotePayerTransfer.', 'PersonalTransferStart · proposed separation of actions'),
         'The existing test selects admin-2, clicks Review payer transfer, then explicitly sends a request. Its successful result is recorded in the 12-test baseline. Retrying discovery must never perform either of those later actions.',
         'Select admin-2, then click Review payer transfer', 'counterpartyId="admin-2"; review can become enabled', 'A quote is requested only through the existing review handler.', 'VERIFIED', ['baseline','regression'], [145,146,147,149,150,156]),
    node('selection', 'Change or clear the organisation', 'Selection branch · reset recovery', 'neutral', excerpt(COMPONENT,101,107,'PersonalTransferStart.chooseOrganisation'),
         proposal(selection, 'PersonalTransferStart.chooseOrganisation · proposal'),
         'The existing handler clears selection-dependent values and stops before requesting members for a blank organisation. The proposal additionally clears the old discovery error. While discovery is pending, the disabled selector and immediate guard prevent an overlapping selection request.',
         'Choose another organisation, or choose the blank option', 'Old members, administrator, quote and discovery error cleared', 'The old recovery state does not follow the user into a different organisation.', 'PROPOSED', ['inspection','proposal','regression'], [102,103,104,105,106,107]),
    node('isolation', 'Keep failure domains separate', 'Boundary · discovery / quote / submit', 'neutral', excerpt(COMPONENT,115,151,'requestQuote / createInvitation'),
         proposal(state+'\n\n'+rendering, 'PersonalTransferStart · proposed separate error state'),
         'requestQuote and createInvitation continue to use error. Only administrator discovery uses membersError and can expose the new retry control. No transfer authority, billing rule, server API or sponsored-transfer repair is proposed.',
         'A quote or submission request fails', 'error changes; membersError does not become a discovery failure', 'Quote/submission errors do not offer the wrong administrator retry action.', 'PROPOSED', ['proposal','regression'], [126,127,144,145]),
    node('tests', 'Reuse the existing evidence', 'Recorded baseline · 12 tests passed', 'neutral', excerpt(TESTS,65,84,'org / member fixtures and beforeEach'),
         proposal('// Planned test work: reuse org("org-b") and member("admin-2", "owner").\n// Control fetchMembers with deferred promises to inspect pending retry state.\n// No new regression test has been written or executed.', 'PayerTransferJourneys.test.tsx · test plan'),
         'The existing file mocks the API and provides synthetic organisation/member fixtures. Its 12 passing tests are baseline evidence, not proof of a repair. New tests must first expose the missing control against unchanged production code.',
         'Read the recorded focused test output', 'Existing synthetic fixtures and mocks are available', '12 existing tests passed in 1.25s; TypeScript checks also passed in stage 1.', 'VERIFIED', ['baseline','types','review'], [65,69,74,79,80]),
    node('coverage', 'Prove the missing cases next', 'Pending · regression coverage', 'pending', excerpt(TESTS,143,158,'existing happy-path coverage'),
         proposal('// Pending assertions, not an executable test:\n// 1. Initial rejection exposes Retry loading administrators.\n// 2. A deferred retry clears the old error and blocks duplicate requests.\n// 3. Rejection again restores recovery; resolution restores owner choices.\n// 4. Empty success and organisation changes clear recovery state.\n// 5. Retry calls neither quotePayerTransfer nor beginPayerTransfer.\n// 6. Quote/submission failures never expose administrator retry.', 'PayerTransferJourneys.test.tsx · pending acceptance matrix'),
         'The contribution is paused before regression work. The next code stage is to add the missing tests, observe an expected failure against the original component, then apply the focused repair. This interface does not execute Sotto or apply the proposal.',
         'Future regression-test stage', 'New regression tests=0; repair applied=false', 'The required failure/recovery cases remain unverified.', 'PROPOSED', ['regression','review'], []),
]

# Align comparisons to the same function/JSX region. A review excerpt must not
# suggest removing unrelated controls, fixtures or quote/submission handlers.
by_id = {item['id']: item for item in nodes}
controls = excerpt(COMPONENT, 164, 168, 'PersonalTransferStart · administrator and review controls')
controls_after = controls['text'].replace('disabled={busy}', 'disabled={formBusy}').replace(
    'disabled={busy || destinationOrgId', 'disabled={formBusy || destinationOrgId')
controls_after = controls_after.replace('    {error !== null && <p role="alert">{error}</p>}',
                                       '\n'.join('    '+line for line in rendering.splitlines()))
for id in ['blocked', 'retry', 'review']:
    by_id[id]['current'] = controls
    by_id[id]['proposed'] = proposal(controls_after, 'PersonalTransferStart · proposed recovery controls')
    by_id[id]['highlights'] = [164,165,168]
for id in ['request','error','pending','success','empty']:
    by_id[id]['current'] = excerpt(COMPONENT,101,113,'PersonalTransferStart.chooseOrganisation')
    by_id[id]['proposed'] = proposal(selection+'\n\n'+helper, 'chooseOrganisation / loadMembers · proposal')
    by_id[id]['highlights'] = [108,110,111,112] if id not in ['success','empty'] else [110]
by_id['isolation']['proposed'] = proposal(by_id['isolation']['current']['text'], 'requestQuote / createInvitation · retained unchanged')
by_id['tests']['proposed'] = dict(by_id['tests']['current'], start=None,end=None,
    function='org / member fixtures · retained; regression additions planned',
    text=by_id['tests']['current']['text']+'\n\n// Planned: add deferred-promise tests using these existing fixtures.\n// No new regression test has been written or executed.')
by_id['coverage']['proposed'] = dict(by_id['coverage']['current'],start=None,end=None,
    function='existing happy path · retained; additional coverage pending',
    text=by_id['coverage']['current']['text']+'\n\n'+by_id['coverage']['proposed']['text'])
nodes.insert(3,node('api','GET organisation members','API boundary · fetchMembers','neutral',
    excerpt(API,1099,1108,'fetchMembers'),
    dict(excerpt(API,1099,1108,'fetchMembers · retained unchanged'),start=None,end=None),
    'The existing API function requests /orgs/{organisation}/members and maps the response to Member objects. The retry proposal reuses this function unchanged; no server API or billing request is introduced.',
    'fetchMembers("org-b") enters the existing API function',
    'GET /orgs/org-b/members; response mapped to Member[]',
    'Resolution returns members; rejection propagates to the caller catch.',
    'OBSERVED',['inspection','proposal'],[1099,1100,1101,1103]))

traces = {
 'select':(('Change Organisation to org-b','The select passes org-b to chooseOrganisation','The existing selection handler is entered.'),('Change Organisation to org-b','The select retains its event and uses disabled={formBusy}','The same selection handler is entered when the form is idle.')),
 'reset':(('chooseOrganisation("org-b")','destinationOrgId="org-b"; counterpartyId=""; members=[]; quote=null; error=null','Values from the old organisation are cleared.'),('chooseOrganisation("org-b")','Existing reset + membersError=null; ref guard prevents overlap','Old recovery state is cleared before the new request.')),
 'request':(('The selection handler reaches await fetchMembers(orgId)','busy=true; members=[]; counterpartyId=""','The current handler waits for the members promise.'),('chooseOrganisation delegates to loadMembers(orgId)','membersLoading=true; membersInFlight=true; membersError=null','The proposed loader waits for the same API with its immediate lock.')),
 'error':(('The members promise rejects','error=message(e); busy=false; members=[]','The shared error is shown; the administrator list stays empty.'),('The members promise rejects','membersError=message(e); membersLoading=false; lock=false','A discovery-specific error and retry action would become available.')),
 'blocked':(('The failed selection request settles','counterpartyId=""; members=[]; organisation remains org-b','Review is disabled. No administrator retry control exists.'),('The proposed discovery request fails','membersError is set; formBusy=false; organisation remains org-b','The proposed recovery controls offer an explicit retry.')),
 'success':(('The initial members request resolves with the owner fixture','members=[admin-2 / owner]; busy=false','CounterpartySelect can offer the returned owner (see source L62–68).'),('A retry resolves with the owner fixture','members=[admin-2 / owner]; membersError=null; membersLoading=false','The recovery feedback disappears; the existing selector offers the owner.')),
 'empty':(('The initial members request resolves with []','members=[]; busy=false; error remains null','No failure is raised; the administrator selector has no eligible choice.'),('A retry resolves with []','members=[]; membersError=null; membersLoading=false','The retry control/error disappear; review stays disabled without an administrator.')),
 'review':(('Select admin-2, then click Review payer transfer','counterpartyId="admin-2"; review is enabled','Only the explicit review click requests a quote; sending is a separate click.'),('Select the returned administrator, then click Review payer transfer','counterpartyId="admin-2"; formBusy=false','The existing review flow is retained. Retrying discovery does not quote or submit.')),
 'selection':(('Choose a different organisation or the blank option','Existing members, administrator, quote and shared error are reset','A blank organisation returns before another members request.'),('Choose a different organisation or the blank option','Existing reset + membersError=null; no overlap while loading','Recovery belonging to the old organisation is cleared.')),
 'isolation':(('A quote or submission request rejects','The existing shared error state changes','Current discovery uses that same error state; no separate recovery domain exists.'),('A quote or submission request rejects','error changes; membersError remains independent','The new administrator retry control is not offered for a quote/submission failure.')),
 'tests':(('Read the retained baseline output','12 existing tests passed; new retry regression tests=0','Existing fixtures and checks are available; the missing case remains pending.'),('Plan additions beside the existing tests','Existing fixtures retained; new regression tests=0','Deferred promises will exercise recovery before production code is changed.')),
}
for item in nodes:
    current, proposed_ = traces.get(item['id'], ((item['event'],item['transition'],item['result']),)*2)
    item['traces'] = {mode:dict(event=t[0],transition=t[1],result=t[2]) for mode,t in [('current',current),('proposed',proposed_)]}

scenarios = [
    dict(id='failure', label='01 / The missing retry', description='Trace the current dead end.', current=['select','reset','request','error','blocked'], proposed=['select','reset','request','error','retry'], extra=['success']),
    dict(id='recovery', label='02 / Recovery succeeds', description='Follow an explicit retry to the existing review flow.', current=['select','reset','request','error','blocked'], proposed=['select','reset','request','error','retry','pending','success','review'], extra=['empty']),
    dict(id='repeat', label='03 / Retry fails again', description='A repeated rejection must restore recovery.', current=['select','reset','request','error','blocked'], proposed=['error','retry','pending','error','retry'], extra=['success']),
    dict(id='empty', label='04 / Empty success', description='An empty response is a successful response.', current=['select','reset','request','empty'], proposed=['error','retry','pending','empty'], extra=['success']),
    dict(id='selection', label='05 / Change selection', description='Clear recovery state when the organisation changes.', current=['select','reset','request','error','selection'], proposed=['error','selection','request'], extra=['blocked']),
    dict(id='isolation', label='06 / Separate errors', description='Keep discovery, quoting and submission distinct.', current=['select','request','success','review','isolation'], proposed=['retry','pending','success','review','isolation'], extra=['blocked']),
    dict(id='evidence', label='07 / Evidence & tests', description='Review what is recorded and what is still pending.', current=['tests','coverage'], proposed=['tests','coverage'], extra=[]),
]

for scenario in scenarios:
    for mode in ['current','proposed']:
        route=scenario[mode]
        if 'request' in route:
            i=route.index('request');route.insert(i+1,'api')

focus = {
    'select': (['chooseOrganisation(event.target.value)'], ['chooseOrganisation(event.target.value)', 'formBusy']),
    'reset': (['setCounterpartyId("")', 'setMembers([])', 'setQuote(null)'], ['setMembersError(null)', 'setCounterpartyId("")']),
    'request': (['await fetchMembers(orgId)'], ['await fetchMembers(orgId)']),
    'api': (['`/orgs/${encodeURIComponent(orgId)}/members`'], ['`/orgs/${encodeURIComponent(orgId)}/members`']),
    'error': (['setError(message(e))'], ['setMembersError(message(e))']),
    'blocked': (['counterpartyId === ""'], ['membersError !== null', 'membersLoading']),
    'retry': (['counterpartyId === ""'], ['loadMembers(destinationOrgId)']),
    'pending': (['setBusy(true)'], ['if (orgId === "" || membersInFlight.current) return;', 'membersInFlight.current = true']),
    'success': (['setMembers(await fetchMembers(orgId))'], ['setMembers(await fetchMembers(orgId))']),
    'empty': (['setMembers(await fetchMembers(orgId))'], ['setMembers(await fetchMembers(orgId))']),
    'review': (['onClick={() => void requestQuote()}'], ['onClick={() => void requestQuote()}']),
    'selection': (['if (orgId === "") return;', 'setDestinationOrgId(orgId)'], ['setMembersError(null)', 'if (orgId === "") return;']),
    'isolation': (['setError(message(e))'], ['setError(message(e))']),
    'tests': (['vi.mocked(api.fetchMembers).mockResolvedValue'], ['vi.mocked(api.fetchMembers).mockResolvedValue']),
    'coverage': (['name: "Review payer transfer"'], ['Initial rejection exposes Retry loading administrators.']),
}

for item in nodes:
    before = item['current']; after = item['proposed']
    # Retain the original illustrative proposal in `text`. Align only its
    # presentation indentation so unchanged source is not painted as replaced.
    indentation = min(len(line)-len(line.lstrip()) for line in before['text'].splitlines() if line.strip())
    after['displayText'] = textwrap.indent(textwrap.dedent(after['text']), ' '*indentation)
    if item['id'] == 'select':
        # The original excerpt explicitly retains existing organisation options.
        # Show that equivalent focused change, preserving those source lines.
        after['displayText'] = before['text'].replace('disabled={busy}', 'disabled={formBusy}')
        after['presentationNote'] = 'Existing options retained as specified by the original illustrative excerpt.'
    item['focus'] = dict(zip(['current','proposed'], focus[item['id']]))
    old = before['text'].splitlines(); new = after['displayText'].splitlines()
    diff = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=old,b=new,autojunk=False).get_opcodes():
        if tag == 'equal':
            diff += [dict(kind='context', old=before['start']+i, new='P'+str(j+1), text=old[i]) for i,j in zip(range(i1,i2),range(j1,j2))]
        else:
            removed = [dict(kind='remove',old=before['start']+i,new=None,text=old[i]) for i in range(i1,i2)] if tag in ('delete','replace') else []
            added = [dict(kind='add',old=None,new='P'+str(j+1),text=new[j]) for j in range(j1,j2)] if tag in ('insert','replace') else []
            used = set()
            for removed_line in removed:
                candidates=[(difflib.SequenceMatcher(a=removed_line['text'],b=line['text'],autojunk=False).ratio(),k) for k,line in enumerate(added) if k not in used]
                if not candidates: continue
                ratio,k=max(candidates)
                if ratio<0.55: continue
                used.add(k); additions=[]; removals=[]
                for op,a1,a2,b1,b2 in difflib.SequenceMatcher(a=removed_line['text'],b=added[k]['text'],autojunk=False).get_opcodes():
                    if op!='equal':
                        if a1<a2: removals.append([a1,a2])
                        if b1<b2: additions.append([b1,b2])
                removed_line['changeRanges']=removals; added[k]['changeRanges']=additions
            diff += removed+added
    item['diff'] = diff

assert '12 passed (12)' in baseline
data = dict(
    title='Sotto #637 · Administrator discovery', commit=commit,
    builtAt=datetime.now(ZoneInfo('Europe/Budapest')).isoformat(timespec='seconds'),
    issue='https://github.com/getsotto/sotto/issues/637', component=COMPONENT, tests=TESTS,
    sourceHashes={name:hashlib.sha256(text.encode()).hexdigest() for name,text in files.items()},
    notes=notes, baseline=baseline, fullSources=files, baselineMtime=datetime.fromtimestamp(baseline_path.stat().st_mtime,ZoneInfo('Europe/Budapest')).isoformat(timespec='seconds'),
    nodes=nodes, scenarios=scenarios, checkpoints=checkpoints,
    acceptance=[
        'Initial failure exposes an accessible error and labelled retry.',
        'Pending retry keeps the organisation, clears the error and blocks overlap.',
        'Repeated failure restores the retry control.',
        'Successful retry restores eligible administrator choices.',
        'Successful empty response is not presented as a failure.',
        'Changing or clearing the organisation clears its recovery state.',
        'Quote/submission failures do not expose administrator retry.',
        'Retry calls neither the quote API nor the transfer API.',
    ],
)
template = (ROOT / 'walkthrough-template.html.in').read_text()
template = template.replace('/*__FOCUS_REFINEMENT__*/', (ROOT / 'focus-refinement.js').read_text())
template = template.replace('/*__FOCUS_STYLES__*/', (ROOT / 'focus-refinement.css').read_text())
assert template.count('__INVESTIGATION_DATA__') == 1
payload = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
compiled = template.replace('__INVESTIGATION_DATA__', payload)
(ROOT / 'interactive-walkthrough.html').write_text(compiled)
# Existing app preview tabs may still point at the old template filename.
# Keep that path runnable too; the authoring template now ends in .html.in.
(ROOT / 'walkthrough-template.html').write_text(compiled)
(ROOT / 'evidence-manifest.json').write_text(json.dumps(dict(commit=commit,sourceHashes=data['sourceHashes'],builtAt=data['builtAt'],baselineTests=12,regressionTests=0,repairApplied=False),indent=2)+'\n')
print('Built interactive-walkthrough.html from source snapshot',commit[:7])
