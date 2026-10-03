#!/usr/bin/env node
/* Browser acceptance test for random past concerts on home scene.
 * SITE_URL=http://127.0.0.1:4175 node tools/test_home_archive_random.cjs
 */
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/rusanivsky/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const BASE = process.env.SITE_URL || 'http://127.0.0.1:4175';

(async () => {
  const browser = await chromium.launch();
  let failed = 0;

  const test = async (name, fn) => {
    const context = await browser.newContext({viewport: {width: 1440, height: 900}, locale: 'uk-UA', timezoneId: 'Europe/Kyiv'});
    const page = await context.newPage();
    try {
      await fn(page);
      console.log('PASS', name);
    } catch (e) {
      failed++;
      console.log('FAIL', name, '\n', e.message);
    }
    await context.close();
  };

  for (const route of ['/', '/en/']) {
    await test(`${route} renders exactly 3 valid past concert cards at runtime`, async page => {
      await page.goto(BASE + route, {waitUntil: 'networkidle'});
      const cards = await page.evaluate(() => {
        const list = document.querySelectorAll('#past-concerts .cards3 .card');
        return Array.from(list).map(card => {
          const link = card.querySelector('a.pic');
          const img = card.querySelector('a.pic img');
          const meta = card.querySelector('.meta');
          const title = card.querySelector('a.t');
          return {
            hasLink: !!link && !!link.getAttribute('href'),
            hasImg: !!img && !!img.getAttribute('src'),
            hasMeta: !!meta && meta.textContent.trim().length > 0,
            hasTitle: !!title && title.textContent.trim().length > 0,
            titleText: title ? title.textContent.trim() : ''
          };
        });
      });

      assert.equal(cards.length, 3, `Expected 3 cards in #past-concerts, got ${cards.length}`);
      for (let i = 0; i < cards.length; i++) {
        assert.ok(cards[i].hasLink, `Card ${i} missing valid link`);
        assert.ok(cards[i].hasImg, `Card ${i} missing valid img`);
        assert.ok(cards[i].hasMeta, `Card ${i} missing meta`);
        assert.ok(cards[i].hasTitle, `Card ${i} missing title`);
      }
    });
  }

  await browser.close();
  console.log(failed ? `Archive random test: ${failed} failed` : 'Archive random test: all passed');
  process.exit(failed ? 1 : 0);
})();
