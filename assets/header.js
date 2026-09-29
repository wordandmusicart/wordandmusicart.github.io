/* Shared navigation: floating header, direction-aware visibility, accessible menu. */
(() => {
  const header = document.querySelector('.hdr');
  if (!header) return;
  const nav = header.querySelector('#nav');
  const button = header.querySelector('.menu-btn');
  const mobile = matchMedia('(max-width:1100px)');
  let lastY = Math.max(0, window.scrollY);
  let frame = 0;
  let menuOpen = false;

  function showHeader(show) {
    header.classList.toggle('is-hidden', !show);
    // A translated header must not leave invisible links in the tab sequence.
    header.inert = !show;
  }
  function setMenu(open, returnFocus = false) {
    menuOpen = open && mobile.matches;
    nav?.classList.toggle('open', menuOpen);
    button?.setAttribute('aria-expanded', String(menuOpen));
    document.documentElement.classList.toggle('menu-open', menuOpen);
    if (menuOpen) showHeader(true);
    if (returnFocus) button?.focus({ preventScroll: true });
  }
  function update() {
    frame = 0;
    const y = Math.max(0, window.scrollY);
    const delta = y - lastY;
    if (y <= 220 || menuOpen || header.contains(document.activeElement)) showHeader(true);
    else if (Math.abs(delta) > 6) showHeader(delta < 0);
    if (Math.abs(delta) > 6 || y === 0) lastY = y;
  }
  button?.addEventListener('click', () => setMenu(!menuOpen));
  nav?.addEventListener('click', e => {
    if (e.target.closest('a')) setMenu(false);
  });
  document.addEventListener('click', e => {
    if (menuOpen && !header.contains(e.target)) setMenu(false);
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && menuOpen) { setMenu(false, true); return; }
    if (e.key !== 'Tab') return;
    showHeader(true);
    if (!menuOpen) return;
    const items = [...header.querySelectorAll('a,button')].filter(el => el.getClientRects().length);
    const first = items[0], last = items[items.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last?.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first?.focus(); }
  });
  header.addEventListener('focusin', () => showHeader(true));
  window.addEventListener('scroll', () => { if (!frame) frame = requestAnimationFrame(update); }, { passive: true });
  window.addEventListener('pageshow', () => { lastY = Math.max(0, scrollY); showHeader(true); });
  mobile.addEventListener('change', () => setMenu(false));
  showHeader(true);
})();
