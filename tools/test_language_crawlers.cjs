#!/usr/bin/env node
/* Observable language/crawler acceptance; serve the site and set SITE_URL.
 * Official UA templates: https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers
 * Chrome's version placeholder is substituted with a fixed test version.
 */
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/rusanivsky/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const BASE = process.env.SITE_URL || 'http://127.0.0.1:4201';
const ORIGIN = 'https://wordandmusic.art';
const PROGRAMME = '/concerts/on-the-wings-of-love.html';
const CRAWLERS = [
  ['Google-InspectionTool desktop', 'Mozilla/5.0 (compatible; Google-InspectionTool/1.0)'],
  ['Google-InspectionTool smartphone', 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36 (compatible; Google-InspectionTool/1.0)'],
  ['GoogleOther', 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GoogleOther) Chrome/131.0.0.0 Safari/537.36'],
  ['Googlebot', 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'],
];
const HUMAN = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36';

async function visit(page, requested, expected, language) {
  try { await page.goto(BASE + requested, {waitUntil: 'domcontentloaded'}); }
  catch (error) { if (!error.message.includes('net::ERR_ABORTED')) throw error; }
  await page.locator('main').waitFor({state: 'attached'});
  await page.waitForFunction(() => document.readyState !== 'loading');
  assert.equal(new URL(page.url()).pathname, expected, `${requested}: requested language must resolve correctly`);
  const rendered = await page.evaluate(() => {
    const all = [];
    function collect(value) {
      if (Array.isArray(value)) { value.forEach(collect); return; }
      if (!value || typeof value !== 'object') return;
      const types = Array.isArray(value['@type']) ? value['@type'] : [value['@type']];
      if (types.includes('MusicEvent') || types.includes('WebSite')) all.push(value);
      Object.values(value).forEach(collect);
    }
    document.querySelectorAll('script[type="application/ld+json"]').forEach(node => collect(JSON.parse(node.textContent)));
    return {language: document.documentElement.lang, schemas: all};
  });
  assert.equal(rendered.language, language, `${expected}: visible language`);
  const schemaType = expected.endsWith('.html') ? 'MusicEvent' : 'WebSite';
  const relevant = rendered.schemas.filter(schema => schema['@type'] === schemaType);
  assert.equal(relevant.length, 1, `${expected}: one ${schemaType}`);
  assert.equal(relevant[0].inLanguage, language, `${expected}: JSON-LD language`);
  assert.equal(relevant[0].url, ORIGIN + expected, `${expected}: JSON-LD URL`);
}

(async () => {
  const browser = await chromium.launch({headless: true});
  let failures = 0;
  async function test(name, body) {
    try { await body(); console.log(`PASS ${name}`); }
    catch (error) { failures++; console.error(`FAIL ${name}\n${error.stack}`); }
  }
  try {
    for (const [name, userAgent] of CRAWLERS) {
      await test(`${name} retains requested UA/EN home and programme despite opposite device language`, async () => {
        for (const language of ['uk', 'en']) {
          const ctx = await browser.newContext({userAgent,
            locale: language === 'uk' ? 'en-US' : 'uk-UA',
            timezoneId: language === 'uk' ? 'UTC' : 'Europe/Kyiv'});
          ctx.setDefaultTimeout(5000);
          try {
            const page = await ctx.newPage();
            for (const route of ['/', PROGRAMME]) {
              const requested = language === 'uk' ? route : '/en' + route;
              await visit(page, requested, requested, language);
            }
          } finally { await ctx.close(); }
        }
      });
    }
    await test('Human with English device outside Ukraine redirects UA home and programme to EN', async () => {
      const ctx = await browser.newContext({userAgent: HUMAN, locale: 'en-US', timezoneId: 'UTC'});
      ctx.setDefaultTimeout(5000);
      try {
        const page = await ctx.newPage();
        for (const route of ['/', PROGRAMME]) await visit(page, route, '/en' + route, 'en');
      } finally { await ctx.close(); }
    });
    await test('Human in Ukraine keeps an explicit EN home and programme link', async () => {
      const ctx = await browser.newContext({userAgent: HUMAN, locale: 'uk-UA', timezoneId: 'Europe/Kyiv'});
      ctx.setDefaultTimeout(5000);
      try {
        const page = await ctx.newPage();
        for (const route of ['/', PROGRAMME]) await visit(page, '/en' + route, '/en' + route, 'en');
      } finally { await ctx.close(); }
    });
    await test('Human in Ukraine still gets UA at the default address', async () => {
      const ctx = await browser.newContext({userAgent: HUMAN, locale: 'en-US', timezoneId: 'Europe/Kyiv'});
      ctx.setDefaultTimeout(5000);
      try {
        const page = await ctx.newPage();
        for (const route of ['/', PROGRAMME]) await visit(page, route, route, 'uk');
      } finally { await ctx.close(); }
    });
    await test('Remembered human Ukrainian choice retains UA home and programme abroad', async () => {
      const ctx = await browser.newContext({userAgent: HUMAN, locale: 'en-US', timezoneId: 'UTC'});
      ctx.setDefaultTimeout(5000);
      try {
        await ctx.addInitScript(() => localStorage.setItem('wm-lang', 'uk'));
        const page = await ctx.newPage();
        for (const route of ['/', PROGRAMME]) await visit(page, route, route, 'uk');
        assert.equal(await page.evaluate(() => localStorage.getItem('wm-lang')), 'uk');
      } finally { await ctx.close(); }
    });
  } finally { await browser.close(); }
  console.log(`Language crawler acceptance: ${failures ? `${failures} failed` : 'all passed'}`);
  process.exitCode = failures ? 1 : 0;
})().catch(error => { console.error(error); process.exitCode = 1; });
