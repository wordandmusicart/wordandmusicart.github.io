#!/usr/bin/env node
/* Observable concert-action and fact typography acceptance.
 * Serve the site; optionally set SITE_URL, SITE_ROOT and PLAYWRIGHT_MODULE.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/rusanivsky/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const ROOT = process.env.SITE_ROOT || path.resolve(__dirname, '..');
const BASE = process.env.SITE_URL || 'http://127.0.0.1:4201';
const WINGS = 'concerts/on-the-wings-of-love.html';
const redirects = {
  '/concerts/on-the-wings-of-love-25102026.html': '/concerts/on-the-wings-of-love-24102026.html',
  '/en/concerts/on-the-wings-of-love-25102026.html': '/en/concerts/on-the-wings-of-love-24102026.html',
};
const VIVRE = 'concerts/vivre-aimer-rever.html';
const TICKET = 'https://eventmate.app/events/share/na-krilah-kohanna-koncert-vokalnoi-muziki';
const WINGS24 = 'concerts/on-the-wings-of-love-24102026.html';
const TICKET24 = TICKET + '-v-budinku-vcenih';
const programmeRoutes = ['/concert.html', '/en/concert.html', ...['concerts', 'en/concerts'].flatMap(directory =>
  fs.readdirSync(path.join(ROOT, directory)).filter(file => file.endsWith('.html')).map(file => '/' + directory + '/' + file))];

async function open(page, route) {
  await page.goto(BASE + route, {waitUntil: 'domcontentloaded'});
  if (redirects[route]) {
    const destination = BASE + redirects[route];
    await page.waitForURL(destination, {waitUntil: 'domcontentloaded'});
    assert.equal(page.url(), destination, `${route}: preserve language on date redirect`);
  }
  await page.evaluate(() => document.fonts.ready);
}
async function scroll(page, fraction) {
  await page.evaluate(async progress => {
    const maximum = document.documentElement.scrollHeight - innerHeight;
    window.scrollTo({top: maximum * progress, behavior: 'instant'});
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  }, fraction);
}
(async () => {
  const browser = await chromium.launch({headless: true});
  let failures = 0;
  async function test(name, width, body) {
    const ctx = await browser.newContext({viewport: {width, height: 844},
      userAgent: 'WordMusicAcceptanceBot', reducedMotion: 'reduce'});
    ctx.setDefaultTimeout(5000);
    try { await body(await ctx.newPage()); console.log(`PASS ${name}`); }
    catch (error) { failures++; console.error(`FAIL ${name}\n${error.stack}`); }
    finally { await ctx.close(); }
  }
  try {
    for (const prefix of ['', 'en/']) for (const route of ['concert.html', WINGS24]) {
      for (const width of [320, 390, 900, 1440]) {
        await test(`${prefix + route} archived concert retains usable navigation without sale actions at ${width}px`, width, async page => {
          await open(page, '/' + prefix + route);
          assert.equal(await page.locator('.sticky-buy').count(), 0);
          assert.equal(await page.locator('a[href*="eventmate.app"]').count(), 0);
          assert.equal(await page.locator('.status').count(), 0);
          for (const identity of ['program', 'artists', 'venue']) {
            const link = page.locator(`.subnav .links a[href="#${identity}"]`);
            assert.equal(await link.count(), 1);
            await link.click();
            assert.equal(new URL(page.url()).hash, '#' + identity);
            assert.ok(await page.locator('#' + identity).isVisible());
          }
          for (const fraction of [0, 0.5, 1]) {
            await scroll(page, fraction);
            assert.equal(await page.locator('.sticky-buy').count(), 0);
          }
        });
      }
    }
    for (const prefix of ['', 'en/']) {
      await test(`${prefix + VIVRE} archive has no ticket bar and no empty mobile programme CTA`, 390, async page => {
        await open(page, '/' + prefix + VIVRE);
        assert.equal(await page.locator('.sticky-buy').count(), 0);
        assert.equal(await page.locator('main a[href*="eventmate.app/events/"]').count(), 0);
        const cta = page.locator('.c-hero .c-cta');
        assert.equal(await cta.count(), 1);
        const state = await cta.evaluate(node => ({display: getComputedStyle(node).display, height: node.getBoundingClientRect().height}));
        assert.equal(state.display, 'none', 'Hiding only the child leaves an empty hero CTA margin');
        assert.equal(state.height, 0);
        await page.setViewportSize({width: 1440, height: 844});
        assert.ok(await cta.locator('.btn-o[href="#program"]').isVisible(), 'Desktop archive programme action remains available');
      });
    }
    for (const width of [390, 1440]) {
      await test(`all concert facts use equal Date/Time/Price font sizes at ${width}px`, width, async page => {
        for (const route of programmeRoutes) {
          await open(page, route);
          const sizes = await page.locator('.c-hero .facts').evaluate(block => {
            const result = {};
            for (const dt of block.querySelectorAll('dt')) {
              const label = dt.textContent.trim();
              if (!['Дата', 'Час', 'Ціна', 'Date', 'Time', 'Price'].includes(label)) continue;
              const dd = dt.nextElementSibling;
              const renderedText = dd.querySelector('.time-range,.price-range') || dd;
              result[label] = parseFloat(getComputedStyle(renderedText).fontSize);
            }
            return result;
          });
          const date = sizes['Дата'] ?? sizes.Date;
          assert.ok(Number.isFinite(date), `${route}: date fact must be present`);
          for (const [label, size] of Object.entries(sizes))
            assert.ok(Math.abs(size - date) <= 0.2, `${route}: ${label} ${size}px must match Date ${date}px`);
        }
      });
    }
  } finally { await browser.close(); }
  console.log(`Mobile concert actions: ${failures ? `${failures} failed` : 'all passed'}`);
  process.exitCode = failures ? 1 : 0;
})().catch(error => { console.error(error); process.exitCode = 1; });
