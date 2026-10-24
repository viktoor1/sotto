import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFile, writeFile, readdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { createHash } from 'node:crypto';
import { createServer } from 'node:http';

const require = createRequire('/workspace/sotto/web/package.json');
const { chromium } = require('@playwright/test');
const root = dirname(fileURLToPath(import.meta.url));
const server=createServer(async(req,res)=>{
 if(req.url==='/favicon.ico'){res.writeHead(204);res.end();return;}
 if(req.url==='/sandbox'){
  const source=(await readFile(join(root,'interactive-walkthrough.html'),'utf8')).replaceAll('&','&amp;').replaceAll('"','&quot;');
  res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});
  res.end('<!doctype html><html><head><title>Embedded preview validation</title></head><body style="margin:0;background:#0c0f13"><iframe title="Walkthrough preview" sandbox="allow-scripts allow-downloads" style="display:block;border:0;width:100%;height:100vh" srcdoc="'+source+'"></iframe></body></html>');return;
 }
 if(!['/interactive-walkthrough.html','/walkthrough-template.html'].includes(req.url?.split('?')[0])){res.writeHead(404);res.end();return;}
 res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store'});
 res.end(await readFile(join(root,'interactive-walkthrough.html')));
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const origin='http://127.0.0.1:'+server.address().port;
const url=origin+'/interactive-walkthrough.html';
const results=[];
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true});
const context=await browser.newContext({viewport:{width:1560,height:1050},permissions:['clipboard-read','clipboard-write'],acceptDownloads:true});
const page=await context.newPage();
const errors=[],requests=[];
page.on('pageerror',e=>errors.push(e.message));
page.on('request',r=>requests.push(r.url()));
const snapshot=()=>page.evaluate(()=>window.walkthrough.getSnapshot());
async function check(name,fn){await fn();results.push({name,status:'passed'});console.log('PASS',name);}
async function mode(name){await page.locator(`[data-mode="${name}"]`).click();}
async function route(id){await page.locator('#scenario').selectOption(id);}
async function node(id){await page.locator(`[data-node="${id}"]`).click();}
try {
 await page.goto(url);
 await page.locator('[data-node="select"]').waitFor();
 await check('Self-contained HTML renders locally without script errors or external requests',async()=>{
  assert.equal(await page.title(),'Sotto #637 — Interactive investigation');
  assert.equal(await page.locator('.panel').count(),3);
  assert.deepEqual(errors,[]);
  assert.ok(requests.every(r=>r.startsWith(origin+'/')||r.startsWith('data:')));
 });
 const data=await page.locator('#investigation-data').evaluate(el=>JSON.parse(el.textContent));
 await check('Every previewable HTML file is fully built, including the old template tab path',async()=>{
  const names=(await readdir(root)).filter(n=>n.endsWith('.html'));
  assert.ok(names.includes('interactive-walkthrough.html')&&names.includes('walkthrough-template.html'));
  for(const name of names){
   const html=await readFile(join(root,name),'utf8');
   assert.equal(html.includes('__INVESTIGATION_DATA__'),false,name);
   const payload=html.match(/<script id="investigation-data" type="application\/json">([\s\S]*?)<\/script>/)?.[1];
   assert.equal(JSON.parse(payload).commit,data.commit,name);
  }
  assert.equal(await readFile(join(root,'walkthrough-template.html'),'utf8'),await readFile(join(root,'interactive-walkthrough.html'),'utf8'));
  const legacy=await context.newPage();
  legacy.on('pageerror',e=>errors.push(e.message));
  await legacy.goto(origin+'/walkthrough-template.html');
  await legacy.locator('[data-node="select"]').waitFor();
  assert.equal(await legacy.locator('#node-title').textContent(),'Choose an organisation');
  await legacy.close();
 });
 await check('Sandboxed embedded preview renders and synchronizes navigation, code and copying',async()=>{
  const embedded=await context.newPage();
  embedded.on('pageerror',e=>errors.push(e.message));
  embedded.on('request',r=>requests.push(r.url()));
  await embedded.goto(origin+'/sandbox');
  const frame=embedded.frameLocator('iframe');
  await frame.locator('[data-node="select"]').waitFor();
  await frame.locator('[data-node="error"]').click();
  assert.equal(await frame.locator('#node-title').textContent(),'Administrator request fails');
  assert.match(await frame.locator('#code-view').textContent(),/setError\(message\(e\)\)/);
  await frame.locator('[data-node="retry"]').click();
  assert.equal(await frame.locator('#mode-proposed').getAttribute('aria-selected'),'true');
  await frame.locator('#mode-diff').click();
  assert.ok(await frame.locator('.code-line.add').count()>0);
  await frame.locator('#code-view').focus();
  await embedded.keyboard.press('ArrowRight');
  assert.equal(await frame.locator('#node-title').textContent(),'Wait with an immediate lock');
  await frame.locator('#copy-code').click();
  const copied=await frame.locator('#toast').textContent();
  const fallback=await frame.locator('#info-dialog').evaluate(el=>el.open);
  assert.ok(copied.includes('copied')||fallback,'Copy must work or expose the selectable manual fallback');
  if(fallback)await embedded.keyboard.press('Escape');
  await frame.locator('#tab-journal').click();
  assert.match(await frame.locator('#context-content').textContent(),/Human review checkpoint/);
  await embedded.screenshot({path:join(root,'walkthrough-refined-embedded.png'),fullPage:true});
  await embedded.close();
 });
 await check('Every current excerpt and its line numbers match the real repository source',async()=>{
  for(const n of data.nodes){
   const source=await readFile(join('/workspace/sotto',n.current.path),'utf8');
   assert.equal(n.current.text,source.split('\n').slice(n.current.start-1,n.current.end).join('\n'),n.id);
  }
  for(const [path,hash] of Object.entries(data.sourceHashes)){
   assert.equal(createHash('sha256').update(await readFile(join('/workspace/sotto',path))).digest('hex'),hash,path);
  }
  assert.equal(data.baseline.includes('12 passed (12)'),true);
 });
 await check('Original analysis, source snapshots, proposal text and recorded results are preserved',async()=>{
  const versions=(await readdir(join(root,'history'))).filter(x=>x.startsWith('before-focus-refinement-')).sort();
  const archive=join(root,'history',versions.at(-1));
  const html=await readFile(join(archive,'interactive-walkthrough.html'),'utf8');
  const old=JSON.parse(html.match(/<script id="investigation-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
  for(const key of ['commit','sourceHashes','notes','baseline','baselineMtime','scenarios','checkpoints','acceptance'])assert.deepEqual(data[key],old[key],key);
  for(const n of data.nodes){const previous=old.nodes.find(x=>x.id===n.id);assert.deepEqual(n.current,previous.current,n.id);for(const key of ['text','function','path','start','end'])assert.deepEqual(n.proposed[key],previous.proposed[key],n.id+'/'+key);}
  assert.equal(await readFile(join(root,'validation-report.json'),'utf8'),await readFile(join(archive,'validation-report.json'),'utf8'));
  assert.equal(await readFile(join(root,'visual-walkthrough.md'),'utf8'),await readFile(join(archive,'visual-walkthrough.md'),'utf8'));
 });
 await check('Minimal diffs reconstruct both sides and retain unchanged lines and exact inline changes',async()=>{
  for(const n of data.nodes){
   assert.equal(n.diff.filter(r=>r.kind!=='add').map(r=>r.text).join('\n'),n.current.text,n.id+' before');
   assert.equal(n.diff.filter(r=>r.kind!=='remove').map(r=>r.text).join('\n'),n.proposed.displayText,n.id+' after');
   const original=await readFile(join('/workspace/sotto',n.current.path),'utf8');
   for(const row of n.diff){if(row.old!==null)assert.equal(row.text,original.split('\n')[row.old-1]);for(const[a,b]of row.changeRanges??[])assert.ok(a>=0&&b>a&&b<=row.text.length);}
  }
  const request=data.nodes.find(n=>n.id==='request');
  assert.equal(request.diff.find(r=>r.old===102).kind,'context');
  assert.equal(request.diff.find(r=>r.old===110).kind,'context');
  assert.ok(request.diff.filter(r=>r.kind==='remove').length<request.current.text.split('\n').length/2);
  const select=data.nodes.find(n=>n.id==='select');
  assert.equal(select.diff.filter(r=>r.kind==='remove').length,1);
  assert.equal(select.diff.filter(r=>r.kind==='add').length,1);
  await mode('diff');await route('failure');await page.locator('[data-node="select"]').click();
  assert.ok(await page.locator('.inline-change').count()>0);
 });
 await check('Focused code folds irrelevant context, keeps exact expression highlights and expands actual full source',async()=>{
  await mode('current');await route('isolation');await node('isolation');
  assert.ok(await page.locator('.code-fold').count()>0);
  assert.match(await page.locator('.code-fold').first().textContent(),/unchanged lines/);
  const marks=await page.locator('.code-focus').allTextContents();
  assert.ok(marks.length>=2);assert.ok(marks.every(x=>x==='setError(message(e))'));
  assert.ok(await page.locator('.code-line.unrelated').count()>0);
  const before=await page.locator('.code-line').count(),height=(await page.locator('#code-view').boundingBox()).height;
  await page.locator('.code-fold').first().click();
  assert.ok(await page.locator('.code-line').count()>before);
  assert.ok(Math.abs((await page.locator('#code-view').boundingBox()).height-height)<1);
  await page.locator('#expand-context').click();
  const source=await readFile('/workspace/sotto/'+data.component,'utf8');
  assert.equal(await page.evaluate(()=>window.walkthrough.getDisplayedText()),source);
  assert.equal(await page.locator('.code-line').count(),source.replace(/\n$/,'').split('\n').length);
  await page.locator('#source-path').click();
  assert.equal(await page.locator('.source-file-line').count(),source.replace(/\n$/,'').split('\n').length);
  await page.keyboard.press('Escape');
  await page.locator('#expand-context').click();
  await route('failure');await node('api');await page.locator('#expand-context').click();
  await page.waitForFunction(()=>document.getElementById('code-view').scrollTop>0);
  const viewport=await page.locator('#code-view').boundingBox(),active=await page.locator('.code-line.focus-line').first().boundingBox();
  assert.ok(active.y>=viewport.y&&active.y<viewport.y+viewport.height);
 });
 await check('State transitions show previous and next values as explicit inferred/proposed models',async()=>{
  await mode('current');await route('failure');await node('error');
  assert.equal(await page.locator('.state-model').getAttribute('data-state-model'),'inferred');
  assert.match(await page.locator('.state-model').textContent(),/ILLUSTRATIVE/);
  const currentError=page.locator('.state-change').filter({has:page.locator('.state-key',{hasText:/^error$/})});
  assert.equal(await currentError.locator('.state-before').textContent(),'null');
  assert.equal(await currentError.locator('.state-new').textContent(),'message(e)');
  await mode('proposed');await route('recovery');await node('retry');
  assert.equal(await page.locator('.state-model').getAttribute('data-state-model'),'proposed');
  const error=page.locator('.state-change').filter({has:page.locator('.state-key',{hasText:/^membersError$/})});
  assert.equal(await error.locator('.state-before').textContent(),'message(e)');assert.equal(await error.locator('.state-new').textContent(),'null');
  assert.equal(await page.locator('#node-evidence').textContent(),'PROPOSED');
 });
 await check('Execution motion is brief, progressive and interruptible without stale selection',async()=>{
  await mode('current');await route('failure');await page.locator('#next').click();
  await page.waitForFunction(()=>document.querySelector('.edge[data-step="1"]')?.getAnimations().length>0);
  const timings=await page.evaluate(()=>document.getAnimations().map(a=>a.effect.getTiming()));
  assert.ok(timings.some(t=>t.duration===200&&t.delay===35));
  assert.ok(timings.some(t=>t.duration===170&&t.delay===115));
  assert.ok(timings.every(t=>Number(t.duration)+t.delay<=350));
  await page.locator('#code-view').focus();
  await page.keyboard.press('ArrowRight');await page.keyboard.press('ArrowRight');await page.keyboard.press('ArrowLeft');
  const selected=(await snapshot()).node;
  await page.waitForTimeout(380);
  assert.equal((await snapshot()).node,selected);
  assert.equal(await page.locator('.flow-node.active').getAttribute('data-node'),selected);
  assert.equal(await page.evaluate(()=>document.getAnimations().filter(a=>a.playState==='running').length),0);
 });
 await check('Selection keeps graph labels readable and the active node within the viewport',async()=>{
  await mode('proposed');await route('recovery');
  while(!await page.locator('#next').isDisabled())await page.locator('#next').click();
  await page.waitForTimeout(30);
  assert.ok((await snapshot()).zoom>=.8);
  const area=await page.locator('#graph-svg').boundingBox(),selected=await page.locator('.flow-node.active').boundingBox();
  assert.ok(selected.y>=area.y&&selected.y+selected.height<=area.y+area.height-40);
 });
 await check('Reduced-motion preference disables execution animations while navigation remains synchronized',async()=>{
  const reduced=await browser.newContext({reducedMotion:'reduce',viewport:{width:1400,height:1000}});
  const rp=await reduced.newPage();rp.on('pageerror',e=>errors.push(e.message));
  await rp.goto(url);await rp.locator('#next').click();await rp.locator('#next').click();
  await rp.waitForTimeout(50);
  assert.equal(await rp.locator('#node-title').textContent(),'Load administrators');
  assert.equal(await rp.evaluate(()=>document.getAnimations().length),0);
  assert.ok(await rp.locator('.code-focus').count()>0);
  await reduced.close();
 });
 await check('Graph selection synchronizes title, source, status and state trace',async()=>{
  await mode('current');await route('failure');
  await node('error');
  assert.equal((await snapshot()).node,'error');
  assert.equal(await page.locator('.flow-node.active').getAttribute('data-node'),'error');
  assert.equal(await page.locator('#node-title').textContent(),'Administrator request fails');
  assert.equal(await page.locator('#node-evidence').textContent(),'INFERRED');
  assert.match(await page.locator('#source-function').textContent(),/chooseOrganisation/);
  assert.match(await page.locator('#context-content').textContent(),/error=message\(e\); busy=false/);
  assert.equal(await page.evaluate(()=>window.walkthrough.getDisplayedText()),data.nodes.find(n=>n.id==='error').current.text);
 });
 await check('Proposed-only node clearly switches to the unapplied proposal',async()=>{
  await node('retry');
  assert.equal((await snapshot()).mode,'proposed');
  assert.equal((await snapshot()).node,'retry');
  assert.equal(await page.locator('#mode-proposed').getAttribute('aria-selected'),'true');
  assert.equal(await page.locator('#node-evidence').textContent(),'PROPOSED');
  assert.match(await page.locator('#code-scope').textContent(),/unapplied excerpt/);
  assert.match(await page.locator('#code-view').textContent(),/loadMembers\(destinationOrgId\)/);
  assert.match(await page.locator('#context-content').textContent(),/destinationOrgId remains org-b/);
 });
 await check('Diff presents additions/removals and copy preserves the displayed diff',async()=>{
  await mode('diff');
  assert.ok(await page.locator('.code-line.add').count()>0);
  await page.locator('#expand-context').click();
  assert.ok(await page.locator('.code-line.remove').count()>0);
  assert.match(await page.locator('#code-scope').textContent(),/P numbers are not repository line numbers/);
  const expected=await page.evaluate(()=>window.walkthrough.getDisplayedText());
  await page.locator('#copy-code').click();
  assert.equal(await page.evaluate(()=>navigator.clipboard.readText()),expected);
  assert.match(expected,/\+.*membersError/);
  await page.locator('#expand-context').click();
 });
 await check('Every route step in all three modes has synchronized code and evidence',async()=>{
  for(const view of ['current','proposed','diff']){
   await mode(view);
   for(const s of data.scenarios){
    await route(s.id);
    const sequence=view==='current'?s.current:s.proposed;
    for(let i=0;i<sequence.length;i++){
     const n=data.nodes.find(x=>x.id===sequence[i]),snap=await snapshot();
     assert.equal(snap.node,n.id,`${view}/${s.id}/${i}`);
     assert.equal(await page.locator('.flow-node.active').getAttribute('data-node'),n.id);
     assert.equal(await page.locator('#node-title').textContent(),n.title);
     assert.ok(await page.locator('.code-line.focus-line').count()>0,`missing focus ${view}/${s.id}/${n.id}`);
     const displayed=await page.evaluate(()=>window.walkthrough.getDisplayedText());
     if(view==='current')assert.equal(displayed,n.current.text);
     if(view==='proposed')assert.equal(displayed,n.proposed.displayText??n.proposed.text);
     if(view==='proposed')assert.equal(await page.locator('#source-path').textContent(),n.proposed.path);
     assert.ok((await page.locator('#context-content').textContent()).includes(n.traces[view==='current'?'current':'proposed'].event));
     if(i<sequence.length-1)await page.locator('#next').click();
    }
    assert.equal(await page.locator('#next').isDisabled(),true);
   }
  }
 });
 await check('Repeated failure loops and empty success remain distinct',async()=>{
  await mode('proposed');await route('repeat');
  assert.equal((await snapshot()).node,'error');
  await page.locator('#next').click();await page.locator('#next').click();
  assert.equal((await snapshot()).node,'pending');
  assert.match(await page.locator('#context-content').textContent(),/membersInFlight=true/);
  await page.locator('#next').click();
  assert.equal((await snapshot()).node,'error');
  assert.ok(await page.locator('.edge[data-from="pending"][data-to="error"]').count()>0);
  await route('empty');
  while(!await page.locator('#next').isDisabled())await page.locator('#next').click();
  assert.equal((await snapshot()).node,'empty');
  assert.match(await page.locator('#context-content').textContent(),/membersError=null; membersLoading=false/);
  await mode('current');
  assert.equal(await page.locator('[data-node="retry"]').count(),0);
  assert.equal(await page.locator('#node-evidence').textContent(),'INFERRED');
 });
 await check('Keyboard navigation, mode tabs, boundaries and help work',async()=>{
  await mode('current');await route('failure');await page.locator('#code-view').focus();
  await page.keyboard.press('ArrowRight');assert.equal((await snapshot()).cursor,1);
  await page.keyboard.press('ArrowLeft');assert.equal((await snapshot()).cursor,0);
  await page.keyboard.press('2');assert.equal((await snapshot()).mode,'proposed');
  await page.keyboard.press('3');assert.equal((await snapshot()).mode,'diff');
  await page.keyboard.press('1');assert.equal((await snapshot()).mode,'current');
  await page.keyboard.press('End');assert.equal(await page.locator('#next').isDisabled(),true);
  await page.keyboard.press('Home');assert.equal(await page.locator('#previous').isDisabled(),true);
  await page.keyboard.press('?');assert.equal(await page.locator('#info-dialog').evaluate(el=>el.open),true);
  await page.keyboard.press('Escape');assert.equal(await page.locator('#info-dialog').evaluate(el=>el.open),false);
  await page.locator('#mode-current').focus();await page.keyboard.press('ArrowRight');
  assert.equal((await snapshot()).mode,'proposed');
 });
 await check('Zoom, pointer-centred wheel zoom, pan and fit-to-view work',async()=>{
  await page.locator('#fit-view').click();let before=await snapshot();
  await page.locator('#zoom-in').click();assert.ok((await snapshot()).zoom>before.zoom);
  await page.locator('#zoom-out').click();assert.ok(Math.abs((await snapshot()).zoom-before.zoom)<.001);
  const box=await page.locator('#graph-svg').boundingBox();
  await page.mouse.move(box.x+box.width-6,box.y+15);await page.mouse.wheel(0,-120);
  assert.ok((await snapshot()).zoom>before.zoom);
  before=await snapshot();
  await page.mouse.move(box.x+box.width-5,box.y+15);await page.mouse.down();await page.mouse.move(box.x+box.width+25,box.y+42);await page.mouse.up();
  const after=await snapshot();assert.ok(after.x!==before.x&&after.y!==before.y);
  await page.locator('#fit-view').click();assert.ok((await snapshot()).zoom<2.7);
 });
 await check('Journal checkpoints and original analysis are retained independently',async()=>{
  await page.locator('#tab-journal').click();
  assert.equal((await snapshot()).context,'journal');
  assert.match(await page.locator('#context-content').textContent(),/task-journal.md/);
  assert.equal(await page.locator('.checkpoint').count(),data.checkpoints.length);
  await page.locator('#original-notes').click();
  assert.equal(await page.locator('#dialog-body pre').textContent(),await readFile(join(root,'visual-walkthrough.md'),'utf8'));
  await page.keyboard.press('Escape');await page.locator('#tab-evidence').click();
 });
 await check('Selected route/view/step survives reload and exports a task-only snapshot',async()=>{
  await mode('diff');await route('isolation');await page.locator('#next').click();
  const before=await snapshot();await page.reload();
  assert.equal((await snapshot()).node,before.node);assert.equal((await snapshot()).scenario,before.scenario);assert.equal((await snapshot()).mode,before.mode);
  const downloadPromise=page.waitForEvent('download');await page.locator('#export-evidence').click();
  const download=await downloadPromise;const target=join(root,'refinement-validation-export.json');await download.saveAs(target);
  const output=JSON.parse(await readFile(target,'utf8'));
  assert.equal(output.repairApplied,false);assert.equal(output.newRegressionTests,0);assert.equal(output.sourceCommit,data.commit);
  assert.equal(output.checkpoints.some(x=>x.id==='baseline'&&x.status==='VERIFIED'),true);
  assert.equal('notes' in output,false);assert.equal('environment' in output,false);
 });
 await page.waitForFunction(()=>!document.getElementById('toast').classList.contains('visible'));
 await check('Responsive layouts render without horizontal page overflow',async()=>{
  await mode('diff');await route('recovery');await node('retry');
  for(const size of [{width:1560,height:1050},{width:1024,height:900},{width:768,height:1024},{width:390,height:844}]){
   await page.setViewportSize(size);await page.waitForTimeout(180);
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),JSON.stringify(size));
   for(const panel of ['.graph-panel','.inspector-panel','.context-panel']){
    const b=await page.locator(panel).boundingBox();assert.ok(b.width>0&&b.x>=0&&b.x+b.width<=size.width+1,`${panel} at ${size.width}`);
   }
  }
  await page.screenshot({path:join(root,'walkthrough-refined-mobile.png'),fullPage:true});
  await page.setViewportSize({width:1560,height:1050});await page.waitForTimeout(180);
  await page.screenshot({path:join(root,'walkthrough-refined-desktop.png'),fullPage:true});
 });
 assert.deepEqual(errors,[]);assert.ok(requests.every(r=>r.startsWith(origin+'/')||r.startsWith('data:')));
 const report={status:'passed',validatedAt:new Date().toISOString(),browser:await browser.version(),delivery:'Self-contained HTML served over local HTTP; managed browser blocks file URLs',checks:results,scriptErrors:errors,remoteRequests:requests.filter(r=>!r.startsWith(origin+'/')&&!r.startsWith('data:')),sottoSourceChanged:false,scope:'Walkthrough interface validation; no Sotto regression test or repair was executed.'};
 await writeFile(join(root,'refinement-validation-report.json'),JSON.stringify(report,null,2)+'\n');
 console.log(`${results.length} interface validation groups passed`);
}catch(error){
 await writeFile(join(root,'refinement-validation-report.json'),JSON.stringify({status:'failed',checks:results,error:String(error),stack:error.stack,scriptErrors:errors},null,2)+'\n');
 await page.screenshot({path:join(root,'walkthrough-refined-failure.png'),fullPage:true}).catch(()=>{});
 throw error;
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
