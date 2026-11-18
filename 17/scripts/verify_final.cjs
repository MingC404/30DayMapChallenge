const fs=require('fs'),assert=require('assert'),crypto=require('crypto'),path=require('path');const {chromium}=require('./browser.cjs'),M=require('../src/model.js');
(async()=>{const d=JSON.parse(fs.readFileSync('17/src/scene.json','utf8')),ref=JSON.parse(fs.readFileSync('17/data/map_reference.json','utf8'));
assert.strictEqual(d.lights.length,153);assert.strictEqual(new Set(d.lights.map(p=>p.id)).size,153);let groups={},checks=0;
for(const p of d.lights){groups[p.kind]=(groups[p.kind]||0)+1;const before=ref.points.find(x=>x.llen_uid===p.id);assert.deepStrictEqual([p.x,p.y],before.pixel);assert.deepStrictEqual(p.colors,before.color_codes);assert.deepStrictEqual([p.lon,p.lat],[before.lon,before.lat]);
 if(p.kind==='sigseq'){assert.deepStrictEqual(p.sigseq.split('+').map(t=>({state:t.startsWith('(')?'off':'on',seconds:Number(t.replace(/[()]/g,''))})),p.sequence);}
 if(p.sequence.length){assert(Math.abs(p.sequence.reduce((a,s)=>a+s.seconds,0)-p.period)<1e-8);for(const n of [0,1,7,37]){let t=n*p.period;for(let i=0;i<p.sequence.length;i++){const s=p.sequence[i];assert.strictEqual(M.signal(p.sequence,t+s.seconds/2,p.period),s.state==='on'?1:0);assert.strictEqual(M.signal(p.sequence,t+s.seconds+1e-7,p.period),p.sequence[(i+1)%p.sequence.length].state==='on'?1:0);checks+=2;t+=s.seconds;}}}
 for(const t of [0,.1,.6,1.2,2.5,5,6,11.99,12]){const a=M.lightAt(p,t,'loop',true),b=M.lightAt(p,t+12,'loop',true);assert.strictEqual(a.state,b.state);for(const k of ['strength','halo','envelope'])assert(Math.abs(a[k]-b[k])<1e-9);checks++;}
 if(p.conditional)assert.strictEqual(M.lightAt(p,3,'continuous',false).state,'conditional-muted');
 if(p.sequence.length&&!M.dividesLoop(p.period)){assert.strictEqual(M.lightAt(p,0,'loop',true).halo,0);assert.strictEqual(M.lightAt(p,0,'continuous',true).halo,1);}
}
assert.deepStrictEqual(groups,{sigseq:141,fixed:8,unknown:3,iso:1});assert.strictEqual(d.actors.find(a=>a.llnr==='35070').period_s,12);assert.strictEqual(d.actors.find(a=>a.llnr==='34910').period_s,12);assert.notStrictEqual(d.actors[0].initial_angle_deg,d.actors[1].initial_angle_deg);
for(const a of d.actors){assert.deepStrictEqual(M.actorAt(a,0),M.actorAt(a,12));}
for(let i=0;i<d.titles.length;i++){for(const k of ['text','bounds','font','size_px'])assert.deepStrictEqual(d.titles[i][k],ref.titles[i][k]);}
const nondiv=d.lights.filter(p=>p.sequence.length&&!M.dividesLoop(p.period));assert.strictEqual(nondiv.length,51);
const b=await chromium.launch({headless:true,executablePath:process.env.DAY17_BROWSER||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});let browserReport;
try{const p=await b.newPage({viewport:{width:1440,height:1300}}),errors=[],external=[];p.on('pageerror',e=>errors.push(e.message));p.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url())});await p.goto('file:///'+path.resolve('17/day17.html').replaceAll('\\','/'));await p.waitForFunction(()=>window.beamPreview?.ready);
assert.strictEqual(await p.locator('#light-select option').count(),154);assert.strictEqual(await p.evaluate(()=>beamPreview.mode),'continuous');assert.strictEqual(await p.locator('#conditional').isChecked(),false);
const a=await p.evaluate(()=>beamPreview.capture(900,0,'loop')),z=await p.evaluate(()=>beamPreview.capture(900,12,'loop'));assert.strictEqual(a,z);
await p.click('#info-toggle');for(const x of d.lights){await p.selectOption('#light-select',x.id);assert((await p.locator('#actor-detail').textContent()).includes(x.name));}
await p.click('#close-info');await p.selectOption('#mode','continuous');await p.evaluate(()=>beamPreview.seek(2,'continuous'));const stop=await p.evaluate(()=>beamPreview.time);await p.waitForTimeout(120);assert.strictEqual(await p.evaluate(()=>beamPreview.time),stop);await p.click('#play');await p.waitForTimeout(220);assert(await p.evaluate(()=>beamPreview.time)>stop+.12);await p.click('#play');
await p.selectOption('#speed','2');assert.strictEqual(await p.evaluate(()=>beamPreview.speed),2);await p.selectOption('#speed','0.5');assert.strictEqual(await p.evaluate(()=>beamPreview.speed),.5);
await p.click('#info-toggle');await p.check('#conditional');assert.strictEqual(await p.locator('#conditional').isChecked(),true);await p.uncheck('#conditional');await p.fill('#search','Romer');assert.strictEqual(await p.locator('#light-select option').count(),2);await p.fill('#search','');
await p.setViewportSize({width:390,height:844});await p.waitForTimeout(100);assert(!(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth)));assert.deepStrictEqual(errors,[]);assert.deepStrictEqual(external,[]);
browserReport={offline_file_open:true,all_153_entries_accessible:true,loop_zero_and_12_pixel_identical:true,continuous_mode_default:true,pause_play_speed_and_conditions:true,mobile_no_horizontal_overflow:true,external_requests:external,errors};}finally{await b.close()}
const report={passed:true,groups,model_checks:checks,entries:153,non_dividing_rhythms:51,source_positions_and_colors_match_approved_layout:true,titles_unchanged:true,beam_period_seconds:12,browser:browserReport};fs.writeFileSync('17/data/validation.json',JSON.stringify(report,null,2));console.log(report);
})().catch(e=>{console.error(e);process.exitCode=1});


