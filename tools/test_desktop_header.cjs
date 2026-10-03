#!/usr/bin/env node
/* The desktop home header stays visible while scrolling; other pages and
 * mobile keep the direction-aware header.
 * SITE_URL=http://127.0.0.1:4175 node tools/test_desktop_header.cjs
 */
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/rusanivsky/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const BASE = process.env.SITE_URL || 'http://127.0.0.1:4175';
const visible = page => page.evaluate(() => {
  const h = document.querySelector('.hdr'), r = h.getBoundingClientRect();
  return !h.classList.contains('is-hidden') && !h.inert && r.top >= 0 && Number(getComputedStyle(h).opacity) > 0.99;
});
async function scrollDown(page) {
  // Instant scroll steps; the home page's scroll snap settles on a scene.
  for (let y = 300; y <= 2100; y += 300) {
    await page.evaluate(t => window.scrollTo({top: t, behavior: 'instant'}), y);
    await page.waitForTimeout(120);
  }
  await page.waitForTimeout(600);
}
(async () => {
  const browser = await chromium.launch();
  let failed = 0;
  const cases = [];
  for (const route of ['/', '/en/']) for (const [width, expected] of [[1440, true], [1280, true], [390, false]]) cases.push([route, width, expected]);
  for (const route of ['/concerts/on-the-wings-of-love.html', '/en/artists.html']) cases.push([route, 1440, false]);
  for (const [route, width, expected] of cases) {
    {
      const context = await browser.newContext({viewport: {width, height: 900}, userAgent: 'WordMusicAcceptanceBot'});
      const page = await context.newPage();
      try {
        await page.goto(BASE + route, {waitUntil: 'load'});
        await scrollDown(page);
        assert.equal(await visible(page), expected, `header visible after scrolling down at ${width}px`);
        console.log('PASS', route, width);
      } catch (e) { failed++; console.log('FAIL', route, width, '\n', e.message); }
      await context.close();
    }
  }
  await browser.close();
  console.log(failed ? `Desktop header: ${failed} failed` : 'Desktop header: all passed');
  process.exit(failed ? 1 : 0);
})();
