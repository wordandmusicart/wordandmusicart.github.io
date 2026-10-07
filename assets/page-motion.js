/* Photo readiness only. Native navigation owns the single page transition. */
(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  if (reduced.matches || !('IntersectionObserver' in window)) return;
  const pending = new Set();
  const timers = new Map();
  let prepareObserver;
  let stopped = false;

  const release = image => {
    clearTimeout(timers.get(image));
    timers.delete(image);
    pending.delete(image);
    image.removeAttribute('data-motion-pending');
    image.dataset.motionReady = '';
    prepareObserver?.unobserve(image);
  };
  const stop = () => {
    stopped = true;
    prepareObserver?.disconnect();
    [...pending].forEach(release);
    timers.forEach(clearTimeout);
    timers.clear();
  };
  const decode = async image => {
    if (stopped || !pending.has(image)) return;
    if (!image.naturalWidth) { release(image); return; }
    try { await image.decode(); } catch { /* Broken decoding must fail open. */ }
    release(image);
  };

  try {
    prepareObserver = new IntersectionObserver(entries => {
      for (const {target: image, isIntersecting} of entries) {
        if (!isIntersecting || stopped) continue;
        prepareObserver.unobserve(image);
        // Promote nearby photos only; a long gallery stays lazy.
        image.loading = 'eager';
        if (!pending.has(image)) continue;
        timers.set(image, setTimeout(() => release(image), 5000));
        if (image.complete) decode(image);
      }
    }, {rootMargin: '400px 0px'});
    for (const image of document.querySelectorAll('main img')) {
      if (image.closest('.logo, .lb')) continue;
      // Already-painted images must never be hidden or replayed by late JS.
      if (image.complete) { release(image); continue; }
      pending.add(image);
      image.dataset.motionPending = '';
      image.decoding = 'async';
      image.addEventListener('load', () => decode(image), {once: true});
      image.addEventListener('error', () => release(image), {once: true});
      prepareObserver.observe(image);
    }
    reduced.addEventListener('change', () => { if (reduced.matches) stop(); });
    addEventListener('pageshow', event => { if (event.persisted) stop(); });
  } catch {
    // Even a partial setup failure cannot leave photos hidden.
    stop();
  }
})();
