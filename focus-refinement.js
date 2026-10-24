// Authoring module: embedded inline by build_walkthrough.py. No runtime imports.
Object.assign(state,{fullContext:false,openFolds:new Set(),contextLines:4,renderKey:'',selectionEpoch:0,motionAnimations:[],codeRows:[]});
const motionPreference=matchMedia('(prefers-reduced-motion: reduce)');

function focusRanges(text,patterns){
 const result=[];
 for(const pattern of patterns){let start=0,index;while((index=text.indexOf(pattern,start))!==-1){result.push([index,index+pattern.length]);start=index+Math.max(1,pattern.length);}}
 return result;
}
function codeSegments(text,focus,changes,kind){
 const stops=[...new Set([0,text.length,...focus.flat(),...changes.flat()])].sort((a,b)=>a-b);let output='';
 for(let i=0;i<stops.length-1;i++){
  const a=stops[i],b=stops[i+1];if(a===b)continue;
  let part=highlight(text.slice(a,b));
  if(changes.some(([x,y])=>a>=x&&b<=y))part=`<span class="inline-change ${kind==='remove'?'inline-remove':'inline-add'}">${part}</span>`;
  if(focus.some(([x,y])=>a>=x&&b<=y))part=`<mark class="code-focus">${part}</mark>`;
  output+=part;
 }
 return output||' ';
}
function focusedLine(row){
 const symbol=row.kind==='add'?'+':row.kind==='remove'?'−':' ';
 return `<div class="code-line ${row.kind||''} ${row.focus.length?'focus-line':'unrelated'}" data-line="${escapeHTML(row.label)}" data-focus="${row.focus.length>0}"><span class="line-no" aria-hidden="true">${escapeHTML(row.label)}</span>${state.mode==='diff'?`<span class="diff-mark" aria-hidden="true">${symbol}</span>`:''}<span class="code-text">${codeSegments(row.text,row.focus,row.changes||[],row.kind)}</span></div>`;
}
function focusedRows(node){
 const before=node.current,after=node.proposed,proposedText=after.displayText??after.text;let rows;
 if(state.mode==='current'){
  const text=state.fullContext?DATA.fullSources[before.path]:before.text,first=state.fullContext?1:before.start;
  rows=(state.fullContext?text.replace(/\n$/,''):text).split('\n').map((text,i)=>({text,label:first+i,old:first+i,kind:'context',focus:first+i>=before.start&&first+i<=before.end?focusRanges(text,node.focus.current):[]}));
 }else if(state.mode==='proposed'){
  rows=proposedText.split('\n').map((text,i)=>({text,label:'P'+(i+1),kind:'context',focus:focusRanges(text,node.focus.proposed)}));
 }else{
  rows=node.diff.map(row=>({...row,label:row.old??row.new,focus:focusRanges(row.text,row.kind==='remove'?node.focus.current:row.kind==='add'?node.focus.proposed:[...node.focus.current,...node.focus.proposed]),changes:row.changeRanges??(row.kind==='context'?[]:[[0,row.text.length]])}));
 }
 return rows;
}
function renderFocusedCode(node){
 const current=node.current,proposed=node.proposed,rows=focusedRows(node);state.codeRows=rows;
 $('source-path').textContent=state.mode==='proposed'?proposed.path:current.path;
 $('source-path').title='Open the complete, actual source snapshot';
 $('source-function').textContent=state.mode==='current'?`${current.function} · L${current.start}–${current.end}`:state.mode==='proposed'?`${proposed.function} · illustrative excerpt`:`${current.function} → proposed excerpt`;
 $('code-scope').className='code-scope'+(state.mode==='current'?'':' proposed');
 $('code-scope').textContent=state.mode==='current'?`OBSERVED SOURCE · ${DATA.commit.slice(0,7)} · actual line numbers${state.fullContext?' · complete file':''}`:state.mode==='proposed'?'PROPOSED · unapplied excerpt · P numbers belong to this excerpt':'EXCERPT DIFF · − current / + proposed · P numbers are not repository line numbers';
 $('inspector-content').setAttribute('aria-labelledby','mode-'+state.mode);
 $('expand-context').textContent=state.fullContext?'Collapse to focus':'Expand full context';
 $('expand-context').setAttribute('aria-expanded',String(state.fullContext));
 const targets=node.focus[state.mode==='current'?'current':'proposed'];
 $('focus-description').textContent=targets[0]??'Selected expression';
 $('focus-description').title=targets.join(' · ');
 const wanted=new Set();
 for(let i=0;i<rows.length;i++)if(rows[i].focus.length)for(let j=Math.max(0,i-state.contextLines);j<=Math.min(rows.length-1,i+state.contextLines);j++)wanted.add(j);
 if(!wanted.size)for(let i=0;i<Math.min(rows.length,9);i++)wanted.add(i);
 let html='',shown=0,folds=0;
 for(let i=0;i<rows.length;){
  if(state.fullContext||wanted.has(i)){html+=focusedLine(rows[i]);shown++;i++;continue;}
  let end=i+1;while(end<rows.length&&!wanted.has(end))end++;
  const hidden=rows.slice(i,end),count=end-i,id=`${i}:${end}`,open=state.openFolds.has(id);
  const additions=hidden.filter(r=>r.kind==='add').length,removals=hidden.filter(r=>r.kind==='remove').length;
  const isUnchanged=!additions&&!removals;
  const label=isUnchanged?`${count} unchanged lines`:`${count} lines outside focus · +${additions} −${removals}`;
  html+=`<button class="code-fold" data-fold="${id}" aria-expanded="${open}" aria-label="${open?'Collapse':'Expand'} ${escapeHTML(label)}"><span class="fold-chevron">${open?'⌄':'›'}</span> ${open?'Collapse':'…'} ${escapeHTML(label)}</button>`;
  if(open){html+=hidden.map(focusedLine).join('');shown+=count;}else folds++;
  i=end;
 }
 $('code-view').innerHTML=html;
 $('code-count').textContent=`${shown} / ${rows.length} lines · ${state.fullContext?'full context':state.contextLines+' surrounding lines'}${folds?' · '+folds+' folds':''}`;
 $('code-origin').textContent=state.mode==='current'?'ACTUAL SOURCE':state.mode==='proposed'?'PROPOSED · NOT APPLIED':'LINE-LEVEL REVIEW · NOT APPLIED';
 $('copy-code').title=state.fullContext&&state.mode==='current'?'Copy the complete source file':'Copy the complete excerpt, including folded context';
}
function scrollToActiveCode(){
 const viewport=$('code-view'),row=viewport.querySelector('.code-line.focus-line');if(!row)return;
 const top=row.getBoundingClientRect().top-viewport.getBoundingClientRect().top+viewport.scrollTop;
 viewport.scrollTo({top:Math.max(0,top-viewport.clientHeight*.28),behavior:'auto'});
}
function getCopyableCode(){
 const node=selectedNode();
 if(state.mode==='current')return state.fullContext?DATA.fullSources[node.current.path]:node.current.text;
 if(state.mode==='proposed')return node.proposed.displayText??node.proposed.text;
 return node.diff.map(r=>(r.kind==='add'?'+':r.kind==='remove'?'-':' ')+r.text).join('\n');
}
async function copyLiteral(text){
 try{await navigator.clipboard.writeText(text);toast('Code copied, including folded context');return;}catch{}
 const area=document.createElement('textarea');area.value=text;area.style.cssText='position:fixed;left:0;top:0;opacity:0';document.body.append(area);area.select();let ok=false;
 try{ok=document.execCommand('copy');}catch{}finally{area.remove();}
 if(ok)toast('Code copied, including folded context');else showDialog('Copy source excerpt','<p>Select and copy this complete excerpt:</p><pre>'+escapeHTML(text)+'</pre>');
}
function showCompleteSource(){
 const path=selectedNode().current.path,source=DATA.fullSources[path];
 const lines=source.replace(/\n$/,'').split('\n');
 showDialog('Complete source snapshot',`<p class="source-dialog-path">${escapeHTML(path)} · ${DATA.commit.slice(0,7)} · actual source</p><button id="copy-complete-source">Copy complete file</button><pre class="complete-source">${lines.map((text,i)=>`<span class="source-file-line" data-source-line="${i+1}"><span class="source-file-number">${i+1}</span>${highlight(text)||' '}</span>`).join('')}</pre>`);
 $('copy-complete-source').addEventListener('click',()=>copyLiteral(source));
 const target=$('dialog-body').querySelector(`[data-source-line="${selectedNode().current.start}"]`);
 requestAnimationFrame(()=>{if(target)$('dialog-body').scrollTop=Math.max(0,target.offsetTop-$('dialog-body').offsetTop-80);});
}
function stepStateModel(){
 const route=currentRoute(),proposed=state.mode!=='current';
 let model={destinationOrgId:route[0]==='select'?'""':'"org-b"',members:'[]',counterpartyId:'""',quote:'null',error:'null',busy:'false'};
 if(proposed)Object.assign(model,{membersError:'null',membersLoading:'false',membersInFlight:'false'});
 if(route[0]==='error'){if(proposed)Object.assign(model,{membersLoading:'true',membersInFlight:'true'});else model.busy='true';}
 let before={...model};
 for(let i=0;i<=state.cursor;i++){
  before={...model};const id=route[i];
  if(id==='reset'){Object.assign(model,{destinationOrgId:'"org-b"',counterpartyId:'""',members:'[]',quote:'null',error:'null'});if(proposed)model.membersError='null';}
  if(id==='request'||id==='retry'){if(proposed)Object.assign(model,{membersLoading:'true',membersInFlight:'true',membersError:'null'});else model.busy='true';}
  if(id==='error'){if(proposed)Object.assign(model,{membersError:'message(e)',membersLoading:'false',membersInFlight:'false'});else Object.assign(model,{error:'message(e)',busy:'false'});}
  if(id==='success'||id==='empty'){Object.assign(model,{members:id==='empty'?'[]':'[admin-2 / owner]',busy:'false'});if(proposed)Object.assign(model,{membersError:'null',membersLoading:'false',membersInFlight:'false'});}
  if(id==='review')model.counterpartyId='"admin-2"';
  if(id==='selection'){Object.assign(model,{destinationOrgId:'""',members:'[]',counterpartyId:'""',quote:'null',error:'null'});if(proposed)model.membersError='null';}
  if(id==='isolation')Object.assign(model,{error:'message(e)',busy:'false'});
 }
 return {before,after:model,changed:Object.keys(model).filter(key=>before[key]!==model[key])};
}
function renderModelTransition(node){
 const model=stepStateModel();
 const rows=model.changed.map(key=>`<div class="state-change"><span class="state-key">${escapeHTML(key)}</span><span class="state-values"><span class="state-before">${escapeHTML(model.before[key]??'not set')}</span><span class="state-arrow" aria-hidden="true">→</span><span class="state-new">${escapeHTML(model.after[key])}</span></span></div>`).join('');
 return `<div class="state-model" data-state-model="${state.mode==='current'?'inferred':'proposed'}"><div class="state-model-label">${state.mode==='current'?'INFERRED':'PROPOSED'} STATE MODEL · ILLUSTRATIVE</div>${rows||'<p class="state-unchanged">No additional state mutation at this boundary.</p>'}${node.id==='selection'?'<p class="state-unchanged">Example shown: clear the selection.</p>':''}</div>`;
}
function keepSelectedLegible(){
 const viewport=$('graph-svg').getBoundingClientRect(),p=state.positions.get(selectedNode().id);if(!p)return;
 const floor=Math.min(.88,(viewport.width-36)/state.graphWidth);
 if(state.zoom<floor){state.zoom=floor;state.x=(viewport.width-state.graphWidth*state.zoom)/2;}
 const top=state.y+p.y*state.zoom,bottom=top+p.h*state.zoom;
 if(top<20||bottom>viewport.height-65)state.y=(viewport.height-45)/2-(p.y+p.h/2)*state.zoom;
 const left=state.x+p.x*state.zoom,right=left+p.w*state.zoom;
 if(left<12||right>viewport.width-12)state.x=(viewport.width-state.graphWidth*state.zoom)/2;
 applyTransform();
}
function cancelSelectionMotion(){for(const animation of state.motionAnimations)animation.cancel();state.motionAnimations=[];}
function animateSelection(epoch){
 if(epoch!==state.selectionEpoch||motionPreference.matches)return;
 const register=(el,frames,options)=>{if(el)state.motionAnimations.push(el.animate(frames,options));};
 const node=$('graph-world').querySelector('.flow-node.active');
 register(node?.querySelector('.node-dot'),[{opacity:.35},{opacity:1}],{duration:180,easing:'ease-out'});
 const incoming=$('graph-world').querySelector(`.edge[data-step="${state.cursor}"]`);
 if(incoming){const length=incoming.getTotalLength();register(incoming,[{strokeDasharray:`${length} ${length}`,strokeDashoffset:length,opacity:.3},{strokeDasharray:`${length} ${length}`,strokeDashoffset:0,opacity:1}],{duration:200,delay:35,easing:'cubic-bezier(.2,.7,.2,1)'});}
 for(const mark of $('code-view').querySelectorAll('.code-focus'))register(mark,[{opacity:.3},{opacity:1}],{duration:170,delay:115,easing:'ease-out',fill:'backwards'});
 for(const value of $('context-content').querySelectorAll('.state-new'))register(value,[{opacity:.25,transform:'translateY(2px)'},{opacity:1,transform:'translateY(0)'}],{duration:180,delay:80,easing:'ease-out',fill:'backwards'});
}
function render(resetGraph=false){
 const key=`${state.mode}/${state.scenario}/${state.cursor}`,changed=key!==state.renderKey;
 document.querySelectorAll('[data-mode]').forEach(b=>{b.setAttribute('aria-selected',b.dataset.mode===state.mode);b.tabIndex=b.dataset.mode===state.mode?0:-1;});
 document.querySelectorAll('[data-context]').forEach(b=>{b.setAttribute('aria-selected',b.dataset.context===state.context);b.tabIndex=b.dataset.context===state.context?0:-1;});
 $('scenario').value=state.scenario;$('scenario-description').textContent=SCENARIOS.get(state.scenario).description;
 if(changed){
  cancelSelectionMotion();state.selectionEpoch++;state.fullContext=false;state.openFolds.clear();
  renderInspector();renderContext();renderGraph(resetGraph);state.renderKey=key;
  const epoch=state.selectionEpoch;
  requestAnimationFrame(()=>{if(epoch!==state.selectionEpoch)return;keepSelectedLegible();scrollToActiveCode();animateSelection(epoch);});
 }else{renderContext();if(resetGraph)renderGraph(true);}
 saveLocation();
}
$('expand-context').addEventListener('click',()=>{state.fullContext=!state.fullContext;state.openFolds.clear();renderFocusedCode(selectedNode());requestAnimationFrame(scrollToActiveCode);});
$('code-view').addEventListener('click',event=>{
 const fold=event.target.closest('[data-fold]');if(!fold)return;
 const id=fold.dataset.fold,viewport=$('code-view'),oldTop=fold.getBoundingClientRect().top;
 if(state.openFolds.has(id))state.openFolds.delete(id);else state.openFolds.add(id);
 renderFocusedCode(selectedNode());const replacement=viewport.querySelector(`[data-fold="${id}"]`);
 if(replacement)viewport.scrollTop+=replacement.getBoundingClientRect().top-oldTop;
 replacement?.focus({preventScroll:true});
});
$('source-path').addEventListener('click',showCompleteSource);
motionPreference.addEventListener('change',()=>{if(motionPreference.matches)cancelSelectionMotion();});
