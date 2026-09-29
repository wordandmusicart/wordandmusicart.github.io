/* Shared navigation: floating header, direction-aware visibility, accessible menu. */
(() => {
  const header = document.querySelector('.hdr');
  if (!header) return;
  const nav = header.querySelector('#nav');
  const button = header.querySelector('.menu-btn');
  const mobile = matchMedia('(max-width:1100px)');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const subnav = document.querySelector('.subnav');
  const sections = subnav ? [...subnav.querySelectorAll('.links a[href^="#"]')]
    .map(link => ({ link, section: document.getElementById(link.hash.slice(1)) }))
    .filter(item => item.section) : [];
  let lastY = Math.max(0, window.scrollY);
  let direction = 0;
  let travel = 0;
  let frame = 0;
  let menuOpen = false;
  let currentSectionLink = null;

  function updateSubnav() {
    if (!sections.length) return;
    const marker = subnav.getBoundingClientRect().bottom + 24;
    let current = sections[0].link;
    for (const item of sections) {
      if (item.section.getBoundingClientRect().top <= marker) current = item.link;
    }
    if (current === currentSectionLink) return;
    for (const item of sections) {
      if (item.link === current) item.link.setAttribute('aria-current', 'location');
      else item.link.removeAttribute('aria-current');
    }
    currentSectionLink = current;
    const linkRect = current.getBoundingClientRect();
    const navRect = subnav.getBoundingClientRect();
    let scrollDelta = 0;
    if (linkRect.left < navRect.left + 12) scrollDelta = linkRect.left - navRect.left - 12;
    else if (linkRect.right > navRect.right - 12) scrollDelta = linkRect.right - navRect.right + 12;
    if (scrollDelta) subnav.scrollBy({ left: scrollDelta, behavior: reducedMotion.matches ? 'auto' : 'smooth' });
  }

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
    const y = Math.min(Math.max(0, window.scrollY), Math.max(0, document.documentElement.scrollHeight - innerHeight));
    const delta = y - lastY;
    if (y <= 220 || menuOpen || header.contains(document.activeElement)) showHeader(true);
    else if (delta) {
      const nextDirection = Math.sign(delta);
      if (nextDirection !== direction) { direction = nextDirection; travel = 0; }
      travel += Math.abs(delta);
      // Ignore small touch corrections and scroll bounce before reversing visibility.
      if (travel >= 24) showHeader(direction < 0);
    }
    if (y <= 220 || menuOpen) { direction = 0; travel = 0; }
    lastY = y;
    updateSubnav();
  }
  button?.addEventListener('click', () => setMenu(!menuOpen));
  nav?.addEventListener('click', e => {
    if (e.target.closest('a')) setMenu(false);
  });
  subnav?.addEventListener('click', e => {
    const link = e.target.closest('.links a[href^="#"]');
    if (!link) return;
    const target = document.getElementById(link.hash.slice(1));
    if (target) showHeader(target.getBoundingClientRect().top <= subnav.getBoundingClientRect().bottom);
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
  window.addEventListener('pageshow', () => { lastY = Math.max(0, scrollY); showHeader(true); updateSubnav(); });
  window.addEventListener('resize', updateSubnav);
  mobile.addEventListener('change', () => setMenu(false));
  showHeader(true);
  updateSubnav();
})();
