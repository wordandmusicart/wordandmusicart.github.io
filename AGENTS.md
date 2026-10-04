# word&music site — working rules

Canonical rules for every agent (Codex, Claude, anyone) working on
wordandmusic.art. `CLAUDE.md` only imports this file — edit rules here.

## Read first

1. `AGENTS.md` — this file: process and content rules.
2. `docs/design-system.md` — tokens, type, hovers, components, portrait
   standard. A new page or block is built only from what is described there.
3. `docs/lessons-learned.md` — what the owner has had to repeat, and why.
   A correction requested twice → add a row there and a rule here.
4. `README.md` — images, structured data, fonts, concert photos.

## Process

- Do only what was asked. Anything not requested (removing metadata,
  renaming, re-encoding, dropping content, re-composing, extra processing)
  needs the owner's OK first. «Заміна» means replace the files with the same
  names — nothing is rearranged or redrawn.
- When a request is ambiguous, ask before expensive work (downloads,
  conversions). Ask only about facts that are missing; do not ask what the
  site, these docs or the conversation already answer; no rhetorical
  questions.
- Any visual change: screenshots before/after at 390 px and 1440 px, light
  and dark theme, before publishing. Coordinates and HTTP 200 are not proof.
- Publish right away: after a change is verified, push, open a PR,
  squash-merge into `main` (GitHub Pages deploys from `main`), wait for the
  deploy and check the live page.
- Production only: wordandmusic.art. There is no staging site.
- Pages come in pairs: every change to a UA page (`/*.html`) goes into its
  EN twin (`/en/*.html`) too (`check_style.py` fails on a missing twin).
- Nothing is invented (same rule as rusanivsky.com): titles, names, roles,
  dates, venues, durations and descriptions come from a real source
  (YouTube, posters, the organisers). Unknown → leave it out, or a neutral
  grey placeholder for a missing photo.

## Gates (all run in CI, `.github/workflows/deploy-pages.yml`)

```
python3 tools/images.py --check          # after any photo change run without --check first
python3 tools/fonts.py --check           # new glyphs → python3 tools/fonts.py
python3 tools/check_seo.py && python3 tools/sitemap.py --check
python3 tools/structured_data.py --check
python3 tools/sync_programme_portraits.py --check
python3 tools/tickets.py --check         # after adding/archiving a concert run without --check
python3 tools/check_style.py             # tokens, inline styles, asset versions, UA/EN pairs
python3 -m http.server 4175 &            # then each tools/test_*.cjs with
SITE_URL=http://127.0.0.1:4175 node tools/test_<name>.cjs
```

Python unit tests: `python3 tools/test_<name>.py` (announced concert:
`python3 -m tools.test_announced_concert`). Never weaken a test to make a
change pass; if a test encodes an old owner decision, ask.

## Code and styles

- Only design-system tokens: no new hex colours, shadows or durations in
  components; hovers use `--hover`/`--zoom`/`--ease`.
- No new hand-written `style="…"` (ratchet in `check_style.py`); add a class
  instead. Generated crops (`tools/build_artists.py`) are exempt.
- After editing `assets/site.css` (or `header.js`, `lang.js`), bump its
  `?v=N` on every page — all pages must carry the same version.
- All URLs are English: page names, anchors, asset folders and file names
  (no transliterated Ukrainian in paths).

## Header, tickets, language

- Header «Квитки»/«Tickets» and all Eventmate links are not edited by hand:
  `python3 tools/tickets.py` reads the MusicEvent offers; `assets/header.js`
  switches to the next concert after one ends, else the organiser profile.
  UA pages link Eventmate with `?locale=uk`, EN pages with `?locale=en`.
- Header on desktop home stays pinned; elsewhere and on mobile it hides on
  scroll down and returns on scroll up. Home on desktop scrolls by screens.
- Language on arrival (`assets/lang.js`, in the head of every page): at a
  UA (default) address, visitors in Ukraine (time zone) get UA; abroad, UA
  if the device language is Ukrainian, otherwise EN. An /en/ address stays
  EN unless UA was chosen before. A UA/EN choice is remembered. Crawlers
  get the requested language.

## Concerts

- Time is a range wherever it is known: `18:00–19:30` (home, concert list,
  programme, subnav). Price as a range: `250–400 ₴`.
- Facts block: first row Дата · Час · Ціна (three columns, date the same
  size as time), then Локація · Адреса. The venue label is «Локація» /
  «Location».
- Past concerts have their own page `/concerts/<english-slug>.html` (+ EN)
  on the `concert.html` layout. Show only blocks that have content; an
  empty block (e.g. programme) is not shown.
