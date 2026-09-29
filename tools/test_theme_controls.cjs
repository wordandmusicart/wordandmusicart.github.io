#!/usr/bin/env node
/* Acceptance tests for footer theme controls. Serve the repository on :4175.
 * node tools/test_theme_controls.cjs
 * Optional: SITE_URL, SITE_ROOT, PLAYWRIGHT_MODULE (path to Playwright module).
 * Tests observable rendering/storage behaviour, independently of theme.js internals.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/rusanivsky/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const ROOT = process.env.SITE_ROOT || path.resolve(__dirname, '..');
const BASE = process.env.SITE_URL || 'http://127.0.0.1:4175';
const modes = ['auto', 'light', 'dark'];
const button = (page, mode) => page.locator(`footer button[data-theme-mode="${mode}"]`);
const routes = [];
function discover(dir, recursive = false) {
  for (const item of fs.readdirSync(path.join(ROOT, dir), {withFileTypes: true})) {
    const relative = path.posix.join(dir, item.name);
    if (item.isFile() && item.name.endsWith('.html')) routes.push('/' + relative);
    else if (recursive && item.isDirectory()) discover(relative, true);
  }
}
discover('');
for (const directory of ['en', 'concerts', 'photo']) discover(directory, true);

async function eventually(check, message) {
  let last;
  for (let attempt = 0; attempt < 40; attempt++) {
    try { await check(); return; } catch (error) { last = error; }
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  throw new Error(message + ': ' + last.message);
}
async function selected(page, mode) {
  for (const value of modes) {
    assert.equal(await button(page, value).getAttribute('aria-pressed'), String(mode === value));
  }
}
async function rendered(page, mode, {picture = true} = {}) {
  await eventually(async () => {
    const result = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement);
      const visibility = selector => [...document.querySelectorAll(selector)].map(node => getComputedStyle(node).display !== 'none');
      return {paper: style.getPropertyValue('--paper').trim().toLowerCase(),
        lightLogos: visibility('.logo-light'), darkLogos: visibility('.logo-dark'),
        picture: document.querySelector('.next-banner picture img')?.currentSrc};
    });
    assert.equal(result.paper, mode === 'dark' ? '#1c1c1c' : '#f5f5f5');
    assert.ok(result.lightLogos.length && result.darkLogos.length, 'Both logo variants must exist');
    assert.ok(result.lightLogos.every(shown => shown === (mode === 'light')), 'Light-mode logos must follow chosen theme');
    assert.ok(result.darkLogos.every(shown => shown === (mode === 'dark')), 'Dark-mode logos must follow chosen theme');
    if (picture) assert.match(result.picture || '', mode === 'dark' ? /vivre-banner-light[-.]/ : /vivre-banner-dark[-.]/);
  }, `Rendering must resolve to ${mode}`);
}
async function choose(page, mode) {
  await button(page, mode).click();
  await selected(page, mode);
}
async function context(browser, colorScheme = 'light') {
  // The site intentionally skips geo/language redirects for crawlers, allowing
  // both language routes to be tested in the same context without redirects.
  const ctx = await browser.newContext({colorScheme, viewport: {width: 1440, height: 1000}, userAgent: 'WordMusicAcceptanceBot'});
  ctx.setDefaultTimeout(4000);
  return ctx;
}

(async () => {
  const browser = await chromium.launch({headless: true});
  let failures = 0;
  async function test(name, body) {
    try { await body(); console.log(`PASS ${name}`); }
    catch (error) { failures++; console.error(`FAIL ${name}\n${error.stack}`); }
  }
  try {
    await test(`all ${routes.length} public footers have accessible theme controls beside Privacy`, async () => {
      assert.ok(routes.length >= 43, 'Expected all public site routes');
      const ctx = await context(browser);
      try {
        const page = await ctx.newPage();
        for (const route of routes) {
          await page.goto(BASE + route);
          const footer = page.locator('footer');
          assert.equal(await footer.count(), 1, route);
          assert.equal(await footer.locator('button[data-theme-mode]').count(), 3, route);
          assert.equal(await footer.locator('a[href$="privacy.html"]').count(), 1, route);
          const labels = route.startsWith('/en/') ? ['Automatic theme', 'Light theme', 'Dark theme'] : ['Автоматична тема', 'Світла тема', 'Темна тема'];
          for (const [index, mode] of modes.entries()) {
            const control = button(page, mode);
            assert.equal(await control.count(), 1, `${route} ${mode}`);
            assert.equal(await footer.getByRole('button', {name: labels[index], exact: true}).count(), 1, `${route} ${mode} accessible label`);
            assert.ok(await control.isEnabled(), `${route} ${mode} enabled`);
          }
          await selected(page, 'auto');
        }
      } finally { await ctx.close(); }
    });
    await test('Auto follows system changes and leaves storage empty', async () => {
      const ctx = await context(browser);
      try {
        const page = await ctx.newPage();
        await page.goto(BASE + '/');
        await selected(page, 'auto');
        assert.equal(await page.evaluate(() => localStorage.getItem('wm-theme')), null);
        await rendered(page, 'light');
        await page.emulateMedia({colorScheme: 'dark'});
        await rendered(page, 'dark');
        await page.emulateMedia({colorScheme: 'light'});
        await rendered(page, 'light');
      } finally { await ctx.close(); }
    });
    for (const mode of ['dark', 'light']) {
      await test(`Manual ${mode} overrides opposite OS, survives reload/navigation, Auto clears`, async () => {
        const opposite = mode === 'dark' ? 'light' : 'dark';
        const ctx = await context(browser, opposite);
        try {
          const page = await ctx.newPage();
          await page.goto(BASE + '/');
          await choose(page, mode);
          assert.equal(await page.evaluate(() => localStorage.getItem('wm-theme')), mode);
          await rendered(page, mode);
          await page.emulateMedia({colorScheme: mode});
          await page.emulateMedia({colorScheme: opposite});
          await selected(page, mode);
          await rendered(page, mode);
          await page.reload();
          await selected(page, mode);
          await rendered(page, mode);
          await page.goto(BASE + '/en/artists.html');
          await selected(page, mode);
          await rendered(page, mode, {picture: false});
          await choose(page, 'auto');
          assert.equal(await page.evaluate(() => localStorage.getItem('wm-theme')), null);
          await rendered(page, opposite, {picture: false});
          await page.reload();
          await selected(page, 'auto');
          await rendered(page, opposite, {picture: false});
        } finally { await ctx.close(); }
      });
    }
    await test('localStorage denial keeps controls usable and emits no uncaught errors', async () => {
      const ctx = await context(browser, 'dark');
      try {
        await ctx.addInitScript(() => {
          for (const method of ['getItem', 'setItem', 'removeItem']) {
            Storage.prototype[method] = () => { throw new DOMException('Blocked by test', 'SecurityError'); };
          }
        });
        const page = await ctx.newPage();
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        await page.goto(BASE + '/');
        await selected(page, 'auto');
        await rendered(page, 'dark');
        await choose(page, 'light');
        await rendered(page, 'light');
        await choose(page, 'auto');
        await rendered(page, 'dark');
        assert.deepEqual(errors, []);
      } finally { await ctx.close(); }
    });
    await test('Reduced motion shows scene content without running entrance animations', async () => {
      const ctx = await context(browser);
      try {
        const page = await ctx.newPage();
        await page.emulateMedia({reducedMotion: 'reduce'});
        await page.goto(BASE + '/');
        for (const id of ['intro', 'about', 'past-concerts', 'media', 'contacts']) {
          await page.locator('#' + id).scrollIntoViewIfNeeded();
          const result = await page.evaluate(async sceneId => {
            await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
            const scene = document.getElementById(sceneId);
            const invisible = [...scene.querySelectorAll('h1,h2,p,a')].filter(node => {
              const style = getComputedStyle(node);
              return style.display !== 'none' && (style.visibility === 'hidden' || Number(style.opacity) === 0);
            }).map(node => node.tagName);
            return {invisible, running: document.getAnimations().filter(animation => animation.playState === 'running').length};
          }, id);
          assert.deepEqual(result.invisible, [], `${id}: content must remain visible`);
          assert.equal(result.running, 0, `${id}: reduced motion must suppress entrances/transitions`);
        }
      } finally { await ctx.close(); }
    });
  } finally { await browser.close(); }
  console.log(`Theme acceptance: ${failures ? `${failures} failed` : 'all passed'}`);
  process.exitCode = failures ? 1 : 0;
})().catch(error => { console.error(error); process.exitCode = 1; });
