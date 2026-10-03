#!/usr/bin/env node
/* Header ticket buttons follow the nearest concert still on sale.
 * SITE_URL=http://127.0.0.1:4175 node tools/test_header_tickets.cjs
 */
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/rusanivsky/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const BASE = process.env.SITE_URL || 'http://127.0.0.1:4175';
const EVENT = 'https://eventmate.app/events/share/na-krilah-kohanna-koncert-vokalnoi-muziki';
const PROFILE = 'https://eventmate.app/users/share/wordmusic';
(async () => {
  const browser = await chromium.launch();
  let failed = 0;
  const cases = [
    ['before the concert ends', '2026-10-15T19:00:00+03:00', EVENT],
    ['after the last concert ends', '2026-10-15T19:31:00+03:00', PROFILE],
  ];
  for (const [label, time, base] of cases) {
    for (const [route, locale] of [['/', 'uk'], ['/en/', 'en'], ['/concerts/vivre-aimer-rever.html', 'uk'], ['/en/artists.html', 'en']]) {
      const context = await browser.newContext({viewport: {width: 1440, height: 900}, locale: locale === 'en' ? 'en-US' : 'uk-UA', timezoneId: locale === 'en' ? 'UTC' : 'Europe/Kyiv'});
      const page = await context.newPage();
      try {
        await page.clock.setFixedTime(new Date(time));
        await page.goto(BASE + route, {waitUntil: 'load'});
        const hrefs = await page.$$eval('.hdr a.btn-acc', links => links.map(a => a.href));
        assert.equal(hrefs.length, 2, 'desktop and mobile header ticket buttons');
        assert.deepEqual([...new Set(hrefs)], [`${base}?locale=${locale}`]);
        console.log('PASS', route, label);
      } catch (e) { failed++; console.log('FAIL', route, label, '\n', e.message); }
      await context.close();
    }
  }
  await browser.close();
  console.log(failed ? `Header tickets: ${failed} failed` : 'Header tickets: all passed');
  process.exit(failed ? 1 : 0);
})();
