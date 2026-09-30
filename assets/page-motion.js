/* One owner for photo readiness and section reveals; navigation remains native. */
(() => {
  const root = document.documentElement;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  if (reduced.matches || !('IntersectionObserver' in window) || !Element.prototype.animate) {
    root.classList.remove('motion-enabled');
    return;
  }
  const animations = new Set();
  const visible = new Set();
  const ready = new WeakSet();
  const revealed = new WeakSet();
  const timers = new Map();
  const queue = new Set();
  let frame = 0;
  let arrival = () => {};
  let arrivalStarted = false;
  addEventListener('pagereveal', event => { if (!event.viewTransition) arrival(); });
  const animate = (element, keyframes, delay = 0) => {
    if (reduced.matches) return;
    const animation = element.animate(keyframes, {
      duration: 280, delay, easing: 'cubic-bezier(.22,1,.36,1)', fill: 'backwards'
    });
    animations.add(animation);
    animation.finished.catch(() => {}).finally(() => animations.delete(animation));
  };
  const failOpen = image => {
    clearTimeout(timers.get(image));
    timers.delete(image);
    revealed.add(image);
    image.dataset.motionReady = '';
    revealObserver.unobserve(image);
    prepareObserver.unobserve(image);
  };
  const flush = () => {
    frame = 0;
    const batch = [...queue].sort((a,b) => a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1);
    queue.clear();
    batch.forEach((image, index) => {
      if (revealed.has(image) || !visible.has(image)) return;
      failOpen(image);
      animate(image, [{opacity: 0}, {opacity: 1}], Math.min(index * 30, 80));
    });
  };
  const enqueue = image => {
    if (!ready.has(image) || !visible.has(image) || revealed.has(image)) return;
    queue.add(image);
    if (!frame) frame = requestAnimationFrame(flush);
  };
  const decode = async image => {
    if (revealed.has(image) || ready.has(image)) return;
    if (!image.naturalWidth) { failOpen(image); return; }
    try { await image.decode(); } catch { failOpen(image); return; }
    ready.add(image);
    clearTimeout(timers.get(image));
    timers.delete(image);
    enqueue(image);
  };
  const prepareObserver = new IntersectionObserver(entries => {
    for (const {target: image, isIntersecting} of entries) {
      if (!isIntersecting) continue;
      prepareObserver.unobserve(image);
      // Promote only nearby photos, keeping long galleries lazy.
      image.loading = 'eager';
      if (!ready.has(image) && !revealed.has(image)) {
        timers.set(image, setTimeout(() => failOpen(image), 5000));
        if (image.complete) decode(image);
      }
    }
  }, {rootMargin: '400px 0px'});
  const revealObserver = new IntersectionObserver(entries => {
    for (const {target: image, isIntersecting} of entries) {
      if (isIntersecting) { visible.add(image); enqueue(image); }
      else visible.delete(image);
    }
  }, {threshold: .01});
  const images = [...document.querySelectorAll('main img')].filter(image => !image.closest('.logo, .lb'));
  images.forEach(image => {
    image.decoding = 'async';
    image.addEventListener('load', () => decode(image), {once: true});
    image.addEventListener('error', () => failOpen(image), {once: true});
    prepareObserver.observe(image);
    revealObserver.observe(image);
    if (image.complete && image.naturalWidth) decode(image);
  });
  // Text is available immediately. Only sections entering from below get a small lift.
  const candidates = [...document.querySelectorAll('main h1, main .sec-head, .artists-intro > *, .artist-author-content > *, .artist-group-heading, .artist-row, .hero .main > *, .hero aside > *, .about .lab, .about h2, .about .txt')]
    .filter(el => !el.querySelector('img') && el.getBoundingClientRect().top >= innerHeight);
  const sectionObserver = new IntersectionObserver(entries => {
    let index = 0;
    entries.forEach(({target, isIntersecting}) => {
      if (!isIntersecting) return;
      sectionObserver.unobserve(target);
      animate(target, [{opacity: .35, transform: 'translateY(8px)'}, {opacity: 1, transform: 'none'}], Math.min(index++ * 30, 80));
    });
  }, {threshold: .06});
  candidates.filter(el => !candidates.some(parent => parent !== el && parent.contains(el)))
    .forEach(el => sectionObserver.observe(el));
  // No arrival animation on restored pages; the browser owns history and scroll.
  arrival = () => {
    if (arrivalStarted) return;
    arrivalStarted = true;
    if (performance.getEntriesByType('navigation')[0]?.type === 'back_forward') return;
    const main = document.querySelector('main');
    if (main) animate(main, [{opacity: .6}, {opacity: 1}]);
  };
  if (typeof window.__motionNativeArrival === 'boolean') {
    if (!window.__motionNativeArrival) arrival();
  } else if (!('onpagereveal' in window)) requestAnimationFrame(() => arrival());
  const stop = () => {
    root.classList.remove('motion-enabled');
    prepareObserver.disconnect(); revealObserver.disconnect(); sectionObserver.disconnect();
    cancelAnimationFrame(frame); queue.clear();
    timers.forEach(clearTimeout); timers.clear();
    animations.forEach(animation => animation.cancel()); animations.clear();
  };
  reduced.addEventListener('change', () => { if (reduced.matches) stop(); });
  addEventListener('pageshow', event => { if (event.persisted) stop(); });
  // Clear the head watchdog only after setup has successfully completed.
  clearTimeout(window.__motionWatchdog);
})();
