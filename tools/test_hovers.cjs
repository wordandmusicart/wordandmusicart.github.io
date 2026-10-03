#!/usr/bin/env node
/* Every interactive element answers the pointer with the shared hover language:
 * a visible change that eases in (300ms colour, 700ms photo zoom) — never instant.
 * SITE_URL=http://127.0.0.1:4175 node tools/test_hovers.cjs
 */
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/rusanivsky/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const BASE = process.env.SITE_URL || 'http://127.0.0.1:4175';
const CASES = [
  ['/', '.hdr nav a:not([aria-current])', 'text'],
  ['/', '.hdr a.btn-acc:not(.mobile-ticket)', 'fill'],
  ['/', '.hero .btn-o, .btn-o', 'fill'],
  ['/', '.about a', 'text'],
  ['/', '.venue-link', 'logo'],
  ['/', '.card .pic', 'photo'],
  ['/', '.next-banner', 'photo'],
  ['/concerts.html', 'button.chip:not([aria-pressed="true"])', 'outline'],
  ['/artists.html', '.artist-concerts summary', 'text'],
  ['/photo.html', '.pt', 'photo'],
  ['/photo/stabat-mater.html', '.pgall a', 'photo'],
  ['/video.html', '.vmain', 'photo'],
  ['/concerts/stabat-mater.html', 'a.lnk', 'text'],
  ['/concerts/on-the-wings-of-love.html', 'main a.btn:not(.btn-acc)', 'fill'],
];
const snapshot = el => {
  const target = el.matches('.venue-link') ? el.querySelector('.venue-logo img')
    : el.matches('.card .pic, .next-banner, .pt, .pgall a, .vmain') ? el.querySelector('img') : el;
  const cs = getComputedStyle(target);
  return {color: cs.color, bg: cs.backgroundColor, shadow: cs.boxShadow, transform: cs.transform, opacity: cs.opacity,
    duration: Math.max(...cs.transitionDuration.split(',').map(parseFloat)), property: cs.transitionProperty};
};
(async () => {
  const browser = await chromium.launch();
  let failed = 0;
  for (const scheme of ['light', 'dark']) {
    const context = await browser.newContext({viewport: {width: 1440, height: 900}, colorScheme: scheme, userAgent: 'WordMusicAcceptanceBot'});
    const page = await context.newPage();
    for (const [route, selector, kind] of CASES) {
      try {
        if (page.url() !== BASE + route) await page.goto(BASE + route, {waitUntil: 'load'});
        const el = page.locator(selector).first();
        await el.scrollIntoViewIfNeeded();
        await page.mouse.move(2, 2); await page.waitForTimeout(900);
        const before = await el.evaluate(snapshot);
        assert.ok(before.duration >= 0.29, `${selector}: transition ${before.duration}s on ${before.property}`);
        await el.hover(); await page.waitForTimeout(1000);
        const after = await el.evaluate(snapshot);
        const changed = {text: ['color'], fill: ['bg'], outline: ['color', 'shadow'], photo: ['transform', 'opacity'], logo: ['opacity']}[kind];
        for (const key of changed) assert.notEqual(after[key], before[key], `${selector}: ${key} must change on hover`);
        console.log('PASS', scheme, route, selector);
      } catch (e) { failed++; console.log('FAIL', scheme, route, selector, '\n ', e.message.split('\n')[0]); }
    }
    await context.close();
  }
  await browser.close();
  console.log(failed ? `Hovers: ${failed} failed` : 'Hovers: all passed');
  process.exit(failed ? 1 : 0);
})();
