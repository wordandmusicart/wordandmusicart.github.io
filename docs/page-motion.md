Word&music motion brief, 2026-09-30
Scope: restrained transitions between pages and soft, fast photo loading on desktop/mobile, UA/EN. Preserve layout, crops, assets and text.
Contract: use standard browser navigation with native cross-document opacity transitions (max 240ms), stable header; arrival fallback where unsupported. One shared reveal controller, visible decoded images only, ordered batches with <=80ms stagger; only near-viewport images promoted from lazy. No movement/scaling of photos. No scroll hijacking or click delay.
Acceptance: delayed images stay reserved/hidden until ready then fade; broken images fail open; JS blocked/disabled and reduced motion leave content readable; preference changes cancel animations; restored pages and hash/language links work. Desktop/mobile representative routes, console errors, screenshot inspection and deployment verification required.
Decision: image decode and viewport intersection must both be ready; image placeholders keep existing dimensions. Never await an entire gallery. Existing artwork remains byte-identical.
Review: independent critic required explicit exclusion of logos/lightbox, error/timeout fail-open, ready-batch ordering instead of waiting for previous photos, and native/fallback ownership. Applied those boundaries.
Implementation: early head opt-in with a 3s script watchdog; each near-viewport photograph has a 5s readiness deadline. CSS never hides images without that opt-in. Decode failure/error exits pending immediately. Timers stop when decoded. Reduced-motion preference changes and BFCache restoration cancel pending animations. Photos animate opacity only, max 280ms + 80ms delay. Section lifts affect below-fold text only, excluding image ancestors. Native page fade lasts 180/240ms; unsupported browsers have a short arrival fade.
Validation: acceptance tests initially failed on undecoded-photo visibility before implementation (RED). Browser test runs cover 390px and 1440px and are part of deployment CI.
Final review: actual pagereveal.viewTransition determines ownership, rather than CSS feature detection. Chromium and WebKit passed 390px/1440px photo, error, decode rejection, history, native/fallback, reduced-motion, no-JS and script-failure tests. WebKit keeps finished browser transition objects; tests count active animations. Visual inspection confirmed stable header and unchanged desktop/mobile geometry. SEO (45 pages), structured data, images, fonts, landing/concert dates, existing theme/mobile-navigation checks passed.
Follow-up: capture pagereveal in the head to handle events arriving before deferred initialization; guard fallback arrival against duplicates. CI first release failed its direct-entry event wait; acceptance now covers delayed controller activation and releases the image gate before awaiting arrival.
Floating panels: header, concert subnav and ticket bar share the ticket bar's 90% background, 20px backdrop blur, border and shadow. Header glass lives directly on the panel instead of a nested pseudo-element. Ticket text inset is24px (20px at <=360px). Independent review and Chromium/WebKit in both themes at320/390/740/1440px verified matching styles, no overflow, no text/button overlap; screenshots inspected.

Desktop home scenes — 3 October 2026: the owner asked for slide-by-slide
scrolling on the desktop home page. This supersedes "no scroll hijacking"
for the home page only, using native CSS scroll snap (no wheel or key
interception): `scroll-snap-type: y mandatory` on the root and
`scroll-snap-stop: always` on each `.home-scene`, for viewports ≥901px wide
and ≥600px tall with a fine pointer. Mobile, touch and all other pages keep
free scrolling. The taller archive scene can still be scrolled through
before the next snap. `tools/test_home_snap.cjs` (CI) checks UA/EN desktop
PageDown/anchor landing and free scrolling on mobile and the artists page.

Desktop home header — 3 October 2026: on the UA/EN home page at desktop
widths (>1100px) the header no longer steps aside while scrolling (owner
request). Other pages and the mobile/tablet header keep the direction-aware
behaviour. `tools/test_desktop_header.cjs` (CI) covers both.
