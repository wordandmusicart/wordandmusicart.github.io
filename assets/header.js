(() => {
  const header = document.querySelector('.hdr');
  if (!header) return;

  let frame = 0;
  const update = () => {
    frame = 0;
    header.style.setProperty('--header-progress', String(Math.min(1, Math.max(0, window.scrollY / 84))));
  };
  const onScroll = () => {
    if (!frame) frame = requestAnimationFrame(update);
  };

  update();
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('pageshow', update);
})();
