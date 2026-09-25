/* Photo viewer, same behaviour as rusanivsky.com:
   - any [data-lb] inside a [data-lb-group] opens the group full-screen;
   - the viewer loads the widest step of the srcset, not the thumbnail;
   - click the left/right half of the picture, arrow keys or a one-finger
     swipe turn the page; Esc closes; a pinch never turns the page. */
(function () {
  var lb = document.getElementById('lb');
  if (!lb) return;
  var root = document.documentElement;
  var img = lb.querySelector('.lb-stage img');
  var count = document.getElementById('lb-count');
  var cap = document.getElementById('lb-cap');
  var group = [], at = 0, opener = null;

  function render() {
    var it = group[at], widestUrl = '', widest = 0;
    if (it.srcset) {
      it.srcset.split(',').forEach(function (c) {
        var b = c.trim().split(/\s+/), w = parseInt(b[1], 10);
        if (w > widest) { widest = w; widestUrl = b[0]; }
      });
      img.srcset = it.srcset;
      img.sizes = widest ? widest + 'px' : '100vw';
    } else { img.removeAttribute('srcset'); img.removeAttribute('sizes'); }
    img.src = widestUrl || it.src;
    img.alt = it.alt;
    if (it.w && it.h) { img.width = it.w; img.height = it.h; }
    count.textContent = (at + 1) + ' / ' + group.length;
    cap.textContent = it.cap || '';
  }
  function open(items, i, src) {
    group = items; at = i; opener = src;
    lb.hidden = false; root.classList.add('no-scroll');
    render(); lb.querySelector('.lb-close').focus();
  }
  function close() {
    lb.hidden = true; root.classList.remove('no-scroll');
    if (opener) opener.focus();
  }
  function step(d) { at = (at + d + group.length) % group.length; render(); }
  function magnified() { var v = window.visualViewport; return !!v && v.scale > 1.01; }

  document.addEventListener('click', function (e) {
    var r = e.target.closest('.rest-toggle');
    if (r) {  // «Усі фото»: show the rest of the series as a gallery first
      var g = document.getElementById(r.getAttribute('aria-controls'));
      if (g) { g.hidden = false; r.setAttribute('aria-expanded', 'true'); r.hidden = true; }
      return;
    }
    var t = e.target.closest('[data-lb]');
    if (t) {
      e.preventDefault();
      var scope = t.closest('[data-lb-group]') || document;
      var all = [].slice.call(scope.querySelectorAll('[data-lb]')).filter(function (el) { return el.querySelector('img'); });
      var start = t.hasAttribute('data-lb-at') ? parseInt(t.getAttribute('data-lb-at'), 10) : all.indexOf(t);
      open(all.map(function (el) {
        var im = el.querySelector('img');
        return {
          src: im.getAttribute('src'), srcset: im.getAttribute('srcset') || '', alt: im.alt,
          w: parseInt(im.getAttribute('width'), 10) || 0, h: parseInt(im.getAttribute('height'), 10) || 0,
          cap: scope.getAttribute('data-lb-group') || ''
        };
      }), Math.max(0, start), t);
      return;
    }
    if (lb.hidden) return;
    if (e.target.closest('.lb-close')) return close();
    if (e.target.closest('[data-lb-prev]')) return step(-1);
    if (e.target.closest('[data-lb-next]')) return step(1);
    var stage = e.target.closest('.lb-stage');
    if (stage && !magnified()) {
      var b = stage.getBoundingClientRect(), back = e.clientX < b.left + b.width / 2;
      lb.setAttribute('data-side', back ? 'prev' : 'next');
      step(back ? -1 : 1);
    }
  });
  lb.addEventListener('pointermove', function (e) {
    if (e.pointerType !== 'mouse') return;
    var b = lb.querySelector('.lb-stage').getBoundingClientRect();
    lb.setAttribute('data-side', e.clientX < b.left + b.width / 2 ? 'prev' : 'next');
  });
  document.addEventListener('keydown', function (e) {
    if (lb.hidden) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') step(-1);
    else if (e.key === 'ArrowRight') step(1);
    else if (e.key === 'Tab') {
      var f = lb.querySelectorAll('button'), first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
  var x0 = null, pinched = false;
  lb.addEventListener('touchstart', function (e) {
    if (e.touches.length > 1) { pinched = true; x0 = null; return; }
    if (!pinched) x0 = e.changedTouches[0].clientX;
  }, { passive: true });
  lb.addEventListener('touchend', function (e) {
    if (pinched) { if (e.touches.length === 0) { pinched = false; x0 = null; } return; }
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 45 && !magnified()) step(dx < 0 ? 1 : -1);
    x0 = null;
  }, { passive: true });
})();
