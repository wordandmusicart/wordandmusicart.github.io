#!/usr/bin/env node
/* The ticket buttons link directly to the current concert in both languages. */
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/rusanivsky/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const BASE = process.env.SITE_URL || 'http://127.0.0.1:4175';

(async () => {
  const browser = await chromium.launch();
  try {
    for (const prefix of ['', '/en']) {
      for (const width of [390, 1440]) {
        for (const javaScriptEnabled of [true, false]) {
          const context = await browser.newContext({
            viewport: {width, height: 900}, javaScriptEnabled,
            locale: prefix ? 'en-US' : 'uk-UA', timezoneId: 'Europe/Kyiv',
          });
          try {
            const page = await context.newPage();
            const destination = prefix + '/concerts/towards-the-stars-29112026.html';
            for (const route of ['/', '/artists.html', '/concerts/vivre-aimer-rever-22112026.html']) {
              await page.goto(BASE + prefix + route, {waitUntil: 'domcontentloaded'});
              const buttons = page.locator('.hdr a.btn-acc');
              assert.deepEqual(await buttons.evaluateAll(links => links.map(link => link.getAttribute('href'))),
                [destination, destination]);
              if (width === 390 && javaScriptEnabled) await page.locator('.menu-btn').click();
              if (width === 1440 || javaScriptEnabled) {
                await buttons.filter({visible: true}).click();
                await page.waitForURL(BASE + destination);
              }
            }
          } finally {
            await context.close();
          }
        }
      }
    }
    console.log('Header ticket links passed in both languages');
  } finally {
    await browser.close();
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
