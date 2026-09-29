/* Reveal on entry without making content depend on JavaScript or hiding it in CSS. */
(() => {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      observer.unobserve(entry.target);
      entry.target.animate([
        { opacity: .35, transform: 'translateY(24px)' },
        { opacity: 1, transform: 'translateY(0)' }
      ], { duration: 700, easing: 'cubic-bezier(.16,1,.3,1)' });
    }
  }, { threshold: .12 });
  document.querySelectorAll('.home-scene:not(#intro) .sec-head,.home-scene:not(#intro) .cards3,.home-scene:not(#intro) .tiles,.home .about .g12,.home-contact .news .g12').forEach(el => observer.observe(el));
})();
