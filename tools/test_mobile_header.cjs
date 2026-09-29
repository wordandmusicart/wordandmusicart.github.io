#!/usr/bin/env node
/* Mobile navigation regression checks. Run against a local server on :4175.
 * node tools/test_mobile_header.cjs
 * Optional SITE_URL and PLAYWRIGHT_MODULE override runtime locations.
 */
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/rusanivsky/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const BASE = process.env.SITE_URL || 'http://127.0.0.1:4175';

async function settleScroll(page, y) {
  await page.evaluate(async target => {
    window.scrollTo({top: target, behavior: 'instant'});
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  }, y);
  assert.equal(await page.evaluate(() => scrollY), y, 'The requested scroll must actually occur');
}
async function settledVisibility(page, visible) {
  await page.waitForFunction(expected => {
    const header = document.querySelector('.hdr');
    const rect = header.getBoundingClientRect();
    const opacity = Number(getComputedStyle(header).opacity);
    return expected ? !header.inert && rect.top >= 0 && opacity >= 0.99 : header.inert && rect.bottom <= 0 && opacity <= 0.01;
  }, visible, {timeout: 2500});
}

(async () => {
  const browser = await chromium.launch({headless: true});
  let failures = 0;
  async function test(name, body) {
    const context = await browser.newContext({viewport: {width: 390, height: 844}, userAgent: 'WordMusicAcceptanceBot'});
    context.setDefaultTimeout(4000);
    try {
      const page = await context.newPage();
      await body(page);
      console.log('PASS ' + name);
    } catch (error) {
      failures++;
      console.error('FAIL ' + name + '\n' + error.stack);
    } finally { await context.close(); }
  }
  try {
    for (const [language, route] of [['UA', '/'], ['EN', '/en/']]) {
      await test(`${language}: mobile language labels align and link has 44px tap target`, async page => {
        await page.goto(BASE + route);
        await page.locator('.menu-btn').click();
        assert.equal(await page.locator('.menu-btn').getAttribute('aria-expanded'), 'true');
        const result = await page.locator('.hdr .mobile-lang').evaluate(group => {
          const state = node => {
            const style = getComputedStyle(node), rect = node.getBoundingClientRect();
            // Range rectangles measure the text, independently of target padding.
            const range = document.createRange(); range.selectNodeContents(node);
            const text = range.getBoundingClientRect();
            return {fontSize: style.fontSize, lineHeight: style.lineHeight,
              center: text.y + text.height / 2, width: rect.width, height: rect.height,
              visible: rect.width > 0 && rect.height > 0};
          };
          return {current: state(group.querySelector('span')), alternate: state(group.querySelector('a'))};
        });
        assert.ok(result.current.visible && result.alternate.visible);
        assert.equal(result.current.fontSize, result.alternate.fontSize, 'UA/EN labels must have equal type size');
        assert.equal(result.current.lineHeight, result.alternate.lineHeight, 'UA/EN labels must have equal line height');
        assert.ok(Math.abs(result.current.center - result.alternate.center) <= 1, 'UA/EN text centres must align within 1px');
        assert.ok(result.alternate.width >= 44 && result.alternate.height >= 44,
          `Language tap area ${result.alternate.width.toFixed(1)} × ${result.alternate.height.toFixed(1)} must be at least 44 × 44px`);
      });
      await test(`${language}: header ignores ±8px noise and returns after sustained 32px upward scroll`, async page => {
        await page.goto(BASE + route);
        await settleScroll(page, 600);
        await settledVisibility(page, false);
        for (const y of [592, 600, 608, 600]) {
          await settleScroll(page, y);
          assert.equal(await page.locator('.hdr').evaluate(header => header.inert), true,
            `Hidden header must not toggle for direction noise at y=${y}`);
        }
        await settleScroll(page, 568);
        await settledVisibility(page, true);
        for (const y of [576, 568, 560, 568]) {
          await settleScroll(page, y);
          assert.equal(await page.locator('.hdr').evaluate(header => header.inert), false,
            `Visible header must not toggle for direction noise at y=${y}`);
        }
      });
    }
    await test('Reduced motion removes header hide/show transitions', async page => {
      await page.emulateMedia({reducedMotion: 'reduce'});
      await page.goto(BASE + '/');
      for (const y of [600, 560]) {
        await settleScroll(page, y);
        const durations = await page.locator('.hdr').evaluate(header => getComputedStyle(header).transitionDuration.split(',').map(value => parseFloat(value)));
        assert.ok(durations.every(duration => duration === 0), `Reduced-motion transition durations: ${durations}`);
        await settledVisibility(page, y === 560);
      }
    });
  } finally { await browser.close(); }
  console.log(`Mobile header acceptance: ${failures ? failures + ' failed' : 'all passed'}`);
  process.exitCode = failures ? 1 : 0;
})().catch(error => { console.error(error); process.exitCode = 1; });
