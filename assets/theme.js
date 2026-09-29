/* Runs before CSS to restore a saved theme without a light/dark flash. */
(() => {
  const root = document.documentElement;
  const system = matchMedia('(prefers-color-scheme: dark)');
  const key = 'wm-theme';
  function stored() {
    try { const value = localStorage.getItem(key); return ['light', 'dark'].includes(value) ? value : 'auto'; }
    catch { return 'auto'; }
  }
  function paint(mode) {
    root.dataset.theme = mode;
    const dark = mode === 'dark' || (mode === 'auto' && system.matches);
    document.querySelectorAll('meta[name="theme-color"]').forEach(meta => { meta.content = dark ? '#1C1C1C' : '#F5F5F5'; });
    document.querySelectorAll('[data-theme-mode]').forEach(button => { button.setAttribute('aria-pressed', String(button.dataset.themeMode === mode)); });
    document.querySelectorAll('picture source[media],picture source[data-theme-media]').forEach(source => {
      const original = source.dataset.themeMedia || source.media;
      if (!original.includes('prefers-color-scheme')) return;
      source.dataset.themeMedia = original;
      source.media = mode === 'auto' ? original : ((original.includes('dark') === dark) ? 'all' : 'not all');
    });
  }
  paint(stored());
  document.addEventListener('DOMContentLoaded', () => paint(root.dataset.theme));
  system.addEventListener('change', () => { if (root.dataset.theme === 'auto') paint('auto'); });
  window.addEventListener('storage', event => { if (event.key === key || event.key === null) paint(stored()); });
  document.addEventListener('click', event => {
    const button = event.target.closest('[data-theme-mode]');
    if (!button) return;
    const mode = button.dataset.themeMode;
    if (!['auto', 'light', 'dark'].includes(mode)) return;
    try { if (mode === 'auto') localStorage.removeItem(key); else localStorage.setItem(key, mode); } catch { /* Session-only when storage is unavailable. */ }
    paint(mode);
  });
})();
