#!/usr/bin/env node
/* Contact sheet of every circular portrait, rendered by the real site CSS.
 * Crops are judged side by side, never alone (docs/design-system.md, «Портрети»).
 *   SITE_URL=http://127.0.0.1:4175 node tools/portrait_sheet.cjs [out.png] [--highlight id,id]
 */
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/rusanivsky/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const BASE = process.env.SITE_URL || 'http://127.0.0.1:4175';
const args = process.argv.slice(2);
const out = args.find(a => a.endsWith('.png')) || 'portrait-sheet.png';
const highlight = new Set((args[args.indexOf('--highlight') + 1] || '').split(',').filter(Boolean));
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({viewport: {width: 1440, height: 900}, deviceScaleFactor: 2, reducedMotion: 'reduce', userAgent: 'WordMusicAcceptanceBot'});
  const page = await context.newPage();
  await page.goto(BASE + '/artists.html', {waitUntil: 'networkidle'});
  await page.evaluate(async () => {
    for (const img of document.images) img.loading = 'eager';
    await Promise.all([...document.images].map(img => img.decode().catch(() => {})));
  });
  const cells = [];
  for (const row of await page.$$('article.artist-row')) {
    const id = await row.getAttribute('id');
    const portrait = await row.$('.artist-portrait');
    await portrait.scrollIntoViewIfNeeded();
    await page.waitForTimeout(250);
    const png = await portrait.screenshot();
    cells.push({id, src: 'data:image/png;base64,' + png.toString('base64')});
  }
  const sheet = await context.newPage();
  await sheet.setContent(`<body style="margin:0;background:#1c1c1c;font:12px system-ui;color:#ddd">
    <div style="display:grid;grid-template-columns:repeat(7,180px);gap:16px;padding:16px">${cells.map(c => `
    <figure style="margin:0;text-align:center"><img src="${c.src}" style="width:168px;height:168px;${highlight.has(c.id) ? 'outline:3px solid #fb8b3c;outline-offset:3px;border-radius:50%' : ''}">
    <figcaption>${c.id}</figcaption></figure>`).join('')}</div></body>`);
  await (await sheet.$('div')).screenshot({path: out});
  await browser.close();
  console.log(`${cells.length} portraits → ${out}`);
})();
