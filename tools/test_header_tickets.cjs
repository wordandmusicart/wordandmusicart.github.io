#!/usr/bin/env node
/* Header ticket buttons always open the organiser profile, with and without JavaScript.
 * SITE_URL=http://127.0.0.1:4175 node tools/test_header_tickets.cjs
 */
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/rusanivsky/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const BASE = process.env.SITE_URL || 'http://127.0.0.1:4175';
const PROFILE = 'https://eventmate.app/users/share/wordmusic';
(async () => {
  const browser = await chromium.launch();
  let failed = 0;
  const cases = [
    ['before the concert ends', '2026-10-15T19:00:00+03:00'],
    ['immediately before October 15 ends', '2026-10-15T19:29:59+03:00'],
    ['after October 15 ends', '2026-10-15T19:30:01+03:00'],
    ['before October 24 starts', '2026-10-24T15:59:59+03:00'],
    ['immediately before October 24 ends', '2026-10-24T17:09:59+03:00'],
    ['after the last concert ends', '2026-10-24T17:10:01+03:00'],
  ];
  for (const [label, time] of cases) {
    for (const javaScriptEnabled of [true, false]) for (const width of [390, 1440]) {
    for (const [route, locale] of [['/', 'uk'], ['/en/', 'en'], ['/concerts/vivre-aimer-rever.html', 'uk'], ['/en/artists.html', 'en']]) {
      const context = await browser.newContext({viewport: {width, height: 900}, javaScriptEnabled, locale: locale === 'en' ? 'en-US' : 'uk-UA', timezoneId: locale === 'en' ? 'UTC' : 'Europe/Kyiv'});
      const page = await context.newPage();
      try {
        if (javaScriptEnabled) await page.clock.setFixedTime(new Date(time));
        await page.goto(BASE + route, {waitUntil: 'load'});
        const hrefs = await page.$$eval('.hdr a.btn-acc', links => links.map(a => a.href));
        assert.equal(hrefs.length, 2, 'desktop and mobile header ticket buttons');
        assert.deepEqual([...new Set(hrefs)], [`${PROFILE}?locale=${locale}`]);
        console.log('PASS', route, label, width, javaScriptEnabled ? 'JS' : 'no-JS');
      } catch (e) { failed++; console.log('FAIL', route, label, width, javaScriptEnabled ? 'JS' : 'no-JS', '\n', e.message); }
      await context.close();
    }
  }
  }
  await browser.close();
  console.log(failed ? `Header tickets: ${failed} failed` : 'Header tickets: all passed');
  process.exit(failed ? 1 : 0);
})();
