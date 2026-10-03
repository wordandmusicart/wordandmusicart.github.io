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
const VIVRE = 'concerts/vivre-aimer-rever.html';
const TICKET = 'https://eventmate.app/events/share/na-krilah-kohanna-koncert-vokalnoi-muziki';
const ticketed = ['', 'en/'].flatMap(prefix => ['concert.html', WINGS].map(route => ({
  route: '/' + prefix + route, lang: prefix ? 'en' : 'uk',
})));
const programmeRoutes = ['/concert.html', '/en/concert.html', ...['concerts', 'en/concerts'].flatMap(directory =>
  fs.readdirSync(path.join(ROOT, directory)).filter(file => file.endsWith('.html')).map(file => '/' + directory + '/' + file))];

async function open(page, route) {
  await page.goto(BASE + route, {waitUntil: 'domcontentloaded'});
  await page.evaluate(() => document.fonts.ready);
}
async function scroll(page, fraction) {
  await page.evaluate(async progress => {
    const maximum = document.documentElement.scrollHeight - innerHeight;
    window.scrollTo({top: maximum * progress, behavior: 'instant'});
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  }, fraction);
}
async function sticky(page, lang, where) {
  const bar = page.locator('.sticky-buy');
  assert.equal(await bar.count(), 1, 'A ticketed programme needs one floating purchase bar');
  assert.ok(await bar.isVisible(), `${where}: purchase bar must remain visible`);
  assert.equal(await bar.locator('a').getAttribute('href'), `${TICKET}?locale=${lang}`);
  assert.match(await bar.innerText(), /15\.10/);
  assert.match(await bar.innerText(), /18:00\s*[–—-]\s*19:30/);
  const geometry = await bar.evaluate(node => {
    const rect = element => {
      const box = element.getBoundingClientRect();
      return {left: box.left, right: box.right, top: box.top, bottom: box.bottom, width: box.width, height: box.height};
    };
    const button = node.querySelector('a');
    const summary = [...node.children].find(child => child !== button);
    const range = document.createRange(); range.selectNodeContents(summary);
    const text = range.getBoundingClientRect();
    const buttonRange = document.createRange(); buttonRange.selectNodeContents(button);
    const buttonText = buttonRange.getBoundingClientRect();
    return {position: getComputedStyle(node).position, bar: rect(node), button: rect(button),
      text: {left: text.left, right: text.right, top: text.top, bottom: text.bottom},
      buttonText: {left: buttonText.left, right: buttonText.right},
      width: innerWidth, height: innerHeight,
      footerControls: [...document.querySelectorAll('footer a, footer button')].map(rect)};
  });
  assert.equal(geometry.position, 'fixed', `${where}: bar must be anchored to the viewport`);
  const {bar: box, button, text} = geometry;
  assert.ok(box.left >= 0 && box.right <= geometry.width + 1 && box.top >= 0 && box.bottom <= geometry.height + 1,
    `${where}: bar must fit the viewport: ${JSON.stringify(geometry)}`);
  assert.ok(geometry.height - box.bottom <= 80, `${where}: bar belongs near the viewport bottom`);
  assert.ok(button.left >= box.left && button.right <= box.right + 1 && button.top >= box.top && button.bottom <= box.bottom + 1,
    `${where}: purchase button must fit inside the bar`);
  assert.ok(text.right <= button.left - 1 && text.left >= box.left && text.top >= box.top - 1 && text.bottom <= box.bottom + 1,
    `${where}: concert summary must fit without overlapping the button`);
  assert.ok(geometry.buttonText.left >= button.left - 1 && geometry.buttonText.right <= button.right + 1,
    `${where}: the button label must fit`);
  if (where === 'end') {
    for (const control of geometry.footerControls) {
      const overlaps = control.width > 0 && control.height > 0 && control.right > box.left && control.left < box.right
        && control.bottom > box.top && control.top < box.bottom;
      assert.equal(overlaps, false, 'The floating purchase bar must leave footer controls usable at the page end');
    }
  }
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
    for (const {route, lang} of ticketed) {
      for (const width of [320, 390, 900]) {
        await test(`${route} ${width}px floating ticket stays visible, fits, and clears footer`, width, async page => {
          await open(page, route);
          for (const [where, fraction] of [['initial', 0], ['middle', 0.5], ['end', 1]]) {
            await scroll(page, fraction);
            await sticky(page, lang, where);
          }
        });
      }
      await test(`${route} mobile hides duplicate hero links and keeps subnav programme/artists usable`, 390, async page => {
        await open(page, route);
        const heroBuy = page.locator('.c-hero .c-cta .btn');
        assert.ok(await heroBuy.isVisible(), 'The hero purchase action remains available');
        assert.equal(await heroBuy.getAttribute('href'), `${TICKET}?locale=${lang}`);
        for (const identity of ['program', 'artists']) {
          assert.equal(await page.locator(`.c-hero .c-cta .btn-o[href="#${identity}"]`).isVisible(), false,
            `The duplicated hero ${identity} link should be hidden on mobile`);
          const link = page.locator(`.subnav .links a[href="#${identity}"]`);
          await link.click();
          assert.equal(new URL(page.url()).hash, '#' + identity);
          assert.ok(await page.locator('#' + identity).isVisible());
        }
      });
      await test(`${route} desktop hides floating ticket and preserves hero programme/artists links`, 1440, async page => {
        await open(page, route);
        assert.equal(await page.locator('.sticky-buy').isVisible(), false);
        for (const identity of ['program', 'artists'])
          assert.ok(await page.locator(`.c-hero .c-cta .btn-o[href="#${identity}"]`).isVisible());
      });
    }
    for (const prefix of ['', 'en/']) {
      await test(`${prefix + VIVRE} archive has no ticket bar and no empty mobile programme CTA`, 390, async page => {
        await open(page, '/' + prefix + VIVRE);
        assert.equal(await page.locator('.sticky-buy').count(), 0);
        assert.equal(await page.locator('a[href*="eventmate.app/events/"]').count(), 0);
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
