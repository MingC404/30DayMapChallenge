/* Actual cover clicks, project-prefix routing, interactive smoke tests, and release isolation. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto'),{spawn}=require('child_process');
const {chromium}=require('../02/.deps-js/node_modules/playwright'),{createServer}=require('./serve_gallery.cjs');
const root=path.resolve(__dirname,'..'),entries=require('./gallery_entries.json'),out=path.join(root,'.work/gallery-check');
fs.mkdirSync(out,{recursive:true});
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const walk=p=>fs.readdirSync(p,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(p,e.name)):[path.join(p,e.name)]);
async function listen(s){await new Promise(r=>s.listen(0,'127.0.0.1',r));return `http://127.0.0.1:${s.address().port}`}
function contrast(a,b){const lum=c=>{const rgb=c.match(/\d+/g).slice(0,3).map(Number).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722};const x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
(async()=>{
 const pub=createServer(false),priv=createServer(true),publicOrigin=await listen(pub),privateOrigin=await listen(priv),base=publicOrigin+'/30DayMapChallenge/';
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'}),errors=[],external=[],checks={};
 try{
  for(const [name,viewport,colorScheme] of [['desktop',{width:1440,height:1000},'light'],['laptop',{width:1366,height:768},'light'],['mobile',{width:390,height:844},'light'],['narrow',{width:320,height:740},'light'],['dark',{width:1440,height:1000},'dark']]){
   const page=await browser.newPage({viewport,colorScheme,hasTouch:name==='mobile'||name==='narrow'});page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)errors.push(r.status()+' '+r.url())});await page.goto(base);
   assert.deepEqual(await page.locator('article').evaluateAll(es=>es.map(e=>e.id)),entries.map(e=>'day-'+e.day));
   for(const e of entries){
    const card=page.locator('#day-'+e.day);assert.equal(await card.locator('.description').innerText(),e.description);assert.equal(await card.locator('.tools').innerText(),e.tools.join(' · '));
    for(const evidence of e.evidence)assert.ok(fs.existsSync(path.join(root,evidence)),evidence);
    for(const img of await card.locator('img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate(el=>el.decode());assert.ok(await img.evaluate(el=>el.naturalWidth>0));assert.equal(await img.evaluate(el=>getComputedStyle(el).objectFit),'contain');assert.ok((await img.getAttribute('alt')).length>20);const a=img.locator('..');assert.equal(await a.getAttribute('target'),'_blank');assert.ok((await a.getAttribute('rel')).includes('noopener'));}
    assert.equal(await card.locator('.badge').count(),0);
    const frame=await card.locator('.media-grid').boundingBox(),header=await card.locator('header').boundingBox(),row=await card.boundingBox();
    const borders=await card.evaluate(el=>({left:getComputedStyle(el).borderLeftWidth,right:getComputedStyle(el).borderRightWidth,top:getComputedStyle(el).borderTopWidth,bg:getComputedStyle(el).backgroundColor}));assert.deepEqual(borders,{left:'0px',right:'0px',top:'0px',bg:'rgba(0, 0, 0, 0)'});
    if(viewport.width>760){assert.ok(header.x+header.width<frame.x);assert.ok(header.width/row.width>=.27&&header.width/row.width<=.35);assert.ok(frame.width/row.width>=.62&&frame.width/row.width<=.70);assert.ok(Math.abs(header.y+header.height/2-(frame.y+frame.height/2))<2);}else{assert.ok(frame.y>=header.y+header.height+20);assert.ok(Math.abs(header.x-frame.x)<1);}
    for(const img of await card.locator('img').all()){const sizes=await img.evaluate(el=>{const r=el.getBoundingClientRect();return{actual:r.width/r.height,natural:el.naturalWidth/el.naturalHeight}});assert.ok(Math.abs(sizes.actual-sizes.natural)<.005,'Original aspect changed '+e.day);}
   }
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Horizontal overflow '+name);
   const colors=await page.locator('article').first().evaluate(el=>({text:getComputedStyle(el.querySelector('.description')).color,bg:getComputedStyle(document.body).backgroundColor}));assert.ok(contrast(colors.text,colors.bg)>=4.5);
   assert.equal(await page.locator('.summary,.badge,.card-meta,.local-notice').count(),0);assert.equal((await page.locator('.intro').innerText()).replace(/\s+/g,' ').trim(),'30 DAY MAP CHALLENGE 2026 Map collection Maps and spatial illustrations by Ming Cao.');
   await page.evaluate(()=>scrollTo(0,0));await page.keyboard.press('Tab');const focused=page.locator(':focus');assert.ok(await focused.count());assert.ok(parseFloat(await focused.evaluate(el=>getComputedStyle(el).outlineWidth))>=2);
   if(['desktop','mobile','dark'].includes(name))await page.screenshot({path:path.join(out,'collection-'+name+'.png'),fullPage:true});
   if(name==='desktop'){
    const links=await page.locator('[href],[src]').evaluateAll(es=>es.flatMap(e=>['href','src'].filter(a=>e.hasAttribute(a)).map(a=>e.getAttribute(a))));
    for(const href of [...new Set(links)]){assert.ok(!/^(file:|[A-Za-z]:\\)/.test(href));if(/^(https?:|data:|#|mailto:)/.test(href))continue;assert.ok((await page.request.get(new URL(href,base).href)).ok(),href);}
   }
   if(name==='mobile'){
    const [popup]=await Promise.all([page.waitForEvent('popup'),page.locator('#day-02 .cover-link').tap()]);await popup.waitForLoadState('domcontentloaded');assert.ok(popup.url().endsWith('/02/'));await popup.close();
   }
   checks[name]={works:entries.length,noOverflow:true,singleColumn:true,originalAspect:true,noCardsOrBadges:true,contrast:contrast(colors.text,colors.bg)};await page.close();
  }
  const gallery=await browser.newPage();await gallery.goto(base);
  for(const day of ['01','02','10']){
   const [page]=await Promise.all([gallery.waitForEvent('popup'),gallery.locator('#day-'+day+' .cover-link').click()]);page.on('pageerror',e=>errors.push('Day '+day+': '+e.message));page.on('requestfailed',r=>{if(!r.url().startsWith(publicOrigin))external.push({day,url:r.url(),failure:r.failure()?.errorText})});
   await page.waitForLoadState('domcontentloaded');
   if(day==='01'){
    await page.setViewportSize({width:1440,height:1000});
    await page.waitForFunction(()=>typeof map!=='undefined'&&typeof visibleRecords!=='undefined',{timeout:30000});
    await page.waitForFunction(()=>basemapReady,{timeout:45000});assert.deepEqual(await page.evaluate(()=>basemapErrors),[]);
    assert.equal(await page.locator('#total').innerText(),'0');await page.getByRole('button',{name:'Select all',exact:true}).click();assert.equal(await page.locator('#total').innerText(),'795');await page.getByRole('button',{name:'Clear',exact:true}).click();assert.equal(await page.locator('#total').innerText(),'0');
    const women=await page.evaluate(()=>data.categories.findIndex(c=>c.key==='women'));await page.locator('#filters input').nth(women).check();await page.waitForTimeout(300);
    const target=await page.evaluate(()=>{const box=map.getContainer().getBoundingClientRect();const cs=markers.filter(({point})=>point.matches.includes('women')).map(e=>({...e,pos:map.latLngToContainerPoint(e.marker.getLatLng())}));const e=cs.find(e=>e.pos.x>80&&e.pos.x<box.width-80&&e.pos.y>80&&e.pos.y<box.height-80&&cs.every(o=>o===e||e.pos.distanceTo(o.pos)>16));if(!e)throw Error('No isolated visible pointer target');return{x:box.left+e.pos.x,y:box.top+e.pos.y,name:e.point.name}});
    await page.mouse.move(target.x,target.y);await page.waitForSelector('.info-tooltip');assert.ok((await page.locator('.info-tooltip').innerText()).includes(target.name));await page.mouse.click(target.x,target.y);assert.ok((await page.locator('.leaflet-popup').innerText()).includes(target.name));checks.day01BasemapAndPointer=true;
   }else if(day==='02'){
    await page.waitForFunction(()=>window.previewReady);assert.ok(await page.locator('.route').count()>0);await page.locator('input[value="permission"]').check();assert.equal(await page.locator('#permission-legend').evaluate(el=>el.style.display),'');await page.locator('input[value="surface"]').check();
    await page.locator('.route').first().evaluate(el=>el.dispatchEvent(new MouseEvent('click',{bubbles:true})));assert.ok((await page.locator('#detail-tags').innerText()).length>0);await page.getByRole('button',{name:'Close details'}).click();
   }else{await page.waitForFunction(()=>window.heritageMap);assert.ok(await page.locator('.heritage-point').count()>0);}
   checks['interactive'+day]={actualCoverClick:true,loaded:true,controls:true};await page.close();
  }
  // Public Day 13 is a truthful status page, with no map/data hidden behind it.
  assert.equal(await gallery.locator('#day-13 img').count(),0);const [status]=await Promise.all([gallery.waitForEvent('popup'),gallery.locator('#day-13 .withheld-media a').click()]);await status.waitForLoadState();assert.ok((await status.locator('main').innerText()).includes('awaiting publication clearance'));assert.equal(await status.locator('script').count(),0);await status.close();
  assert.equal((await gallery.request.get(publicOrigin+'/local-day13/output/Where_Night_Comes_From.html')).status(),404);
  assert.equal((await gallery.request.get(base+'assets/13/Where_Night_Comes_From.png')).status(),404);await gallery.close();
  const privateGallery=await browser.newPage({viewport:{width:1440,height:1000}});await privateGallery.goto(privateOrigin+'/30DayMapChallenge/');assert.equal(await privateGallery.locator('#day-13 img').getAttribute('src'),'/local-day13/output/Where_Night_Comes_From.png');
  const [day13]=await Promise.all([privateGallery.waitForEvent('popup'),privateGallery.locator('#day-13 .cover-link').click()]);await day13.waitForFunction(()=>window.prototypeReady);assert.equal(await day13.locator('#destination option').count(),11);await day13.selectOption('#destination','421010088025');assert.equal(await day13.locator('#selectionName').innerText(),'40th St & Walnut St');await day13.locator('#aug').click();assert.equal((await day13.evaluate(()=>prototypeState)).month,'2025-08');await day13.close();checks.privateDay13={canonicalFiles:true,interactive:true,noCopiedPayload:true};
  for(const [name,selector] of [['top','.intro'],['middle','#day-08'],['day13','#day-13']]){await privateGallery.locator(selector).scrollIntoViewIfNeeded();await privateGallery.evaluate(sel=>scrollTo(0,document.querySelector(sel).getBoundingClientRect().top+scrollY-60),selector);for(const img of await privateGallery.locator(selector+' img').all())await img.evaluate(el=>el.decode());await privateGallery.screenshot({path:path.join(out,'portfolio-'+name+'.png'),fullPage:false});}
  await privateGallery.setViewportSize({width:390,height:844});await privateGallery.evaluate(()=>scrollTo(0,0));await privateGallery.screenshot({path:path.join(out,'portfolio-mobile-top.png'),fullPage:false});await privateGallery.locator('#day-13').scrollIntoViewIfNeeded();await privateGallery.screenshot({path:path.join(out,'portfolio-mobile-day13.png'),fullPage:false});await privateGallery.close();
  const animated=entries.flatMap(e=>e.media.filter(m=>m.path.endsWith('.gif'))),gifPage=await browser.newPage({viewport:{width:1440,height:1000}});await gifPage.setContent('<html><body style="margin:0;background:white;display:grid;grid-template-columns:repeat(3,400px);gap:10px">'+animated.map(m=>`<img src="${base+m.path}" width="400" height="400" style="object-fit:contain">`).join('')+'</body></html>');for(const img of await gifPage.locator('img').all())await img.evaluate(el=>el.decode());const gifFrames=animated.map(()=>new Set());for(let sample=0;sample<4;sample++){for(let i=0;i<animated.length;i++)gifFrames[i].add(crypto.createHash('sha256').update(await gifPage.locator('img').nth(i).screenshot()).digest('hex'));if(sample<3)await gifPage.waitForTimeout(1500);}for(let i=0;i<animated.length;i++)assert.ok(gifFrames[i].size>1,'GIF did not animate '+animated[i].source);checks.gifPlayback={files:animated.length,allChanged:true};await gifPage.close();
  const privateHashes=new Set([path.join(root,'13/output/Where_Night_Comes_From.png'),...walk(path.join(root,'13/.local/data'))].map(sha));
  for(const file of walk(path.join(root,'docs'))){assert.ok(!privateHashes.has(sha(file)),'Restricted file copied to docs: '+file);if(/\.(html|js|json|geojson)$/.test(file)){const s=fs.readFileSync(file,'utf8');assert.ok(!s.includes('nightlife_home_origins')&&!s.includes('NIGHTLIFE_DEVICE_HOME_AREAS')&&!s.includes('/local-day13/'),'Restricted payload/reference in docs '+file);}}
  checks.publicationIsolation=true;
  // Reuse the existing complete hosted Day 10 interaction suite without editing that day.
  await new Promise((resolve,reject)=>{const child=spawn(process.execPath,[path.join(__dirname,'check_gallery.cjs'),'--interactive-only',base],{stdio:'inherit'});child.on('error',reject);child.on('exit',c=>c===0?resolve():reject(Error('Day 10 suite failed '+c)))});
  assert.deepEqual(errors,[]);checks.errors=errors;checks.externalFailures=external;checks.day10FullSuite=true;
  fs.writeFileSync(path.join(out,'collection-validation.json'),JSON.stringify(checks,null,2));console.log(JSON.stringify(checks,null,2));
 }finally{await browser.close();await Promise.all([new Promise(r=>pub.close(r)),new Promise(r=>priv.close(r))]);}
})().catch(e=>{console.error(e);process.exitCode=1});
