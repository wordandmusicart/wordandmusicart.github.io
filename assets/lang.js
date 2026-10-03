/* Site language on arrival at a Ukrainian (default) address: visitors in
   Ukraine get Ukrainian; visitors abroad get Ukrainian if their device
   language is Ukrainian, otherwise English. /en/ addresses stay English.
   A language picked with the UA/EN switch is remembered. */
(function () {
  var KEY = 'wm-lang';
  var page = document.documentElement.lang === 'en' ? 'en' : 'uk';

  function save(lang) { try { localStorage.setItem(KEY, lang); } catch (e) {} }
  function load() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('.lang a[hreflang]');
    if (a) save(a.getAttribute('hreflang') === 'en' ? 'en' : 'uk');
  });

  if (/bot|crawl|spider|slurp|lighthouse|preview|google-inspectiontool|googleother/i.test(navigator.userAgent)) return;

  var want = load();
  // An /en/ address is an explicit English link (e.g. shared with a guest in
  // Kyiv): without a remembered choice it is never switched to Ukrainian.
  if (want !== 'uk' && want !== 'en' && page === 'en') return;
  if (want !== 'uk' && want !== 'en') {
    var tz = '';
    try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) {}
    var inUkraine = /^Europe\/(Kyiv|Kiev|Uzhgorod|Zaporozhye|Simferopol)$/.test(tz);
    var langs = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ''];
    var deviceUk = String(langs[0] || '').toLowerCase().indexOf('uk') === 0;
    want = inUkraine || deviceUk ? 'uk' : 'en';
  }
  if (want === page) return;

  var alt = document.querySelector('link[rel="alternate"][hreflang="' + want + '"]');
  if (!alt) return;
  var url = new URL(alt.href, location.href);
  location.replace(url.pathname + location.search + location.hash);
})();
