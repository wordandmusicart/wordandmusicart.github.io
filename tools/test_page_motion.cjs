const assert = require('node:assert/strict');
const {chromium, webkit} = require(process.env.PLAYWRIGHT_MODULE || '/Users/rusanivsky/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const BASE = process.env.SITE_URL || 'http://127.0.0.1:4175';
(async () => {
 const browser = await (process.env.BROWSER === 'webkit' ? webkit : chromium).launch();
 try {
  for (const width of [390, 1440]) {
   const context = await browser.newContext({viewport:{width,height:900},timezoneId:'Europe/Kyiv'});
   await context.addInitScript(()=>{
    window.__motionTest={arrivals:0,reveals:[],nativeReveals:[]};
    const original=Element.prototype.animate;
    Element.prototype.animate=function(...args){if(this.tagName==='MAIN') window.__motionTest.arrivals++;return original.apply(this,args);};
    addEventListener('pagereveal',e=>{window.__motionTest.reveals.push(Boolean(e.viewTransition));if(e.isTrusted)window.__motionTest.nativeReveals.push(Boolean(e.viewTransition));});
   });
   const page = await context.newPage();
   const errors=[]; page.on('pageerror',e=>errors.push(e.message));
   // Reproduce browsers delivering pagereveal before the deferred controller.
   await page.route('**/assets/page-motion.js*',async route=>{
    const response=await route.fetch();
    const source=await response.text();
    await new Promise(resolve=>setTimeout(resolve,250));
    await route.fulfill({response,body:"{const e=new Event('pagereveal');Object.defineProperty(e,'viewTransition',{value:location.pathname==='/photo.html'?{}:null});dispatchEvent(e);}"+source});
   });

   let release; const gate=new Promise(r=>release=r);
   await page.route('**/assets/photo/**',async route=>{await gate;await route.continue();});
   await page.goto(BASE+'/photo/stabat-mater.html', {waitUntil:'domcontentloaded'});
   const photo=page.locator('main img').first();
   assert.equal(await photo.evaluate(el=>getComputedStyle(el).opacity),'0','An undecoded photo must not flash');
   const before=await photo.boundingBox();
   assert.equal(await page.locator('main img').last().getAttribute('loading'),'lazy','Distant gallery photos remain lazy');
   release();
   await page.waitForFunction(()=>{const el=document.querySelector('main img');return el?.naturalWidth>0&&getComputedStyle(el).opacity==='1';});
   await page.waitForFunction(()=>window.__motionTest.arrivals===1);
   assert.equal(await page.evaluate(()=>window.__motionTest.arrivals),1,'Direct entry gets one arrival fade');
   const after=await photo.boundingBox();
   for (const key of ['x','y','width','height']) assert.ok(Math.abs(after[key]-before[key])<=1, 'Decode must not meaningfully shift the photo box: '+key);
   if(width<900) await page.locator('.menu-btn').click();
   await page.locator('.hdr a[href="/photo.html"]').click();
   await page.waitForURL(BASE+'/photo.html');
   await page.waitForTimeout(350);
   if(process.env.BROWSER!=='webkit') {
    assert.ok(await page.evaluate(()=>window.__motionTest.nativeReveals.includes(true)),'Chromium navigation uses a native transition');
    assert.equal(await page.evaluate(()=>window.__motionTest.arrivals),0,'Native transition must not also run fallback arrival');
   } else {
    const native=await page.evaluate(()=>window.__motionTest.reveals.includes(true));
    assert.equal(await page.evaluate(()=>window.__motionTest.arrivals),native?0:1,'Arrival fallback follows actual transition availability');
   }
   await page.goBack(); await page.waitForURL(BASE+'/photo/stabat-mater.html');
   await page.waitForTimeout(450);
   assert.equal(await photo.evaluate(el=>getComputedStyle(el).opacity),'1','Restored photo stays visible');
   await page.emulateMedia({reducedMotion:'reduce'});
   await page.waitForFunction(()=>matchMedia('(prefers-reduced-motion: reduce)').matches && document.getAnimations().every(a=>a.playState==='finished'||a.playState==='idle'), null, {timeout:1500});
   assert.equal(await page.evaluate(()=>document.getAnimations().filter(a=>a.playState!=='finished'&&a.playState!=='idle').length),0,'Reduced motion cancels active motion');
   assert.deepEqual(errors,[]);
   await context.close();
   for (const options of [{javaScriptEnabled:false},{reducedMotion:'reduce'}]) {
    const c=await browser.newContext({...options,viewport:{width,height:900},timezoneId:'Europe/Kyiv'});
    const p=await c.newPage(); await p.goto(BASE+'/en/photo.html');
    assert.equal(await p.locator('main img').first().evaluate(el=>getComputedStyle(el).opacity),'1','Content visible without motion');
    await c.close();
   }
   const c=await browser.newContext({viewport:{width,height:900},timezoneId:'Europe/Kyiv'});
   const p=await c.newPage(); await p.route('**/assets/page-motion.js*',r=>r.abort());
   await p.goto(BASE+'/photo.html'); await p.waitForTimeout(3600);
   assert.equal(await p.locator('main img').first().evaluate(el=>getComputedStyle(el).opacity),'1','Script failure must fail open');
   await c.close();
   for (const failure of ['error','decode']) {
    const c=await browser.newContext({viewport:{width,height:900},timezoneId:'Europe/Kyiv'});
    const p=await c.newPage();
    if(failure==='error') await p.route('**/assets/photo/**',r=>r.abort());
    else await p.addInitScript(()=>{HTMLImageElement.prototype.decode=()=>Promise.reject(new Error('Test decode failure'));});
    await p.goto(BASE+'/photo/stabat-mater.html');
    await p.waitForFunction(()=>getComputedStyle(document.querySelector('main img')).opacity==='1');
    assert.equal(await p.locator('main h1').isVisible(),true,'Image failure must preserve text');
    await c.close();
   }
   console.log('PASS photo readiness, navigation/back, reduced motion, no JS and script failure at '+width+'px');
  }
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
