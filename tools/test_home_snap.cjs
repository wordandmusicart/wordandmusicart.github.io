#!/usr/bin/env node
/* Desktop home scrolls one full-screen scene at a time; mobile and other pages scroll freely.
 * SITE_URL=http://127.0.0.1:4175 node tools/test_home_snap.cjs
 */
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/rusanivsky/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const BASE = process.env.SITE_URL || 'http://127.0.0.1:4175';
const snapType = page => page.evaluate(() => getComputedStyle(document.documentElement).scrollSnapType);
(async () => {
  const browser = await chromium.launch();
  let failed = 0;
  const test = async (name, viewport, route, fn) => {
    const context = await browser.newContext({viewport, locale: 'uk-UA', timezoneId: 'Europe/Kyiv'});
    const page = await context.newPage();
    try { await page.goto(BASE + route, {waitUntil: 'networkidle'}); await fn(page); console.log('PASS', name); }
    catch (e) { failed++; console.log('FAIL', name, '\n', e.message); }
    await context.close();
  };
  for (const route of ['/', '/en/']) {
    await test(`${route} desktop snaps scene by scene`, {width: 1440, height: 900}, route, async page => {
      assert.equal(await snapType(page), 'y mandatory');
      const tops = await page.evaluate(() => [...document.querySelectorAll('.home-scene')].map(s => Math.round(s.getBoundingClientRect().top + scrollY)));
      assert.ok(tops.length >= 5);
      for (const target of tops.slice(1, 3)) {
        await page.keyboard.press('PageDown');
        await page.waitForFunction(t => Math.abs(scrollY - t) <= 1, target, {timeout: 3000})
          .catch(async () => assert.fail(`PageDown should land on ${target}, got ${await page.evaluate(() => scrollY)}`));
        await page.waitForTimeout(700); // let the snap animation settle before the next key press
        assert.ok(Math.abs(await page.evaluate(() => scrollY) - target) <= 1, `Scene ${target} must stay aligned`);
      }
      await page.evaluate(() => { location.hash = '#contacts'; });
      await page.waitForFunction(() => Math.abs(scrollY - (document.getElementById('contacts').getBoundingClientRect().top + scrollY)) <= 1, null, {timeout: 3000})
        .catch(async () => assert.fail(`#contacts should align to the top, got ${await page.evaluate(() => scrollY)}`));
    });
    await test(`${route} mobile scrolls freely`, {width: 390, height: 844}, route, async page => {
      assert.equal(await snapType(page), 'none');
    });
  }
  await test('/artists.html desktop scrolls freely', {width: 1440, height: 900}, '/artists.html', async page => {
    assert.equal(await snapType(page), 'none');
  });
  await browser.close();
  console.log(failed ? `Home snap: ${failed} failed` : 'Home snap: all passed');
  process.exit(failed ? 1 : 0);
})();
