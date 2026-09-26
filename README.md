# word&music

Static website for word&music, published with GitHub Pages.

## Preview locally

```sh
python3 -m http.server 4173
```

Then open <http://localhost:4173>.

## Images

Every photo on the site loads at the size the screen needs, the same way
rusanivsky.com does:

- Keep one master per image in `assets/img/<name>.jpg` at its original
  resolution. Never upscale.
- `python3 tools/images.py` (needs `pip install pillow`) writes
  `<name>-320/-480/-720/-960/-1440/-2400.webp`, only for widths smaller than the
  master, and fills `srcset` in every page. Variants keep the master's
  colour profile, EXIF and XMP; only GPS is removed.
- Every `<img>` (and `<source>`) gets a hand-written `sizes` that matches
  its layout, e.g. `sizes="(max-width:900px) 100vw, 40vw"`.
- `python3 tools/images.py --check` fails if a variant, `srcset` or `sizes`
  is missing, or a variant has lost the master's metadata. The deploy workflow runs it, so a broken image blocks the
  deploy.

### Structured data

Home pages carry schema.org `Organization` + `WebSite`; every concert page
carries a `MusicEvent`. `python3 tools/structured_data.py` builds the
JSON-LD from what the page already shows (H1, date, start/end, venue,
address, performers, ticket link, og:image, description) — run it after
editing any concert page or the contacts block. `--check` runs in the
deploy and fails if a page's JSON-LD is out of date.

### Fonts

Fixel Text is served as a subset (Latin, Latin Extended-A, Ukrainian
Cyrillic, punctuation) to keep each file near 30 KB. The full fonts live
in `tools/fonts-src/` and are not deployed. `python3 tools/fonts.py`
(needs `pip install fonttools brotli`) rebuilds `assets/fonts/FixelText-*`;
`--check` fails, in the deploy too, if a page uses a character the subset
lacks — then add it to `UNICODES` and rebuild.

### Concert photos

Photos from concerts live in `assets/photo/<concert-slug>/`, one folder per
concert with an English slug (e.g. `autumn-rendezvous`). Each file keeps its
original Drive name: `<name>.webp` is the top step (2400 px or the original
width if smaller) and `<name>-320/-480/-720/-960/-1440.webp` are the smaller
steps; `tools/images.py` makes missing steps from the top step.
One frame per shot; byte-identical copies (e.g. `… 1.jpg`) are skipped.
All metadata (EXIF, XMP, colour profile, author/copyright) is kept except
GPS, which is removed from EXIF and XMP. Originals stay on Google Drive
(KR/Production/Photography). The media page shows five frames per concert;
«Усі фото · N» and every frame open the full set in the lightbox
(`assets/lightbox.js`). Right-click on a frame copies its file link.