- Concert-page description sits at the top, under the facts, written about
  the concert: «Концерт … відбувся <дата> в <місце>», past tense, no
  «Запис концерту…». Nothing beside the video. The Відео page keeps the
  full description.
- Performers: see design-system §5 (main performers 4:5 tiles, students
  circles, host after students). Under a name only the role from
  `assets/artists.json`, identical on every page (artists, programmes,
  video performer lists), formatted like the 15 October page:
  «Мецо-сопрано · Солістка Національної опери України, народна артистка
  України», «Концертмейстер». Every caption starts with a capital, in UA and EN. Never «партія …», «лауреат…», «співавторка».
  `tools/test_artist_roles.py` fails on any drift.
- Composer names in full on the site (Вольфганг Амадей Моцарт).

## Posters and images

- Posters only from the concert's latest export folder (`03_Експорт`) on
  Google Drive; after each new export replace them on the site under the
  same names. Never from screenshots, caches or older folders.
- Posters are never cropped: hero shows the full poster at 69 % of the
  column width, top-right (`assets/img/<slug>-poster.jpg`, ≤2400 px). The
  upcoming concert (`concert.html`) shows it at full column width, 80 % on
  screens ≥1800 px. Without a poster the hero uses the video preview. No
  captions under posters.
- Images: follow "Images" in README.md. Originals come from Google Drive,
  byte-for-byte; keep all metadata except GPS; keep original Drive file
  names; skip byte-identical duplicates. Run `python3 tools/images.py`, then
  `--check`.
- Portraits: crops are data in `assets/artists.json` (`crop` circle,
  `programme_crop` 4:5 tile). Follow design-system §6: compute the circle
  with `python3 tools/portrait_crop.py <id>` (never by eye), judge it on the
  contact sheet next to all others
  (`SITE_URL=… node tools/portrait_sheet.cjs sheet.png --highlight <id>`);
  `tools/test_portrait_crops.py` (CI) fails on a crop outside the photo or a
  face that is off-centre, too small or too large. Fix the crop, never the
  bands. A detector PASS is only a safety gate: inspect the visible circle
  for excess background and optical head placement, especially with a tilt or profile.
  A rejected crop must be compared before/after at the same size; do not
  report it fixed solely from measurements. When the owner rejects framing,
  review the entire circle sheet for the same defect before closing the task.
- Logos (word&music, venues, Eventmate) only in original colours or in the
  system monochrome (`.venue-logo--mono`), never recoloured, no plates.
- Photo previews (5 frames on Фото and concert pages): bright colour shots
  of performances and the hall, no black-and-white; heads never cut — shift
  `object-position`.
- «Усі фото · N» opens `/photo/<slug>.html` (+ EN) with every photo; a
  click opens the lightbox. Exception: Різдвяний Калейдоскоп has no gallery
  page; its «Усі фото · 4» is plain text.

## Text and metadata

- Descriptive text: `--copy-size` 18px / 1.5, `--ink2` (`.text`,
  `.people-note`); annotations beside recordings `.small` 14px.
- Video descriptions on the Відео page use one template, filled only with
  facts from that video's YouTube description: «Запис концерту «Назва»,
  дата, місце (Київ).» + optional paragraph about the programme or
  dedication; then, skipping what does not apply: Виконавці (Імʼя — роль),
  Концертмейстер, Художнє слово / Ведучі, Автори проєкту,
  Відеовиробництво, Подяки. No links, handles, hashtags, © lines or
  timecodes. EN pages keep the Ukrainian text (`lang="uk"`).
- Every «Повний запис» / «Відео» link to a full recording carries its
  duration (e.g. «Відео 54:36»).
- Page titles: past concert «<Назва> — концерт word&music у Києві, <рік>»
  (EN «<Name> — word&music concert in Kyiv, <year>»), gallery «<Назва> —
  фото з концерту word&music, <рік>». og:title equals the title. Concert
  photo alt: «<Назва> — фото N · ДД.ММ.РРРР, <локація>, Київ».
- Photos by Kyrylo Rusanivsky (EXIF Artist) carry the rusanivsky.com
  credit: Description «Photo by Kyrylo Rusanivsky», Copyright «(c) Kyrylo
  Rusanivsky - rusanivsky.com», XMP Rights «© Kyrylo Rusanivsky ·
  rusanivsky.com», Credit, CreatorWorkURL/WebStatement
  https://rusanivsky.com. Write with `exiftool -P` (no re-encode). Posters,
  banners and the concert og image: «Poster design by Kyrylo Rusanivsky»;
  og-image.jpg «Design by Kyrylo Rusanivsky»; video stills (yt-*, *-16x9)
  «Video by Kyrylo Rusanivsky»; other fields as above.
