const assert = require('node:assert/strict');
const {chromium, webkit} = require(process.env.PLAYWRIGHT_MODULE || '/Users/rusanivsky/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const BASE = process.env.SITE_URL || 'http://127.0.0.1:4175';
const GALLERY = '/photo/stabat-mater.html';

// Acceptance contract: the native cross-document fade is the only entry/reveal
// animation. Readiness gates only genuinely pending photos, without animating
// their release; decoded photos remain painted across delayed JS activation.
function observeMotion() {
 window.__motionTest = {waapi:[], transitions:[], nativeReveals:[], shows:[]};
 const original = Element.prototype.animate;
 Element.prototype.animate = function(...args) {
  if (this.matches('main') || this.closest('main')) {
   window.__motionTest.waapi.push({tag:this.tagName, className:this.className});
  }
  return original.apply(this,args);
 };
 addEventListener('transitionrun', event => {
  if (event.target.matches('main img') && event.propertyName === 'opacity') {
   window.__motionTest.transitions.push(event.target.currentSrc);
  }
 }, true);
 addEventListener('pagereveal', event => {
  if (event.isTrusted) window.__motionTest.nativeReveals.push(Boolean(event.viewTransition));
 });
 addEventListener('pageshow', event => window.__motionTest.shows.push(event.persisted));
}
async function assertNoRevealMotion(page, label) {
 const observed = await page.evaluate(() => window.__motionTest);
 assert.deepEqual(observed.waapi, [], label+': no MAIN, photo, heading or section WAAPI reveal');
 assert.deepEqual(observed.transitions, [], label+': readiness must not create an opacity CSS transition');
}
async function photoState(photo) {
 return photo.evaluate(el => {
  const style = getComputedStyle(el);
  return {visible:style.visibility !== 'hidden' && Number(style.opacity) === 1,
   hidden:style.visibility === 'hidden' || Number(style.opacity) === 0,
   complete:el.complete, width:el.naturalWidth};
 });
}
function assertGeometry(before, after, label) {
 assert.ok(before && after, label+': the photo has a reserved box');
 for (const key of ['x','y','width','height']) {
  assert.ok(Math.abs(after[key]-before[key]) <= 1, label+': photo box '+key+' stays stable');
 }
}
async function waitVisible(page) {
 await page.waitForFunction(() => {
  const el = document.querySelector('main img');
  if (!el) return false;
  const style = getComputedStyle(el);
  return style.visibility !== 'hidden' && style.opacity === '1';
 });
}
async function makeContext(browser, width, options={}) {
 const context = await browser.newContext({viewport:{width,height:900},timezoneId:'Europe/Kyiv',...options});
 if (options.javaScriptEnabled !== false) await context.addInitScript(observeMotion);
 return context;
}
async function earlyRevealRoute(page) {
 // Exercise pagereveal delivered before the deferred controller, as browsers do.
 await page.route('**/assets/page-motion.js*', async route => {
  const response = await route.fetch();
  const source = await response.text();
  await new Promise(resolve => setTimeout(resolve, 250));
  await route.fulfill({response, body:"{const e=new Event('pagereveal');Object.defineProperty(e,'viewTransition',{value:location.pathname==='/photo.html'?{}:null});dispatchEvent(e);}"+source});
 });
}

(async () => {
 const browser = await (process.env.BROWSER === 'webkit' ? webkit : chromium).launch();
 const failures = [];
 async function scenario(width, name, run) {
  const context = await makeContext(browser,width);
  try {
   const page = await context.newPage();
   const errors = [];
   page.on('pageerror', e => errors.push(e.message));
   await run(page,context);
   assert.deepEqual(errors, [], name+': no uncaught script errors');
   console.log('PASS '+name+' at '+width+'px');
  } catch (error) {
   failures.push(name+' at '+width+'px: '+error.message);
   console.error('FAIL '+failures.at(-1));
  } finally { await context.close(); }
 }
 try {
  for (const width of [390,1440]) {
   await scenario(width,'pending readiness, geometry and native navigation/history',async page => {
    await earlyRevealRoute(page);
    await page.addInitScript(() => {
     const originalDecode=HTMLImageElement.prototype.decode;
     window.__decodeCalls=0;
     const decodedGate=new Promise(resolve => window.__releaseDecode=resolve);
     HTMLImageElement.prototype.decode=function(...args) {
      if (!this.matches('main img')) return originalDecode.apply(this,args);
      window.__decodeCalls++;
      return Promise.all([originalDecode.apply(this,args),decodedGate]);
     };
    });
    let release;
    const gate = new Promise(resolve => release=resolve);
    await page.route('**/assets/photo/**', async route => {await gate;await route.continue();});
    await page.goto(BASE+GALLERY,{waitUntil:'domcontentloaded'});
    const photo = page.locator('main img').first();
    await page.waitForFunction(() => document.querySelector('main img')?.loading === 'eager');
    assert.ok((await photoState(photo)).hidden,'A genuinely pending photo must not flash');
    const before = await photo.boundingBox();
    const headingBefore = await page.locator('main h1').boundingBox();
    assert.equal(await page.locator('main img').last().getAttribute('loading'),'lazy','Distant gallery photos remain lazy');
    release();
    await page.waitForFunction(() => document.querySelector('main img')?.naturalWidth > 0 && window.__decodeCalls > 0);
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    assert.ok((await photoState(photo)).hidden,'Newly loaded photo stays gated until decode resolves');
    assert.equal(await page.locator('main h1').isVisible(),true,'Decode gating preserves text');
    await page.evaluate(() => window.__releaseDecode());
    await waitVisible(page);
    await page.waitForTimeout(450);
    assertGeometry(before,await photo.boundingBox(),'Decode');
    assertGeometry(headingBefore,await page.locator('main h1').boundingBox(),'Heading during decode');
    // Report readiness transition separately from WAAPI, so a duplicate CSS
    // opacity transition cannot hide behind the absence of JS animation calls.
    assert.deepEqual(await page.evaluate(() => window.__motionTest.transitions),[],
     'Delayed photo release must not start an opacity CSS transition');
    await assertNoRevealMotion(page,'Direct entry and decoded photo release');
    if (width < 900) await page.locator('.menu-btn').click();
    await page.locator('.hdr a[href="/photo.html"]').click();
    await page.waitForURL(BASE+'/photo.html');
    await page.waitForTimeout(350);
    if (process.env.BROWSER !== 'webkit') {
     assert.ok(await page.evaluate(() => window.__motionTest.nativeReveals.includes(true)),
      'Supported Chromium navigation still uses its native cross-document transition');
    }
    await assertNoRevealMotion(page,'Navigation, including an unsupported native transition');
    await page.goBack();
    await page.waitForURL(BASE+GALLERY);
    await waitVisible(page);
    await page.waitForTimeout(450);
    assertGeometry(before,await photo.boundingBox(),'History restoration');
    await assertNoRevealMotion(page,'History restoration');
    // Exercise BFCache cleanup even in browsers where automation prevents
    // genuine cache eligibility; actual back navigation is tested above.
    await page.evaluate(() => dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true})));
    assert.equal((await photoState(photo)).visible,true,'BFCache pageshow keeps decoded photo visible');
    await assertNoRevealMotion(page,'BFCache pageshow');
    await page.emulateMedia({reducedMotion:'reduce'});
    await page.waitForFunction(() => matchMedia('(prefers-reduced-motion: reduce)').matches &&
     document.getAnimations().every(a => a.playState === 'finished' || a.playState === 'idle'),null,{timeout:1500});
    assert.equal((await photoState(photo)).visible,true,'Reduced motion keeps decoded content visible');
   });

   await scenario(width,'below-fold headings and sections stay stable',async page => {
    await page.goto(BASE+'/artists.html',{waitUntil:'domcontentloaded'});
    const belowFold=page.locator('main .artist-group-heading').last();
    assert.ok(await belowFold.count(),'Artists page has a below-fold group heading to exercise');
    await belowFold.evaluate(el => {
     window.__sectionFrames=[];
     let remaining=40;
     const sample=() => {
      const style=getComputedStyle(el);
      window.__sectionFrames.push({opacity:style.opacity,transform:style.transform});
      if (--remaining) requestAnimationFrame(sample);
     };
     requestAnimationFrame(sample);
    });
    await belowFold.scrollIntoViewIfNeeded();
    await page.waitForFunction(() => window.__sectionFrames.length === 40);
    assert.ok(await page.evaluate(() => window.__sectionFrames.every(frame => frame.opacity==='1' && frame.transform==='none')),
     'Below-fold heading never fades or translates on entering viewport');
    await assertNoRevealMotion(page,'Below-fold headings and sections');
   });

   await scenario(width,'decoded first paint across delayed controller activation',async page => {
    let activate;
    const controllerGate = new Promise(resolve => activate=resolve);
    await page.route('**/assets/page-motion.js*',async route => {
     const response = await route.fetch();
     await controllerGate;
     await route.fulfill({response});
    });
    await page.goto(BASE+GALLERY,{waitUntil:'commit'});
    const photo = page.locator('main img').first();
    await page.waitForFunction(() => document.querySelector('main img')?.naturalWidth > 0);
    // With the controller deliberately held, this photo is already decoded in
    // the browser image cache. Its first paint must not await JS or a watchdog.
    await photo.evaluate(el => el.decode());
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    assert.equal((await photoState(photo)).visible,true,'Cached decoded photo is visible before controller activation');
    const before = await photo.boundingBox();
    await photo.evaluate(el => {
     window.__cachedPhotoFrames=[];
     let remaining=40;
     const sample=() => {
      const style=getComputedStyle(el);
      window.__cachedPhotoFrames.push({opacity:style.opacity,visibility:style.visibility});
      if (--remaining) requestAnimationFrame(sample);
     };
     requestAnimationFrame(sample);
    });
    activate();
    await page.waitForLoadState('domcontentloaded');
    await page.waitForFunction(() => window.__cachedPhotoFrames.length === 40);
    assert.ok(await page.evaluate(() => window.__cachedPhotoFrames.every(frame => frame.opacity==='1' && frame.visibility!=='hidden')),
     'Already decoded photo must never be hidden or replayed when delayed controller activates');
    assertGeometry(before,await photo.boundingBox(),'Delayed controller activation');
    await assertNoRevealMotion(page,'Cached first paint');
   });

   for (const options of [{javaScriptEnabled:false},{reducedMotion:'reduce'}]) {
    const context = await makeContext(browser,width,options);
    try {
     const page = await context.newPage();
     await page.goto(BASE+'/en/photo.html');
     assert.equal((await photoState(page.locator('main img').first())).visible,true,'Content visible without motion');
     if (options.javaScriptEnabled !== false) await assertNoRevealMotion(page,'Reduced-motion entry');
    } finally { await context.close(); }
   }
   await scenario(width,'script failure remains visible',async page => {
    await page.route('**/assets/page-motion.js*',route => route.abort());
    await page.goto(BASE+'/photo.html');
    await page.waitForTimeout(3600);
    assert.equal((await photoState(page.locator('main img').first())).visible,true,'Script failure must fail open');
   });
   for (const failure of ['error','decode','timeout','reduced-motion']) {
    await scenario(width,'photo fail-open '+failure,async page => {
     let release;
     if (failure === 'error') await page.route('**/assets/photo/**',route => route.abort());
     if (failure === 'decode') await page.addInitScript(() => {
      HTMLImageElement.prototype.decode=() => Promise.reject(new Error('Test decode failure'));
     });
     if (failure === 'timeout' || failure === 'reduced-motion') {
      const gate = new Promise(resolve => release=resolve);
      await page.route('**/assets/photo/**',async route => {await gate;await route.abort();});
     }
     await page.goto(BASE+GALLERY,{waitUntil:'domcontentloaded'});
     if (failure === 'reduced-motion') {
      assert.ok((await photoState(page.locator('main img').first())).hidden,'Pending photo is gated before reduced motion');
      await page.emulateMedia({reducedMotion:'reduce'});
     }
     await waitVisible(page);
     assert.equal(await page.locator('main h1').isVisible(),true,'Image failure must preserve text');
     await assertNoRevealMotion(page,'Fail-open '+failure);
     if (release) release();
    });
   }
  }
 } finally {await browser.close();}
 assert.deepEqual(failures,[],'Page motion acceptance failures');
})().catch(error => {console.error(error);process.exitCode=1;});
