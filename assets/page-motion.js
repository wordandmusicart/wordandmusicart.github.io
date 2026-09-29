/* Quick one-shot sequences. Only compositor properties; no hidden-content CSS. */
(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  if (reduced.matches || !('IntersectionObserver' in window) || !Element.prototype.animate) return;
  const animations = new Set();
  const selectors = document.body.classList.contains('home')
    ? '.hero .main > *, .hero aside > *, .about .lab, .about h2, .about .txt, .home-archive .sec-head, .home-archive .card, .home-media .sec-head, .home-media .tile, .home-contact .news .l, .home-contact .news .col'
    : '.artists-intro > *, .artist-author-content > *, .artist-author-photo, .artist-group-heading, .artist-row, main h1, main .sec-head, main .upc, main .c-hero .facts, main .c-hero figure, main .tabs';
  const candidates = [...document.querySelectorAll(selectors)];
  // Avoid animating a parent and its child together.
  const targets = candidates.filter(el => !candidates.some(parent => parent !== el && parent.contains(el)));
  const observer = new IntersectionObserver(entries => {
    let sequence = 0;
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      observer.unobserve(entry.target);
      if (reduced.matches) continue;
      const animation = entry.target.animate([
        { opacity: 0, transform: 'translateY(10px)' },
        { opacity: 1, transform: 'translateY(0)' }
      ], { duration: 320, delay: Math.min(sequence++, 3) * 40, easing: 'cubic-bezier(.16,1,.3,1)', fill: 'backwards' });
      animations.add(animation);
      animation.finished.catch(() => {}).finally(() => animations.delete(animation));
    }
  }, { threshold: .06 });
  targets.forEach(el => observer.observe(el));
  reduced.addEventListener('change', () => {
    if (!reduced.matches) return;
    observer.disconnect();
    animations.forEach(animation => animation.cancel());
    animations.clear();
  });
})();
