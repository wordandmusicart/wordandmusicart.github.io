(() => {
  const mark = document.querySelector('.mark-motion');
  if (!mark) return;

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const layers = [
    ['#wm_plane_01', -5.0, 2.2, 0.00075, 0.1],
    ['#wm_plane_02', 3.8, -2.8, 0.00091, 1.4],
    ['#wm_plane_03', -2.9, -3.5, 0.00066, 2.7],
    ['#wm_afterimage', 2.4, 1.9, 0.00083, 3.6],
    ['#wm_foreground', 4.4, -2.3, 0.00072, 4.8],
  ].map(([selector, x, y, speed, phase]) => {
    const element = mark.querySelector(selector);
    return { element, base: element.getAttribute('transform') || '', x, y, speed, phase };
  });
  const line = mark.querySelector('#wm_gesture');
  const originalLine = line.getAttribute('d');
  let hovering = false;
  let strength = 0;
  let lastTime = 0;
  let frame = 0;

  const reset = () => {
    layers.forEach(({ element, base }) => {
      if (base) element.setAttribute('transform', base);
      else element.removeAttribute('transform');
    });
    line.setAttribute('d', originalLine);
  };

  const tick = (time) => {
    frame = 0;
    if (reducedMotion.matches) {
      hovering = false;
      strength = 0;
      reset();
      return;
    }

    const elapsed = Math.min(50, time - (lastTime || time));
    lastTime = time;
    const target = hovering ? 1 : 0;
    strength += (target - strength) * (1 - Math.exp(-elapsed / (hovering ? 1100 : 950)));
    const motionTime = time * 1.12;

    layers.forEach(({ element, base, x, y, speed, phase }) => {
      const dx = strength * x * 1.15 * Math.sin(motionTime * speed + phase);
      const dy = strength * y * Math.cos(motionTime * speed * 0.83 + phase);
      element.setAttribute('transform', `${base} translate(${dx.toFixed(2)} ${dy.toFixed(2)})`.trim());
    });

    const wave = (value, phase) => (value + strength * 3.2 * Math.sin(motionTime * 0.0015 - phase)).toFixed(2);
    line.setAttribute('d', `M 403,260 C 447,${wave(296, 0)} 572,${wave(277, 0.8)} 649,${wave(247, 1.6)} C 754,${wave(207, 2.4)} 818,${wave(146, 3.2)} 934,${wave(134, 4)} C 1032,${wave(121, 4.8)} 1099,${wave(142, 5.6)} 1171,169`);

    if (hovering || strength > 0.003) frame = requestAnimationFrame(tick);
    else {
      strength = 0;
      lastTime = 0;
      reset();
    }
  };

  const start = () => {
    if (!frame && !reducedMotion.matches) frame = requestAnimationFrame(tick);
  };
  mark.addEventListener('pointerenter', (event) => {
    if (event.pointerType === 'touch' || reducedMotion.matches) return;
    hovering = true;
    mark.classList.add('is-hovered');
    start();
  });
  mark.addEventListener('pointerleave', () => {
    hovering = false;
    mark.classList.remove('is-hovered');
    start();
  });
  reducedMotion.addEventListener('change', () => {
    if (reducedMotion.matches) {
      hovering = false;
      strength = 0;
      mark.classList.remove('is-hovered');
      reset();
    }
  });
})();
