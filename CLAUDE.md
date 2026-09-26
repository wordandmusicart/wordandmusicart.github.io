# word&music site — working rules

- Do only what was asked. Anything not requested (removing metadata,
  renaming, re-encoding, dropping content, extra processing) needs the
  owner's OK first. When a request is ambiguous, ask before doing
  expensive work (downloads, conversions) — redoing it wastes time and
  tokens.

- Publish right away: after a change is verified, push, open a PR and
  squash-merge it into `main` (GitHub Pages deploys from `main`).
- Pages come in pairs: every change to a UA page (`/*.html`) goes into its
  EN twin (`/en/*.html`) too.
- Images: follow "Images" in README.md. Run `python3 tools/images.py`
  after adding or replacing any photo, then `--check`.
- After editing `assets/site.css`, bump `site.css?v=N` on every page.
- Concert end time (e.g. 16:00 – 17:00) appears only in the facts block of
  the concert programme page (`concert.html`). Everywhere else (header,
  subnav, sticky buy bar, home, concert list) show the start time only.
- UA pages link Eventmate with `?locale=uk`, EN pages with `?locale=en`.
- Language on arrival (`assets/lang.js`, in the head of every page):
  visitors in Ukraine (time zone) get UA; abroad, UA if the device
  language is Ukrainian, otherwise EN. A UA/EN choice is remembered.
- Nothing is invented (same rule as rusanivsky.com): titles, names, dates,
  venues, durations and descriptions come from a real source (YouTube,
  posters, the organisers). If something is unknown, leave it out rather
  than guess.
- Video descriptions on the Відео page use one template, filled only with
  facts from that video's YouTube description: «Запис концерту «Назва»,
  дата, місце (Київ).» + optional paragraph about the programme or
  dedication; then sections in this order, skipping any that do not
  apply: Виконавці (Імʼя — роль), Концертмейстер, Художнє слово / Ведучі,
  Автори проєкту, Відеовиробництво, Подяки. No links, handles, hashtags,
  © lines or timecodes. EN pages keep the Ukrainian text (`lang="uk"`).
- Every «Повний запис» / «Відео» link to a full recording carries its
  duration (e.g. «Відео 54:36»).
- Staging: test.rusanivsky.com is closed to indexing (`robots.txt` +
  `noindex` on every page). Before moving to production, remove exactly
  those two, nothing else signals staging.
- All URLs are English: page names, anchors, asset folders and file names
  (transliterated Ukrainian is not used in paths).
- Concert photos: keep the original Drive file names; keep all metadata
  except GPS; skip byte-identical duplicate copies. See README "Concert
  photos".
- Past concerts have their own page `/concerts/<english-slug>.html` (+ EN
  twin) built on the `concert.html` layout. Show only blocks that have
  content (photo, video, …); an empty block (e.g. programme) is not shown.
- Concert pages: the concert description (intro of the YouTube
  description) sits at the top, under the facts; nothing is shown beside
  the video. The Відео page keeps the full description.
- Descriptive text uses `--copy-size: 18px` with 1.5 line-height, including concert descriptions, performer notes, and privacy copy. Video annotations and descriptions beside recordings use `.small` at 14px. `.text` and `.people-note` use `--ink2`.
- «Усі фото · N» opens the concert's gallery page `/photo/<slug>.html`
  (+ EN) with every photo; a click on a photo opens the lightbox.
  Exception: Різдвяний Калейдоскоп has no gallery page; its «Усі фото · 4»
  is plain text.
- Photo previews (5 frames on the Фото and concert pages): bright, lively
  colour shots — performances and the hall, no black-and-white. Heads and
  faces are never cut by the frame; shift the crop (object-position) if
  needed.
- Posters are never cropped on concert pages: the hero shows the full
  poster at 69% of the column width, top-right, (`assets/img/<slug>-poster.jpg`, ≤2400 px, metadata kept except
  GPS). Without a poster the hero uses the video preview.
  The upcoming concert (`concert.html`) shows its poster at the full
  column width, 80% on screens ≥1800px.
- Concert facts label the venue «Локація» / «Location». The upcoming
  concert's first facts row has four columns: date, start, end, price.
- Concert-page descriptions are written as about the concert, not the
  recording: «Концерт … відбувся <дата> в <місце>», past tense, no
  «Запис концерту…».
- Page titles name what and where: past concert «<Назва> — концерт
  word&music у Києві, <рік>» (EN «<Name> — word&music concert in Kyiv,
  <year>»), gallery «<Назва> — фото з концерту word&music, <рік>».
  og:title always equals the title. Concert photo alt: «<Назва> — фото N ·
  ДД.ММ.РРРР, <локація>, Київ».
- Photos by Kyrylo Rusanivsky (EXIF Artist) carry the rusanivsky.com
  credit: Description «Photo by Kyrylo Rusanivsky», Copyright «(c) Kyrylo
  Rusanivsky - rusanivsky.com», XMP Rights «© Kyrylo Rusanivsky ·
  rusanivsky.com», Credit, CreatorWorkURL/WebStatement https://rusanivsky.com.
  Write it with `exiftool -P` (no re-encode). Posters, banners and the
  concert og image are his design («Poster design by Kyrylo Rusanivsky»);
  og-image.jpg «Design by Kyrylo Rusanivsky»;
  video stills (yt-*, *-16x9) are his video («Video by Kyrylo Rusanivsky»);
  other fields as above.
