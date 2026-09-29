# Landing and artists — 2026-09-29

## Brief and vocabulary
A “scene” is a large, self-contained section in continuous natural scrolling, not a snapped slide. Preserve Word&music typography, colours, mark, source artwork and concert facts. Make the homepage read as five scenes. Add an archive-wide directory of artists with source-backed identities and photographs. Header hides on downward scroll and returns upward (confirmed by user).

## Scope / acceptance contract
AC1. UA and EN home have exactly five scenes in this order: introduction/current concert; about; past concerts; combined photo/video; contacts with footer. No repertoire block or menu link remains. Preserve current concert tickets and programme access.
AC2. Site-wide navigation starts Concerts, then Artists, Photo, Video, About, Contacts, with language and ticket controls retained. Existing page active states remain correct. New artists pair participates in language navigation and sitemap.
AC3. Desktop header is a centered rounded floating capsule, fits its contents, hides after downward scrolling past 220px, reappears on upward scrolling; visible while keyboard focused or menu open. Mobile navigation remains usable including Escape and language choice. No hidden focusable navigation.
AC4. CTA buttons are capsules. Desktop home scenes use at least viewport height without clipping content; mobile/short windows expand naturally. No forced scroll snapping. Motion honours reduced-motion and does not hide content if JavaScript fails.
AC5. Artists includes every named performer credited by the concert archive and the author Hennadii Taraniuk, grouping confirmed roles without invented biographies or current-employment claims. Portraits require explicit source attribution; unknown identity/photo must not be fabricated. Existing image originals/metadata are preserved.
AC6. Responsive and dark/light layouts work at 390, 768, 1024, 1440 widths, including EN; no document horizontal overflow, no clipped heads, no inaccessible CTA. Existing SEO, responsive-image, font, structured-data and event-date checks pass.

## Non-goals / prohibitions
No new framework/backend/API, no new palette/fonts, no Sora imagery, no poster recropping, no fabricated artist data or face recognition, no autoplay/scroll locking, no unrelated archive changes. Round buttons are explicitly requested. Do not convert all imagery/cards into rounded cards.

## Architecture / data contract
Keep static paired HTML and shared CSS/JS. Homepage `.home-scene` elements define the five scenes with ordered IDs `intro`, `about`, `past-concerts`, `media`, `contacts`. Shared header owns scroll visibility and mobile-menu accessibility. Artist records retain UA/EN name, evidenced role, source concert URLs, and optional explicitly attributed portrait path; HTML is indexable without JS. No database/API is introduced.

## Tasks / verification
1. Independently review this contract; write failing acceptance checks from AC1–AC4 before implementation.
2. Implement shared navigation/header and five home scenes (AC1–AC4), then bilingual artist directory (AC5).
3. Run acceptance/production gates, inspect browser screenshots and keyboard/mobile behaviour (AC6), independent critique and fixes.
4. Commit, PR, merge and verify deployed pages and assets.

## Decision/review log
- Fresh production clone used because old local folder points to obsolete staging and contains unrelated uncommitted archive work.
- User confirmed all archive participants and header return on upward scrolling.
- Portrait completeness depends on evidence; resolve missing attributions before making public identity claims.
- Independent acceptance author captured RED (5 checks; 48 expected missing-feature failures), then GREEN after implementation. Gate is included in the deploy workflow.
- Portrait audit: 29 people (28 archive participants plus current violinist); 15 explicitly attributed images, 14 text-only entries pending a supplied portrait source. Source poster/cover details are CSS views of explicitly labelled images; original files are unchanged.
- Mobile Contact reference inspected at 390×844: inset capsule, circular menu control, naturally flowing sections. Applied this navigation principle in both languages.
- Independent browser critic verified header direction/keyboard/menu behaviour and found a head crop in Mykola's portrait; corrected its object-position to the top.
- GREEN: 5 acceptance tests; SEO 43 pages; responsive-image and font checks; structured data; event dates; archive/venue coverage; deterministic artist-page rebuild; git diff whitespace check.
- Visual review: Chromium UA/EN, light/dark, widths 390/768/1024/1101/1440, short 600px window; desktop/mobile menus and keyboard, existing concert/photo pages. WebKit runtime unavailable, so Safari rendering is not claimed.
- Independent final review found no remaining blockers in implemented layout; missing 14 portraits remains an explicit content limitation.

## Follow-up polish — 2026-09-29
- Keep the existing vertical centring; user withdrew the request to move compositions upward.
- Every absent artist photo gets a neutral grey circle aligned with real portraits. Remove the baked-in source-art rings through presentation crop only; do not change original images.
- Add the rusanivsky.com-style Auto/Light/Dark icon control beside Privacy on every UA/EN footer. Auto follows the OS; manual choice persists across navigation/reload. Logos, theme pictures, browser theme colour and SVG respond to the selected effective theme.
- Header hide animation becomes gentler; reduced-motion remains immediate.
- Verify new theme behaviour with independent failing acceptance tests, then visual checks of portrait edges, scene position, both languages/themes and header movement. Publish after gates pass.

- Added quick sequential entrances: 320ms opacity/transform, 40ms stagger capped at 120ms, once per element, reduced-motion disabled, no layout-dependent animation or persistent hidden styles. Performance verification compares the same local page with animation enabled/disabled under CPU throttling.
- User withdrew the About colour change; retain the original background. Homepage heading is now Медіа / Media.

- Mobile regression RED: unequal language font sizes and premature visibility after an 8px scroll reversal. GREEN: both labels 14px with 44px touch targets; 24px directional threshold filters touch corrections and clamped scroll bounds filter overscroll. Five browser checks pass in UA/EN including reduced motion.
- Independent portrait review requested less inset for Ponomarenko; changed only that crop to .015.
- Local Chromium mobile performance, CPU 4x, three paired animation on/off runs: animation CLS 0, no long tasks, no frames over 50ms; median LCP 104ms vs100ms and frame p95 9.3ms vs9.4ms. Local measurements are regression evidence, not production field scores. Entrance script adds 1.9KB uncompressed.
- Theme checks pass on all43 footers and cover OS changes, persistence, blocked storage, assets and reduced motion. Browser regressions now run in deployment CI.

## Editorial originality audit
- Preserve authored mark, display typography, posters, five scenes, rounded controls and existing colour/centred layout.
- Independent critique identified generic About contrast-slogan and repeated storytelling claims. Replace with concrete musical forms, the named spoken-word author and the archive's actual contents; mirror UA/EN.
- Artists introduction now identifies vocalists, instrumentalists and the project author rather than repeating the brand premise. Avoid unsupported plural readers.
- Rename the Media section's video-only destination to All videos / Усі відео.
- No additional decorative components or animation dependencies introduced.
